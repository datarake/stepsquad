from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta, date as date_type
import os, uuid, logging
from typing import Optional, Literal
from pathlib import Path

# Load environment variables from .env.local file if it exists
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"Loaded environment variables from {env_path}")

from gcp_clients import init_clients
from storage import (
    upsert_user, create_team, update_team, join_team, leave_team, create_competition,
    write_daily_steps, get_user_steps, check_idempotency, is_user_in_team_for_competition,
    individual_leaderboard, team_leaderboard,
    get_user, get_all_users, get_team, get_teams, get_competition, get_competitions, update_competition, delete_competition,
    get_oauth_state_token
)
from pubsub_bus import publish_ingest
from firebase_auth import verify_id_token, get_user_info_from_token
from device_storage import (
    store_device_tokens, get_device_tokens, get_user_devices,
    remove_device_tokens, update_device_sync_time
)
from garmin_client import (
    generate_state_token,
    build_garmin_oauth_url,
    exchange_garmin_code,
    get_garmin_daily_steps,
    refresh_garmin_token
)
from fitbit_client import (
    generate_state_token as fitbit_generate_state_token,
    build_fitbit_oauth_url,
    exchange_fitbit_code,
    get_fitbit_daily_steps,
    refresh_fitbit_token
)

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
    comp_id: str                   # Competition ID (required)
    date: str                      # YYYY-MM-DD in competition TZ
    steps: int = Field(ge=0, le=100000)  # Max 100k steps per day (reasonable limit)
    provider: str = "manual"        # e.g., "garmin", "fitbit", "healthkit", "manual"
    tz: str = COMP_TZ              # client tz (IANA), for traceability
    source_ts: Optional[str] = None # ISO8601 from device sync time (optional for manual)
    idempotency_key: Optional[str] = None  # client-generated to dedupe (optional)

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    comp_id: str
    owner_uid: str

class TeamJoin(BaseModel):
    team_id: str
    uid: str

class TeamUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

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
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_dev_user: Optional[str] = Header(None, alias="X-Dev-User")
) -> User:
    GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
    ALLOW_DEV_AUTH_LOCAL = os.getenv("ALLOW_DEV_AUTH_LOCAL", "false").lower() == "true"
    
    # Log authentication attempt for debugging (without sensitive data)
    logging.debug(f"Auth attempt: GCP_ENABLED={GCP_ENABLED}, has_auth={bool(authorization)}, has_dev={bool(x_dev_user)}")
    
    # Dev mode authentication (when GCP_ENABLED=false OR when ALLOW_DEV_AUTH_LOCAL=true)
    # This allows testing with Firestore locally while using dev auth
    if (not GCP_ENABLED or ALLOW_DEV_AUTH_LOCAL) and x_dev_user:
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
    if GCP_ENABLED:
        if not authorization:
            logging.warning("GCP_ENABLED=true but no authorization header provided")
            raise HTTPException(status_code=401, detail="Authentication required: Authorization header missing")
        
        if not authorization.startswith("Bearer "):
            logging.warning(f"Invalid authorization header format: {authorization[:20]}...")
            raise HTTPException(status_code=401, detail="Invalid authorization header format. Expected 'Bearer <token>'")
        
        token = authorization.split(" ", 1)[1]  # Use split with maxsplit to handle tokens with spaces
        
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
            error_msg = str(e)
            logging.warning(f"Firebase token verification failed: {error_msg}", exc_info=True)
            # Return more detailed error for debugging
            raise HTTPException(status_code=401, detail=error_msg)
        except Exception as e:
            logging.error(f"Unexpected error during Firebase auth: {e}", exc_info=True)
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
    # No valid authentication provided
    logging.warning(f"Authentication failed: GCP_ENABLED={GCP_ENABLED}, has_auth={bool(authorization)}, has_dev={bool(x_dev_user)}")
    raise HTTPException(status_code=401, detail="Authentication required")

