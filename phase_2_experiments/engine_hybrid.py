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
import re
import csv
import json
import uuid
from pathlib import Path
from datetime import datetime

try:
    import numpy as np
    from sklearn.decomposition import PCA
    _VIZ_DEPS = True
except ImportError:
    _VIZ_DEPS = False

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

# -- Session Provider State ----------------------------------------------------
# Set once per session by the notebook (Cell 2) after routing decision.
# call_role() reads these when no provider= is passed explicitly.
# Critic role automatically uses CRITIC_PROVIDER; all others use PRIMARY_PROVIDER.

PRIMARY_PROVIDER = "anthropic"   # overwritten by notebook Cell 2
CRITIC_PROVIDER  = "openai"      # overwritten by notebook Cell 2

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

# v5.0 — Domain lens reference for Critic context block assembly
DOMAIN_LENSES = {
    "BRANDING": (
        "BRANDING: Does this direction have distinctive brand logic, or does it "
        "describe a category move anyone could make? Is the identity claim "
        "authentic or aspirational without grounding?"
    ),
    "OPERATIONS": (
        "OPERATIONS: Is this executable at the PIL's actual scale and capacity? "
        "Does it require capabilities not established in the brief? "
        "What breaks first under real conditions?"
    ),
    "REGULATORY": (
        "REGULATORY: Are there compliance implications that would block or "
        "constrain this direction? Flag but do not provide legal conclusions. "
        "Note when specialist engagement is required."
    ),
    "FINANCIAL": (
        "FINANCIAL: Is the financial logic sound? Are revenue and cost assumptions "
        "grounded in the Researcher's evidence? Flag unsupported assumptions. "
        "Is there a clear path to viability?"
    ),
    "CX": (
        "CX: Does this meaningfully change how the customer or user experiences "
        "the product or service — or only in a stated way? Is the proposed "
        "experience change realistic given this PIL's context?"
    ),
    "POSITIONING": (
        "POSITIONING: Is the competitive differentiation genuine and durable? "
        "Will it be replicated quickly? Does it create real distance from "
        "alternatives or describe a position competitors already occupy?"
    ),
    "TECHNOLOGY": (
        "TECHNOLOGY: Is this technically feasible at the scale and timeline implied? "
        "Does it require infrastructure, platform, or build capability not "
        "established in the brief? Flag when specialist assessment is required."
    ),
    "HUMAN_PROF": (
        "HUMAN/PROFESSIONAL: Do the organizational dynamics support this direction? "
        "Does it account for institutional resistance, team capacity, or professional "
        "relationship constraints? Who in the organization would block this and why?"
    ),
    "HUMAN_PERSONAL": (
        "HUMAN/PERSONAL: Does this direction account for the relational and "
        "psychological consequences for the PIL personally? Does it require a version "
        "of the PIL that may not exist yet? What does it cost them beyond resources?"
    ),
    "BEHAVIORAL": (
        "BEHAVIORAL [always active]: Is this direction actually livable or executable "
        "for this specific person? Does it ask too much, too fast? Does it underestimate "
        "resistance — internal or external? Is it grounded in how people actually "
        "behave, not how they ideally would?"
    ),
}


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
            "is_visual":          False, # DEFINITIVE: set by Director tag in Cell 16
            "is_visual_hint":     False, # HINT only: keyword scan in Cell 7
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
        "evaluation_payload": {},
        # v5.0 additions
        "session_slug":       "",
        "domain_context":     {},
        "domain_inventory": {
            "primary":      "",
            "flagged":      [],
            "missing":      [],
            "absent":       [],
            "domain_count": 0
        },
        "blind_spots":        [],
        "colophon_extended":  False,
        "pil_rating":         None,
        "document_path":      "",
        # v5.0 — visual prompt output (triggered when problem is visually-weighted)
        "visual_prompts": {
            "is_visual":       False,  # set by Director tag in Cell 16
            "midjourney":      "",     # compressed evocative prompt for Midjourney v7
            "gpt_image":       "",     # detailed structured prompt for GPT Image API
            "generated":       False,  # True once Director has produced both prompts
            "mini_discovery":  {}      # answers from Cell 51b conversation (mode="on" only)
        },
        # v5.0 Phase 3 — visualization data
        "visualization_data": {
            "anchor_embedding":   None,   # 1536-dim vector of user prompt
            "anchor_text":        "",     # the user prompt verbatim
            "turn_embeddings":    [],     # [{turn_index, role, text, vector, distance_from_anchor}]
            "pil_portrait": {
                "turns":              [],  # [{turn_index, text, spontaneous, certainty_score, new_vocab_count}]
                "vocabulary_timeline": [] # new terms introduced per PIL turn
            },
            "clarity_signals":    [],     # [{turn_index, signal_type, magnitude}]
            "idea_arcs":          [],     # [{arc_id, origin_turn, terminus_turn, origin_pos, terminus_pos, depth, role, pil_engagement}]
            "semantic_clusters":  [],     # [{cluster_id, center, member_turns, peak_density, clarity_achieved}]
            "reduced_3d":         None,   # PCA-reduced coordinates, generated at session end
            "viz_ready":          False   # True once reduce_to_3d has run
        }
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


