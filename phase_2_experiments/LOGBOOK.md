# LOGBOOK
## The Creative Prism — Experiment Record

*Active experiment log for the Creative Prism project.*
*Predecessor work: `phase_1_experiments/LOGBOOK.md`*
*First Creative Prism experiment: `phase_2_experiments/phase_2_archive/NOTES.md`*

---

## SYSTEM OVERVIEW

**Engine:** `engine.py` v2.1
**Schema:** Blackboard v2.2
**Notebooks:** `creative_prism_studio_v2_1.ipynb` (current) · earlier versions in `phase_2_experiments/phase_2_archive/`
**Role sequence:** Director → Creator → Critic → Researcher → Creator Pass 2 → Critic Pass 2 → Director
**Traits system:** 52-trait matrix (`phase_2_experiments/persona_traits_matrix_v2.csv`) with five-band language directives
**Models:** DIRECTOR_MODEL (Sonnet) for PIL-facing calls · SESSION_MODEL (Haiku) for Creative Team
**Evaluator:** `prism_evaluator.py` v2.0 — dual evaluator (Gemini 1.5 Pro + GPT-4o), Tier 1 JSON metrics + Tier 2 LLM scoring

---

## ARCHITECTURE DECISIONS LOG

| Decision | Rationale |
|---|---|
| `engine.py` as machinery, notebooks as experiments | Production-ready pattern, clean separation |
| Studio Brief Document as shared memory | Real studio practice, ~800-1200 tokens, no summarization loss |
| Role sequence: Creator → Critic → Researcher | Researcher acts on ideation output, not bare brief |
| Two-pass Creative Team loop | Creator → Critic → Researcher → Creator Pass 2 → Critic Pass 2 → Director |
| Scribe runs end-of-session, on by default | Most distinctive UX feature — PIL sees visualization automatically |
| Researcher: one autonomous contribution per session | Bounded proactivity — Director as permission gate |
| JSON brief format with validation gate | Eliminates fragile line-by-line parsing failure mode |
| Sessions gitignored, curated manually | Experimental data; notable sessions committed intentionally |
| `prompts/` and `governance/` gitignored | Core IP — not yet public |
| Visualization target: Eye motif (SVG + Anime.js) | Replay instrument — post-session retrospective |
| Live-building visualization deferred | Second generation target |
| Adaptive discovery loop (v1.5+) | Director controls turn count (1-6), deploys extraction toolkit |
| Routing gate (v1.5+) | Director classifies STUDIO / DIRECT / OUT_OF_SCOPE before discovery |
| DIRECTOR_MODEL separate from SESSION_MODEL (v1.5+) | Sonnet for PIL-facing, Haiku for Creative Team |
| Director team configuration (v1.5+) | Director tunes Creative Team traits per problem |
| 52-trait matrix replaces 9-trait system (v2.0) | Values-based personality system with min/max ranges and five-band language |
| Brief document max_chars (v2.0) | read_brief_doc() loads only most recent 12000 chars to prevent token accumulation |
| All PIL interactions live input (v1.5.2+) | No simulated personas or hardcoded test responses in discovery/routing |
| generate_baseline() (v2.1) | Zero-shot Control B call before any agents run — raw prompt → Haiku, no system prompt |
| assemble_evaluation_payload() (v2.1) | Packages prompt/baseline/synthesis at session end for evaluator |
| Stage 8c Second Loop (v2.1) | Re-runs full Creative Team when second_exploration.triggered is True |
| Governed domain constraint recognition (v2.1) | Director names regulatory/legal hard boundaries in Brief regardless of PIL awareness |
| Researcher governed domain priority (v2.1) | Compliance research is Category 1 in regulated domains — included automatically |

---

## INTELLECTUAL FOUNDATION

| Source | Relevance |
|---|---|
| Bohm — *Thought as a System* | Proprioception of thought — philosophical foundation |
| Dowd — *Taking Root to Fly* | Somatic proprioception — origin of the core insight |
| IDEO / d.school HCD | Discovery methodology, sacrificial concepts, empathic orientation |
| Shneiderman — HCAI Framework | Amplify / augment / empower / enhance as success standard |
| Verbalized Sampling (arXiv 2510.01171) | Validates ideation diversity approach |
| VECTOR (arXiv 2509.14455) | Validates semantic trajectory visualization approach |
| Cognitive-Affective Maps (Thagard/Reuter) | Visualization theory with affective valence |
| Socratic Dialogue (MSP Tool 49) | Structural predecessor |
| Albers / Abstract Expressionists / Duchamp / LeWitt | Modernist lineage: medium as subject, instruction as art |

