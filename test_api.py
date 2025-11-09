#!/usr/bin/env python3
"""
Manual test script for StepSquad API
Tests the key endpoints according to the specification
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    print("✅ Health check passed")

def test_auth_admin():
    """Test admin authentication"""
    print("\nTesting admin authentication...")
    headers = {"X-Dev-User": "admin@stepsquad.club"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "ADMIN"
    assert data["email"] == "admin@stepsquad.club"
    print("✅ Admin auth passed")
    return headers

def test_auth_member():
    """Test member authentication"""
    print("\nTesting member authentication...")
    headers = {"X-Dev-User": "member@example.com"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "MEMBER"
    assert data["email"] == "member@example.com"
    print("✅ Member auth passed")
    return headers

def test_create_competition(admin_headers):
    """Test competition creation"""
    print("\nTesting competition creation...")
    competition_data = {
        "comp_id": "test-comp-001",
        "name": "Test Competition",
        "tz": "Europe/Bucharest",
        "status": "DRAFT",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 5,
        "max_members_per_team": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/competitions",
        headers={**admin_headers, "Content-Type": "application/json"},
        json=competition_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["comp_id"] == "test-comp-001"
    print("✅ Competition creation passed")

def test_create_duplicate_competition(admin_headers):
    """Test duplicate competition creation (should fail)"""
    print("\nTesting duplicate competition creation...")
    competition_data = {
        "comp_id": "test-comp-001",  # Same as above
        "name": "Another Test Competition",
        "tz": "Europe/Bucharest",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 5,
        "max_members_per_team": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/competitions",
        headers={**admin_headers, "Content-Type": "application/json"},
        json=competition_data
    )
    assert response.status_code == 409
    print("✅ Duplicate competition rejection passed")

def test_invalid_date_validation(admin_headers):
    """Test date validation"""
    print("\nTesting date validation...")
    competition_data = {
        "comp_id": "test-comp-invalid",
        "name": "Invalid Date Competition",
        "tz": "Europe/Bucharest",
        "registration_open_date": "2025-03-01",  # After start date
        "start_date": "2025-02-01",
        "end_date": "2025-01-01",  # Before start date
        "max_teams": 5,
        "max_members_per_team": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/competitions",
        headers={**admin_headers, "Content-Type": "application/json"},
        json=competition_data
    )
    assert response.status_code == 422
    print("✅ Date validation passed")

def test_list_competitions(admin_headers):
    """Test competition listing"""
    print("\nTesting competition listing...")
    response = requests.get(f"{BASE_URL}/competitions", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert len(data["rows"]) > 0
    print(f"✅ Competition listing passed ({len(data['rows'])} competitions)")

def test_get_competition(admin_headers):
    """Test getting specific competition"""
    print("\nTesting get competition...")
    response = requests.get(f"{BASE_URL}/competitions/test-comp-001", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["comp_id"] == "test-comp-001"
    assert data["name"] == "Test Competition"
    print("✅ Get competition passed")

def test_update_competition(admin_headers):
    """Test competition update"""
    print("\nTesting competition update...")
    update_data = {
        "name": "Updated Test Competition",
        "status": "REGISTRATION"
    }
    
    response = requests.patch(
        f"{BASE_URL}/competitions/test-comp-001",
        headers={**admin_headers, "Content-Type": "application/json"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    print("✅ Competition update passed")

def test_member_cannot_create(member_headers):
    """Test that members cannot create competitions"""
    print("\nTesting member cannot create competition...")
    competition_data = {
        "comp_id": "member-comp",
        "name": "Member Competition",
        "tz": "Europe/Bucharest",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 5,
        "max_members_per_team": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/competitions",
        headers={**member_headers, "Content-Type": "application/json"},
        json=competition_data
    )
    assert response.status_code == 403
    print("✅ Member access restriction passed")

def test_soft_delete(admin_headers):
    """Test soft delete (archive)"""
    print("\nTesting soft delete...")
    response = requests.delete(f"{BASE_URL}/competitions/test-comp-001", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    
    # Verify competition is archived, not deleted
    response = requests.get(f"{BASE_URL}/competitions/test-comp-001", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ARCHIVED"
    print("✅ Soft delete passed")

def main():
    """Run all tests"""
    print("🧪 Running StepSquad API Tests")
    print("=" * 50)
    
    try:
        test_health()
        admin_headers = test_auth_admin()
        member_headers = test_auth_member()
        test_create_competition(admin_headers)
        test_create_duplicate_competition(admin_headers)
        test_invalid_date_validation(admin_headers)
        test_list_competitions(admin_headers)
        test_get_competition(admin_headers)
        test_update_competition(admin_headers)
        test_member_cannot_create(member_headers)
        test_soft_delete(admin_headers)
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