# -- v5.0 Session Slug --------------------------------------------------------

def generate_session_slug(prompt):
    """
    Generate a short human-readable session identifier.
    Format: YYYYMMDD_first_three_content_words
    Example: 20260501_chicken_parm_stand

    Skips stopwords so the slug captures meaningful content,
    not filler words like "I", "am", "thinking", "of".
    """
    _STOPWORDS = {
        "i", "im", "me", "my", "we", "our", "you", "your",
        "a", "an", "the", "and", "or", "but", "so", "yet",
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "can", "could", "should", "may", "might", "must", "shall",
        "to", "of", "in", "on", "at", "for", "with", "about",
        "from", "up", "out", "if", "as", "by", "into", "through",
        "thinking", "looking", "trying", "want", "need", "like",
        "help", "know", "think", "feel", "get", "make", "give",
        "how", "what", "when", "where", "who", "why", "that", "this",
        "it", "its", "there", "here", "been", "some", "any",
    }
    date = datetime.now().strftime("%Y%m%d")
    words = re.sub(r"[^a-zA-Z0-9 ]", "", prompt).lower().split()
    content_words = [w for w in words if w.isalpha() and w not in _STOPWORDS]
    slug_words = content_words[:3] if content_words else ["session"]
    slug = "_".join(slug_words)
    return f"{date}_{slug}"


# -- v5.0 Domain Inventory -----------------------------------------------------

def scan_domain_inventory(user_prompt):
    """
    Scan the initial prompt against nine functional domains.
    Returns a domain_inventory dict with primary, flagged, missing, absent,
    and domain_count fields.

    Nine domains: BRANDING, OPERATIONS, REGULATORY, FINANCIAL, CX,
    POSITIONING, TECHNOLOGY, HUMAN_PROF, HUMAN_PERSONAL.
    BEHAVIORAL is a permanent overlay — not inventoried, always applied.

    Uses ANTHROPIC_DEFAULT (Haiku) — fast, cheap, runs in Cell 2b.
    Enriched later in Cell 5 from discovery content on the blackboard.
    """

    inventory_prompt = f"""You are reading a problem statement to identify which functional
domains are active, missing, or absent.

PROBLEM:
\"\"\"{user_prompt}\"\"\"

Nine functional domains:
  BRANDING      — identity, name, voice, perception, how the world sees it
  OPERATIONS    — process, logistics, execution, capacity, workflow
  REGULATORY    — compliance, legal constraints, permits, rules, standards
  FINANCIAL     — revenue, cost, pricing, viability, funding, unit economics
  CX            — customer experience, service design, human interaction
  POSITIONING   — competitive landscape, differentiation, market placement
  TECHNOLOGY    — technical feasibility, platform, infrastructure, build complexity
  HUMAN_PROF    — organizational dynamics, team capacity, professional relationships,
                  institutional politics
  HUMAN_PERSONAL — individual psychology, personal relationships, emotional stakes,
                  relational consequences of the decision

Definitions:
  primary  — the single domain the problem most clearly operates in
  flagged  — domains actively present in the problem statement
  missing  — domains NOT mentioned but likely relevant given the primary domain
             and problem type (the PIL may not know these gaps exist)
  absent   — domains genuinely not applicable to this problem

Return ONLY this JSON (use exact domain names from the list above):
{{
  "primary": "<single domain name>",
  "flagged": ["<domain>", ...],
  "missing": ["<domain>", ...],
  "absent":  ["<domain>", ...],
  "rationale": "<one sentence on what kind of problem this is>"
}}"""

    try:
        response = _anthropic_client.messages.create(
            model=ANTHROPIC_DEFAULT,
            max_tokens=400,
            messages=[{"role": "user", "content": inventory_prompt}]
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())

        flagged = data.get("flagged", [])
        return {
            "primary":      data.get("primary", ""),
            "flagged":      flagged,
            "missing":      data.get("missing", []),
            "absent":       data.get("absent", []),
            "domain_count": len(flagged),
            "rationale":    data.get("rationale", "")
        }
    except Exception as e:
        print(f"  ⚠ Domain inventory scan failed: {e}")
        return {
            "primary": "", "flagged": [], "missing": [],
            "absent": [], "domain_count": 0, "rationale": ""
        }


