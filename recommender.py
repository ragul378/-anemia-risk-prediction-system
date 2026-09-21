"""Rule-Based Personalized Nutrition & Educational Recommendation Engine for Women.

Strict Medical Safety Guidelines:
- Never provide diagnoses or prescriptions.
- Never recommend supplements, medications, or specific dosages.
- All guidance is educational and food-first.
- Flag conditions requiring direct consultation with licensed healthcare professionals.
"""

def generate_recommendations(assessment_data: dict, risk_level: str) -> list[dict]:
    """Generate categorized educational nutrition recommendations and clinical lifestyle notes.
    
    Returns a list of dicts with keys:
      - category: str (e.g., "Iron-Rich Foods", "Absorption Enhancers", "Absorption Inhibitors", "Clinical Guidance")
      - food: str
      - reason: str
    """
    recs = []

    is_veg = bool(assessment_data.get("vegetarian", False))
    iron_freq = assessment_data.get("iron_rich_food_frequency", "sometimes")
    vit_c_freq = assessment_data.get("vitamin_c_frequency", "sometimes")
    tea_coffee = bool(assessment_data.get("tea_coffee_with_meals", False))
    heavy_flow = bool(assessment_data.get("heavy_menstrual_flow", False))
    pregnant = bool(assessment_data.get("pregnant", False))
    fatigue = bool(assessment_data.get("fatigue", False))
    dizziness = bool(assessment_data.get("dizziness", False))
    pale_skin = bool(assessment_data.get("pale_skin", False))
    weakness = bool(assessment_data.get("weakness", False))

    # 1. Iron-Rich Food Recommendations (Tailored to Dietary Preference)
    if is_veg:
        recs.append({
            "category": "Iron-Rich Foods (Plant / Non-Heme)",
            "food": "Lentils, Chickpeas, Spinach, and Moringa Leaves",
            "reason": (
                "Legumes and dark green leafy vegetables are dense sources of non-heme plant iron. "
                "Pairing them with acid or vitamin C improves their bioavailability."
            )
        })
        recs.append({
            "category": "Iron-Rich Foods (Plant / Non-Heme)",
            "food": "Pumpkin Seeds, Sesame Seeds, and Black Raisins",
            "reason": (
                "Seeds and dried fruits offer concentrated non-heme iron and essential trace minerals "
                "suitable for a plant-based daily diet."
            )
        })
    else:
        recs.append({
            "category": "Iron-Rich Foods (Heme & Non-Heme)",
            "food": "Poultry, Eggs, and Lean Meats",
            "reason": (
                "Animal sources contain heme iron, which is absorbed up to 2 to 3 times more efficiently "
                "by the intestinal tract than non-heme plant iron."
            )
        })
        recs.append({
            "category": "Iron-Rich Foods (Plant / Non-Heme)",
            "food": "Spinach, Beetroot, Chickpeas, and Quinoa",
            "reason": (
                "Complementing animal proteins with mineral-rich greens and whole legumes provides "
                "diverse dietary fiber, folate, and sustained micronutrient density."
            )
        })

    # If dietary iron frequency was reported as 'rarely'
    if iron_freq == "rarely":
        recs.append({
            "category": "Dietary Habit Adjustment",
            "food": "Consistent Daily Inclusion of Iron Sources",
            "reason": (
                "Your assessment indicated infrequent intake of iron-rich foods. Establishing a daily routine "
                "with at least one iron-dense food item per meal helps sustain red blood cell production."
            )
        })

    # 2. Vitamin C Absorption Enhancers
    if vit_c_freq in ["rarely", "sometimes"]:
        recs.append({
            "category": "Iron Absorption Enhancer",
            "food": "Amla (Indian Gooseberry), Guava, Lemons, and Oranges",
            "reason": (
                "Vitamin C (ascorbic acid) chemically reduces ferric iron (Fe3+) to ferrous iron (Fe2+), "
                "significantly increasing non-heme iron uptake in the duodenum."
            )
        })
        recs.append({
            "category": "Iron Absorption Enhancer",
            "food": "Bell Peppers, Tomatoes, and Fresh Lime Dressing",
            "reason": (
                "Adding fresh lime juice or crisp bell peppers directly over cooked lentils or salads "
                "counteracts naturally occurring phytates."
            )
        })

    # 3. Dietary Inhibitors (Tea / Coffee with meals)
    if tea_coffee:
        recs.append({
            "category": "Absorption Inhibitor Awareness",
            "food": "Separating Tea / Coffee from Main Meals (1 to 2 Hour Window)",
            "reason": (
                "Tannins, polyphenols, and chlorogenic acid present in tea and coffee bind to dietary iron "
                "forming insoluble complexes that reduce iron absorption by 50% to 70%. Enjoy these beverages "
                "at least 60 to 90 minutes away from iron-rich meals."
            )
        })

    # 4. Physiological & Clinical Guidance
    if heavy_flow:
        recs.append({
            "category": "Clinical Consultation Notice",
            "food": "Gynecological & Medical Evaluation for Menstrual Loss",
            "reason": (
                "Heavy menstrual blood loss (menorrhagia) is one of the leading drivers of negative iron balance "
                "in women of reproductive age. Please discuss your flow volume with a healthcare provider for "
                "formal serum ferritin testing."
            )
        })

    if pregnant:
        recs.append({
            "category": "Maternal Nutritional Safety",
            "food": "Supervised Obstetric Care & Routine Prenatal Blood Work",
            "reason": (
                "During pregnancy, plasma volume and fetal-placental demands expand dramatically. Dietary planning "
                "must be reviewed directly with your obstetrician or registered dietitian."
            )
        })

    if fatigue or dizziness or pale_skin or weakness:
        recs.append({
            "category": "Symptom Monitoring & Medical Evaluation",
            "food": "Healthcare Professional Consultation (CBC & Iron Profile)",
            "reason": (
                "Self-reported fatigue, dizziness, pale skin, or weakness can indicate depleted hemoglobin or other "
                "underlying physiological conditions. We strongly recommend scheduling a Complete Blood Count (CBC) "
                "with your physician."
            )
        })

    return recs


