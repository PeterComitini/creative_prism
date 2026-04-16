# ── CELL 2b — MODEL ROUTING ───────────────────────────────────────────────────
# Captures the initial prompt, classifies orientation and PIL profile,
# sets model constants, and pushes PRIMARY_PROVIDER and CRITIC_PROVIDER
# into engine_hybrid so all subsequent call_role() calls use the correct
# provider automatically.

print("═" * 60)
print("MODEL ROUTING")
print("═" * 60)

# ── Capture initial prompt — used by routing AND passed to Cell 3 ─────────────
initial_prompt = input(
    "Welcome to The Creative Prism. What would you like to explore today?\n> "
).strip()

if not initial_prompt:
    print("⚠ No prompt entered. Defaulting to Claude primary (strategic).")
    _routing = {
        "orientation":          "strategic",
        "orientation_score":    0.5,
        "primary_provider":     "anthropic",
        "critic_provider":      "openai",
        "director_model":       ANTHROPIC_DIRECTOR,
        "session_model":        ANTHROPIC_DEFAULT,
        "critic_model":         OPENAI_DEFAULT,
        "tiebreaker_used":      False,
        "tiebreaker_answers":   [],
        "rationale":            "No prompt provided — defaulted to strategic.",
        "pil_read":             "",
        "domain_fluency":       "",
        "cognitive_style":      "",
        "relational_proximity": "",
    }
else:
    print("\n  Classifying...")
    _routing = route_session(initial_prompt)

# ── Set model constants ───────────────────────────────────────────────────────
DIRECTOR_MODEL      = _routing["director_model"]       # Sonnet — PIL-facing
DIRECTOR_FAST_MODEL = ANTHROPIC_DEFAULT                # Haiku  — internal/admin
SESSION_MODEL       = _routing["session_model"]
CRITIC_MODEL        = _routing["critic_model"]
PRIMARY_PROVIDER    = _routing["primary_provider"]
CRITIC_PROVIDER     = _routing["critic_provider"]

# ── Push provider state into engine_hybrid ───────────────────────────────────
engine_hybrid.PRIMARY_PROVIDER = PRIMARY_PROVIDER
engine_hybrid.CRITIC_PROVIDER  = CRITIC_PROVIDER

# ── Print routing decision ────────────────────────────────────────────────────
print()
print(f"  Orientation    : {_routing['orientation'].upper()}  "
      f"(score: {_routing['orientation_score']:.2f})")
print(f"  Rationale      : {_routing['rationale']}")
print()
print(f"  PIL read       : {_routing.get('pil_read', '')}")
print(f"  Domain fluency : {_routing.get('domain_fluency', '')}")
print(f"  Cognitive style: {_routing.get('cognitive_style', '')}")
print(f"  Relational     : {_routing.get('relational_proximity', '')}")
if _routing["tiebreaker_used"]:
    print(f"\n  Tiebreaker     : used")
    for a in _routing["tiebreaker_answers"]:
        print(f"    {a}")
print()
print(f"  Director model : {DIRECTOR_MODEL}  (Sonnet — PIL-facing)")
print(f"  Fast model     : {DIRECTOR_FAST_MODEL}  (Haiku — internal)")
print(f"  Team model     : {SESSION_MODEL}  [{PRIMARY_PROVIDER}]")
print(f"  Critic model   : {CRITIC_MODEL}  [{CRITIC_PROVIDER}]")
print()
print("  To override: manually set model constants then re-run.")
print("═" * 60)
print()
print("✓ Routing complete — proceed to Cell 3")