def enrich_domain_inventory(blackboard):
    """
    Enrich the domain inventory from discovery content already on the blackboard.
    Called in Cell 5 (brief assembly) — no additional API call.
    Reads discovery insights and adds any newly surfaced domains to flagged.
    """
    inventory = blackboard.get("domain_inventory", {})
    discovery = blackboard.get("discovery", {})

    # Collect all discovery text for a quick keyword scan
    discovery_text = " ".join([
        discovery.get("orientation_summary", ""),
        " ".join(discovery.get("context_insights", [])),
        discovery.get("desired_outcome", ""),
    ]).lower()

    # Keyword signals per domain — fast heuristic, no API call
    domain_signals = {
        "FINANCIAL":     ["cost", "revenue", "price", "budget", "money", "fund",
                          "profit", "loss", "invest", "cash"],
        "REGULATORY":    ["compliance", "legal", "permit", "regulation", "law",
                          "license", "govern", "policy", "rule"],
        "OPERATIONS":    ["process", "workflow", "logistics", "capacity", "scale",
                          "execute", "operate", "manage", "system"],
        "TECHNOLOGY":    ["tech", "platform", "software", "build", "api", "data",
                          "infra", "code", "digital", "ai"],
        "HUMAN_PROF":    ["team", "staff", "org", "politics", "stakeholder",
                          "manager", "culture", "hire", "talent"],
        "HUMAN_PERSONAL":["feel", "family", "personal", "relationship", "fear",
                          "anxiety", "identity", "values", "life"],
    }

    currently_flagged = set(inventory.get("flagged", []))
    currently_missing = set(inventory.get("missing", []))
    newly_surfaced = []

    for domain, signals in domain_signals.items():
        if domain not in currently_flagged:
            if any(sig in discovery_text for sig in signals):
                newly_surfaced.append(domain)

    if newly_surfaced:
        updated_flagged = list(currently_flagged) + newly_surfaced
        # Remove from missing if now flagged
        updated_missing = [d for d in currently_missing if d not in newly_surfaced]
        inventory["flagged"] = updated_flagged
        inventory["missing"] = updated_missing
        inventory["domain_count"] = len(updated_flagged)
        blackboard["domain_inventory"] = inventory

    return blackboard


# -- v5.0 Critic Domain Lens Context Block ------------------------------------

def build_critic_context_block(domain_inventory, pil_reading):
    """
    Assemble the domain lens context block for Critic injection.
    Injected as system context in Cells 6b and 7c.

    Includes lenses for all flagged domains + BEHAVIORAL (always active).
    PIL reading used to calibrate register and behavioral lens priority.
    """
    flagged = domain_inventory.get("flagged", [])
    missing = domain_inventory.get("missing", [])
    primary = domain_inventory.get("primary", "")
    relational = pil_reading.get("relational_proximity", "professional")

    # Build active lenses — flagged domains + behavioral always last
    active_lenses = []
    for domain in flagged:
        if domain in DOMAIN_LENSES:
            active_lenses.append(DOMAIN_LENSES[domain])
    active_lenses.append(DOMAIN_LENSES["BEHAVIORAL"])

    # Missing domain note
    missing_note = ""
    if missing:
        missing_note = (
            f"\nMissing dimensions (not yet surfaced — flag if relevant): "
            f"{', '.join(missing)}"
        )

    # Register calibration
    if relational == "personal":
        register_note = (
            "PIL context: personal/relational register. "
            "Prioritize BEHAVIORAL lens. Domain lenses are secondary — "
            "apply only where clearly relevant."
        )
    else:
        register_note = (
            f"PIL context: {relational} register. "
            "Apply all active domain lenses with full rigor."
        )

    block = f"""── DOMAIN LENS CONTEXT (v5.0) ─────────────────────────────────────
Apply these lenses IN ADDITION to the Surprise Audit — not instead of it.

Primary domain: {primary}
Active dimensions: {', '.join(flagged) if flagged else 'general'}
{missing_note}

Lenses to apply to each direction:

{chr(10).join(active_lenses)}

{register_note}
────────────────────────────────────────────────────────────────────"""

    return block


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

