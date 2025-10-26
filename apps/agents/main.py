from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
app = FastAPI(title="StepSquad Agents")
class RunPayload(BaseModel): agent: Literal["sync","fairness"] = "sync"
@app.post("/run")
def run(payload: RunPayload):
    if payload.agent == "sync":
        return {"ok": True, "agent": "sync", "actions": []}
    return {"ok": True, "agent": "fairness", "flags": []}
@app.get("/health")
def health(): return {"ok": True}