@app.get("/health")
def health():
    """Health check endpoint with system status"""
    from firebase_auth import init_firebase
    
    gcp_enabled = os.getenv("GCP_ENABLED", "false").lower() == "true"
    firebase_status = "not_initialized"
    firebase_project = None
    
    if gcp_enabled:
        try:
            firebase_app = init_firebase()
            if firebase_app:
                firebase_status = "initialized"
                firebase_project = firebase_app.project_id
            else:
                firebase_status = "failed_to_initialize"
        except Exception as e:
            firebase_status = f"error: {str(e)}"
            logging.error(f"Firebase initialization check failed: {e}", exc_info=True)
    
    health_status = {
        "ok": True,
        "time": datetime.utcnow().isoformat(),
        "tz": COMP_TZ,
        "gcp_enabled": gcp_enabled,
        "firebase": {
            "status": firebase_status,
            "project": firebase_project,
            "expected_firebase_project": os.getenv("FIREBASE_PROJECT_ID") or "stepsquad-46d14",
            "gcp_project": os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID") or "not set"
        },
    }
    
    return health_status

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
def ingest_steps(e: StepIngest, current_user: User = Depends(get_current_user)):
    """
    Submit step data for a competition.
    
    Validation:
    - User must be authenticated
    - User must be in a team for the competition
    - Competition must exist and be ACTIVE
    - Date must be within competition date range (with grace days)
    - Steps must be between 0 and 100,000
    - Idempotency key must be unique (if provided)
    """
    uid = current_user.uid
    
    # Validate competition exists
    competition = get_competition(e.comp_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Validate competition status
    if competition.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail=f"Step submission only allowed for ACTIVE competitions. Current status: {competition.get('status')}"
        )
    
    # Validate user is in a team for this competition
    if not is_user_in_team_for_competition(uid, e.comp_id):
        raise HTTPException(
            status_code=403,
            detail="You must be a member of a team in this competition to submit steps"
        )
    
    # Validate date is within competition date range (with grace days)
    try:
        step_date = datetime.strptime(e.date, "%Y-%m-%d").date()
        start_date = datetime.strptime(competition.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(competition.get("end_date"), "%Y-%m-%d").date()
        grace_end_date = end_date + timedelta(days=GRACE_DAYS)
        
        if step_date < start_date:
            raise HTTPException(
                status_code=400,
                detail=f"Date {e.date} is before competition start date {competition.get('start_date')}"
            )
        if step_date > grace_end_date:
            raise HTTPException(
                status_code=400,
                detail=f"Date {e.date} is after competition end date + grace period ({grace_end_date.isoformat()})"
            )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e.date}. Expected YYYY-MM-DD")
    
    # Validate step count
    if e.steps < 0:
        raise HTTPException(status_code=400, detail="Step count cannot be negative")
    if e.steps > 100000:
        raise HTTPException(status_code=400, detail="Step count exceeds maximum allowed (100,000 steps per day)")
    
    # Check idempotency if key provided
    if e.idempotency_key:
        if check_idempotency(e.idempotency_key, uid, e.date):
            raise HTTPException(
                status_code=409,
                detail="Duplicate submission detected. This idempotency key has already been used."
            )
    
    # Store the steps
    write_daily_steps(uid, e.date, e.steps)
    
    # Publish to Pub/Sub for async processing
    try:
        publish_ingest({
            "user_id": uid,
            "comp_id": e.comp_id,
            "date": e.date,
            "steps": e.steps,
            "provider": e.provider,
            "tz": e.tz,
            "source_ts": e.source_ts,
            "idempotency_key": e.idempotency_key,
        })
    except Exception as pubsub_error:
        # Log error but don't fail the request since steps are already stored
        logging.warning(f"Failed to publish step ingestion event to Pub/Sub: {pubsub_error}")
    
    logging.info(f"User {current_user.email} submitted {e.steps} steps for competition {e.comp_id} on {e.date}")
    
    return {
        "status": "success",
        "stored": True,
        "user_id": uid,
        "comp_id": e.comp_id,
        "date": e.date,
        "steps": e.steps
    }

