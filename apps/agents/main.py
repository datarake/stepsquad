"""
StepSquad Agents Service - Using Google Agent Development Kit (ADK)

This service implements two AI agents:
1. Sync Agent - Detects missing step data and triggers synchronization
2. Fairness Agent - Analyzes step data for anomalies and flags unrealistic entries

Both agents are built using Google's Agent Development Kit (ADK) and communicate
with each other to complete workflows.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

try:
    from agents import SyncAgent, FairnessAgent, create_multi_agent_workflow, ADK_AVAILABLE, GEMINI_AVAILABLE
except ImportError as e:
    import logging
    logging.error(f"Failed to import agents: {e}")
    ADK_AVAILABLE = False
    GEMINI_AVAILABLE = False
    SyncAgent = None
    FairnessAgent = None
    create_multi_agent_workflow = None

from gcp_clients import init_clients

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="StepSquad Agents", version="0.3.0")

# Initialize GCP clients
init_clients()

# Initialize agents (with error handling)
try:
    sync_agent = SyncAgent() if SyncAgent else None
    fairness_agent = FairnessAgent() if FairnessAgent else None
    workflow = create_multi_agent_workflow(sync_agent, fairness_agent) if create_multi_agent_workflow and sync_agent and fairness_agent else None
except Exception as e:
    logger.error(f"Failed to initialize agents: {e}", exc_info=True)
    sync_agent = None
    fairness_agent = None
    workflow = None


class RunPayload(BaseModel):
    agent: Literal["sync", "fairness", "workflow"] = "sync"
    comp_id: Optional[str] = None
    date: Optional[str] = None
    user_id: Optional[str] = None


@app.post("/run")
def run(payload: RunPayload):
    """
    Run an agent or workflow
    
    Agents:
    - sync: Run sync agent to detect missing/late data
    - fairness: Run fairness agent to analyze data for anomalies
    - workflow: Run both agents in sequence with communication
    """
    try:
        if not sync_agent or not fairness_agent:
            raise HTTPException(status_code=503, detail="Agents not initialized. Check logs for errors.")
        
        if not payload.comp_id:
            raise HTTPException(status_code=400, detail="comp_id is required")
        
        if payload.agent == "sync":
            logger.info(f"Running sync agent for competition {payload.comp_id}")
            result = sync_agent.run(payload.comp_id, payload.date)
            return result
        
        elif payload.agent == "fairness":
            logger.info(f"Running fairness agent for competition {payload.comp_id}")
            result = fairness_agent.run(payload.comp_id, payload.user_id)
            return result
        
        elif payload.agent == "workflow":
            if not workflow:
                raise HTTPException(status_code=503, detail="Workflow not initialized")
            logger.info(f"Running multi-agent workflow for competition {payload.comp_id}")
            result = workflow(payload.comp_id, payload.date)
            return result
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {payload.agent}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "service": "stepsquad-agents",
        "agents": ["sync", "fairness", "workflow"],
        "adk_available": ADK_AVAILABLE if 'ADK_AVAILABLE' in globals() else False,
        "gemini_available": GEMINI_AVAILABLE if 'GEMINI_AVAILABLE' in globals() else False,
        "agents_initialized": sync_agent is not None and fairness_agent is not None,
        "tools_count": len(sync_agent.tools) if sync_agent and sync_agent.tools else 0,
        "version": "0.3.0"
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "stepsquad-agents",
        "version": "0.3.0",
        "endpoints": {
            "health": "/health",
            "run": "/run"
        }
    }
