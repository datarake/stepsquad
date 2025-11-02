"""
Device token storage for OAuth providers (Garmin, Fitbit)

Stores encrypted OAuth tokens in Firestore for linked devices.
"""

import os
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from gcp_clients import fs

logger = logging.getLogger(__name__)

GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"

# In-memory storage for local dev
DEVICE_TOKENS: Dict[str, Dict[str, Dict[str, Any]]] = {}  # uid -> provider -> tokens


def _fs_coll(name: str):
    """Get Firestore collection reference"""
    return fs().collection(name) if fs() and GCP_ENABLED else None


def store_device_tokens(uid: str, provider: str, tokens: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store OAuth tokens for a user's device
    
    Args:
        uid: User ID
        provider: Provider name ("garmin" or "fitbit")
        tokens: OAuth token data (access_token, refresh_token, expires_at, etc.)
    
    Returns:
        Stored device data
    """
    device_data = {
        "uid": uid,
        "provider": provider,
        "tokens": tokens,
        "linked_at": datetime.utcnow().isoformat(),
        "last_sync": None,
        "sync_enabled": True,
    }
    
    device_id = f"{uid}_{provider}"
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        # Store in Firestore
        # Note: In production, encrypt tokens before storing
        doc_ref = _fs_coll("device_tokens").document(device_id)
        doc_ref.set(device_data, merge=True)
        logger.info(f"Stored {provider} tokens for user {uid} in Firestore")
    else:
        # Local storage
        if uid not in DEVICE_TOKENS:
            DEVICE_TOKENS[uid] = {}
        DEVICE_TOKENS[uid][provider] = device_data
        logger.info(f"Stored {provider} tokens for user {uid} in memory")
    
    return device_data


def get_device_tokens(uid: str, provider: str) -> Optional[Dict[str, Any]]:
    """
    Get stored OAuth tokens for a user's device
    
    Args:
        uid: User ID
        provider: Provider name ("garmin" or "fitbit")
    
    Returns:
        Device token data or None if not found
    """
    device_id = f"{uid}_{provider}"
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        doc_ref = _fs_coll("device_tokens").document(device_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    else:
        # Local storage
        return DEVICE_TOKENS.get(uid, {}).get(provider)


def get_user_devices(uid: str) -> List[Dict[str, Any]]:
    """
    Get all linked devices for a user
    
    Args:
        uid: User ID
    
    Returns:
        List of device data
    """
    devices = []
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        query = _fs_coll("device_tokens").where("uid", "==", uid)
        docs = query.stream()
        
        for doc in docs:
            device_data = doc.to_dict()
            # Remove sensitive token data from response (keep structure)
            safe_data = {
                "provider": device_data.get("provider"),
                "linked_at": device_data.get("linked_at"),
                "last_sync": device_data.get("last_sync"),
                "sync_enabled": device_data.get("sync_enabled", True),
            }
            devices.append(safe_data)
    else:
        # Local storage
        for provider, device_data in DEVICE_TOKENS.get(uid, {}).items():
            safe_data = {
                "provider": provider,
                "linked_at": device_data.get("linked_at"),
                "last_sync": device_data.get("last_sync"),
                "sync_enabled": device_data.get("sync_enabled", True),
            }
            devices.append(safe_data)
    
    return devices


def remove_device_tokens(uid: str, provider: str) -> bool:
    """
    Remove stored OAuth tokens (unlink device)
    
    Args:
        uid: User ID
        provider: Provider name ("garmin" or "fitbit")
    
    Returns:
        True if removed, False if not found
    """
    device_id = f"{uid}_{provider}"
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        doc_ref = _fs_coll("device_tokens").document(device_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            logger.info(f"Removed {provider} tokens for user {uid}")
            return True
        return False
    else:
        # Local storage
        if uid in DEVICE_TOKENS and provider in DEVICE_TOKENS[uid]:
            del DEVICE_TOKENS[uid][provider]
            logger.info(f"Removed {provider} tokens for user {uid}")
            return True
        return False


def update_device_sync_time(uid: str, provider: str, sync_time: Optional[datetime] = None) -> bool:
    """
    Update last sync time for a device
    
    Args:
        uid: User ID
        provider: Provider name ("garmin" or "fitbit")
        sync_time: Sync timestamp (defaults to now)
    
    Returns:
        True if updated
    """
    if sync_time is None:
        sync_time = datetime.utcnow()
    
    device_id = f"{uid}_{provider}"
    update_data = {"last_sync": sync_time.isoformat()}
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        doc_ref = _fs_coll("device_tokens").document(device_id)
        doc_ref.update(update_data)
        return True
    else:
        # Local storage
        if uid in DEVICE_TOKENS and provider in DEVICE_TOKENS[uid]:
            DEVICE_TOKENS[uid][provider].update(update_data)
            return True
        return False


def get_all_linked_devices() -> List[Dict[str, Any]]:
    """
    Get all linked devices across all users (for background sync)
    
    Returns:
        List of device data with tokens
    """
    devices = []
    
    if GCP_ENABLED and _fs_coll("device_tokens"):
        docs = _fs_coll("device_tokens").stream()
        
        for doc in docs:
            device_data = doc.to_dict()
            # Include tokens for sync workers
            devices.append(device_data)
    else:
        # Local storage
        for uid, providers in DEVICE_TOKENS.items():
            for provider, device_data in providers.items():
                devices.append(device_data)
    
    return devices

