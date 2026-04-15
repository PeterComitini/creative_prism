# Creative Prism — Hybrid Engine
# Version 1.0
#
# Unified engine supporting both Anthropic (Claude) and OpenAI (GPT) providers.
# Identical architecture and blackboard schema to engine.py v2.1.
# Provider is selected per-call via the `provider` parameter in call_role().
#
# Design:
#   - Primary model (Director + Creative Team) uses one provider
#   - Critic uses the opposite provider for cognitive contrast
#   - Provider routing is decided in Cell 2b — Model Routing
#   - All other cells are unchanged except Critic cells (Cell 6, Cell 7c)
#     which pass provider=CRITIC_PROVIDER and model=CRITIC_MODEL
#
# Provider constants (set in Cell 2 after routing):
#   PRIMARY_PROVIDER  = "anthropic" | "openai"
#   CRITIC_PROVIDER   = "openai"    | "anthropic"  (always opposite)
#   DIRECTOR_MODEL    = e.g. "claude-sonnet-4-20250514" | "gpt-5.4"
#   SESSION_MODEL     = e.g. "claude-haiku-4-5-20251001" | "gpt-5.4-mini"
#   CRITIC_MODEL      = opposite provider's session-tier model
#
# Prompt directories:
#   prompts_hybrid/           — shared prompts (director, creator, researcher, scribe)
#   prompts_hybrid/critic.md          — Claude Critic (constraint-oriented)
#   prompts_hybrid/critic_gpt.md      — GPT Critic (creative-oriented)
#
# Sessions: sessions_hybrid/
#
# Token note: OpenAI uses max_completion_tokens; Anthropic uses max_tokens.
#   call_role() handles this transparently based on provider.
#
# Usage:
#   from engine_hybrid import (
#       create_blackboard, scribe_log,
#       build_prompt, call_role, save_session, verify_engine,
#       create_brief_doc, update_brief_doc, read_brief_doc,
#       load_traits_matrix, weight_to_band, build_trait_profile,
#       get_tunable_traits, validate_adjustments,
#       validate_stage, generate_baseline, assemble_evaluation_payload,
#       route_session,
#       ANTHROPIC_DEFAULT, OPENAI_DEFAULT,
#   )

import os
import csv
import json
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
import anthropic
from openai import OpenAI

# -- Environment Setup ---------------------------------------------------------

load_dotenv(find_dotenv())

_anthropic_key = os.getenv("ANTHROPIC_API_KEY")
_openai_key    = os.getenv("OPENAI_API_KEY")

if not _anthropic_key:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY not found. Add it to your .env file.")
if not _openai_key:
    raise EnvironmentError(
        "OPENAI_API_KEY not found. Add it to your .env file.")

_anthropic_client = anthropic.Anthropic(api_key=_anthropic_key)
_openai_client    = OpenAI(api_key=_openai_key)

# -- Model Constants -----------------------------------------------------------

ANTHROPIC_DEFAULT  = "claude-haiku-4-5-20251001"
ANTHROPIC_DIRECTOR = "claude-sonnet-4-20250514"
OPENAI_DEFAULT     = "gpt-5.4-mini"
OPENAI_DIRECTOR    = "gpt-5.4"

# Routing classifier uses the cheapest available model on each provider
ROUTING_MODEL_ANTHROPIC = "claude-haiku-4-5-20251001"
ROUTING_MODEL_OPENAI    = "gpt-5.4-mini"

# -- Directories ---------------------------------------------------------------

PROMPTS_DIR  = Path(__file__).parent / "prompts_hybrid"
SESSIONS_DIR = Path(__file__).parent / "sessions_hybrid"
MATRIX_PATH  = Path(__file__).parent / "persona_traits_matrix_v2.csv"


# -- Blackboard ----------------------------------------------------------------

