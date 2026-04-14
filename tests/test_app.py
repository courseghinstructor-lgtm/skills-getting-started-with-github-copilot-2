"""
Tests for the FastAPI application using AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities endpoint returns all activities."""
    # Arrange
    # (No special setup needed for this test)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities
    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_root_redirect():
    """Test GET / root endpoint redirects to static index.html."""
    # Arrange
    # (No special setup needed)

    # Act
    response = client.get("/", follow_redirects=False)  # Don't follow redirect

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]

    # Verify participant was added
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up."""
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Programming Class"

    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "NonExistent Club"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange
    email = "unregister@mergington.edu"
    activity = "Gym Class"

    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]

    # Verify participant was removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_unregister_invalid_activity():
    """Test unregister fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Fake Club"

    # Act
    response = client.delete(f"/activities/{invalid_activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_invalid_participant():
    """Test unregister fails when participant is not signed up."""
    # Arrange
    email = "notsignedup@mergington.edu"
    activity = "Debate Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Participant not found" in result["detail"]