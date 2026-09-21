"""Authentication, Registration, and Protected Route Tests."""

from database import get_user_by_email

def test_register_success(client, app):
    """Test successful user registration and auto-login."""
    response = client.post("/register", data={
        "name": "Ananya Sharma",
        "email": "ananya@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "age": "24",
        "height": "162",
        "weight": "55",
        "dietary_preference": "Vegetarian"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome, Ananya Sharma!" in response.data

    with app.app_context():
        user = get_user_by_email("ananya@example.com")
        assert user is not None
        assert user.name == "Ananya Sharma"
        # Password must be hashed, never plaintext
        assert user.password_hash != "Password123!"
        assert user.check_password("Password123!") is True
        assert user.dietary_preference == "Vegetarian"

def test_register_duplicate_email(client, test_user):
    """Registration with an already existing email should be rejected."""
    response = client.post("/register", data={
        "name": "Duplicate User",
        "email": "test@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An account with this email already exists." in response.data

def test_register_password_mismatch(client):
    """Registration with mismatched passwords should fail."""
    response = client.post("/register", data={
        "name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "Password123!",
        "confirm_password": "DifferentPassword!"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords do not match." in response.data

def test_login_success(client, test_user):
    """Test valid login credentials."""
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "securepassword123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Test Woman!" in response.data

def test_login_invalid_password(client, test_user):
    """Test login failure with incorrect password."""
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data

def test_logout(auth_client):
    """Test logging out clears session and redirects to login."""
    response = auth_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been successfully logged out." in response.data

def test_protected_routes_unauthenticated(client):
    """Unauthenticated access to protected routes must redirect to login."""
    protected_urls = ["/dashboard", "/assessment", "/history", "/profile"]
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