def create_blackboard(user_prompt, system_version="hybrid-1.0",
                      director_model="", primary_provider="anthropic"):
    """
    Initialize a fresh Blackboard for a new hybrid studio session.
    Schema v2.2 plus hybrid routing metadata.
    """
    return {
        "session_metadata": {
            "session_id":        str(uuid.uuid4()),
            "timestamp":         datetime.now().isoformat(),
            "system_version":    system_version,
            "schema_version":    "2.2",
            "environment":       "Creative Prism Studio — Hybrid",
            "director_model":    director_model,
            "primary_provider":  primary_provider,
            "director_summary":  "",
            "notes":             ""
        },
        "routing": {
            "orientation":        "",   # "creative" | "strategic" | "balanced"
            "orientation_score":  0.0,  # 0.0 (strategic) → 1.0 (creative)
            "primary_provider":   primary_provider,
            "critic_provider":    "",
            "tiebreaker_used":    False,
            "tiebreaker_answers": [],
            "rationale":          "",
            "operator_override":  False,
        },
        "user_prompt": user_prompt,
        "discovery": {
            "orientation_summary": "",
            "context_insights":    [],
            "desired_outcome":     "",
            "preferences":         [],
            "exploratory_prompts": [],
            "sacrificial_exploration": {
                "probe_prompt":      "",
                "user_response":     "",
                "insight_extracted": ""
            }
        },
        "creative_brief": {
            "challenge":         "",
            "context":           "",
            "desired_result":    "",
            "constraints":       [],
            "research_insights": [],
            "open_questions":    []
        },
        "research_trace":  [],
        "idea_space":      [],
        "ideation_cycles": [],
        "candidate_set":   [],
        "director_review": {
            "alignment_with_brief":       "",
            "distinctiveness_assessment": "",
            "balance_assessment":         "",
            "clarity_assessment":         "",
            "iteration_required":         False
        },
        "presentation": {
            "ordered_directions":  [],
            "director_commentary": []
        },
        "user_response": {
            "selected_direction": None,
            "feedback_summary":   "",
            "signals_extracted":  []
        },
        "second_exploration": {
            "triggered":         False,
            "reason":            "",
            "additional_cycles": []
        },
        "final_synthesis": {
            "final_direction": None,
            "refinements":     [],
            "summary":         ""
        },
        "reasoning_trace":    [],
        "evaluation_payload": {}
    }


# -- Scribe --------------------------------------------------------------------

def scribe_log(blackboard, role, action, summary, target=""):
    """Append a step to the reasoning trace."""
    step = len(blackboard["reasoning_trace"]) + 1
    blackboard["reasoning_trace"].append({
        "step":      step,
        "timestamp": datetime.now().isoformat(),
        "role":      role,
        "action":    action,
        "target":    target,
        "summary":   summary
    })


# -- Stage Validation ----------------------------------------------------------

def validate_stage(blackboard, stage_name):
    """Validate that a pipeline stage completed successfully."""
    if stage_name == "brief":
        brief   = blackboard.get("creative_brief", {})
        missing = [f for f in ["challenge", "context", "desired_result"]
                   if not brief.get(f, "").strip()]
        if missing:
            raise RuntimeError(
                f"VALIDATION FAILED — brief: missing fields: {missing}")

    elif stage_name == "ideation":
        cycles   = blackboard.get("ideation_cycles", [])
        if not cycles:
            raise RuntimeError("VALIDATION FAILED — ideation: no cycles found.")
        proposals = cycles[-1].get("creator_proposals", [])
        if not proposals or not proposals[0].get("raw_response", "").strip():
            raise RuntimeError("VALIDATION FAILED — ideation: creator_proposals empty.")

    elif stage_name == "critic":
        cycles   = blackboard.get("ideation_cycles", [])
        if not cycles:
            raise RuntimeError("VALIDATION FAILED — critic: no cycles found.")
        feedback = cycles[-1].get("critic_feedback", [])
        if not feedback or not feedback[0].get("raw_response", "").strip():
            raise RuntimeError("VALIDATION FAILED — critic: critic_feedback empty.")

    elif stage_name == "candidate_set":
        if not blackboard.get("candidate_set", []):
            raise RuntimeError("VALIDATION FAILED — candidate_set: empty.")

    else:
        raise ValueError(f"Unknown stage_name: '{stage_name}'")

    return True


