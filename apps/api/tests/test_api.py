"""
Unit tests for StepSquad API endpoints
"""
import pytest
from datetime import datetime

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert "time" in data
    assert "tz" in data

def test_me_endpoint_creates_admin(client, admin_headers):
    """Test /me endpoint creates admin user"""
    response = client.get("/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@stepsquad.com"
    assert data["role"] == "ADMIN"
    assert "uid" in data

def test_me_endpoint_creates_member(client, member_headers):
    """Test /me endpoint creates member user"""
    response = client.get("/me", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "member@example.com"
    assert data["role"] == "MEMBER"
    assert "uid" in data

def test_me_endpoint_requires_auth(client):
    """Test /me endpoint requires authentication"""
    response = client.get("/me")
    assert response.status_code == 401

def test_create_competition_requires_admin(client, member_headers):
    """Test that members cannot create competitions"""
    competition_data = {
        "comp_id": "test-001",
        "name": "Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    response = client.post("/competitions", json=competition_data, headers=member_headers)
    assert response.status_code == 403

def test_create_competition_valid(client, admin_headers):
    """Test creating a valid competition"""
    competition_data = {
        "comp_id": "test-comp-001",
        "name": "Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    response = client.post("/competitions", json=competition_data, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["comp_id"] == "test-comp-001"

def test_create_competition_duplicate(client, admin_headers):
    """Test creating duplicate competition (should fail)"""
    competition_data = {
        "comp_id": "test-comp-dup",
        "name": "Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    # Create first time
    response1 = client.post("/competitions", json=competition_data, headers=admin_headers)
    assert response1.status_code == 200
    
    # Try to create duplicate
    response2 = client.post("/competitions", json=competition_data, headers=admin_headers)
    assert response2.status_code == 409

def test_create_competition_invalid_dates(client, admin_headers):
    """Test creating competition with invalid date ordering"""
    competition_data = {
        "comp_id": "test-invalid",
        "name": "Invalid Competition",
        "registration_open_date": "2025-03-01",  # After start date
        "start_date": "2025-02-01",
        "end_date": "2025-01-01",  # Before start date
        "max_teams": 10,
        "max_members_per_team": 5
    }
    response = client.post("/competitions", json=competition_data, headers=admin_headers)
    assert response.status_code == 422

def test_list_competitions(client, admin_headers):
    """Test listing competitions"""
    # Create a competition first
    competition_data = {
        "comp_id": "test-list-001",
        "name": "List Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    client.post("/competitions", json=competition_data, headers=admin_headers)
    
    # List competitions
    response = client.get("/competitions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert isinstance(data["rows"], list)
    assert len(data["rows"]) > 0

def test_get_competition(client, admin_headers):
    """Test getting a single competition"""
    # Create a competition
    competition_data = {
        "comp_id": "test-get-001",
        "name": "Get Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    client.post("/competitions", json=competition_data, headers=admin_headers)
    
    # Get the competition
    response = client.get("/competitions/test-get-001", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["comp_id"] == "test-get-001"
    assert data["name"] == "Get Test Competition"

def test_get_competition_not_found(client, admin_headers):
    """Test getting non-existent competition"""
    response = client.get("/competitions/nonexistent", headers=admin_headers)
    assert response.status_code == 404

def test_update_competition(client, admin_headers):
    """Test updating a competition"""
    # Create a competition
    competition_data = {
        "comp_id": "test-update-001",
        "name": "Original Name",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    client.post("/competitions", json=competition_data, headers=admin_headers)
    
    # Update the competition
    update_data = {
        "name": "Updated Name",
        "status": "REGISTRATION"
    }
    response = client.patch("/competitions/test-update-001", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    
    # Verify update
    get_response = client.get("/competitions/test-update-001", headers=admin_headers)
    assert get_response.status_code == 200
    updated = get_response.json()
    assert updated["name"] == "Updated Name"
    assert updated["status"] == "REGISTRATION"

def test_delete_competition_soft_delete(client, admin_headers):
    """Test soft delete (archive) competition"""
    # Create a competition
    competition_data = {
        "comp_id": "test-delete-001",
        "name": "Delete Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=competition_data, headers=admin_headers)
    
    # Delete (archive) the competition
    response = client.delete("/competitions/test-delete-001", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    
    # Verify it's archived (not deleted)
    get_response = client.get("/competitions/test-delete-001", headers=admin_headers)
    assert get_response.status_code == 200
    archived = get_response.json()
    assert archived["status"] == "ARCHIVED"

def test_member_can_read_competitions(client, member_headers, admin_headers):
    """Test that members can read competitions"""
    # Admin creates a competition
    competition_data = {
        "comp_id": "test-member-read",
        "name": "Member Read Test",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5
    }
    client.post("/competitions", json=competition_data, headers=admin_headers)
    
    # Member can read it
    response = client.get("/competitions/test-member-read", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["comp_id"] == "test-member-read"

def test_validation_max_teams(client, admin_headers):
    """Test validation for max_teams range"""
    competition_data = {
        "comp_id": "test-validation",
        "name": "Validation Test",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 600,  # Exceeds limit of 500
        "max_members_per_team": 5
    }
    response = client.post("/competitions", json=competition_data, headers=admin_headers)
    assert response.status_code == 422
