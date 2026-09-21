"""IronHer AI - Nutritional Chatbot Copilot Engine.

Features:
- Evidence-based nutritional advice for women's iron health.
- Strict Medical Safety Guardrails: Rejects medication/supplement prescriptions and dosages.
- Dual-Mode Engine:
    1. Built-in Biomedical NLP & Knowledge Base (works 100% offline without API keys).
    2. Optional Google Gemini API integration if GEMINI_API_KEY is configured in .env.
"""

import os
import re

# Strict Medical Guardrail System Instruction
SYSTEM_GUARDRAIL = """
You are the IronHer AI Nutrition Copilot, a specialized educational assistant for women's nutritional health.
Your goal is to provide food-first dietary advice regarding iron, absorption enhancers, and absorption inhibitors.

CRITICAL MEDICAL SAFETY RULES:
1. NEVER diagnose medical conditions.
2. NEVER prescribe medications, pharmaceutical iron supplements (e.g., ferrous sulfate, ferrous fumarate, iron injections), or specific milligram (mg) dosages.
3. If a user asks about taking iron pills or supplements, reply that supplements require formal laboratory blood tests (CBC, Ferritin) and prescription by a licensed doctor. Direct them to food sources instead.
4. Always prioritize food-first advice (lentils, spinach, amla, citrus, meat/eggs for non-vegetarians).
5. Always explain absorption biology (Vitamin C reduces ferric Fe3+ to absorbable ferrous Fe2+; tea/coffee tannins inhibit absorption).
"""

# Knowledge Base for Local Intelligent Offline Response
KNOWLEDGE_PATTERNS = [
    {
        "keywords": ["vitamin c", "ascorbic acid", "citrus", "lemon", "amla", "enhance", "absorption"],
        "reply": (
            "**Vitamin C (Ascorbic Acid) is the strongest promoter of iron absorption!**\n\n"
            "• **Biochemical Mechanism**: Non-heme iron from plant foods (lentils, greens) enters the body as insoluble ferric iron (Fe³⁺). "
            "Vitamin C chemically reduces it into soluble ferrous iron (Fe²⁺), which binds readily to the DMT1 intestinal transporter.\n"
            "• **Best Sources**: Amla (Indian gooseberry — ~300mg/fruit), guava (~228mg), yellow bell peppers, oranges, and fresh lemon juice.\n"
            "• **Practical Tip**: Always squeeze fresh lime or lemon directly over cooked dal or salads right before eating!"
        )
    },
    {
        "keywords": ["tea", "coffee", "tannin", "caffeine", "inhibit", "block", "chai"],
        "reply": (
            "**Tea and coffee are potent dietary iron inhibitors.**\n\n"
            "• **The Science**: Tea and coffee contain polyphenols, chlorogenic acid, and tannins that bind to non-heme iron, forming insoluble precipitates that pass unabsorbed through the gut.\n"
            "• **Absorption Drop**: Drinking strong black tea with an iron-rich meal can reduce iron absorption by **50% to 70%**.\n"
            "• **Recommended Action**: Do not consume tea, coffee, or milk within **60 to 90 minutes** before or after iron-dense meals."
        )
    },
    {
        "keywords": ["vegetarian", "plant", "vegan", "dal", "spinach", "lentil", "seeds"],
        "reply": (
            "**Top Plant-Based (Non-Heme) Iron Sources for Vegetarians:**\n\n"
            "1. **Cooked Lentils & Legumes**: Chickpeas (chana), black lentils, and kidney beans (rajma) provide 4–6 mg iron per cup.\n"
            "2. **Dark Leafy Greens**: Moringa (drumstick) leaves, spinach (palak), and fenugreek (methi).\n"
            "3. **Seeds & Dried Fruits**: Pumpkin seeds, sesame seeds (til), and soaked black raisins.\n\n"
            "*Remember*: Plant iron is non-heme (2%–20% baseline absorption). Always pair these foods with Vitamin C (lemon, tomatoes, amla) to double absorption!"
        )
    },
    {
        "keywords": ["non-vegetarian", "meat", "chicken", "egg", "fish", "heme"],
        "reply": (
            "**Heme Iron in Non-Vegetarian Diets:**\n\n"
            "• Animal protein sources contain **heme iron**, which is absorbed at **15% to 35% efficiency** via the HCP1 transporter, largely independent of meal composition.\n"
            "• **Top Sources**: Lean poultry, eggs, seafood, and organ meats.\n"
            "• **Balance**: Combine animal proteins with antioxidant-rich greens and whole legumes for comprehensive micronutrient coverage and gut health."
        )
    },
    {
        "keywords": ["menstrual", "period", "bleeding", "heavy flow", "menorrhagia", "cycle"],
        "reply": (
            "**Menstrual Blood Loss & Iron Balance:**\n\n"
            "• Heavy menstrual bleeding (*menorrhagia*) is the leading cause of iron depletion in women of reproductive age.\n"
            "• Each milliliter of lost blood removes approximately 0.5 mg of elemental iron from the body's reserves.\n"
            "• **Action Plan**: Focus on daily iron-dense meals and schedule a consultation with a gynecologist or physician to check your **serum ferritin** levels."
        )
    },
    {
        "keywords": ["pregnant", "pregnancy", "trimester", "baby", "maternal"],
        "reply": (
            "**Pregnancy & Maternal Iron Needs:**\n\n"
            "• During pregnancy, maternal blood volume expands by up to 50%, and fetal-placental tissue requires substantial iron stores.\n"
            "• **Food Strategy**: Eat varied iron-rich legumes, leafy greens, and Vitamin C sources daily.\n"
            "• **Medical Notice**: Pregnancy-related nutritional requirements must be directly supervised by your obstetrician. Never self-prescribe supplements without clinical blood tests."
        )
    },
    {
        "keywords": ["supplement", "pill", "tablet", "ferrous sulfate", "dosage", "injection", "medicine", "syrup"],
        "reply": (
            "**Medical Safety Policy on Supplements & Medications:**\n\n"
            "⚠️ **IronHer AI does not recommend or prescribe pharmaceutical iron supplements or dosages.**\n\n"
            "• Taking unsupervised iron pills can lead to adverse gastrointestinal side effects or dangerous iron overload (*hemochromatosis*).\n"
            "• If you suspect severe deficiency or experience chronic exhaustion, please visit a doctor for a Complete Blood Count (CBC) and serum ferritin test. A licensed physician must determine appropriate clinical therapy."
        )
    },
    {
        "keywords": ["symptom", "fatigue", "tired", "dizzy", "weak", "pale", "breath"],
        "reply": (
            "**Common Symptoms Associated with Iron Depletion:**\n\n"
            "• **Why it happens**: Low hemoglobin reduces oxygen delivery to muscles, heart, and brain.\n"
            "• **Frequent Signs**: Chronic fatigue despite sleep, dizziness upon standing, pale inner eyelids/nailbeds, and shortness of breath during stairs.\n"
            "• **What to do**: Use our **Screening Assessment** tool to estimate your risk, adopt food-first iron habits, and schedule routine laboratory blood work."
        )
    },
    {
        "keywords": ["calcium", "milk", "cheese", "dairy", "yogurt", "curd"],
        "reply": (
            "**Calcium and Iron Interaction:**\n\n"
            "• Calcium is an essential mineral, but it competes with both heme and non-heme iron for intestinal uptake.\n"
            "• **Best Practice**: Enjoy milk, yogurt, and cheese separately from your primary iron-dense meals (e.g., as snacks) rather than washing down lentils with a glass of milk."
        )
    }
]