# -- Studio Brief Document -----------------------------------------------------

def create_brief_doc(session_id, user_prompt, sessions_dir=None):
    """Create a new Studio Brief Document for a session."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    path    = Path(sessions_dir) / f"brief_{session_id}.md"
    content = (
        f"# STUDIO BRIEF DOCUMENT\n"
        f"## The Creative Prism — Hybrid\n"
        f"**Session:** {session_id}\n"
        f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n"
        f"## SESSION\n\n"
        f"**Initial Request:** {user_prompt}\n\n"
        f"---\n\n"
        f"*This document is the shared working memory of the studio session.\n"
        f"Every role reads this document before acting.*\n\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def update_brief_doc(session_id, role, section_title, content,
                     sessions_dir=None):
    """Append a new section to the Studio Brief Document."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    path = Path(sessions_dir) / f"brief_{session_id}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Brief document not found for session {session_id}.")
    timestamp = datetime.now().strftime('%H:%M')
    addition  = (f"\n---\n\n## {section_title}\n"
                 f"*{role} — {timestamp}*\n\n{content}\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(addition)


def read_brief_doc(session_id, max_chars=12000, sessions_dir=None):
    """Read the Studio Brief Document, loading only the most recent max_chars."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    path = Path(sessions_dir) / f"brief_{session_id}.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return "...[earlier content compressed]...\n\n" + text[-max_chars:]


# -- Traits Matrix System ------------------------------------------------------

def load_traits_matrix(matrix_path=None):
    """Load the persona traits matrix from CSV."""
    if matrix_path is None:
        matrix_path = MATRIX_PATH
    matrix_path = Path(matrix_path)
    if not matrix_path.exists():
        raise FileNotFoundError(
            f"Traits matrix not found: {matrix_path}")
    traits = []
    with open(matrix_path, 'r', encoding='utf-8') as f:
        lines = [line for line in f
                 if line.strip() and not line.strip().startswith('#')]
    reader    = csv.DictReader(lines)
    float_cols = [
        'creator_base', 'creator_min', 'creator_max',
        'critic_base',  'critic_min',  'critic_max',
        'researcher_base', 'researcher_min', 'researcher_max',
        'scribe_base',  'scribe_min',  'scribe_max'
    ]
    for row in reader:
        try:
            active = int(float(row.get('Active', '0')))
        except (ValueError, TypeError):
            active = 0
        if not active:
            continue
        for col in float_cols:
            try:
                row[col] = float(row[col])
            except (ValueError, TypeError, KeyError):
                row[col] = 0.0
        traits.append(row)
    return traits


def weight_to_band(value):
    """Convert a numeric trait weight to a five-band language directive."""
    if value >= 0.90:
        return ("HIGHEST", "is a defining quality of your work in this session "
                "— bring it fully and without reservation")
    elif value >= 0.70:
        return ("HIGH", "should be strongly present throughout your output")
    elif value >= 0.45:
        return ("MEDIUM", "is relevant to this work — apply it where it "
                "genuinely serves the output")
    elif value >= 0.20:
        return ("LOW", "should be restrained — use it sparingly and only "
                "when the work clearly requires it")
    else:
        return ("LOWEST", "is a minor undercurrent — it should not noticeably "
                "influence your output")


def build_trait_profile(role, session_adjustments, traits_matrix):
    """Build the natural language trait profile block for a given role."""
    base_col = f"{role}_base"
    bands = {
        "DEFINING QUALITIES (bring fully, without reservation)": [],
        "STRONGLY PRESENT (consistently expressed)":             [],
        "ACTIVE AND BALANCED (apply where it serves the output)": [],
        "RESTRAINED (use sparingly)":                            [],
        "BACKGROUND ONLY (should not noticeably influence output)": []
    }
    band_map = {
        "HIGHEST": "DEFINING QUALITIES (bring fully, without reservation)",
        "HIGH":    "STRONGLY PRESENT (consistently expressed)",
        "MEDIUM":  "ACTIVE AND BALANCED (apply where it serves the output)",
        "LOW":     "RESTRAINED (use sparingly)",
        "LOWEST":  "BACKGROUND ONLY (should not noticeably influence output)"
    }
    for trait_row in traits_matrix:
        base_val = trait_row.get(base_col, 0.0)
        if base_val <= 0.0:
            continue
        trait_name   = trait_row['trait']
        effective    = session_adjustments.get(trait_name, base_val)
        band_name, _ = weight_to_band(effective)
        display_name = trait_name.replace('_', ' ')
        bands[band_map[band_name]].append(display_name)

    lines = [f"TRAIT PROFILE — {role.upper()} — SESSION CONFIGURATION\n"]
    for band_label, trait_list in bands.items():
        if trait_list:
            lines.append(f"{band_label}:")
            for t in trait_list:
                lines.append(f"  — {t}")
            lines.append("")
    return "\n".join(lines)


def get_tunable_traits(role, traits_matrix):
    """Return list of traits the Director can adjust for this role."""
    base_col = f"{role}_base"
    min_col  = f"{role}_min"
    max_col  = f"{role}_max"
    tunable  = []
    for row in traits_matrix:
        base_val = row.get(base_col, 0.0)
        min_val  = row.get(min_col,  0.0)
        max_val  = row.get(max_col,  0.0)
        if base_val <= 0.0 or min_val == max_val:
            continue
        tunable.append({
            "trait":       row['trait'],
            "category":    row.get('category', ''),
            "base":        base_val,
            "min":         min_val,
            "max":         max_val,
            "description": row.get('description', '')
        })
    return tunable


def validate_adjustments(role, adjustments, traits_matrix):
    """Validate and clamp Director's trait adjustments to allowed ranges."""
    min_col = f"{role}_min"
    max_col = f"{role}_max"
    ranges  = {row['trait']: (row.get(min_col, 0.0), row.get(max_col, 0.0))
               for row in traits_matrix}
    cleaned  = {}
    warnings = []
    for trait, value in adjustments.items():
        if trait not in ranges:
            warnings.append(f"{role}: unknown trait '{trait}' — skipped")
            continue
        lo, hi  = ranges[trait]
        if lo == hi:
            warnings.append(f"{role}: '{trait}' is fixed at {lo} — skipped")
            continue
        clamped = max(lo, min(hi, float(value)))
        if clamped != float(value):
            warnings.append(
                f"{role}: '{trait}' clamped {value} → {clamped} "
                f"(range: {lo}-{hi})")
        cleaned[trait] = clamped
    return cleaned, warnings


# -- Prompt Compiler -----------------------------------------------------------

_SYSTEM_FOUNDATION_CACHE = {}


def _get_system_foundation(prompts_dir=PROMPTS_DIR):
    """Load and cache the system foundation prompt."""
    key  = str(prompts_dir)
    if key not in _SYSTEM_FOUNDATION_CACHE:
        path = Path(prompts_dir) / "SYSTEM_PROMPT.md"
        if not path.exists():
            raise FileNotFoundError(
                f"SYSTEM_PROMPT.md not found at {path.resolve()}")
        _SYSTEM_FOUNDATION_CACHE[key] = path.read_text(encoding="utf-8")
    return _SYSTEM_FOUNDATION_CACHE[key]


def _load_role_prompt(role, prompts_dir=PROMPTS_DIR):
    """Load a role prompt file."""
    path = Path(prompts_dir) / f"{role}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Role prompt not found: {path.resolve()}\n"
            f"Run setup: cp prompts/* prompts_hybrid/")
    return path.read_text(encoding="utf-8")


