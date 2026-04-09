```python
# ==========================================
# PROJECT: THE INTELLIGENCE OF SEEING (v1.3.2)
# SUBTITLE: Direct-Library Nitro Prototype
# ==========================================

# 1. INSTALL
!pip install -q -U google-generativeai

import google.generativeai as genai
import json
import os
from google.colab import userdata

# 2. CONFIG
API_KEY = userdata.get('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

# List available models and select a suitable flash model
valid_model_name = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
        valid_model_name = m.name
        break

if valid_model_name:
    print(f"Using model: {valid_model_name}")
    model = genai.GenerativeModel(valid_model_name)
else:
    raise ValueError("No suitable Gemini Flash model found with generateContent capability.")

def run_direct_nitro(user_input, workspace="Studio"):
    print(f"--- [DIRECT NITRO START: {workspace.upper()} MODE] ---")

    # STEP 1: MODERATOR TRIAGE (The Atmospheric Specs)
    mod_prompt = f"""ROLE: Moderator. Workspace: {workspace}.
    Analyze the prompt and output a JSON block to set the 'Physics' of the run.
    JSON SCHEMA: {{"temp": 0.9, "rigor": 0.8, "sparks": 3, "vibe": "architectural poetry"}}"""

    triage = model.generate_content(mod_prompt + "\nUser Input: " + user_input)
    # Basic cleaning to ensure JSON loads even if LLM adds markdown backticks
    clean_json = triage.text.replace('```json', '').replace('```', '').strip()
    v = json.loads(clean_json)
    print(f"Physics Set: {v}")

    # STEP 2: VERBALIZED SAMPLING (Diving into Latent Space)
    vs_prompt = f"ROLE: Advocate. Verbalize {v.get('sparks', 3)} radical, non-typical approaches. Dig into the 'unlikely' latent space."
    sparks = model.generate_content(vs_prompt + "\nUser Input: " + user_input)

    # STEP 3: THE SOCRATIC FRICTION
    adv_prompt = f"ROLE: Advocate. Vibe: {v.get('vibe')}. Ground this in one CONCRETE POETIC PARTICULAR EXAMPLE (Tool 49)."
    skp_prompt = f"ROLE: Skeptic. Rigor: {v.get('rigor')}. Find the 'typical' AI fluff and dismantle it."

    adv_res = model.generate_content(adv_prompt + "\nSpark: " + sparks.text)
    skp_res = model.generate_content(skp_prompt + "\nAdvocate Output: " + adv_res.text)

    # STEP 4: FINAL REVELATION
    pres_prompt = "ROLE: Presenter. Synthesize into: 1. Visual Anchor, 2. The Discovery, 3. Business Moat, 4. Teacher Note."
    final = model.generate_content(pres_prompt + f"\nSparks: {sparks.text}\nAudit: {skp_res.text}")

    print("\n--- [REVELATION: THE INTELLIGENCE OF SEEING] ---")
    print(final.text)

# ==========================================
# GROUND TRUTH STRESS TEST: MIDTOWN 1970s
# ==========================================

real_world_prompt = """
STRATEGY REQ: Adaptive reuse of a 1970s Midtown office floor plate.
SITE SPECS: 150' x 150' footprint, massive core-to-window depth (60'+).
GOAL: High-end residential 'lofts' without 'bowling alley' layouts.

CONSTRAINTS:
1. Solve for natural light in the deep interior (60'+ from windows).
2. NO traditional light wells or structural voids (preserving Floor Area).
3. Must satisfy NYC DOB Habitability (Section 1205) for natural light/air.
4. Aesthetic: Must appeal to Soho-style loft buyers (raw, open, high-end).
"""

# EXECUTE WITH WAR ROOM RIGOR
run_direct_nitro(real_world_prompt, workspace="War Room")
```

    Using model: models/gemini-2.5-flash
    --- [DIRECT NITRO START: STUDIO MODE] ---
    Physics Set: {'temp': 0.9, 'rigor': 0.8, 'sparks': 3, 'vibe': 'architectural poetry'}
    
    --- [REVELATION: THE INTELLIGENCE OF SEEING] ---
    Alright, let's illuminate this future. As your Presenter, I'm here to distill these audacious concepts into tangible insights, guiding us through the brilliance and the pragmatic challenges of this new era.
    
    ---
    
    ### 1. Visual Anchor
    
    (Imagine a striking image projected: A futuristic Manhattan skyline at dawn. One towering skyscraper stands out – its entire facade is not glass or steel, but a shimmering, fluid skin of light. It's constantly shifting, subtly rippling with blues, yellows, and whites. You see faint tendrils of light not just radiating outwards, but actively *bending* and *cascading* down its own structure, illuminating a shadowed street below with an artificial yet vibrant 'sunlight.' The building feels alive, sentient.)
    
    "Imagine this, ladies and gentlemen: Not a static monument, but a living, breathing interface. This is a building whose very surface is a dynamic, responsive canvas of light – actively sensing, orchestrating, and distributing natural, or bio-optimized, illumination across the urban fabric. Its facade isn't just *catching* the sun; it's *dancing* with it, ensuring every corner of the city receives its vital share. This isn't just architecture; it's **orchestrated urban light.**"
    
    ---
    
    ### 2. The Discovery
    
    "The profound discovery we're championing today is a fundamental re-wiring of our urban DNA: **Natural light is hereby re-designated as a public utility and a fundamental human right, managed by a sophisticated, city-wide AI.** We are dismantling the archaic notion of 'air-rights' and ushering in the era of 'light-rights' – where the sun is not a commodity to be blocked, but a nutrient to be cultivated and distributed equitably. Buildings will shed their static envelopes, transforming into 'sentient skins' – active participants in a networked 'Light Commons,' ensuring that access to light, crucial for our circadian health, is not dictated by wealth or location, but by a collective urban mandate."
    
    ---
    
    ### 3. Business Moat
    
    "What makes this radical reimagining not just a vision, but a defensible, sustainable, and deeply integrated system? Our business moat is forged from several interlocking, formidable pillars:
    
    1.  **Exclusive, City-Scale AI Orchestration:** At the core lies the **Urban Light Optimization Algorithm (ULOA)** – a singular, proprietary intelligence layer. This AI monitors atmospheric conditions, energy demand, and even aggregated public health data city-wide, issuing real-time directives to every building. This creates an unparalleled, centralized data and control advantage over the urban environment.
    2.  **Regulatory Lock-in & New Economic Models:** We're not just proposing technology; we're proposing a *mandate*. The universal requirement for dynamic facades and the introduction of **'Shadow Futures'** and **'Light-Debt Collateralization'** create entirely new, regulated financial markets. This system cornerstones urban light management, turning negative externalities (shadows) into tradable, collateralizable assets, effectively creating an economic ecosystem entirely dependent on our framework.
    3.  **Massive, Integrated Infrastructure Investment:** The sheer scale of mandated dynamic facades, embedded fiber optics, and city-wide sensor networks represents an unprecedented and non-replicable infrastructure investment. Once established, this deeply integrated, distributed system becomes an indispensable foundation of urban life, virtually impossible to displace or compete with piecemeal.
    4.  **Data-Driven Human Optimization & Equitable Distribution:** By integrating anonymized health data into a **'Bio-Optimization Score,'** our system uniquely optimizes for collective human well-being, creating a 'meritocracy of need' for prime light access. This elevates light management from a utility to a therapeutic resource, grounded in unique health insights, providing an invaluable, human-centric competitive edge."
    
    ---
    
    ### 4. Teacher Note
    
    "Now, for the essential takeaway, the 'Teacher Note' that allows us to reflect critically on these bold propositions. While the ambition to treat natural light as a public utility and a therapeutic tool is profoundly inspiring and necessary, its proposed mechanics as described – particularly the notion of buildings 'scavenging' and 'intensifying' scant ambient light into full-spectrum illumination without massive external energy input – currently exists beyond the bounds of fundamental physics and economic feasibility.
    
    The true lesson here is multifaceted: It's about the vital tension between a truly audacious, transformative vision for human well-being and the rigorous demands of scientific and engineering reality. This conceptual framework serves as a powerful thought experiment, urging us to ask: How do we achieve the *spirit* of such radical ideas – ensuring equitable access to vital environmental nutrients and fostering collective biological flourishing – with solutions that are both physically possible, economically sustainable, and ethically sound? It is a call not just to dream big, but to **innovate smarter, grounded in the unyielding laws of nature and responsible resource allocation.**"

