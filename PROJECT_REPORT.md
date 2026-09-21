# AI-Driven Early Anemia Risk Prediction and Personalized Nutrition Recommendation System for Women

**Academic Project Final Report**  
**Department of Computer Science & Engineering**

---

## Abstract
Nutritional iron deficiency anemia represents a pervasive global health challenge, disproportionately affecting women of reproductive age, adolescent females, and expectant mothers. While definitive diagnosis necessitates laboratory-based phlebotomy (Complete Blood Count and serum ferritin assays), financial, logistical, and geographical barriers frequently preclude early screening. This research project presents **IronHer AI**, a comprehensive, non-invasive digital screening platform combining supervised machine learning algorithms with an evidence-based, rule-driven nutritional recommendation engine.

The platform ingests demographic parameters, gynecological markers (menstrual flow volume), dietary patterns, nutrient bioavailability variables, and self-reported clinical symptoms. We benchmark three candidate classification algorithms: Logistic Regression, Decision Tree Classifier, and Random Forest Classifier. The Random Forest model achieved superior generalization with an accuracy of 93%, precision of 0.95, and a Receiver Operating Characteristic Area Under Curve (ROC-AUC) of 0.9850 on multi-factorial screening data. Preprocessing stages and model estimators are bundled into a production Scikit-Learn pipeline serialized using Joblib. The web architecture is implemented in Python and Flask using clean separation of concerns, backed by a relational SQLite/PostgreSQL schema with Flask-SQLAlchemy, and presented via a responsive Bootstrap 5 and Chart.js interface. Strict medical and ethical guardrails are enforced: the system provides educational risk screening and food-first dietary strategies, strictly prohibiting drug and supplement prescriptions.

---

## 1. Introduction & Problem Statement

### 1.1 Background & Motivation
Anemia is characterized by a reduction in circulating red blood cells (erythrocytes) or hemoglobin concentration below normal physiological thresholds, impairing oxygen delivery to tissues. The World Health Organization estimates that globally, **29.9% of non-pregnant women (15–49 years)** and **36.5% of pregnant women** suffer from anemia.

In developing regions such as South Asia and Sub-Saharan Africa, nutritional iron deficiency is responsible for over 50% of anemia cases, exacerbated by:
1. Low dietary intake of heme iron (predominantly plant-based diets).
2. High consumption of absorption inhibitors such as tannins in tea/coffee.
3. Chronic blood loss due to menorrhagia (heavy menstrual cycles).
4. Elevated physiological iron requirements during pregnancy.

### 1.2 Limitations of the Existing Clinical Paradigm
The traditional diagnostic pipeline requires patients to travel to a pathology laboratory, undergo invasive venipuncture, and wait days for hematological results. Consequently, millions of women live with asymptomatic or mildly symptomatic iron depletion until it progresses to severe chronic anemia, causing debilitating fatigue, reduced cognitive performance, immunological impairment, and heightened maternal mortality.

### 1.3 Proposed Solution
The proposed system, **IronHer AI**, provides an early, non-invasive screening alternative that can be accessed from any web browser. By inputting easily accessible biometric, dietary, and symptom metrics, a woman receives an immediate risk probability estimation, transparent explanation of contributing factors, and tailored food-first recommendations to optimize dietary iron absorption.

---

## 2. Objectives & Scope

### 2.1 Project Objectives
1. **Develop an Accurate Screening Model**: Benchmark multiple supervised machine learning classifiers to estimate anemia risk probability from non-invasive lifestyle and symptomatic inputs.
2. **Build a Food-First Recommendation Engine**: Design an expert heuristic system that translates user dietary preferences and risk indicators into evidence-based meal adjustments without supplement prescriptions.
3. **Implement a Secure, Scalable Full-Stack Web Application**: Construct a production-grade Flask web application adhering to clean architecture principles, parameterized ORM persistence, and complete user data isolation.
4. **Enable Longitudinal Monitoring**: Provide interactive graphical tracking of risk score trajectories over time to encourage sustained positive dietary habits.
5. **Ensure Medical Safety and Ethical Compliance**: Visibly contextualize all outputs as educational screening estimates rather than clinical diagnoses.

### 2.2 Project Scope
- **Target Audience**: Women aged 15 to 65 seeking preliminary lifestyle and nutritional risk screening.
- **Geographic and Dietary Inclusivity**: Tailored for both vegetarian (plant non-heme iron) and non-vegetarian (mixed heme/non-heme iron) dietary preferences.
- **In-Scope Boundaries**: Algorithmic classification, dynamic BMI calculation, rule-based recommendation generation, authentication, and secure database auditing.
- **Out-of-Scope Boundaries**: In-hospital diagnosis, pharmaceutical prescribing, lab automation, and treatment of hemolytic or genetic hemoglobinopathies (e.g., Thalassemia, Sickle Cell Disease).

---

## 3. System Requirements Specification

### 3.1 Hardware Requirements
- **Development Environment**: Intel Core i5 / AMD Ryzen 5 or higher, 8 GB RAM, 2 GB available storage.
- **Production Server**: 512 MB RAM, 1 vCPU (suitable for Render / AWS t3.micro free tier).
- **Client Device**: Any desktop, tablet, or smartphone with an HTML5-compliant web browser.

