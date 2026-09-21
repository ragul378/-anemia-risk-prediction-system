"""AI-Driven Early Anemia Risk Prediction and Personalized Nutrition Recommendation System.

Clean Architecture:
- Routes only handle HTTP request parsing, authentication checks, validation, and view rendering.
- All database operations are mediated through reusable functions in database.py.
- Recommendation generation is managed through recommender.py.
- Model inference is encapsulated in an isolated helper loading models/anemia_model.joblib.
"""

import os
import importlib.metadata
import werkzeug
import joblib
import pandas as pd
from functools import wraps
from pathlib import Path

# Ensure werkzeug.__version__ compatibility with Flask test client and extensions
if not hasattr(werkzeug, "__version__"):
    try:
        werkzeug.__version__ = importlib.metadata.version("werkzeug")
    except Exception:
        werkzeug.__version__ = "3.1.3"

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    jsonify
)

from config import config_by_name
from database import (
    db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    save_assessment,
    save_recommendations,
    get_user_assessments,
    get_assessment_by_id,
    get_dashboard_stats
)
from recommender import generate_recommendations, get_factors_considered
from ai_chat import generate_chat_response

# Cached ML Pipeline
_model_pipeline = None


def get_model_pipeline(model_path: Path):
    """Lazy load and cache the scikit-learn model pipeline."""
    global _model_pipeline
    if _model_pipeline is None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model pipeline not found at {model_path}. Please execute 'python train_model.py' first."
            )
        _model_pipeline = joblib.load(model_path)
    return _model_pipeline


