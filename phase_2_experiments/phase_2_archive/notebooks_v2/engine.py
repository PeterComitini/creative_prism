# Creative Prisim — Core Engine
# The Intelligence of Seeing (IOS)
# Version 1.2
#
# IoS Experimental Instrument — Do Not Refactor Without Explicit Approval
#
# Changes in v1.2:
#   - Schema v2.2: director_summary in session_metadata
#   - Schema v2.2: idea_space with per-idea influences and refinement_history
#   - Schema v2.2: reasoning_trace entries include target field
#   - scribe_log() accepts optional target parameter
#   - Environment setup and API client
#   - Blackboard state model
#   - Scribe logging
#   - Traits system and role weight profiles
#   - Prompt compiler (constitutional layer + role identity + trait guidance)
#   - API call function
#   - Session persistence
#
# Usage:
#   from engine import (
#       client, create_blackboard, scribe_log,
#       build_prompt, call_role, save_session,
#       ROLE_WEIGHTS, GLOBAL_MODES, apply_global_mode,
#       DEFAULT_MODEL
#   )

import os
import json
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
import anthropic

# ── Environment Setup ─────────────────────────────────────────────────────────

load_dotenv(find_dotenv())
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY not found.\n"
        "Create a .env file in your project root with: ANTHROPIC_API_KEY=your_key_here"
    )

client = anthropic.Anthropic(api_key=api_key)

# ── Model Configuration ───────────────────────────────────────────────────────

# Haiku: fast and cheap for development and testing
# Swap to claude-sonnet-4-6 for quality demo runs
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# ── Prompts Directory ─────────────────────────────────────────────────────────

PROMPTS_DIR = Path(__file__).parent / "prompts"
SESSIONS_DIR = Path(__file__).parent / "sessions"

# ── Blackboard ────────────────────────────────────────────────────────────────

