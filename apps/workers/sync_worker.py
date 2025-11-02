"""
Background sync worker for device integrations

Syncs steps from linked Garmin/Fitbit devices daily via Cloud Scheduler
"""

import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from gcp_clients import init_clients

# Import API clients (same directory structure)
try:
    from api.device_storage import get_all_linked_devices, update_device_sync_time, get_device_tokens
    from api.garmin_client import get_garmin_daily_steps, refresh_garmin_token
    from api.fitbit_client import get_fitbit_daily_steps, refresh_fitbit_token
    from api.storage import write_daily_steps, check_idempotency, is_user_in_team_for_competition, get_competitions, get_competition
    from api.pubsub_bus import publish_ingest
except ImportError:
    # Try alternative import path
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))
    from device_storage import get_all_linked_devices, update_device_sync_time, get_device_tokens
    from garmin_client import get_garmin_daily_steps, refresh_garmin_token
    from fitbit_client import get_fitbit_daily_steps, refresh_fitbit_token
    from storage import write_daily_steps, check_idempotency, is_user_in_team_for_competition, get_competitions, get_competition
    from pubsub_bus import publish_ingest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="StepSquad Sync Worker")

# Initialize GCP clients
init_clients()

COMP_TZ = os.getenv("COMP_TZ", "Europe/Bucharest")
GRACE_DAYS = int(os.getenv("GRACE_DAYS", "2"))


def sync_device_for_user(uid: str, provider: str, sync_date: date) -> Dict[str, Any]:
    """
    Sync steps from a device for a specific user and date
    
    Args:
        uid: User ID
        provider: Device provider ("garmin" or "fitbit")
        sync_date: Date to sync steps for
    
    Returns:
        Sync result with steps and submissions
    """
    try:
        # Get stored tokens
        device_data = get_device_tokens(uid, provider)
        
        if not device_data:
            return {
                "status": "error",
                "error": f"{provider.capitalize()} device not linked",
                "steps": 0
            }
        
        tokens = device_data.get("tokens", {})
        access_token = tokens.get("access_token")
        
        if not access_token:
            return {
                "status": "error",
                "error": f"{provider.capitalize()} access token not found",
                "steps": 0
            }
        
        # Check if token is expired and refresh if needed
        expires_at = tokens.get("expires_at")
        if expires_at and datetime.utcnow().timestamp() >= expires_at:
            logger.info(f"Refreshing {provider} token for user {uid}")
            try:
                if provider == "fitbit" and tokens.get("refresh_token"):
                    new_tokens = refresh_fitbit_token(tokens.get("refresh_token"))
                    # Update stored tokens
                    from api.device_storage import store_device_tokens
                    store_device_tokens(uid, provider, new_tokens)
                    access_token = new_tokens.get("access_token")
                elif provider == "garmin":
                    # Garmin OAuth 1.0a doesn't have refresh tokens
                    return {
                        "status": "error",
                        "error": "Garmin token expired, re-authentication required",
                        "steps": 0
                    }
            except Exception as e:
                logger.error(f"Failed to refresh {provider} token: {e}")
                return {
                    "status": "error",
                    "error": f"Token refresh failed: {str(e)}",
                    "steps": 0
                }
        
        # Fetch steps from device API
        try:
            if provider == "garmin":
                steps = get_garmin_daily_steps(access_token, sync_date)
            elif provider == "fitbit":
                steps = get_fitbit_daily_steps(access_token, sync_date)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown provider: {provider}",
                    "steps": 0
                }
        except ValueError as e:
            logger.warning(f"Failed to fetch steps from {provider} for {uid}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "steps": 0
            }
        
        if steps == 0:
            logger.info(f"No steps found for {uid} from {provider} on {sync_date}")
            return {
                "status": "success",
                "steps": 0,
                "message": "No steps found for this date"
            }
        
        # Find user's active competitions and submit steps
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
            if not is_user_in_team_for_competition(uid, comp_id):
                continue
            
            # Check if date is within competition range (with grace days)
            try:
                comp_start = datetime.strptime(competition.get("start_date"), "%Y-%m-%d").date()
                comp_end = datetime.strptime(competition.get("end_date"), "%Y-%m-%d").date()
                grace_end = comp_end + timedelta(days=GRACE_DAYS)
                
                if comp_start <= sync_date <= grace_end:
                    user_competitions.append(comp_id)
            except (ValueError, KeyError) as e:
                logger.warning(f"Error checking date range for competition {comp_id}: {e}")
                continue
        
        # Submit steps to each active competition
        submissions = []
        for comp_id in user_competitions:
            try:
                # Generate idempotency key
                idempotency_key = f"{provider}_{sync_date.isoformat()}_{uid}_{comp_id}"
                
                # Check idempotency
                if check_idempotency(idempotency_key, uid, sync_date.isoformat()):
                    logger.info(f"Skipping duplicate submission for {uid} in {comp_id} on {sync_date}")
                    submissions.append({
                        "comp_id": comp_id,
                        "status": "skipped",
                        "reason": "duplicate"
                    })
                    continue
                
                # Write steps
                write_daily_steps(uid, sync_date.isoformat(), steps)
                
                # Publish to Pub/Sub
                try:
                    publish_ingest({
                        "user_id": uid,
                        "comp_id": comp_id,
                        "date": sync_date.isoformat(),
                        "steps": steps,
                        "provider": provider,
                        "tz": COMP_TZ,
                        "source_ts": datetime.utcnow().isoformat(),
                        "idempotency_key": idempotency_key,
                    })
                except Exception as pubsub_error:
                    logger.warning(f"Failed to publish step ingestion event to Pub/Sub: {pubsub_error}")
                
                submissions.append({
                    "comp_id": comp_id,
                    "status": "submitted",
                    "steps": steps
                })
                
                logger.info(f"Submitted {steps} steps for {uid} to competition {comp_id}")
                
            except Exception as e:
                logger.error(f"Failed to submit steps to competition {comp_id}: {e}")
                submissions.append({
                    "comp_id": comp_id,
                    "status": "error",
                    "error": str(e)
                })
        
        # Update sync time
        update_device_sync_time(uid, provider)
        
        return {
            "status": "success",
            "provider": provider,
            "date": sync_date.isoformat(),
            "steps": steps,
            "competitions": submissions,
            "submitted_count": len([s for s in submissions if s.get("status") == "submitted"]),
        }
    
    except Exception as e:
        logger.error(f"Error syncing {provider} device for user {uid}: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "steps": 0
        }