def generate_chat_response(user_message: str) -> str:
    """Generate an evidence-based, medically safe nutritional response."""
    cleaned = user_message.strip().lower()
    if not cleaned:
        return "Please ask a question about iron-rich foods, Vitamin C enhancers, or dietary habits!"

    # 1. Check for Medication / Supplement Dosage attempts (Strict Guardrail Check)
    supplement_triggers = ["how many mg", "prescribe", "iron pill", "ferrous sulfate", "dosage", "inject", "syrup dose"]
    if any(t in cleaned for t in supplement_triggers):
        return (
            "⚠️ **Clinical Guardrail Notice**: As an educational platform, IronHer AI strictly avoids prescribing pharmaceutical supplements, medications, or dosages. "
            "High-dose iron can cause toxicity without formal laboratory blood work (CBC / Ferritin). "
            "Please consult a certified physician for therapeutic prescriptions. In the meantime, I can recommend natural food sources like lentils, moringa, amla, and citrus fruits!"
        )

    # 2. Try Gemini API if GEMINI_API_KEY is available in environment
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_GUARDRAIL
            )
            response = model.generate_content(user_message)
            if response and response.text:
                return response.text.strip()
        except Exception:
            # Fall back to local knowledge base on any API error or quota limit
            pass

    # 3. Intelligent Local Biomedical Knowledge Base Engine (Offline fallback)
    best_match = None
    max_score = 0

    for item in KNOWLEDGE_PATTERNS:
        score = sum(1 for kw in item["keywords"] if re.search(r'\b' + re.escape(kw) + r'\b', cleaned) or kw in cleaned)
        if score > max_score:
            max_score = score
            best_match = item["reply"]

    if best_match and max_score > 0:
        return best_match

    # Default Intelligent Guidance
    return (
        "Hello! I am your **IronHer AI Nutrition Copilot**.\n\n"
        "I can assist you with:\n"
        "• **Iron-Dense Foods**: Best options for vegetarian and non-vegetarian diets.\n"
        "• **Absorption Enhancers**: How Vitamin C (amla, citrus) boosts non-heme iron.\n"
        "• **Dietary Inhibitors**: Why to avoid tea, coffee, and excess calcium with meals.\n"
        "• **Menstrual & Pregnancy Nutrition**: Dietary strategies for high-demand stages.\n\n"
        "*Try asking: 'What are the best vegetarian iron foods?' or 'How does tea affect iron?'*"
    )