def create_blackboard(user_prompt: str, system_version: str = "1.2") -> dict:
    """
    Initialize a fresh Blackboard for a new studio session.

    The Blackboard is the complete archival record of a session.
    Schema v2.2 additions from original G-S-A-C design:
      - session_metadata.director_summary: high-level summary written at session end
      - idea_space: per-idea tracking with influences and refinement_history
      - reasoning_trace.target: what Blackboard object each action was targeting
    """
    return {
        "session_metadata": {
            "session_id":       str(uuid.uuid4()),
            "timestamp":        datetime.now().isoformat(),
            "system_version":   system_version,
            "schema_version":   "2.2",
            "environment":      "Creative Prisim Studio",
            "director_model":   DEFAULT_MODEL,
            "director_summary": "",   # ← Written by Director at session end
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
        # Each entry: {research_id, initiated_by, query, sources,
        #              summary, influence_on_ideation}

        "idea_space": [],
        # Per-idea tracking — populated as ideation runs.
        # Each entry: {idea_id, origin_role, idea_description, rationale,
        #              influences, critique_notes, refinement_history}
        # influences: list of research_ids or idea_ids that shaped this idea
        # refinement_history: list of changes made through the Critic dialogue

        "ideation_cycles": [],
        # Each entry: {cycle_number, creator_proposals, critic_feedback,
        #              synthesized_directions}

        "candidate_set": [],
        # Each entry: {direction_id, internal_type, description,
        #              reasoning_summary, research_influences, critic_assessment}

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
        # Each entry: {step, timestamp, role, action, target, summary}
        # target: which Blackboard object the action was acting on
    }


# ── Scribe ────────────────────────────────────────────────────────────────────

def scribe_log(blackboard: dict, role: str, action: str, summary: str,
               target: str = "") -> None:
    """
    Append a step to the reasoning trace.
    Full summary stored — no truncation.
    target: which Blackboard object this action was acting on
            e.g. "creative_brief", "ideation_cycles[0]", "candidate_set"
    This chronological log is the session's semantic trajectory —
    the raw data for Phase 3 VECTOR-style visualization.
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



# ── Studio Brief Document ─────────────────────────────────────────────────────
#
# The Studio Brief Document is the shared working memory of the session.
# It lives as a markdown file in sessions/ and is passed to every role call.
# Unlike the Blackboard (complete archival record), the Brief Document is
# the live working document — the thing pinned to the studio wall that
# everyone reads and contributes to.

def create_brief_doc(session_id: str, user_prompt: str,
                     sessions_dir: Path = None) -> Path:
    """
    Create a new Studio Brief Document for a session.
    Returns the path to the created file.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    path = sessions_dir / f"brief_{session_id}.md"

    content = f"""# STUDIO BRIEF DOCUMENT
## Creative Prisim — The Intelligence of Seeing
**Session:** {session_id}
**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## SESSION

**Initial Request:** {user_prompt}

---

*This document is the shared working memory of the studio session.
Every role reads this document before acting. Every role that contributes
to the session appends their section here.*

"""
    path.write_text(content, encoding="utf-8")
    return path


def update_brief_doc(session_id: str, role: str, section_title: str,
                     content: str, sessions_dir: Path = None) -> None:
    """
    Append a new section to the Studio Brief Document.

    Args:
        session_id    : the current session ID
        role          : which role is writing (DIRECTOR, RESEARCHER, etc.)
        section_title : the section heading
        content       : the content to append
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    path = sessions_dir / f"brief_{session_id}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Brief document not found for session {session_id}.\n"
            f"Call create_brief_doc() first."
        )
    timestamp = datetime.now().strftime('%H:%M')
    addition = f"\n---\n\n## {section_title}\n*{role} — {timestamp}*\n\n{content}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(addition)


def read_brief_doc(session_id: str, sessions_dir: Path = None) -> str:
    """
    Read the current Studio Brief Document for a session.
    Returns the full document as a string.
    This is passed to every role call as shared context.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    path = sessions_dir / f"brief_{session_id}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# ── Traits System ─────────────────────────────────────────────────────────────

ROLE_WEIGHTS = {
    "creator": {
        "divergence":          0.9,
        "novelty":             0.85,
        "playfulness":         0.7,
        "practicality":        0.4,
        "clarity":             0.6,
        "depth":               0.6,
        "convergence":         0.2,
        "critical_strictness": 0.1,
        "bias_toward_action":  0.3
    },
    "critic": {
        "divergence":          0.2,
        "novelty":             0.3,
        "playfulness":         0.2,
        "practicality":        0.9,
        "clarity":             0.85,
        "depth":               0.9,
        "convergence":         0.85,
        "critical_strictness": 0.9,
        "bias_toward_action":  0.6
    },
    "director": {
        "divergence":          0.5,
        "novelty":             0.5,
        "playfulness":         0.3,
        "practicality":        0.8,
        "clarity":             0.9,
        "depth":               0.8,
        "convergence":         0.9,
        "critical_strictness": 0.6,
        "bias_toward_action":  0.9
    },
    "researcher": {
        "divergence":          0.3,
        "novelty":             0.2,
        "playfulness":         0.1,
        "practicality":        0.9,
        "clarity":             0.9,
        "depth":               0.8,
        "convergence":         0.7,
        "critical_strictness": 0.5,
        "bias_toward_action":  0.4
    },
    "scribe": {
        "divergence":          0.1,
        "novelty":             0.1,
        "playfulness":         0.0,
        "practicality":        0.8,
        "clarity":             1.0,
        "depth":               0.7,
        "convergence":         0.9,
        "critical_strictness": 0.2,
        "bias_toward_action":  0.3
    }
}

GLOBAL_MODES = {
    "exploratory": {
        "divergence":          +0.2,
        "novelty":             +0.2,
        "critical_strictness": -0.2,
        "convergence":         -0.2
    },
    "execution": {
        "practicality":        +0.2,
        "convergence":         +0.3,
        "bias_toward_action":  +0.3,
        "divergence":          -0.3
    },
    "balanced": {}
}


def apply_global_mode(weights: dict, mode: str = "balanced") -> dict:
    """
    Apply a global personality mode modifier to a role's weight profile.
    Returns a new dict — does not mutate the original.
    Values are clamped to [0.0, 1.0].
    """
    modifier = GLOBAL_MODES.get(mode, {})
    return {
        trait: max(0.0, min(1.0, weights[trait] + modifier.get(trait, 0.0)))
        for trait in weights
    }


# ── Prompt Compiler ───────────────────────────────────────────────────────────

HIGH_THRESHOLD = 0.75
LOW_THRESHOLD  = 0.25

TRAIT_INSTRUCTIONS = {
    "divergence": {
        "high": "Generate multiple distinct and varied approaches. Resist the pull toward "
                "obvious solutions. Explore the edges of the problem space.",
        "low":  "Focus tightly. Generate one or two well-considered directions rather "
                "than a wide range."
    },
    "novelty": {
        "high": "Prioritize originality. Seek lateral connections, unexpected analogies, "
                "and ideas that challenge conventional approaches.",
        "low":  "Stay within familiar, proven territory. Prioritize reliability over surprise."
    },
    "playfulness": {
        "high": "Bring imaginative energy. Experiment freely. Unusual framings and "
                "speculative ideas are welcome.",
        "low":  "Maintain a formal, restrained tone. Prioritize precision over expression."
    },
    "practicality": {
        "high": "Keep ideas grounded in real-world feasibility. Every proposal should "
                "be implementable.",
        "low":  "Speculative and conceptual ideas are welcome. Feasibility is secondary "
                "to exploratory value."
    },
    "critical_strictness": {
        "high": "Apply rigorous evaluation. Identify weaknesses clearly. Do not let "
                "weak ideas pass without challenge.",
        "low":  "Be permissive. The goal is exploration, not filtering."
    },
    "clarity": {
        "high": "Write with maximum clarity. Use clean structure, plain language, "
                "and logical organization.",
        "low":  "Density and abstraction are acceptable. Prioritize richness over readability."
    },
    "depth": {
        "high": "Go deep. Provide layered reasoning. Explain the why behind each "
                "idea or evaluation.",
        "low":  "Stay at surface level. Concise observations are sufficient."
    },
    "convergence": {
        "high": "Move toward synthesis and decision. Reduce options. Identify the "
                "strongest directions.",
        "low":  "Stay in exploration mode. Avoid narrowing prematurely."
    },
    "bias_toward_action": {
        "high": "Push toward outcomes. Make recommendations. Move the process forward.",
        "low":  "Remain exploratory. Resist pressure to conclude."
    }
}

# Cache system foundation in memory — loaded once per process
_SYSTEM_FOUNDATION = None


def _load_system_prompt(prompts_dir: Path = PROMPTS_DIR) -> str:
    path = prompts_dir / "SYSTEM_PROMPT.md"
    if not path.exists():
        raise FileNotFoundError(
            f"SYSTEM_PROMPT.md not found at {path.resolve()}\n"
            "This file is the constitutional foundation for all role calls."
        )
    return path.read_text(encoding="utf-8")


def _get_system_foundation(prompts_dir: Path = PROMPTS_DIR) -> str:
    global _SYSTEM_FOUNDATION
    if _SYSTEM_FOUNDATION is None:
        _SYSTEM_FOUNDATION = _load_system_prompt(prompts_dir)
    return _SYSTEM_FOUNDATION


def _load_role_prompt(role: str, prompts_dir: Path = PROMPTS_DIR) -> str:
    path = prompts_dir / f"{role}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Role prompt file not found: {path.resolve()}\n"
            f"Make sure the prompts/ folder contains {role}.md"
        )
    return path.read_text(encoding="utf-8")


