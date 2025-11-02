# OAuth Credentials Setup Guide

This guide will walk you through setting up OAuth credentials for Garmin and Fitbit device integrations.

---

## Prerequisites

- Garmin Connect account
- Fitbit account
- Access to Google Cloud Console (for environment variables)
- Access to your application's deployment environment

---

## Part 1: Fitbit OAuth 2.0 Setup

Fitbit uses OAuth 2.0 authorization code flow, which is straightforward to set up.

### Step 1: Register Your Application

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Sign in with your Fitbit account
3. Navigate to **Manage** → **Register An App**
4. Click **Register a New App**

### Step 2: Fill in Application Details

Fill in the following information:

- **Application Name**: `StepSquad` (or your app name)
- **Description**: `Step competition platform for syncing step data`
- **Application Website**: `https://your-domain.com` (or your production URL)
- **Organization**: Your organization name
- **Organization Website**: Your website
- **OAuth 2.0 Application Type**: `Server`
- **Redirect URL**: 
  - For local dev: `http://localhost:8080/oauth/fitbit/callback`
  - For production: `https://your-api-domain.com/oauth/fitbit/callback`
- **Default Access Type**: `Read`
- **Callback URL**: Same as Redirect URL above

### Step 3: Select API Access Scopes

Select the following scopes (minimum required):

- ✅ **Activity** - Required for step data access
- ✅ **Profile** - Optional, for user profile data

### Step 4: Save Credentials

After registration, you'll receive:

- **OAuth 2.0 Client ID** - Copy this
- **Client Secret** - Copy this (keep it secure!)

### Step 5: Configure Environment Variables

Set the following environment variables in your deployment:

**For Local Development** (`.env.local`):
```bash
FITBIT_CLIENT_ID=your_fitbit_client_id_here
FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here
FITBIT_REDIRECT_URI=http://localhost:8080/oauth/fitbit/callback
```

**For Production** (Cloud Run / Environment Variables):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Run** → Select your service → **Edit & Deploy New Revision**
3. Go to **Variables & Secrets** tab
4. Add the following environment variables:

```
FITBIT_CLIENT_ID=your_fitbit_client_id_here
FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here
FITBIT_REDIRECT_URI=https://your-api-domain.com/oauth/fitbit/callback
```

**Or via gcloud CLI:**
```bash
gcloud run services update stepsquad-api \
  --update-env-vars="FITBIT_CLIENT_ID=your_fitbit_client_id_here,FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here,FITBIT_REDIRECT_URI=https://your-api-domain.com/oauth/fitbit/callback" \
  --region=us-central1
```

**Or via GitHub Secrets** (for CI/CD):

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

```
FITBIT_CLIENT_ID
FITBIT_CLIENT_SECRET
```

Then update your CI/CD workflow to use these secrets.

---

## Part 2: Garmin OAuth 1.0a Setup

Garmin uses OAuth 1.0a, which requires Consumer Key and Consumer Secret.

### Step 1: Register for Garmin Developer Program

