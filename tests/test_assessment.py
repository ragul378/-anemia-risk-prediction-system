"""Assessment Submission, Prediction Flow, and User Isolation Tests."""

from database import create_user, get_user_by_email, get_user_assessments, get_assessment_by_id

def test_assessment_submission_and_prediction(auth_client, app, test_user):
    """Submitting assessment should calculate BMI, predict risk, save DB rows, and render result."""
    response = auth_client.post("/assessment", data={
        "age": "26",
        "height": "160",
        "weight": "50",
        "heavy_menstrual_flow": "yes",
        "pregnant": "no",
        "vegetarian": "yes",
        "iron_rich_food_frequency": "rarely",
        "vitamin_c_frequency": "rarely",
        "tea_coffee_with_meals": "yes",
        "fatigue": "yes",
        "dizziness": "yes",
        "weakness": "yes",
        "shortness_of_breath": "no",
        "pale_skin": "yes",
        "previous_anemia": "yes",
        "chronic_condition": "no"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Screening assessment completed successfully!" in response.data
    assert b"AI Anemia Risk Screening Summary" in response.data
    assert b"Factors Considered by the Model" in response.data
    assert b"Personalized Nutrition" in response.data

    with app.app_context():
        user = get_user_by_email("test@example.com")
        assessments = get_user_assessments(user.id)
        assert len(assessments) == 1
        a = assessments[0]
        # Check correct BMI calculation: 50 / (1.60^2) = 19.53
        assert round(a.bmi, 2) == 19.53
        assert 0.0 <= a.risk_probability <= 1.0
        assert a.risk_level in ["Low", "Moderate", "High"]
        # High-risk profile should yield elevated probability
        assert a.risk_probability > 0.50
        assert len(a.recommendations) > 0
        for rec in a.recommendations:
            assert rec.category is not None
            assert rec.food is not None
            assert rec.reason is not None

def test_history_shows_own_assessments(auth_client, app, test_user):
    """History page should display user's past screening entries."""
    # Submit one assessment first
    auth_client.post("/assessment", data={
        "age": "28", "height": "165", "weight": "58",
        "heavy_menstrual_flow": "no", "pregnant": "no", "vegetarian": "no",
        "iron_rich_food_frequency": "often", "vitamin_c_frequency": "often",
        "tea_coffee_with_meals": "no", "fatigue": "no", "dizziness": "no",
        "weakness": "no", "shortness_of_breath": "no", "pale_skin": "no",
        "previous_anemia": "no", "chronic_condition": "no"
    }, follow_redirects=True)

    response = auth_client.get("/history")
    assert response.status_code == 200
    assert b"Your Screening History" in response.data
    assert b"View Result" in response.data

def test_user_data_isolation_access_control(client, app, test_user):
    """Ensure User B CANNOT view User A's assessment result (403 Forbidden)."""
    # Create Assessment for User A (test_user)
    assessment_id = None
    with app.app_context():
        client.post("/login", data={"email": "test@example.com", "password": "securepassword123"})
        res = client.post("/assessment", data={
            "age": "30", "height": "155", "weight": "52",
            "heavy_menstrual_flow": "no", "pregnant": "no", "vegetarian": "yes",
            "iron_rich_food_frequency": "sometimes", "vitamin_c_frequency": "sometimes",
            "tea_coffee_with_meals": "no", "fatigue": "no", "dizziness": "no",
            "weakness": "no", "shortness_of_breath": "no", "pale_skin": "no",
            "previous_anemia": "no", "chronic_condition": "no"
        })
        user_a = get_user_by_email("test@example.com")
        user_a_assessments = get_user_assessments(user_a.id)
        assessment_id = user_a_assessments[0].id
        client.get("/logout")

    # Create and login as User B
    with app.app_context():
        create_user(name="User B", email="userb@example.com", password="passwordB123")

    client.post("/login", data={"email": "userb@example.com", "password": "passwordB123"}, follow_redirects=True)

    # User B attempts to access User A's assessment ID
    response = client.get(f"/result/{assessment_id}")
    assert response.status_code == 403
    assert b"Access Denied &amp; Data Protection Protected" in response.data or b"Access Denied" in response.data