@app.post("/cron/sync-devices")
async def sync_all_devices(request: Request):
    """
    Cloud Scheduler endpoint to sync all linked devices
    
    This endpoint is called by Cloud Scheduler daily to sync steps
    from all linked Garmin and Fitbit devices.
    
    Expected call: POST /cron/sync-devices
    """
    try:
        # Get sync date (default to yesterday for daily sync)
        # Cloud Scheduler typically runs at midnight, syncing previous day
        sync_date = datetime.now().date() - timedelta(days=1)
        
        # Get all linked devices
        all_devices = get_all_linked_devices()
        
        if not all_devices:
            logger.info("No linked devices found")
            return {
                "status": "success",
                "message": "No linked devices found",
                "sync_count": 0
            }
        
        logger.info(f"Starting sync for {len(all_devices)} devices on {sync_date}")
        
        sync_results = []
        success_count = 0
        error_count = 0
        
        for device_data in all_devices:
            uid = device_data.get("uid")
            provider = device_data.get("provider")
            
            if not uid or not provider:
                continue
            
            logger.info(f"Syncing {provider} device for user {uid}")
            
            result = sync_device_for_user(uid, provider, sync_date)
            result["uid"] = uid
            result["provider"] = provider
            
            sync_results.append(result)
            
            if result.get("status") == "success":
                success_count += 1
            else:
                error_count += 1
        
        logger.info(f"Sync complete: {success_count} successful, {error_count} errors")
        
        return {
            "status": "success",
            "sync_date": sync_date.isoformat(),
            "total_devices": len(all_devices),
            "successful": success_count,
            "errors": error_count,
            "results": sync_results
        }
    
    except Exception as e:
        logger.error(f"Error in sync_all_devices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "service": "stepsquad-sync-worker",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