def get_factors_considered(assessment_data: dict) -> list[dict]:
    """Identify key factors considered by the screening model for transparent user feedback.
    
    Notice: Phrased strictly as 'considered factors', NOT definitive causes.
    """
    factors = []

    if bool(assessment_data.get("heavy_menstrual_flow")):
        factors.append({
            "factor": "Heavy Menstrual Flow",
            "impact": "Higher recurrent iron losses during menstrual cycles."
        })

    if bool(assessment_data.get("pregnant")):
        factors.append({
            "factor": "Pregnancy",
            "impact": "Significantly elevated maternal blood volume and fetal iron requirements."
        })

    if bool(assessment_data.get("vegetarian")):
        factors.append({
            "factor": "Plant-Based Dietary Pattern",
            "impact": "Relying predominantly on non-heme iron, which has lower physiological bioavailability."
        })

    if assessment_data.get("iron_rich_food_frequency") == "rarely":
        factors.append({
            "factor": "Infrequent Iron-Dense Food Intake",
            "impact": "Lower baseline dietary intake of essential heme/non-heme minerals."
        })

    if assessment_data.get("vitamin_c_frequency") == "rarely":
        factors.append({
            "factor": "Low Vitamin C Intake",
            "impact": "Reduced conversion and bioavailability of plant-derived non-heme iron."
        })

    if bool(assessment_data.get("tea_coffee_with_meals")):
        factors.append({
            "factor": "Tea / Coffee Consumption with Meals",
            "impact": "Polyphenols and tannins binding to iron, impeding intestinal absorption."
        })

    symptoms = []
    if assessment_data.get("fatigue"): symptoms.append("Fatigue")
    if assessment_data.get("dizziness"): symptoms.append("Dizziness")
    if assessment_data.get("weakness"): symptoms.append("Weakness")
    if assessment_data.get("shortness_of_breath"): symptoms.append("Shortness of breath")
    if assessment_data.get("pale_skin"): symptoms.append("Pale skin")

    if symptoms:
        factors.append({
            "factor": f"Reported Symptoms ({', '.join(symptoms)})",
            "impact": "Common clinical signs frequently associated with decreased tissue oxygenation."
        })

    if bool(assessment_data.get("previous_anemia")):
        factors.append({
            "factor": "Previous History of Anemia",
            "impact": "Past clinical history indicates elevated susceptibility to recurring iron depletion."
        })

    if bool(assessment_data.get("chronic_condition")):
        factors.append({
            "factor": "Chronic Health Condition",
            "impact": "Chronic inflammatory states can alter hepcidin regulation and iron utilization."
        })

    bmi = assessment_data.get("bmi", 22.0)
    if bmi < 18.5:
        factors.append({
            "factor": f"Underweight BMI ({bmi:.1f})",
            "impact": "May correlate with overall micronutrient and caloric insufficiency."
        })

    return factors
