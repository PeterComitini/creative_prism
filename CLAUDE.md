# CLAUDE.md
# The Creative Prism — Project Context
# Read at the start of every Claude Code session.

---

## WHO I AM

Peter Comitini. Graphic designer by training, multiple careers in visual
communication, brand, and technology. Graduate Certificate in Generative AI
for Business, UT Austin McCombs (Distinction). This project is both a
learning environment and a key portfolio piece for a career pivot into AI
and computer science.

I think like a designer — systemically, visually, iteratively. I rely on
Claude for coding implementation, technical guidance, and disciplined
engineering support. I am not a software engineer.

---

## THE PROJECT

**Name:** The Creative Prism
**Domains:** clarityprism.ai / creativeprism.ai (registered via Cloudflare)
**Repository:** `/Volumes/code_space/02_projects/creative_prism/`
**IDE:** VS Code
**Phase:** 2 — Active experimental run, v4.0 Hybrid deployed, v5.0 in design

The Creative Prism is a multi-agent AI creative studio. A structured
nine-stage workflow guides a Person in the Loop (PIL) through creative
exploration using five AI roles. The system surfaces what people actually
need rather than what they said, runs it through genuine role-separated
creative pressure, and lands somewhere the person couldn't have reached
alone.

**Philosophical foundation:** Proprioception of thought — making the
movement of human thought visible. The PIL is the subject. The system is
the catalyst, not the oracle.

---

## ACTIVE ARCHITECTURE — v4.0 Hybrid

**Engine:** `engine_hybrid.py` — holds both Anthropic and OpenAI clients.
`call_role()` dispatches by `provider` parameter.

**Active notebook:** `creative_prism_studio_v4_0.ipynb`

**Model routing:**
- Orientation classifier in Cell 2b scores 0.0 (strategic) → 1.0 (creative)
- ≤0.35 → Strategic: Claude primary, GPT Critic
- ≥0.65 → Creative: GPT primary, Claude Critic
- 0.36–0.64 → Balanced zone, tiebreaker decides
- DIRECTOR_MODEL = Sonnet (PIL-facing calls)
- DIRECTOR_FAST_MODEL = Haiku/GPT-mini (internal/admin calls)
- SESSION_MODEL = primary provider session-tier model
- CRITIC_MODEL = opposite provider model — always cross-model

**Cell map (v4.0):**
Cell 1=Load | Cell 2=Config | Cell 2b=Routing | Cell 3=Stage 0
Cell 4=Stage 1 | Cell 5=Stages 2&3 | Cell 5a=Stage 3a | Cell 5b=Stage 3b
Cell 6a=Stage 4a Creator | Cell 6b=Stage 4b Critic | Cell 7=Stage 4c Researcher
Cell 7b=Stage 4d Creator P2 | Cell 7c=Stage 4e Critic P2
Cell 8=Stages 5&6 | Cell 8a=Stage 6a (iteration loop)
Cell 9=Stage 7 | Cell 10=Stage 8 | Cell 10b=Stage 8b | Cell 10c=Stage 8c
Cell 11=Stage 9 | Cell 11b=Stage 9b | Cell 12=Record

**Key rule:** Any call using `provider=CRITIC_PROVIDER` must also use
`model=CRITIC_MODEL`. They are a matched pair. SESSION_MODEL is always
the primary provider's model only.

---

## FILE STRUCTURE

```
creative_prism/
├── engine_hybrid.py          ← active engine
├── engine.py                 ← Claude-only engine (reference)
├── engine_openai.py          ← OpenAI-only engine (reference)
├── prism_evaluator.py        ← evaluator v1.0
├── prism_evaluator_v2.py     ← evaluator v2.0 (three-layer)
├── LOGBOOK.md                ← experiment history — read this
├── CLAUDE.md                 ← this file
├── notebooks/
│   └── creative_prism_studio_v4_0.ipynb   ← active notebook
├── prompts_hybrid/           ← active prompt files (gitignored)
│   ├── director.md
│   ├── creator.md
│   ├── critic.md
│   ├── critic_gpt.md
│   ├── researcher.md
│   └── director_extraction_games.md
├── governance/               ← system constitution, laws (gitignored)
├── sessions_hybrid/          ← session JSONs (gitignored)
├── outputs/                  ← evaluator outputs
└── persona_traits_matrix_v2.csv
```

**What is NOT in the repo (private IP, gitignored):**
- `prompts_hybrid/` — role identity files
- `governance/` — system constitution and operating protocol
- `sessions_hybrid/` — session data
- `phase_3_visualization/` — large files

---

## FIVE ROLES — NAMES ARE FIXED

| Role | Function |
|---|---|
| Director | Orchestrates, PIL-facing, discovery, brief, presentation, synthesis |
| Creator | Verbalized Sampling, four directions with probability scores |
| Critic | Cross-model evaluation, Surprise Audit, synthesis direction S1 |
| Researcher | Three-tier epistemic system: CITED FINDING / PATTERN / EPISTEMIC FLAG |
| Scribe | Session logging, semantic trace (v5.0), session record |

**Person in the Loop (PIL)** = sixth role. Human participant. Final authority
at every stage.

---

## CURRENT PROMPT VERSIONS

| File | Version | Key feature |
|---|---|---|
| director.md | v1.9 + v4.0 additions | Commitment protocol, VS discovery gate (v5.0), plain prose prohibition |
| creator.md | v1.2 | Step 0 verbalized sampling, band ranges |
| critic.md | v1.3 | Surprise Audit all bands, no sequencing role |
| critic_gpt.md | v1.0 | GPT Critic: distinctiveness, surprise, behavioral resonance |
| researcher.md | v1.3 + three-tier | CITED FINDING / PATTERN / EPISTEMIC FLAG |
| director_extraction_games.md | v1.3 | 19 extraction games, Specialist personas (v5.0) |