def create_app(config_name: str = None) -> Flask:
    """Application factory for Flask application."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config_cls = config_by_name.get(config_name, config_by_name["default"])

    app = Flask(__name__)
    app.config.from_object(config_cls)

    # Initialize extensions
    db.init_app(app)

    # ---------------------------------------------------------
    # Authentication & Access Control Decorator
    # ---------------------------------------------------------
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("login", next=request.path))
            return f(*args, **kwargs)
        return decorated_function

    @app.context_processor
    def inject_current_user():
        """Inject current logged-in user into all templates."""
        user = None
        if "user_id" in session:
            user = get_user_by_id(session["user_id"])
        return {"current_user": user}

    # ---------------------------------------------------------
    # Public Routes
    # ---------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/nutrition")
    def nutrition():
        return render_template("nutrition.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    # ---------------------------------------------------------
    # Authentication Routes
    # ---------------------------------------------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if "user_id" in session:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            dietary_preference = request.form.get("dietary_preference", "Non-Vegetarian")

            # Optional demographic inputs
            age_raw = request.form.get("age", "").strip()
            height_raw = request.form.get("height", "").strip()
            weight_raw = request.form.get("weight", "").strip()

            errors = []
            if not name or len(name) < 2:
                errors.append("Full Name must be at least 2 characters.")
            if not email or "@" not in email:
                errors.append("Please provide a valid email address.")
            if not password or len(password) < 6:
                errors.append("Password must be at least 6 characters.")
            if password != confirm_password:
                errors.append("Passwords do not match.")

            # Duplicate email check
            existing = get_user_by_email(email)
            if existing:
                errors.append("An account with this email already exists.")

            age = None
            if age_raw:
                try:
                    age = int(age_raw)
                    if age < 12 or age > 110:
                        errors.append("Age must be between 12 and 110.")
                except ValueError:
                    errors.append("Invalid age specified.")

            height = None
            if height_raw:
                try:
                    height = float(height_raw)
                    if height < 90 or height > 250:
                        errors.append("Height must be between 90 cm and 250 cm.")
                except ValueError:
                    errors.append("Invalid height specified.")

            weight = None
            if weight_raw:
                try:
                    weight = float(weight_raw)
                    if weight < 25 or weight > 300:
                        errors.append("Weight must be between 25 kg and 300 kg.")
                except ValueError:
                    errors.append("Invalid weight specified.")

            if errors:
                for err in errors:
                    flash(err, "danger")
                return render_template("register.html", form=request.form)

            # Create user and auto-login
            user = create_user(
                name=name,
                email=email,
                password=password,
                age=age,
                height=height,
                weight=weight,
                dietary_preference=dietary_preference
            )
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash(f"Welcome, {user.name}! Your account was created successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("register.html", form={})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = get_user_by_email(email)
            if user and user.check_password(password):
                session["user_id"] = user.id
                session["user_name"] = user.name
                flash(f"Welcome back, {user.name}!", "success")
                next_url = request.args.get("next")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password. Please try again.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been successfully logged out.", "info")
        return redirect(url_for("login"))

    # ---------------------------------------------------------
    # Protected Application Routes
    # ---------------------------------------------------------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        user_id = session["user_id"]
        stats = get_dashboard_stats(user_id)
        return render_template("dashboard.html", stats=stats)

    @app.route("/assessment", methods=["GET", "POST"])
    @login_required
    def assessment():
        user = get_user_by_id(session["user_id"])

        if request.method == "POST":
            try:
                age = int(request.form.get("age", 25))
                height = float(request.form.get("height", 160))  # in cm
                weight = float(request.form.get("weight", 55))   # in kg
            except (ValueError, TypeError):
                flash("Please enter valid numeric values for age, height, and weight.", "danger")
                return render_template("assessment.html", user=user)

            if height <= 0 or weight <= 0:
                flash("Height and weight must be positive numbers.", "danger")
                return render_template("assessment.html", user=user)

            # Accurate metric BMI calculation: weight (kg) / (height (m) ^ 2)
            height_meters = height / 100.0
            bmi = round(weight / (height_meters ** 2), 2)

            # Parse inputs
            assessment_data = {
                "age": age,
                "height": height,
                "weight": weight,
                "bmi": bmi,
                "heavy_menstrual_flow": 1 if request.form.get("heavy_menstrual_flow") == "yes" else 0,
                "pregnant": 1 if request.form.get("pregnant") == "yes" else 0,
                "vegetarian": 1 if request.form.get("vegetarian") == "yes" else 0,
                "iron_rich_food_frequency": request.form.get("iron_rich_food_frequency", "sometimes"),
                "vitamin_c_frequency": request.form.get("vitamin_c_frequency", "sometimes"),
                "tea_coffee_with_meals": 1 if request.form.get("tea_coffee_with_meals") == "yes" else 0,
                "fatigue": 1 if request.form.get("fatigue") == "yes" else 0,
                "dizziness": 1 if request.form.get("dizziness") == "yes" else 0,
                "weakness": 1 if request.form.get("weakness") == "yes" else 0,
                "shortness_of_breath": 1 if request.form.get("shortness_of_breath") == "yes" else 0,
                "pale_skin": 1 if request.form.get("pale_skin") == "yes" else 0,
                "previous_anemia": 1 if request.form.get("previous_anemia") == "yes" else 0,
                "chronic_condition": 1 if request.form.get("chronic_condition") == "yes" else 0
            }

            # Predict using serialized ML pipeline
            model_path = Path(app.config["MODEL_PATH"])
            try:
                pipeline = get_model_pipeline(model_path)
            except Exception as e:
                flash(f"Model error: {str(e)}", "danger")
                return render_template("assessment.html", user=user)

            input_df = pd.DataFrame([assessment_data])
            risk_prob = float(pipeline.predict_proba(input_df)[0, 1])

            # Map to Prototype Risk Levels
            if risk_prob < app.config["RISK_THRESHOLD_LOW"]:
                risk_level = "Low"
            elif risk_prob < app.config["RISK_THRESHOLD_HIGH"]:
                risk_level = "Moderate"
            else:
                risk_level = "High"

            # Generate and persist assessment and rule-based recommendations
            assessment_record = save_assessment(
                user_id=session["user_id"],
                assessment_data=assessment_data,
                risk_probability=risk_prob,
                risk_level=risk_level
            )

            recs = generate_recommendations(assessment_data, risk_level)
            save_recommendations(assessment_record.id, recs)

            flash("Screening assessment completed successfully!", "success")
            return redirect(url_for("result", assessment_id=assessment_record.id))

        return render_template("assessment.html", user=user)

    @app.route("/result/<int:assessment_id>")
    @login_required
    def result(assessment_id: int):
        assessment_record = get_assessment_by_id(assessment_id)

        if not assessment_record:
            abort(404)

        # STRICT OWNERSHIP CHECK: Per-user data isolation
        if assessment_record.user_id != session["user_id"]:
            abort(403)

        # Reconstruct factors considered for transparent presentation
        assessment_dict = assessment_record.to_dict()
        factors = get_factors_considered(assessment_dict)

        return render_template(
            "result.html",
            assessment=assessment_record,
            recommendations=assessment_record.recommendations,
            factors=factors
        )

    @app.route("/history")
    @login_required
    def history():
        user_id = session["user_id"]
        assessments = get_user_assessments(user_id)
        return render_template("history.html", assessments=assessments)

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        user_id = session["user_id"]
        user = get_user_by_id(user_id)
        if not user:
            abort(404)

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            dietary_preference = request.form.get("dietary_preference", "Non-Vegetarian")
            
            try:
                age = int(request.form.get("age", user.age or 25))
                height = float(request.form.get("height", user.height or 160))
                weight = float(request.form.get("weight", user.weight or 55))
            except (ValueError, TypeError):
                flash("Please provide valid numbers for age, height, and weight.", "danger")
                return render_template("profile.html", user=user)

            if not name:
                flash("Name cannot be empty.", "danger")
                return render_template("profile.html", user=user)

            update_user_profile(
                user_id=user_id,
                name=name,
                age=age,
                height=height,
                weight=weight,
                dietary_preference=dietary_preference
            )
            session["user_name"] = name
            flash("Your profile was updated successfully!", "success")
            return redirect(url_for("profile"))

        return render_template("profile.html", user=user)

    # ---------------------------------------------------------
    # API endpoints for dynamic chart support
    # ---------------------------------------------------------
    @app.route("/api/user/trends")
    @login_required
    def user_trends_api():
        stats = get_dashboard_stats(session["user_id"])
        return jsonify({
            "labels": stats["chart_labels"],
            "data": stats["chart_values"],
            "total": stats["total_assessments"]
        })

    @app.route("/api/chat", methods=["POST"])
    def chat_api():
        """Nutritional AI Copilot endpoint."""
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "Please type a question to ask the IronHer AI Nutrition Copilot."}), 400

        reply = generate_chat_response(user_message)
        return jsonify({"reply": reply})

    # ---------------------------------------------------------
    # Custom Error Handlers (Never expose raw tracebacks)
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app


# Application entry point for development and gunicorn
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
