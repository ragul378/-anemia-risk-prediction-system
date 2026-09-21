# Comprehensive Viva Voce Questions & Answers (30+ Q&A)

**Project**: AI-Driven Early Anemia Risk Prediction and Personalized Nutrition Recommendation System for Women  
**Domain**: Full-Stack Web Development, Machine Learning, Applied Health Informatics

---

### Section 1: Flask, Architecture & Web Engineering

#### Q1: What is the architectural pattern followed in this Flask project?
**Answer**: The project follows a **Clean Layered Architecture (Model-View-Controller adaptation)**:
- **Presentation / Views (`templates/`)**: Jinja2 templates rendering semantic HTML, CSS, and Chart.js.
- **Controllers / Routing (`app.py`)**: Flask view functions handling HTTP methods (GET/POST), request parsing, session checks, and view transitions.
- **Service Layer (`recommender.py`, ML pipeline)**: Pure Python business logic performing probability inference and nutrition rule mapping.
- **Persistence Layer (`database.py`)**: SQLAlchemy models and reusable CRUD functions. Routes never contain inlined raw SQL queries.

#### Q2: What is an Application Factory in Flask and why is it used?
**Answer**: An Application Factory is a function (here `create_app(config_name)`) that instantiates and configures the Flask application object. It allows creating multiple app instances with distinct configurations (e.g., `TestingConfig` with an in-memory SQLite database during Pytest vs. `DevelopmentConfig` or `ProductionConfig`), preventing global state leaks and facilitating isolated automated testing.

#### Q3: How is user authentication implemented without external heavy dependencies?
**Answer**: Authentication is implemented using **Flask session-based authentication**:
- Upon registration/login, user identity is verified against a salted password hash.
- On successful verification, the user's primary key (`session["user_id"]`) and name are stored inside Flask's cryptographically signed, client-side session cookie.
- A custom Python decorator (`@login_required`) wraps protected routes (`/dashboard`, `/assessment`, `/history`, `/profile`), redirecting unauthenticated requests to `/login`.
- Logging out calls `session.clear()`, invalidating the session.

#### Q4: What does the `@app.context_processor` decorator do in our application?
**Answer**: It injects global variables into all Jinja2 templates automatically. In our app, `inject_current_user()` retrieves the current logged-in user object from the database using `session.get("user_id")` and makes `current_user` universally accessible across `base.html` and child templates without passing it manually from every route.

#### Q5: How are HTTP errors handled to prevent raw traceback leakage?
**Answer**: Custom error handlers (`@app.errorhandler(404)`, `@app.errorhandler(403)`, `@app.errorhandler(500)`) intercept exceptions and render polished, user-friendly HTML error pages (`404.html`, `403.html`, `500.html`). In the 500 handler, `db.session.rollback()` is explicitly invoked to release any failed database transaction locks.

---

### Section 2: Database Design, SQLAlchemy & Migrations

#### Q6: Explain the database schema and its entity relationships.
**Answer**: The schema consists of three normalized tables:
- **`User (1)`** $\to$ **`Assessment (N)`**: One user can undergo multiple longitudinal assessments. Linked via `user_id` foreign key with `ondelete="CASCADE"`.
- **`Assessment (1)`** $\to$ **`Recommendation (N)`**: Each assessment generates a collection of personalized dietary items. Linked via `assessment_id` foreign key with `ondelete="CASCADE"`.
This enforces relational integrity: deleting a user automatically cleans up all associated assessments and recommendations.

#### Q7: How does the application achieve database portability between SQLite and PostgreSQL?
**Answer**: Through **Flask-SQLAlchemy abstraction** and environment variable detection in `config.py`:
- In local development, if `DATABASE_URL` is unset, it defaults to a local SQLite database at `instance/anemia.db`.
- In production (e.g., Render), setting `DATABASE_URL=postgresql://user:pass@host:port/dbname` switches the engine to PostgreSQL without modifying a single line of application code.
- `config.py` also normalizes legacy `postgres://` prefixes to `postgresql://` as required by modern SQLAlchemy 2.0+.

