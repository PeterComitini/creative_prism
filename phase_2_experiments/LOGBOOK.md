# LOGBOOK
## The Creative Prism — Experiment Record

*Active experiment log for the Creative Prism project.*
*Predecessor work: `phase_1_experiments/LOGBOOK.md`*
*First Creative Prism experiment: `phase_2_experiments/phase_2_archive/NOTES.md`*

---

## SYSTEM OVERVIEW

**Engine:** `engine.py` v2.1 (Claude) · `engine_openai.py` v1.0 (OpenAI) · `engine_hybrid.py` v1.0 (Hybrid — active)
**Schema:** Blackboard v2.2 + routing block (hybrid)
**Notebooks:** `creative_prism_studio_v3_1.ipynb` (Claude v3.2) · `creative_prism_studio_openai_v3_1.ipynb` (OpenAI) · `creative_prism_studio_v4_0.ipynb` (Hybrid — active)
**Role sequence:** Director → Creator → Critic (cross-model) → Researcher → Creator Pass 2 → Critic Pass 2 (cross-model) → Director
**Traits system:** 52-trait matrix (`persona_traits_matrix_v2.csv`) with five-band language directives
**Models:** Hybrid — PRIMARY_PROVIDER routes Director + Creative Team; CRITIC_PROVIDER always opposite
**Evaluator:** `prism_evaluator.py` v2.0 — dual evaluator (Gemini 1.5 Pro + GPT-4o)
**Prompt directories:** `prompts/` (Claude) · `prompts_openai/` (OpenAI) · `prompts_hybrid/` (Hybrid — active)

---

## ARCHITECTURE DECISIONS LOG

| Decision | Rationale |
|---|---|
| `engine.py` as machinery, notebooks as experiments | Production-ready pattern, clean separation |
| Studio Brief Document as shared memory | Real studio practice, ~800-1200 tokens, no summarization loss |
| Role sequence: Creator → Critic → Researcher | Researcher acts on ideation output, not bare brief |
| Two-pass Creative Team loop | Creator → Critic → Researcher → Creator Pass 2 → Critic Pass 2 → Director |
| Scribe runs end-of-session, on by default | Most distinctive UX feature |
| Researcher: one autonomous contribution per session | Bounded proactivity — Director as permission gate |
| JSON brief format with validation gate | Eliminates fragile line-by-line parsing failure mode |
| Sessions gitignored, curated manually | Experimental data |
| `prompts/` and `governance/` gitignored | Core IP |
| Visualization target: Eye motif (SVG + Anime.js) | Replay instrument — post-session retrospective |
| Adaptive discovery loop (v1.5+) | Director controls turn count (1-6), deploys extraction toolkit |
| Routing gate (v1.5+) | Director classifies STUDIO / DIRECT / OUT_OF_SCOPE |
| DIRECTOR_MODEL separate from SESSION_MODEL (v1.5+) | Sonnet for PIL-facing, Haiku for Creative Team |
| Director team configuration (v1.5+) | Director tunes Creative Team traits per problem |
| 52-trait matrix replaces 9-trait system (v2.0) | Values-based personality system with five-band language |
| Brief document max_chars (v2.0) | read_brief_doc() loads only most recent 12000 chars |
| All PIL interactions live input (v1.5.2+) | No simulated personas |
| generate_baseline() (v2.1) | Zero-shot Control B call before agents run |
| assemble_evaluation_payload() (v2.1) | Packages prompt/baseline/synthesis for evaluator |
| Stage 8c Second Loop (v2.1) | Re-runs Creative Team when second_exploration.triggered is True |
| Governed domain constraint recognition (v2.1) | Director names regulatory/legal hard boundaries |
| Researcher governed domain priority (v2.1) | Compliance research is Category 1 |
| Verbalized Sampling Step 0 (v3.0) | Creator names convergence mode before assigning bands |
| Critic Surprise Audit (v3.0) | Required field in every Pass 1 — flags predictable HIGH band |
| Researcher equal band weight (v3.0) | LOW band research treated as Category 1 |
| Researcher self-budgeting (v3.0) | Complete each finding before starting next; name gaps |
| Assumption Validation replaces Open Questions (v3.0) | Director states premises, PIL corrects |
| pressure_point field in brief (v3.0) | Productive tension for the Creative Team |
| Reframing signal read (v3.0) | Director branch: A) confirmed B) new signal C) significant correction |
| Lifecycle Stage Assessment (v3.0) | Stage changes what solution must address |
| Functional Domain Inventory (v3.0) | Catches implied but unmentioned domains |
| Discovery planning enforcement (v3.0/v3.1) | Forced choice capped at 2; Director plans before first turn |
| Focused Refinement replaces second loop (v3.1) | Director restatement → Creator 1-2 directions → conditional Researcher → selection → PIL mini-presentation |
| Stage 8c→9 gap closed (v3.1) | PIL sees refined directions before final synthesis |
| Stage 8b minimum signal threshold (v3.1) | ≤10 word responses trigger one re-probe |
| Transparency on request (v3.1) | PIL can request research, evaluation, or full internal dialogue |
| Presentation format expansion (v3.2) | Core Move 8-12 sentences; Research Foundation self-contained for PIL |
| Research Foundation PIL-first rule (v3.2) | PIL has not seen research — named cases require one sentence of context |
| Stage 9 research-anchored synthesis (v3.2) | Director draws on research_trace; phased action plan; no fabricated citations |
| Stage 9b Research Appendix (v3.2) | Full research trace printed after synthesis with verification caveat |
| Multi-provider architecture (v4.0) | engine_hybrid.py holds both Anthropic and OpenAI clients; call_role() dispatches by provider |
| Cross-model Critic injection (v4.0) | Critic always runs on opposite provider from primary — creative challenge vs constraint challenge |
| Cell 2b Model Routing (v4.0) | Lightweight classifier scores orientation 0.0–1.0; tiebreaker for balanced zone; operator override available |
| Orientation vocabulary: Creative / Strategic (v4.0) | Replaces Expansion/Constraint framing — maps to how people actually think about these functions |
| critic_gpt.md — GPT Critic prompt (v4.0) | Evaluates distinctiveness, positioning, surprise, behavioral resonance — complement to critic.md constraint orientation |
| Routing decision recorded in blackboard (v4.0) | routing block stores orientation score, primary/critic provider, tiebreaker answers, rationale |
| Traits matrix shared across all providers (v4.0) | Model-agnostic — same persona_traits_matrix_v2.csv used by Claude, OpenAI, and Hybrid engines |
| Typo fix: curiosity trait (v4.0) | "curPRISMITY" corrected to "curiosity" across all prompt files and matrix |