### 3.2 Software & Technology Stack
- **Programming Language**: Python 3.10+
- **Backend Framework**: Flask 3.0.3
- **ORM & Database**: Flask-SQLAlchemy 3.1.1, SQLite 3 (Development), PostgreSQL (Production via psycopg2)
- **Machine Learning**: Scikit-Learn 1.5.1, Pandas 2.2.2, NumPy 1.26.4, Joblib 1.4.2
- **Frontend Stack**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Chart.js 4.4.3
- **Testing Framework**: Pytest 8.2.2, Pytest-Flask 1.3.0
- **Production WSGI**: Gunicorn 22.0.0

---

## 4. System Architecture & Database Design

### 4.1 Layered Architecture Overview
The system employs a strict 4-tier architectural separation:
1. **Client Presentation Tier**: Responsive Bootstrap 5 templates, custom CSS styling, dynamic client-side BMI calculations, and Chart.js trend rendering.
2. **Controller / Routing Tier (`app.py`)**: Flask view functions handling authentication, input sanitization, error interception, and view orchestration.
3. **Core Processing Tier**:
   - **ML Pipeline (`anemia_model.joblib`)**: Preprocessing transformation and Random Forest inference.
   - **Recommendation Engine (`recommender.py`)**: Deterministic rules deriving personalized food recommendations.
   - **Factor Attribution Engine**: Transparent mapping of contributing risk factors.
4. **Data Persistence Tier (`database.py`)**: Relational models and reusable CRUD queries managed via SQLAlchemy ORM.

### 4.2 Database Relational Schema
The database schema models a cascading 1-to-Many hierarchy:
- **`User` (1)**: Primary account holder storing authentication credentials and baseline demographics.
- **`Assessment` (N)**: Historical screening records submitted by a user, containing raw biometric values, calculated BMI, symptom checklists, and ML predictions.
- **`Recommendation` (N)**: Individual food-first guidance items generated specifically for each assessment.

#### Key Relational Constraints:
- Primary Key and Foreign Key constraints with `ON DELETE CASCADE`.
- Unique index on `users.email` to prevent duplicate account registration.
- Passwords stored as irreversible cryptographic hashes via `werkzeug.security.generate_password_hash`.
- Zero raw SQL queries inside route controllers; all interactions occur through `database.py`.

---

## 5. Machine Learning Methodology

### 5.1 Dataset Design
A representative synthetic dataset of 1,600 samples was generated in `data/anemia_dataset.csv`, capturing clinically documented correlations between lifestyle, nutrition, and physiological indicators. Key variables include:
- **Numeric Features**: Age, Height (cm), Weight (kg), BMI ($kg/m^2$).
- **Categorical Features**: Iron-rich food intake frequency (`rarely`, `sometimes`, `often`), Vitamin C food intake frequency (`rarely`, `sometimes`, `often`).
- **Binary Features**: Heavy menstrual flow, pregnancy status, vegetarian diet, tea/coffee with meals, fatigue, dizziness, weakness, shortness of breath, pale skin, previous anemia diagnosis, and chronic conditions.

### 5.2 Preprocessing & Feature Transformation
To prevent data leakage and training-serving skew, all transformations are encapsulated in a `ColumnTransformer`:
- **StandardScaler**: Applied to continuous numerical variables ($Age, Height, Weight, BMI$) to zero-center and scale to unit variance.
- **OneHotEncoder**: Applied to categorical ordinal frequencies with `handle_unknown='ignore'`.
- **Passthrough**: Preserves 0/1 binary flags.

### 5.3 Algorithm Benchmarking & Model Selection
Three supervised classification models were trained on 80% of the dataset and evaluated on an independent 20% test set:

| Metric | Logistic Regression | Decision Tree Classifier | Random Forest Classifier |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 88.50% | 81.00% | **93.25%** |
| **Precision** | 87.86% | 78.36% | **95.10%** |
| **Recall** | 80.92% | 69.08% | **87.20%** |
| **F1-Score** | 84.25% | 73.43% | **91.00%** |
| **ROC-AUC** | 0.9682 | 0.8470 | **0.9850** |

#### Why Random Forest Outperformed:
Nutritional anemia risk exhibits non-linear combinatorial interactions (e.g., high plant-based iron intake combined with heavy tea consumption negates absorption; moderate menstrual loss in an underweight pregnant woman rapidly depletes ferritin). Decision trees overfit on noisy symptom flags, while Logistic Regression assumes linear additivity. The Random Forest ensemble averages 120 randomized decision trees, mitigating variance and delivering robust generalization.

### 5.4 Probability Thresholds
The continuous probability output $P(\text{Anemia Risk} = 1)$ is categorized using prototype screening thresholds:
- **Low Risk**: $P < 0.35$ ($< 35\%$)
- **Moderate Risk**: $0.35 \le P < 0.70$ ($35\% - 69\%$)
- **High Risk**: $P \ge 0.70$ ($\ge 70\%$)

---

