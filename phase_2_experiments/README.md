# phase_2_experiments
### The Creative Prism — Active Lab

---

## What This Directory Is

The active working environment for The Creative Prism studio system.
All development from v1.0 through the current v4.0 hybrid architecture
happened here. The root `LOGBOOK.md` is the authoritative experiment
record — this README is orientation for anyone landing in this directory.

---

## Active Files

| File | Description |
|---|---|
| `engine_hybrid.py` | Active engine — Anthropic + OpenAI unified. `call_role()` dispatches by provider. Reads `persona_traits_matrix_v2.csv` from same directory. |
| `persona_traits_matrix_v2.csv` | 58-trait personality matrix. Five-band language directives. Director adjusts per session within min/max ranges. |
| `creative_prism_studio_v4_0.ipynb` | Active nine-stage notebook. Hybrid routing in Cell 2b. Cross-model Critic in Cells 6 and 7c. |
| `prism_evaluator_v2.py` | Dual evaluator — Gemini 1.5 Pro + GPT-4o score independently. Three-layer architecture: structural (20%), semantic transformation (40%), human signal (40%). |
| `LOGBOOK.md` | Full experiment record. Start here. |

---

## Directory Map

```
phase_2_experiments/
  engine_hybrid.py
  persona_traits_matrix_v2.csv
  creative_prism_studio_v4_0.ipynb
  prism_evaluator_v2.py
  LOGBOOK.md

  prompts_hybrid/            ← active prompt set (gitignored)
    director.md              ← v1.9 + v4.0 additions + WOW Standard (v5.0)
    creator.md               ← v1.2 — Verbalized Sampling, Step 0
    critic.md                ← v1.3 — Surprise Audit, all three bands
    critic_gpt.md            ← v1.0 — GPT Critic, creative challenge orientation
    researcher.md            ← v1.3 + three-tier epistemic system
    scribe.md
    director_extraction_games.md  ← 19 extraction games + Studio Specialist Personas (v5.0)

  scenario_prompts/          ← v5.0 test prompt set (19 scenarios)
  sessions_hybrid/           ← session JSONs (gitignored)
  sessions_openai/           ← OpenAI session JSONs (gitignored)
  governance/                ← system constitution, operating protocol (gitignored)

  archived_py/               ← prior engine versions and notebook iterations
    engine.py                ← v2.1 Claude-only (superseded)
    engine_openai.py         ← v1.0 OpenAI-only (superseded)
    creative_prism_studio_v2_1.ipynb
    creative_prism_studio_v3_1.ipynb
    creative_prism_studio_openai_v3_1.ipynb
    persona_traits_matrix_gem.csv
    persona_traits_matrix_v2.csv  ← pre-v5.0 traits (superseded)

  phase_2_archive/           ← first Creative Prism experiments (v1.0–v1.2)
  phase_3_visualization/     ← Three.js and p5.js visualization work (gitignored)
```

---

## How the Engine Works

`engine_hybrid.py` is the only file that needs to run. The notebook imports
from it. Both files must be in the same directory — the engine resolves
`persona_traits_matrix_v2.csv` relative to its own location.

**Provider routing** is decided in Cell 2b of the notebook. A Sonnet-based
classifier reads the initial prompt and produces an orientation score
(0.0 = strategic, 1.0 = creative). Thresholds:

```
≤ 0.35  →  Strategic: Claude primary, GPT Critic
≥ 0.65  →  Creative:  GPT primary, Claude Critic
0.36–0.64  →  Balanced: tiebreaker questions decide
```

**Model tiers:**
- `DIRECTOR_MODEL` (Sonnet) — all PIL-facing Director calls
- `DIRECTOR_FAST_MODEL` (Haiku or GPT-mini) — internal/admin calls
- `SESSION_MODEL` — Creator, Researcher, Scribe
- `CRITIC_MODEL` — always the opposite provider's session-tier model

---

## Traits System

`persona_traits_matrix_v2.csv` defines 58 traits across four roles
(Creator, Critic, Researcher, Scribe). Each trait has a base value,
min/max range, and a five-band language directive:

```
≥ 0.90  HIGHEST — defining quality of your work in this session
≥ 0.70  HIGH    — strongly present throughout
≥ 0.45  MEDIUM  — apply where it genuinely serves the output
≥ 0.20  LOW     — use sparingly
< 0.20  LOWEST  — minor undercurrent, should not noticeably influence
```

The Director configures the team at Stage 3 — adjusting trait values
within the allowed min/max range for the specific problem. These
adjustments are invisible to the person in the loop.

---

## Experimental Run Status

Active run: **v5.0 scenario set — 19 prompts**

Prior runs (archived in sessions_hybrid/):
- 11 complete sessions across conventional, stress test, and frontier lab prompt types
- Evaluator results: `evaluator_results.md`
- Comparative analysis: see LOGBOOK entries for April 16–27, 2026

---

## What's Next — v5.0

Three-layer build. Layer 1 deployed. Layers 2 and 3 pending test data from
current run.

**Layer 1 (complete):** Commitment protocol in Final Synthesis. WOW Standard
in Director quality review. Traits matrix updates (iconoclasm, beginner_mind,
constructive_feedback, discernment).

**Layer 2 (ready to build):** Deterministic second loop trigger. Pre-brief
interrogation round (Creator + Critic challenge Director framing before brief
is written). Semantic drift gate (cosine similarity between initial prompt and
brief challenge field).

**Layer 3 (after test data):** Full prompt compression. VS applied to discovery
question generation. Studio Specialist Persona System (8 theatrical personas
deployed by Director as MC).

Full spec: `creative_prism_v5_development_brief.md`

---

*See `LOGBOOK.md` for the full experiment record and architecture decisions.*
