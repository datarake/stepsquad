from __future__ import annotations
from typing import Dict, Tuple, List, Optional
import os
from gcp_clients import fs, bq
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
BQ_DATASET = os.getenv("BQ_DATASET", "stepsquad")
USERS: Dict[str, dict] = {}
TEAMS: Dict[str, dict] = {}
COMPETITIONS: Dict[str, dict] = {}
DAILY_STEPS: Dict[Tuple[str, str], int] = {}
TEAM_MEMBERS: Dict[str, List[str]] = {}
IDEMPOTENCY_KEYS: Dict[str, str] = {}  # idempotency_key -> date mapping
OAUTH_STATE_TOKENS: Dict[str, Dict[str, str]] = {}  # state_token -> {uid, provider} mapping
def _fs_coll(name: str):
    return fs().collection(name) if fs() else None
def upsert_user(uid: str, data: dict):
    if GCP_ENABLED and _fs_coll("users"):
        _fs_coll("users").document(uid).set(data, merge=True)
    USERS[uid] = {**USERS.get(uid, {}), **data}
def create_team(team_id: str, name: str, owner_uid: str, comp_id: str | None = None):
    doc = {"team_id": team_id, "name": name, "owner_uid": owner_uid}
    if comp_id:
        doc["comp_id"] = comp_id
    if GCP_ENABLED and _fs_coll("teams"):
        _fs_coll("teams").document(team_id).set(doc, merge=True)
        _fs_coll("team_members").document(team_id).set({"members": [owner_uid]})
    TEAMS[team_id] = doc
    TEAM_MEMBERS.setdefault(team_id, []).append(owner_uid)

def update_team(team_id: str, name: str) -> bool:
    """Update team name"""
    if team_id not in TEAMS:
        if GCP_ENABLED and _fs_coll("teams"):
            doc_ref = _fs_coll("teams").document(team_id)
            doc = doc_ref.get()
            if not doc.exists:
                return False
            doc_ref.update({"name": name})
            return True
        return False
    
    TEAMS[team_id]["name"] = name
    
    if GCP_ENABLED and _fs_coll("teams"):
        _fs_coll("teams").document(team_id).update({"name": name})
    
    return True
def join_team(team_id: str, uid: str):
    TEAM_MEMBERS.setdefault(team_id, [])
    if uid not in TEAM_MEMBERS[team_id]:
        TEAM_MEMBERS[team_id].append(uid)
    if GCP_ENABLED and _fs_coll("team_members"):
        tm_ref = _fs_coll("team_members").document(team_id)
        tm = tm_ref.get().to_dict() or {"members": []}
        if uid not in tm["members"]: tm["members"].append(uid)
        tm_ref.set(tm)

def get_team(team_id: str) -> dict | None:
    """Get team details"""
    if GCP_ENABLED and _fs_coll("teams"):
        doc = _fs_coll("teams").document(team_id).get()
        if doc.exists:
            team_data = doc.to_dict()
            # Get members
            members_ref = _fs_coll("team_members").document(team_id)
            members_doc = members_ref.get()
            if members_doc.exists:
                team_data["members"] = members_doc.to_dict().get("members", [])
            else:
                team_data["members"] = []
            
            # Ensure owner is always in members list (fix for data inconsistency)
            owner_uid = team_data.get("owner_uid")
            if owner_uid and owner_uid not in team_data["members"]:
                team_data["members"].append(owner_uid)
                # Update Firestore to fix inconsistency
                members_ref.set({"members": team_data["members"]})
            
            return team_data
        return None
    team_data = TEAMS.get(team_id)
    if team_data:
        team_data = team_data.copy()
        members = TEAM_MEMBERS.get(team_id, [])
        team_data["members"] = members
        
        # Ensure owner is always in members list (fix for data inconsistency)
        owner_uid = team_data.get("owner_uid")
        if owner_uid and owner_uid not in members:
            members.append(owner_uid)
            TEAM_MEMBERS[team_id] = members
            team_data["members"] = members
    
    return team_data

