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
            return team_data
        return None
    team_data = TEAMS.get(team_id)
    if team_data:
        team_data = team_data.copy()
        team_data["members"] = TEAM_MEMBERS.get(team_id, [])
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
    if team_id not in TEAM_MEMBERS or uid not in TEAM_MEMBERS[team_id]:
        return False
    
    TEAM_MEMBERS[team_id].remove(uid)
    
    if GCP_ENABLED and _fs_coll("team_members"):
        tm_ref = _fs_coll("team_members").document(team_id)
        tm = tm_ref.get().to_dict() or {"members": []}
        if uid in tm["members"]:
            tm["members"].remove(uid)
            tm_ref.set(tm)
    
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
def individual_leaderboard(date: str | None):
    if GCP_ENABLED and _fs_coll("daily_steps") and date:
        qs = _fs_coll("daily_steps").where("date","==",date).stream()
        rows = [{"user_id": d.get("user_id"), "steps": int(d.get("steps",0))} for d in (x.to_dict() for x in qs)]
    elif date:
        rows = [{"user_id": uid, "steps": s} for (uid, d), s in DAILY_STEPS.items() if d == date]
    else:
        agg = {}
        for (uid, d), s in DAILY_STEPS.items(): agg[uid]=agg.get(uid,0)+s
        rows = [{"user_id": uid, "steps": steps} for uid, steps in agg.items()]
    rows.sort(key=lambda r: r["steps"], reverse=True); return rows
def team_leaderboard(date: str | None):
    members = TEAM_MEMBERS.copy()
    teams_local = TEAMS.copy()
    if GCP_ENABLED and _fs_coll("team_members") and _fs_coll("teams"):
        for doc in _fs_coll("team_members").stream(): members[doc.id] = doc.to_dict().get("members",[])
        for tdoc in _fs_coll("teams").stream(): teams_local[tdoc.id] = tdoc.to_dict()
    result=[]
    for team_id, mlist in members.items():
        if date:
            total = sum(DAILY_STEPS.get((m, date), 0) for m in mlist)
        else:
            total = 0
            for (uid, d), s in DAILY_STEPS.items():
                if uid in mlist: total += s
        result.append({"team_id": team_id, "name": teams_local.get(team_id, {}).get("name", team_id), "steps": total})
    result.sort(key=lambda r: r["steps"], reverse=True); return result