---

## INTELLECTUAL FOUNDATION

| Source | Relevance |
|---|---|
| Bohm — Thought as a System | Proprioception of thought — philosophical foundation |
| Dowd — Taking Root to Fly | Somatic proprioception — origin of the core insight |
| IDEO / d.school HCD | Discovery methodology, sacrificial concepts |
| Shneiderman — HCAI Framework | Amplify / augment / empower / enhance |
| Verbalized Sampling (arXiv 2510.01171) | Validates ideation diversity approach |
| VECTOR (arXiv 2509.14455) | Validates semantic trajectory visualization |
| Cognitive-Affective Maps (Thagard/Reuter) | Visualization theory with affective valence |
| Socratic Dialogue (MSP Tool 49) | Structural predecessor |
| Albers / Abstract Expressionists / Duchamp / LeWitt | Modernist lineage: medium as subject |

---

## EXPERIMENT RECORD

### [2026-03-17] Experiment 1 — Phase 1 v1.0 First Run
**Status:** PARTIAL — archived. First full end-to-end workflow. TEST_MODE bookstore brief.
All 18 trace steps executed. Brief parsing failure, content truncation, wrong role sequence.
Full diagnosis: `phase_2_experiments/phase_2_archive/NOTES.md`

---

### [2026-03-18] Architecture Redesign — v1.1 / v1.2
**Status:** Complete. Studio Brief Document added. JSON brief format. Role sequence corrected.
Engine fixes: SESSIONS_DIR, brief_doc parameter in call_role() and build_prompt().

---

### [2026-03-19] Experiment 2 — Phase 1 v1.2 First Run
**Status:** COMPLETE — first clean full-pipeline execution
**Session:** `session_20260319_123403_efd6ce66.json`
**Brief:** Bookstore cafe brand identity.
Creator produced 4 distinct VS directions including A4 (p=0.11, "The Heretical Reading Practice") which drove the final synthesis — validates VS approach directly.
A4 at p=0.11 was the most surprising direction and became the most important one.

---

### [2026-03-19] Article Development — Medium Draft Sections Written
Sections: The First Clean Run, The Studio Model, The Memory Problem, The Lineage of the Idea, Conclusion: The Eighth Square.

