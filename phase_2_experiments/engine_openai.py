# Creative Prism — OpenAI Engine
# Version 1.0
#
# Parallel engine to engine.py v2.1.
# Identical architecture and API surface — only the model provider changes.
#
# Provider:      OpenAI (gpt-5.4 / gpt-5.4-mini)
# Prompt dirs:   prompts_openai/   (independent copy — do not share with prompts/)
# Sessions dir:  sessions_openai/  (independent — do not mix with sessions/)
#
# API differences from engine.py:
#   - client.chat.completions.create() instead of client.messages.create()
#   - System prompt passed as {"role": "developer"} message (OpenAI convention)
#   - Response extracted via response.choices[0].message.content
#   - OPENAI_API_KEY environment variable
#
# Token limit notes (vs Claude version):
#   GPT models are slightly more verbose in formatted outputs.
#   Three calls carry adjusted limits — see call sites in notebook:
#     Cell 4  Stage 1 Discovery:          600 → 800
#     Cell 8  Stage 5/6 Director Review:  800 → 1000  (JSON — critical)
#     Cell 11 Stage 9 Final Synthesis:   1400 → 1600
#   All other limits are unchanged from the Claude version.
#
# Setup (one time):
#   mkdir prompts_openai && cp prompts/* prompts_openai/
#   mkdir sessions_openai
#   Add OPENAI_API_KEY to your .env file
#
# Usage:
#   from engine_openai import (
#       client, create_blackboard, scribe_log,
#       build_prompt, call_role, save_session, verify_engine,
#       create_brief_doc, update_brief_doc, read_brief_doc,
#       load_traits_matrix, weight_to_band, build_trait_profile,
#       get_tunable_traits, validate_adjustments,
#       validate_stage, generate_baseline, assemble_evaluation_payload,
#       DEFAULT_MODEL,
#   )

import os
import csv
import json
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# -- Environment Setup ---------------------------------------------------------

load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY not found.\n"
        "Add OPENAI_API_KEY=your_key_here to your .env file."
    )

client = OpenAI(api_key=api_key)

# -- Model Configuration -------------------------------------------------------

DEFAULT_MODEL = "gpt-5.4-mini"

# -- Directories ---------------------------------------------------------------

PROMPTS_DIR = Path(__file__).parent / "prompts_openai"
SESSIONS_DIR = Path(__file__).parent / "sessions_openai"
MATRIX_PATH  = Path(__file__).parent / "persona_traits_matrix_v2.csv"


# -- Blackboard ----------------------------------------------------------------

