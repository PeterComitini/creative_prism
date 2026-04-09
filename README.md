# The Creative Prism 
### A Human-Centered AI Creative Studio

---

## What This Is

The Creative Prism is a research project exploring whether structured
multi-agent AI reasoning can function as a cognitive prisim — a tool that makes
the process of human thinking visible, navigable, and more generative.

The system is not a chatbot. It is a collaborative studio in which multiple AI
roles work together to help a person explore a problem, generate ideas, evaluate
alternatives, and arrive at a genuinely considered outcome. The person in the loop
remains the final authority at every stage.

---

## The Creative Prisim

The current phase of the project is **The Creative Prism** — a five-role AI studio
that runs a nine-stage creative reasoning workflow.

**Five studio roles:**
- **Director** — the sole voice with the person in the loop. Governs the process, synthesizes work, maintains continuity across the session.
- **Creator** — generative ideation using Verbalized Sampling to push toward lateral thinking.
- **Critic** — rigorous evaluation and synthesis. Strengthens ideas rather than filtering them.
- **Researcher** — contextual knowledge and adjacent-domain enrichment. Acts after the creative team, informed by what they produced.
- **Scribe** — reads the complete session record and produces a structured interpretation for visualization.

**Nine-stage workflow:**
```
Discovery → Reframing → Creative Brief → Ideation → Critique →
Research Enrichment → Director Review → Presentation → Final Synthesis
```

**Shared memory:**
Every role reads the Studio Brief Document — a living markdown file that
accumulates the complete session record. The Director has genuine continuity.
The Creator reads the research context. The Critic evaluates against the actual
brief. The Researcher responds to what the team produced, not just the brief in isolation.

---

## Intellectual Foundation

The Creative Prism is grounded in a specific intellectual lineage:

- **Bohm** — *Thought as a System* — proprioception of thought as the philosophical foundation
- **Dowd** — *Taking Root to Fly* — somatic proprioception as the origin of the insight
- **IDEO / d.school** — Human-Centered Design methodology, sacrificial concepts, discovery frameworks
- **Shneiderman** — HCAI framework: amplify, augment, empower, enhance as the standard of success
- **Verbalized Sampling** (arXiv 2510.01171) — validates the ideation diversity approach
- **VECTOR** (arXiv 2509.14455) — validates the semantic trajectory visualization approach
- **Cognitive-Affective Maps** (Thagard/Reuter) — visualization theory with affective valence
- **Socratic Dialogue** (MSP Tool 49) — structural predecessor

The through-line: Dowd showed that awareness of bodily movement patterns creates the
possibility of changing them. Bohm applied the same logic to thought itself. The
Creative Prism applies it to AI-assisted creative reasoning — making the trajectory
of thinking visible so it can be examined, extended, and redirected.

---

## Repository Structure

```
the_intelligence_of_seeing/
  README.md                        ← this file
  CLAUDE.md                        ← repo-level AI context
  .gitignore
  archive/
    gasc_experiment/               ← G-S-A-C predecessor work + LOGBOOK
    phase1_v1_experiment/          ← first Creative Prisim experiment + NOTES
  creative_prisim/
    engine.py                      ← core engine: Blackboard, roles, API, session persistence
    creative_prisim_phase0.ipynb   ← verification notebook
    creative_prisim_phase1.ipynb   ← full nine-stage workflow
    LOGBOOK.md                     ← experiment record
    CLAUDE.md                      ← standing brief for AI sessions
    schema/
      studio_run_schema_v2_2.json  ← Blackboard data model
    sessions/                      ← session JSONs (gitignored, local only)
```

**What is not in this repository:**
- Role prompts (`prompts/`) — core IP, not yet public
- Governance documents (`governance/`) — system constitution, operating protocol, etc.
- Research resources (`_resources/`) — papers and reference materials
- Session data (`sessions/`) — experimental outputs, curated separately

---

## Predecessor Work

The G-S-A-C pipeline (Generator, Structurer, Adversary, Compressor) is preserved
in `archive/gasc_experiment/` with its original LOGBOOK, schema, and experiment
notebooks. That work established the core insight: structured multi-role AI dialogue
produces richer reasoning than single-model interaction. The Creative Prisim is its successor.

---

## Phase Roadmap

```
Phase 0  Foundation Scaffold          ✅ Complete
Phase 1  Full Studio Workflow         ✅ v1.2 — Studio Brief Document, corrected role sequence
Phase 2  Refinement & Memory          🔧 Next
Phase 3  Visualization                📋 Planned — VECTOR-style semantic trajectory map
```

---

## Status

Active research and development. Not yet ready for external use.
The system is being tested and refined through structured experiments
documented in `creative_prisim/LOGBOOK.md`.

---

*"The prism does not replace the thinker. It expands the range of thinking available to them."*
— The Creative Prism, System Constitution V2.2