def build_prompt(role, context, trait_profile="", brief_doc="",
                 prompts_dir=PROMPTS_DIR, provider="anthropic"):
    """
    Compile a complete system prompt for a studio role.

    For the Critic role, provider determines which prompt file is loaded:
      provider="anthropic"  →  critic.md     (constraint-oriented)
      provider="openai"     →  critic_gpt.md (creative-oriented)

    All other roles use the same prompt file regardless of provider.
    """
    system_foundation = _get_system_foundation(prompts_dir)

    # Critic uses provider-specific prompt file
    if role == "critic" and provider == "openai":
        role_file = "critic_gpt"
    else:
        role_file = role

    role_identity = _load_role_prompt(role_file, prompts_dir)
    parts         = [system_foundation, "\n\n---", role_identity]

    if trait_profile and trait_profile.strip():
        parts.append(f"\n\n---\n## SESSION TRAIT PROFILE\n"
                     f"*These traits have been configured by the Director "
                     f"for this specific problem.*\n\n{trait_profile}")

    if brief_doc and brief_doc.strip():
        parts.append(f"\n\n---\n## STUDIO BRIEF DOCUMENT\n"
                     f"*This is the shared working memory of the current "
                     f"session. Read this before acting.*\n\n{brief_doc}")

    parts.append(f"\n\n---\n## Current Task Context\n{context}")
    return "\n".join(parts)