---

### [2026-04-01] Experiment 3 — Phase 1 v1.5 First Live PIL Session
**Status:** PARTIAL — session terminated (TEST_MODE contamination)
**Brief:** Chicken Parmesan sandwich business — Petrina's.
First live session. Discovery worked. TEST_MODE contamination killed Critic pass.

---

### [2026-04-01] Experiment 4 — Phase 1 v1.5.1/v1.5.2
**Status:** PARTIAL — new bugs surfaced
Same chicken parm scenario. Session ran further. Researcher truncation, Director Review reading wrong pass, brief doc duplication identified.

---

### [2026-04-03] Engine v2.0 Build — Traits Matrix
**Status:** COMPLETE — built by Opus 4.6
52-trait persona matrix. load_traits_matrix(), weight_to_band(), build_trait_profile(). Old ROLE_WEIGHTS system retired. All names updated to Creative Prism.

---

### [2026-03-25 – 2026-04-02] Phase 3 Visualization — Development Arc
**Track 1** (p5.js Galaxy/Flower, Sketches 1-21): Frozen. Wrong metaphor for data.
**Track 2** (Three.js Membrane, Sketch 22): Step 1 locked. Three immutable pillars established. Step 2 (pearl placement) next.
**Track 3** (SVG + Anime.js Eye Motif): Active. Dashed circle boundary, nodes trailing inward to synthesis. MVP: Replay instrument for creativeprism.ai.

---

### [2026-04-06/07] Experiment 5 — Phase 1 v2.0 First Live Run
**Status:** COMPLETE
**Brief:** ADD/perfectionism — pattern of abandoning meaningful projects.
Traits matrix produced distinct role personalities. Final synthesis: "The Perfectionist's Completion System."
Bugs fixed: Creator Pass 2 max_tokens raised to 2400. Stage 8c created for second loop.

---

### [2026-04-08] Session Comparison — Petrina's v1.5 vs v2.1
Zero-shot Haiku baseline caught commercial kitchen licensing; Sonnet Director missed it.
Documented honestly — the Prism does not always outperform on every dimension.
director.md v1.3 and researcher.md v1.3 written to address governed domain gap structurally.

---

### [2026-04-08] Engine v2.1 Build
**Status:** COMPLETE — committed to GitHub
Added: generate_baseline(), assemble_evaluation_payload(), Stage 8c cell (Cell 10c), JSON signal extraction, Creator Pass 2 2400 tokens.

---

### [2026-04-08] Evaluation Framework — prism_evaluator.py v2.0
**Status:** COMPLETE
Gemini 1.5 Pro + GPT-4o score independently. Tier 1 JSON metrics + Tier 2 LLM scoring.

---

### [2026-04-10 – 2026-04-13] Development Session — v3.0/v3.1 Overhaul

**Status:** COMPLETE

This session addressed gaps identified through comparative analysis of 5 conventional sessions (C-26 through C-30) and 2 stress tests (S-01 housing vs climate). Complete changes follow.

---

#### Extraction Games Expansion (director_extraction_games.md v1.3)

**Games 12-15 — Analytical Tools:**
- Game 12: Root Cause Drill — adapted Five Whys, "what's underneath" not "why"
- Game 13: Future Headline — forces articulation of success in concrete language
- Game 14: Best/Worst — surfaces both ambition and fear in one exchange
- Game 15: Assumption Surface — names the unexamined premise

**Games 16-19 — Playful Tools:**
- Game 16: Personification — describe business/brand as a person at a dinner party
- Game 17: Obituary — describe the failure scenario to surface hidden constraints
- Game 18: The Alien — explain to someone who knows nothing; strips expert vocabulary
- Game 19: The Gift — unconstrained desire reveals the aspirational brief

**WHEN TO USE WHICH GAME section added:**
Five columns: PIL can't say what they want / can't say it abstractly / framing feels wrong / need to understand stakes / signal is weak.

**HOW MIGHT WE** identified as Director's internal brief-writing tool, not a PIL-facing game. Added to integration section of extraction games doc.

---

#### creator.md v1.2

**Step 0 — Probability Landscape Assessment (new, required):**
Before assigning any band, Creator names what most models would converge on for this brief. This is the mode the Creator is deliberately moving away from. All bands calibrated relative to this assessment.

Without Step 0: bands are labels assigned to pre-generated ideas → probability lock (0.68/0.38/0.16 every session).
With Step 0: Creator genuinely assesses distribution → varied scores, true tail-sampling for LOW band.