def build_prompt(
    role: str,
    weights: dict,
    context: str,
    mode: str = "balanced",
    prompts_dir: Path = PROMPTS_DIR,
    brief_doc: str = ""
) -> str:
    """
    Compile a complete system prompt for a studio role.

    Structure:
      1. System Foundation  — System Laws + HCD standard (shared, cached)
      2. Role Identity      — role-specific .md file
      3. Behavioral Guidance — derived from trait weights and global mode
      4. Task Context       — the current brief or problem

    The System Foundation is identical across all calls in a session,
    enabling Anthropic prompt caching (~90% cost reduction after first call).
    """
    effective_weights = apply_global_mode(weights, mode)
    system_foundation = _get_system_foundation(prompts_dir)
    role_identity     = _load_role_prompt(role, prompts_dir)

    behavioral_instructions = []
    for trait, value in effective_weights.items():
        if trait in TRAIT_INSTRUCTIONS:
            if value >= HIGH_THRESHOLD:
                behavioral_instructions.append(TRAIT_INSTRUCTIONS[trait]["high"])
            elif value <= LOW_THRESHOLD:
                behavioral_instructions.append(TRAIT_INSTRUCTIONS[trait]["low"])

    parts = [system_foundation, "\n\n---", role_identity]

    if behavioral_instructions:
        parts.append("\n\n---\n## Behavioral Guidance for This Session")
        for instruction in behavioral_instructions:
            parts.append(f"- {instruction}")

    if brief_doc and brief_doc.strip():
        parts.append(f"\n\n---\n## STUDIO BRIEF DOCUMENT\n"
                     f"*This is the shared working memory of the current session. "
                     f"Read this before acting.*\n\n{brief_doc}")

    parts.append(f"\n\n---\n## Current Task Context\n{context}")

    return "\n".join(parts)