def create_brief_doc(session_id, user_prompt, sessions_dir=None,
                     session_slug=None):
    """
    Create the Studio Brief Document — shared working memory for the session.
    Named using session_slug (YYYYMMDD_HHMMSS_topic) for human readability,
    consistent with the JSON and Scribe output filenames.
    Falls back to brief_{session_id} if slug not provided.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    os.makedirs(sessions_dir, exist_ok=True)

    if session_slug:
        path = Path(sessions_dir) / f"{session_slug}_studio.md"
        display_id = session_slug
    else:
        path = Path(sessions_dir) / f"brief_{session_id}.md"
        display_id = session_id

    content_brief = (
        f"# STUDIO BRIEF DOCUMENT\n"
        f"## The Creative Prism — Hybrid\n"
        f"**Session:** {display_id}\n"
        f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n"
        f"## SESSION\n\n"
        f"**Initial Request:** {user_prompt}\n\n"
        f"---\n\n"
        f"*This document is the shared working memory of the studio session.\n"
        f"Every role reads this document before acting.*\n\n"
    )
    path.write_text(content_brief, encoding="utf-8")
    return path
def update_brief_doc(session_id, role, section_title, content,
                     sessions_dir=None, session_slug=None):
    """
    Append a new section to the Studio Brief Document.
    Resolves path by slug first, falls back to brief_{session_id}.
    """
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR

    # Try slug-based path first, then legacy path
    if session_slug:
        path = Path(sessions_dir) / f"{session_slug}_studio.md"
    else:
        path = Path(sessions_dir) / f"brief_{session_id}.md"

    # Fallback: search for any brief matching session_id prefix
    if not path.exists():
        candidates = list(Path(sessions_dir).glob(f"*{session_id[:8]}*studio.md"))
        if candidates:
            path = candidates[0]
        else:
            legacy = Path(sessions_dir) / f"brief_{session_id}.md"
            if legacy.exists():
                path = legacy
            else:
                raise FileNotFoundError(
                    f"Brief document not found for session {session_id}.")

    timestamp = datetime.now().strftime('%H:%M')
    addition  = (f"\n---\n\n## {section_title}\n"
                 f"*{role} — {timestamp}*\n\n{content}\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(addition)


def read_brief_doc(session_id, max_chars=12000, sessions_dir=None, session_slug=None):
    """Read the Studio Brief Document, loading only the most recent max_chars."""
    if sessions_dir is None:
        sessions_dir = SESSIONS_DIR
    # Three-tier lookup: slug first, then UUID glob, then legacy path
    path = None
    if session_slug:
        slug_path = Path(sessions_dir) / f"{session_slug}_studio.md"
        if slug_path.exists():
            path = slug_path
    if path is None:
        candidates = list(Path(sessions_dir).glob(f"*{session_id[:8]}*studio.md"))
        if candidates:
            path = candidates[0]
    if path is None:
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
              provider=None):
    """
    Make a single API call as a studio role.

    provider: "anthropic" | "openai" | None (auto-resolved from module state)

    If provider is not passed, it is resolved automatically:
      - role="critic"  → uses module-level CRITIC_PROVIDER
      - all other roles → uses module-level PRIMARY_PROVIDER

    Both PRIMARY_PROVIDER and CRITIC_PROVIDER are set by the notebook
    in Cell 2 after the routing decision. This means no call site in the
    notebook needs to pass provider= explicitly.

    For Critic calls, build_prompt() automatically loads critic_gpt.md
    when provider resolves to "openai".
    """
    # Resolve provider from module state if not passed explicitly
    if provider is None:
        if role == "critic":
            provider = CRITIC_PROVIDER
        else:
            provider = PRIMARY_PROVIDER

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
    Classify the session's primary orientation and read the PIL.
    Two separate calls — orientation scoring and PIL reading are kept apart
    so the model doesn't deprioritize structured fields in favor of narrative.
    Orientation label is computed in Python from the adjusted score —
    never trusted from model output.

    Returns a dict with orientation, scores, PIL dimensions, and model constants.

    Classification logic:
      Adjusted score ≤ 0.35  → strategic  → Claude primary, GPT critic
      Adjusted score 0.36–0.64 → balanced → tiebreaker questions decide
      Adjusted score ≥ 0.65  → creative   → GPT primary, Claude critic

    Bias rules applied in Python:
      domain_fluency = "low"                          → score - 0.15
      relational_proximity = "personal", score > 0.50 → score - 0.10
      cognitive_style = "analytical", score > 0.50    → score - 0.08
    """

    # ── Call 1: Orientation scoring ────────────────────────────────────────────
    orientation_prompt = f"""You are scoring a problem's cognitive orientation.

PROBLEM:
\"\"\"{user_prompt}\"\"\"

Score from 0.0 to 1.0:
0.0 = Purely strategic (operational viability, execution, compliance,
      feasibility, scaling, cost, risk — "how do we make this work?")
1.0 = Purely creative (identity, positioning, meaning, differentiation,
      brand, experience design, behavioral insight — "what should this
      become and why will people care?")

Most problems score 0.2–0.8. Do NOT use governed domains as a signal
toward strategic — those are handled separately regardless.
Classify based on what kind of thinking the PIL most needs.

Return ONLY this JSON:
{{
  "orientation_score": <float 0.0-1.0>,
  "rationale": "<one sentence>"
}}"""

    # ── Call 2: PIL reading ────────────────────────────────────────────────────
    pil_prompt = f"""You are reading the person who wrote this request to
understand how they think and what they need.

REQUEST:
\"\"\"{user_prompt}\"\"\"

Assess three dimensions from the language itself — vocabulary, sentence
structure, domain terminology, emotional register, what was named vs omitted.

DOMAIN FLUENCY — familiarity with the domain of their own problem:
  "high"       — accurate domain vocabulary, aware of real constraints
  "developing" — general familiarity, some vocabulary, gaps visible
  "low"        — outsider or beginner language, may not know the gaps

Note: domain fluency ≠ general intelligence. A skilled professional outside
their domain may show low fluency. Read domain signals only.

COGNITIVE STYLE — how this person naturally thinks:
  "analytical" — structured, criteria-driven, sequential, data-first
  "intuitive"  — feeling-first, metaphor-heavy, associative, example-driven
  "mixed"      — both present

RELATIONAL PROXIMITY — emotional closeness to this problem:
  "personal"     — identity-adjacent, personal stakes, family/life references
  "professional" — work problem, organizational stakes, some distance
  "mixed"        — both dimensions present

Return ONLY this JSON:
{{
  "domain_fluency": "<high|developing|low>",
  "cognitive_style": "<analytical|intuitive|mixed>",
  "relational_proximity": "<personal|professional|mixed>",
  "pil_read": "<one sentence: who this person appears to be and what they need>"
}}"""

    result = {
        "orientation":          "strategic",
        "orientation_score":    0.5,
        "primary_provider":     "anthropic",
        "critic_provider":      "openai",
        "director_model":       ANTHROPIC_DIRECTOR,
        "session_model":        ANTHROPIC_DEFAULT,
        "critic_model":         OPENAI_DEFAULT,
        "tiebreaker_used":      False,
        "tiebreaker_answers":   [],
        "rationale":            "",
        "pil_read":             "",
        "domain_fluency":       "",
        "cognitive_style":      "",
        "relational_proximity": "",
    }

    def _parse_json(raw):
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())

    # ── Step 1: Orientation score ──────────────────────────────────────────────
    try:
        raw1   = _call_anthropic(
            system_prompt="You are a concise JSON classifier. Return only valid JSON.",
            user_message=orientation_prompt,
            model=ROUTING_MODEL_ANTHROPIC,
            max_tokens=150
        )
        p1     = _parse_json(raw1)
        score  = float(p1.get("orientation_score", 0.5))
        result["rationale"] = p1.get("rationale", "")
    except Exception as e:
        print(f"  ⚠ Orientation scoring failed: {e}")
        print(f"  ⚠ Defaulting to strategic (Claude primary)")
        result["rationale"] = "Classification failed — defaulting to strategic."
        return result

    # ── Step 2: PIL reading ────────────────────────────────────────────────────
    try:
        raw2   = _call_anthropic(
            system_prompt="You are a concise JSON classifier. Return only valid JSON.",
            user_message=pil_prompt,
            model=ROUTING_MODEL_ANTHROPIC,
            max_tokens=200
        )
        p2     = _parse_json(raw2)
        domain_fluency  = p2.get("domain_fluency", "")
        cognitive_style = p2.get("cognitive_style", "")
        relational_prox = p2.get("relational_proximity", "")
        pil_read        = p2.get("pil_read", "")

        result["domain_fluency"]       = domain_fluency
        result["cognitive_style"]      = cognitive_style
        result["relational_proximity"] = relational_prox
        result["pil_read"]             = pil_read
    except Exception as e:
        print(f"  ⚠ PIL reading failed: {e} — continuing without PIL dimensions")
        domain_fluency  = ""
        cognitive_style = ""
        relational_prox = ""

    # ── Step 3: Apply bias rules in Python ────────────────────────────────────
    adjusted = score
    if domain_fluency == "low":
        adjusted -= 0.15
    if relational_prox == "personal" and score > 0.50:
        adjusted -= 0.10
    if cognitive_style == "analytical" and score > 0.50:
        adjusted -= 0.08
    adjusted = max(0.0, min(1.0, adjusted))  # clamp to [0, 1]

    # ── Step 4: Compute orientation label deterministically ───────────────────
    # Never trust the model's label — compute from the number.
    if adjusted <= 0.35:
        orientation = "strategic"
    elif adjusted >= 0.65:
        orientation = "creative"
    else:
        orientation = "balanced"

    result["orientation_score"] = round(adjusted, 2)
    result["orientation"]       = orientation

    # ── Step 5: Tiebreaker if balanced ────────────────────────────────────────
    if orientation == "balanced":
        tiebreaker_prompt = f"""Answer three questions about this problem to
decide whether it needs creative-oriented or strategic-oriented primary thinking.

PROBLEM:
\"\"\"{user_prompt}\"\"\"

Answer each with "creative" or "strategic".

Return ONLY this JSON:
{{
  "q1": "<creative|strategic>",
  "q1_reasoning": "<one phrase>",
  "q2": "<creative|strategic>",
  "q2_reasoning": "<one phrase>",
  "q3": "<creative|strategic>",
  "q3_reasoning": "<one phrase>",
  "tiebreaker_winner": "<creative|strategic>"
}}

Q1: What does the PIL most need to leave with — a direction to believe in,
    or a path they can execute?
    (direction to believe in = creative, path to execute = strategic)

Q2: What is the bigger risk — that the output is boring and generic, or
    that it is impractical and unworkable?
    (boring/generic = creative, impractical/unworkable = strategic)

Q3: Does this problem have a known answer needing reframe, or an unknown
    answer needing discovery?
    (known needing reframe = creative, unknown needing discovery = strategic)

tiebreaker_winner: whichever answer appears most in q1, q2, q3."""

        try:
            raw3    = _call_anthropic(
                system_prompt="You are a concise JSON classifier. Return only valid JSON.",
                user_message=tiebreaker_prompt,
                model=ROUTING_MODEL_ANTHROPIC,
                max_tokens=200
            )
            p3      = _parse_json(raw3)
            winner  = p3.get("tiebreaker_winner", "strategic")
            answers = [
                f"Q1: {p3.get('q1','')} — {p3.get('q1_reasoning','')}",
                f"Q2: {p3.get('q2','')} — {p3.get('q2_reasoning','')}",
                f"Q3: {p3.get('q3','')} — {p3.get('q3_reasoning','')}",
            ]
            result["tiebreaker_used"]    = True
            result["tiebreaker_answers"] = answers
            orientation = winner  # tiebreaker overrides balanced
            result["orientation"] = orientation
        except Exception as e:
            print(f"  ⚠ Tiebreaker failed: {e} — defaulting to strategic")
            orientation = "strategic"
            result["orientation"] = orientation

    # ── Step 6: Set provider and model constants ───────────────────────────────
    if orientation == "creative":
        result["primary_provider"] = "openai"
        result["critic_provider"]  = "anthropic"
        result["director_model"]   = OPENAI_DIRECTOR
        result["session_model"]    = OPENAI_DEFAULT
        result["critic_model"]     = ANTHROPIC_DEFAULT
    else:
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

