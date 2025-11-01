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


# Team Management Tests

def test_create_team_requires_competition(client, admin_headers, member_headers):
    """Test that creating a team requires a valid competition"""
    # First create a competition
    comp_data = {
        "comp_id": "test-team-comp-001",
        "name": "Team Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user info to get uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create team with valid competition
    team_data = {
        "name": "Test Team",
        "comp_id": "test-team-comp-001",
        "owner_uid": uid
    }
    response = client.post("/teams", json=team_data, headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "team_id" in data
    assert data["name"] == "Test Team"
    assert data["comp_id"] == "test-team-comp-001"

def test_create_team_invalid_competition(client, member_headers):
    """Test creating team with non-existent competition"""
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    team_data = {
        "name": "Test Team",
        "comp_id": "nonexistent-comp",
        "owner_uid": uid
    }
    response = client.post("/teams", json=team_data, headers=member_headers)
    assert response.status_code == 404

def test_create_team_wrong_status(client, admin_headers, member_headers):
    """Test that teams can only be created when competition is in REGISTRATION or ACTIVE status"""
    # Create competition with DRAFT status
    comp_data = {
        "comp_id": "test-team-draft",
        "name": "Draft Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "DRAFT"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    team_data = {
        "name": "Test Team",
        "comp_id": "test-team-draft",
        "owner_uid": uid
    }
    response = client.post("/teams", json=team_data, headers=member_headers)
    assert response.status_code == 422

def test_create_team_max_teams_reached(client, admin_headers, member_headers):
    """Test that team creation fails when max teams is reached"""
    # Create competition with max_teams = 1
    comp_data = {
        "comp_id": "test-team-max",
        "name": "Max Teams Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 1,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create first team (should succeed)
    team_data = {
        "name": "First Team",
        "comp_id": "test-team-max",
        "owner_uid": uid
    }
    response1 = client.post("/teams", json=team_data, headers=member_headers)
    assert response1.status_code == 200
    
    # Try to create second team (should fail)
    team_data2 = {
        "name": "Second Team",
        "comp_id": "test-team-max",
        "owner_uid": uid
    }
    response2 = client.post("/teams", json=team_data2, headers=member_headers)
    assert response2.status_code == 409

def test_create_team_wrong_user(client, admin_headers, member_headers):
    """Test that user can only create team for themselves"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-user",
        "name": "User Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get admin uid
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Member tries to create team for admin (should fail)
    team_data = {
        "name": "Test Team",
        "comp_id": "test-team-user",
        "owner_uid": admin_uid  # Wrong user
    }
    response = client.post("/teams", json=team_data, headers=member_headers)
    assert response.status_code == 403

def test_list_competition_teams(client, admin_headers, member_headers):
    """Test listing teams for a competition"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-list",
        "name": "List Teams Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "List Test Team",
        "comp_id": "test-team-list",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # List teams
    response = client.get("/competitions/test-team-list/teams", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert isinstance(data["rows"], list)
    assert len(data["rows"]) > 0
    assert data["rows"][0]["name"] == "List Test Team"

def test_list_teams_nonexistent_competition(client, member_headers):
    """Test listing teams for non-existent competition"""
    response = client.get("/competitions/nonexistent/teams", headers=member_headers)
    assert response.status_code == 404

def test_get_team_details(client, admin_headers, member_headers):
    """Test getting team details"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-detail",
        "name": "Detail Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Detail Test Team",
        "comp_id": "test-team-detail",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get team details
    response = client.get(f"/teams/{team_id}", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["team_id"] == team_id
    assert data["name"] == "Detail Test Team"
    assert "members" in data
    assert uid in data["members"]

def test_get_team_not_found(client, member_headers):
    """Test getting non-existent team"""
    response = client.get("/teams/nonexistent", headers=member_headers)
    assert response.status_code == 404

def test_join_team(client, admin_headers, member_headers):
    """Test joining a team"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-join",
        "name": "Join Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Join Test Team",
        "comp_id": "test-team-join",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get another user (admin) to join
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Join team
    join_data = {
        "team_id": team_id,
        "uid": admin_uid
    }
    response = client.post("/teams/join", json=join_data, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["team_id"] == team_id
    
    # Verify member was added
    team_response = client.get(f"/teams/{team_id}", headers=member_headers)
    team_details = team_response.json()
    assert admin_uid in team_details["members"]

def test_join_team_already_member(client, admin_headers, member_headers):
    """Test joining a team when already a member"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-join-twice",
        "name": "Join Twice Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Join Twice Team",
        "comp_id": "test-team-join-twice",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Try to join again (should fail - already owner/member)
    join_data = {
        "team_id": team_id,
        "uid": uid
    }
    response = client.post("/teams/join", json=join_data, headers=member_headers)
    assert response.status_code == 409

def test_join_team_full(client, admin_headers, member_headers):
    """Test joining a team when it's full"""
    # Create competition with max_members_per_team = 1
    comp_data = {
        "comp_id": "test-team-full",
        "name": "Full Team Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 1,  # Only 1 member allowed
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team (owner is already member)
    team_data = {
        "name": "Full Team",
        "comp_id": "test-team-full",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Try to join (should fail - team is full)
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    join_data = {
        "team_id": team_id,
        "uid": admin_uid
    }
    response = client.post("/teams/join", json=join_data, headers=admin_headers)
    assert response.status_code == 409

def test_leave_team(client, admin_headers, member_headers):
    """Test leaving a team"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-leave",
        "name": "Leave Test Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Leave Test Team",
        "comp_id": "test-team-leave",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get another user (admin) to join
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Join team
    join_data = {
        "team_id": team_id,
        "uid": admin_uid
    }
    client.post("/teams/join", json=join_data, headers=admin_headers)
    
    # Leave team
    response = client.delete(f"/teams/{team_id}/members/{admin_uid}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    
    # Verify member was removed
    team_response = client.get(f"/teams/{team_id}", headers=member_headers)
    team_details = team_response.json()
    assert admin_uid not in team_details["members"]

def test_leave_team_not_member(client, admin_headers, member_headers):
    """Test leaving a team when not a member"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-leave-not-member",
        "name": "Leave Not Member Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Leave Not Member Team",
        "comp_id": "test-team-leave-not-member",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get another user (admin) to try to leave (but not a member)
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Try to leave (should fail - not a member)
    response = client.delete(f"/teams/{team_id}/members/{admin_uid}", headers=admin_headers)
    assert response.status_code == 404

def test_leave_team_owner_with_members(client, admin_headers, member_headers):
    """Test that owner cannot leave if team has other members"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-leave-owner",
        "name": "Leave Owner Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Leave Owner Team",
        "comp_id": "test-team-leave-owner",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get another user (admin) to join
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Join team
    join_data = {
        "team_id": team_id,
        "uid": admin_uid
    }
    client.post("/teams/join", json=join_data, headers=admin_headers)
    
    # Owner tries to leave (should fail - has other members)
    response = client.delete(f"/teams/{team_id}/members/{uid}", headers=member_headers)
    assert response.status_code == 422

def test_leave_team_wrong_user(client, admin_headers, member_headers):
    """Test that user can only leave their own team membership"""
    # Create competition
    comp_data = {
        "comp_id": "test-team-leave-wrong",
        "name": "Leave Wrong Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "REGISTRATION"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Leave Wrong Team",
        "comp_id": "test-team-leave-wrong",
        "owner_uid": uid
    }
    create_response = client.post("/teams", json=team_data, headers=member_headers)
    team_id = create_response.json()["team_id"]
    
    # Get another user (admin) to try to remove member
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Admin tries to remove member (should fail - can only remove themselves)
    response = client.delete(f"/teams/{team_id}/members/{uid}", headers=admin_headers)
    assert response.status_code == 403
