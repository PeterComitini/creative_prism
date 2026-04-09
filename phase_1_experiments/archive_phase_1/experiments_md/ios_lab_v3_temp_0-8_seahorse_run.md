# Project: The Intelligence of Seeing (IoS)
## Experimental Series | Baseline and Human-in-the-Loop Variants

---

## Overview

The Intelligence of Seeing (IoS) is an experimental investigation into structured reasoning as a design instrument.

The project treats large language models not as answer engines, but as **cognitive prisims** — systems that can expose structure, surface assumptions, and apply bounded adversarial pressure to an idea.

The central question:

> What happens to an idea when it is forced through staged structural friction?

This repository documents an evolving series of experiments exploring that question.

---

## Core Topology: G–S–A–C

All IoS experiments are built around a shared reasoning structure:

**G–S → A → C**

| Phase | Function |
|------|----------|
| **G–S (Generator–Structurer)** | Distills the seed idea into structural components and exposes central tension. |
| **A (Adversary)** | Identifies unsupported assumptions and destabilizing causal gaps. |
| **C (Consolidation)** | Reconstructs the idea into a clarified, stabilized topology. |

This topology remains constant across experiments.  
What changes is the degree of human intervention and generative variance.

---

## Phase 0 — Baseline Engine

The Baseline Engine executes the full G–S–A–C cycle autonomously.

Characteristics:

• No human intervention between phases  
• Temperature parameterization in the G–S phase  
• Deterministic stabilization in the C phase  
• Structured JSON logging (`schema_v2.json`)  
• Gemini 2.5 Flash (G–S and C phases)  
• Gemini 2.5 Pro (Adversary phase)

This configuration serves as the control condition.

It reveals how the reasoning architecture behaves when left entirely to the model.

---

## Phase 1 — Human-in-the-Loop (HITL) Variant

The HITL Engine preserves the same G–S–A–C topology but inserts deliberate human gates between phases.

Characteristics:

• Explicit pause after the Prisim phase for human steering  
• Explicit pause after the Adversary phase for human evaluation  
• Temperature-controlled generative variance  
• Retry safeguards for API stability  
• Structured JSON logging (`schema_v2.json`)  
• Gemini 2.5 Flash (Prisim and Synthesis)  
• Gemini 2.5 Pro (Adversary)

The system is no longer autonomous.

The human becomes an active stabilizing force within the reasoning cycle.

This phase explores what the project calls the **Intuition Delta**:

> How does structured reasoning evolve when human judgment shapes intermediate states?

---

## Experimental Variable: Generative Variance

Temperature is parameterized during execution to explore variation in generative behavior.

Temperature sweep used in this experiment:

• 0.0  
• 0.3  
• 0.6  
• 0.8  

Each run records:

• model identifiers  
• timestamp  
• temperature value  
• raw outputs for each reasoning phase  
• human responses inserted between phases  

Outputs are stored as structured JSON artifacts.

These artifacts allow later comparison of reasoning cycles under different generative conditions.

---

## Observations from Initial HITL Temperature Sweep

The first full HITL experiment produced a stable reasoning cycle across all temperature conditions.

Key observations:

• The Prisim phase consistently extracted the same structural conflict from the narrative seed.  
• The Adversary phase reliably surfaced implicit assumptions and systemic tensions.  
• The Synthesis phase reconstructed coherent decision frameworks integrating model reasoning and human input.

However, temperature variation produced **minimal conceptual divergence**.

Even at higher temperatures, the system consistently interpreted the scenario through a structured analytical lens.

Narrative absurdities embedded in the seed text were largely ignored, and the system reframed the problem as a system optimization challenge.

This suggests that **temperature alone does not alter the reasoning mode of the model**.

Future experiments will therefore explore modifications to the Prisim prompt that introduce alternative interpretive frames capable of generating greater conceptual diversity.

---

## Design Position

IoS is not a production framework.

It is an evolving experimental instrument.

The objective is not to demonstrate engineering maturity, but to investigate:

• structural clarity under constraint  
• bounded adversarial pressure  
• the role of human intuition in generative systems  
• the design of reasoning as architecture  

The output of the system is not “the answer.”

It is a stabilized topology shaped through staged friction.


```python
"""
GSAC Socratic Human-in-the-Loop Engine
--------------------------------------

Environment-locked version.
Validated against local model list.

Uses:
    models/gemini-2.5-flash
    models/gemini-2.5-pro
"""

# ============================================================
# IMPORTS
# ============================================================

import os
import json
import copy
from datetime import datetime
from google import genai
from dotenv import load_dotenv
```