# ── API Call ──────────────────────────────────────────────────────────────────

def call_role(
    role: str,
    user_message: str,
    weights: dict,
    context: str,
    blackboard: dict,
    mode: str = "balanced",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    brief_doc: str = ""
) -> str:
    """
    Make a single API call as a studio role.
    Compiles the system prompt, calls the API, logs to the reasoning trace.

    Args:
        role         : studio role name
        user_message : the specific instruction for this call
        weights      : trait weights for this role
        context      : creative brief or task description
        blackboard   : the session blackboard (for Scribe logging)
        mode         : global personality mode
        model        : Claude model string
        max_tokens   : response length limit

    Returns:
        The role's response as a string.
    """
    system_prompt = build_prompt(role, weights, context, mode, brief_doc=brief_doc)
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



# ── Session Persistence ───────────────────────────────────────────────────────

def save_session(blackboard: dict,
                 sessions_dir: Path = None) -> str:
    """
    Save the Blackboard to a timestamped JSON file.
    Full content — nothing truncated.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)
    session_id = blackboard["session_metadata"]["session_id"][:8]
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = sessions_dir / f"session_{timestamp}_{session_id}.json"
    with open(filename, "w") as f:
        json.dump(blackboard, f, indent=2, default=str)
    return str(filename)


def load_session(session_id: str,
                 sessions_dir: Path = None) -> dict:
    """
    Load a saved session Blackboard from disk.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    sessions_dir = Path(sessions_dir)
    matches = list(sessions_dir.glob(f"session_*_{session_id[:8]}*.json"))
    if not matches:
        matches = [p for p in sessions_dir.glob("session_*.json")
                   if session_id in p.name]
    if not matches:
        raise FileNotFoundError(
            f"No session found matching ID: {session_id}\n"
            f"Run list_sessions() to see all available sessions."
        )
    latest = sorted(matches)[-1]
    with open(latest) as f:
        return json.load(f)


def list_sessions(sessions_dir: Path = None) -> list:
    """
    List all saved sessions with key metadata.
    """
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


def print_sessions(sessions_dir: Path = None) -> None:
    """Print a readable table of all saved sessions."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    sessions = list_sessions(sessions_dir)
    if not sessions:
        print("No sessions found in sessions/")
        return
    print("── SAVED SESSIONS ──────────────────────────────────────────")
    print(f"  {'ID':<10} {'Date':<17} {'Steps':<7} {'Prompt'}")
    print(f"  {'─'*8} {'─'*15} {'─'*5} {'─'*50}")
    for s in sessions:
        print(f"  {s['session_id']:<10} {s['timestamp']:<17} "
              f"{s['reasoning_steps']:<7} {s['user_prompt'][:60]}")
    print(f"  {len(sessions)} session(s) total")
    print("────────────────────────────────────────────────────────────")


# ── Engine Verification ───────────────────────────────────────────────────────

def verify_engine(prompts_dir: Path = PROMPTS_DIR) -> bool:
    """
    Check that all required prompt files exist and the API client is ready.
    Returns True if all checks pass, False otherwise.
    Prints a status report.
    """
    print("── ENGINE VERIFICATION ─────────────────────────────────────")
    all_ok = True

    # API client
    print(f"  ✓ API client initialized")
    print(f"  ✓ Key loaded: {api_key[:8]}...{api_key[-4:]}")
    print(f"  ✓ Default model: {DEFAULT_MODEL}")
    print()

    # Prompt files
    required = ["SYSTEM_PROMPT"] + [
        "director", "creator", "critic", "researcher", "scribe",
        "director_extraction_games"
    ]
    for name in required:
        fname = f"{name}.md"
        path  = prompts_dir / fname
        tag   = "← constitutional layer" if name == "SYSTEM_PROMPT" else ""
        if path.exists():
            print(f"  ✓  prompts/{fname}  {tag}")
        else:
            print(f"  ✗  prompts/{fname}  MISSING")
            all_ok = False

    print()
    if all_ok:
        foundation = _get_system_foundation(prompts_dir)
        print(f"  ✓ System foundation: ~{len(foundation)//4} tokens (cached after first call)")
        print(f"  ✓ All checks passed — engine ready")
    else:
        print(f"  ✗ Missing files — fix before running sessions")

    print("────────────────────────────────────────────────────────────")
    return all_ok


# ── Run verification on import (silent in production, useful in dev) ──────────
if __name__ == "__main__":
    verify_engine()
