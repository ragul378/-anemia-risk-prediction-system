"""Machine Learning Model & Pipeline Integration Tests."""

import joblib
import pandas as pd
from pathlib import Path
from config import Config

def test_model_file_exists():
    """Ensure the serialized pipeline file is generated and non-empty."""
    model_path = Path(Config.MODEL_PATH)
    assert model_path.exists(), "anemia_model.joblib does not exist. Run train_model.py first."
    assert model_path.stat().st_size > 1000, "Model file appears corrupted or empty."

def test_model_inference_contract():
    """Verify that model consumes input dataframe and outputs valid probabilities."""
    model = joblib.load(Config.MODEL_PATH)

    low_risk_sample = pd.DataFrame([{
        "age": 22,
        "height": 165.0,
        "weight": 60.0,
        "bmi": 22.04,
        "heavy_menstrual_flow": 0,
        "pregnant": 0,
        "vegetarian": 0,
        "iron_rich_food_frequency": "often",
        "vitamin_c_frequency": "often",
        "tea_coffee_with_meals": 0,
        "fatigue": 0,
        "dizziness": 0,
        "weakness": 0,
        "shortness_of_breath": 0,
        "pale_skin": 0,
        "previous_anemia": 0,
        "chronic_condition": 0
    }])

    high_risk_sample = pd.DataFrame([{
        "age": 28,
        "height": 155.0,
        "weight": 44.0,
        "bmi": 18.31,
        "heavy_menstrual_flow": 1,
        "pregnant": 1,
        "vegetarian": 1,
        "iron_rich_food_frequency": "rarely",
        "vitamin_c_frequency": "rarely",
        "tea_coffee_with_meals": 1,
        "fatigue": 1,
        "dizziness": 1,
        "weakness": 1,
        "shortness_of_breath": 1,
        "pale_skin": 1,
        "previous_anemia": 1,
        "chronic_condition": 1
    }])

    prob_low = model.predict_proba(low_risk_sample)[0, 1]
    prob_high = model.predict_proba(high_risk_sample)[0, 1]

    # Probabilities must be within [0, 1]
    assert 0.0 <= prob_low <= 1.0
    assert 0.0 <= prob_high <= 1.0

    # High-risk profile must exhibit substantially higher probability than healthy baseline
    assert prob_high > prob_low
    assert prob_high >= 0.60
    assert prob_low < 0.40