```python
class GSAC_Socratic_HITL:

    def __init__(self, schema_path="schema_v2.json"):

        load_dotenv(override=True)

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found.")

        self.client = genai.Client(api_key=api_key)

        self.fast_model = "models/gemini-2.5-flash"
        self.logic_model = "models/gemini-2.5-pro"

        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"❌ Cannot find {schema_path}.")

        with open(schema_path, "r") as f:
            self.blank_template = json.load(f)

        print("✅ SOCRATIC HITL ENGINE ONLINE:")
        print("   G/C Model:", self.fast_model)
        print("   A Model:", self.logic_model)

    def safe_generate(self, model, prompt, config=None, retries=5):

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )

                return response.text

            except Exception as e:

                print(f"⚠️ Attempt {attempt+1} failed: {type(e).__name__}: {e}")
                time.sleep(2)

        raise Exception("❌ Model failed after retries.")

    def run_experiment(self, text, temperature=0.0):

        print("\n" + "="*80)
        print(f"INITIATING EXPERIMENT 2.3 | TEMPERATURE: {temperature}")
        print("="*80 + "\n")

        gs_prompt = f"""ROLE & TONE:
Act as a collegial and sharp thought partner.
Be precise. No flattery.

TASK:

Here's what I see:
Distill the core structural conflict into one sentence.

Tell me this:
Ask two short questions:
1) An interpretive fork between two readings
2) A concrete risk or trade-off

USER TEXT:
{text}
"""

        structure = self.safe_generate(
            model=self.fast_model,
            prompt=gs_prompt,
            config={"temperature": temperature}
        )

        print("\n--- PHASE G-S : STRUCTURAL PRISIM ---\n")
        print(structure)

        user_reaction_1 = input("\n[YOUR CALL] Respond (or Enter to skip): ")

        a_prompt = (
            f"Seed: {text}\n"
            f"Prisim Output: {structure}\n"
            f"User Reflection: {user_reaction_1}\n\n"
            "Identify the single most destabilizing assumption.\n\n"
            "Use exactly these headings:\n"
            "Structural Tension:\n"
            "Thought Partner’s Challenge:"
        )

        critique = self.safe_generate(
            model=self.logic_model,
            prompt=a_prompt
        )

        print("\n--- PHASE A : ADVERSARIAL REFLECTION ---\n")
        print(critique)

        user_reaction_2 = input("\n[YOUR CALL] Respond (or Enter to skip): ")

        c_prompt = (
            f"Original Idea: {text}\n"
            f"User Steering: {user_reaction_1}\n"
            f"Risk Reflection: {user_reaction_2}\n\n"
            "Produce a stabilized synthesis with exactly these sections:\n\n"
            "Central Claim\n"
            "Structural Dependencies\n"
            "Accepted Risk\n\n"
            "Do not reuse prior headers.\n"
            "Do not include 'Here's what I see' or 'Tell me this'."
        )

        final = self.safe_generate(
            model=self.fast_model,
            prompt=c_prompt
        )

        print("\n" + "="*50)
        print("Final Observation")
        print("="*50 + "\n")
        print(final)

        summary_prompt = (
            f"Original Idea:\n{text}\n\n"
            f"G-S Output:\n{structure}\n\n"
            f"A Output:\n{critique}\n\n"
            f"Final Synthesis:\n{final}\n\n"
            "In 3-4 sentences explain how the idea evolved across the phases."
        )

        reasoning_summary = self.safe_generate(
            model=self.fast_model,
            prompt=summary_prompt
        )

        print("\n--- Reasoning Summary ---\n")
        print(reasoning_summary)

        record = copy.deepcopy(self.blank_template)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        record["run_metadata"]["experiment_id"] = "Exp2.3_Socratic_HITL"
        record["run_metadata"]["timestamp"] = timestamp
        record["run_metadata"]["models"]["G"] = self.fast_model
        record["run_metadata"]["models"]["A"] = self.logic_model
        record["run_metadata"]["parameters"]["temperature"] = temperature

        record["input"]["raw_text"] = text

        if user_reaction_1 or user_reaction_2:
            record["input"]["human_intervention"]["present"] = True
            record["input"]["human_intervention"]["phase"] = "GS_and_A"
            record["input"]["human_intervention"]["description"] = (
                f"Gate1: {user_reaction_1} | Gate2: {user_reaction_2}"
            )

        record["gs_phase"]["generator_output"] = structure
        record["adversarial_phase"]["notes"] = critique
        record["compression_phase"]["stabilized_claim"] = final

        record["process_notes"] = reasoning_summary

        filename = f"library_socratic_hitL_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(record, f, indent=2)

        print(f"\n📁 LOG SAVED: {filename}")

        return final


engine = GSAC_Socratic_HITL()


print("\nENTER SEED PARAGRAPH FOR EXPERIMENT\n")
seed_text = input("Seed: ")

if not seed_text.strip():
    raise ValueError("❌ Seed text cannot be empty.")


temperatures = [0.0, 0.3, 0.6, 0.8]

total_runs = len(temperatures)

for run_index, temp in enumerate(temperatures, start=1):

    print("\n" + "="*80)
    print(f"RUN {run_index} / {total_runs}")
    print(f"TEMPERATURE: {temp}")
    print("="*80 + "\n")

    engine.run_experiment(
        text=seed_text,
        temperature=temp
    )
```