def get_teams(comp_id: str | None = None) -> list[dict]:
    """Get teams, optionally filtered by competition"""
    if GCP_ENABLED and _fs_coll("teams"):
        query = _fs_coll("teams")
        if comp_id:
            query = query.where("comp_id", "==", comp_id)
        docs = query.stream()
        teams = []
        for doc in docs:
            team_data = doc.to_dict()
            # Get members
            members_ref = _fs_coll("team_members").document(doc.id)
            members_doc = members_ref.get()
            if members_doc.exists:
                team_data["members"] = members_doc.to_dict().get("members", [])
            else:
                team_data["members"] = []
            teams.append(team_data)
        return teams
    
    # Local storage
    teams = []
    for team_id, team_data in TEAMS.items():
        if comp_id and team_data.get("comp_id") != comp_id:
            continue
        team_copy = team_data.copy()
        team_copy["members"] = TEAM_MEMBERS.get(team_id, [])
        teams.append(team_copy)
    return teams

def leave_team(team_id: str, uid: str) -> bool:
    """Remove a member from a team"""
    # Check Firestore first if enabled
    if GCP_ENABLED and _fs_coll("team_members"):
        tm_ref = _fs_coll("team_members").document(team_id)
        tm_doc = tm_ref.get()
        if tm_doc.exists:
            tm = tm_doc.to_dict() or {"members": []}
            if uid in tm["members"]:
                tm["members"].remove(uid)
                tm_ref.set(tm)
                # Also update local storage for consistency
                if team_id in TEAM_MEMBERS and uid in TEAM_MEMBERS[team_id]:
                    TEAM_MEMBERS[team_id].remove(uid)
                return True
        # If team doesn't exist in Firestore, return False
        return False
    
    # Local storage only
    if team_id not in TEAM_MEMBERS or uid not in TEAM_MEMBERS[team_id]:
        return False
    
    TEAM_MEMBERS[team_id].remove(uid)
    return True
def create_competition(comp_id: str, data: dict):
    if GCP_ENABLED and _fs_coll("competitions"):
        _fs_coll("competitions").document(comp_id).set(data, merge=True)
    COMPETITIONS[comp_id] = data