---

## EXPERIMENT RECORD

---

### [2026-03-17] Experiment 1 — Phase 1 v1.0 First Run

**Status:** PARTIAL — archived in `phase_2_experiments/phase_2_archive/`
**Engine:** v1.0 · **Schema:** v2.1 · **Notebook:** Phase 1 v1.0

**What was tested:** First full end-to-end nine-stage workflow. TEST_MODE with bookstore cafe brief. All five roles called.

**What worked:**
- All 18 reasoning trace steps executed without crashing
- API calls succeeded for all five roles
- Session JSON saved correctly
- Epistemic integrity held — every role refused to work with empty brief rather than hallucinating content

**What failed:**
- Silent brief parsing failure — `line.startswith("CHALLENGE:")` didn't match Director's markdown format
- Content truncation — `research_response[:200]` stored permanently to Blackboard
- Director tone failure — exposed internal system failure to PIL
- Role sequence error — Researcher received brief before Creator
- No shared session memory — Director unaware of its own prior outputs

**Full diagnosis:** `phase_2_experiments/phase_2_archive/NOTES.md`

---

### [2026-03-18] Architecture Redesign — v1.1 / v1.2

**Status:** Complete

**Engine v1.2:**
- Studio Brief Document: `create_brief_doc()`, `update_brief_doc()`, `read_brief_doc()`
- Session loader: `load_session()`, `list_sessions()`, `print_sessions()`
- Schema v2.2: `director_summary`, `idea_space`, `target` in reasoning trace
- No truncation anywhere — full content stored

**Phase 1 v1.2 notebook:**
- Role sequence corrected: Creator → Critic → Researcher
- JSON brief format with validation gate
- Studio Brief Document passed to every role call
- Researcher task updated — responds to ideation output, not bare brief

**Engine fixes applied during Experiment 2 setup (2026-03-19):**
- `SESSIONS_DIR` was missing from module level — added after `PROMPTS_DIR`
- `call_role()` was missing `brief_doc` parameter — added with `= ""` default
- `build_prompt()` was missing `brief_doc` parameter and injection block — both added

---

### [2026-03-19] Experiment 2 — Phase 1 v1.2 First Run

**Status:** COMPLETE — first clean full-pipeline execution
**Engine:** v1.2 · **Schema:** v2.2 · **Notebook:** `creative_mirror_phase2_v1.2.ipynb` (archived in `phase_2_experiments/phase_2_archive/notebooks_v2/`)
**Session:** `session_20260319_123403_efd6ce66.json`
**Model:** claude-haiku-4-5-20251001 · **Mode:** TEST_MODE = True

**Brief:** Bookstore cafe brand identity — community rootedness, intellectual warmth, anti-cliche

**What was tested:** Full nine-stage workflow with Studio Brief Document threading, JSON brief parsing, corrected role sequence (Creator → Critic → Researcher), and Director-led review and synthesis.

**What worked:**
- Studio Brief Document gave Director genuine session continuity
- JSON brief parsed cleanly
- Creator produced four genuinely distinct directions using Verbalized Sampling, including A4 (probability 0.11 — "The Heretical Reading Practice")
- Critic evaluation of A1 was rigorous and complete
- Director correctly identified incomplete Critic evaluation and flagged the gap
- Researcher produced intellectually strong findings
- Final synthesis — "The Library of Small Arguments" — was genuinely strong
- 18 reasoning trace steps completed and saved correctly

**What failed / gaps identified:**

1. **Critic truncation at max_tokens=1200** — output cut off mid-evaluation. Fix: raise to 1800-2000.
2. **Director review parsing failure** — narrative format instead of JSON. Fix: convert to JSON with validation gate.
3. **Researcher role misaligned** — operated as second Critic. Fix: rewrite prompt to center sourcing behavior.
4. **Missing depth-extraction stage** — no Stage 8b. Fix: add Director-PIL depth dialogue.
5. **Iteration loop not wired** — ITERATE flag not connected. Fix: conditional re-run in Cell 8.

**Observations:**
- The Studio Brief Document is the most important architectural decision in the system
- A4 (probability 0.11) drove the final synthesis — validates Verbalized Sampling directly
- Token budget is a real constraint at Haiku scale

