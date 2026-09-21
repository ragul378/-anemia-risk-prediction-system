"""Database initialization script.
Safely creates database tables for User, Assessment, and Recommendation
without wiping existing data. Works with SQLite and PostgreSQL.
"""
import os
import sys
from pathlib import Path
from flask import Flask
from config import config_by_name
from database import db

def init_database():
    env_name = os.getenv("FLASK_ENV", "development")
    config_cls = config_by_name.get(env_name, config_by_name["default"])

    app = Flask(__name__)
    app.config.from_object(config_cls)

    # Ensure instance directory exists for SQLite
    instance_dir = Path(app.root_path) / "instance"
    instance_dir.mkdir(exist_ok=True)

    db.init_app(app)

    with app.app_context():
        print(f"[*] Connecting to database at: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        print("[+] Database tables initialized successfully (safe check, existing data preserved).")

        # Seed sample demo user if not already existing
        from database import (
            get_user_by_email,
            create_user,
            save_assessment,
            save_recommendations
        )
        demo_user = get_user_by_email("demo@ironher.ai")
        if not demo_user:
            print("[*] Creating demo user: demo@ironher.ai / password123")
            demo_user = create_user(
                name="Ananya Demo",
                email="demo@ironher.ai",
                password="password123",
                age=25,
                height=161.0,
                weight=53.0,
                dietary_preference="Vegetarian"
            )
            # Add two baseline assessments to show live longitudinal chart immediately
            a1 = save_assessment(
                user_id=demo_user.id,
                assessment_data={
                    "age": 25, "height": 161.0, "weight": 53.0, "bmi": 20.45,
                    "heavy_menstrual_flow": 1, "pregnant": 0, "vegetarian": 1,
                    "iron_rich_food_frequency": "rarely", "vitamin_c_frequency": "rarely",
                    "tea_coffee_with_meals": 1, "fatigue": 1, "dizziness": 1,
                    "weakness": 1, "shortness_of_breath": 0, "pale_skin": 1,
                    "previous_anemia": 1, "chronic_condition": 0
                },
                risk_probability=0.824,
                risk_level="High"
            )
            save_recommendations(a1.id, [
                {"category": "Iron-Rich Foods (Plant / Non-Heme)", "food": "Lentils, Chickpeas, Spinach, and Moringa Leaves", "reason": "Rich non-heme iron sources for vegetarian diet."},
                {"category": "Iron Absorption Enhancer", "food": "Amla, Guava, and Lemons", "reason": "Vitamin C enhances non-heme iron uptake."},
                {"category": "Absorption Inhibitor Awareness", "food": "Separate Tea/Coffee 1-2 Hours From Meals", "reason": "Tannins inhibit iron absorption."},
                {"category": "Clinical Consultation Notice", "food": "Gynecological Evaluation for Flow", "reason": "Heavy menstrual loss requires serum ferritin evaluation."}
            ])

            a2 = save_assessment(
                user_id=demo_user.id,
                assessment_data={
                    "age": 25, "height": 161.0, "weight": 53.5, "bmi": 20.64,
                    "heavy_menstrual_flow": 1, "pregnant": 0, "vegetarian": 1,
                    "iron_rich_food_frequency": "sometimes", "vitamin_c_frequency": "often",
                    "tea_coffee_with_meals": 0, "fatigue": 0, "dizziness": 0,
                    "weakness": 0, "shortness_of_breath": 0, "pale_skin": 0,
                    "previous_anemia": 1, "chronic_condition": 0
                },
                risk_probability=0.312,
                risk_level="Low"
            )
            save_recommendations(a2.id, [
                {"category": "Iron-Rich Foods (Plant / Non-Heme)", "food": "Sesame Seeds, Lentils, and Drumstick Leaves", "reason": "Sustaining daily plant iron intake."},
                {"category": "Maintenance", "food": "Fresh Citrus & Amla Dressing", "reason": "Maintain ascorbic acid to enhance non-heme iron uptake."}
            ])
            print("[+] Demo user and longitudinal assessment history seeded successfully.")

if __name__ == "__main__":
    init_database()
