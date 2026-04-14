from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
EXISTING_ACTIVITY = "Chess Club"
INVALID_ACTIVITY = "Nonexistent Club"
TEST_EMAIL = "test.student@mergington.edu"


def test_get_activities_returns_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert EXISTING_ACTIVITY in payload
    assert "description" in payload[EXISTING_ACTIVITY]
    assert "participants" in payload[EXISTING_ACTIVITY]


def test_signup_for_activity_adds_participant():
    # Arrange
    email = TEST_EMAIL
    assert email not in activities[EXISTING_ACTIVITY]["participants"]

    # Act
    response = client.post(
        f"/activities/{quote(EXISTING_ACTIVITY)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {EXISTING_ACTIVITY}"}
    assert email in activities[EXISTING_ACTIVITY]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = TEST_EMAIL
    activities[EXISTING_ACTIVITY]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{quote(EXISTING_ACTIVITY)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_removes_registered_user():
    # Arrange
    email = TEST_EMAIL
    activities[EXISTING_ACTIVITY]["participants"].append(email)
    assert email in activities[EXISTING_ACTIVITY]["participants"]

    # Act
    response = client.delete(
        f"/activities/{quote(EXISTING_ACTIVITY)}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {EXISTING_ACTIVITY}"}
    assert email not in activities[EXISTING_ACTIVITY]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    email = TEST_EMAIL
    assert email not in activities[EXISTING_ACTIVITY]["participants"]

    # Act
    response = client.delete(
        f"/activities/{quote(EXISTING_ACTIVITY)}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_invalid_activity_returns_404_for_signup_and_delete():
    # Arrange
    email = TEST_EMAIL

    # Act
    signup_response = client.post(
        f"/activities/{quote(INVALID_ACTIVITY)}/signup",
        params={"email": email},
    )
    delete_response = client.delete(
        f"/activities/{quote(INVALID_ACTIVITY)}/participants",
        params={"email": email},
    )

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
