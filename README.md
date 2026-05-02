# The Creative Prism
### A Human-Centered AI Creative Studio

---

## What This Is

The Creative Prism is a research project exploring whether structured
multi-agent AI reasoning can function as a cognitive prism — a tool that makes
the process of human thinking visible, navigable, and more generative.

The system is not a chatbot. It is a collaborative studio in which multiple AI
roles work together to help a person explore a problem, generate ideas, evaluate
alternatives, and arrive at a genuinely considered outcome. The person in the
loop remains the final authority at every stage.

The work succeeds when the person is surprised — not confused, not alienated.
When they recognize something they didn't know they needed until they saw it.
That gap between what they brought in and what they leave with is the measure
of the studio's value.

---

## The Studio

The current system is **The Creative Prism v4.0** — a five-role AI studio
running a nine-stage creative reasoning workflow on a hybrid multi-provider
architecture (Anthropic + OpenAI).

**Five studio roles:**

- **Director** — the sole voice the person hears. Governs the process, synthesizes
  the team's work, maintains continuity across the session. Runs on Sonnet for
  all PIL-facing calls.
- **Creator** — generative ideation using Verbalized Sampling to push toward
  genuinely lateral thinking. Step 0 names the convergent mode before moving
  away from it.
- **Critic** — rigorous evaluation using a Surprise Audit across all three
  directions. Always runs on the opposite provider from the Creator (cross-model
  cognitive contrast is intentional architecture).
- **Researcher** — contextual knowledge and adjacent-domain enrichment. Acts
  after the creative team, informed by what they produced. Uses a three-tier
  epistemic system (CITED FINDING / PATTERN / EPISTEMIC FLAG) to prevent
  fabrication.
- **Scribe** — reads the complete session record and produces a structured
  interpretation for downstream visualization.

**Nine-stage workflow:**
```
Stage 0  Director reads PIL language (domain fluency, cognitive style, relational proximity)
Stage 1  Discovery — Director deploys extraction toolkit; Specialist Personas (v5.0)
Stage 2  Reframing — Director frames the real problem
Stage 3  Creative Brief — JSON brief with pressure point and assumption validation
Stage 4  Ideation — Creator (Pass 1 + Pass 2) and Critic (Pass 1 + Pass 2, cross-model)
Stage 5  Research Enrichment — Researcher responds to what the team produced
Stage 6  Director Review — quality gate; second loop triggers if needed
Stage 7  Focused Refinement — conditional Creator pass targeting identified gap
Stage 8  Presentation — five-part format per direction (Core Move, Innovation,
         What It Asks, Research Foundation, Invitation to Go Deeper)
Stage 9  Final Synthesis — commitment protocol; Director selects strongest direction
         and defends it before writing
```

**Shared memory:**
Every role reads the Studio Brief Document — a living markdown file that
accumulates the complete session record (capped at 12,000 characters).
The Director has genuine continuity. The Creator reads the research context.
The Critic evaluates against the actual brief. The Researcher responds to
what the team produced, not just the prompt in isolation.

**Routing:**
A Sonnet-based routing classifier reads the initial prompt and assigns an
orientation score (0.0 = strategic, 1.0 = creative). This determines which
provider runs the primary creative roles and which runs the Critic. The
cross-provider Critic pairing is the key architectural choice: Claude and
GPT have genuinely different cognitive orientations (Claude: structural/legacy;
GPT: behavioral/experiential). Neither finds what the other finds. The
difference is complementary, not competitive.

---

## Intellectual Foundation

| Source | Relevance |
|---|---|
| Bohm — *Thought as a System* | Proprioception of thought — philosophical foundation |
| Dowd — *Taking Root to Fly* | Somatic proprioception — origin of the core insight |
| IDEO / d.school HCD | Discovery methodology, sacrificial concepts |
| Shneiderman — HCAI Framework | Amplify / augment / empower / enhance |
| Verbalized Sampling (arXiv 2510.01171) | Validates the ideation diversity approach |
| VECTOR (arXiv 2509.14455) | Validates the semantic trajectory visualization approach |
| Cognitive-Affective Maps (Thagard/Reuter) | Visualization theory with affective valence |
| Socratic Dialogue (MSP Tool 49) | Structural predecessor |
| Albers / Abstract Expressionists / Duchamp / LeWitt | Modernist lineage: medium as subject |

The through-line: Dowd showed that awareness of bodily movement patterns creates
the possibility of changing them. Bohm applied the same logic to thought itself.
The Creative Prism applies it to AI-assisted creative reasoning — making the
trajectory of thinking visible so it can be examined, extended, and redirected.

---

## Repository Structure

```
creative_prism/
  README.md                          ← this file
  CLAUDE.md                          ← repo-level AI context and standing brief
  LOGBOOK.md                         ← full experiment record, architecture decisions
  .gitignore
  engine_hybrid.py                   ← active engine: Anthropic + OpenAI, routing,
  persona_traits_matrix_v2.csv       ←   58-trait personality system (five-band language)
  prism_evaluator_v2.py              ← evaluator: Gemini 1.5 Pro + GPT-4o dual scoring
  creative_prism_studio_v4_0.ipynb   ← active notebook: nine-stage hybrid workflow

  phase_2_experiments/               ← active lab (see phase_2_experiments/README.md)
    engine_hybrid.py                 ← symlinked / mirrored from root
    persona_traits_matrix_v2.csv
    prompts_hybrid/                  ← active prompt set (director, creator, critic,
                                         critic_gpt, researcher, scribe)
    sessions_hybrid/                 ← session JSONs (gitignored, local only)
    governance/                      ← system constitution, operating protocol (gitignored)
    archived_py/                     ← prior engine versions and notebook iterations
```

**What is not in this repository:**
- `prompts_hybrid/` — core IP, not yet public
- `governance/` — system constitution, operating protocol, director evaluation protocol
- `sessions_*/` — experimental outputs, curated separately
- `phase_3_visualization/` — large visualization files, gitignored

---

## Predecessor Work

The G-S-A-C pipeline (Generator, Structurer, Adversary, Compressor) is preserved
in `phase_1_experiments/` with its original LOGBOOK, schema, and experiment
notebooks. That work established the core insight: structured multi-role AI
dialogue produces richer reasoning than single-model interaction.

The first full nine-stage Creative Prism workflow is preserved in
`phase_2_experiments/phase_2_archive/`. The active system is v4.0.

---

## Phase Roadmap

```
Phase 1  Early Experiments           ✅ Complete
           Socratic Spiral, Prism predecessor, HITL, temperature sweeps

Phase 2  Full Studio Workflow        🔧 Active — v4.0 Hybrid current
           Hybrid engine, cross-model Critic, 30-prompt experimental run
           v5.0 design sprint complete; Layer 2/3 build pending test data

Phase 3  Visualization               🔧 Active (parallel track)
           Semantic trajectory map; Three.js membrane; SVG eye motif
           Replay instrument MVP for creativeprism.ai
```

---

## Status

Active research and development. Not yet ready for external use.
Experiments are documented in `LOGBOOK.md`. Architecture decisions are settled
and reasoned — see the ARCHITECTURE DECISIONS LOG in the logbook.

---

*"The prism does not replace the thinker. It expands the range of thinking available to them."*
— The Creative Prism, System Constitution V2.2