Evidence from VS paper (arXiv 2510.01171): VS recovers pre-training distribution when model is prompted to verbalize probabilities. Without naming the mode, the model defaults to the aligned/collapsed distribution.

**LOW band operationalization (3 steps):**
1. State conventional approach in one sentence
2. Explicitly move away from that starting point
3. Ask: what would this problem look like if it weren't this kind of problem?

**Band ranges tightened:** HIGH 0.55-0.75 (was 0.55-0.80), LOW 0.05-0.18 (was 0.08-0.22)

**WHAT YOU NEVER DO additions:**
- Skip Step 0
- Produce LOW band direction that's just a strange variation of HIGH band starting point

---

#### critic.md v1.2

**Surprise Audit (new, required field in every Pass 1):**
After evaluating all three directions, Critic asks: could the PIL have predicted the HIGH band direction from what they told the Director?
- If yes: flags explicitly, recommends less predictable HIGH or elevating MID to lead
- If no: confirms with brief statement of what makes it surprising

**HOW YOU THINK addition:**
"Could the PIL have predicted this direction from what they said in discovery?"

**WHAT YOU NEVER DO additions:**
- Skip the Surprise Audit
- Accept predictable execution of the obvious answer as sufficient

---

#### researcher.md v1.3

**Equal weight across all bands:**
LOW band direction research treated as Category 1, not secondary to conventional directions. Unconventional directions often need research most — they're starting from unmapped territory.

**Self-budgeting instruction:**
1. Identify all requests before writing any response
2. Prioritize: governed domain first, LOW band research equal to others
3. Complete each finding fully before starting next
4. If capacity runs short: name what wasn't addressed rather than truncate mid-sentence
"Depth on three well-developed findings beats five findings that end mid-sentence."

---

#### director.md v1.5 additions

**Lifecycle Stage Assessment (new section):**
5 stages with signal vocabulary: pre-launch, early traction, growth, mature, pivot.
Stage determines what solution must address — wrong stage = wrong brief.
Ambiguity path: one targeted question, or surface as Stage 3b assumption.

**Functional Domain Inventory (new section):**
6x5 domain-stage matrix (illustrative, not lookup table).
Domains: branding/identity, operations, governed domains, competitive positioning, customer experience, financial model.
Stage-qualified requirements — established brands do not reflexively receive branding advice.
Key question: does the PIL need to build it, formalize it, protect it, or evolve it?

---

#### director.md v1.6 additions (same session)

**Discovery planning — hardened enforcement:**
"Failure to plan" framing replaces soft guidance.
"Forced choice may not be used more than twice in a session."
From turn 3 onward, forced choice is unavailable — not a preference, a prohibition.
Concrete positive example of well-planned session (turn 1 forced choice, turn 3 personification, turn 5 deliberate provocation).

Evidence for why this was necessary: S-01 session ran with v1.5 director.md deployed — still produced 4 forced choices in 6 turns. Prompt compliance failure: model weighs soft instruction against path-of-least-resistance pull toward forced choice; forced choice wins. v1.6 removes the choice.

**Presentation transparency hooks (new requirement):**
Each direction in every presentation must include one transparency hook — research anchor or evaluation signal. One sentence. Invitation not disclosure. PIL decides whether to ask.
Purpose: PIL knows the reasoning depth exists and can access it.

**Transparency on request (new section):**
Three disclosure levels: research findings, Critic evaluation, full internal dialogue.
Example phrasing for each level.
"The opacity is a default, not a rule. When the PIL asks to see inside, show them."
"The Creative Prism is not a black box."

---

#### Notebook Changes

**Cell 5 (Stage 2 & 3 — Reframing + Creative Brief):**
- signal_read_response call added after PIL confirmation input
- Three-branch logic: A) confirmed B) new signal C) significant correction
- signal_read_response passed into brief_task
- brief JSON: assumptions field (stored as open_questions for schema compatibility)
- pressure_point field added
- Brief display and console print updated

**Cell 4b (Stage 3b — complete rewrite):**
- Renamed: "Open Questions to PIL" → "Assumption Validation"
- Director presents inferred premises for PIL correction
- One constraint question: what would be off the table?
- Director synthesis call after PIL response: acknowledges, names additions, confirms ready
- Goal: PIL feels heard and understands what changed before ideation starts