# -- API Dispatch --------------------------------------------------------------

def _call_anthropic(system_prompt, user_message, model, max_tokens):
    """Make a single Anthropic API call. Returns text string."""
    response = _anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


def _call_openai(system_prompt, user_message, model, max_tokens):
    """Make a single OpenAI API call. Returns text string."""
    response = _openai_client.chat.completions.create(
        model=model,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "developer", "content": system_prompt},
            {"role": "user",      "content": user_message}
        ]
    )
    return response.choices[0].message.content


# -- call_role -----------------------------------------------------------------

def call_role(role, user_message, context, blackboard,
              model=ANTHROPIC_DEFAULT, max_tokens=1024,
              trait_profile="", brief_doc="",
              provider="anthropic"):
    """
    Make a single API call as a studio role.

    provider: "anthropic" (default) | "openai"
    Compiles the system prompt, dispatches to the correct API,
    logs to the reasoning trace.

    For Critic calls:
      Pass provider=CRITIC_PROVIDER and model=CRITIC_MODEL.
      build_prompt() will automatically load critic_gpt.md for openai.
    """
    system_prompt = build_prompt(
        role, context,
        trait_profile=trait_profile,
        brief_doc=brief_doc,
        provider=provider
    )

    if provider == "openai":
        result = _call_openai(system_prompt, user_message, model, max_tokens)
    else:
        result = _call_anthropic(system_prompt, user_message, model, max_tokens)

    scribe_log(
        blackboard,
        role=role.upper(),
        action="api_call",
        summary=(f"[{provider}] Responded to: '{user_message[:80]}...'"
                 if len(user_message) > 80
                 else f"[{provider}] Responded to: '{user_message}'")
    )

    return result


# -- Routing Classifier --------------------------------------------------------

