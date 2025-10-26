from __future__ import annotations
from typing import Dict, Tuple, List
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
def create_team(team_id: str, name: str, owner_uid: str):
    doc = {"team_id": team_id, "name": name, "owner_uid": owner_uid}
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
def create_competition(comp_id: str, data: dict):
    if GCP_ENABLED and _fs_coll("competitions"):
        _fs_coll("competitions").document(comp_id).set(data, merge=True)
    COMPETITIONS[comp_id] = data
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
