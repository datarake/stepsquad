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


# Step Ingestion Tests
def test_submit_steps_success(client, admin_headers, member_headers):
    """Test successful step submission"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-001",
        "name": "Steps Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Steps Team",
        "comp_id": "test-steps-001",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps
    step_data = {
        "comp_id": "test-steps-001",
        "date": "2025-02-15",
        "steps": 10000,
        "provider": "manual"
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["stored"] == True
    assert data["user_id"] == uid
    assert data["comp_id"] == "test-steps-001"
    assert data["steps"] == 10000

def test_submit_steps_requires_auth(client):
    """Test that step submission requires authentication"""
    step_data = {
        "comp_id": "test-steps-001",
        "date": "2025-02-15",
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data)
    assert response.status_code == 401

def test_submit_steps_requires_team(client, admin_headers, member_headers):
    """Test that user must be in a team to submit steps"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-no-team",
        "name": "Steps Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Submit steps without joining a team (should fail)
    step_data = {
        "comp_id": "test-steps-no-team",
        "date": "2025-02-15",
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 403
    assert "must be a member of a team" in response.json()["detail"]

def test_submit_steps_wrong_status(client, admin_headers, member_headers):
    """Test that step submission only works for ACTIVE competitions"""
    # Create REGISTRATION competition
    comp_data = {
        "comp_id": "test-steps-registration",
        "name": "Registration Competition",
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
        "name": "Registration Team",
        "comp_id": "test-steps-registration",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Try to submit steps (should fail)
    step_data = {
        "comp_id": "test-steps-registration",
        "date": "2025-02-15",
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 400
    assert "ACTIVE" in response.json()["detail"]

def test_submit_steps_date_before_start(client, admin_headers, member_headers):
    """Test that date must be on or after competition start date"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-date",
        "name": "Date Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Date Team",
        "comp_id": "test-steps-date",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps with date before start (should fail)
    step_data = {
        "comp_id": "test-steps-date",
        "date": "2025-01-15",
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 400
    assert "before competition start date" in response.json()["detail"]

def test_submit_steps_date_after_end(client, admin_headers, member_headers):
    """Test that date must be within grace period after end date"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-date-end",
        "name": "End Date Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "End Date Team",
        "comp_id": "test-steps-date-end",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps with date too far after end (should fail)
    step_data = {
        "comp_id": "test-steps-date-end",
        "date": "2025-03-10",  # More than 2 days after end
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 400
    assert "after competition end date" in response.json()["detail"]

def test_submit_steps_invalid_count(client, admin_headers, member_headers):
    """Test that step count must be within valid range"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-count",
        "name": "Count Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Count Team",
        "comp_id": "test-steps-count",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps with count > 100000 (should fail with 422 - Pydantic validation)
    step_data = {
        "comp_id": "test-steps-count",
        "date": "2025-02-15",
        "steps": 150000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    # Pydantic validates Field(le=100000) before our endpoint code, so returns 422
    assert response.status_code == 422

def test_submit_steps_idempotency(client, admin_headers, member_headers):
    """Test that duplicate idempotency keys are rejected"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-idempotency",
        "name": "Idempotency Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "Idempotency Team",
        "comp_id": "test-steps-idempotency",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps with idempotency key (should succeed)
    step_data = {
        "comp_id": "test-steps-idempotency",
        "date": "2025-02-15",
        "steps": 10000,
        "idempotency_key": "unique-key-123"
    }
    response1 = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response1.status_code == 200
    
    # Submit same steps with same idempotency key (should fail)
    response2 = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response2.status_code == 409
    assert "Duplicate submission" in response2.json()["detail"]

def test_get_user_step_history(client, admin_headers, member_headers):
    """Test getting user step history"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-steps-history",
        "name": "History Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Create a team
    team_data = {
        "name": "History Team",
        "comp_id": "test-steps-history",
        "owner_uid": uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps
    step_data = {
        "comp_id": "test-steps-history",
        "date": "2025-02-15",
        "steps": 10000
    }
    client.post("/ingest/steps", json=step_data, headers=member_headers)
    
    # Get step history
    response = client.get(f"/users/{uid}/steps", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert len(data["rows"]) > 0
    assert any(entry["date"] == "2025-02-15" and entry["steps"] == 10000 for entry in data["rows"])

def test_get_user_step_history_forbidden(client, admin_headers, member_headers):
    """Test that users can only view their own step history"""
    # Get user uids
    member_me = client.get("/me", headers=member_headers)
    member_uid = member_me.json()["uid"]
    
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Member tries to view admin's steps (should fail)
    response = client.get(f"/users/{admin_uid}/steps", headers=member_headers)
    assert response.status_code == 403
    assert "own step history" in response.json()["detail"]

def test_get_user_step_history_nonexistent_competition(client, admin_headers, member_headers):
    """Test submitting steps to nonexistent competition"""
    # Get user uid
    me_response = client.get("/me", headers=member_headers)
    user_data = me_response.json()
    uid = user_data["uid"]
    
    # Submit steps to nonexistent competition (should fail)
    step_data = {
        "comp_id": "nonexistent-comp",
        "date": "2025-02-15",
        "steps": 10000
    }
    response = client.post("/ingest/steps", json=step_data, headers=member_headers)
    assert response.status_code == 404
    assert "Competition not found" in response.json()["detail"]


# Leaderboard Tests
def test_individual_leaderboard_with_competition(client, admin_headers, member_headers):
    """Test individual leaderboard filtered by competition"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-lb-comp",
        "name": "Leaderboard Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uids
    member_me = client.get("/me", headers=member_headers)
    member_uid = member_me.json()["uid"]
    
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Create teams
    team1_data = {
        "name": "Team 1",
        "comp_id": "test-lb-comp",
        "owner_uid": member_uid
    }
    team1_response = client.post("/teams", json=team1_data, headers=member_headers)
    team1_id = team1_response.json()["team_id"]
    
    team2_data = {
        "name": "Team 2",
        "comp_id": "test-lb-comp",
        "owner_uid": admin_uid
    }
    client.post("/teams", json=team2_data, headers=admin_headers)
    
    # Join admin to team 2
    join_data = {
        "team_id": team1_id,
        "uid": admin_uid
    }
    client.post("/teams/join", json=join_data, headers=admin_headers)
    
    # Submit steps
    member_steps = {
        "comp_id": "test-lb-comp",
        "date": "2025-02-15",
        "steps": 10000
    }
    client.post("/ingest/steps", json=member_steps, headers=member_headers)
    
    admin_steps = {
        "comp_id": "test-lb-comp",
        "date": "2025-02-15",
        "steps": 15000
    }
    client.post("/ingest/steps", json=admin_steps, headers=admin_headers)
    
    # Get leaderboard
    response = client.get("/leaderboard/individual?comp_id=test-lb-comp", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert len(data["rows"]) >= 2
    
    # Admin should be first (more steps)
    assert data["rows"][0]["steps"] == 15000
    assert data["rows"][0]["user_id"] == admin_uid
    assert data["rows"][0]["rank"] == 1

def test_individual_leaderboard_with_date(client, admin_headers, member_headers):
    """Test individual leaderboard filtered by date"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-lb-date",
        "name": "Date Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    member_me = client.get("/me", headers=member_headers)
    member_uid = member_me.json()["uid"]
    
    # Create team
    team_data = {
        "name": "Date Team",
        "comp_id": "test-lb-date",
        "owner_uid": member_uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps for different dates
    steps1 = {
        "comp_id": "test-lb-date",
        "date": "2025-02-15",
        "steps": 10000
    }
    client.post("/ingest/steps", json=steps1, headers=member_headers)
    
    steps2 = {
        "comp_id": "test-lb-date",
        "date": "2025-02-16",
        "steps": 5000
    }
    client.post("/ingest/steps", json=steps2, headers=member_headers)
    
    # Get leaderboard for specific date
    response = client.get("/leaderboard/individual?comp_id=test-lb-date&date=2025-02-15", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) >= 1
    assert data["rows"][0]["steps"] == 10000

def test_team_leaderboard_with_competition(client, admin_headers, member_headers):
    """Test team leaderboard filtered by competition"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-lb-team",
        "name": "Team Leaderboard Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uids
    member_me = client.get("/me", headers=member_headers)
    member_uid = member_me.json()["uid"]
    
    admin_me = client.get("/me", headers=admin_headers)
    admin_uid = admin_me.json()["uid"]
    
    # Create teams
    team1_data = {
        "name": "Team Alpha",
        "comp_id": "test-lb-team",
        "owner_uid": member_uid
    }
    team1_response = client.post("/teams", json=team1_data, headers=member_headers)
    team1_id = team1_response.json()["team_id"]
    
    team2_data = {
        "name": "Team Beta",
        "comp_id": "test-lb-team",
        "owner_uid": admin_uid
    }
    team2_response = client.post("/teams", json=team2_data, headers=admin_headers)
    team2_id = team2_response.json()["team_id"]
    
    # Submit steps for each team
    member_steps = {
        "comp_id": "test-lb-team",
        "date": "2025-02-15",
        "steps": 10000
    }
    client.post("/ingest/steps", json=member_steps, headers=member_headers)
    
    admin_steps = {
        "comp_id": "test-lb-team",
        "date": "2025-02-15",
        "steps": 15000
    }
    client.post("/ingest/steps", json=admin_steps, headers=admin_headers)
    
    # Get team leaderboard
    response = client.get("/leaderboard/team?comp_id=test-lb-team", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert len(data["rows"]) >= 2
    
    # Team Beta should be first (more steps)
    team_beta = next((t for t in data["rows"] if t["name"] == "Team Beta"), None)
    assert team_beta is not None
    assert team_beta["steps"] == 15000
    assert team_beta["rank"] == 1

def test_leaderboard_pagination(client, admin_headers, member_headers):
    """Test leaderboard pagination"""
    # Create ACTIVE competition
    comp_data = {
        "comp_id": "test-lb-pag",
        "name": "Pagination Competition",
        "registration_open_date": "2025-01-01",
        "start_date": "2025-02-01",
        "end_date": "2025-03-01",
        "max_teams": 10,
        "max_members_per_team": 5,
        "status": "ACTIVE"
    }
    client.post("/competitions", json=comp_data, headers=admin_headers)
    
    # Get user uid
    member_me = client.get("/me", headers=member_headers)
    member_uid = member_me.json()["uid"]
    
    # Create team
    team_data = {
        "name": "Pagination Team",
        "comp_id": "test-lb-pag",
        "owner_uid": member_uid
    }
    client.post("/teams", json=team_data, headers=member_headers)
    
    # Submit steps
    steps = {
        "comp_id": "test-lb-pag",
        "date": "2025-02-15",
        "steps": 10000
    }
    client.post("/ingest/steps", json=steps, headers=member_headers)
    
    # Get leaderboard with pagination
    response = client.get("/leaderboard/individual?comp_id=test-lb-pag&page=1&page_size=10", headers=member_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["rows"]) <= 10

def test_leaderboard_requires_auth(client):
    """Test that leaderboard requires authentication"""
    response = client.get("/leaderboard/individual")
    assert response.status_code == 401
    
    response = client.get("/leaderboard/team")
    assert response.status_code == 401
