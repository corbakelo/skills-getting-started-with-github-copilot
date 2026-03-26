import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    yield
    # Reset to initial state after each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    })


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "Chess Club" in response.json()

    def test_get_activities_includes_participant_count(self, client):
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "participants" in chess_club
        assert len(chess_club["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_student(self, client):
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client):
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant(self, client):
        client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "alice@mergington.edu" in participants


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""

    def test_remove_participant_success(self, client):
        response = client.delete(
            "/activities/Chess%20Club/remove?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_participant_not_registered(self, client):
        response = client.delete(
            "/activities/Chess%20Club/remove?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_participant_activity_not_found(self, client):
        response = client.delete(
            "/activities/Nonexistent%20Club/remove?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_updates_list(self, client):
        client.delete("/activities/Chess%20Club/remove?email=michael@mergington.edu")
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
        assert len(participants) == 1