1. Go to [Garmin Developer Portal](https://developer.garmin.com/gc-developer-program/)
2. Sign in or create a Garmin Connect account
3. Navigate to **My Account** → **Manage OAuth Clients**

### Step 2: Create OAuth Client

1. Click **Create a New OAuth Client**
2. Fill in the following information:

- **Application Name**: `StepSquad`
- **Application Description**: `Step competition platform for syncing step data`
- **Application Type**: `Server`
- **Callback URL**: 
  - For local dev: `http://localhost:8080/oauth/garmin/callback`
  - For production: `https://your-api-domain.com/oauth/garmin/callback`

### Step 3: Save Credentials

After creation, you'll receive:

- **Consumer Key** - This is your OAuth 1.0a client ID
- **Consumer Secret** - This is your OAuth 1.0a client secret (keep it secure!)

### Step 4: Configure Environment Variables

Set the following environment variables:

**For Local Development** (`.env.local`):
```bash
GARMIN_CLIENT_ID=your_garmin_consumer_key_here
GARMIN_CLIENT_SECRET=your_garmin_consumer_secret_here
GARMIN_REDIRECT_URI=http://localhost:8080/oauth/garmin/callback
```

**For Production** (Cloud Run / Environment Variables):

Add the following environment variables:

```
GARMIN_CLIENT_ID=your_garmin_consumer_key_here
GARMIN_CLIENT_SECRET=your_garmin_consumer_secret_here
GARMIN_REDIRECT_URI=https://your-api-domain.com/oauth/garmin/callback
```

**Or via gcloud CLI:**
```bash
gcloud run services update stepsquad-api \
  --update-env-vars="GARMIN_CLIENT_ID=your_garmin_consumer_key_here,GARMIN_CLIENT_SECRET=your_garmin_consumer_secret_here,GARMIN_REDIRECT_URI=https://your-api-domain.com/oauth/garmin/callback" \
  --region=us-central1
```

**Or via GitHub Secrets** (for CI/CD):

Add the following secrets:
```
GARMIN_CLIENT_ID
GARMIN_CLIENT_SECRET
```

---

## Part 3: Update Application Code

### Step 1: Install OAuth 1.0a Library for Garmin

Garmin requires OAuth 1.0a implementation. Install the required library:

```bash
cd apps/api
pip install oauthlib requests-oauthlib
```

Or add to `apps/api/pyproject.toml`:

```toml
dependencies = [
  # ... existing dependencies ...
  "oauthlib>=3.2.0",
  "requests-oauthlib>=1.3.1",
]
```

### Step 2: Update Garmin Client Implementation

The current `garmin_client.py` has placeholder implementations. You'll need to complete the OAuth 1.0a flow using `oauthlib`.

**Example implementation** (to be added to `apps/api/garmin_client.py`):

```python
from oauthlib.oauth1 import Client
from requests_oauthlib import OAuth1Session

def build_garmin_oauth_url(state: str) -> str:
    """Build Garmin OAuth 1.0a authorization URL"""
    if not GARMIN_CLIENT_ID or not GARMIN_CLIENT_SECRET:
        raise ValueError("Garmin OAuth credentials not configured")
    
    # Step 1: Get request token
    oauth = OAuth1Session(
        GARMIN_CLIENT_ID,
        client_secret=GARMIN_CLIENT_SECRET,
        callback_uri=GARMIN_REDIRECT_URI
    )
    
    # Get request token
    request_token_url = f"{GARMIN_BASE_URL}/oauth-service/oauth/request_token"
    fetch_response = oauth.fetch_request_token(request_token_url)
    
    # Store request token for callback (in production, use Redis or similar)
    request_token = fetch_response.get('oauth_token')
    request_token_secret = fetch_response.get('oauth_token_secret')
    
    # Step 2: Build authorization URL
    authorization_url = f"{GARMIN_BASE_URL}/oauth-service/oauth/authorize"
    authorization_url = oauth.authorization_url(authorization_url)
    
    return authorization_url

def exchange_garmin_code(oauth_token: str, oauth_verifier: str) -> Dict[str, Any]:
    """Exchange OAuth 1.0a request token for access token"""
    if not GARMIN_CLIENT_ID or not GARMIN_CLIENT_SECRET:
        raise ValueError("Garmin OAuth credentials not configured")
    
    # Step 3: Get access token
    oauth = OAuth1Session(
        GARMIN_CLIENT_ID,
        client_secret=GARMIN_CLIENT_SECRET,
        resource_owner_key=oauth_token,
        verifier=oauth_verifier
    )
    
    access_token_url = f"{GARMIN_BASE_URL}/oauth-service/oauth/access_token"
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    
    return {
        "access_token": oauth_tokens.get('oauth_token'),
        "token_secret": oauth_tokens.get('oauth_token_secret'),
        "token_type": "OAuth",
        "expires_in": None,  # OAuth 1.0a doesn't have expiration
    }
```

---

## Part 4: Environment Variables Summary

### Complete Environment Variables List

**Local Development** (`.env.local` in `apps/api/`):

```bash
# Fitbit OAuth 2.0
FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_client_secret
FITBIT_REDIRECT_URI=http://localhost:8080/oauth/fitbit/callback

# Garmin OAuth 1.0a
GARMIN_CLIENT_ID=your_garmin_consumer_key
GARMIN_CLIENT_SECRET=your_garmin_consumer_secret
GARMIN_REDIRECT_URI=http://localhost:8080/oauth/garmin/callback

# Other existing variables
GCP_ENABLED=false
COMP_TZ=Europe/Bucharest
GRACE_DAYS=2
```

**Production** (Cloud Run Environment Variables):

```
FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_client_secret
FITBIT_REDIRECT_URI=https://your-api-domain.com/oauth/fitbit/callback
GARMIN_CLIENT_ID=your_garmin_consumer_key
GARMIN_CLIENT_SECRET=your_garmin_consumer_secret
GARMIN_REDIRECT_URI=https://your-api-domain.com/oauth/garmin/callback
GCP_ENABLED=true
GOOGLE_CLOUD_PROJECT=your-project-id
COMP_TZ=Europe/Bucharest
GRACE_DAYS=2
```

---

## Part 5: Testing the Integration

### Step 1: Test Fitbit OAuth Flow

1. Start your API server:
   ```bash
   cd apps/api
   uvicorn main:app --reload --port 8080
   ```

2. In your browser, navigate to:
   ```
   http://localhost:5174/devices
   ```

3. Click **Connect Fitbit**
4. You should be redirected to Fitbit OAuth page
5. Authorize the application
6. You should be redirected back to `/devices` with a success message

### Step 2: Test Garmin OAuth Flow

1. Navigate to `/devices`
2. Click **Connect Garmin**
3. You should be redirected to Garmin OAuth page
4. Authorize the application
5. You should be redirected back with a success message

### Step 3: Test Device Sync

1. Once a device is connected, click **Sync Now**
2. Steps should be fetched from the device API
3. Steps should be submitted to your active competitions

---

## Part 6: Security Best Practices

### 1. Store Secrets Securely

- **Never commit secrets to Git**
- Use environment variables or secret management (Google Secret Manager)
- Rotate secrets periodically

### 2. Use Google Secret Manager (Recommended for Production)

Instead of environment variables, use Google Secret Manager:

```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Usage
FITBIT_CLIENT_ID = get_secret("fitbit-client-id")
FITBIT_CLIENT_SECRET = get_secret("fitbit-client-secret")
```

### 3. Validate Redirect URIs

Ensure redirect URIs match exactly (including protocol, domain, and path).

### 4. Use HTTPS in Production

Always use HTTPS for OAuth callbacks in production to protect tokens.

---

## Part 7: Troubleshooting

### Common Issues

**1. "Invalid redirect URI"**
- Ensure redirect URI in environment matches exactly with provider settings
- Check for trailing slashes or protocol differences

**2. "Invalid client credentials"**
- Verify client ID and secret are correct
- Check for extra spaces or encoding issues

**3. "OAuth callback not working"**
- Verify callback URL is accessible
- Check CORS settings
- Ensure route is registered in frontend

**4. "Token refresh failing"**
- Check token expiration times
- Verify refresh token is stored correctly
- Ensure token refresh logic is implemented

---

## Part 8: Next Steps

After configuring OAuth credentials:

1. ✅ Set up Cloud Scheduler for daily sync
2. ✅ Test OAuth flows end-to-end
3. ✅ Monitor token refresh and expiration
4. ✅ Set up error alerts for OAuth failures
5. ✅ Document OAuth flows for your team

---

## Quick Reference

### Fitbit OAuth URLs

- **Authorization URL**: `https://www.fitbit.com/oauth2/authorize`
- **Token URL**: `https://api.fitbit.com/oauth2/token`
- **API Base URL**: `https://api.fitbit.com`

### Garmin OAuth URLs

- **Request Token URL**: `https://connectapi.garmin.com/oauth-service/oauth/request_token`
- **Authorization URL**: `https://connectapi.garmin.com/oauth-service/oauth/authorize`
- **Access Token URL**: `https://connectapi.garmin.com/oauth-service/oauth/access_token`
- **API Base URL**: `https://connectapi.garmin.com`

---

**Last Updated**: November 2, 2025  
**Status**: ✅ Ready for Configuration

