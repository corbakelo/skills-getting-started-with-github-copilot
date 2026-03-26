import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Provide sample activity data for testing"""
    return {
        "name": "Test Activity",
        "description": "A test activity",
        "schedule": "Test time",
        "max_participants": 5,
        "participants": ["test1@school.edu", "test2@school.edu"]
    }
