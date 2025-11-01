from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime
import os, uuid, logging
from typing import Optional, Literal

from gcp_clients import init_clients
from storage import (
    upsert_user, create_team, join_team, leave_team, create_competition,
    write_daily_steps, individual_leaderboard, team_leaderboard,
    get_user, get_all_users, get_team, get_teams, get_competition, get_competitions, update_competition, delete_competition
)
from pubsub_bus import publish_ingest
from firebase_auth import verify_id_token, get_user_info_from_token

app = FastAPI(title="StepSquad API", version="0.5.0")
init_clients()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMP_TZ = os.getenv("COMP_TZ", "Europe/Bucharest")
GRACE_DAYS = int(os.getenv("GRACE_DAYS", "2"))

class StepIngest(BaseModel):
    user_id: str
    date: str                      # YYYY-MM-DD in competition TZ
    steps: int = Field(ge=0)
    provider: str                  # e.g., "garmin", "fitbit", "healthkit"
    tz: str                        # client tz (IANA), for traceability
    source_ts: str                 # ISO8601 from device sync time
    idempotency_key: str           # client-generated to dedupe

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    comp_id: str
    owner_uid: str

class TeamJoin(BaseModel):
    team_id: str
    uid: str

class CompetitionCreate(BaseModel):
    comp_id: str
    name: str
    tz: Optional[str] = COMP_TZ
    status: Optional[Literal["DRAFT", "REGISTRATION", "ACTIVE", "ENDED", "ARCHIVED"]] = "DRAFT"
    registration_open_date: str
    start_date: str
    end_date: str
    max_teams: Optional[int] = 10
    max_members_per_team: Optional[int] = 10

    @validator('registration_open_date', 'start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('max_teams')
    def validate_max_teams(cls, v):
        if v is not None and (v < 1 or v > 500):
            raise ValueError('max_teams must be between 1 and 500')
        return v

    @validator('max_members_per_team')
    def validate_max_members_per_team(cls, v):
        if v is not None and (v < 1 or v > 200):
            raise ValueError('max_members_per_team must be between 1 and 200')
        return v

    @validator('end_date')
    def validate_date_ordering(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('start_date')
    def validate_start_date(cls, v, values):
        if 'registration_open_date' in values and v < values['registration_open_date']:
            raise ValueError('start_date must be after registration_open_date')
        return v

class CompetitionUpdate(BaseModel):
    name: Optional[str] = None
    tz: Optional[str] = None
    status: Optional[Literal["DRAFT", "REGISTRATION", "ACTIVE", "ENDED", "ARCHIVED"]] = None
    registration_open_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_teams: Optional[int] = None
    max_members_per_team: Optional[int] = None

    @validator('registration_open_date', 'start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @validator('max_teams')
    def validate_max_teams(cls, v):
        if v is not None and (v < 1 or v > 500):
            raise ValueError('max_teams must be between 1 and 500')
        return v

    @validator('max_members_per_team')
    def validate_max_members_per_team(cls, v):
        if v is not None and (v < 1 or v > 200):
            raise ValueError('max_members_per_team must be between 1 and 200')
        return v

class User(BaseModel):
    uid: str
    email: str
    role: Literal["ADMIN", "MEMBER"]

# Authentication dependency
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_dev_user: Optional[str] = Header(None)
) -> User:
    GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
    
    # Dev mode authentication (only when GCP_ENABLED=false)
    if not GCP_ENABLED and x_dev_user:
        user_data = get_user(x_dev_user)
        if not user_data:
            # Create user if doesn't exist
            role = "ADMIN" if x_dev_user.lower() == "admin@stepsquad.com" else "MEMBER"
            now = datetime.utcnow().isoformat()
            user_data = {
                "uid": x_dev_user,
                "email": x_dev_user.lower(),
                "role": role,
                "created_at": now,
                "updated_at": now
            }
            upsert_user(x_dev_user, user_data)
        return User(**user_data)
    
    # Firebase authentication (production mode)
    if GCP_ENABLED and authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.split(" ")[1]
        
        try:
            # Verify Firebase ID token
            decoded_token = verify_id_token(token)
            user_info = get_user_info_from_token(decoded_token)
            
            # Get or create user in our system
            uid = user_info['uid']
            user_data = get_user(uid)
            
            if not user_data:
                # Create user if doesn't exist
                now = datetime.utcnow().isoformat()
                user_data = {
                    **user_info,
                    "created_at": now,
                    "updated_at": now
                }
                upsert_user(uid, user_data)
            else:
                # Update user role if it changed (for custom claims)
                if user_data.get('role') != user_info['role']:
                    user_data['role'] = user_info['role']
                    user_data['updated_at'] = datetime.utcnow().isoformat()
                    upsert_user(uid, user_data)
            
            return User(**user_data)
            
        except ValueError as e:
            logging.warning(f"Firebase token verification failed: {e}")
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logging.error(f"Unexpected error during Firebase auth: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    # No valid authentication provided
    raise HTTPException(status_code=401, detail="Authentication required")

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat(), "tz": COMP_TZ}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users")
def get_users_list(current_user: User = Depends(get_current_user)):
    """List all users (ADMIN only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = get_all_users()
    return {"rows": users}

@app.get("/users/{uid}")
def get_user_detail(uid: str, current_user: User = Depends(get_current_user)):
    """Get user details (ADMIN only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user_data = get_user(uid)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_data

@app.patch("/users/{uid}")
def update_user_role(
    uid: str, 
    role: str,
    current_user: User = Depends(get_current_user)
):
    """Update user role (ADMIN only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if role not in ["ADMIN", "MEMBER"]:
        raise HTTPException(status_code=422, detail="Role must be ADMIN or MEMBER")
    
    user_data = get_user(uid)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data["role"] = role
    user_data["updated_at"] = datetime.utcnow().isoformat()
    upsert_user(uid, user_data)
    
    logging.info(f"Admin {current_user.email} updated user {uid} role to {role}")
    
    return {"ok": True}

@app.get("/competitions")
def get_competitions_list(
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
    tz: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """List competitions with optional filtering, search, and pagination"""
    competitions = get_competitions(status=status, tz=tz, search=search)
    
    # Pagination
    total = len(competitions)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_competitions = competitions[start:end]
    
    return {
        "rows": paginated_competitions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
    }

@app.get("/competitions/{comp_id}")
def get_competition_detail(comp_id: str, current_user: User = Depends(get_current_user)):
    competition = get_competition(comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition

@app.post("/ingest/steps")
def ingest_steps(e: StepIngest):
    write_daily_steps(e.user_id, e.date, e.steps)
    publish_ingest(e.model_dump())
    return {"status": "queued", "stored": True}

@app.get("/leaderboard/individual")
def leaderboard_individual(date: str | None = None):
    return {"rows": individual_leaderboard(date)}

@app.get("/leaderboard/team")
def leaderboard_team(date: str | None = None):
    return {"rows": team_leaderboard(date)}

@app.get("/competitions/{comp_id}/teams")
def get_competition_teams(comp_id: str, current_user: User = Depends(get_current_user)):
    """Get all teams for a competition"""
    # Verify competition exists
    competition = get_competition(comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    teams = get_teams(comp_id=comp_id)
    return {"rows": teams}

@app.get("/teams/{team_id}")
def get_team_detail(team_id: str, current_user: User = Depends(get_current_user)):
    """Get team details with members"""
    team = get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team

@app.post("/teams")
def api_create_team(body: TeamCreate, current_user: User = Depends(get_current_user)):
    """Create a team for a competition"""
    # Verify competition exists
    competition = get_competition(body.comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Check if competition is in registration or active phase
    status = competition.get("status", "").upper()
    if status not in ["REGISTRATION", "ACTIVE"]:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot create teams for competition with status {status}. Competition must be in REGISTRATION or ACTIVE status."
        )
    
    # Check if max teams reached
    existing_teams = get_teams(comp_id=body.comp_id)
    max_teams = competition.get("max_teams", 500)
    if len(existing_teams) >= max_teams:
        raise HTTPException(
            status_code=409,
            detail=f"Maximum number of teams ({max_teams}) reached for this competition"
        )
    
    # Verify owner is authenticated user
    if body.owner_uid != current_user.uid:
        raise HTTPException(status_code=403, detail="Cannot create team for another user")
    
    # Create team
    team_id = uuid.uuid4().hex[:8]
    create_team(team_id, body.name, body.owner_uid, body.comp_id)
    
    logging.info(f"User {current_user.email} created team {team_id} for competition {body.comp_id}")
    
    return {"team_id": team_id, "name": body.name, "comp_id": body.comp_id}

@app.post("/teams/join")
def api_join_team(body: TeamJoin, current_user: User = Depends(get_current_user)):
    """Join an existing team"""
    # Get team details
    team = get_team(body.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify user is joining their own team (or allow if not)
    if body.uid != current_user.uid:
        raise HTTPException(status_code=403, detail="Cannot join team for another user")
    
    # Check if user is already a member
    if body.uid in team.get("members", []):
        raise HTTPException(status_code=409, detail="User is already a member of this team")
    
    # Get competition to check limits
    comp_id = team.get("comp_id")
    if comp_id:
        competition = get_competition(comp_id)
        if competition:
            max_members = competition.get("max_members_per_team", 200)
            if len(team.get("members", [])) >= max_members:
                raise HTTPException(
                    status_code=409,
                    detail=f"Team is full. Maximum {max_members} members allowed."
                )
            
            # Check competition status
            status = competition.get("status", "").upper()
            if status not in ["REGISTRATION", "ACTIVE"]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Cannot join teams for competition with status {status}. Competition must be in REGISTRATION or ACTIVE status."
                )
    
    # Join team
    join_team(body.team_id, body.uid)
    
    logging.info(f"User {current_user.email} joined team {body.team_id}")
    
    return {"ok": True, "team_id": body.team_id}

@app.delete("/teams/{team_id}/members/{uid}")
def api_leave_team(team_id: str, uid: str, current_user: User = Depends(get_current_user)):
    """Leave a team (remove member)"""
    # Verify user can only leave their own team
    if uid != current_user.uid:
        raise HTTPException(status_code=403, detail="Cannot remove another user from team")
    
    # Get team details
    team = get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is a member
    if uid not in team.get("members", []):
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    # Cannot leave if user is the owner (optional - you might want to allow this)
    if team.get("owner_uid") == uid and len(team.get("members", [])) > 1:
        raise HTTPException(
            status_code=422,
            detail="Team owner cannot leave. Transfer ownership or delete team first."
        )
    
    # Leave team
    success = leave_team(team_id, uid)
    if not success:
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    logging.info(f"User {current_user.email} left team {team_id}")
    
    return {"ok": True}

@app.post("/competitions")
def api_create_competition(body: CompetitionCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if competition with this comp_id already exists
    existing = get_competition(body.comp_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Competition with comp_id '{body.comp_id}' already exists")
    
    competition_data = body.model_dump()
    competition_data.update({
        "created_by": current_user.uid,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    
    create_competition(body.comp_id, competition_data)
    
    # Log admin action
    logging.info(f"Admin {current_user.email} created competition {body.comp_id}: {body.name}")
    
    return {"ok": True, "comp_id": body.comp_id}

@app.patch("/competitions/{comp_id}")
def api_update_competition(comp_id: str, body: CompetitionUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    competition = get_competition(comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Additional validation for date ordering when updating dates
    update_data = body.model_dump(exclude_unset=True)
    
    # Get current values for validation
    reg_date = update_data.get('registration_open_date', competition.get('registration_open_date'))
    start_date = update_data.get('start_date', competition.get('start_date'))
    end_date = update_data.get('end_date', competition.get('end_date'))
    
    # Validate date ordering
    if reg_date and start_date and reg_date > start_date:
        raise HTTPException(status_code=422, detail="registration_open_date must be before start_date")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    update_competition(comp_id, update_data)
    
    # Log admin action
    fields_updated = list(update_data.keys())
    logging.info(f"Admin {current_user.email} updated competition {comp_id}: {fields_updated}")
    
    return {"ok": True}

@app.delete("/competitions/{comp_id}")
def api_delete_competition(comp_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    competition = get_competition(comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Soft delete: set status to ARCHIVED
    update_data = {
        "status": "ARCHIVED",
        "updated_at": datetime.utcnow().isoformat()
    }
    update_competition(comp_id, update_data)
    
    # Log admin action
    logging.info(f"Admin {current_user.email} archived competition {comp_id}: {competition.get('name')}")
    
    return {"ok": True}

@app.post("/dev/seed")
def dev_seed():
    # Create users with roles
    admin_email = os.getenv("VITE_ADMIN_EMAIL", "admin@stepsquad.com")
    upsert_user("u1", {"email": "a@x", "role": "MEMBER"})
    upsert_user("u2", {"email": "b@x", "role": "MEMBER"})
    upsert_user("u3", {"email": "c@x", "role": "MEMBER"})
    upsert_user(admin_email, {"email": admin_email, "role": "ADMIN"})

    create_team("t1", "Falcons", "u1")
    join_team("t1", "u2")
    create_team("t2", "Panthers", "u3")

    # Create competitions with new structure
    create_competition("c1", {
        "comp_id": "c1",
        "name": "Demo Cup",
        "status": "ACTIVE",
        "tz": COMP_TZ,
        "registration_open_date": "2025-09-01",
        "start_date": "2025-10-01",
        "end_date": "2025-12-31",
        "max_teams": 10,
        "max_members_per_team": 5,
        "created_by": admin_email,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })

    create_competition("c2", {
        "comp_id": "c2",
        "name": "Spring Challenge",
        "status": "DRAFT",
        "tz": COMP_TZ,
        "registration_open_date": "2025-03-01",
        "start_date": "2025-04-01",
        "end_date": "2025-06-30",
        "max_teams": 20,
        "max_members_per_team": 8,
        "created_by": admin_email,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })

    write_daily_steps("u1", "2025-10-24", 8200)
    write_daily_steps("u2", "2025-10-24", 10400)
    write_daily_steps("u3", "2025-10-24", 5600)
    write_daily_steps("u1", "2025-10-25", 9200)
    write_daily_steps("u2", "2025-10-25", 7000)
    write_daily_steps("u3", "2025-10-25", 14000)
    return {"ok": True}