@app.get("/users/{uid}/steps")
def get_user_step_history(uid: str, comp_id: str | None = None, current_user: User = Depends(get_current_user)):
    """Get step history for a user (own steps or admin viewing other users)"""
    # Users can only view their own steps, unless they're admin
    if uid != current_user.uid and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only view your own step history")
    
    steps = get_user_steps(uid, comp_id)
    return {"rows": steps}

@app.get("/leaderboard/individual")
def leaderboard_individual(
    comp_id: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    team_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
):
    """
    Get individual leaderboard.
    
    Query parameters:
    - comp_id: Filter by competition
    - date: Filter by specific date (YYYY-MM-DD)
    - start_date: Filter by date range start (YYYY-MM-DD)
    - end_date: Filter by date range end (YYYY-MM-DD)
    - team_id: Filter by team
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    """
    # Validate pagination
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    
    # Get all results
    rows = individual_leaderboard(
        comp_id=comp_id,
        date=date,
        start_date=start_date,
        end_date=end_date,
        team_id=team_id,
    )
    
    # Apply pagination
    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_rows = rows[start:end]
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "rows": paginated_rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

@app.get("/leaderboard/team")
def leaderboard_team(
    comp_id: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
):
    """
    Get team leaderboard.
    
    Query parameters:
    - comp_id: Filter by competition (required for competition-specific leaderboards)
    - date: Filter by specific date (YYYY-MM-DD)
    - start_date: Filter by date range start (YYYY-MM-DD)
    - end_date: Filter by date range end (YYYY-MM-DD)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)
    """
    # Validate pagination
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    
    # Get all results
    rows = team_leaderboard(
        comp_id=comp_id,
        date=date,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Apply pagination
    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_rows = rows[start:end]
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "rows": paginated_rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

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
    
    # Check if user is already in a team in this competition
    if is_user_in_team_for_competition(current_user.uid, body.comp_id):
        raise HTTPException(
            status_code=409,
            detail="You are already a member of a team in this competition. Please leave your current team before creating a new one."
        )
    
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
        # Check if user is already in another team in this competition
        if is_user_in_team_for_competition(body.uid, comp_id):
            raise HTTPException(
                status_code=409,
                detail="You are already a member of a team in this competition. Please leave your current team before joining another one."
            )
        
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
    
    # Log team details for debugging
    logging.info(f"Leave team request: team_id={team_id}, uid={uid}, owner_uid={team.get('owner_uid')}, members={team.get('members', [])}, current_user.uid={current_user.uid}")
    
    # Team owner cannot leave their own team (even if only member)
    if team.get("owner_uid") == uid:
        raise HTTPException(
            status_code=422,
            detail="Team owner cannot leave their own team."
        )
    
    # Check if user is a member
    members = team.get("members", [])
    if uid not in members:
        logging.warning(f"User {uid} not found in team members: {members}")
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    # Leave team
    success = leave_team(team_id, uid)
    if not success:
        # Log for debugging
        logging.warning(f"Failed to leave team: team_id={team_id}, uid={uid}, members={team.get('members', [])}")
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    logging.info(f"User {current_user.email} left team {team_id}")
    
    return {"ok": True}

@app.patch("/teams/{team_id}")
def api_update_team(team_id: str, body: TeamUpdate, current_user: User = Depends(get_current_user)):
    """Update team name (only owner can update)"""
    # Get team details
    team = get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify user is the team owner
    if team.get("owner_uid") != current_user.uid:
        raise HTTPException(status_code=403, detail="Only the team owner can update the team name")
    
    # Update team name
    success = update_team(team_id, body.name)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    
    logging.info(f"User {current_user.email} updated team {team_id} name to {body.name}")
    
    return {"ok": True, "team_id": team_id, "name": body.name}

def calculate_competition_status(competition_data: dict, existing_status: str = None) -> str:
    """
    Calculate the appropriate competition status based on dates.
    Automatically updates status based on current date relative to competition dates.
    """
    now = datetime.utcnow().date()
    status = existing_status or competition_data.get('status', 'DRAFT')
    
    # Get dates (handle both string and date objects)
    reg_date_str = competition_data.get('registration_open_date')
    start_date_str = competition_data.get('start_date')
    end_date_str = competition_data.get('end_date')
    
    if not reg_date_str or not start_date_str or not end_date_str:
        return status
    
    try:
        # Parse dates - handle both YYYY-MM-DD format and ISO datetime strings
        def parse_date(date_value):
            if isinstance(date_value, date_type):
                return date_value
            if isinstance(date_value, str):
                # Try ISO format first (with timezone)
                try:
                    return datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
                except ValueError:
                    # Try simple YYYY-MM-DD format
                    return datetime.strptime(date_value.split('T')[0], '%Y-%m-%d').date()
            return None
        
        reg_date = parse_date(reg_date_str)
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        
        if not reg_date or not start_date or not end_date:
            return status
    except (ValueError, AttributeError, TypeError) as e:
        # If date parsing fails, return current status
        logging.warning(f"Failed to parse competition dates: {e}")
        return status
    
    # Auto-update status based on dates
    # Only auto-update if status is DRAFT, REGISTRATION, or ACTIVE (don't override ENDED or ARCHIVED)
    if status in ['DRAFT', 'REGISTRATION', 'ACTIVE']:
        if now >= end_date:
            return 'ENDED'
        elif now >= start_date:
            return 'ACTIVE'
        elif now >= reg_date:
            return 'REGISTRATION'
        else:
            return 'DRAFT'
    
    return status

@app.post("/competitions")
def api_create_competition(body: CompetitionCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if competition with this comp_id already exists
    existing = get_competition(body.comp_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Competition with comp_id '{body.comp_id}' already exists")
    
    competition_data = body.model_dump()
    
    # Auto-calculate status based on dates
    calculated_status = calculate_competition_status(competition_data, competition_data.get('status'))
    competition_data['status'] = calculated_status
    
    competition_data.update({
        "created_by": current_user.uid,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    
    create_competition(body.comp_id, competition_data)
    
    # Log admin action
    logging.info(f"Admin {current_user.email} created competition {body.comp_id}: {body.name} with status {calculated_status}")
    
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
    
    # Get current values for validation (merge with existing competition data)
    merged_data = {**competition, **update_data}
    reg_date = merged_data.get('registration_open_date')
    start_date = merged_data.get('start_date')
    end_date = merged_data.get('end_date')
    
    # Validate date ordering
    if reg_date and start_date and reg_date > start_date:
        raise HTTPException(status_code=422, detail="registration_open_date must be before start_date")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    
    # Auto-calculate status based on dates if status wasn't explicitly set
    # Only auto-update if status wasn't in the update_data (let admins override if they explicitly set status)
    if 'status' not in update_data:
        calculated_status = calculate_competition_status(merged_data, competition.get('status'))
        if calculated_status != competition.get('status'):
            update_data['status'] = calculated_status
            logging.info(f"Auto-updated competition {comp_id} status from {competition.get('status')} to {calculated_status} based on dates")
    
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


# ============================================================================
# OAuth Device Integration Endpoints
# ============================================================================

@app.get("/oauth/garmin/authorize")
async def garmin_authorize(current_user: User = Depends(get_current_user)):
    """
    Initiate Garmin OAuth flow
    
    Returns authorization URL for user to redirect to Garmin
    """
    try:
        # Check if user already has a device connected
        existing_devices = get_user_devices(current_user.uid)
        if existing_devices:
            existing_provider = existing_devices[0].get("provider")
            raise HTTPException(
                status_code=400,
                detail=f"You already have a {existing_provider} device connected. Only one device can be connected at a time. Please unlink your {existing_provider} device first."
            )
        
        # Generate state token for CSRF protection
        state = generate_state_token(current_user.uid)
        
        # Build OAuth authorization URL
        authorization_url = build_garmin_oauth_url(state)
        
        return {
            "authorization_url": authorization_url,
            "state": state,
            "provider": "garmin"
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error initiating Garmin OAuth: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate Garmin OAuth")


@app.get("/oauth/garmin/callback")
async def garmin_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    oauth_token: Optional[str] = Query(None),  # OAuth 1.0a request token
    oauth_verifier: Optional[str] = Query(None),  # OAuth 1.0a verifier
    error: Optional[str] = Query(None),
):
    """
    Handle Garmin OAuth callback
    
    Garmin uses OAuth 1.0a, which has a different flow:
    1. Request token → 2. Authorization → 3. Access token
    
    This endpoint handles step 2 (authorization) and 3 (access token).
    This endpoint doesn't require authentication because Garmin redirects here
    without auth headers. We identify the user from the state token.
    """
    try:
        # Check for OAuth errors
        if error:
            raise HTTPException(status_code=400, detail=f"Garmin OAuth error: {error}")
        
        if not state:
            raise HTTPException(status_code=400, detail="State parameter required")
        
        # Look up user from state token
        state_data = get_oauth_state_token(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid or expired state token")
        
        uid = state_data.get("uid")
        if not uid:
            raise HTTPException(status_code=400, detail="User not found in state token")
        
        # Check if user already has a different device connected
        existing_devices = get_user_devices(uid)
        if existing_devices:
            existing_provider = existing_devices[0].get("provider")
            if existing_provider != "garmin":
                raise HTTPException(
                    status_code=400,
                    detail=f"You already have a {existing_provider} device connected. Only one device can be connected at a time. Please unlink your {existing_provider} device first."
                )
        
        # Exchange authorization for access token
        # Garmin uses OAuth 1.0a, so we need oauth_token and oauth_verifier
        if oauth_token and oauth_verifier:
            # Exchange request token for access token
            tokens = exchange_garmin_code(oauth_verifier, oauth_token)
        elif code:
            # If using OAuth 2.0 (newer Garmin API)
            tokens = exchange_garmin_code(code)
        else:
            raise HTTPException(status_code=400, detail="OAuth parameters missing")
        
        # Store tokens for user
        store_device_tokens(uid, "garmin", tokens)
        
        # Get user info for logging
        user = get_user(uid)
        email = user.get("email", "unknown") if user else "unknown"
        logging.info(f"User {email} (uid: {uid}) linked Garmin device")
        
        # Return HTML page that redirects to frontend
        frontend_url = os.getenv("VITE_WEB_URL", "https://stepsquad.club")
        # Build redirect URL with all OAuth parameters
        redirect_params = []
        if code:
            redirect_params.append(f"code={code}")
        if state:
            redirect_params.append(f"state={state}")
        if oauth_token:
            redirect_params.append(f"oauth_token={oauth_token}")
        if oauth_verifier:
            redirect_params.append(f"oauth_verifier={oauth_verifier}")
        redirect_params.append("status=success")
        
        return RedirectResponse(
            url=f"{frontend_url}/oauth/garmin/callback?{'&'.join(redirect_params)}",
            status_code=302
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error in Garmin OAuth callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to complete Garmin OAuth")


@app.get("/oauth/fitbit/authorize")
async def fitbit_authorize(current_user: User = Depends(get_current_user)):
    """
    Initiate Fitbit OAuth 2.0 flow
    
    Returns authorization URL for user to redirect to Fitbit
    """
    try:
        # Check if user already has a device connected
        existing_devices = get_user_devices(current_user.uid)
        if existing_devices:
            existing_provider = existing_devices[0].get("provider")
            raise HTTPException(
                status_code=400,
                detail=f"You already have a {existing_provider} device connected. Only one device can be connected at a time. Please unlink your {existing_provider} device first."
            )
        
        # Generate state token for CSRF protection
        state = fitbit_generate_state_token(current_user.uid)
        
        # Build OAuth authorization URL
        authorization_url = build_fitbit_oauth_url(state)
        
        return {
            "authorization_url": authorization_url,
            "state": state,
            "provider": "fitbit"
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error initiating Fitbit OAuth: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initiate Fitbit OAuth")


@app.get("/oauth/fitbit/callback")
async def fitbit_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
):
    """
    Handle Fitbit OAuth 2.0 callback
    
    Fitbit uses OAuth 2.0 authorization code flow.
    This endpoint doesn't require authentication because Fitbit redirects here
    without auth headers. We identify the user from the state token.
    """
    try:
        # Check for OAuth errors
        if error:
            raise HTTPException(status_code=400, detail=f"Fitbit OAuth error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code required")
        
        if not state:
            raise HTTPException(status_code=400, detail="State parameter required")
        
        # Look up user from state token
        state_data = get_oauth_state_token(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid or expired state token")
        
        uid = state_data.get("uid")
        if not uid:
            raise HTTPException(status_code=400, detail="User not found in state token")
        
        # Check if user already has a different device connected
        existing_devices = get_user_devices(uid)
        if existing_devices:
            existing_provider = existing_devices[0].get("provider")
            if existing_provider != "fitbit":
                raise HTTPException(
                    status_code=400,
                    detail=f"You already have a {existing_provider} device connected. Only one device can be connected at a time. Please unlink your {existing_provider} device first."
                )
        
        # Exchange authorization code for access token
        tokens = exchange_fitbit_code(code)
        
        # Store tokens for user
        store_device_tokens(uid, "fitbit", tokens)
        
        # Get user info for logging
        user = get_user(uid)
        email = user.get("email", "unknown") if user else "unknown"
        logging.info(f"User {email} (uid: {uid}) linked Fitbit device")
        
        # Return HTML page that redirects to frontend
        frontend_url = os.getenv("VITE_WEB_URL", "https://stepsquad.club")
        return RedirectResponse(
            url=f"{frontend_url}/oauth/fitbit/callback?code={code}&state={state}&status=success",
            status_code=302
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error in Fitbit OAuth callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to complete Fitbit OAuth")


@app.get("/devices")
async def list_devices(current_user: User = Depends(get_current_user)):
    """
    List all linked devices for the current user
    
    Returns list of linked devices with sync status
    """
    try:
        devices = get_user_devices(current_user.uid)
        return {
            "devices": devices,
            "count": len(devices)
        }
    
    except Exception as e:
        logging.error(f"Error listing devices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list devices")


@app.post("/devices/{provider}/sync")
async def sync_device(
    provider: str,
    date: Optional[str] = Query(None),  # Optional: sync specific date (YYYY-MM-DD)
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger device sync for a specific provider
    
    Syncs steps from the linked device for today or specified date
    """
    if provider not in ["garmin", "fitbit"]:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Supported: garmin, fitbit")
    
    try:
        # Get stored tokens
        device_data = get_device_tokens(current_user.uid, provider)
        
        if not device_data:
            raise HTTPException(status_code=404, detail=f"{provider.capitalize()} device not linked")
        
        tokens = device_data.get("tokens", {})
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail=f"{provider.capitalize()} access token not found")
        
        # Determine date to sync
        if date:
            try:
                sync_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            sync_date = datetime.now().date()
        
        # Fetch steps from device API
        if provider == "garmin":
            steps = get_garmin_daily_steps(access_token, sync_date)
        elif provider == "fitbit":
            steps = get_fitbit_daily_steps(access_token, sync_date)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        # Find user's active competitions and sync steps to each
        # Get all competitions and check if user is in a team
        all_competitions = get_competitions()
        user_competitions = []
        
        for competition in all_competitions:
            comp_id = competition.get("comp_id")
            if not comp_id:
                continue
            
            # Check if competition is ACTIVE
            if competition.get("status") != "ACTIVE":
                continue
            
            # Check if user is in a team for this competition
            if not is_user_in_team_for_competition(current_user.uid, comp_id):
                continue
            
            # Check if date is within competition range (with grace days)
            try:
                comp_start = datetime.strptime(competition.get("start_date"), "%Y-%m-%d").date()
                comp_end = datetime.strptime(competition.get("end_date"), "%Y-%m-%d").date()
                grace_end = comp_end + timedelta(days=GRACE_DAYS)
                
                if comp_start <= sync_date <= grace_end:
                    user_competitions.append(comp_id)
            except (ValueError, KeyError) as e:
                logging.warning(f"Error checking date range for competition {comp_id}: {e}")
                continue
        
        # Submit steps to each active competition
        submissions = []
        for comp_id in user_competitions:
            try:
                # Use existing ingest endpoint logic
                # Check idempotency
                idempotency_key = f"{provider}_{sync_date.isoformat()}_{current_user.uid}"
                if not check_idempotency(idempotency_key, current_user.uid, sync_date.isoformat()):
                    # Write steps for this competition
                    write_daily_steps(current_user.uid, sync_date.isoformat(), steps)
                    
                    # Publish to Pub/Sub
                    try:
                        publish_ingest({
                            "user_id": current_user.uid,
                            "comp_id": comp_id,
                            "date": sync_date.isoformat(),
                            "steps": steps,
                            "provider": provider,
                            "tz": COMP_TZ,
                            "source_ts": datetime.utcnow().isoformat(),
                            "idempotency_key": idempotency_key,
                        })
                    except Exception as pubsub_error:
                        logging.warning(f"Failed to publish step ingestion event to Pub/Sub: {pubsub_error}")
                    
                    submissions.append({
                        "comp_id": comp_id,
                        "status": "submitted",
                        "steps": steps
                    })
            except Exception as e:
                logging.warning(f"Failed to submit steps to competition {comp_id}: {e}")
                submissions.append({
                    "comp_id": comp_id,
                    "status": "error",
                    "error": str(e)
                })
        
        # Update sync time
        update_device_sync_time(current_user.uid, provider)
        
        logging.info(f"User {current_user.email} synced {steps} steps from {provider} for {sync_date}, submitted to {len(submissions)} competitions")
        
        return {
            "status": "success",
            "provider": provider,
            "date": sync_date.isoformat(),
            "steps": steps,
            "competitions": submissions,
            "submitted_count": len([s for s in submissions if s.get("status") == "submitted"]),
            "message": f"Synced {steps} steps from {provider} and submitted to {len([s for s in submissions if s.get('status') == 'submitted'])} competition(s)"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error syncing {provider} device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to sync {provider} device: {str(e)}")


@app.delete("/devices/{provider}")
async def unlink_device(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """
    Unlink a device (remove stored OAuth tokens)
    
    User can unlink their Garmin or Fitbit device
    """
    if provider not in ["garmin", "fitbit"]:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Supported: garmin, fitbit")
    
    try:
        # Check if device is linked
        device_data = get_device_tokens(current_user.uid, provider)
        
        if not device_data:
            raise HTTPException(status_code=404, detail=f"{provider.capitalize()} device not linked")
        
        # Remove tokens
        removed = remove_device_tokens(current_user.uid, provider)
        
        if removed:
            logging.info(f"User {current_user.email} unlinked {provider} device")
            return {
                "status": "success",
                "provider": provider,
                "message": f"{provider.capitalize()} device unlinked successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to unlink {provider} device")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error unlinking {provider} device: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to unlink {provider} device")


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