def route_session(user_prompt, prompts_dir=PROMPTS_DIR):
    """
    Classify the session's primary orientation and select models.

    Returns a dict:
      {
        "orientation":       "creative" | "strategic" | "balanced",
        "orientation_score": float (0.0=strategic, 1.0=creative),
        "primary_provider":  "anthropic" | "openai",
        "critic_provider":   "openai"    | "anthropic",
        "director_model":    str,
        "session_model":     str,
        "critic_model":      str,
        "tiebreaker_used":   bool,
        "tiebreaker_answers": list,
        "rationale":         str,
      }

    Classification logic:
      Score ≤ 0.35        → strategic  → Claude primary, GPT critic
      Score 0.36–0.64     → balanced   → tiebreaker questions decide
      Score ≥ 0.65        → creative   → GPT primary, Claude critic

    Uses cheapest available model on each provider for the classification call.
    Tries Anthropic first; falls back to OpenAI if unavailable.
    """

    classification_prompt = f"""You are classifying a creative problem to determine
the optimal cognitive orientation for solving it.

PROBLEM:
\"\"\"{user_prompt}\"\"\"

Analyze this problem and return ONLY a JSON object with no preamble or markdown.

ORIENTATION SCORING:
Score from 0.0 to 1.0 on this scale:
0.0 = Purely strategic (operational viability, execution, compliance, feasibility,
      stakeholder management, systems design, scaling, cost, risk — answers the
      question "how do we make this work?")
1.0 = Purely creative (identity, positioning, meaning, differentiation, brand,
      experience design, behavioral insight, cultural resonance — answers the
      question "what should this become and why will people care?")

Most problems will score between 0.2 and 0.8. A score of 0.5 is genuinely rare.

IMPORTANT: Do NOT use the presence of regulatory or governed domains as a signal
toward strategic. Those are handled by the system regardless of orientation.
Classify based on what kind of thinking the PIL most needs from the studio.

Return this JSON exactly:
{{
  "orientation_score": <float 0.0-1.0>,
  "orientation": "<creative|strategic|balanced>",
  "rationale": "<one sentence explaining the classification>"
}}

orientation must be:
  "creative"  if score >= 0.65
  "strategic" if score <= 0.35
  "balanced"  if score is between 0.36 and 0.64"""

    tiebreaker_prompt = f"""You previously classified this problem as balanced
(score between 0.36 and 0.64). Answer three tiebreaker questions to determine
whether the primary model should be creative-oriented (GPT) or strategic-oriented
(Claude).

PROBLEM:
\"\"\"{user_prompt}\"\"\"

Answer each question with either "creative" or "strategic".

Return ONLY a JSON object:
{{
  "q1": "<creative|strategic>",
  "q1_reasoning": "<one phrase>",
  "q2": "<creative|strategic>",
  "q2_reasoning": "<one phrase>",
  "q3": "<creative|strategic>",
  "q3_reasoning": "<one phrase>",
  "tiebreaker_winner": "<creative|strategic>"
}}

Questions:
Q1: What does the PIL most need to leave with — a direction to believe in,
    or a path they can execute?
    (direction to believe in = creative, path to execute = strategic)

Q2: What is the bigger risk for this problem — that the output is boring
    and generic, or that it is impractical and unworkable?
    (boring/generic = creative, impractical/unworkable = strategic)

Q3: Does this problem have a known answer that needs reframing, or an
    unknown answer that needs discovering?
    (known answer needing reframe = creative, unknown needing discovery = strategic)

tiebreaker_winner: whichever orientation appears more often in q1, q2, q3."""

    result = {
        "orientation":        "balanced",
        "orientation_score":  0.5,
        "primary_provider":   "anthropic",
        "critic_provider":    "openai",
        "director_model":     ANTHROPIC_DIRECTOR,
        "session_model":      ANTHROPIC_DEFAULT,
        "critic_model":       OPENAI_DEFAULT,
        "tiebreaker_used":    False,
        "tiebreaker_answers": [],
        "rationale":          "",
    }

    # -- Step 1: Initial classification (use Anthropic classifier) -------------
    try:
        raw = _call_anthropic(
            system_prompt="You are a concise JSON classifier. Return only valid JSON.",
            user_message=classification_prompt,
            model=ROUTING_MODEL_ANTHROPIC,
            max_tokens=300
        )
        clean  = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        parsed = json.loads(clean.strip())

        score       = float(parsed.get("orientation_score", 0.5))
        orientation = parsed.get("orientation", "balanced")
        rationale   = parsed.get("rationale", "")

        result["orientation_score"] = score
        result["orientation"]       = orientation
        result["rationale"]         = rationale

    except Exception as e:
        print(f"  ⚠ Classification call failed: {e}")
        print(f"  ⚠ Defaulting to strategic (Claude primary)")
        result["rationale"] = "Classification failed — defaulting to strategic."
        return result

    # -- Step 2: Tiebreaker if balanced ----------------------------------------
    if orientation == "balanced":
        try:
            raw2   = _call_anthropic(
                system_prompt="You are a concise JSON classifier. Return only valid JSON.",
                user_message=tiebreaker_prompt,
                model=ROUTING_MODEL_ANTHROPIC,
                max_tokens=300
            )
            clean2 = raw2.strip()
            if clean2.startswith("```"):
                clean2 = clean2.split("```")[1]
                if clean2.startswith("json"):
                    clean2 = clean2[4:]
            parsed2 = json.loads(clean2.strip())

            winner   = parsed2.get("tiebreaker_winner", "strategic")
            answers  = [
                f"Q1: {parsed2.get('q1','')} — {parsed2.get('q1_reasoning','')}",
                f"Q2: {parsed2.get('q2','')} — {parsed2.get('q2_reasoning','')}",
                f"Q3: {parsed2.get('q3','')} — {parsed2.get('q3_reasoning','')}",
            ]
            result["tiebreaker_used"]    = True
            result["tiebreaker_answers"] = answers
            result["orientation"]        = winner

        except Exception as e:
            print(f"  ⚠ Tiebreaker call failed: {e}")
            print(f"  ⚠ Defaulting balanced → strategic (Claude primary)")
            result["orientation"] = "strategic"

    # -- Step 3: Set provider and model constants ------------------------------
    if result["orientation"] == "creative":
        result["primary_provider"] = "openai"
        result["critic_provider"]  = "anthropic"
        result["director_model"]   = OPENAI_DIRECTOR
        result["session_model"]    = OPENAI_DEFAULT
        result["critic_model"]     = ANTHROPIC_DEFAULT
    else:
        # strategic or balanced-resolved-to-strategic
        result["primary_provider"] = "anthropic"
        result["critic_provider"]  = "openai"
        result["director_model"]   = ANTHROPIC_DIRECTOR
        result["session_model"]    = ANTHROPIC_DEFAULT
        result["critic_model"]     = OPENAI_DEFAULT

    return result


