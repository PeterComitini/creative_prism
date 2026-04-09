import os
import re
import json
import glob
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# =======================================================================
# THE CREATIVE PRISM: EVALUATION ENGINE
# Version 2.0
#
# Dual-evaluator design: Gemini 1.5 Pro + GPT-4o score independently.
# Agreement between evaluators validates rubric stability.
# Tier 1 metrics extracted directly from session JSON — no LLM required.
#
# Requires in .env:
#   GEMINI_API_KEY
#   OPENAI_API_KEY
#
# Input:  sessions/*.json files with evaluation_payload field
# Output: outputs/eval_<session_id>.json per run
# =======================================================================


class PrismEvaluator:

    def __init__(self):
        # -- Directory structure -------------------------------------------
        self.root_dir   = Path(__file__).parent.resolve()
        self.data_dir   = self.root_dir / "sessions"
        self.outputs_dir = self.root_dir / "outputs"
        self._ensure_directories()

        # -- Load environment ----------------------------------------------
        load_dotenv(find_dotenv())

        # -- Gemini client -------------------------------------------------
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. "
                "Add it to your .env file.")
        genai.configure(api_key=gemini_key)
        self.gemini = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            }
        )

        # -- OpenAI client -------------------------------------------------
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Add it to your .env file.")
        self.openai = OpenAI(api_key=openai_key)

        print("-- EVALUATOR READY -----------------------------------------")
        print("  Gemini 1.5 Pro   : configured")
        print("  GPT-4o           : configured")
        print("  Sessions dir     : sessions/")
        print("  Outputs dir      : outputs/")
        print("------------------------------------------------------------")

    def _ensure_directories(self):
        for directory in [self.data_dir, self.outputs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    # -- Evaluation Prompt -------------------------------------------------

    def _get_evaluation_prompt(self, problem_prompt: str,
                                response_text: str) -> str:
        """
        Shared evaluation prompt used by both Gemini and GPT-4o.
        Identical text ensures comparable scoring conditions.

        IMPORTANT: The prompt contains no model-identifying information
        about the response being scored. Both evaluators score blind.
        """
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

    # -- Tier 1 Metrics ----------------------------------------------------

    def _compute_tier1_metrics(self, log_data: dict) -> dict:
        """
        Compute Prism-specific structural metrics directly from session JSON.
        No LLM call required. Pure data extraction.

        Three metrics:

        1. Brief Specificity Delta
           How much more specific is the Creative Brief than the raw user
           input? Measures the value of the discovery stage. Expressed as
           a ratio: brief word count / prompt word count. A ratio above
           1.5 indicates meaningful discovery extraction.

        2. Pass 1 to Pass 2 Novelty
           Within each ideation cycle, compares first and last Creator
           proposals. Measures how much new content the second pass added.
           Expressed as 1 - (shared words / total unique words).
           1.0 = entirely new content. 0.0 = pure restatement.
           Averaged across all cycles.

        3. Researcher Citation Rate
           Proportion of research_trace entries containing at least one
           citation signal: URLs, named institutions, statistics, or
           attribution language. Distinguishes real research from
           analysis dressed as research.
        """
        metrics = {}

        # 1. Brief Specificity Delta ----------------------------------
        user_prompt = log_data.get("user_prompt", "")
        brief = log_data.get("creative_brief", {})
        brief_text = " ".join(filter(None, [
            brief.get("challenge", ""),
            brief.get("context", ""),
            brief.get("desired_result", ""),
            " ".join(brief.get("constraints", [])),
            " ".join(brief.get("research_insights", []))
        ]))
        prompt_words = max(len(user_prompt.split()), 1)
        brief_words  = len(brief_text.split())
        delta = round(brief_words / prompt_words, 2)

        metrics["brief_specificity_delta"] = delta
        metrics["brief_specificity_note"] = (
            f"{brief_words} brief words vs {prompt_words} prompt words "
            f"(ratio {delta}). Above 1.5 indicates meaningful discovery extraction."
        )

        # 2. Pass 1 to Pass 2 Novelty --------------------------------
        cycles = log_data.get("ideation_cycles", [])
        novelty_scores = []
        for cycle in cycles:
            proposals = cycle.get("creator_proposals", [])
            if len(proposals) >= 2:
                words1 = set(proposals[0].get("raw_response", "").lower().split())
                words2 = set(proposals[-1].get("raw_response", "").lower().split())
                if words1 and words2:
                    shared = len(words1 & words2)
                    total  = len(words1 | words2)
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

        # 3. Researcher Citation Rate --------------------------------
        citation_pattern = re.compile(
            r'https?://'                                              # URLs
            r'|\b(according to|cited in|source:|per |reported by)\b' # Attribution
            r'|\b[A-Z][a-z]+ (Foundation|Institute|Association|'
            r'University|Bureau|Agency|Council|Federation)\b'         # Named orgs
            r'|\b\d+(\.\d+)?%'                                        # Percentages
            r'|\$\d+'                                                  # Dollar amounts
            r'|\b(study|research|report|survey|data) '
            r'(shows?|finds?|suggests?|indicates?)\b',                # Research language
            re.IGNORECASE
        )
        research_entries = log_data.get("research_trace", [])
        if research_entries:
            cited = sum(
                1 for entry in research_entries
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

    # -- Individual Evaluator Calls ----------------------------------------

    def _score_with_gemini(self, problem_prompt: str,
                           response_text: str) -> dict:
        """Score one response with Gemini 1.5 Pro. Returns parsed score dict."""
        prompt = self._get_evaluation_prompt(problem_prompt, response_text)
        response = self.gemini.generate_content(prompt)
        return json.loads(response.text)

    def _score_with_openai(self, problem_prompt: str,
                           response_text: str) -> dict:
        """Score one response with GPT-4o. Returns parsed score dict."""
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
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)

    # -- Agreement Calculation ---------------------------------------------

    def _calculate_agreement(self, gemini_scores: dict,
                              openai_scores: dict) -> dict:
        """
        Compute per-dimension agreement between Gemini and GPT-4o.
        Agreement threshold: abs(score_a - score_b) <= 1 point.
        Dimensions diverging by more than 1 point flag rubric ambiguity.

        Returns agreement dict with per-dimension flags and overall rate.
        """
        agreement = {}
        agreed_count = 0
        dimensions = list(gemini_scores.keys())

        for dim in dimensions:
            g_score = gemini_scores[dim]["score"]
            o_score = openai_scores[dim]["score"]
            agrees  = abs(g_score - o_score) <= 1
            agreement[dim] = {
                "gemini_score": g_score,
                "openai_score": o_score,
                "delta":        abs(g_score - o_score),
                "agrees":       agrees
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

    # -- Composite Score Calculation ---------------------------------------

    def _calculate_composites(self, gemini_scores: dict,
                               openai_scores: dict) -> dict:
        """
        Average Gemini and GPT-4o scores per dimension.
        The composite is the authoritative score used for delta calculation.
        """
        composites = {}
        for dim in gemini_scores.keys():
            g = gemini_scores[dim]["score"]
            o = openai_scores[dim]["score"]
            composites[dim] = {"composite_score": round((g + o) / 2, 2)}
        return composites

    # -- Delta Calculation -------------------------------------------------

    def _calculate_deltas(self, baseline_composites: dict,
                           prism_composites: dict) -> dict:
        """
        Calculate per-dimension and overall improvement deltas.
        Uses composite scores (average of both evaluators).
        Positive delta = Prism outperformed baseline on that dimension.
        """
        deltas = {}
        total_baseline = 0.0
        total_prism    = 0.0

        for dim in baseline_composites.keys():
            b = baseline_composites[dim]["composite_score"]
            p = prism_composites[dim]["composite_score"]
            deltas[f"{dim}_delta"] = round(p - b, 2)
            total_baseline += b
            total_prism    += p

        deltas["total_baseline_score"]      = round(total_baseline, 2)
        deltas["total_prism_score"]         = round(total_prism, 2)
        deltas["overall_improvement_delta"] = round(total_prism - total_baseline, 2)
        return deltas

    # -- Single Run Evaluation ---------------------------------------------

    def _evaluate_run(self, run_id: str, problem_prompt: str,
                      baseline_text: str, prism_text: str,
                      tier1_metrics: dict):
        """
        Evaluate one session run.
        Scores both baseline and Prism outputs with both evaluators.
        Computes agreement, composites, and deltas.
        Saves to outputs/eval_<run_id>.json.
        """
        print(f"\n--- Evaluating Run ID: {run_id} ---")

        results = {
            "run_id":         run_id,
            "timestamp":      datetime.now().isoformat(),
            "problem_prompt": problem_prompt,
            "tier1_metrics":  tier1_metrics,
            "evaluations":    {},
            "inter_evaluator_agreement": {},
            "metrics":        {}
        }

        # -- Score baseline ------------------------------------------------
        print("  Scoring baseline — Gemini...")
        baseline_gemini = self._score_with_gemini(problem_prompt, baseline_text)
        print("  Scoring baseline — GPT-4o...")
        baseline_openai = self._score_with_openai(problem_prompt, baseline_text)

        results["evaluations"]["baseline"] = {
            "gemini": baseline_gemini,
            "openai": baseline_openai
        }
        results["inter_evaluator_agreement"]["baseline"] = \
            self._calculate_agreement(
                baseline_gemini["scores"], baseline_openai["scores"])

        # -- Score Prism synthesis -----------------------------------------
        print("  Scoring Creative Prism — Gemini...")
        prism_gemini = self._score_with_gemini(problem_prompt, prism_text)
        print("  Scoring Creative Prism — GPT-4o...")
        prism_openai = self._score_with_openai(problem_prompt, prism_text)

        results["evaluations"]["creative_prism"] = {
            "gemini": prism_gemini,
            "openai": prism_openai
        }
        results["inter_evaluator_agreement"]["creative_prism"] = \
            self._calculate_agreement(
                prism_gemini["scores"], prism_openai["scores"])

        # -- Composites and deltas ----------------------------------------
        baseline_composites = self._calculate_composites(
            baseline_gemini["scores"], baseline_openai["scores"])
        prism_composites    = self._calculate_composites(
            prism_gemini["scores"], prism_openai["scores"])

        results["metrics"] = self._calculate_deltas(
            baseline_composites, prism_composites)
        results["metrics"]["baseline_composites"] = baseline_composites
        results["metrics"]["prism_composites"]    = prism_composites

        # -- Agreement summary --------------------------------------------
        b_rate = results["inter_evaluator_agreement"]["baseline"]["agreement_rate"]
        p_rate = results["inter_evaluator_agreement"]["creative_prism"]["agreement_rate"]
        overall_delta = results["metrics"]["overall_improvement_delta"]

        print(f"  Baseline agreement rate   : {b_rate}")
        print(f"  Prism agreement rate      : {p_rate}")
        print(f"  Overall improvement delta : {overall_delta:+.2f}")

        # -- Save ----------------------------------------------------------
        filename = self.outputs_dir / f"eval_{run_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"  Saved: {filename.name}")

    # -- Batch Processing --------------------------------------------------

    def process_data_directory(self):
        """
        Find all session JSON files in sessions/ and evaluate each one.
        Skips files missing the evaluation_payload field.
        Files already evaluated (matching eval_ output exists) are skipped
        unless force=True — avoids re-spending API budget on stable runs.
        """
        log_files = glob.glob(str(self.data_dir / "*.json"))

        if not log_files:
            print("No session JSON files found in sessions/")
            return

        print(f"Found {len(log_files)} session file(s). Beginning evaluation...")
        processed = 0
        skipped   = 0

        for file_path in sorted(log_files):
            filename = Path(file_path).name

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    log_data = json.load(f)

                # Check for evaluation_payload
                if "evaluation_payload" not in log_data or \
                        not log_data["evaluation_payload"]:
                    print(f"  SKIP {filename}: missing evaluation_payload")
                    skipped += 1
                    continue

                payload = log_data["evaluation_payload"]

                # Validate payload fields
                required_fields = [
                    "problem_prompt",
                    "control_group_baseline",
                    "experimental_group_synthesis"
                ]
                missing = [f for f in required_fields if not payload.get(f, "").strip()]
                if missing:
                    print(f"  SKIP {filename}: empty payload fields: {missing}")
                    skipped += 1
                    continue

                run_id = log_data.get(
                    "session_metadata", {}).get(
                    "session_id",
                    f"run_{int(datetime.now().timestamp())}"
                )[:8]

                # Skip if already evaluated
                eval_file = self.outputs_dir / f"eval_{run_id}.json"
                if eval_file.exists():
                    print(f"  SKIP {filename}: eval_{run_id}.json already exists")
                    skipped += 1
                    continue

                # Compute Tier 1 metrics
                tier1 = self._compute_tier1_metrics(log_data)

                self._evaluate_run(
                    run_id        = run_id,
                    problem_prompt = payload["problem_prompt"],
                    baseline_text  = payload["control_group_baseline"],
                    prism_text     = payload["experimental_group_synthesis"],
                    tier1_metrics  = tier1
                )
                processed += 1

            except json.JSONDecodeError as e:
                print(f"  ERROR {filename}: JSON parse error — {e}")
            except Exception as e:
                print(f"  ERROR {filename}: {e}")

        print(f"\nComplete: {processed} evaluated, {skipped} skipped.")


if __name__ == "__main__":
    evaluator = PrismEvaluator()
    evaluator.process_data_directory()