---

## KEY ARCHITECTURAL DECISIONS — DO NOT RE-LITIGATE

- `engine_hybrid.py` is the machinery. Notebooks are experiments only.
- Critic always runs on opposite provider from primary — cross-model is intentional.
- DIRECTOR_MODEL (Sonnet) for PIL-facing only. DIRECTOR_FAST_MODEL for internal.
- Studio Brief Document is shared working memory — not full conversation threading.
- Role sequence: Creator → Critic → Researcher (Researcher acts post-ideation).
- Researcher three-tier epistemic system — fabrication prohibition is primary.
- Commitment protocol in FINAL SYNTHESIS — Director commits to a position, not a menu.
- Sessions gitignored. Notable sessions curated manually.
- PIL is the subject. The system is the catalyst.

---

## V5.0 BUILD PLAN — NEXT MILESTONE

**Layer 1:** Complete ✅ — commitment protocol deployed

**Layer 2 — build next:**
- Deterministic second loop trigger (hard conditions, not interpretive)
- Pre-brief interrogation round (new cell between Cell 4 and Cell 5)
- Semantic drift gate in engine_hybrid.py (cosine similarity, threshold 0.85)
- Session slug in Cell 12 (YYYYMMDD_first_three_words)
- PIL rating capture in Cell 12 (1–5 scale)

**Layer 3 — after first v5.0 sessions:**
- Full prompt rewrite (director 180 lines, creator 120, critic/researcher 100)
- VS Step 0 gate on discovery questions
- Studio Specialist persona system (8 personas, mandatory 1 per session)
- Scribe semantic trace (idea_XXX suite, UMAP 384D→3D)

**idea_XXX suite (Scribe capture for Phase 3 visualization):**
- `idea_directions` — all Creator/Critic directions, parsed with embeddings
- `idea_selections` — Director curation decisions including rejections
- `idea_research` — Researcher findings tagged by direction relevance
- `idea_pil_moves` — PIL injection points as discrete events with force vectors
- `idea_synthesis_path` — full trajectory waypoints prompt→synthesis
- `idea_space` — flat point cloud index for Phase 3 renderer

**Dependencies needed for v5.0:**
```bash
pip3 install umap-learn --break-system-packages
# sentence-transformers already installed
```

---

## EVALUATOR STATUS

**v1.0** (`prism_evaluator.py`) — structural only, 5-dimension dual LLM scoring.
Gemini 2.5 Flash + GPT-4o. Known bias toward baseline responses.

**v2.0** (`prism_evaluator_v2.py`) — three-layer:
- Layer 1: structural (20%) — retained from v1.0
- Layer 2: semantic transformation (40%) — reframing distance, synthesis novelty, direction spread
- Layer 3: human signal (40%) — PIL rating 1–5

Run against 11 sessions. Inversion resolved. PIL 4 sessions cluster 69–73,
PIL 1–2 sessions cluster 44–50.

Sessions directory: `sessions_hybrid/`
Outputs directory: `outputs/`

**Note:** `google.generativeai` deprecated — FutureWarning on import.
Migrate to `google.genai` SDK before next large batch run.

---

## PHASE 3 VISUALIZATION — STATUS

Target: 3D semantic trajectory visualization of session geometry.
Render in Three.js. Free spherical orbit navigation. Click-to-expand nodes.

Design principles:
- Data leads design. Geometry emerges from session data, not painted explicitly.
- Different visual languages for different data types:
  lines = sequences, nodes = crystallized events, volumes = fields/influences
- The PIL's magnetic influence (attraction/repulsion) is the primary visual object
- Maximum divergence moment (widest opening of Creative Team directions)
  is more important than the synthesis endpoint
- Objective: beauty and rapture, not measurement and data

Current canonical state: design phase. idea_XXX suite schema specified.
UMAP for dimensionality reduction (384D→3D, random_state=42 for determinism).
Build begins after first v5.0 sessions generate real trajectory data.

---

## WHAT REQUIRES EXPLICIT CONFIRMATION BEFORE ACTING

- Any file rename or folder restructure
- Any schema field addition, removal, or rename in session JSON
- Any change to role names or role identity files
- Any new dependency or library
- Any refactor of working code
- Any change to CLAUDE.md itself
- Any notebook cell that affects session save or evaluation payload

---

## SESSION STARTUP CHECKLIST

- [ ] Read this file
- [ ] Read LOGBOOK.md
- [ ] Confirm session goal before writing any code
- [ ] Do not assume continuity from a previous chat — confirm it
- [ ] Check which notebook version is active before touching cells

---

## DOCUMENTS TO READ IF AVAILABLE

1. `LOGBOOK.md` — complete experiment history and current status
2. `continuity_prompt_april_24_2026_final.md` — last major continuity doc
3. `creative_prism_v5_development_brief.md` — v5.0 design spec
4. `idea_xxx_schema_spec.md` — Phase 3 data schema
5. `studio_run_schema_v2_2.json` — session JSON schema

---

## PROJECT PHILOSOPHY

*"The Creative Prism does not replace the thinker.*
*It expands the range of thinking available to them."*
— System Constitution V2.2

The objective is beauty and rapture, not measurement and data.
The beauty comes from the data.
The sense of beauty comes from inside the person.

---

*Last updated: April 27, 2026*
*Maintained by: Peter Comitini*
*Update this file when working rules, build status, or project direction changes.*