def create_blackboard(user_prompt, system_version="1.0",
                      director_model=DEFAULT_MODEL):
    """
    Initialize a fresh Blackboard for a new studio session.
    Schema v2.2 — identical to engine.py.
    system_version records the OpenAI engine version, not the Claude one.
    """
    return {
        "session_metadata": {
            "session_id":       str(uuid.uuid4()),
            "timestamp":        datetime.now().isoformat(),
            "system_version":   system_version,
            "schema_version":   "2.2",
            "environment":      "Creative Prism Studio — OpenAI",
            "director_model":   director_model,
            "director_summary": "",
            "notes":            ""
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
    """Append a step to the reasoning trace. Full summary stored."""
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
        brief = blackboard.get("creative_brief", {})
        missing = [f for f in ["challenge", "context", "desired_result"]
                   if not brief.get(f, "").strip()]
        if missing:
            raise RuntimeError(
                f"VALIDATION FAILED — brief: missing fields: {missing}")

    elif stage_name == "ideation":
        cycles = blackboard.get("ideation_cycles", [])
        if not cycles:
            raise RuntimeError("VALIDATION FAILED — ideation: no cycles found.")
        proposals = cycles[-1].get("creator_proposals", [])
        if not proposals or not proposals[0].get("raw_response", "").strip():
            raise RuntimeError("VALIDATION FAILED — ideation: creator_proposals empty.")

    elif stage_name == "critic":
        cycles = blackboard.get("ideation_cycles", [])
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
    path = Path(sessions_dir) / f"brief_{session_id}.md"
    content = (
        f"# STUDIO BRIEF DOCUMENT\n"
        f"## The Creative Prism — OpenAI\n"
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
            f"Brief document not found for session {session_id}.\n"
            f"Call create_brief_doc() first.")
    timestamp = datetime.now().strftime('%H:%M')
    addition = f"\n---\n\n## {section_title}\n*{role} — {timestamp}*\n\n{content}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(addition)


def read_brief_doc(session_id, max_chars=12000, sessions_dir=None):
    """
    Read the Studio Brief Document for a session.
    Loads only the most recent max_chars to prevent token accumulation.
    """
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
            f"Traits matrix not found: {matrix_path}\n"
            f"Place persona_traits_matrix_v2.csv next to engine_openai.py.")

    traits = []
    with open(matrix_path, 'r', encoding='utf-8') as f:
        lines = [line for line in f
                 if line.strip() and not line.strip().startswith('#')]

    reader = csv.DictReader(lines)
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
        "STRONGLY PRESENT (consistently expressed)": [],
        "ACTIVE AND BALANCED (apply where it serves the output)": [],
        "RESTRAINED (use sparingly)": [],
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
        trait_name = trait_row['trait']
        effective  = session_adjustments.get(trait_name, base_val)
        band_name, _ = weight_to_band(effective)
        display_name  = trait_name.replace('_', ' ')
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
        lo, hi = ranges[trait]
        if lo == hi:
            warnings.append(f"{role}: '{trait}' is fixed at {lo} — skipped")
            continue
        clamped = max(lo, min(hi, float(value)))
        if clamped != float(value):
            warnings.append(
                f"{role}: '{trait}' clamped from {value} to {clamped} "
                f"(range: {lo}-{hi})")
        cleaned[trait] = clamped
    return cleaned, warnings


# -- Prompt Compiler -----------------------------------------------------------

_SYSTEM_FOUNDATION = None


def _load_system_prompt(prompts_dir=PROMPTS_DIR):
    path = Path(prompts_dir) / "SYSTEM_PROMPT.md"
    if not path.exists():
        raise FileNotFoundError(
            f"SYSTEM_PROMPT.md not found at {path.resolve()}\n"
            "This file is the constitutional foundation for all role calls.")
    return path.read_text(encoding="utf-8")


def _get_system_foundation(prompts_dir=PROMPTS_DIR):
    global _SYSTEM_FOUNDATION
    if _SYSTEM_FOUNDATION is None:
        _SYSTEM_FOUNDATION = _load_system_prompt(prompts_dir)
    return _SYSTEM_FOUNDATION


def _load_role_prompt(role, prompts_dir=PROMPTS_DIR):
    path = Path(prompts_dir) / f"{role}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Role prompt file not found: {path.resolve()}\n"
            f"Run setup: cp prompts/* prompts_openai/")
    return path.read_text(encoding="utf-8")


def build_prompt(role, context, trait_profile="", brief_doc="",
                 prompts_dir=PROMPTS_DIR):
    """
    Compile a complete system prompt for a studio role.
    Structure identical to engine.py — only the directory changes.
    """
    system_foundation = _get_system_foundation(prompts_dir)
    role_identity     = _load_role_prompt(role, prompts_dir)

    parts = [system_foundation, "\n\n---", role_identity]

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


# -- API Call ------------------------------------------------------------------

def call_role(role, user_message, context, blackboard,
              model=DEFAULT_MODEL, max_tokens=1024,
              trait_profile="", brief_doc=""):
    """
    Make a single API call as a studio role using OpenAI Chat Completions.

    System prompt is passed as the "developer" role message — this is
    OpenAI's current convention for instruction-level context in newer models.
    User message is passed as the "user" role message as normal.

    Response extracted from response.choices[0].message.content.
    """
    system_prompt = build_prompt(
        role, context, trait_profile=trait_profile, brief_doc=brief_doc)

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "developer", "content": system_prompt},
            {"role": "user",      "content": user_message}
        ]
    )

    result = response.choices[0].message.content

    scribe_log(
        blackboard,
        role=role.upper(),
        action="api_call",
        summary=(f"Responded to: '{user_message[:80]}...'"
                 if len(user_message) > 80
                 else f"Responded to: '{user_message}'")
    )

    return result


