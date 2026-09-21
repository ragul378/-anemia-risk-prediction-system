# AI-Driven Early Anemia Risk Prediction & Personalized Nutrition Recommendation System for Women

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0.3](https://img.shields.io/badge/framework-Flask%203.0-lightgrey.svg)](https://palletsprojects.com/p/flask/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Important Academic & Medical Notice**: This software is an academic engineering prototype developed for research and educational purposes. It is **NOT** a clinical diagnostic system. A clinical diagnosis of anemia requires laboratory evaluation (e.g., Complete Blood Count, Serum Ferritin) interpreted by a certified medical practitioner. This system never prescribes medication, supplements, or clinical dosages.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Capabilities](#key-capabilities)
3. [Technology Stack](#technology-stack)
4. [Project Directory Structure](#project-directory-structure)
5. [Step-by-Step Installation & Local Execution](#step-by-step-installation--local-execution)
6. [Machine Learning Pipeline](#machine-learning-pipeline)
7. [Running the Automated Test Suite](#running-the-automated-test-suite)
8. [Production Deployment (Render / PostgreSQL)](#production-deployment-render--postgresql)
9. [College Viva & Academic Demonstration Guide](#college-viva--academic-demonstration-guide)

---

## 1. Project Overview
Anemia remains a pervasive global public health crisis affecting more than 30% of non-pregnant women and 36% of pregnant women globally (WHO). In developing economies, nutritional iron deficiency accounts for the vast majority of cases.

**IronHer AI** provides an accessible, non-invasive early risk screening prototype. By evaluating demographic metrics, menstrual flow characteristics, dietary habits, and self-reported clinical symptoms, an ensemble machine learning model calculates an estimated anemia risk probability. The system then outputs transparent factor explanations alongside personalized, food-first nutritional education tailored to the woman's dietary preferences (vegetarian vs. non-vegetarian).

---

## 2. Key Capabilities
- **Non-Invasive Risk Estimation**: Combines 17 physiological and dietary features without requiring immediate phlebotomy.
- **Ensemble Machine Learning**: Evaluates Logistic Regression, Decision Trees, and Random Forest; wraps preprocessing and classification into an end-to-end serialized Scikit-Learn Pipeline (`anemia_model.joblib`).
- **Dynamic BMI Computation**: Real-time JavaScript calculation with proper centimeter-to-meter conversion ($BMI = \text{weight} / (\text{height}/100)^2$).
- **Rule-Based Food-First Recommender**: Tailors plant vs. animal iron sources, advises on Vitamin C enhancers, warns against dietary inhibitors (tea/coffee), and flags clinical alerts for heavy menstrual bleeding and pregnancy.
- **Longitudinal Trend Tracking**: Real-time Chart.js visualization mapping a user's risk trajectory over time.
- **Top-Right AI Nutrition Copilot**: Intelligent chatbot answering women's nutrition questions, explaining non-heme iron absorption biology, and enforcing strict clinical guardrails against drug/supplement prescriptions.
- **Per-User Isolation & Privacy**: Session-based auth, secure password hashing (scrypt/werkzeug), and URL tampering protection (`403 Forbidden` if attempting to view unauthorized records).

---

## 3. Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js.
- **Backend**: Python 3.10+, Flask 3.0 (Clean Layered Architecture).
- **Database**: SQLite (`instance/anemia.db`) for local development; automatic PostgreSQL support via `DATABASE_URL` for production.
- **ORM**: Flask-SQLAlchemy 3.1.
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib.
- **Testing**: Pytest, Pytest-Flask.
- **Server**: Gunicorn WSGI.

---

## 4. Project Directory Structure
```
anemia_prediction_system/
├── app.py                      # Flask application factory, controllers, and error handlers
├── config.py                   # Configuration environments (Dev, Testing, Production)
├── database.py                 # SQLAlchemy ORM models (User, Assessment, Recommendation) & reusable DB queries
├── init_db.py                  # Safe database table initialization (preserves data)
├── train_model.py              # Synthetic dataset generator, algorithm benchmarking, pipeline training & saving
├── evaluate_model.py           # Model evaluation metrics, ROC-AUC, classification report
├── recommender.py              # Rule-based food-first nutrition and clinical alert engine
├── requirements.txt            # Locked Python dependencies
├── Procfile                    # Gunicorn entry point for production
├── render.yaml                 # Infrastructure-as-code for Render deployment
├── .env.example                # Sample environment variables template
├── .gitignore                  # Git ignore rules for virtual environments and databases
├── README.md                   # Project documentation & runbook
├── PROJECT_REPORT.md           # Full academic research report
├── SYSTEM_ARCHITECTURE.md      # Mermaid system architecture flowchart
├── DATABASE_ER_DIAGRAM.md      # Mermaid Entity-Relationship diagram
├── VIVA_QUESTIONS.md           # 30+ Comprehensive Viva Voce questions & answers
├── PRESENTATION.md             # 15 Academic slide presentation deck
├── data/
│   └── anemia_dataset.csv      # Generated synthetic screening dataset (1,600 samples)
├── models/
│   └── anemia_model.joblib     # Preprocessing + Random Forest pipeline artifact
├── instance/
│   └── anemia.db              # SQLite development database
├── templates/                  # 14 Jinja2 templates (base, index, auth, dashboard, result, errors)
├── static/
│   ├── css/style.css           # Custom responsive styles & color palette
│   └── js/
│       ├── main.js             # Form validation & dynamic BMI calculation
│       └── dashboard.js        # Chart.js dynamic longitudinal line graph
└── tests/
    ├── conftest.py             # Pytest fixtures, test client, and isolated in-memory DB
    ├── test_auth.py            # Registration, login, logout, and protected routes tests
    ├── test_assessment.py      # Assessment submission, BMI math, and user data isolation tests
    ├── test_model.py           # ML pipeline prediction bounds and inference tests
    └── test_recommender.py     # Dietary recommendations and medical safety compliance tests
```

---

## 5. Step-by-Step Installation & Local Execution

Follow these exact terminal commands step-by-step to install and run the application locally:

### Step 5.1: Create and Activate a Python Virtual Environment
Open your terminal inside the project directory:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

*Explanation*: A virtual environment isolates project dependencies, preventing version conflicts with your system Python.

---

### Step 5.2: Install Required Dependencies
Install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

*Explanation*: Installs Flask, SQLAlchemy, Scikit-Learn, Pandas, NumPy, Joblib, Gunicorn, and Pytest.

---

### Step 5.3: Initialize the Database
Run the safe database setup script:

```bash
python init_db.py
```

*Explanation*: Creates the `instance/` folder and `anemia.db` SQLite database with `users`, `assessments`, and `recommendations` tables. Existing user data will **not** be dropped or erased.

---

### Step 5.4: Train and Compare the Machine Learning Models
Train and serialize the Random Forest pipeline:

```bash
python train_model.py
```

*Explanation*: 
1. Generates `data/anemia_dataset.csv` (1,600 synthetic patient records modeling physiological interactions).
2. Performs an 80/20 stratified train/test split.
3. Benchmarks **Logistic Regression**, **Decision Trees**, and **Random Forest** across Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
4. Serializes the winning ensemble pipeline (`StandardScaler` + `OneHotEncoder` + `RandomForestClassifier`) to `models/anemia_model.joblib`.

Optional Verification: Run `python evaluate_model.py` to inspect the classification report and confusion matrix.

---

### Step 5.5: Start the Flask Application
Launch the local development server:

```bash
python app.py
```

*Explanation*: Starts Flask on `http://127.0.0.1:5000` with debug mode enabled.

---

### Step 5.6: Open in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

1. Click **Sign Up** to create an account (`test@example.com` / `password123`).
2. You will be automatically redirected to your **Dashboard**.
3. Click **Start Screening Assessment** to enter biometric metrics, dietary patterns, and symptoms.
4. View your **Estimated Risk Probability**, **Model Factors Considered**, and **Personalized Food Recommendations**.
5. Observe how subsequent assessments dynamically populate the **Longitudinal Risk Trend Chart** on your Dashboard!

---

## 6. Machine Learning Pipeline
The machine learning architecture wraps data transformation and inference into an immutable Scikit-Learn `Pipeline`:

$$\text{Raw Features} \xrightarrow{\text{ColumnTransformer}} \left[\text{StandardScaler}(\text{Numeric}) + \text{OneHotEncoder}(\text{Categorical}) + \text{Passthrough}(\text{Binary})\right] \xrightarrow{} \text{RandomForestClassifier}$$

### Prototype Risk Probability Thresholds:
- **Low Risk**: Estimated probability $< 0.35$ ($< 35\%$)
- **Moderate Risk**: Estimated probability between $0.35$ and $0.69$ ($35\% - 69\%$)
- **High Risk**: Estimated probability $\ge 0.70$ ($\ge 70\%$)

---

## 7. Running the Automated Test Suite
Execute the comprehensive Pytest verification suite:

```bash
python -m pytest tests -v
```

### Verified Test Cases (17 Tests, 100% Pass Rate):
- `test_auth.py`: User registration, password hashing verification, duplicate email prevention, password mismatch handling, session login, logout, and protected route access control.
- `test_assessment.py`: Metric BMI computation check ($kg/m^2$), assessment persistence, prediction generation, recommendation persistence, and user isolation (`403 Forbidden` check).
- `test_model.py`: Pipeline existence, feature input schema verification, prediction bounds ($[0.0, 1.0]$), and contrasting profile sensitivity.
- `test_recommender.py`: Vegetarian vs. non-vegetarian food routing, vitamin C enhancer logic, tannin inhibitor warnings, maternal/menorrhagia clinical notices, and non-negotiable **medical safety verification** (asserting no supplements, medications, or dosages are ever outputted).

---

## 8. Production Deployment (Render / PostgreSQL)

### Deploying to Render
1. Push your repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Complete Anemia Risk Prediction & Nutrition System"
   git remote add origin https://github.com/your-username/anemia-prediction-system.git
   git push -u origin main
   ```
2. Log in to [Render.com](https://render.com) and click **New +** &rarr; **Blueprint**.
3. Connect your GitHub repository. Render will automatically detect `render.yaml`.
4. Render will create:
   - A **PostgreSQL Database** instance (`anemia_db`).
   - A **Python Web Service** executing:
     - Build Command: `pip install -r requirements.txt && python train_model.py && python init_db.py`
     - Start Command: `gunicorn app:app`
5. In your Web Service environment variables on Render, set `DATABASE_URL` to your PostgreSQL internal connection string. Our `config.py` automatically normalizes `postgres://` to `postgresql://` for SQLAlchemy 2.0+ compliance!

---

## 9. College Viva & Academic Demonstration Guide

When presenting this project to examiners, follow this 4-minute demonstration flow:

1. **The Motivation (1 min)**:
   - State the WHO statistic on anemia prevalence among women.
   - Clarify the core value proposition: Non-invasive early risk screening and education prior to severe deficiency.
   - Point out the **Medical Disclaimer Ribbon**: Emphasize that the system provides educational screening and food-first recommendations, never medical prescriptions or supplements.

2. **The Architecture (1 min)**:
   - Highlight the **Clean Layered Architecture**: Routes in `app.py` handle HTTP requests; all database logic is encapsulated in `database.py`; recommendation rules reside in `recommender.py`.
   - Explain the Database Model: `User (1) -> Assessment (N) -> Recommendation (N)` with foreign key cascade deletion and strict user isolation.

3. **The ML Pipeline (1 min)**:
   - Discuss model selection: Show that you compared **Logistic Regression**, **Decision Trees**, and **Random Forest**.
   - Explain why Random Forest was selected: It captures non-linear interactions between heavy menstrual flow, plant-based diets, and symptoms without overfitting.
   - Explain the end-to-end `Pipeline` saved via Joblib to prevent training-serving skew.

4. **Live System Demonstration (1 min)**:
   - Register a new user and show the Dashboard.
   - Enter an assessment with heavy menstrual flow, vegetarian diet, tea with meals, and fatigue.
   - Show how the model predicts **Elevated Risk**, presents **Factors Considered**, and persists **Tailored Plant Iron + Vitamin C Recommendations**.
   - Show how the **Longitudinal Trend Graph** updates automatically.
   - Demonstrate **Security**: Log in with User B, attempt to navigate to User A's `/result/1` URL, and show the **403 Forbidden Access Denied** screen.
   - Show `python -m pytest tests -v` passing all 17 tests.
