# Database Entity-Relationship (ER) Diagram

## Overview
The **IronHer AI** database schema follows a normalized relational structure enforcing 1-to-Many cascade relationships:
`User (1) ───< Assessment (N) ───< Recommendation (N)`

```mermaid
erDiagram
    USERS ||--o{ ASSESSMENTS : "submits"
    ASSESSMENTS ||--o{ RECOMMENDATIONS : "generates"

    USERS {
        int id PK "Primary Key, Auto-increment"
        string name "Full Name"
        string email "Unique, Indexed"
        string password_hash "Werkzeug / Scrypt Hash"
        int age "Demographic age (years)"
        float height "Height in centimeters"
        float weight "Weight in kilograms"
        string dietary_preference "Vegetarian / Non-Vegetarian / Vegan"
        datetime created_at "Timestamp (UTC)"
        datetime updated_at "Timestamp (UTC)"
    }

    ASSESSMENTS {
        int id PK "Primary Key, Auto-increment"
        int user_id FK "Foreign Key -> USERS.id (CASCADE)"
        int age "Age at time of assessment"
        float height "Height (cm)"
        float weight "Weight (kg)"
        float bmi "Calculated BMI (kg/m^2)"
        boolean heavy_menstrual_flow "Menorrhagia flag"
        boolean pregnant "Pregnancy status flag"
        boolean vegetarian "Plant-based diet flag"
        string iron_rich_food_frequency "rarely | sometimes | often"
        string vitamin_c_frequency "rarely | sometimes | often"
        boolean tea_coffee_with_meals "Absorption inhibitor flag"
        boolean fatigue "Symptom: Chronic fatigue"
        boolean dizziness "Symptom: Dizziness / lightheadedness"
        boolean weakness "Symptom: Muscle weakness"
        boolean shortness_of_breath "Symptom: Dyspnea on exertion"
        boolean pale_skin "Symptom: Pallor in skin/eyelids"
        boolean previous_anemia "Clinical history: Previous anemia"
        boolean chronic_condition "Clinical history: Chronic illness"
        float risk_probability "Model output [0.0 - 1.0]"
        string risk_level "Low | Moderate | High"
        datetime created_at "Timestamp (UTC), Indexed"
    }

    RECOMMENDATIONS {
        int id PK "Primary Key, Auto-increment"
        int assessment_id FK "Foreign Key -> ASSESSMENTS.id (CASCADE)"
        string category "Dietary / Enhancer / Inhibitor / Clinical"
        string food "Target food item or clinical action"
        text reason "Evidence-based rationale"
        datetime created_at "Timestamp (UTC)"
    }
```

## Relational Integrity & Schema Guarantees
1. **User Isolation**: Every assessment has a mandatory `user_id` foreign key with cascade deletion. Query scopes are strictly filtered by `user_id = session["user_id"]`.
2. **Audit Preservation**: Assessments are append-only. When a user updates their profile, existing historical assessments remain intact with the biometric values recorded at screening time.
3. **Database Portability**: The schema uses standard ANSI types compatible with SQLite for local development and PostgreSQL (e.g., Render, AWS RDS, Supabase) for cloud production.