def get_user(uid: str) -> dict | None:
    if GCP_ENABLED and _fs_coll("users"):
        doc = _fs_coll("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    return USERS.get(uid)

def get_all_users() -> list[dict]:
    """Get all users"""
    if GCP_ENABLED and _fs_coll("users"):
        docs = _fs_coll("users").stream()
        return [doc.to_dict() for doc in docs]
    return list(USERS.values())

def get_competition(comp_id: str) -> dict | None:
    if GCP_ENABLED and _fs_coll("competitions"):
        doc = _fs_coll("competitions").document(comp_id).get()
        return doc.to_dict() if doc.exists else None
    return COMPETITIONS.get(comp_id)

def get_competitions(status: Optional[str] = None, tz: Optional[str] = None, search: Optional[str] = None) -> list[dict]:
    """Get competitions with optional filters"""
    if GCP_ENABLED and _fs_coll("competitions"):
        query = _fs_coll("competitions")
        
        # Apply filters
        if status:
            query = query.where("status", "==", status)
        if tz:
            query = query.where("tz", "==", tz)
        
        docs = query.order_by("created_at", direction="DESCENDING").stream()
        competitions = [doc.to_dict() for doc in docs]
        
        # Apply search if needed (Firestore doesn't support full-text search easily)
        if search:
            search_lower = search.lower()
            competitions = [
                c for c in competitions
                if search_lower in c.get("name", "").lower() 
                or search_lower in c.get("comp_id", "").lower()
            ]
        
        return competitions
    
    # Local storage: sort by created_at desc
    competitions = list(COMPETITIONS.values())
    competitions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Apply filters
    if status:
        competitions = [c for c in competitions if c.get("status") == status]
    if tz:
        competitions = [c for c in competitions if c.get("tz") == tz]
    if search:
        search_lower = search.lower()
        competitions = [
            c for c in competitions
            if search_lower in c.get("name", "").lower() 
            or search_lower in c.get("comp_id", "").lower()
        ]
    
    return competitions

def update_competition(comp_id: str, data: dict):
    if GCP_ENABLED and _fs_coll("competitions"):
        _fs_coll("competitions").document(comp_id).set(data, merge=True)
    if comp_id in COMPETITIONS:
        COMPETITIONS[comp_id].update(data)

def delete_competition(comp_id: str):
    # This function is not used anymore since we implement soft delete in the API
    # Keeping for backward compatibility but API uses update_competition for soft delete
    if GCP_ENABLED and _fs_coll("competitions"):
        _fs_coll("competitions").document(comp_id).delete()
    COMPETITIONS.pop(comp_id, None)
def write_daily_steps(uid: str, date: str, steps: int):
    key = (uid, date); prev = DAILY_STEPS.get(key, 0); new_steps = max(prev, steps)
    DAILY_STEPS[key] = new_steps
    if GCP_ENABLED and _fs_coll("daily_steps"):
        _fs_coll("daily_steps").document(f"{uid}_{date}").set({"user_id":uid,"date":date,"steps":new_steps}, merge=True)
        if bq():
            table = f"{BQ_DATASET}.fact_daily_steps"
            bq().insert_rows_json(table, [{"user_id": uid, "date": date, "steps": int(new_steps)}])

def get_user_steps(uid: str, comp_id: str | None = None) -> list[dict]:
    """Get user's step history, optionally filtered by competition"""
    if GCP_ENABLED and _fs_coll("daily_steps"):
        query = _fs_coll("daily_steps").where("user_id", "==", uid)
        docs = query.stream()
        steps = [{"user_id": doc.to_dict().get("user_id"), "date": doc.to_dict().get("date"), "steps": doc.to_dict().get("steps", 0)} for doc in docs]
        # Note: Competition filtering would require storing comp_id with steps
        return sorted(steps, key=lambda x: x.get("date", ""), reverse=True)
    
    # Local storage
    steps = []
    for (user_id, date), step_count in DAILY_STEPS.items():
        if user_id == uid:
            steps.append({"user_id": user_id, "date": date, "steps": step_count})
    return sorted(steps, key=lambda x: x.get("date", ""), reverse=True)

def check_idempotency(idempotency_key: str, uid: str, date: str) -> bool:
    """Check if idempotency key has been used before"""
    if not idempotency_key:
        return False
    
    storage_key = f"{idempotency_key}_{uid}"
    
    if GCP_ENABLED and _fs_coll("idempotency_keys"):
        doc = _fs_coll("idempotency_keys").document(storage_key).get()
        if doc.exists:
            return True  # Key already used
        # Store the key
        _fs_coll("idempotency_keys").document(storage_key).set({
            "idempotency_key": idempotency_key,
            "user_id": uid,
            "date": date,
            "created_at": datetime.utcnow().isoformat()
        })
        return False
    
    # Local storage
    if storage_key in IDEMPOTENCY_KEYS:
        return True  # Key already used
    IDEMPOTENCY_KEYS[storage_key] = date
    return False

def is_user_in_team_for_competition(uid: str, comp_id: str) -> bool:
    """Check if user is a member of any team in the competition"""
    teams = get_teams(comp_id=comp_id)
    for team in teams:
        if uid in team.get("members", []):
            return True
    return False
def individual_leaderboard(
    comp_id: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    team_id: str | None = None,
) -> list[dict]:
    """Get individual leaderboard with optional filters"""
    # If filtering by competition, we need to get teams in that competition
    user_ids_in_comp = set()
    if comp_id:
        teams = get_teams(comp_id=comp_id)
        for team in teams:
            user_ids_in_comp.update(team.get("members", []))
    
    # If filtering by team, get team members
    user_ids_in_team = set()
    if team_id:
        team = get_team(team_id)
        if team:
            user_ids_in_team.update(team.get("members", []))
    
    # Aggregate steps by user
    agg = {}
    if GCP_ENABLED and _fs_coll("daily_steps"):
        query = _fs_coll("daily_steps")
        
        # Apply date filters
        if date:
            query = query.where("date", "==", date)
        elif start_date and end_date:
            query = query.where("date", ">=", start_date).where("date", "<=", end_date)
        elif start_date:
            query = query.where("date", ">=", start_date)
        elif end_date:
            query = query.where("date", "<=", end_date)
        
        docs = query.stream()
        for doc in docs:
            doc_data = doc.to_dict()
            uid = doc_data.get("user_id")
            step_date = doc_data.get("date")
            steps = int(doc_data.get("steps", 0))
            
            # Apply filters
            if comp_id and uid not in user_ids_in_comp:
                continue
            if team_id and uid not in user_ids_in_team:
                continue
            if date and step_date != date:
                continue
            if start_date and step_date < start_date:
                continue
            if end_date and step_date > end_date:
                continue
            
            agg[uid] = agg.get(uid, 0) + steps
    else:
        # Local storage
        for (uid, step_date), steps in DAILY_STEPS.items():
            # Apply filters
            if comp_id and uid not in user_ids_in_comp:
                continue
            if team_id and uid not in user_ids_in_team:
                continue
            if date and step_date != date:
                continue
            if start_date and step_date < start_date:
                continue
            if end_date and step_date > end_date:
                continue
            
            agg[uid] = agg.get(uid, 0) + steps
    
    # Convert to rows with user info
    rows = []
    for uid, total_steps in agg.items():
        user_info = get_user(uid) or {}
        rows.append({
            "user_id": uid,
            "email": user_info.get("email", uid),
            "steps": total_steps,
            "rank": 0,  # Will be set after sorting
        })
    
    # Sort by steps descending
    rows.sort(key=lambda r: r["steps"], reverse=True)
    
    # Assign ranks (handle ties)
    rank = 1
    for i, row in enumerate(rows):
        if i > 0 and rows[i-1]["steps"] != row["steps"]:
            rank = i + 1
        row["rank"] = rank
    
    return rows
def team_leaderboard(
    comp_id: str | None = None,
    date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """Get team leaderboard with optional filters"""
    # Get teams (optionally filtered by competition)
    if comp_id:
        teams = get_teams(comp_id=comp_id)
    else:
        teams = get_teams()
    
    # Aggregate steps by team
    result = []
    for team in teams:
        team_id = team.get("team_id")
        team_name = team.get("name", team_id)
        members = team.get("members", [])
        
        if not members:
            continue
        
        total_steps = 0
        if GCP_ENABLED and _fs_coll("daily_steps"):
            query = _fs_coll("daily_steps")
            
            # Filter by members
            # Note: Firestore doesn't support IN queries with multiple values easily
            # So we'll query all and filter in memory
            if date:
                query = query.where("date", "==", date)
            elif start_date and end_date:
                query = query.where("date", ">=", start_date).where("date", "<=", end_date)
            elif start_date:
                query = query.where("date", ">=", start_date)
            elif end_date:
                query = query.where("date", "<=", end_date)
            
            docs = query.stream()
            for doc in docs:
                doc_data = doc.to_dict()
                uid = doc_data.get("user_id")
                step_date = doc_data.get("date")
                steps = int(doc_data.get("steps", 0))
                
                if uid in members:
                    if date and step_date == date:
                        total_steps += steps
                    elif not date:
                        if start_date and step_date < start_date:
                            continue
                        if end_date and step_date > end_date:
                            continue
                        total_steps += steps
                    elif not date and start_date and end_date:
                        if start_date <= step_date <= end_date:
                            total_steps += steps
        else:
            # Local storage
            if date:
                total_steps = sum(DAILY_STEPS.get((uid, date), 0) for uid in members)
            else:
                for (uid, step_date), steps in DAILY_STEPS.items():
                    if uid in members:
                        if start_date and step_date < start_date:
                            continue
                        if end_date and step_date > end_date:
                            continue
                        total_steps += steps
        
        result.append({
            "team_id": team_id,
            "name": team_name,
            "comp_id": team.get("comp_id"),
            "steps": total_steps,
            "member_count": len(members),
            "rank": 0,  # Will be set after sorting
        })
    
    # Sort by steps descending
    result.sort(key=lambda r: r["steps"], reverse=True)
    
    # Assign ranks (handle ties)
    rank = 1
    for i, team in enumerate(result):
        if i > 0 and result[i-1]["steps"] != team["steps"]:
            rank = i + 1
        team["rank"] = rank
    
    return result

def store_oauth_state_token(state_token: str, uid: str, provider: str):
    """Store OAuth state token with user UID and provider"""
    data = {"uid": uid, "provider": provider}
    if GCP_ENABLED and _fs_coll("oauth_states"):
        _fs_coll("oauth_states").document(state_token).set(data)
    OAUTH_STATE_TOKENS[state_token] = data

def get_oauth_state_token(state_token: str) -> Optional[Dict[str, str]]:
    """Retrieve OAuth state token data (uid and provider)"""
    if GCP_ENABLED and _fs_coll("oauth_states"):
        doc = _fs_coll("oauth_states").document(state_token).get()
        if doc.exists:
            data = doc.to_dict()
            # Delete the token after use (one-time use)
            _fs_coll("oauth_states").document(state_token).delete()
            return data
    if state_token in OAUTH_STATE_TOKENS:
        data = OAUTH_STATE_TOKENS.pop(state_token)  # Delete after use
        return data
    return None
