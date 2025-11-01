import pytest
from fastapi.testclient import TestClient
from main import app
import os

# Set environment for testing
os.environ["GCP_ENABLED"] = "false"
os.environ["COMP_TZ"] = "Europe/Bucharest"

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def admin_headers():
    """Headers for admin user"""
    return {"X-Dev-User": "admin@stepsquad.com"}

@pytest.fixture
def member_headers():
    """Headers for member user"""
    return {"X-Dev-User": "member@example.com"}