#### Q8: What is the purpose of `init_db.py`?
**Answer**: `init_db.py` creates the required SQLite/PostgreSQL tables using `db.create_all()` within the Flask application context. It checks if tables already exist and will **not** drop or wipe existing user records, making it safe to run in deployment pipelines.

#### Q9: Why is user data isolation critical, and how is it enforced?
**Answer**: Medical screening data is sensitive personal information. If User A could view User B's screening by changing the URL to `/result/2`, this would be an **Insecure Direct Object Reference (IDOR)** vulnerability. In `app.py`, the `result()` route explicitly asserts:
`if assessment_record.user_id != session["user_id"]: abort(403)`
If an unauthorized user attempts to view a record, the server immediately returns a `403 Forbidden` response.

---

### Section 3: Password Hashing & Security

#### Q10: How are passwords secured in the database?
**Answer**: Passwords are never stored in plaintext. When a user registers, `werkzeug.security.generate_password_hash()` hashes the password using **scrypt** (or pbkdf2:sha256) with a cryptographic salt. During login, `check_password_hash(user.password_hash, candidate_password)` compares the candidate against the stored hash in constant time, preventing timing attacks.

#### Q11: How does the application prevent SQL Injection?
**Answer**: The application strictly uses **SQLAlchemy Object Relational Mapping (ORM)** and parameterized queries. User inputs from forms are treated as data parameters rather than executable SQL strings, making SQL injection impossible.

#### Q12: How is the application protected against secret leakage?
**Answer**: `SECRET_KEY` and `DATABASE_URL` are loaded from environment variables using `python-dotenv`. The `.env` file containing secrets is added to `.gitignore`. A `.env.example` template with dummy values is committed for team onboarding.

---

### Section 4: Machine Learning Concepts & Preprocessing

#### Q13: Why is this labeled a "synthetic" dataset, and why is that appropriate for this project?
**Answer**: Clinical healthcare datasets require Institutional Review Board (IRB) ethical approvals and strict HIPAA/GDPR de-identification. For an academic prototype, generating a clearly labeled synthetic dataset based on published clinical correlations allows rigorous software engineering, model comparison, and pipeline verification without ethical or patient privacy breaches.

#### Q14: What features are used in the ML model?
**Answer**: The model utilizes 17 features:
1. **Continuous Biometrics**: Age, Height, Weight, BMI.
2. **Physiological Factors**: Heavy menstrual bleeding (menorrhagia), pregnancy status.
3. **Dietary Patterns**: Vegetarian status, iron-rich food frequency, vitamin C frequency, tea/coffee with meals.
4. **Clinical Symptoms**: Fatigue, dizziness, weakness, shortness of breath, pale skin/conjunctiva.
5. **Medical History**: Previous anemia diagnosis, chronic health condition.

#### Q15: How are numerical and categorical features preprocessed?
**Answer**: Using Scikit-Learn's `ColumnTransformer`:
- **Numerical Features** ($Age, Height, Weight, BMI$): Scaled using `StandardScaler` ($\mu=0, \sigma=1$) to prevent features with large absolute ranges (e.g., height) from dominating gradient calculations.
- **Categorical Features** (food frequencies): Encoded using `OneHotEncoder(handle_unknown='ignore')` to convert text categories into binary indicator vectors.
- **Binary Features**: Passed through directly as 0/1 integers.

#### Q16: What is training-serving skew, and how does the pipeline prevent it?
**Answer**: Training-serving skew occurs when data transformations applied during model training differ from the transformations applied during live web inference. We prevent this by wrapping both the `ColumnTransformer` and the classifier into a single `sklearn.pipeline.Pipeline` serialized to `anemia_model.joblib`. The web application passes the raw user dictionary into `pipeline.predict_proba()`, guaranteeing identical transformations.

---

### Section 5: Algorithms, Evaluation Metrics & Overfitting

#### Q17: Which three machine learning algorithms were compared, and why?
**Answer**:
1. **Logistic Regression**: A linear baseline estimating class probabilities via the sigmoid function. Highly interpretable, but assumes linear relationships.
2. **Decision Tree Classifier**: A non-linear tree partitioner using Gini impurity. Intuitive, but prone to high variance and overfitting on noisy symptom data.
3. **Random Forest Classifier**: An ensemble of randomized decision trees using bagging and feature subspace sampling. It reduces variance, captures complex dietary-symptom interactions, and generalizes well.