# -- v5.0 Domain Expert Activation --------------------------------------------

def activate_domain_expert(initial_prompt, domain_inventory,
                            session_id, sessions_dir=None):
    """
    Pre-discovery domain expert activation call.
    Runs before Cell 4 (Discovery). Uses ANTHROPIC_DEFAULT (Haiku).

    Reads the initial prompt and domain inventory, activates the model's
    domain knowledge, and returns a structured brief covering:
      - Precise domain portrait (what kind of engagement this actually is)
      - What the PIL doesn't know they need (domain practitioner knowledge)
      - Discovery priorities (what the Director must surface before briefing)

    Output is written to blackboard["domain_context"] and appended to
    brief_doc so all subsequent roles read it.

    Epistemic flag protocol:
    When domain knowledge has currency limits (local regulations, current
    market conditions, specific pricing), the function flags these explicitly
    with WHERE_TO_VERIFY guidance so the PIL can do targeted field research.
    """

    flagged = domain_inventory.get("flagged", [])
    primary = domain_inventory.get("primary", "")
    missing = domain_inventory.get("missing", [])

    domain_summary = (
        f"Primary domain: {primary}. "
        f"Active dimensions: {', '.join(flagged) if flagged else 'general'}. "
        f"Potentially missing: {', '.join(missing) if missing else 'none identified'}."
    )

    expert_prompt = f"""You are activating as a domain consultant before a creative studio engagement begins.

INITIAL REQUEST FROM PIL:
\"\"\"{initial_prompt}\"\"\"

DOMAIN CLASSIFIER OUTPUT:
{domain_summary}

Your task is three parts. Be specific to this PIL's actual situation — not generic to the domain.

---

PART 1 — DOMAIN PORTRAIT (2-3 sentences)
Name the precise domain this engagement lives in. Not just the broad category,
but the specific type of problem: e.g. "farmers market food vendor launch in a
dense urban market with high permit competition" not just "food business."
What kind of engagement is this actually?

---

PART 2 — WHAT THE PIL LIKELY DOESN'T KNOW THEY NEED
List 5-8 dimensions of this problem that a domain practitioner would immediately
identify as essential — things a non-expert PIL would not know to raise.
Be specific. For each item, note if it is:
  [STANDARD] — well-established domain requirement, reliably known
  [EPISTEMIC FLAG: verify at SOURCE TYPE] — currency-sensitive or locally variable;
    include WHERE_TO_VERIFY so the PIL knows where to confirm current specifics.

Format each item as:
• [item name] [tag]: [one sentence description] [WHERE_TO_VERIFY if flagged]

---

PART 3 — DISCOVERY PRIORITIES
List the 3-5 most important questions the Director must answer during discovery
— questions the PIL may not know to address — before a creative brief can be
written with domain completeness.
These are gaps the Director should fill through conversation, not assumptions.

Format: numbered list, one sentence per question.

---

Keep the entire response under 500 words. Be direct and specific."""

    result = {
        "domain_portrait": "",
        "pil_knowledge_gaps": [],
        "discovery_priorities": [],
        "raw_response": "",
        "model_used": ANTHROPIC_DEFAULT
    }

    try:
        response = _anthropic_client.messages.create(
            model=ANTHROPIC_DEFAULT,
            max_tokens=700,
            messages=[{"role": "user", "content": expert_prompt}]
        )
        raw = response.content[0].text.strip()
        result["raw_response"] = raw

        # Parse sections by header markers
        sections = {
            "domain_portrait": "",
            "pil_knowledge_gaps": "",
            "discovery_priorities": ""
        }

        current = None
        lines = []
        for line in raw.split("\n"):
            if "PART 1" in line or "DOMAIN PORTRAIT" in line:
                current = "domain_portrait"
                lines = []
            elif "PART 2" in line or "PIL LIKELY" in line or "DOESN\'T KNOW" in line:
                if current:
                    sections[current] = "\n".join(lines).strip()
                current = "pil_knowledge_gaps"
                lines = []
            elif "PART 3" in line or "DISCOVERY PRIORITIES" in line:
                if current:
                    sections[current] = "\n".join(lines).strip()
                current = "discovery_priorities"
                lines = []
            elif current:
                lines.append(line)

        if current and lines:
            sections[current] = "\n".join(lines).strip()

        result["domain_portrait"] = sections["domain_portrait"]
        result["pil_knowledge_gaps"] = [
            line.strip() for line in sections["pil_knowledge_gaps"].split("\n")
            if line.strip().startswith("•")
        ]
        result["discovery_priorities"] = [
            line.strip() for line in sections["discovery_priorities"].split("\n")
            if line.strip() and line.strip()[0].isdigit()
        ]

    except Exception as e:
        result["raw_response"] = f"Domain expert activation failed: {str(e)}"

    return result


