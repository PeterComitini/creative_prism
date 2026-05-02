import glob
import json
import os
import re
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
import numpy as np
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

# =======================================================================
# THE CREATIVE PRISM: EVALUATION ENGINE
# Version 2.0 — Three-Layer Architecture
#
# Layer 1 — Structural reasoning (20% weight)
#   Dual LLM scoring: Gemini 2.5 Flash + GPT-4o, blind, 5 dimensions
#   Retained from v1.0. Measures reasoning structure.
#
# Layer 2 — Semantic transformation (40% weight)
#   Embedding-based distance metrics. Model-neutral. No LLM calls.
#   Reframing distance: prompt → brief (did discovery move the problem?)
#   Synthesis novelty: prompt → synthesis (how far did we land?)
#   Direction spread: pairwise distance across candidate set
#
# Layer 3 — Human signal (40% weight)
#   PIL rating 1–5: "Did you get something a direct prompt wouldn't give?"
#   Read from session metadata pil_rating field.
#   Retroactive ratings seeded for the first 11 sessions from observer notes.
#
# Requires in .env:
#   GEMINI_API_KEY
#   OPENAI_API_KEY
#
# Requires installed:
#   pip3 install sentence-transformers --break-system-packages
#
# Input:  sessions_hybrid/*.json files with evaluation_payload field
# Output: outputs/eval_v2_<session_id>.json per run
# =======================================================================

try:
    from sentence_transformers import SentenceTransformer

    LAYER2_AVAILABLE = True
except ImportError:
    LAYER2_AVAILABLE = False
    print("WARNING: sentence-transformers not installed.")
    print("Layer 2 (semantic transformation) will be skipped.")
    print("Install: pip3 install sentence-transformers --break-system-packages")


# Retroactive PIL ratings for the first 11 sessions.
# Based on observer notes captured in session metadata.
# Scale: 1 = no value beyond baseline, 5 = clearly beyond what direct prompt produces.
RETROACTIVE_PIL_RATINGS = {
    "ca084b3b": {
        "rating": 4,
        "basis": "Very strong performance — tiered model validation run",
    },
    "9998dd55": {
        "rating": 4,
        "basis": "Very credible and serious approach with excellent research",
    },
    "a481bbf4": {
        "rating": 3,
        "basis": "Stress test with absurd inputs — behavioral observation, not value test",
    },
    "a5e83c01": {
        "rating": 4,
        "basis": "External user (not developer): extremely impressive and helpful",
    },
    "e7fafe01": {
        "rating": 2,
        "basis": "Clarifying questions mundane and almost pointless",
    },
    "6fd6a1e7": {
        "rating": 1,
        "basis": "This is a failure of the system — barely actionable, throws work back to PIL",
    },
    "a815bfad": {"rating": 3, "basis": "Competent run, recommendations feel generic"},
    "47a00742": {
        "rating": 2,
        "basis": "Director gave homework assignments instead of solving the problem",
    },
    "baaad0b1": {
        "rating": 3,
        "basis": "Better at process-oriented problems but PIL refinement not honored",
    },
    "b06c9dbf": {
        "rating": 4,
        "basis": "Unusual and creative outcomes, improved during second iteration",
    },
    "321d6ab4": {
        "rating": 3,
        "basis": "Stress test with intentionally ambiguous PIL inputs",
    },
}


# Reframing distance interpretation thresholds
def _interpret_distance(distance: float) -> str:
    if distance < 0.15:
        return "restatement — discovery added little"
    elif distance < 0.30:
        return "elaboration — some movement"
    else:
        return "genuine reframe — problem changed"


def _interpret_spread(spread: float) -> str:
    if spread < 0.10:
        return "converged — directions too similar"
    elif spread < 0.25:
        return "moderate — reasonable spread"
    else:
        return "divergent — strong creative range"


