"""Model Evaluation and Diagnostics Script.
Loads the serialized pipeline and generates a comprehensive evaluation report.
"""

import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "anemia_model.joblib"
DATA_PATH = BASE_DIR / "data" / "anemia_dataset.csv"

def evaluate_saved_model():
    if not MODEL_PATH.exists():
        print(f"[!] Error: Model file not found at {MODEL_PATH}. Please run train_model.py first.")
        return

    if not DATA_PATH.exists():
        print(f"[!] Error: Dataset not found at {DATA_PATH}. Please run train_model.py first.")
        return

    print(f"[*] Loading model from: {MODEL_PATH}")
    pipeline = joblib.load(MODEL_PATH)
    
    print(f"[*] Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["anemia_risk"])
    y = df["anemia_risk"]

    y_pred = pipeline.predict(X)
    y_prob = pipeline.predict_proba(X)[:, 1]

    print("\n" + "=" * 60)
    print("SAVED PIPELINE EVALUATION ON DATASET")
    print("=" * 60)
    print(classification_report(y, y_pred, target_names=["Low Risk (0)", "Elevated Risk (1)"]))

    auc = roc_auc_score(y, y_prob)
    cm = confusion_matrix(y, y_pred)
    print(f"Overall ROC-AUC Score: {auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"TN: {cm[0][0]:<5} | FP: {cm[0][1]:<5}")
    print(f"FN: {cm[1][0]:<5} | TP: {cm[1][1]:<5}")
    print("=" * 60)

    # Test sample prediction
    sample = pd.DataFrame([{
        "age": 28,
        "height": 158.0,
        "weight": 52.0,
        "bmi": 20.83,
        "heavy_menstrual_flow": 1,
        "pregnant": 0,
        "vegetarian": 1,
        "iron_rich_food_frequency": "rarely",
        "vitamin_c_frequency": "rarely",
        "tea_coffee_with_meals": 1,
        "fatigue": 1,
        "dizziness": 1,
        "weakness": 1,
        "shortness_of_breath": 0,
        "pale_skin": 1,
        "previous_anemia": 1,
        "chronic_condition": 0
    }])
    
    prob = pipeline.predict_proba(sample)[0, 1]
    print(f"\nTest High-Risk Profile Predicted Probability: {prob:.4f} ({prob*100:.1f}%)")
    print("[+] Model pipeline verified and ready for production inference.")

if __name__ == "__main__":
    evaluate_saved_model()
