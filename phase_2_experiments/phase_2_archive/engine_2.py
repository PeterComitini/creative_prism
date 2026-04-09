# Creative Prism — Core Engine
# Version 2.0
#
# Changes in v2.0:
#   - Name cleanup: all references updated to "Creative Prism"
#   - Traits matrix system replaces old 9-trait ROLE_WEIGHTS
#   - load_traits_matrix() reads persona_traits_matrix_v2.csv
#   - weight_to_band() converts numeric weights to five-band language directives
#   - build_trait_profile() assembles natural language trait blocks for prompt injection
#   - create_blackboard() accepts director_model parameter (Bug 2 fix)
#   - read_brief_doc() accepts max_chars parameter (Bug 6 fix)
#   - build_prompt() uses trait profile system instead of old TRAIT_INSTRUCTIONS
#   - call_role() simplified — no weights/mode params, accepts trait_profile string
#   - Old system removed: ROLE_WEIGHTS, GLOBAL_MODES, TRAIT_INSTRUCTIONS, apply_global_mode
#   - Studio Brief Document header updated to "Creative Prism"
#
# Usage:
#   from engine import (
#       client, create_blackboard, scribe_log,
#       build_prompt, call_role, save_session, verify_engine,
#       create_brief_doc, update_brief_doc, read_brief_doc,
#       load_traits_matrix, weight_to_band, build_trait_profile,
#       validate_stage, DEFAULT_MODEL
#   )

import os
import csv
import json
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
import anthropic

# -- Environment Setup -----------------------------------------------------

load_dotenv(find_dotenv())
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY not found.\n"
        "Create a .env file in your project root with: ANTHROPIC_API_KEY=your_key_here"
    )

client = anthropic.Anthropic(api_key=api_key)

# -- Model Configuration ---------------------------------------------------

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# -- Directories -----------------------------------------------------------

PROMPTS_DIR = Path(__file__).parent / "prompts"
SESSIONS_DIR = Path(__file__).parent / "sessions"
MATRIX_PATH = Path(__file__).parent / "persona_traits_matrix_v2.csv"


# -- Blackboard ------------------------------------------------------------