class PrismEvaluator:

    def __init__(self):
        # -- Directory structure -------------------------------------------
        self.root_dir = Path(__file__).parent.resolve()
        self.data_dir = self.root_dir / "sessions_hybrid"
        self.outputs_dir = self.root_dir / "outputs"
        self._ensure_directories()

        # -- Load environment ----------------------------------------------
        load_dotenv(find_dotenv())

        # -- Gemini client -------------------------------------------------
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. " "Add it to your .env file."
            )
        genai.configure(api_key=gemini_key)
        self.gemini = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )

        # -- OpenAI client -------------------------------------------------
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. " "Add it to your .env file."
            )
        self.openai = OpenAI(api_key=openai_key)

        # -- Sentence transformer (Layer 2) --------------------------------
        self.embed_model = None
        if LAYER2_AVAILABLE:
            print("  Loading sentence-transformers model...")
            self.embed_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            print("  all-MiniLM-L6-v2 loaded")

        print("-- EVALUATOR V2 READY ------------------------------------")
        print("  Gemini 2.5 Flash  : configured")
        print("  GPT-4o            : configured")
        layer2_status = (
            "active" if LAYER2_AVAILABLE else "SKIPPED (install sentence-transformers)"
        )
        print(f"  Layer 2 semantic  : {layer2_status}")
        print("  Sessions dir      : sessions_hybrid/")
        print("  Outputs dir       : outputs/")
        print("----------------------------------------------------------")

    def _ensure_directories(self):
        for directory in [self.data_dir, self.outputs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    # ── Layer 1: Structural Scoring (unchanged from v1.0) ─────────────────

    def _get_evaluation_prompt(self, problem_prompt: str, response_text: str) -> str:
        return f"""
You are an evaluation system assessing the quality of reasoning in an
AI-generated response. Evaluate STRUCTURED THINKING, not style or voice.

Step 1: Classify the Problem Domain
(e.g., Financial Compliance, Brand Strategy, Product Design, Logistics,
Personal Decision-Making, Blue-Sky Creative)

Step 2: Recommend a Weighting Profile
(e.g., High-Rigor, High-Adaptability, Balanced, Creative-First)

Step 3: Score the response across 5 dimensions using a strict 1-5 scale.

SCORING GUIDANCE (1-5):
1: Fails entirely | 2: Weak | 3: Adequate | 4: Strong | 5: Explicit and integral

DIMENSIONS:

1. Anchor Integrity
   Does the response identify and consistently maintain the core problem?
   Does it avoid drifting into adjacent concerns or losing the thread?

2. Constraint Engagement
   Does the response treat the stated constraints as strategic inputs
   rather than obstacles? Does it use them to sharpen the direction?

3. Structural Coherence
   Is the response logically progressive? Does each section build on
   the last? Is the architecture clear from beginning to end?

4. Adaptive Interpretation
   Does the response navigate ambiguity intelligently? Does it make
   reasonable inferences where information is incomplete?

5. Failure Honesty
   Does the response accurately map what it does not know? Does it
   avoid false precision or overconfident claims?

ORIGINAL PROBLEM / PROMPT:
{problem_prompt}

RESPONSE TO EVALUATE:
{response_text}

Return strict JSON matching this exact schema — no preamble, no markdown:
{{
  "problem_analysis": {{
    "inferred_domain": "<string>",
    "recommended_weighting_profile": "<string>"
  }},
  "scores": {{
    "anchor_integrity":       {{"score": <int 1-5>, "justification": "<string>"}},
    "constraint_engagement":  {{"score": <int 1-5>, "justification": "<string>"}},
    "structural_coherence":   {{"score": <int 1-5>, "justification": "<string>"}},
    "adaptive_interpretation":{{"score": <int 1-5>, "justification": "<string>"}},
    "failure_honesty":        {{"score": <int 1-5>, "justification": "<string>"}}
  }}
}}
"""

    def _compute_tier1_metrics(self, log_data: dict) -> dict:
        """
        Compute Prism-specific structural metrics directly from session JSON.
        No LLM call required. Pure data extraction.
        Retained from v1.0 unchanged.
        """
        metrics = {}

        # 1. Brief Specificity Delta
        user_prompt = log_data.get("user_prompt", "")
        brief = log_data.get("creative_brief", {})
        brief_text = " ".join(
            filter(
                None,
                [
                    brief.get("challenge", ""),
                    brief.get("context", ""),
                    brief.get("desired_result", ""),
                    " ".join(brief.get("constraints", [])),
                    " ".join(brief.get("research_insights", [])),
                ],
            )
        )
        prompt_words = max(len(user_prompt.split()), 1)
        brief_words = len(brief_text.split())
        delta = round(brief_words / prompt_words, 2)

        metrics["brief_specificity_delta"] = delta
        metrics["brief_specificity_note"] = (
            f"{brief_words} brief words vs {prompt_words} prompt words "
            f"(ratio {delta}). Above 1.5 indicates meaningful discovery extraction."
        )

        # 2. Pass 1 to Pass 2 Novelty
        cycles = log_data.get("ideation_cycles", [])
        novelty_scores = []
        for cycle in cycles:
            proposals = cycle.get("creator_proposals", [])
            if len(proposals) >= 2:
                words1 = set(proposals[0].get("raw_response", "").lower().split())
                words2 = set(proposals[-1].get("raw_response", "").lower().split())
                if words1 and words2:
                    shared = len(words1 & words2)
                    total = len(words1 | words2)
                    novelty_scores.append(
                        round(1 - (shared / total), 3) if total > 0 else 0.0
                    )

        if novelty_scores:
            avg_novelty = round(sum(novelty_scores) / len(novelty_scores), 3)
            metrics["pass1_to_pass2_novelty"] = avg_novelty
            metrics["pass1_to_pass2_note"] = (
                f"Avg novelty {avg_novelty} across {len(novelty_scores)} cycle(s). "
                "1.0 = entirely new content, 0.0 = restatement."
            )
        else:
            metrics["pass1_to_pass2_novelty"] = None
            metrics["pass1_to_pass2_note"] = (
                "Insufficient ideation cycles for Pass 1/Pass 2 comparison."
            )

        # 3. Researcher Citation Rate
        citation_pattern = re.compile(
            r"https?://"
            r"|\b(according to|cited in|source:|per |reported by)\b"
            r"|\b[A-Z][a-z]+ (Foundation|Institute|Association|"
            r"University|Bureau|Agency|Council|Federation)\b"
            r"|\b\d+(\.\d+)?%"
            r"|\$\d+"
            r"|\b(study|research|report|survey|data) "
            r"(shows?|finds?|suggests?|indicates?)\b",
            re.IGNORECASE,
        )
        research_entries = log_data.get("research_trace", [])
        if research_entries:
            cited = sum(
                1
                for entry in research_entries
                if citation_pattern.search(entry.get("summary", ""))
            )
            rate = round(cited / len(research_entries), 2)
            metrics["researcher_citation_rate"] = rate
            metrics["researcher_citation_note"] = (
                f"{cited} of {len(research_entries)} research entries "
                f"contain citation signals (rate: {rate}). "
                "1.0 = all entries cited. 0.0 = no citations found."
            )
        else:
            metrics["researcher_citation_rate"] = None
            metrics["researcher_citation_note"] = (
                "No research_trace entries found in session."
            )

        return metrics

    def _score_with_gemini(self, problem_prompt: str, response_text: str) -> dict:
        prompt = self._get_evaluation_prompt(problem_prompt, response_text)
        response = self.gemini.generate_content(prompt)
        return json.loads(response.text)

    def _score_with_openai(self, problem_prompt: str, response_text: str) -> dict:
        prompt = self._get_evaluation_prompt(problem_prompt, response_text)
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation system. Return only valid JSON "
                        "matching the schema specified in the user message. "
                        "No preamble, no markdown fences."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content)

    def _calculate_agreement(self, gemini_scores: dict, openai_scores: dict) -> dict:
        agreement = {}
        agreed_count = 0
        dimensions = list(gemini_scores.keys())

        for dim in dimensions:
            g_score = gemini_scores[dim]["score"]
            o_score = openai_scores[dim]["score"]
            agrees = abs(g_score - o_score) <= 1
            agreement[dim] = {
                "gemini_score": g_score,
                "openai_score": o_score,
                "delta": abs(g_score - o_score),
                "agrees": agrees,
            }
            if agrees:
                agreed_count += 1

        agreement["agreement_rate"] = round(agreed_count / len(dimensions), 2)
        agreement["note"] = (
            f"{agreed_count}/{len(dimensions)} dimensions agree "
            f"(threshold: ≤1 point difference). "
            "Dimensions with delta > 1 indicate rubric ambiguity."
        )
        return agreement

    def _calculate_composites(self, gemini_scores: dict, openai_scores: dict) -> dict:
        composites = {}
        for dim in gemini_scores.keys():
            g = gemini_scores[dim]["score"]
            o = openai_scores[dim]["score"]
            composites[dim] = {"composite_score": round((g + o) / 2, 2)}
        return composites

    def _calculate_deltas(
        self, baseline_composites: dict, prism_composites: dict
    ) -> dict:
        deltas = {}
        total_baseline = 0.0
        total_prism = 0.0

        for dim in baseline_composites.keys():
            b = baseline_composites[dim]["composite_score"]
            p = prism_composites[dim]["composite_score"]
            deltas[f"{dim}_delta"] = round(p - b, 2)
            total_baseline += b
            total_prism += p

        deltas["total_baseline_score"] = round(total_baseline, 2)
        deltas["total_prism_score"] = round(total_prism, 2)
        deltas["overall_improvement_delta"] = round(total_prism - total_baseline, 2)
        return deltas

    # ── Layer 2: Semantic Transformation ──────────────────────────────────

    def _cosine_distance(self, text_a: str, text_b: str) -> float:
        """
        Compute cosine distance between two texts using sentence embeddings.
        Distance = 1 - cosine_similarity.
        Returns float in [0.0, 1.0]. Lower = more similar.
        0.0 = identical meaning. 1.0 = completely dissimilar.
        """
        if not self.embed_model or not text_a.strip() or not text_b.strip():
            return None
        embeddings = self.embed_model.encode(
            [text_a, text_b], normalize_embeddings=True, show_progress_bar=False
        )
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        similarity = max(-1.0, min(1.0, similarity))
        return round(1.0 - similarity, 4)

    def _compute_layer2_metrics(self, log_data: dict) -> dict:
        """
        Three semantic distance metrics:

        1. Reframing distance
           Cosine distance between raw user prompt and creative brief
           (challenge + context + desired_result).
           Measures whether discovery moved the problem.
           < 0.15 = restatement  |  0.15-0.30 = elaboration  |  > 0.30 = genuine reframe

        2. Synthesis novelty distance
           Cosine distance between raw user prompt and final synthesis.
           Measures how far the endpoint is from the starting point.
           Same thresholds as reframing distance.

        3. Direction spread
           Average pairwise cosine distance between candidate direction descriptions.
           Measures how distinct the Creative Team's output was.
           < 0.10 = converged  |  0.10-0.25 = moderate  |  > 0.25 = divergent
        """
        if not self.embed_model:
            return {"available": False, "note": "sentence-transformers not installed"}

        metrics = {"available": True}

        # -- Extract source texts ------------------------------------------
        user_prompt = log_data.get("user_prompt", "")

        brief = log_data.get("creative_brief", {})
        brief_text = " ".join(
            filter(
                None,
                [
                    brief.get("challenge", ""),
                    brief.get("context", ""),
                    brief.get("desired_result", ""),
                ],
            )
        )

        # Synthesis: prefer evaluation_payload synthesis, fall back to
        # final_synthesis.summary, then final_synthesis as string
        ep = log_data.get("evaluation_payload", {})
        synthesis_text = ep.get("experimental_group_synthesis", "")
        if not synthesis_text:
            fs = log_data.get("final_synthesis", {})
            if isinstance(fs, dict):
                synthesis_text = fs.get("summary", "")
            elif isinstance(fs, str):
                synthesis_text = fs

        candidates = log_data.get("candidate_set", [])
        candidate_descriptions = [
            c.get("description", "")
            for c in candidates
            if c.get("description", "").strip()
        ]

        # -- 1. Reframing distance -----------------------------------------
        if user_prompt and brief_text:
            rd = self._cosine_distance(user_prompt, brief_text)
            metrics["reframing_distance"] = rd
            metrics["reframing_interpretation"] = (
                _interpret_distance(rd) if rd is not None else "unavailable"
            )
        else:
            metrics["reframing_distance"] = None
            metrics["reframing_interpretation"] = "missing source text"

        # -- 2. Synthesis novelty distance ---------------------------------
        if user_prompt and synthesis_text:
            snd = self._cosine_distance(user_prompt, synthesis_text)
            metrics["synthesis_novelty_distance"] = snd
            metrics["synthesis_novelty_interpretation"] = (
                _interpret_distance(snd) if snd is not None else "unavailable"
            )
        else:
            metrics["synthesis_novelty_distance"] = None
            metrics["synthesis_novelty_interpretation"] = "missing source text"

        # -- 3. Direction spread ------------------------------------------
        if len(candidate_descriptions) >= 2:
            pairwise_distances = []
            for i in range(len(candidate_descriptions)):
                for j in range(i + 1, len(candidate_descriptions)):
                    d = self._cosine_distance(
                        candidate_descriptions[i], candidate_descriptions[j]
                    )
                    if d is not None:
                        pairwise_distances.append(d)

            if pairwise_distances:
                avg_spread = round(sum(pairwise_distances) / len(pairwise_distances), 4)
                metrics["direction_spread"] = avg_spread
                metrics["direction_spread_interpretation"] = _interpret_spread(
                    avg_spread
                )
                metrics["direction_spread_note"] = (
                    f"{len(candidate_descriptions)} candidates, "
                    f"{len(pairwise_distances)} pairs measured."
                )
            else:
                metrics["direction_spread"] = None
                metrics["direction_spread_interpretation"] = "computation failed"
        else:
            metrics["direction_spread"] = None
            metrics["direction_spread_interpretation"] = (
                f"fewer than 2 candidates ({len(candidate_descriptions)} found)"
            )

        # -- Layer 2 composite (average of available metrics) -------------
        l2_values = [
            v for k, v in metrics.items() if k.endswith("_distance") and v is not None
        ]
        metrics["layer2_composite"] = (
            round(sum(l2_values) / len(l2_values), 4) if l2_values else None
        )

        return metrics

    # ── Layer 3: Human Signal ─────────────────────────────────────────────

    def _get_pil_rating(self, log_data: dict, run_id: str) -> dict:
        """
        Retrieve PIL rating from session metadata if present,
        otherwise look up retroactive rating for known sessions.
        Returns dict with rating (1-5 or None) and basis string.
        """
        # Check live session metadata first (forward-captured sessions)
        metadata = log_data.get("session_metadata", {})
        live_rating = metadata.get("pil_rating")
        if live_rating is not None:
            try:
                rating = int(live_rating)
                if 1 <= rating <= 5:
                    return {
                        "rating": rating,
                        "source": "live_capture",
                        "basis": metadata.get("notes", "")[:200],
                    }
            except (ValueError, TypeError):
                pass

        # Fall back to retroactive ratings for the first 11 sessions
        retroactive = RETROACTIVE_PIL_RATINGS.get(run_id)
        if retroactive:
            return {
                "rating": retroactive["rating"],
                "source": "retroactive_observer_notes",
                "basis": retroactive["basis"],
            }

        return {
            "rating": None,
            "source": "not_available",
            "basis": "No PIL rating captured and no retroactive entry found.",
        }

    # ── Composite v2 ──────────────────────────────────────────────────────

    def _compute_composite_v2(
        self, layer1_delta: float, layer2_metrics: dict, pil_rating_data: dict
    ) -> dict:
        """
        Three-layer weighted composite score (0-100).

        Weights: Layer 1 = 20%, Layer 2 = 40%, Layer 3 = 40%
        If PIL rating unavailable: reweight to Layer 1 = 35%, Layer 2 = 65%

        Layer 1: normalize overall_improvement_delta from [-5, +5] to [0, 1]
        Layer 2: use layer2_composite (already in [0, 1] distance space,
                 inverted — higher distance = more movement = better)
        Layer 3: normalize PIL rating from [1, 5] to [0, 1]
        """
        # Layer 1 normalization
        l1_norm = (layer1_delta + 5.0) / 10.0
        l1_norm = max(0.0, min(1.0, l1_norm))

        # Layer 2 normalization
        # For reframing/synthesis distance: higher distance = more movement
        # Normalize against a ceiling of 0.5 (distances above 0.5 are very rare)
        l2_composite = layer2_metrics.get("layer2_composite")
        if l2_composite is not None:
            l2_norm = min(l2_composite / 0.5, 1.0)
        else:
            l2_norm = None

        # Layer 3 normalization
        pil_rating = pil_rating_data.get("rating")
        if pil_rating is not None:
            l3_norm = (pil_rating - 1.0) / 4.0
        else:
            l3_norm = None

        # Weighted composite
        if l3_norm is not None and l2_norm is not None:
            composite = (l1_norm * 0.20) + (l2_norm * 0.40) + (l3_norm * 0.40)
            weights_used = {"l1": 0.20, "l2": 0.40, "l3": 0.40}
            note = "All three layers present."
        elif l2_norm is not None:
            composite = (l1_norm * 0.35) + (l2_norm * 0.65)
            weights_used = {"l1": 0.35, "l2": 0.65, "l3": 0.0}
            note = "No PIL rating — reweighted L1/L2 to 35/65."
        elif l3_norm is not None:
            composite = (l1_norm * 0.50) + (l3_norm * 0.50)
            weights_used = {"l1": 0.50, "l2": 0.0, "l3": 0.50}
            note = "No Layer 2 (sentence-transformers missing) — reweighted L1/L3 to 50/50."
        else:
            composite = l1_norm
            weights_used = {"l1": 1.0, "l2": 0.0, "l3": 0.0}
            note = "Only Layer 1 available."

        return {
            "composite_score": round(composite * 100, 1),
            "l1_normalized": round(l1_norm, 4),
            "l2_normalized": round(l2_norm, 4) if l2_norm is not None else None,
            "l3_normalized": round(l3_norm, 4) if l3_norm is not None else None,
            "weights_used": weights_used,
            "note": note,
        }

    # ── Single Run Evaluation ─────────────────────────────────────────────

    def _evaluate_run(
        self,
        run_id: str,
        problem_prompt: str,
        baseline_text: str,
        prism_text: str,
        tier1_metrics: dict,
        layer2_metrics: dict,
        pil_rating_data: dict,
        log_data: dict,
    ):

        print(f"\n--- Evaluating Run ID: {run_id} ---")
        print(
            f"  PIL rating: {pil_rating_data.get('rating')} "
            f"({pil_rating_data.get('source')})"
        )

        results = {
            "run_id": run_id,
            "evaluator_version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "problem_prompt": problem_prompt,
            "tier1_metrics": tier1_metrics,
            "layer2_semantic": layer2_metrics,
            "layer3_human": pil_rating_data,
            "evaluations": {},
            "inter_evaluator_agreement": {},
            "metrics": {},
        }

        # -- Score baseline ------------------------------------------------
        print("  Scoring baseline — Gemini...")
        baseline_gemini = self._score_with_gemini(problem_prompt, baseline_text)
        print("  Scoring baseline — GPT-4o...")
        baseline_openai = self._score_with_openai(problem_prompt, baseline_text)

        results["evaluations"]["baseline"] = {
            "gemini": baseline_gemini,
            "openai": baseline_openai,
        }
        results["inter_evaluator_agreement"]["baseline"] = self._calculate_agreement(
            baseline_gemini["scores"], baseline_openai["scores"]
        )

        # -- Score Prism synthesis -----------------------------------------
        print("  Scoring Creative Prism — Gemini...")
        prism_gemini = self._score_with_gemini(problem_prompt, prism_text)
        print("  Scoring Creative Prism — GPT-4o...")
        prism_openai = self._score_with_openai(problem_prompt, prism_text)

        results["evaluations"]["creative_prism"] = {
            "gemini": prism_gemini,
            "openai": prism_openai,
        }
        results["inter_evaluator_agreement"]["creative_prism"] = (
            self._calculate_agreement(prism_gemini["scores"], prism_openai["scores"])
        )

        # -- Composites, deltas, and composite v2 -------------------------
        baseline_composites = self._calculate_composites(
            baseline_gemini["scores"], baseline_openai["scores"]
        )
        prism_composites = self._calculate_composites(
            prism_gemini["scores"], prism_openai["scores"]
        )

        results["metrics"] = self._calculate_deltas(
            baseline_composites, prism_composites
        )
        results["metrics"]["baseline_composites"] = baseline_composites
        results["metrics"]["prism_composites"] = prism_composites

        overall_delta = results["metrics"]["overall_improvement_delta"]
        composite_v2 = self._compute_composite_v2(
            overall_delta, layer2_metrics, pil_rating_data
        )
        results["composite_v2"] = composite_v2

        # -- Print summary -------------------------------------------------
        b_rate = results["inter_evaluator_agreement"]["baseline"]["agreement_rate"]
        p_rate = results["inter_evaluator_agreement"]["creative_prism"][
            "agreement_rate"
        ]
        rd = layer2_metrics.get("reframing_distance", "n/a")
        snd = layer2_metrics.get("synthesis_novelty_distance", "n/a")
        ds = layer2_metrics.get("direction_spread", "n/a")

        print(f"  Baseline agreement rate   : {b_rate}")
        print(f"  Prism agreement rate      : {p_rate}")
        print(f"  Layer 1 delta             : {overall_delta:+.2f}")
        print(f"  Reframing distance        : {rd}")
        print(f"  Synthesis novelty         : {snd}")
        print(f"  Direction spread          : {ds}")
        print(f"  PIL rating                : {pil_rating_data.get('rating')}/5")
        print(f"  Composite v2 score        : {composite_v2['composite_score']}/100")

        # -- Save ----------------------------------------------------------
        filename = self.outputs_dir / f"eval_v2_{run_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"  Saved: {filename.name}")

    # ── Batch Processing ──────────────────────────────────────────────────

    def process_data_directory(self):
        """
        Find all session JSON files in sessions_hybrid/ and evaluate each.
        Skips files missing evaluation_payload.
        Saves to outputs/eval_v2_<session_id>.json.
        Does NOT skip already-evaluated files — always overwrites with v2 output.
        """
        log_files = glob.glob(str(self.data_dir / "*.json"))

        if not log_files:
            print("No session JSON files found in sessions_hybrid/")
            return

        print(f"Found {len(log_files)} session file(s). Beginning evaluation...")
        processed = 0
        skipped = 0

        for file_path in sorted(log_files):
            filename = Path(file_path).name

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    log_data = json.load(f)

                # Check for evaluation_payload
                if (
                    "evaluation_payload" not in log_data
                    or not log_data["evaluation_payload"]
                ):
                    print(f"  SKIP {filename}: missing evaluation_payload")
                    skipped += 1
                    continue

                payload = log_data["evaluation_payload"]

                # Validate required payload fields
                required_fields = [
                    "problem_prompt",
                    "control_group_baseline",
                    "experimental_group_synthesis",
                ]
                missing = [f for f in required_fields if not payload.get(f, "").strip()]
                if missing:
                    print(f"  SKIP {filename}: empty payload fields: {missing}")
                    skipped += 1
                    continue

                run_id = log_data.get("session_metadata", {}).get(
                    "session_id", f"run_{int(datetime.now().timestamp())}"
                )[:8]

                # Compute all metrics
                tier1 = self._compute_tier1_metrics(log_data)
                layer2 = self._compute_layer2_metrics(log_data)
                layer3 = self._get_pil_rating(log_data, run_id)

                self._evaluate_run(
                    run_id=run_id,
                    problem_prompt=payload["problem_prompt"],
                    baseline_text=payload["control_group_baseline"],
                    prism_text=payload["experimental_group_synthesis"],
                    tier1_metrics=tier1,
                    layer2_metrics=layer2,
                    pil_rating_data=layer3,
                    log_data=log_data,
                )
                processed += 1

            except json.JSONDecodeError as e:
                print(f"  ERROR {filename}: JSON parse error — {e}")
            except Exception as e:
                print(f"  ERROR {filename}: {e}")

        print(f"\nComplete: {processed} evaluated, {skipped} skipped.")

        if processed > 0:
            self._print_summary_table()

    def _print_summary_table(self):
        """Print a comparison table of all v2 eval results after the run."""
        eval_files = sorted(glob.glob(str(self.outputs_dir / "eval_v2_*.json")))
        if not eval_files:
            return

        print("\n── RESULTS SUMMARY ──────────────────────────────────────────────")
        print(
            f"{'run_id':<12} {'L1 delta':>10} {'reframe':>9} {'novelty':>9} "
            f"{'spread':>8} {'PIL':>5} {'v2 score':>9}"
        )
        print("─" * 68)

        for fp in eval_files:
            try:
                with open(fp) as f:
                    r = json.load(f)
                run_id = r.get("run_id", "")[:8]
                l1_delta = r.get("metrics", {}).get("overall_improvement_delta", "–")
                l2 = r.get("layer2_semantic", {})
                reframe = l2.get("reframing_distance", "–")
                novelty = l2.get("synthesis_novelty_distance", "–")
                spread = l2.get("direction_spread", "–")
                pil = r.get("layer3_human", {}).get("rating", "–")
                v2_score = r.get("composite_v2", {}).get("composite_score", "–")

                l1_str = (
                    f"{l1_delta:+.2f}" if isinstance(l1_delta, float) else str(l1_delta)
                )
                rf_str = (
                    f"{reframe:.3f}" if isinstance(reframe, float) else str(reframe)
                )
                nv_str = (
                    f"{novelty:.3f}" if isinstance(novelty, float) else str(novelty)
                )
                sp_str = f"{spread:.3f}" if isinstance(spread, float) else str(spread)
                v2_str = (
                    f"{v2_score:.1f}" if isinstance(v2_score, float) else str(v2_score)
                )

                print(
                    f"{run_id:<12} {l1_str:>10} {rf_str:>9} {nv_str:>9} "
                    f"{sp_str:>8} {str(pil):>5} {v2_str:>9}"
                )
            except Exception:
                pass

        print("─" * 68)
        print(
            "L1=structural delta | reframe=prompt→brief | "
            "novelty=prompt→synthesis | spread=candidate spread | "
            "PIL=human rating/5 | v2=composite score/100"
        )


if __name__ == "__main__":
    evaluator = PrismEvaluator()
    evaluator.process_data_directory()