#### Q18: What are Accuracy, Precision, Recall, and F1-Score?
**Answer**:
- **Accuracy**: $\frac{TP + TN}{TP + TN + FP + FN}$ (Overall proportion of correct predictions).
- **Precision**: $\frac{TP}{TP + FP}$ (Out of all predicted elevated-risk cases, how many were truly at risk).
- **Recall (Sensitivity)**: $\frac{TP}{TP + FN}$ (Out of all actual elevated-risk cases, how many did the model detect).
- **F1-Score**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ (Harmonic mean balancing Precision and Recall).

#### Q19: In medical risk screening, why is Recall typically favored over Precision?
**Answer**: A **False Negative (FN)** means a woman with iron deficiency is told she has low risk, delaying care and allowing anemia to progress. A **False Positive (FP)** merely prompts a healthy woman to eat more lentils, citrus fruits, or request a routine blood check. Because missing a sick patient has higher clinical risk, high Recall (sensitivity) is paramount.

#### Q20: What is ROC-AUC, and what does an ROC-AUC of 0.9850 signify?
**Answer**: The **Receiver Operating Characteristic Area Under Curve (ROC-AUC)** measures the model's ability to rank positive instances higher than negative instances across all possible classification thresholds. An ROC-AUC of 0.9850 means there is a 98.5% probability that the model will assign a higher risk probability to a randomly chosen anemic individual than to a healthy individual.

#### Q21: What is a Confusion Matrix, and what are its four quadrants?
**Answer**: A confusion matrix tabulates actual vs. predicted classes:
- **True Negatives (TN)**: Healthy individuals correctly predicted as Low Risk.
- **False Positives (FP)**: Healthy individuals incorrectly flagged as Elevated Risk (Type I Error).
- **False Negatives (FN)**: Anemic individuals incorrectly flagged as Low Risk (Type II Error).
- **True Positives (TP)**: Anemic individuals correctly flagged as Elevated Risk.

#### Q22: What techniques were used to prevent overfitting?
**Answer**:
1. **Ensemble Averaging**: Random Forest averages predictions across 120 trees, canceling out individual tree variance.
2. **Tree Depth Constraints**: Setting `max_depth=7` and `min_samples_split=10` prevents individual trees from memorizing training noise.
3. **Stratified Train-Test Split**: Using `train_test_split(..., stratify=y)` preserves class proportions across training (80%) and test (20%) partitions.

---

### Section 6: Recommendation Engine & Nutritional Science

#### Q23: Why is the recommendation engine rule-based rather than machine learning-based?
**Answer**: Machine learning models can hallucinate or produce unpredictable recommendations when trained on sparse dietary data. Rule-based systems provide **deterministic, audited, and explainable** medical advice. Nutritional rules grounded in biochemistry (e.g., separating tannins from iron meals) must always execute reliably without probabilistic drift.

#### Q24: What is the biological difference between heme and non-heme iron?
**Answer**:
- **Heme Iron**: Found in animal flesh (poultry, meat, fish). Bound within a porphyrin ring and absorbed via the Heme Carrier Protein 1 (HCP1) with 15%–35% absorption efficiency. Unaffected by dietary inhibitors.
- **Non-Heme Iron**: Found in plants (lentils, spinach, seeds, beans) in the insoluble ferric ($\text{Fe}^{3+}$) state. Absorbed via DMT1 with 2%–20% efficiency, and highly sensitive to enhancers (Vitamin C) and inhibitors (tannins, phytates).

#### Q25: What is the biochemical mechanism of Vitamin C in enhancing non-heme iron absorption?
**Answer**: Vitamin C (ascorbic acid) acts as an electron donor, reducing insoluble ferric iron ($\text{Fe}^{3+}$) to soluble ferrous iron ($\text{Fe}^{2+}$). Ferrous iron readily binds to the Divalent Metal Transporter 1 (DMT1) in duodenal enterocytes. Additionally, ascorbic acid forms a soluble chelate that prevents iron from precipitating at the alkaline pH of the duodenum.