def create_blackboard(user_prompt, system_version="2.0",
                      director_model=DEFAULT_MODEL):
    """
    Initialize a fresh Blackboard for a new studio session.
    Schema v2.2. The director_model parameter records the actual model
    used for Director calls in session metadata.
    """
    return {
        "session_metadata": {
            "session_id":       str(uuid.uuid4()),
            "timestamp":        datetime.now().isoformat(),
            "system_version":   system_version,
            "schema_version":   "2.2",
            "environment":      "Creative Prism Studio",
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
        "research_trace": [],
        "idea_space": [],
        "ideation_cycles": [],
        "candidate_set": [],
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
        "reasoning_trace": []
    }


# -- Scribe ----------------------------------------------------------------

def scribe_log(blackboard, role, action, summary, target=""):
    """
    Append a step to the reasoning trace.
    Full summary stored — no truncation.
    """
    step = len(blackboard["reasoning_trace"]) + 1
    blackboard["reasoning_trace"].append({
        "step":      step,
        "timestamp": datetime.now().isoformat(),
        "role":      role,
        "action":    action,
        "target":    target,
        "summary":   summary
    })


# -- Stage Validation ------------------------------------------------------

def validate_stage(blackboard, stage_name):
    """
    Validate that a pipeline stage completed successfully.
    Pure Python — no API call. Raises RuntimeError on failure.
    """
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


# -- Studio Brief Document ------------------------------------------------

def create_brief_doc(session_id, user_prompt, sessions_dir=None):
    """Create a new Studio Brief Document for a session."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    path = sessions_dir / f"brief_{session_id}.md"
    content = (
        f"# STUDIO BRIEF DOCUMENT\n"
        f"## The Creative Prism\n"
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
    path = sessions_dir / f"brief_{session_id}.md"
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
    Loads only the most recent max_chars of the brief.
    The brief grows throughout the session — loading the full document
    into every call causes token accumulation and silent truncation.
    Most recent content is what active roles need.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    path = sessions_dir / f"brief_{session_id}.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return "...[earlier content compressed]...\n\n" + text[-max_chars:]


# -- Traits Matrix System --------------------------------------------------

def load_traits_matrix(matrix_path=None):
    """
    Load the persona traits matrix from CSV.
    Returns a list of dicts, one per active trait.
    Skips comment lines (starting with #) and inactive traits.
    Uses csv module — no pandas dependency.
    """
    if matrix_path is None:
        matrix_path = MATRIX_PATH
    matrix_path = Path(matrix_path)
    if not matrix_path.exists():
        raise FileNotFoundError(
            f"Traits matrix not found: {matrix_path}\n"
            f"Place persona_traits_matrix_v2.csv next to engine.py.")

    traits = []
    with open(matrix_path, 'r', encoding='utf-8') as f:
        # Read all lines, skip comments and blanks
        lines = [line for line in f
                 if line.strip() and not line.strip().startswith('#')]

    reader = csv.DictReader(lines)
    float_cols = [
        'creator_base', 'creator_min', 'creator_max',
        'critic_base', 'critic_min', 'critic_max',
        'researcher_base', 'researcher_min', 'researcher_max',
        'scribe_base', 'scribe_min', 'scribe_max'
    ]
    for row in reader:
        # Skip inactive traits
        try:
            active = int(float(row.get('Active', '0')))
        except (ValueError, TypeError):
            active = 0
        if not active:
            continue

        # Convert numeric columns
        for col in float_cols:
            try:
                row[col] = float(row[col])
            except (ValueError, TypeError, KeyError):
                row[col] = 0.0

        traits.append(row)

    return traits


def weight_to_band(value):
    """
    Converts a numeric trait weight to a five-band language directive.
    Bands are absolute — same scale regardless of role.
    """
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
    """
    Builds the natural language trait profile block for a given role.

    Args:
        role: "creator", "critic", "researcher", or "scribe"
        session_adjustments: dict of trait_name -> adjusted_value.
            If a trait is not in session_adjustments, use the base value.
        traits_matrix: list of dicts from load_traits_matrix()

    Returns: string — the assembled trait profile block for prompt injection
    """
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
            continue  # Trait does not apply to this role

        trait_name = trait_row['trait']
        # Use session adjustment if provided, else base
        effective = session_adjustments.get(trait_name, base_val)

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
    """
    Returns a list of traits the Director can adjust for this role.
    A trait is tunable if min != max for the role.
    Returns list of dicts with trait, base, min, max, description.
    """
    base_col = f"{role}_base"
    min_col = f"{role}_min"
    max_col = f"{role}_max"

    tunable = []
    for row in traits_matrix:
        base_val = row.get(base_col, 0.0)
        min_val = row.get(min_col, 0.0)
        max_val = row.get(max_col, 0.0)
        if base_val <= 0.0:
            continue
        if min_val == max_val:
            continue  # Fixed trait — not tunable
        tunable.append({
            "trait": row['trait'],
            "category": row.get('category', ''),
            "base": base_val,
            "min": min_val,
            "max": max_val,
            "description": row.get('description', '')
        })
    return tunable


def validate_adjustments(role, adjustments, traits_matrix):
    """
    Validate and clamp Director's trait adjustments to allowed ranges.
    Returns cleaned dict and list of any warnings.
    """
    min_col = f"{role}_min"
    max_col = f"{role}_max"

    # Build lookup
    ranges = {}
    for row in traits_matrix:
        ranges[row['trait']] = (row.get(min_col, 0.0), row.get(max_col, 0.0))

    cleaned = {}
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


# -- Prompt Compiler -------------------------------------------------------

_SYSTEM_FOUNDATION = None


def _load_system_prompt(prompts_dir=PROMPTS_DIR):
    path = prompts_dir / "SYSTEM_PROMPT.md"
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
    path = prompts_dir / f"{role}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Role prompt file not found: {path.resolve()}\n"
            f"Make sure the prompts/ folder contains {role}.md")
    return path.read_text(encoding="utf-8")


def build_prompt(role, context, trait_profile="", brief_doc="",
                 prompts_dir=PROMPTS_DIR):
    """
    Compile a complete system prompt for a studio role.

    Structure:
      1. System Foundation  — System Laws + HCD standard (shared, cached)
      2. Role Identity      — role-specific .md file
      3. Trait Profile      — session-configured personality (from matrix)
      4. Studio Brief Doc   — shared working memory
      5. Task Context       — the current brief or problem

    The System Foundation is identical across all calls in a session,
    enabling Anthropic prompt caching (~90% cost reduction after first call).
    """
    system_foundation = _get_system_foundation(prompts_dir)
    role_identity = _load_role_prompt(role, prompts_dir)

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


# -- API Call --------------------------------------------------------------

def call_role(role, user_message, context, blackboard,
              model=DEFAULT_MODEL, max_tokens=1024,
              trait_profile="", brief_doc=""):
    """
    Make a single API call as a studio role.
    Compiles the system prompt, calls the API, logs to the reasoning trace.
    """
    system_prompt = build_prompt(
        role, context, trait_profile=trait_profile, brief_doc=brief_doc)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    result = response.content[0].text

    scribe_log(
        blackboard,
        role=role.upper(),
        action="api_call",
        summary=(f"Responded to: '{user_message[:80]}...'"
                 if len(user_message) > 80
                 else f"Responded to: '{user_message}'")
    )

    return result


# -- Session Persistence ---------------------------------------------------

def save_session(blackboard, sessions_dir=None):
    """Save the Blackboard to a timestamped JSON file."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    session_id = blackboard["session_metadata"]["session_id"][:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = sessions_dir / f"session_{timestamp}_{session_id}.json"
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
        raise FileNotFoundError(
            f"No session found matching ID: {session_id}")
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
            meta = data.get("session_metadata", {})
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
        print("No sessions found in sessions/")
        return
    print("-- SAVED SESSIONS ------------------------------------------")
    print(f"  {'ID':<10} {'Date':<17} {'Steps':<7} {'Prompt'}")
    for s in sessions:
        print(f"  {s['session_id']:<10} {s['timestamp']:<17} "
              f"{s['reasoning_steps']:<7} {s['user_prompt'][:60]}")
    print(f"  {len(sessions)} session(s) total")


# -- Engine Verification ---------------------------------------------------

def verify_engine(prompts_dir=PROMPTS_DIR):
    """
    Check that all required files exist and the API client is ready.
    Returns True if all checks pass.
    """
    print("-- ENGINE VERIFICATION -------------------------------------")
    all_ok = True

    print(f"  API client initialized")
    print(f"  Key loaded: {api_key[:8]}...{api_key[-4:]}")
    print(f"  Default model: {DEFAULT_MODEL}")
    print()

    # Prompt files
    required = ["SYSTEM_PROMPT", "director", "creator", "critic",
                "researcher", "scribe", "director_extraction_games"]
    for name in required:
        fname = f"{name}.md"
        path = prompts_dir / fname
        tag = " <- constitutional layer" if name == "SYSTEM_PROMPT" else ""
        if path.exists():
            print(f"  OK  prompts/{fname}{tag}")
        else:
            print(f"  MISSING  prompts/{fname}")
            all_ok = False

    # Traits matrix
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
        print(f"  System foundation: ~{len(foundation)//4} tokens (cached)")
        print(f"  All checks passed — engine ready")
    else:
        print(f"  Missing files — fix before running sessions")

    print("------------------------------------------------------------")
    return all_ok


if __name__ == "__main__":
    verify_engine()