def write_domain_context_to_brief(session_id, domain_context,
                                   sessions_dir=None, session_slug=None):
    """
    Append the domain expert brief to brief_doc so all subsequent roles
    read it as part of their context.
    """
    if not domain_context.get("raw_response", "").strip():
        return

    section = (
        "\n\n---\n"
        "## DOMAIN EXPERT BRIEF (pre-discovery)\n\n"
        f"**Domain portrait:** {domain_context['domain_portrait']}\n\n"
    )

    if domain_context["pil_knowledge_gaps"]:
        section += "**What the PIL likely doesn't know they need:**\n"
        for gap in domain_context["pil_knowledge_gaps"]:
            section += f"{gap}\n"
        section += "\n"

    if domain_context["discovery_priorities"]:
        section += "**Discovery priorities for Director:**\n"
        for p in domain_context["discovery_priorities"]:
            section += f"{p}\n"

    section += "---\n"

    update_brief_doc(session_id, "DOMAIN_EXPERT", "DOMAIN_ACTIVATION", section,
                     session_slug=session_slug)


# ── v5.0 Phase 3 — Visualization Functions ────────────────────────────────────

def generate_embedding(text, openai_client=None):
    """
    Generate a 1536-dimension embedding vector for a text string.
    Uses OpenAI text-embedding-3-small — fast and cheap.
    Returns None if the call fails rather than crashing the session.
    """
    if openai_client is None:
        try:
            openai_client = _openai_client
        except Exception:
            return None
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # safety trim — model limit is 8191 tokens
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"  ⚠ Embedding failed: {e}")
        return None