**Conceptual note — PIL session (Peter's reflection):**
The roles in the Creative Prism are externalized aspects of the designer's own creative persona, given structure and made executable. The intellectual lineage runs from Albers through abstract expressionism, Duchamp, LeWitt, to creative coding (Casey Reas). The Creative Prism continues this lineage into computation: the isolation of intelligent process itself as medium. The system is the artwork.

---

### [2026-03-19] Article Development — Medium Draft Sections Written

**Status:** COMPLETE — four new sections drafted and approved

**Sections produced:**

1. **The First Clean Run** — Narrative account of Experiment 2
2. **The Studio Model** — Origin story from Socratic Loop through G-S-A-C to five-role system
3. **The Memory Problem** — Studio Brief Document traced to Newsweek editorial wall practice
4. **The Lineage of the Idea** — Modernist lineage: Albers → LeWitt → Creative Prism
5. **Conclusion: The Eighth Square** — Phase 3 visualization as aspiration

---

### [2026-04-01] Experiment 3 — Phase 1 v1.5 First Live PIL Session

**Status:** PARTIAL — significant architectural progress, multiple bugs identified
**Engine:** v1.2 · **Schema:** v2.2 · **Notebook:** `creative_prism_phase1_v1_5.ipynb`
**Session:** `session_20260401_111300_c59648d2.json`
**Director model:** claude-sonnet-4-20250514 · **Team model:** claude-haiku-4-5-20251001
**PIL:** Peter (live input — first session without TEST_MODE for discovery)

**Brief:** Chicken Parmesan sandwich business — "Petrina's" — semi-retired person, limited capital, farmer's market entry, family legacy

**What was new in v1.5:**
- Stage 0 Routing — Director classifies request before engaging studio
- Stage 1 Adaptive Discovery — Director-controlled loop, 1-6 turns, extraction toolkit
- Stage 2 Reframing — Director proposes reframing, PIL confirms
- Stage 3a Team Configuration — Director tunes trait weights for Creative Team
- DIRECTOR_MODEL separate from SESSION_MODEL
- All PIL interactions live input (routing, discovery, reframing)

**What worked:**
- Routing correctly classified chicken parm business as STUDIO
- Adaptive discovery ran 6 turns with genuine signal extraction
- Director used forced choice technique (A/B/C business model options) — effective
- Director extracted meaningful signals: financial risk concerns, family involvement, farmer's market preference, "wow factor" quality standard
- Reframing was strong — PIL confirmed with "yeah, that's about right"
- Creative brief was specific and grounded in discovery signals
- Team configuration produced meaningful personality adjustments
- Creator Pass 1 produced three genuinely distinct directions
- Researcher findings were substantive and cited (NAFMM, FDA Food Code, NRA economics data)

**What failed:**

1. **Discovery READY-with-question bug** — Director asked a final question and simultaneously set status to READY. Loop exited without collecting the answer. Fix: explicit instruction + safety net (if READY message ends with ?, collect response).
2. **Team config missing trait** — Critic weights returned without `playfulness`. Fix: list all traits explicitly in template.
3. **Creator A3 truncated** — cut off mid-sentence at max_tokens=1200. Fix: raise to 1800 + no-preamble instruction.
4. **Critic evaluated bookstore project instead of chicken parm** — session-killing bug. Hardcoded TEST_MODE response blocks in Cells 14, 32, and 34 contained stale bookstore content. Contamination propagated through Studio Brief Document into all downstream roles.
5. **Seven Director calls on wrong model** — downstream cells used SESSION_MODEL instead of DIRECTOR_MODEL. Fix: audit all Director calls.
6. **Director interaction quality was flat** — defaulted to generic open questions instead of deploying extraction techniques.

**Session terminated** after Critic contamination was discovered.

---

### [2026-04-01] Experiment 4 — Phase 1 v1.5.1/v1.5.2 Second Live PIL Session

**Status:** PARTIAL — ran further, new bugs surfaced
**Engine:** v1.2 · **Schema:** v2.2 · **Notebook:** `creative_prism_phase1_v1_5_2.ipynb` (archived in `phase_2_experiments/phase_2_archive/notebooks_v2/`)
**Session:** `session_20260401_214700_a28e4bd0.json`
**Director model:** claude-sonnet-4-20250514 · **Team model:** claude-haiku-4-5-20251001
**PIL:** Peter (live input)

**Brief:** Same chicken parm scenario, fresh session after Mac restart

**Fixes applied in v1.5.1/v1.5.2:**
- All TEST_MODE blocks with bookstore content removed entirely
- All Director calls corrected to DIRECTOR_MODEL
- Creator max_tokens raised to 1800 with no-preamble instruction
- Discovery READY instruction + question safety net added
- Team config trait template made explicit
- Discovery prompt tightened to push extraction techniques after turn 2
- "Creative Mirror" replaced with "Creative Prism" throughout notebook

**What worked:**
- Discovery ran cleanly — Director was more engaged, used forced choice
- Reframing confirmed by PIL
- Brief was strong and specific
- Team configuration applied meaningful adjustments
- Creator Pass 1 produced three strong, distinct directions
- Critic Pass 1 was rigorous and on-topic
- Researcher findings were substantive with named citations
- Creator Pass 2 refinement incorporated research and critique effectively
- Session ran through Stage 5/6 Director Review

**What failed / gaps identified:**

1. **Researcher max_tokens=800 too low** — output truncated mid-sentence. Fix: raise to 2000.
2. **Session metadata records wrong director model** — `create_blackboard()` hardcodes DEFAULT_MODEL. Fix: accept director_model parameter.
3. **Director Review reads Pass 1 instead of Pass 2** — `creator_proposals[0]` instead of `[-1]`. Fix: change index.
4. **Brief document records Director Review twice** — duplicate entries contribute to token bloat. Fix: audit `update_brief_doc` calls.
5. **Brief document token accumulation** — full brief loaded into every call grows unboundedly. Fix: `read_brief_doc()` with max_chars parameter.
6. **Critic Pass 2 uses recommendation language** — "The Critic recommends S1..." violates role boundary. Fix: neutral presentation language.
7. **Stage 9 generic naming** — output titled "Final Synthesis" regardless of problem type. Fix: dynamic document naming, intro sentence, outro feedback request.

---

### [2026-04-03] Engine v2.0 Build — Traits Matrix, Bug Fixes, Name Cleanup

**Status:** COMPLETE — built by Claude Opus 4.6, spec by Claude Sonnet 4.6
**Engine:** v2.0 · **Notebook:** `creative_prism_studio_v2_0.ipynb`
**Build spec:** `_resources/continuity_prompts/opus_prompt_v2_build.md`

**What was built:**

Engine v2.0:
- 52-trait persona matrix system replacing old 9-trait ROLE_WEIGHTS
- `load_traits_matrix()` reads `persona_traits_matrix_v2.csv` (no pandas dependency)
- `weight_to_band()` converts numeric weights to five-band language directives
- `build_trait_profile()` assembles natural language trait blocks for prompt injection
- `get_tunable_traits()` identifies traits the Director can adjust per role
- `validate_adjustments()` clamps Director's adjustments to allowed min/max ranges
- `create_blackboard()` accepts director_model parameter (Bug 2 fix)
- `read_brief_doc()` accepts max_chars parameter, default 12000 (Bug 5 fix)
- `build_prompt()` rewritten — injects trait profile block instead of old TRAIT_INSTRUCTIONS
- `call_role()` simplified — trait_profile string parameter replaces weights/mode
- Old system fully retired: ROLE_WEIGHTS, GLOBAL_MODES, TRAIT_INSTRUCTIONS, apply_global_mode removed
- All names updated: "Creative Prism" throughout
- Studio Brief Document header updated

Notebook v2.0:
- Kernel restart warning at Cell 0
- Imports updated for new engine API
- All Creative Team calls inject trait_profiles
- All Director calls use DIRECTOR_MODEL (12 calls verified)
- Researcher max_tokens raised to 2000 (Bug 1)
- Director Review reads [-1] not [0] (Bug 3)
- Critic Pass 2 uses neutral presentation language (Bug 6)
- Stage 9 dynamic document naming, intro sentence, outro feedback (Bug 7)
- Zero contamination: no TEST_MODE, no bookstore content, no old names
- All PIL interactions live input (8 input points)
- 40 cells total

**What was not changed:**
- Nine-stage workflow structure
- Verbalized Sampling system for Creator
- Studio Brief Document compression architecture
- Session JSON schema v2.2 (additive only)
- Prompt files (name cleanup done separately via find-and-replace)

---

### [2026-03-25 – 2026-04-02] Phase 3 Visualization — Development Arc

**Status:** Three tracks developed in sequence; two complete, one active
**Location:** `phase_3_visualization/`
**Full documentation:** `phase_3_visualization/README.md`

**Track 1 — Galaxy / Flower (p5.js, Sketches 1–21)**
Over 21 sketches in p5.js, a visual grammar emerged: a multi-ring Fibonacci flower forming from inside outward, with role-coded light points entering from the periphery and settling as luminous petals around a nucleus representing final synthesis. The full visual spec is in `_resources/continuity_prompts/PHASE3_SESSION_UPDATE.md`.

Canonical frozen file: `phase_3_visualization/galaxy_dev_sketches/sketch_21_galaxy_canonical/creative_prism_sketch_21.js` — Step 4 locked. Terminus-first architecture, continuous comet-tail taper renderer, emergent interference nodes, three-ring golden angle structure.

**Status: Frozen.** The spiral galaxy metaphor was determined to be conceptually wrong for the data. The visual language developed here — role color semantics, temporal arc, formation-from-center, light-point-to-petal metaphor — is composted into future work and will resurface in the Eye motif in reincarnated form.

**Track 2 — Membrane Landscape (Three.js, Sketches 22–23)**
Developed in collaboration with Google Gemini Pro (March 28, 2026). A continuous procedural membrane with a raised rim profile representing the semantic domain — the field of knowledge through which a session moves. Connects directly to gradient descent visualization in ML and to the dream imagery that originally inspired the project.

Canonical file: `phase_3_visualization/landscape_dev_sketches/sketch_22_canonical/creative_prism_sketch_22.js`

Three immutable architectural pillars established and locked:
1. Shadow maps disabled (`renderer.shadowMap.enabled = false`) — pure geometric shading
2. Calculus normals via finite difference derivatives — not `computeVertexNormals()`
3. C2 continuous mathematics — fractional power curves (1.5 exponent), 5th-order smootherstep

Full eight-step failure and diagnosis record: `phase_3_visualization/landscape_dev_sketches/sketch_22_canonical/sketch_22_development_log.docx`

Sketch 23 (Three.js bubble/metaball overlay) — built, technically functional, aesthetically wrong. Abandoned. Preserved in `phase_3_visualization/landscape_dev_sketches/sketch_23/`.

**Status: Sketch 22 complete at Step 1. Step 2 (pearl placement) is next.**

**Track 3 — Eye Motif (SVG + Anime.js, Active)**
Emerged from the final frame of the Sketch 22 development session, which resembled an eye. The motif: a dashed circle boundary (domain), nodes entering from the perimeter and trailing inward toward a central point where they merge into a solid pupil (synthesized thought).

Stack: SVG + Anime.js — crisp vector math, deliberate easing, resolution independence, full editorial control.
SVG source files: `phase_3_visualization/metaball_dev/eyedev/`

**MVP: Replay instrument** — post-session retrospective where a recorded session unfolds chronologically using actual timestamps for pacing. Role-specific node materials, emergence animations. Target: creativeprism.ai.

**Status: Visual language in active exploration. Prototype build pending.**

---

### [2026-04-06/07] Experiment 5 — Phase 1 v2.0 First Live Run with Traits Matrix

**Status:** COMPLETE — first successful v2.0 live run; two bugs found and fixed
**Engine:** v2.0 · **Notebook:** `creative_prism_studio_v2_0.ipynb`
**Session:** `session_20260407_001244_0afc528c.json`
**Director model:** claude-sonnet-4-20250514 · **Team model:** claude-haiku-4-5-20251001
**PIL:** Peter (live input)

**Brief:** ADD/perfectionism — user arriving with pattern of abandoning meaningful
projects mid-way. Director reframed as vision-reality gap, not a motivation problem.

**What worked:**
- Traits matrix produced distinct, readable role personalities in system prompts
- Director team configuration applied meaningful adjustments for the problem type
- Five-band language directives produced observable tone differences across roles
- Researcher citations were precise and substantive: Barkley (temporal motivation
  theory), Deci & Ryan (self-determination theory), Piers Steel (procrastination
  meta-analysis), Hallowell & Ratey (satisficing as neurological relief for ADD brains)
- Final synthesis — "The Perfectionist's Completion System" — was directly responsive
  to the reframed problem and grounded in the research
- evaluation_payload correctly assembled with baseline and synthesis for comparison

**Bugs found and fixed during session:**

1. **Creator Pass 2 truncated** — max_tokens=1200 insufficient for full two-pass
   refinement. A3 direction cut off mid-sentence. Fix applied: raised to 2400.
2. **Second loop not triggering** — `second_exploration.triggered` flag was being set
   by Stage 8 correctly but no cell was reading it. Stage 8c cell was missing entirely.
   Fix applied: JSON signal parser added to Cell 10; Cell 10c (Stage 8c) created to
   re-run full Creator/Critic/Researcher loop when flag is True.

**Observations:**
- 52-trait matrix is working — role outputs feel calibrated, not generic
- ADD/perfectionism demonstrates the system's range beyond business/brand problems
- The reframing mechanism (vision-reality gap) drove the synthesis quality
- Second loop gap was a significant architectural hole — now closed

---

### [2026-04-08] Session Comparison — Petrina's v1.5 vs v2.1

**Status:** COMPLETE — comparative analysis, no new PIL session
**Sessions compared:**
- v1.5 original run (session `4ced178a`) — Haiku Director, pre-traits-matrix
- v2.1 re-run (session `61034eec`) — Sonnet Director, traits matrix active

**Key findings:**

1. **Governed domain gap identified** — zero-shot Haiku baseline caught the commercial
   kitchen licensing requirement (NY State food service regulations, commercial kitchen
   partnership required before permit application, 45-90 day timeline) immediately.
   The v2.1 Sonnet Director produced a richer, more aspirational brief but missed it.
   The baseline outperformed the studio on this specific dimension despite lower overall
   quality. This is a documented finding — the Prism will not always outperform on
   every dimension. Report honestly in evaluation.

2. **Synthesis quality improvement confirmed** — v2.1 Director produced materially
   better synthesis: specific cost breakdowns, phased milestones (Year 1 vs Year 2),
   budget risk thresholds, compliance-first launch sequence. v1.5 synthesis was
   aspirational but thin on operational specifics.

3. **PIL experience improvement confirmed** — Peter reported feeling more heard and
   engaged in v2.1 session. Discovery was more targeted, reframing more precise.

**Action taken:** director.md v1.3 and researcher.md v1.3 written to address the
governed domain gap structurally. Director now required to name regulatory/legal
hard boundaries in the Brief regardless of whether PIL mentioned them. Researcher
now treats governed domain compliance research as Category 1 (automatic, not optional).

---

### [2026-04-08] Engine v2.1 Build — Baseline Generation, Evaluation Payload, Bug Fixes

**Status:** COMPLETE — committed and pushed to `github.com/PeterComitini/creative_prism`
**Engine:** v2.1 · **Notebook:** `creative_prism_studio_v2_1.ipynb`

**What was added:**

Engine v2.1:
- `generate_baseline()` — zero-shot Control B call. Raw prompt → SESSION_MODEL, no
  system prompt. Called once at session start, before any agents run.
  Architecture is the isolated variable; same model capability throughout.
- `assemble_evaluation_payload()` — packages `problem_prompt`, `baseline_response`,
  and `final_synthesis` into `evaluation_payload` block at session end
- `evaluation_payload: {}` field added to `create_blackboard()` schema

Notebook v2.1 (20 cells total):
- Cell 1: Imports updated for v2.1 functions
- Cell 3: Baseline generation call added; session opens "Welcome to The Creative Prism"
- Cell 7b: Creator Pass 2 `max_tokens` 1200 → 2400 (Exp 5 fix)
- Cell 10: Stage 8 signal extraction converted to JSON format; `max_tokens` 400 → 800
- Cell 10c (NEW): Stage 8c Second Loop — re-runs Creative Team when
  `second_exploration.triggered` is True (Exp 5 fix)
- Cell 12: `assemble_evaluation_payload(blackboard, baseline_response)` before
  `save_session()`

Prompt files updated:
- `director.md` v1.3 — governed domain constraint recognition section added
- `researcher.md` v1.3 — governed domain as Proactive Behavior 2 (Category 1)
- All other prompt files — "Creative Mirror" references removed, confirmed clean

Repository:
- Renamed from `intelligence-of-seeing` to `creative_prism` on GitHub
- `phase_3_visualization/` added to `.gitignore` (large binary files)
- Last commit: "engine+notebook+eval: v2.1 complete — second loop, governed domain
  prompts, dual evaluator"

---

### [2026-04-08] Evaluation Framework — prism_evaluator.py v2.0

**Status:** COMPLETE
**File:** `phase_2_experiments/prism_evaluator.py`

**Architecture:**
- Gemini 1.5 Pro + GPT-4o score sessions independently (cross-family, no alignment bias)
- Both evaluators receive identical evaluation prompt and score blind
- Agreement calculated per dimension (≤1 point = agree; divergence flags rubric ambiguity)
- Composite score = average of both evaluators — authoritative result
- Skips already-evaluated sessions (no re-spending API budget)
- Outputs `eval_<session_id>.json` to `phase_2_experiments/outputs/`

**Tier 1 metrics (computed from session JSON, no LLM required):**
1. Brief Specificity Delta — brief word count / prompt word count (>1.5 = meaningful)
2. Pass 1→2 Novelty — 1 - (shared words / total unique words) across ideation cycles
3. Researcher Citation Rate — proportion of research_trace entries with citation signals

**Tier 2 dimensions (LLM scored):** Anchor Integrity · Constraint Engagement ·
Structural Coherence · Adaptive Interpretation · Failure Honesty

**Requires in .env:** `ANTHROPIC_API_KEY` · `GEMINI_API_KEY` · `OPENAI_API_KEY`

**Rationale for cross-family design:** Using two evaluators from different AI families
eliminates the alignment bias that would arise from using a single evaluator or two
evaluators from the same family. Agreement between independent evaluators replaces
the need for human inter-rater reliability checks.

---

## NEXT MILESTONE — v3.0 Experimental Runs

**Target:** Lock system at v3.0, run standardized experiments on two test groups

**Two patches not yet applied — apply before v3.0 lock:**

Patch A — Session notes (Cell 12, before save_session):
```python
session_notes = input("\nSession notes (press Enter to skip):\n> ").strip()
if session_notes:
    blackboard["session_metadata"]["notes"] = session_notes
```

Patch B — Scenario metadata (Cell 3, after scribe_log session_start):
```python
scenario_id = input("Scenario ID (press Enter to skip): ").strip()
if scenario_id:
    scenario_category = input("Category: ").strip()
    blackboard["session_metadata"]["scenario_metadata"] = {
        "scenario_id":       scenario_id,
        "category":          scenario_category,
        "prompt_as_entered": initial_prompt
    }
    print(f"  Scenario: {scenario_id} [{scenario_category}]")
```

**Test set:** 30 prompts in `_resources/User Test Prompts/THE_30-PROMPT_CORE_SET.docx`
(15 stress test + 15 conventional enterprise). Stress test set additionally expanded
by ~7 unique prompts in `System_Stress_Test_Prompts___scoring_rubric.md`.
Peter to add bookstore + up to 4 more conventional prompts before v3.0 lock.

**Sequencing:**
1. Apply Patches A and B
2. Diagnostic pass — 3-5 stress test prompts, fix critical failures
3. Lock at v3.0
4. Run Group 1 (standard set) first — primary efficacy claim
5. Run Group 2 (stress test) second — robustness characterization

---

## TRAIT WEIGHT EXPERIMENTS

| Date | Role | Trait | From | To | Mode | Observed Effect |
|---|---|---|---|---|---|---|
| 2026-04-01 | Creator | practicality | 0.40 | 0.65 | Exp 3 (chicken parm) | Director raised for practical business problem |
| 2026-04-01 | Critic | critical_strictness | 0.90 | 0.95 | Exp 3 (chicken parm) | Director raised to protect against financial risk |
| 2026-04-06 | Creator | intellectual_adventurousness | raised | — | Exp 5 (ADD/perfectionism) | Director raised for conceptual reframing problem |
| 2026-04-06 | Researcher | citation_rigor | raised | — | Exp 5 (ADD/perfectionism) | Director raised; citations were precise and substantive |

---

## SECOND GENERATION TARGETS

| Feature | Description | Priority | Status |
|---|---|---|---|
| Live-building visualization | Half-chat, half-visual — map builds as session progresses | High | Planned |
| Director team-building | Director dynamically configures role traits per problem type | High | IMPLEMENTED v1.5 / v2.0 |
| Scribe dual mission | (1) Session report for PIL (2) Semantic trajectory data for visualization | High | Planned |
| Stage 8b — depth extraction | Director-PIL dialogue using extraction games before final synthesis | High | IMPLEMENTED v1.5 |
| Iteration loop | Conditional re-run of creative team when Director signals ITERATE | High | IMPLEMENTED v1.4 |
| Adaptive discovery | Director-controlled discovery loop with extraction toolkit | High | IMPLEMENTED v1.5 |
| Routing gate | Director classifies requests before engaging studio | High | IMPLEMENTED v1.5 |
| PIL reframing confirmation | Director proposes reframing, PIL confirms before brief | Medium | IMPLEMENTED v1.5 |
| 52-trait matrix | Full trait system replacing 9-dimension prototype | Medium | IMPLEMENTED v2.0 |
| Replay instrument (Phase 3 MVP) | Post-session retrospective using session JSON timestamps | High | Active — Eye motif track |
| Scribe during-session mode | Key nodes written in real time | Medium | Planned |
| Session comparison | Scribe compares Before/After delta across sessions | Medium | Planned |
| Token compression strategies | Prompt engineering to deliver equal depth within tighter budgets | Medium | Partially addressed (brief max_chars) |

---

## KNOWN ISSUES

| Issue | Severity | Status | Notes |
|---|---|---|---|
| `idea_space` not yet populated | Low | Noted | Schema field exists, Phase 1 doesn't write to it yet |
| Researcher autonomous trigger not wired | Low | Noted | Prompt describes behavior, code doesn't implement trigger |
| Scribe LLM call not implemented | Low | Noted | `scribe_log()` is mechanical Python. Scribe LLM call is future |
| Bug 4 (duplicate brief entries) | Low | Diagnosed | Audit update_brief_doc calls in Director Review |
| Iteration loop in v2.0 simplified | Low | Noted | Prints skip message instead of re-running full team |
| Director closing question hangs | Low | Noted | Stage 9 asks a question but no Cell 13 collects the response — known gap, v4.0 scope |
| Session notes not yet captured | Low | Pending | Patch A code written, not yet applied to notebook |
| Scenario metadata not yet injected | Low | Pending | Patch B code written, not yet applied to notebook |

---

## PHASE ROADMAP

```
Phase 1  Early Experiments        Complete
           Socratic Spiral, Prism, HITL, temperature sweeps
           phase_1_experiments/

Phase 2  Full Studio Workflow     Active — v2.1 current
           Engine v2.1 — baseline generation, evaluation payload, second loop
           Experiments 1-5 complete · Session comparison complete
           Evaluation framework (prism_evaluator.py v2.0) complete
           Next: Apply Patches A+B → diagnostic pass → lock v3.0 → experimental runs
           phase_2_experiments/

Phase 3  Visualization            Active (parallel track)
           Galaxy/flower (Sketch 21) — frozen
           Membrane landscape (Sketch 22) — Step 1 locked, Step 2 next (Gemini)
           Eye motif — visual language exploration, prototype pending
           Replay instrument MVP for creativeprism.ai
           phase_3_visualization/ (gitignored)
```

---

## REFERENCES

| Document | Version | Location |
|---|---|---|
| System Constitution | V2.2 | `phase_2_experiments/governance/system_constitution_v2_2.docx` |
| System Laws | V1 | `phase_2_experiments/governance/system_laws.docx` |
| Operating Protocol | V2.1 | `phase_2_experiments/governance/operating_protocol_v2.1.docx` |
| Discovery Framework | V2.1 | `phase_2_experiments/governance/discovery_framework_v2.1.docx` |
| Director Evaluation Protocol | V2.1 | `phase_2_experiments/governance/director_evaluation_protocol_v2.1.docx` |
| Blackboard Data Model | V1 | `phase_2_experiments/governance/blackboard_data_model_v1.docx` |
| Studio Run Schema | V2.2 | `phase_2_experiments/phase_2_archive/notebooks_v2/schema/studio_run_schema_v2_2.json` |
| Traits Matrix | V2 | `phase_2_experiments/persona_traits_matrix_v2.csv` |
| System Architecture Spec | V1 | `phase_2_experiments/governance/system_architecture_specification.docx` |
| v2.0 Build Spec | V1 | `_resources/continuity_prompts/opus_prompt_v2_build.md` |
| Phase 3 visual grammar spec | — | `_resources/continuity_prompts/PHASE3_SESSION_UPDATE.md` |
| Sketch 22 technical post-mortem | — | `phase_3_visualization/landscape_dev_sketches/sketch_22_canonical/sketch_22_development_log.docx` |
| Medium Article Draft | — | in progress |

---

*"The prism does not replace the thinker. It expands the range of thinking available to them."*
— System Constitution V2.2