#### Q26: Why does drinking tea or coffee with meals reduce iron uptake?
**Answer**: Tea and coffee contain polyphenolic compounds, specifically **tannins and chlorogenic acid**. These molecules chelate non-heme iron, forming insoluble iron-tannate precipitates that cannot be absorbed by the intestinal brush border. Recommending a 60–90 minute separation restores baseline absorption.

---

### Section 7: Medical Safety, Ethics & Limitations

#### Q27: What strict medical safety rules are embedded in the software?
**Answer**:
1. **Clear Terminology**: It is labeled an **"educational screening prototype"** and "risk estimate", never a medical diagnosis.
2. **No Supplements or Medications**: The system **never** prescribes iron supplements (e.g., ferrous sulfate, ferrous fumarate), injections, or dosages, as unsupervised iron supplementation can cause iron overload (hemochromatosis) or organ toxicity.
3. **Prominent Disclaimers**: Displayed across the top navigation bar, assessment form, result page, and nutrition guide.
4. **Clinical Escalation**: Flags heavy menstrual bleeding, pregnancy, and chronic symptoms for formal physician consultation.

#### Q28: What are the primary limitations of this academic project?
**Answer**:
1. The ML model was trained on synthetic data modeled after clinical distributions, rather than hospital electronic health records.
2. Symptoms like fatigue, dizziness, and pallor are self-reported and subject to user perception.
3. The platform addresses nutritional iron deficiency and does not detect genetic hemoglobinopathies such as Thalassemia or Sickle Cell Anemia.

---

### Section 8: Testing, DevOps & Deployment

#### Q29: How was the test suite designed and executed?
**Answer**: The test suite was built using **Pytest** and **Pytest-Flask** across 4 modules (`test_auth.py`, `test_assessment.py`, `test_model.py`, `test_recommender.py`), verifying 17 test cases:
- In-memory database fixtures in `conftest.py` ensure test isolation.
- Tests verify password hashing, duplicate email handling, session access controls, 403 authorization guards, metric BMI calculation, ML model probability bounds, and confirm that zero pharmaceutical keywords exist in recommendation outputs.

#### Q30: What files enable production deployment on Render?
**Answer**:
- `requirements.txt`: Locked dependency versions.
- `Procfile`: Declares the WSGI process `web: gunicorn app:app`.
- `render.yaml`: Infrastructure-as-code specifying build commands (`pip install -r requirements.txt && python train_model.py && python init_db.py`), web server execution, environment variables, and managed PostgreSQL integration.
- `config.py`: Automatically swaps from SQLite to PostgreSQL when `DATABASE_URL` is set.

---

### Section 9: Conversational AI & Guardrails

#### Q31: How is the Top-Right "IronHer AI Nutrition Copilot" implemented?
**Answer**: The chatbot is implemented using a **hybrid biomedical NLP engine** in `ai_chat.py`:
- It features an intelligent local pattern-matching and heuristic biomedical knowledge base that works **100% offline** without requiring external API keys during college presentations.
- It also supports seamless cloud LLM integration (Google Gemini API via `GEMINI_API_KEY` in `.env`).
- In the frontend, it is positioned as a sleek floating button and sliding dialog in the top-right corner of the layout, complete with suggested quick questions, asynchronous `fetch('/api/chat')` communication, and markdown formatting.

#### Q32: What guardrails prevent the AI Chatbot from generating dangerous medical advice?
**Answer**: The chatbot implements strict **Clinical Guardrail Enforcement**:
- If a user asks questions like *"How many mg iron pills should I take?"* or *"Prescribe ferrous sulfate"*, the engine detects medication/dosage trigger keywords and immediately responds with a clinical refusal guardrail.
- It explains that therapeutic iron supplementation can cause toxicity without formal laboratory tests (CBC, Ferritin) and redirects the user to food-first alternatives (lentils, spinach, amla, citrus).
- This is reinforced through unit tests in `tests/test_chat.py` which assert that no pharmaceutical dosages or supplement prescriptions are ever outputted.