def compute_anchor(blackboard, openai_client=None):
    """
    Embed the user's initial prompt as the session anchor — the origin
    of the visualization coordinate system.
    Called once at session start (Cell 3) after blackboard creation.
    All subsequent embeddings are measured relative to this anchor.
    """
    user_prompt = blackboard.get("user_prompt", "")
    if not user_prompt:
        return blackboard

    vector = generate_embedding(user_prompt, openai_client)
    if vector is not None:
        blackboard["visualization_data"]["anchor_embedding"] = vector
        blackboard["visualization_data"]["anchor_text"] = user_prompt
        print(f"  ✓ Anchor embedding generated ({len(vector)} dims)")
    else:
        print("  ⚠ Anchor embedding failed — visualization data will be incomplete")
    return blackboard


def embed_turn(text, role, turn_index, blackboard, openai_client=None):
    """
    Embed a single conversation turn and store with metadata.
    Computes cosine distance from the session anchor.
    Called after each significant turn (PIL turns, Director turns, role outputs).

    Distance from anchor = how far this turn is semantically from the
    opening problem statement. High distance = exploratory territory.
    Low distance = returning to or refining the original framing.
    """
    if not text or not text.strip():
        return blackboard

    vector = generate_embedding(text, openai_client)
    if vector is None:
        return blackboard

    # Compute cosine distance from anchor
    distance = None
    anchor = blackboard["visualization_data"].get("anchor_embedding")
    if anchor and _VIZ_DEPS:
        import numpy as np
        a = np.array(anchor)
        b = np.array(vector)
        cosine_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        distance = float(1.0 - cosine_sim)  # distance: 0=identical, 2=opposite

    entry = {
        "turn_index":           turn_index,
        "role":                 role,
        "text_preview":         text[:100],
        "vector":               vector,
        "distance_from_anchor": distance,
    }
    blackboard["visualization_data"]["turn_embeddings"].append(entry)
    return blackboard


