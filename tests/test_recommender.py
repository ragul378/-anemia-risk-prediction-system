"""Recommendation Engine and Medical Safety Rule Tests."""

from recommender import generate_recommendations, get_factors_considered

def test_vegetarian_recommendations():
    """Vegetarian assessment should receive plant-based iron foods."""
    data = {
        "vegetarian": True,
        "iron_rich_food_frequency": "rarely",
        "vitamin_c_frequency": "sometimes",
        "tea_coffee_with_meals": False
    }
    recs = generate_recommendations(data, "Moderate")
    categories = [r["category"] for r in recs]
    foods = " ".join([r["food"] for r in recs]).lower()

    assert any("Plant" in c for c in categories)
    assert "lentils" in foods or "chickpeas" in foods or "spinach" in foods

def test_non_vegetarian_recommendations():
    """Non-vegetarian assessment should receive heme animal protein guidance."""
    data = {
        "vegetarian": False,
        "iron_rich_food_frequency": "sometimes",
        "vitamin_c_frequency": "often",
        "tea_coffee_with_meals": False
    }
    recs = generate_recommendations(data, "Low")
    foods = " ".join([r["food"] for r in recs]).lower()

    assert "poultry" in foods or "eggs" in foods or "meats" in foods

def test_tea_coffee_inhibitor_rule():
    """Drinking tea/coffee with meals must generate timing spacing guidance."""
    data = {
        "vegetarian": True,
        "tea_coffee_with_meals": True
    }
    recs = generate_recommendations(data, "Moderate")
    reasons = " ".join([r["reason"] for r in recs]).lower()

    assert "tannin" in reasons or "inhibitor" in reasons or "tea" in reasons or "60" in reasons

def test_menorrhagia_and_pregnancy_clinical_alerts():
    """Heavy menstrual flow and pregnancy must trigger professional consultation flags."""
    data = {
        "heavy_menstrual_flow": True,
        "pregnant": True
    }
    recs = generate_recommendations(data, "High")
    categories = [r["category"] for r in recs]
    reasons = " ".join([r["reason"] for r in recs]).lower()

    assert any("Clinical" in c or "Maternal" in c for c in categories)
    assert "obstetrician" in reasons or "healthcare provider" in reasons or "ferritin" in reasons

def test_strict_medical_safety_no_prescriptions():
    """CRITICAL: Recommender must NEVER recommend medication, supplements, or clinical dosages."""
    sample_assessments = [
        {"vegetarian": True, "heavy_menstrual_flow": True, "pregnant": True, "fatigue": True},
        {"vegetarian": False, "tea_coffee_with_meals": True, "dizziness": True, "pale_skin": True},
        {"iron_rich_food_frequency": "rarely", "vitamin_c_frequency": "rarely"}
    ]

    forbidden_keywords = [
        "mg tablet", "ferrous sulfate", "ferrous fumarate", "iron injection",
        "oral supplement", "take 1 pill", "prescription", "dosage:", "daily dose"
    ]

    for sample in sample_assessments:
        recs = generate_recommendations(sample, "High")
        for r in recs:
            content = f"{r['category']} {r['food']} {r['reason']}".lower()
            for forbidden in forbidden_keywords:
                assert forbidden not in content, f"Forbidden medical term found: '{forbidden}' in {content}"