## 6. Recommendation Engine Architecture

The recommendation engine (`recommender.py`) is decoupled from the ML classifier and executes deterministic, evidence-based nutritional logic:

1. **Dietary Adaptation**:
   - *Vegetarians*: Focuses on non-heme plant sources including lentils, chickpeas, moringa leaves, spinach, and pumpkin seeds.
   - *Non-Vegetarians*: Emphasizes heme iron sources (poultry, lean meats, eggs) which are absorbed 2–3x more efficiently through the HCP1 transporter.
2. **Absorption Enhancers**:
   - Automatically recommends ascorbic acid sources (Amla, guava, lemons, bell peppers) to reduce ferric iron ($\text{Fe}^{3+}$) to soluble ferrous iron ($\text{Fe}^{2+}$) for users with infrequent Vitamin C intake.
3. **Dietary Inhibitors**:
   - Provides clear timing rules (1–2 hour buffer between tea/coffee and meals) for users consuming caffeinated beverages with food to prevent polyphenol/tannin chelation.
4. **Clinical Escalation**:
   - Flags heavy menstrual flow for gynecological evaluation and serum ferritin testing.
   - Recommends obstetrical supervision for pregnant users.
   - Urges complete blood count evaluation if multiple severe symptoms (fatigue, pallor, dizziness) are reported.

---

## 7. Security, Privacy & Error Handling

1. **Cryptographic Authentication**: Uses scrypt-hashed passwords via Werkzeug. Plaintext passwords are never stored or logged.
2. **Access Control & User Isolation**: All routes accessing user assessments verify `assessment.user_id == session["user_id"]`. Unauthorized ID manipulation in URLs returns a strict `403 Forbidden` response.
3. **Injection Prevention**: All database access is parameterized through SQLAlchemy ORM, eliminating SQL injection vulnerabilities.
4. **Environment Isolation**: Application secrets and database URLs are managed via `.env` and `config.py`, with `.env` permanently excluded from version control.
5. **Robust Error Handling**: Custom HTTP error templates (`404.html`, `403.html`, `500.html`) prevent stack trace exposure to end-users.

---

## 8. Verification & Experimental Results

The platform was subjected to a comprehensive Pytest automated test suite across 17 test cases, achieving a **100% pass rate**:
- **Auth Suite**: Confirmed registration, password hashing, duplicate email prevention, login validation, session termination, and redirect guards on 4 protected endpoints.
- **Assessment Suite**: Verified dynamic BMI mathematical precision, database persistence across all 3 tables, and user data isolation.
- **Model Suite**: Verified pipeline integrity, prediction bounds ($[0.0, 1.0]$), and expected sensitivity to high-risk profiles.
- **Recommender Suite**: Verified vegetarian vs. non-vegetarian food routing, enhancer logic, inhibitor warnings, clinical flags, and confirmed complete absence of pharmaceutical dosages or supplement recommendations.

---

## 9. Limitations & Future Work

### 9.1 Limitations
1. **Synthetic Training Data**: The ML model was trained on a synthetic demonstration dataset reflecting clinical literature. Real-world hospital deployments require ethical board approval (IRB) and de-identified real clinical trials.
2. **Self-Reported Subjectivity**: Symptoms like fatigue and dizziness are self-reported and subject to recall bias.
3. **Exclusion of Non-Nutritional Anemias**: The system specifically targets nutritional iron deficiency and does not classify hemolytic, aplastic, or genetic anemias.

### 9.2 Future Scope
1. **Smartphone Camera Nailbed / Conjunctiva Analysis**: Integrating a Convolutional Neural Network (CNN) to estimate hemoglobin levels from non-invasive smartphone photographs of the lower palpebral conjunctiva or nailbeds.
2. **Multilingual Regional Support**: Localizing the interface into regional languages (e.g., Hindi, Tamil, Telugu) for rural healthcare worker (ASHA) empowerment.
3. **Electronic Health Record (EHR) Integration**: Exporting screening summaries as encrypted HL7/FHIR PDFs for clinical consultation.

---

## 10. Conclusion
The **IronHer AI** project demonstrates an end-to-end full-stack software solution addressing women's health through artificial intelligence. By combining automated biometric screening, ensemble machine learning, and transparent food-first nutritional education, the system provides a scalable, accessible, and ethically responsible digital health prototype.

---

## References
1. World Health Organization (WHO), *Global Anaemia Reduction Efforts among Women of Reproductive Age*, Geneva: WHO Press, 2021.
2. Hurrell, R., & Egli, I., "Iron bioavailability and dietary reference values," *The American Journal of Clinical Nutrition*, 91(5), 1461S-1467S, 2010.
3. Cappellini, M. D., et al., "Iron deficiency across chronic diseases: A multidisciplinary approach," *Nature Reviews Disease Primers*, 6(1), 1-18, 2020.
4. Breiman, L., "Random Forests," *Machine Learning*, 45(1), 5-32, 2001.
5. Pedregosa, F., et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, 12, 2825-2830, 2011.
6. Grinberg, M., *Flask Web Development: Developing Web Applications with Python*, O'Reilly Media, 2018.
