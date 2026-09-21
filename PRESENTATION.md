# Project Presentation Slide Deck (15 Slides)

**Project Title**: AI-Driven Early Anemia Risk Prediction and Personalized Nutrition Recommendation System for Women  
**Academic Presentation**: Final Year Capstone Defense

---

### Slide 1: Title Slide
- **Title**: AI-Driven Early Anemia Risk Prediction & Personalized Nutrition Recommendation System for Women
- **Sub-Title**: A Non-Invasive Digital Health Screening & Food-First Advisory Platform
- **Domain**: Machine Learning, Web Engineering, Healthcare Informatics
- **Technology Stack**: Python, Flask, Scikit-Learn, SQLAlchemy, Bootstrap 5, Chart.js

---

### Slide 2: Introduction & Motivation
- **Global Health Challenge**: Anemia is a worldwide condition affecting oxygen-carrying capacity in the blood.
- **Disproportionate Impact**: WHO reports **29.9% of non-pregnant women** and **36.5% of pregnant women** are affected globally.
- **Primary Etiology**: Nutritional iron deficiency accounts for >50% of cases in developing economies.
- **Project Vision**: Provide an early, digital, non-invasive risk screening mechanism that prompts timely medical consultation and dietary adjustments.

---

### Slide 3: Problem Statement & Existing Limitations
- **Current Practice**: Diagnostic confirmation depends on venous blood draws (Complete Blood Count, Serum Ferritin).
- **Bottlenecks**:
  - High testing costs and rural healthcare access deficits.
  - Phlebotomy anxiety and lack of symptom awareness.
  - Patients often present late when severe chronic anemia has already caused physical/cognitive exhaustion.
- **Opportunity**: Use machine learning to evaluate accessible physiological, dietary, and symptomatic markers before severe clinical manifestation.

---

### Slide 4: Proposed System
- **Non-Invasive AI Screening**: Evaluates 17 self-reported biological, lifestyle, and clinical features.
- **Ensemble Machine Learning**: Leverages Random Forest to output a continuous risk probability and tiered category (Low / Moderate / High).
- **Personalized Food-First Guidance**: Deterministic rule engine providing meal plans tailored to vegetarian or non-vegetarian habits.
- **Longitudinal Tracking**: Interactive Chart.js timeline allowing women to track their risk trajectory.
- **Strict Ethical Boundaries**: Visible screening disclaimers; zero drug or supplement prescriptions.

---

### Slide 5: Project Objectives
1. Build an end-to-end web platform following clean layered software architecture.
2. Train and benchmark three supervised ML models (Logistic Regression, Decision Trees, Random Forest).
3. Serialize an immutable preprocessing and prediction pipeline using Joblib.
4. Implement a deterministic dietary recommendation engine centered on bioavailable iron and Vitamin C.
5. Guarantee complete user data isolation, password encryption, and robust error handling.

---

### Slide 6: System Architecture & Data Flow
- **4-Tier Architecture**:
  - **Client**: HTML5, CSS3, JavaScript (dynamic metric BMI), Bootstrap 5, Chart.js.
  - **Application Controller**: Flask 3.0 routing, `@login_required` middleware, custom error handling.
  - **Core Logic**: Scikit-Learn pipeline (`anemia_model.joblib`), `recommender.py`, factor explainability.
  - **Persistence**: Relational models in `database.py` with SQLAlchemy ORM (SQLite / PostgreSQL).
- **Data Flow**: Form Input $\to$ Metric BMI $\to$ ML Pipeline $\to$ Probability & Category $\to$ Rule Engine $\to$ Database Persistence $\to$ Result Page & Dashboard.

---

### Slide 7: Database Design & Entity Relationships
- **Normalized Relational Schema**: `User (1) ───< Assessment (N) ───< Recommendation (N)`
- **Key Tables**:
  - **`users`**: ID, Name, Unique Email, Password Hash (scrypt), Baseline Demographics.
  - **`assessments`**: User FK (CASCADE), Biometrics, Menstrual Flow, Diet, Symptoms, Model Probability, Risk Tier.
  - **`recommendations`**: Assessment FK (CASCADE), Category, Food Item, Rationale.
- **Data Isolation**: Query filters enforce `user_id == session['user_id']`. Unauthorized access triggers `403 Forbidden`.

---

