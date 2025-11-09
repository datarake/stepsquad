"""
Fitbit Web API Client

Handles OAuth 2.0 flow and API calls to Fitbit Web API.
"""

import os
import logging
import requests
from typing import Dict, Optional, Any
from datetime import datetime, date
import secrets
import base64

logger = logging.getLogger(__name__)

# Fitbit OAuth 2.0 configuration
FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID", "")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET", "")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8004/oauth/fitbit/callback")
FITBIT_BASE_URL = "https://api.fitbit.com"
FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"


def generate_state_token(uid: str) -> str:
    """Generate a secure state token for OAuth and store it with user UID"""
    from storage import store_oauth_state_token
    token = secrets.token_urlsafe(32)
    store_oauth_state_token(token, uid, "fitbit")
    return token


def build_fitbit_oauth_url(state: str) -> str:
    """
    Build Fitbit OAuth 2.0 authorization URL
    
    Fitbit uses OAuth 2.0 with authorization code flow
    """
    if not FITBIT_CLIENT_ID:
        raise ValueError("FITBIT_CLIENT_ID not configured")
    
    params = {
        "response_type": "code",
        "client_id": FITBIT_CLIENT_ID,
        "redirect_uri": FITBIT_REDIRECT_URI,
        "scope": "activity",  # Required scope for step data
        "state": state,
        "expires_in": 2592000,  # 30 days
    }
    
    from urllib.parse import urlencode
    query_string = urlencode(params)
    return f"{FITBIT_AUTH_URL}?{query_string}"


def exchange_fitbit_code(code: str) -> Dict[str, Any]:
    """
    Exchange OAuth authorization code for access token
    
    Fitbit uses OAuth 2.0 authorization code flow
    """
    if not FITBIT_CLIENT_ID or not FITBIT_CLIENT_SECRET:
        raise ValueError("Fitbit OAuth credentials not configured")
    
    # Fitbit requires Basic Authentication for token exchange
    credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": FITBIT_REDIRECT_URI,
    }
    
    try:
        response = requests.post(FITBIT_TOKEN_URL, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        
        logger.info("Successfully exchanged Fitbit authorization code for tokens")
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_in": token_data.get("expires_in", 28800),  # Default 8 hours
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
            "expires_at": datetime.utcnow().timestamp() + token_data.get("expires_in", 28800),
        }
    
    except requests.RequestException as e:
        logger.error(f"Error exchanging Fitbit code: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response: {e.response.text}")
        raise ValueError(f"Failed to exchange Fitbit code: {str(e)}")


def refresh_fitbit_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh Fitbit access token using refresh token
    
    Fitbit access tokens expire in 8 hours, refresh tokens last 90 days
    """
    if not FITBIT_CLIENT_ID or not FITBIT_CLIENT_SECRET:
        raise ValueError("Fitbit OAuth credentials not configured")
    
    if not refresh_token:
        raise ValueError("Refresh token required")
    
    credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    
    try:
        response = requests.post(FITBIT_TOKEN_URL, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        
        logger.info("Successfully refreshed Fitbit access token")
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", refresh_token),  # Keep existing if not provided
            "expires_in": token_data.get("expires_in", 28800),
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_at": datetime.utcnow().timestamp() + token_data.get("expires_in", 28800),
        }
    
    except requests.RequestException as e:
        logger.error(f"Error refreshing Fitbit token: {e}")
        raise ValueError(f"Failed to refresh Fitbit token: {str(e)}")


def get_fitbit_daily_steps(access_token: str, date: date) -> int:
    """
    Fetch daily step count from Fitbit API
    
    Args:
        access_token: OAuth access token
        date: Date to fetch steps for (YYYY-MM-DD format)
    
    Returns:
        Step count for the day
    """
    if not access_token:
        raise ValueError("Access token required")
    
    # Fitbit API endpoint for daily activity summary
    # Format: /1/user/{user_id}/activities/date/{date}.json
    # For OAuth, user_id is typically "-" (current user)
    url = f"{FITBIT_BASE_URL}/1/user/-/activities/date/{date.isoformat()}.json"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract step count from response
        # Structure: {"summary": {"steps": 12345}}
        summary = data.get("summary", {})
        steps = summary.get("steps", 0)
        
        logger.info(f"Fetched {steps} steps from Fitbit for {date}")
        return int(steps)
    
    except requests.RequestException as e:
        logger.error(f"Error fetching Fitbit steps: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        
        # Handle token expiry
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                raise ValueError("Fitbit access token expired or invalid")
        
        raise ValueError(f"Failed to fetch Fitbit data: {str(e)}")


def get_fitbit_steps_range(access_token: str, start_date: date, end_date: date) -> Dict[str, int]:
    """
    Fetch step counts for a date range from Fitbit
    
    Returns:
        Dictionary mapping date (ISO format) to step count
    """
    steps_data = {}
    
    current_date = start_date
    while current_date <= end_date:
        try:
            steps = get_fitbit_daily_steps(access_token, current_date)
            steps_data[current_date.isoformat()] = steps
        except Exception as e:
            logger.warning(f"Failed to fetch steps for {current_date}: {e}")
            # Continue with next date
        
        # Move to next day
        from datetime import timedelta
        current_date += timedelta(days=1)
    
    return steps_data

