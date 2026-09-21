import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-anemia-risk-key-2025")
    
    # Database URL handling with postgres:// fix for SQLAlchemy 2.0+
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        instance_dir = BASE_DIR / "instance"
        instance_dir.mkdir(exist_ok=True)
        db_path = instance_dir / "anemia.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model configuration
    MODEL_PATH = BASE_DIR / "models" / "anemia_model.joblib"
    DATA_PATH = BASE_DIR / "data" / "anemia_dataset.csv"

    # Prototype risk probability thresholds (Screening estimates)
    # Low: < 0.35, Moderate: 0.35 to 0.69, High: >= 0.70
    RISK_THRESHOLD_LOW = 0.35
    RISK_THRESHOLD_HIGH = 0.70

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-key"

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