# -- Baseline Generation -------------------------------------------------------

def generate_baseline(user_prompt, model=ANTHROPIC_DEFAULT,
                      provider="anthropic"):
    """
    Zero-shot Control B baseline. Uses primary provider's session-tier model.
    Architecture is the isolated variable — same model tier, no studio context.
    """
    message = (
        f"Please help me with the following:\n\n{user_prompt}\n\n"
        "Give me your best thinking on this. Be direct and practical."
    )
    if provider == "openai":
        response = _openai_client.chat.completions.create(
            model=model,
            max_completion_tokens=800,
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    else:
        response = _anthropic_client.messages.create(
            model=model,
            max_tokens=800,
            messages=[{"role": "user", "content": message}]
        )
        return response.content[0].text


# -- Evaluation Payload Assembly -----------------------------------------------

def assemble_evaluation_payload(blackboard, baseline_response):
    """Package evaluation fields into blackboard at session end."""
    blackboard["evaluation_payload"] = {
        "problem_prompt":               blackboard.get("user_prompt", ""),
        "control_group_baseline":       baseline_response,
        "experimental_group_synthesis": blackboard.get(
            "final_synthesis", {}).get("summary", "")
    }


# -- Session Persistence -------------------------------------------------------

def save_session(blackboard, sessions_dir=None):
    """Save the Blackboard to a timestamped JSON file."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    session_id = blackboard["session_metadata"]["session_id"][:8]
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = Path(sessions_dir) / f"session_{timestamp}_{session_id}.json"
    with open(filename, "w") as f:
        json.dump(blackboard, f, indent=2, default=str)
    return str(filename)


def load_session(session_id, sessions_dir=None):
    """Load a saved session Blackboard from disk."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    sessions_dir = Path(sessions_dir)
    matches      = list(sessions_dir.glob(f"session_*_{session_id[:8]}*.json"))
    if not matches:
        matches = [p for p in sessions_dir.glob("session_*.json")
                   if session_id in p.name]
    if not matches:
        raise FileNotFoundError(f"No session found matching ID: {session_id}")
    with open(sorted(matches)[-1]) as f:
        return json.load(f)


def list_sessions(sessions_dir=None):
    """List all saved sessions with key metadata."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    sessions_dir = Path(sessions_dir)
    if not sessions_dir.exists():
        return []
    results = []
    for path in sorted(sessions_dir.glob("session_*.json"), reverse=True):
        try:
            with open(path) as f:
                data = json.load(f)
            meta     = data.get("session_metadata", {})
            routing  = data.get("routing", {})
            synthesis= data.get("final_synthesis", {})
            results.append({
                "session_id":       meta.get("session_id", "")[:8],
                "timestamp":        meta.get("timestamp", "")[:16],
                "user_prompt":      data.get("user_prompt", "")[:80],
                "primary_provider": routing.get("primary_provider", ""),
                "orientation":      routing.get("orientation", ""),
                "final_direction":  synthesis.get("final_direction"),
                "reasoning_steps":  len(data.get("reasoning_trace", [])),
                "filename":         path.name
            })
        except Exception:
            continue
    return results


def print_sessions(sessions_dir=None):
    """Print a readable table of all saved sessions."""
    sessions = list_sessions(sessions_dir)
    if not sessions:
        print("No sessions found in sessions_hybrid/")
        return
    print("-- SAVED SESSIONS (Hybrid) ---------------------------------")
    print(f"  {'ID':<10} {'Date':<17} {'Provider':<12} {'Orient':<12} {'Prompt'}")
    for s in sessions:
        print(f"  {s['session_id']:<10} {s['timestamp']:<17} "
              f"{s['primary_provider']:<12} {s['orientation']:<12} "
              f"{s['user_prompt'][:40]}")
    print(f"  {len(sessions)} session(s) total")


# -- Engine Verification -------------------------------------------------------

def verify_engine(prompts_dir=PROMPTS_DIR):
    """Check all required files and both API clients."""
    print("-- ENGINE VERIFICATION (Hybrid) ----------------------------")
    all_ok = True

    print(f"  Anthropic client: key ...{_anthropic_key[-4:]}")
    print(f"  OpenAI client:    key ...{_openai_key[-4:]}")
    print()

    required = ["SYSTEM_PROMPT", "director", "creator", "critic", "critic_gpt",
                "researcher", "scribe", "director_extraction_games"]
    for name in required:
        fname = f"{name}.md"
        path  = Path(prompts_dir) / fname
        tag   = " <- constitutional layer" if name == "SYSTEM_PROMPT" else ""
        tag   = " <- GPT critic" if name == "critic_gpt" else tag
        if path.exists():
            print(f"  OK  prompts_hybrid/{fname}{tag}")
        else:
            print(f"  MISSING  prompts_hybrid/{fname}")
            all_ok = False

    print()
    if MATRIX_PATH.exists():
        traits = load_traits_matrix()
        print(f"  OK  persona_traits_matrix_v2.csv ({len(traits)} active traits)")
    else:
        print(f"  MISSING  persona_traits_matrix_v2.csv")
        all_ok = False

    print()
    if all_ok:
        foundation = _get_system_foundation(prompts_dir)
        print(f"  System foundation: ~{len(foundation)//4} tokens")
        print(f"  All checks passed — hybrid engine ready")
    else:
        print(f"  Missing files — fix before running sessions")
        print(f"  Setup: mkdir prompts_hybrid && cp prompts/* prompts_hybrid/")
        print(f"  Then create: prompts_hybrid/critic_gpt.md")
    print("------------------------------------------------------------")
    return all_ok


if __name__ == "__main__":
    verify_engine()
