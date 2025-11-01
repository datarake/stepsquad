"""
Storage helper functions for agents to access Firestore data
"""

import os
from typing import List, Dict, Optional
from google.cloud import firestore

GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"

def _fs_coll(name: str):
    """Get Firestore collection reference"""
    if not GCP_ENABLED:
        return None
    try:
        client = firestore.Client()
        return client.collection(name)
    except Exception:
        return None


def get_competitions(comp_id: Optional[str] = None) -> List[Dict]:
    """Get competitions, optionally filtered by comp_id"""
    if GCP_ENABLED and _fs_coll("competitions"):
        if comp_id:
            doc = _fs_coll("competitions").document(comp_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["comp_id"] = comp_id
                return [data]
            return []
        else:
            docs = _fs_coll("competitions").stream()
            return [{"comp_id": doc.id, **doc.to_dict()} for doc in docs]
    return []


def get_teams_for_competition(comp_id: str) -> List[Dict]:
    """Get all teams for a competition"""
    teams = []
    if GCP_ENABLED and _fs_coll("teams"):
        query = _fs_coll("teams").where("comp_id", "==", comp_id)
        team_docs = query.stream()
        for team_doc in team_docs:
            team_data = team_doc.to_dict()
            team_data["team_id"] = team_doc.id
            # Get members
            members_ref = _fs_coll("team_members").document(team_doc.id).get()
            if members_ref.exists:
                team_data["members"] = members_ref.to_dict().get("members", [])
            else:
                team_data["members"] = []
            teams.append(team_data)
    return teams


def get_user_steps(uid: str, comp_id: Optional[str] = None) -> List[Dict]:
    """Get user's step history, optionally filtered by competition"""
    steps = []
    if GCP_ENABLED and _fs_coll("daily_steps"):
        query = _fs_coll("daily_steps").where("user_id", "==", uid)
        docs = query.stream()
        for doc in docs:
            step_data = doc.to_dict()
            steps.append({
                "user_id": step_data.get("user_id"),
                "date": step_data.get("date"),
                "steps": step_data.get("steps", 0)
            })
    return sorted(steps, key=lambda x: x.get("date", ""), reverse=True)


def flag_unfair_data(user_id: str, comp_id: str, date: str, reason: str) -> Dict:
    """Flag a data entry as potentially unfair"""
    from datetime import datetime
    
    flag_data = {
        "user_id": user_id,
        "comp_id": comp_id,
        "date": date,
        "reason": reason,
        "flagged_at": datetime.now().isoformat(),
        "status": "pending_review"
    }
    
    if GCP_ENABLED and _fs_coll("flagged_data"):
        flag_id = f"{user_id}_{comp_id}_{date}"
        fs_coll = _fs_coll("flagged_data")
        # Convert to dict without SERVER_TIMESTAMP for Firestore
        flag_data_fs = flag_data.copy()
        flag_data_fs["flagged_at"] = firestore.SERVER_TIMESTAMP if GCP_ENABLED else datetime.now()
        fs_coll.document(flag_id).set(flag_data_fs, merge=True)
    
    return flag_data


def get_flagged_data(comp_id: Optional[str] = None) -> List[Dict]:
    """Get flagged data entries, optionally filtered by competition"""
    flags = []
    if GCP_ENABLED and _fs_coll("flagged_data"):
        query = _fs_coll("flagged_data")
        if comp_id:
            query = query.where("comp_id", "==", comp_id)
        docs = query.stream()
        for doc in docs:
            flags.append(doc.to_dict())
    return flags

