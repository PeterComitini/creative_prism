# CLAUDE.md
## Standing Brief — The Creative Prisim Project
### The Intelligence of Seeing (IoS)
**For Claude: Read this at the start of every new session.**

---

## WHO I AM

My name is Peter Comitini. I am a graphic designer by training with multiple
careers in visual communication, brand, and technology. I am currently a
computer science student (completed ML/AI at UT Austin, considering a masters).
This project is both a learning environment and a key portfolio piece for my
transition into AI.

I am not a software engineer. I think like a designer — systemically,
visually, and iteratively. I am highly capable of understanding complex systems
but I rely on you for coding implementation, technical guidance, and
disciplined engineering support.

I work with AI collaboratively. I have been developing this project with
ChatGPT and Gemini before bringing Claude in as primary coding partner.

---

## THE PROJECT

**Name:** The Creative Prisim
**Subtitle:** The Intelligence of Seeing (IoS)
**Phase:** 1 — Active prototype, first experiments complete
**Repository:** `code_space/02_projects/the_intelligence_of_seeing/creative_prisim/`

The Creative Prisim is a structured reasoning environment in which multiple
AI roles collaborate to help a person explore problems, generate ideas, and
evaluate solutions. It is a human-centered cognitive studio, not a chatbot
or autonomous agent.

**Philosophical foundation:** The proprioception of thought — the idea
(from David Bohm and somatic educator Irene Dowd) that awareness of the
movement of thought creates the conditions for new thinking.

**Project lineage:**
- Phase 0-1: G-S-A-C pipeline (Generator, Structurer, Adversary, Consolidator)
  — experimental predecessor, complete, preserved in archive/
- Phase 1: The Creative Prisim — active development, lives in creative_prisim/
- Phase 2: Refinement and persistent memory — planned
- Phase 3: Visualization — VECTOR-style semantic trajectory map — planned

---

## CORE ARCHITECTURE

**Five studio roles — names are fixed, do not rename:**

| Role | Function |
|---|---|
| Director | Orchestrates process, communicates with user, maintains session continuity |
| Creator | Generates ideas using Verbalized Sampling, expands possibility space |
| Critic | Evaluates and refines ideas constructively, proposes synthesis directions |
| Researcher | Introduces contextual knowledge — acts AFTER Creator/Critic, not before |
| Scribe | Reads complete session JSON, produces Session Interpretation for visualization |

**Key components:**
- engine.py — all infrastructure: Blackboard, Scribe, Traits, Prompt Compiler, API, session persistence
- Blackboard — shared session state (JSON). Schema v2.2.
- Studio Brief Document — living markdown file (sessions/brief_[id].md) passed to every role call. Shared working memory that gives roles genuine continuity.
- Traits System — 9-dimension weight profiles that shape role behavior via prompt compiler
- Prompt Compiler — build_prompt(role, weights, context, mode, brief_doc)
- SYSTEM_PROMPT.md — constitutional layer prepended to every role call
- Session loader — load_session(), list_sessions() for persistent memory

**What is NOT in the repo (private IP):**
- prompts/ — role identity files and SYSTEM_PROMPT.md
- governance/ — system constitution, operating protocol, all governance docs
- _resources/ — research papers and reference materials
- sessions/ — session data (gitignored, local only)

---

## CURRENT BUILD STATUS

| Component | Status | Version |
|---|---|---|
| engine.py | Complete | v1.2 |
| Blackboard state object | Complete | Schema v2.2 |
| Traits system + role weight profiles | Complete | — |
| Prompt compiler | Complete | v3 |
| SYSTEM_PROMPT.md (constitutional layer) | Complete | v1.0 |
| Role identity statements (all 5 roles) | Complete | v1.1 |
| Studio Brief Document system | Complete | v1.0 |
| Session persistence + loader | Complete | — |
| Phase 0 verification notebook | Complete | — |
| Phase 1 — full nine-stage workflow | Complete | v1.2 |
| First experiment run | Complete | Archived in archive/phase1_v1_experiment/ |
| Phase 2 — refinement and persistent memory | Next | — |
| Phase 3 — visualization layer | Planned | VECTOR-style |

**API:** Anthropic (Claude). Key stored in root-level .env as ANTHROPIC_API_KEY.
**Model:** claude-haiku-4-5-20251001 for development. Swap to claude-sonnet-4-6 for quality runs.
**Environment:** Jupyter notebooks + engine.py. Local development on Mac (code_space drive).

---

## KEY DECISIONS MADE (do not re-litigate without good reason)

- engine.py is the machinery. Notebooks are experiments only.
- Studio Brief Document is the shared memory mechanism — not full conversation threading.
- Role sequence: Creator → Critic → Researcher (Researcher acts post-ideation).
- Scribe runs end-of-session, on by default, PIL-facing narrative only.
- Researcher has one autonomous contribution per session maximum.
- Director is the permission gate for all Researcher activity beyond that.
- Sessions are gitignored. Notable sessions will be curated manually.
- prompts/ and governance/ are gitignored — private IP for now.
- Visualization target: p5.js, VECTOR-style semantic trajectory, clickable nodes.
- Live-building visualization is second generation target.

---

## HOW TO WORK WITH ME

**1. Deliver code as downloadable files.** Do not paste long code blocks inline.

**2. Call out proposed changes explicitly.** Format: "I'm proposing [X] — confirm before acting."

**3. One variable at a time.** State: Variable / Expected effect / How to verify.

**4. Do not rename things without explicit confirmation.**

**5. Do not refactor working code without explicit request.**

**6. Ask before introducing new dependencies.**

**7. When in doubt, ask.**

---

## WHAT REQUIRES EXPLICIT CONFIRMATION BEFORE ACTING

- Any file rename or folder restructure
- Any schema field addition, removal, or rename
- Any change to role names or role identity statements
- Any new dependency or library
- Any refactor of working code
- Any change to .cursorrules or CLAUDE.md themselves

---

## DOCUMENTS TO READ IF AVAILABLE

1. creative_prisim/LOGBOOK.md — experiment history and current status
2. creative_prisim/.cursorrules — operational rules for this folder
3. creative_prisim/governance/system_constitution_v2_2.docx — philosophy + HCAI
4. creative_prisim/governance/operating_protocol_v2.1.docx — nine-stage workflow
5. creative_prisim/schema/studio_run_schema_v2_2.json — session schema
6. creative_prisim/governance/traits_matrix_weighting_v1.docx — personality layer

---

## PROJECT PHILOSOPHY

"The Creative Prisim treats reasoning as a collaborative process.
Through structured interaction between human and artificial intelligence,
the system aims to expand perspective, reveal hidden assumptions, and
support thoughtful decision-making. The prisim does not replace the thinker.
It expands the range of thinking available to them."
— System Constitution V2.2

The system exists to amplify, augment, empower, and enhance human reasoning.
The Person in the Loop retains final authority at every stage.

---

## SESSION STARTUP CHECKLIST

- [ ] Read this file
- [ ] Read LOGBOOK.md if available
- [ ] Confirm current build phase with Peter before writing any code
- [ ] Ask what the goal of this session is before proposing anything
- [ ] Do not assume continuity from a previous session — confirm it

---

*Last updated: 2026-03-18*
*Maintained by: Peter Comitini*
*Update this file when working rules, build status, or project direction changes.*