**Cell 10b (Stage 8b — updated):**
- Minimum signal threshold: ≤10 words triggers one re-probe
- Re-probe uses different technique
- Maximum one re-probe — if second answer also thin, log whichever has more substance
- Thin-signal flag noted in brief doc

**Cell 10c (Stage 8c — complete rewrite):**
Was: Full Creator → Critic → Researcher second loop (same cost as first loop, largely redundant)
Now: Focused Refinement

Step 1 — Director restatement: JSON output with rejection_type (flat/partial/reframe), surviving_direction, restated_brief, research_needed, research_question
Step 2 — Conditional Researcher: only fires if Director flagged; one targeted question, 1200 tokens max
Step 3 — Creator focused pass: 1-2 directions only targeting identified gap; Step 0 still required
Step 4 — Director selection: flat → new only; partial → survivor + new (max 3); reframe → new only
Step 5 — Director presents refined directions with transparency hooks
Step 6 — PIL reacts via live input (closes Stage 8c → Stage 9 gap)
Step 7 — Director reads reaction, acknowledges, logs signal, proceeds to synthesis

Removed from second loop: Critic pass (Director reviews directly with full accumulated context)
Token savings: approximately two-thirds reduction vs original second loop

**Cell 12 (Session Record — updated):**
- Director summary call added (was missing from project notebook entirely)
- Fix: brief_doc=read_brief_doc(session_id) (was missing entirely)
- Prompt: name domain, core challenge, solution direction; max 35 words
- Try/except wrapper: summary failure does not block session save
- Result stored in blackboard["session_metadata"]["director_summary"]

---

#### Comparative Analysis — Three Petrina's Runs

Sessions: v1.5 (4ced178a), v2.1 (61034eec), v3.0 (a9c19752)

Key improvements v1.5 → v3.0:
- Discovery: forced choice ×2 + fill_blank ×2 (was forced choice ×2-3 only)
- Assumption validation captured: semi-retired, $5K budget, fresh-fried on-site — new signal not in prior runs
- Pressure point present in brief (first time)
- Step 0 fired in Creator Cycle 1 — mode named as "systematize recipe, certify, build brand"
- Surprise audit working — HIGH band flagged as predictable from brief
- Synthesis quality: strongest of three runs
- Branding gap identified: structural absence — now addressed by Functional Domain Inventory

Persistent gap: director_summary blank in all three runs → fixed in Cell 12 rewrite.

---

#### Stress Test — S-01 Housing vs Climate Infrastructure
**Session:** `session_20260412_235102_7fc5d0e5.json`
**Prompt:** Design a decision framework for a city choosing between public housing and climate infrastructure.
**PIL:** Peter playing grumpy, conflicted decision-maker intentionally.

What worked: reframing branch fired correctly (SIGNIFICANT CORRECTION logged), assumption validation captured 120-day timeline + democratic vote + no education defunding, pressure point strong, Step 0 fired, research R001+R002 each ~14,500 chars no truncation, Surprise Audit correctly flagged predictable HIGH band, second loop triggered correctly.

What failed: 4 forced choices in 6 turns despite v1.5 director.md deployed (prompt compliance failure → v1.6 hardening), Stage 8c→9 gap (PIL never saw second-loop output before synthesis → Cell 10c rewrite), depth extraction logged "that would help" as usable signal (→ Cell 10b threshold), director_summary blank (→ Cell 12 fix).

PIL behavior note: even with difficult intentional behavior, system maintained professional scope throughout. The framework worked within its constraints.

---

#### Design Debate — Critic Role in Second Loop
**Resolved: Critic removed from second loop; retained in first loop.**

Analysis: By second loop, Critic has done full two-pass evaluation. Director has reviewed. PIL has reacted. The second-loop Creator writes into an already-rich evaluative context. Running formal Critic pass is redundant scaffolding.

Critic's irreplaceable first-loop contributions: PATTERN sections (cross-direction structural insights), synthesis direction S1 (consistently the most sophisticated direction). These require genuine peer separation — Creator cannot evaluate its own output simultaneously.