# -- Baseline Generation -------------------------------------------------------

def generate_baseline(user_prompt, model=DEFAULT_MODEL):
    """
    Generate a zero-shot baseline response to the raw user prompt.
    Control B: no system prompt, no studio context, no multi-agent structure.
    Model should match SESSION_MODEL so architecture is the isolated variable.
    """
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=800,
        messages=[{
            "role": "user",
            "content": (
                f"Please help me with the following:\n\n{user_prompt}\n\n"
                "Give me your best thinking on this. Be direct and practical."
            )
        }]
    )
    return response.choices[0].message.content


# -- Evaluation Payload Assembly -----------------------------------------------

def assemble_evaluation_payload(blackboard, baseline_response):
    """
    Assemble the evaluation_payload block and inject into the blackboard.
    Called once at session end, before save_session().
    """
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
    matches = list(sessions_dir.glob(f"session_*_{session_id[:8]}*.json"))
    if not matches:
        matches = [p for p in sessions_dir.glob("session_*.json")
                   if session_id in p.name]
    if not matches:
        raise FileNotFoundError(f"No session found matching ID: {session_id}")
    latest = sorted(matches)[-1]
    with open(latest) as f:
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
            meta      = data.get("session_metadata", {})
            synthesis = data.get("final_synthesis", {})
            results.append({
                "session_id":      meta.get("session_id", "")[:8],
                "timestamp":       meta.get("timestamp", "")[:16],
                "user_prompt":     data.get("user_prompt", "")[:80],
                "final_direction": synthesis.get("final_direction"),
                "reasoning_steps": len(data.get("reasoning_trace", [])),
                "filename":        path.name
            })
        except Exception:
            continue
    return results


def print_sessions(sessions_dir=None):
    """Print a readable table of all saved sessions."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    sessions = list_sessions(sessions_dir)
    if not sessions:
        print("No sessions found in sessions_openai/")
        return
    print("-- SAVED SESSIONS (OpenAI) ---------------------------------")
    print(f"  {'ID':<10} {'Date':<17} {'Steps':<7} {'Prompt'}")
    for s in sessions:
        print(f"  {s['session_id']:<10} {s['timestamp']:<17} "
              f"{s['reasoning_steps']:<7} {s['user_prompt'][:60]}")
    print(f"  {len(sessions)} session(s) total")


# -- Engine Verification -------------------------------------------------------

def verify_engine(prompts_dir=PROMPTS_DIR):
    """Check that all required files exist and the OpenAI client is ready."""
    print("-- ENGINE VERIFICATION (OpenAI) ----------------------------")
    all_ok = True

    print(f"  API client initialized")
    print(f"  Key loaded: {api_key[:8]}...{api_key[-4:]}")
    print(f"  Default model: {DEFAULT_MODEL}")
    print()

    required = ["SYSTEM_PROMPT", "director", "creator", "critic",
                "researcher", "scribe", "director_extraction_games"]
    for name in required:
        fname = f"{name}.md"
        path  = Path(prompts_dir) / fname
        tag   = " <- constitutional layer" if name == "SYSTEM_PROMPT" else ""
        if path.exists():
            print(f"  OK  prompts_openai/{fname}{tag}")
        else:
            print(f"  MISSING  prompts_openai/{fname}")
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
        print(f"  All checks passed — OpenAI engine ready")
    else:
        print(f"  Missing files — fix before running sessions")

    print("------------------------------------------------------------")
    return all_ok


if __name__ == "__main__":
    verify_engine()
