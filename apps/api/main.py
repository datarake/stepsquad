from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import os, uuid

from gcp_clients import init_clients
from storage import (
    upsert_user, create_team, join_team, create_competition,
    write_daily_steps, individual_leaderboard, team_leaderboard
)
from pubsub_bus import publish_ingest

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
    name: str
    owner_uid: str

class TeamJoin(BaseModel):
    team_id: str
    uid: str

class CompetitionCreate(BaseModel):
    comp_id: str
    name: str
    tz: str = COMP_TZ
    start_date: str
    end_date: str
    topN_per_team: int | None = None
    grace_days: int = GRACE_DAYS

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat(), "tz": COMP_TZ}

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

@app.post("/teams")
def api_create_team(body: TeamCreate):
    team_id = uuid.uuid4().hex[:8]
    create_team(team_id, body.name, body.owner_uid)
    return {"team_id": team_id, "name": body.name}

@app.post("/teams/join")
def api_join_team(body: TeamJoin):
    join_team(body.team_id, body.uid)
    return {"ok": True}

@app.post("/competitions")
def api_create_competition(body: CompetitionCreate):
    create_competition(body.comp_id, body.model_dump())
    return {"ok": True, "comp_id": body.comp_id}

@app.post("/dev/seed")
def dev_seed():
    upsert_user("u1", {"email": "a@x"})
    upsert_user("u2", {"email": "b@x"})
    upsert_user("u3", {"email": "c@x"})

    create_team("t1", "Falcons", "u1")
    join_team("t1", "u2")
    create_team("t2", "Panthers", "u3")

    create_competition("c1", {
        "name": "Demo Cup",
        "tz": COMP_TZ,
        "start_date": "2025-10-01",
        "end_date": "2025-12-31"
    })

    write_daily_steps("u1", "2025-10-24", 8200)
    write_daily_steps("u2", "2025-10-24", 10400)
    write_daily_steps("u3", "2025-10-24", 5600)
    write_daily_steps("u1", "2025-10-25", 9200)
    write_daily_steps("u2", "2025-10-25", 7000)
    write_daily_steps("u3", "2025-10-25", 14000)
    return {"ok": True}
