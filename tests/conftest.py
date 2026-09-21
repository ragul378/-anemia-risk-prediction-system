import sys
from pathlib import Path
import importlib.metadata
import werkzeug

# Ensure werkzeug.__version__ compatibility with Flask test_client
if not hasattr(werkzeug, "__version__"):
    try:
        werkzeug.__version__ = importlib.metadata.version("werkzeug")
    except Exception:
        werkzeug.__version__ = "3.1.3"

# Add application root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app import create_app
from database import db, create_user



@pytest.fixture
def app():
    """Create and configure a testing Flask application."""
    test_app = create_app("testing")

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a default test user."""
    with app.app_context():
        user = create_user(
            name="Test Woman",
            email="test@example.com",
            password="securepassword123",
            age=26,
            height=160.0,
            weight=54.0,
            dietary_preference="Non-Vegetarian"
        )
        db.session.commit()
        db.session.refresh(user)
        user_id = user.id
    
    # Attach user_id directly as an integer attribute so detached state never causes error
    user.__dict__["id"] = user_id
    return user


@pytest.fixture
def auth_client(client, test_user):
    """A test client logged in with test_user."""
    client.post("/login", data={
        "email": "test@example.com",
        "password": "securepassword123"
    }, follow_redirects=True)
    return client