### Slide 8: Machine Learning Methodology
- **Dataset**: 1,600 synthetic records capturing physiological correlations (iron intake, menorrhagia, pregnancy, symptoms).
- **Preprocessing via `ColumnTransformer`**:
  - `StandardScaler`: Continuous variables ($Age, Height, Weight, BMI$).
  - `OneHotEncoder`: Categorical frequencies (iron intake, Vitamin C intake).
  - `Passthrough`: Binary clinical flags (0/1).
- **Pipeline Architecture**: Both transformer and estimator wrapped in one pipeline to eliminate training-serving skew.

---

### Slide 9: Model Comparison & Benchmark Results
- **Evaluation on 20% Stratified Test Partition**:

| Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression | 88.50% | 87.86% | 80.92% | 84.25% | 0.9682 |
| Decision Tree | 81.00% | 78.36% | 69.08% | 73.43% | 0.8470 |
| **Random Forest (Selected)** | **93.25%** | **95.10%** | **87.20%** | **91.00%** | **0.9850** |

- **Selection Rationale**: Random Forest captures complex non-linear feature interactions between diet, menstruation, and symptoms while preventing single-tree overfitting.

---

### Slide 10: Risk Prediction & Factor Attribution
- **Prototype Risk Probability Thresholds**:
  - **Low Risk**: Probability $< 0.35$ ($< 35\%$).
  - **Moderate Risk**: Probability between $0.35$ and $0.69$ ($35\% - 69\%$).
  - **High Risk**: Probability $\ge 0.70$ ($\ge 70\%$).
- **Transparent Explainability**: Result page presents "Factors Considered by the Model" (e.g., Heavy Menstrual Flow, Plant-Based Diet, Low Vitamin C, Fatigue) without claiming direct causality.

---

### Slide 11: Food-First Recommendation Engine
- **Engine Logic (`recommender.py`)**:
  - **Vegetarian**: Recommends lentils, chickpeas, moringa leaves, pumpkin seeds, and spinach.
  - **Non-Vegetarian**: Emphasizes heme iron sources (poultry, eggs, lean meats) with higher bioavailability.
  - **Vitamin C Enhancers**: Suggests amla, guava, and lemons to reduce $\text{Fe}^{3+}$ to absorbable $\text{Fe}^{2+}$.
  - **Dietary Inhibitors**: Guides spacing tea/coffee 60–90 minutes away from meals to prevent tannin chelation.
  - **Clinical Alerts**: Recommends medical consultation for heavy bleeding, pregnancy, or persistent fatigue.
  - **Medical Safety Rule**: Zero supplements, medications, or clinical dosages.

---

### Slide 12: Dynamic Dashboard & Interactive Trends
- **Live User Summary**: Total assessments, latest risk probability, current risk tier, and average historical risk.
- **Chart.js Trend Visualization**:
  - Plots longitudinal line graph of risk probability over time.
  - Dynamically fetches user data points via `/api/user/trends`.
  - Gradient stroke and fill with responsive tooltip hover states.
- **Recent Snapshot**: Direct link to historical recommendation plans.

---

### Slide 13: Security, Privacy & Quality Assurance
- **Security Protections**:
  - Werkzeug / Scrypt password hashing (never plaintext).
  - CSRF protection and session-based authentication.
  - Parameterized ORM queries preventing SQL injection.
  - IDOR prevention with strict `403 Forbidden` verification.
- **Automated Verification**:
  - 17 Pytest test cases executed across authentication, prediction, persistence, access control, and safety rules.
  - **100% Pass Rate**.

---

### Slide 14: Limitations & Future Enhancements
- **Current Limitations**:
  - ML pipeline trained on synthetic demonstration data modeled on clinical literature.
  - Self-reported symptoms are subject to user perception and recall bias.
  - Only screens for nutritional iron deficiency; excludes hemoglobinopathies (Thalassemia).
- **Future Roadmap**:
  - Computer Vision module to estimate hemoglobin from smartphone photos of the lower eyelid (conjunctiva).
  - Localization into regional languages for rural healthcare workers (e.g., ASHA workers in India).
  - Exporting encrypted clinical reports in HL7/FHIR format for hospital integration.

---

### Slide 15: Conclusion & Key Takeaways
- **Holistic Academic Solution**: Successfully integrated Machine Learning, Web Engineering, Database Design, and Clinical Informatics.
- **Actionable Impact**: Bridges the gap between passive symptom neglect and active clinical engagement through non-invasive screening and food-first education.
- **Engineering Rigor**: 100% test pass rate, modular clean architecture, zero hardcoded secrets, and dual-database compatibility (SQLite / PostgreSQL).
- **Thank You**: Questions & Discussion.
