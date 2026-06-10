from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess Club/signup?email=tester@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up tester@mergington.edu for Chess Club"
    assert "tester@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_participant():
    response = client.delete("/activities/Chess Club/participants/michael%40mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess Club/participants/notfound%40mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unknown_activity_returns_404_for_signup():
    response = client.post("/activities/Nonexistent/signup?email=tester@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unknown_activity_returns_404_for_unregister():
    response = client.delete("/activities/Nonexistent/participants/tester%40mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
