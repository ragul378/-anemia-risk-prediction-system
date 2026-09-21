from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    dietary_preference = db.Column(db.String(50), default="Non-Vegetarian")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    assessments = db.relationship(
        "Assessment",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(Assessment.created_at)"
    )

    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "dietary_preference": self.dietary_preference,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Biometric data
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    bmi = db.Column(db.Float, nullable=False)

    # Clinical & Physiological factors
    heavy_menstrual_flow = db.Column(db.Boolean, default=False, nullable=False)
    pregnant = db.Column(db.Boolean, default=False, nullable=False)
    vegetarian = db.Column(db.Boolean, default=False, nullable=False)
    
    # Dietary frequencies: rarely, sometimes, often
    iron_rich_food_frequency = db.Column(db.String(20), nullable=False)
    vitamin_c_frequency = db.Column(db.String(20), nullable=False)
    tea_coffee_with_meals = db.Column(db.Boolean, default=False, nullable=False)

    # Symptom checklist (Boolean)
    fatigue = db.Column(db.Boolean, default=False, nullable=False)
    dizziness = db.Column(db.Boolean, default=False, nullable=False)
    weakness = db.Column(db.Boolean, default=False, nullable=False)
    shortness_of_breath = db.Column(db.Boolean, default=False, nullable=False)
    pale_skin = db.Column(db.Boolean, default=False, nullable=False)

    # History & Conditions
    previous_anemia = db.Column(db.Boolean, default=False, nullable=False)
    chronic_condition = db.Column(db.Boolean, default=False, nullable=False)

    # Prediction outputs
    risk_probability = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    risk_level = db.Column(db.String(20), nullable=False)    # Low, Moderate, High

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    recommendations = db.relationship(
        "Recommendation",
        backref="assessment",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Recommendation.id"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "bmi": round(self.bmi, 2),
            "heavy_menstrual_flow": self.heavy_menstrual_flow,
            "pregnant": self.pregnant,
            "vegetarian": self.vegetarian,
            "iron_rich_food_frequency": self.iron_rich_food_frequency,
            "vitamin_c_frequency": self.vitamin_c_frequency,
            "tea_coffee_with_meals": self.tea_coffee_with_meals,
            "fatigue": self.fatigue,
            "dizziness": self.dizziness,
            "weakness": self.weakness,
            "shortness_of_breath": self.shortness_of_breath,
            "pale_skin": self.pale_skin,
            "previous_anemia": self.previous_anemia,
            "chronic_condition": self.chronic_condition,
            "risk_probability": round(self.risk_probability, 4),
            "risk_level": self.risk_level,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)  # e.g., Iron-Rich Food, Enhancers, Inhibitors, Clinical
    food = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "category": self.category,
            "food": self.food,
            "reason": self.reason
        }


# ---------------------------------------------------------
# Reusable Database Service Functions
# ---------------------------------------------------------

def create_user(name: str, email: str, password: str, age: int = None,
                height: float = None, weight: float = None,
                dietary_preference: str = "Non-Vegetarian") -> User:
    """Create and persist a new user with hashed password."""
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        age=age,
        height=height,
        weight=weight,
        dietary_preference=dietary_preference
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email: str) -> User | None:
    """Find user by email address."""
    return User.query.filter_by(email=email.strip().lower()).first()


def get_user_by_id(user_id: int) -> User | None:
    """Find user by primary key ID."""
    return db.session.get(User, user_id)


def update_user_profile(user_id: int, name: str, age: int, height: float,
                        weight: float, dietary_preference: str) -> User | None:
    """Update profile information for the given user."""
    user = db.session.get(User, user_id)
    if user:
        user.name = name.strip()
        user.age = age
        user.height = height
        user.weight = weight
        user.dietary_preference = dietary_preference
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    return user


def save_assessment(user_id: int, assessment_data: dict, risk_probability: float, risk_level: str) -> Assessment:
    """Create and persist an Assessment record."""
    assessment = Assessment(
        user_id=user_id,
        age=assessment_data["age"],
        height=assessment_data["height"],
        weight=assessment_data["weight"],
        bmi=assessment_data["bmi"],
        heavy_menstrual_flow=bool(assessment_data.get("heavy_menstrual_flow", False)),
        pregnant=bool(assessment_data.get("pregnant", False)),
        vegetarian=bool(assessment_data.get("vegetarian", False)),
        iron_rich_food_frequency=assessment_data.get("iron_rich_food_frequency", "sometimes"),
        vitamin_c_frequency=assessment_data.get("vitamin_c_frequency", "sometimes"),
        tea_coffee_with_meals=bool(assessment_data.get("tea_coffee_with_meals", False)),
        fatigue=bool(assessment_data.get("fatigue", False)),
        dizziness=bool(assessment_data.get("dizziness", False)),
        weakness=bool(assessment_data.get("weakness", False)),
        shortness_of_breath=bool(assessment_data.get("shortness_of_breath", False)),
        pale_skin=bool(assessment_data.get("pale_skin", False)),
        previous_anemia=bool(assessment_data.get("previous_anemia", False)),
        chronic_condition=bool(assessment_data.get("chronic_condition", False)),
        risk_probability=risk_probability,
        risk_level=risk_level
    )
    db.session.add(assessment)
    db.session.commit()
    return assessment


def save_recommendations(assessment_id: int, recommendation_items: list[dict]) -> list[Recommendation]:
    """Persist a list of recommendation items for an assessment."""
    records = []
    for item in recommendation_items:
        rec = Recommendation(
            assessment_id=assessment_id,
            category=item.get("category", "General Nutrition"),
            food=item.get("food", ""),
            reason=item.get("reason", "")
        )
        db.session.add(rec)
        records.append(rec)
    db.session.commit()
    return records


def get_user_assessments(user_id: int) -> list[Assessment]:
    """Retrieve full history of assessments for a specific user ordered by date descending."""
    return Assessment.query.filter_by(user_id=user_id).order_by(Assessment.created_at.desc()).all()


def get_assessment_by_id(assessment_id: int) -> Assessment | None:
    """Retrieve single assessment with its recommendations."""
    return db.session.get(Assessment, assessment_id)


def get_latest_assessment(user_id: int) -> Assessment | None:
    """Get the most recent assessment for a user."""
    return Assessment.query.filter_by(user_id=user_id).order_by(Assessment.created_at.desc()).first()


def get_dashboard_stats(user_id: int) -> dict:
    """Calculate aggregate dashboard statistics and historical trends for user."""
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.created_at.asc()).all()
    
    total = len(assessments)
    if total == 0:
        return {
            "total_assessments": 0,
            "latest_assessment": None,
            "latest_risk_level": "N/A",
            "latest_risk_prob": None,
            "latest_date": "No assessments yet",
            "average_risk": 0.0,
            "chart_labels": [],
            "chart_values": []
        }

    latest = assessments[-1]
    avg_risk = sum(a.risk_probability for a in assessments) / total
    
    # Generate labels and points for Chart.js
    chart_labels = [a.created_at.strftime("%b %d, %H:%M") for a in assessments]
    chart_values = [round(a.risk_probability * 100, 1) for a in assessments]

    return {
        "total_assessments": total,
        "latest_assessment": latest,
        "latest_risk_level": latest.risk_level,
        "latest_risk_prob": round(latest.risk_probability * 100, 1),
        "latest_date": latest.created_at.strftime("%b %d, %Y %I:%M %p"),
        "average_risk": round(avg_risk * 100, 1),
        "chart_labels": chart_labels,
        "chart_values": chart_values
    }
