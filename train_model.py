"""AI-Driven Early Anemia Risk Prediction - Model Training & Comparison Script.

Notice: The dataset generated here is a synthetic demonstration dataset designed
strictly for educational, academic modeling, and software engineering demonstration.
It DOES NOT represent actual medical clinical trials and MUST NOT be used for clinical
diagnostic decision-making.
"""

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

NUMERIC_FEATURES = ["age", "height", "weight", "bmi"]
CATEGORICAL_FEATURES = ["iron_rich_food_frequency", "vitamin_c_frequency"]
BINARY_FEATURES = [
    "heavy_menstrual_flow",
    "pregnant",
    "vegetarian",
    "tea_coffee_with_meals",
    "fatigue",
    "dizziness",
    "weakness",
    "shortness_of_breath",
    "pale_skin",
    "previous_anemia",
    "chronic_condition"
]

ALL_FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES


def generate_synthetic_dataset(n_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic dataset reflecting known nutritional and physiological risk factors.
    
    Factors considered:
    - Low iron intake, heavy menstrual flow, pregnancy, fatigue, dizziness, pale skin, previous anemia.
    """
    np.random.seed(random_seed)

    ages = np.random.randint(18, 60, size=n_samples)
    heights = np.random.normal(158, 7, size=n_samples).round(1)  # cm
    weights = np.random.normal(57, 10, size=n_samples).round(1)  # kg
    bmis = (weights / ((heights / 100) ** 2)).round(2)

    heavy_flow = np.random.choice([0, 1], size=n_samples, p=[0.70, 0.30])
    pregnant = np.random.choice([0, 1], size=n_samples, p=[0.90, 0.10])
    vegetarian = np.random.choice([0, 1], size=n_samples, p=[0.60, 0.40])
    
    iron_freq = np.random.choice(["rarely", "sometimes", "often"], size=n_samples, p=[0.35, 0.45, 0.20])
    vit_c_freq = np.random.choice(["rarely", "sometimes", "often"], size=n_samples, p=[0.30, 0.50, 0.20])
    tea_with_meals = np.random.choice([0, 1], size=n_samples, p=[0.55, 0.45])

    prev_anemia = np.random.choice([0, 1], size=n_samples, p=[0.80, 0.20])
    chronic_cond = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])

    # Latent risk score calculation (physiologically weighted prototype formula)
    risk_score = (
        (heavy_flow * 2.2) +
        (pregnant * 1.8) +
        (prev_anemia * 2.5) +
        (chronic_cond * 1.2) +
        (tea_with_meals * 0.8) +
        (vegetarian * 0.6) +
        (np.where(iron_freq == "rarely", 2.2, np.where(iron_freq == "sometimes", 0.8, 0.0))) +
        (np.where(vit_c_freq == "rarely", 1.2, np.where(vit_c_freq == "sometimes", 0.4, 0.0))) +
        (np.where(bmis < 18.5, 1.0, 0.0))
    )

    # Symptoms are more likely when latent risk is higher
    prob_fatigue = np.clip(0.15 + (risk_score / 14.0), 0.05, 0.90)
    prob_dizziness = np.clip(0.10 + (risk_score / 16.0), 0.05, 0.85)
    prob_weakness = np.clip(0.12 + (risk_score / 15.0), 0.05, 0.88)
    prob_short_breath = np.clip(0.08 + (risk_score / 18.0), 0.02, 0.75)
    prob_pale_skin = np.clip(0.10 + (risk_score / 15.0), 0.04, 0.82)

    fatigue = (np.random.rand(n_samples) < prob_fatigue).astype(int)
    dizziness = (np.random.rand(n_samples) < prob_dizziness).astype(int)
    weakness = (np.random.rand(n_samples) < prob_weakness).astype(int)
    shortness_breath = (np.random.rand(n_samples) < prob_short_breath).astype(int)
    pale_skin = (np.random.rand(n_samples) < prob_pale_skin).astype(int)

    # Final combined risk score including clinical symptoms
    symptom_sum = fatigue + dizziness + weakness + shortness_breath + pale_skin
    final_score = risk_score + (symptom_sum * 1.4) + np.random.normal(0, 1.0, size=n_samples)

    # Binarize for classification label (Elevated risk threshold)
    threshold = np.percentile(final_score, 62)  # ~38% positive class prevalence
    anemia_risk = (final_score >= threshold).astype(int)

    df = pd.DataFrame({
        "age": ages,
        "height": heights,
        "weight": weights,
        "bmi": bmis,
        "heavy_menstrual_flow": heavy_flow,
        "pregnant": pregnant,
        "vegetarian": vegetarian,
        "iron_rich_food_frequency": iron_freq,
        "vitamin_c_frequency": vit_c_freq,
        "tea_coffee_with_meals": tea_with_meals,
        "fatigue": fatigue,
        "dizziness": dizziness,
        "weakness": weakness,
        "shortness_of_breath": shortness_breath,
        "pale_skin": pale_skin,
        "previous_anemia": prev_anemia,
        "chronic_condition": chronic_cond,
        "anemia_risk": anemia_risk
    })

    return df


def build_preprocessor() -> ColumnTransformer:
    """Construct Scikit-Learn preprocessing pipeline for tabular input."""
    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES)
        ]
    )
    return preprocessor


def train_and_compare_models():
    """Train and compare Logistic Regression, Decision Tree, and Random Forest."""
    print("=" * 70)
    print("STEP 1: Generating Synthetic Anemia Screening Dataset...")
    df = generate_synthetic_dataset(n_samples=1600, random_seed=42)
    dataset_path = DATA_DIR / "anemia_dataset.csv"
    df.to_csv(dataset_path, index=False)
    print(f"[+] Dataset saved to: {dataset_path} (Total records: {len(df)})")
    print(f"    Positive Class (Elevated Risk): {df['anemia_risk'].sum()} / {len(df)} "
          f"({df['anemia_risk'].mean() * 100:.1f}%)")

    X = df[ALL_FEATURE_COLUMNS]
    y = df["anemia_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"[+] Train set: {len(X_train)} samples | Test set: {len(X_test)} samples\n")

    preprocessor = build_preprocessor()

    # Candidate Models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_split=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=7, random_state=42)
    }

    results = {}
    fitted_pipelines = {}

    print("=" * 70)
    print(f"{'Algorithm':<22} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<7} | {'F1':<6} | {'ROC-AUC':<7}")
    print("-" * 70)

    for name, clf in models.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        pipe.fit(X_train, y_train)

        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": auc,
            "confusion_matrix": cm,
            "pipeline": pipe
        }
        fitted_pipelines[name] = pipe

        print(f"{name:<22} | {acc:.4f}   | {prec:.4f}    | {rec:.4f}  | {f1:.4f} | {auc:.4f}")

    print("=" * 70)

    # Detailed Confusion Matrix for Each Model
    for name in models:
        print(f"\n--- Confusion Matrix [{name}] ---")
        cm = results[name]["confusion_matrix"]
        print(f"True Negatives:  {cm[0][0]:<4} | False Positives: {cm[0][1]:<4}")
        print(f"False Negatives: {cm[1][0]:<4} | True Positives:  {cm[1][1]:<4}")

    # Random Forest is selected as requested in specifications
    best_model_name = "Random Forest"
    print(f"\n[*] Selected Production Model: {best_model_name} (ROC-AUC: {results[best_model_name]['roc_auc']:.4f}, F1: {results[best_model_name]['f1']:.4f})")

    best_pipeline = results[best_model_name]["pipeline"]
    model_output_path = MODELS_DIR / "anemia_model.joblib"
    joblib.dump(best_pipeline, model_output_path)
    print(f"[+] Full preprocessing + model pipeline successfully saved to: {model_output_path}")

    return best_model_name, results


if __name__ == "__main__":
    train_and_compare_models()
