"""
GSAC Socratic Human-in-the-Loop Engine
--------------------------------------

Environment-locked version.
Validated against local model list.

Uses:
    models/gemini-2.5-flash
    models/gemini-2.5-pro
"""

import os
import json
import copy
import time
from datetime import datetime

from dotenv import load_dotenv
from google import genai


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

    # --------------------------------------------------------
    # MULTILINE INPUT HELPER
    # --------------------------------------------------------

    def multiline_input(self, prompt):

        print(prompt)
        print("(Press ENTER on a blank line to submit)\n")

        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)

        return "\n".join(lines)

    # --------------------------------------------------------
    # Safe model call
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Main experiment loop
    # --------------------------------------------------------

    def run_experiment(self, text, temperature=0.0):

        print("\n" + "="*80)
        print(f"INITIATING EXPERIMENT 2.3 | TEMPERATURE: {temperature}")
        print("="*80 + "\n")

        # ----------------------------------------------------
        # PHASE G-S : STRUCTURAL PRISIM
        # ----------------------------------------------------

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

        user_reaction_1 = self.multiline_input(
            "\n[YOUR CALL] Respond to the prisim:"
        )

        # ----------------------------------------------------
        # PHASE A : ADVERSARIAL REFLECTION
        # ----------------------------------------------------

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

        user_reaction_2 = self.multiline_input(
            "\n[YOUR CALL] Respond to the adversarial critique:"
        )

        # ----------------------------------------------------
        # PHASE C : FINAL SYNTHESIS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # REASONING SUMMARY
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

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