def record_pil_turn(text, turn_index, blackboard,
                    prev_pil_vocabulary=None, spontaneous=False):
    """
    Record a PIL turn with portrait metadata.
    Extracts clarity signals: certainty language, vocabulary stability,
    new concept introduction.

    certainty_score: ratio of declarative to hedging language (higher = more certain)
    new_vocab_count: number of significant new terms introduced in this turn
    spontaneous: True if PIL volunteered information not directly asked for
    """
    import re as _re

    HEDGING = {"think", "maybe", "perhaps", "wonder", "guess", "might", "could",
               "possibly", "seems", "appears", "feel like", "not sure", "unclear"}
    DECLARATIVE = {"is", "are", "the key", "clearly", "definitely", "this means",
                   "i understand", "that's it", "exactly", "precisely", "the answer"}

    words = set(_re.sub(r"[^a-zA-Z ]", "", text.lower()).split())
    hedge_count = sum(1 for h in HEDGING if h in text.lower())
    decl_count = sum(1 for d in DECLARATIVE if d in text.lower())
    total = hedge_count + decl_count
    certainty_score = decl_count / total if total > 0 else 0.5

    # New vocabulary: significant words (>4 chars) not seen in previous PIL turns
    if prev_pil_vocabulary is None:
        prev_pil_vocabulary = set()
    significant_words = {w for w in words if len(w) > 4}
    new_vocab = significant_words - prev_pil_vocabulary
    new_vocab_count = len(new_vocab)

    turn_data = {
        "turn_index":    turn_index,
        "text":          text,
        "spontaneous":   spontaneous,
        "certainty_score": round(certainty_score, 3),
        "new_vocab_count": new_vocab_count,
        "new_vocab":     list(new_vocab)[:10]  # store top 10 for inspection
    }

    blackboard["visualization_data"]["pil_portrait"]["turns"].append(turn_data)
    blackboard["visualization_data"]["pil_portrait"]["vocabulary_timeline"].append(
        list(new_vocab)[:10]
    )

    # Clarity signal: low new vocab + high certainty = potential clarity moment
    if new_vocab_count <= 2 and certainty_score > 0.6:
        blackboard["visualization_data"]["clarity_signals"].append({
            "turn_index":  turn_index,
            "signal_type": "vocabulary_lock",
            "magnitude":   round(certainty_score, 3)
        })

    return blackboard, significant_words | prev_pil_vocabulary


def reduce_to_3d(blackboard):
    """
    Reduce all stored embeddings to 3D using PCA.
    Called once at session end (Cell 12).
    The anchor embedding becomes the coordinate origin —
    all other points are expressed relative to it.

    Stores reduced coordinates back into each turn_embedding entry
    and into visualization_data["reduced_3d"] as a summary structure.
    """
    if not _VIZ_DEPS:
        print("  ⚠ numpy/sklearn not available — skipping 3D reduction")
        return blackboard

    import numpy as np

    turn_embeddings = blackboard["visualization_data"]["turn_embeddings"]
    anchor = blackboard["visualization_data"]["anchor_embedding"]

    if not turn_embeddings or anchor is None:
        print("  ⚠ No embeddings to reduce")
        return blackboard

    # Build matrix: anchor first, then all turns
    all_vectors = [anchor] + [e["vector"] for e in turn_embeddings
                               if e.get("vector") is not None]

    if len(all_vectors) < 3:
        print("  ⚠ Too few embeddings for PCA reduction")
        return blackboard

    matrix = np.array(all_vectors)

    # PCA to 3D
    n_components = min(3, matrix.shape[0] - 1, matrix.shape[1])
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(matrix)

    # Translate so anchor is at origin
    origin = reduced[0]
    reduced_centered = reduced - origin

    # Store coordinates back into turn entries
    vec_idx = 1
    for entry in turn_embeddings:
        if entry.get("vector") is not None:
            entry["position_3d"] = reduced_centered[vec_idx].tolist()
            vec_idx += 1

    # Store summary
    blackboard["visualization_data"]["reduced_3d"] = {
        "anchor_position":     [0.0, 0.0, 0.0],
        "explained_variance":  pca.explained_variance_ratio_.tolist(),
        "n_turns_reduced":     len(turn_embeddings),
        "coordinate_system":   "PCA-centered on anchor (user prompt)"
    }
    blackboard["visualization_data"]["viz_ready"] = True

    var_explained = sum(pca.explained_variance_ratio_) * 100
    print(f"  ✓ 3D reduction complete: {len(turn_embeddings)} turns, "
          f"{var_explained:.1f}% variance explained")
    return blackboard



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