Architectural note: The Director/Critic dynamic was observed live in the design session. When Peter proposed removing the Critic (devil's advocate) and Claude stress-tested the idea honestly rather than validating it, the exchange produced better architectural understanding than agreement would have. The role separation being designed into the system was itself demonstrated by the process of designing it.

---

## NEXT MILESTONE — v3.1 Deployment and Experimental Runs

**Files to deploy locally:**

Notebook patches (full cell replacements):
- `cell_10b_depth_extraction.py` → Cell 10b
- `cell_10c_focused_refinement.py` → Cell 10c
- `cell_12_session_record.py` → Cell 12
- `cell5_corrected.py` → Cell 5

Prompt files (full file replacements):
- `creator.md` v1.2
- `critic.md` v1.2
- `researcher.md` v1.3
- `director.md` v1.6
- `director_extraction_games.md` v1.3

**Diagnostic pass checklist after deployment:**
- [ ] Step 0 fires and produces varied probabilities (not 0.68/0.38/0.16 lock)
- [ ] Surprise audit present in every Critic Pass 1
- [ ] Forced choice not used more than twice per session
- [ ] Stage 8c → Stage 9: PIL sees refined directions before synthesis
- [ ] Director summary populated in session JSON

**Medium article:**
- Parts I-IV written: early experiments through evaluation framework
- Part V needed: covers v3.0/v3.1 overhaul, three-run Petrina's comparison, S-01 stress test, architecture debates (Critic role, opacity vs transparency, second loop design)
- Current draft: `the_creative_prism_medium_article.docx` in project folder

---

## TRAIT WEIGHT EXPERIMENTS

| Date | Role | Trait | From | To | Mode | Observed Effect |
|---|---|---|---|---|---|---|
| 2026-04-01 | Creator | practicality | 0.40 | 0.65 | Exp 3 | Director raised for practical business problem |
| 2026-04-01 | Critic | critical_strictness | 0.90 | 0.95 | Exp 3 | Director raised to protect against financial risk |
| 2026-04-06 | Creator | intellectual_adventurousness | raised | — | Exp 5 | Director raised for conceptual reframing problem |
| 2026-04-06 | Researcher | citation_rigor | raised | — | Exp 5 | Precise and substantive citations confirmed |

---
---

### [2026-04-14] director.md v1.7 — Structured Presentation Format + Session Record Access

**Status:** COMPLETE — deployed to project folder

**PRESENTATION section rewritten:**
Each direction now follows a five-part labeled format:
- Direction Title (mechanism-conveying, not marketing label)
- The Core Move (2-3 sentences grounded in discovery)
- The Innovation (what the PIL couldn't have arrived at alone)
- What It Asks (honest cost of this direction)
- Research Foundation (always present — substantive findings or reason research not initiated)
- Invitation to Go Deeper (specific named invitation, not vague offer)

Purpose: PIL-facing presentation must reflect the sophistication of the internal work. Previous format (bold nickname + 3 sentences) was systematically underselling the studio's output.

**Session record offer added to TRANSPARENCY ON REQUEST:**
At session close, Director offers the full studio dialogue once, with specific language. Made once only, not repeated.

---

### [2026-04-14] Experimental Runs — v3.1 30-Prompt Set (Sessions 1-2)

**Decision:** All pre-v3.1 sessions archived as development work. Clean experimental run begins from v3.1 with kernel restart discipline.

**Run C-01 — Housing vs Climate Infrastructure (rerun)**
Session: `session_20260414_104431_acecf271.json`
Prompt: Design a decision framework for a city choosing between public housing and climate infrastructure.
Status: COMPLETE

What worked: Brief tighter than S-01 run. Pressure point strong ("What does it mean to create a fair process for an inherently unfair choice?"). Researcher autonomous contribution fired correctly on temporal sequencing even when Creator omitted request. Step 0 fired. Surprise Audit present.

What failed / noted:
1. Assumption checks not numbered — PIL cannot respond by number. Minor UX gap.
2. Critic making sequencing recommendations to Director — role boundary violation. Critic should present trade-offs factually; Director makes all lead/sequence decisions.
3. "Invitation to Go Deeper" not honored — PIL explicitly requested more on the research and ratification protocol. Director acknowledged, extracted as signal, then proceeded directly to final synthesis without delivering what was asked. Trust failure. Missing process step.
4. Presentation format upgrade (v1.7) visibly working.

**Run C-02 — Personal project positioning (added to set)**
Session: `session_20260414_162207_9dc6d309.json`
Prompt: Peter's own career pivot / Creative Prism positioning problem.
Status: COMPLETE

What worked: Brief excellent — pressure point precisely right. Presentation format working. Final synthesis strong and personal — named specific contacts (Michael Bierut, IDEO). Director folded discovery signals into actionable specifics.

What failed / noted:
- Researcher confabulated named citations (Dario Amodei origin story wrong, Tom Brown attribution incorrect). Plausible-sounding specific details that don't hold up. Hallucination risk on named individuals and institutional claims. Noted for future fix — web search tool for Researcher is the proper architectural solution (deferred post-run).
- Surprise Audit limited to HIGH band only — should extend to all three directions. LOW and MID can also be predictable in different ways. Added to v4.0 list.

---

### [2026-04-15] Experimental Runs — v3.2 30-Prompt Set Reset

**Decision:** 30-prompt experimental run reset to C-01. All prior runs (C-01, C-02 on earlier notebook versions) archived as development work. Clean run begins from v3.2 with full Cell 11/11b patches applied and kernel restart discipline.

**Run C-01 — Chicken Parmesan business concept (Claude v3.2)**
Session: `session_20260415_125328_ab70a835.json`
Prompt: Starting a Chicken Parmesan sandwich business named after grandmother Petrina.
Status: COMPLETE

What worked: Pressure point strong. Presentation format visibly improved — Core Move sections developed, Research Foundation self-contained. Three distinct directions. Apprentice/Legacy/Diversified-Revenue framing unique to this run.

What noted:
- Researcher produced suspicious precision statistics (60-80% return rates, 90% retention) — same hallucination pattern as C-02 but as numbers rather than named citations. Web search tool remains the proper fix.

---

### [2026-04-15] Model Comparison — Claude vs OpenAI (Chicken Parm)

**Sessions compared:**
- Claude v3.2: `session_20260415_125328_ab70a835.json`
- OpenAI (gpt-5.4 / gpt-5.4-mini): `session_20260415_103142_4d7a1f1f.json`

**Finding:** Both ran on identical v3.2 prompts. Difference is genuine model cognitive orientation, not prompt gap.

GPT orientation: behavioral/experiential — produced ritual/habit/weekly-favorite framing; sharper brief kernel; more structured action plan with named phases.
Claude orientation: structural/legacy — produced Apprentice/Legacy/Diversified-Revenue framing; deeper brand personality; synthesis with stronger narrative continuity.

Neither found what the other found. Both outputs were high quality. Difference is complementary, not competitive.

**Implication:** Hybrid architecture justified. Cross-model Critic injection designed to use this difference intentionally at the evaluation stage rather than averaging outputs at synthesis.

---

### [2026-04-15] OpenAI Engine — engine_openai.py v1.0

**Status:** COMPLETE — deployed

Built parallel engine for OpenAI (gpt-5.4 / gpt-5.4-mini).
Key differences from engine.py: `max_completion_tokens` replaces `max_tokens`; `developer` role message for system prompt; `prompts_openai/` and `sessions_openai/` directories.
Token adjustments vs Claude version: Discovery +200 (600→800), Director Review JSON +200 (800→1000), Final Synthesis +200 (1400→1600).

---

### [2026-04-15] director.md v1.9 — Presentation Format Expansion

**Status:** COMPLETE

**Core Move:** Expanded to 8-12 sentences. Requires mechanical explanation, operational picture, and human context. Explicitly flagged as the heart of the proposal.

**Research Foundation:** PIL-has-not-seen-the-research rule added. Named cases, cities, studies require one sentence of context: what happened, what it showed, why it applies. "A citation the PIL cannot evaluate" named as the failure condition.

---

### [2026-04-15] Hybrid Architecture — engine_hybrid.py v1.0

**Status:** COMPLETE — deployed

**Core design:** Single unified engine holding both Anthropic and OpenAI clients. `call_role()` dispatches by `provider` parameter. Critic always runs on opposite provider from primary.

**Routing:** Cell 2b classifies orientation on 0.0–1.0 scale (0.0=strategic, 1.0=creative). Thresholds: ≤0.35 → Strategic (Claude primary, GPT critic); ≥0.65 → Creative (GPT primary, Claude critic); 0.36–0.64 → Balanced zone, tiebreaker questions decide. Tiebreaker: three questions about what PIL needs, biggest risk, and nature of the answer. Two-of-three wins.

**Vocabulary:** Creative / Strategic (replaces Expansion / Constraint — maps to how people think about these functions).

**Governed domains:** Explicitly excluded from routing signal — handled by Director prompt regardless of orientation.

**New files:**
- `engine_hybrid.py` v1.0
- `critic_gpt.md` v1.0 — GPT Critic, creative-challenge orientation (distinctiveness, positioning, surprise, behavioral resonance)
- `prompts_hybrid/` — copy of `prompts/` plus `critic_gpt.md`
- `sessions_hybrid/`
- Notebook: `creative_prism_studio_v4_0.ipynb`

**Notebook changes from v3.1:**
- Cell 1: imports from `engine_hybrid`
- Cell 2: provider-aware placeholder constants
- Cell 2b: new routing cell (classifier + tiebreaker + operator confirmation)
- Cell 6 — Critic Pass 1: `provider=CRITIC_PROVIDER, model=CRITIC_MODEL`
- Cell 7c — Critic Pass 2: same change
- All other cells: unchanged

**Status:** COMPLETE

Added explicit instruction: Critic presents trade-offs factually across all directions. It does not rank directions, recommend a lead direction, or advise the Director on sequencing. Those decisions belong entirely to the Director. The Critic's authority ends at evaluation. Sequencing, lead selection, and presentation order are not within the Critic's remit.

---

### [2026-04-14] director.md v1.8 — Numbered Assumptions + Honor Requests Before Proceeding

**Status:** COMPLETE

**Assumption Validation — numbered format:**
Assumptions now presented as a numbered list so PIL can respond by number. Reduces friction in PIL response and makes it explicit which assumptions were addressed.

**Honor requests before proceeding (new requirement):**
If the PIL explicitly requests more information on a direction, research findings, or the rationale behind the evaluation — the Director must deliver that information in the current turn before extracting signals or moving to synthesis. Acknowledging a request and moving on without honoring it is a trust failure and a process violation.

---

## KNOWN ISSUES

| Issue | Severity | Status | Notes |
|---|---|---|---|
| `idea_space` not yet populated | Low | Noted | Schema field exists, Phase 1 doesn't write to it yet |
| Researcher autonomous trigger not wired | Low | Noted | Prompt describes behavior, code doesn't implement trigger |
| Scribe LLM call not implemented | Low | Noted | scribe_log() is mechanical Python |
| Bug 4 (duplicate brief entries) | Low | Diagnosed | Audit update_brief_doc calls in Director Review |
| Director closing question hangs | Low | Noted | Stage 9 asks a question but no Cell 13 collects it — v4.0 scope |
| Forced choice dominance | Low | ADDRESSED v1.6 | Prohibition explicit; planning required |
| Director summary blank | Medium | FIXED v3.1 | Cell 12 now includes call with read_brief_doc(session_id) |
| Stage 8c → 9 gap | High | FIXED v3.1 | Cell 10c now presents to PIL before synthesis |
| Branding gap in startup briefs | Medium | ADDRESSED v1.5 | Functional Domain Inventory catches it |
| Assumption checks not numbered | Low | FIXED v1.8 | Numbered list format in Assumption Validation |
| Critic recommending direction to Director | Medium | FIXED v1.3 | Role boundary enforcement added to critic.md |
| "Invitation to Go Deeper" not honored | High | FIXED v1.8 | Director must deliver requested info before proceeding |
| Researcher hallucination on named citations | Medium | Noted | Web search tool = proper fix; deferred post-run. Also manifests as fabricated precision statistics. |
| Surprise Audit HIGH band only | Low | Noted | Should cover all three bands — v4.0 scope |
| Post-session research document | Low | Noted | format_research_summary() + Cell 12 integration — v4.0 scope |
| Routing classifier accuracy unvalidated | Low | Noted | Will surface errors during 30-prompt hybrid run; thresholds and tiebreakers subject to refinement |

---

## PHASE ROADMAP

```
Phase 1  Early Experiments        Complete
           Socratic Spiral, Prism, HITL, temperature sweeps

Phase 2  Full Studio Workflow     Active — v4.0 current
           Engine v2.1 (Claude) · engine_openai.py v1.0 · engine_hybrid.py v1.0
           Prompts v3.2 — director.md v1.9, critic.md v1.3, critic_gpt.md v1.0
           Notebook v4.0 — Hybrid: Cell 2b routing, cross-model Critic (Cells 6, 7c)
           30-prompt experimental run: reset, C-01 pending on v4.0 hybrid
           Parallel: v3.2 Claude-only run available for comparison

Phase 3  Visualization            Active (parallel track)
           Galaxy/flower (Sketch 21) — frozen
           Membrane landscape (Sketch 22) — Step 1 locked, Step 2 next
           Eye motif — prototype build pending
           Replay instrument MVP for creativeprism.ai
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
| Medium Article Draft | — | `the_creative_prism_medium_article.docx` |

---

*"The prism does not replace the thinker. It expands the range of thinking available to them."*
— System Constitution V2.2
