# Garmin OAuth App Setup Guide

Complete step-by-step guide for creating and configuring a Garmin OAuth app for StepSquad.

---

## Overview

Garmin uses **OAuth 1.0a** (not OAuth 2.0), which requires:
- **Consumer Key** (like Client ID)
- **Consumer Secret** (like Client Secret)
- **Callback URL** for OAuth flow

---

## Step 1: Register for Garmin Developer Program

### Prerequisites

1. **Garmin Connect Account**: You need a Garmin Connect account
   - If you don't have one, create at [Garmin Connect](https://connect.garmin.com/)

2. **Developer Account**: Register as a developer
   - Go to [Garmin Developer Portal](https://developer.garmin.com/)
   - Sign in with your Garmin Connect account

### Register for Developer Program

1. Go to [Garmin Developer Portal](https://developer.garmin.com/gc-developer-program/)
2. Click **"Apply Now"** or **"Register"**
3. Fill in the registration form:
   - **Application Name**: `StepSquad`
   - **Company/Organization**: `Tekolin` (or your organization)
   - **Description**: `Step competition platform for syncing step data from Garmin devices`
   - **Application Website**: `https://www.stepsquad.club`
   - **Terms of Service**: `https://stepsquad.club/terms`
   - **Privacy Policy**: `https://stepsquad.club/privacy`
4. Accept terms and submit
5. Wait for approval (can take 1-3 business days)

**Note**: Garmin Developer Program approval may take some time. Be patient!

---

## Step 2: Create OAuth Client

After your developer account is approved:

### Access OAuth Client Management

1. Go to [Garmin Developer Portal](https://developer.garmin.com/)
2. Sign in with your Garmin Connect account
3. Navigate to **"My Account"** or **"Manage Applications"**
4. Look for **"OAuth Clients"** or **"API Access"** section
5. Click **"Create OAuth Client"** or **"Register New Client"**

### Fill in OAuth Client Details

Fill in the following information:

- **Application Name**: `StepSquad`
- **Application Description**: 
  ```
  Step competition platform that syncs step data from Garmin devices 
  to allow users to participate in team-based step challenges.
  ```
- **Application Website**: `https://www.stepsquad.club`
- **Application Type**: `Server` or `Web Application`
- **Callback URL**: 
  ```
  https://api.stepsquad.club/oauth/garmin/callback
  ```
- **API Access**: Enable access to **Activity API** or **Wellness API** (for step data)

### Submit OAuth Client Registration

1. Review all information
2. Accept terms and conditions
3. Click **"Create"** or **"Register"**

**Note**: OAuth client registration may require approval. Wait for confirmation email.

---

## Step 3: Get OAuth Credentials

After OAuth client is created and approved:

### Consumer Key and Consumer Secret

You'll receive:
- **Consumer Key** - This is your OAuth 1.0a client ID (keep it secure!)
- **Consumer Secret** - This is your OAuth 1.0a client secret (keep it very secure!)

**Important**: 
- Store these securely - you'll need them for environment variables
- Consumer Secret should be treated like a password - never commit to Git
- If you lose Consumer Secret, you'll need to regenerate it

### Where to Find Them

1. Go to **Garmin Developer Portal** → **My Account** → **OAuth Clients**
2. Find your **StepSquad** OAuth client
3. Click **"View Details"** or **"Manage"**
4. You'll see:
   - **Consumer Key**: `xxxxxxxxxxxxxxxx`
   - **Consumer Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Callback URL**: `https://api.stepsquad.club/oauth/garmin/callback`

---

## Step 4: Configure Environment Variables

### For Production (Cloud Run)

Set environment variables in Cloud Run service:

```bash
gcloud run services update stepsquad-api \
  --update-env-vars="GARMIN_CLIENT_ID=your_consumer_key_here,GARMIN_CLIENT_SECRET=your_consumer_secret_here,GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback" \
  --region us-central1
```

**Replace:**
- `your_consumer_key_here` with your actual Consumer Key
- `your_consumer_secret_here` with your actual Consumer Secret

### For Local Development

Create `apps/api/.env.local`:

```bash
GARMIN_CLIENT_ID=your_consumer_key_here
GARMIN_CLIENT_SECRET=your_consumer_secret_here
GARMIN_REDIRECT_URI=http://localhost:8080/oauth/garmin/callback
```

### Using Google Secret Manager (Recommended for Production)

Instead of environment variables, use Secret Manager for security:

1. **Create secrets**:
   ```bash
   # Create Consumer Key secret
   echo -n "your_consumer_key_here" | gcloud secrets create garmin-client-id \
     --data-file=- \
     --replication-policy="automatic"
   
   # Create Consumer Secret secret
   echo -n "your_consumer_secret_here" | gcloud secrets create garmin-client-secret \
     --data-file=- \
     --replication-policy="automatic"
   ```

2. **Grant access to Cloud Run service**:
   ```bash
   # Get service account email
   SERVICE_ACCOUNT=$(gcloud run services describe stepsquad-api \
     --region us-central1 \
     --format 'value(spec.template.spec.serviceAccountName)')
   
   # Grant access
   gcloud secrets add-iam-policy-binding garmin-client-id \
     --member="serviceAccount:${SERVICE_ACCOUNT}" \
     --role="roles/secretmanager.secretAccessor"
   
   gcloud secrets add-iam-policy-binding garmin-client-secret \
     --member="serviceAccount:${SERVICE_ACCOUNT}" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. **Reference secrets in Cloud Run**:
   ```bash
   gcloud run services update stepsquad-api \
     --update-secrets="GARMIN_CLIENT_ID=garmin-client-id:latest,GARMIN_CLIENT_SECRET=garmin-client-secret:latest,GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback" \
     --region us-central1
   ```

---

## Step 5: Verify Configuration

### Test OAuth Flow

1. **Start your backend** (if testing locally):
   ```bash
   cd apps/api
   uvicorn main:app --reload --port 8080
   ```

2. **Test OAuth authorization endpoint**:
   ```bash
   # Get authorization URL
   curl http://localhost:8080/oauth/garmin/authorize \
     -H "X-Dev-User: test@stepsquad.com"
   ```

3. **You should get**:
   ```json
   {
     "authorization_url": "https://connectapi.garmin.com/oauth-service/oauth/request_token?...",
     "state": "...",
     "provider": "garmin"
   }
   ```

### Test in Production

After DNS propagates:

1. **Test authorization endpoint**:
   ```bash
   curl https://api.stepsquad.club/oauth/garmin/authorize \
     -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
   ```

2. **Frontend integration**:
   - Go to `https://www.stepsquad.club/devices`
   - Click **"Connect Garmin"**
   - Should redirect to Garmin OAuth page

---

## Step 6: OAuth 1.0a Implementation Notes

### Important: Garmin Uses OAuth 1.0a (Not OAuth 2.0)

Garmin uses **OAuth 1.0a**, which is different from OAuth 2.0:

**OAuth 1.0a Flow:**
1. **Request Token** - Get temporary request token from Garmin
2. **Authorization** - Redirect user to Garmin to authorize
3. **Access Token** - Exchange request token for access token (with verifier)

**This is more complex than OAuth 2.0** (which Fitbit uses).

### Current Implementation Status

Our current `garmin_client.py` has placeholder implementations. To complete the OAuth 1.0a flow:

**Required Library:**
```bash
pip install oauthlib requests-oauthlib
```

**Or add to `apps/api/pyproject.toml`:**
```toml
dependencies = [
  # ... existing dependencies ...
  "oauthlib>=3.2.0",
  "requests-oauthlib>=1.3.1",
]
```

### Complete OAuth 1.0a Implementation

You'll need to update `apps/api/garmin_client.py` with full OAuth 1.0a flow using `oauthlib`.

**Example implementation:**
```python
from requests_oauthlib import OAuth1Session

def build_garmin_oauth_url(state: str) -> str:
    """Build Garmin OAuth 1.0a authorization URL"""
    oauth = OAuth1Session(
        GARMIN_CLIENT_ID,
        client_secret=GARMIN_CLIENT_SECRET,
        callback_uri=GARMIN_REDIRECT_URI
    )
    
    # Step 1: Get request token
    request_token_url = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
    fetch_response = oauth.fetch_request_token(request_token_url)
    
    # Step 2: Build authorization URL
    authorization_url = "https://connectapi.garmin.com/oauth-service/oauth/authorize"
    authorization_url = oauth.authorization_url(authorization_url)
    
    return authorization_url

def exchange_garmin_code(oauth_token: str, oauth_verifier: str) -> Dict[str, Any]:
    """Exchange OAuth 1.0a request token for access token"""
    oauth = OAuth1Session(
        GARMIN_CLIENT_ID,
        client_secret=GARMIN_CLIENT_SECRET,
        resource_owner_key=oauth_token,
        verifier=oauth_verifier
    )
    
    # Step 3: Get access token
    access_token_url = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    
    return {
        "access_token": oauth_tokens.get('oauth_token'),
        "token_secret": oauth_tokens.get('oauth_token_secret'),
        "token_type": "OAuth",
        "expires_in": None,  # OAuth 1.0a doesn't have expiration
    }
```

---

## Step 7: Update Garmin API Endpoints

After OAuth setup, verify API endpoints for fetching step data:

### Garmin API Endpoints

**Wellness API** (for step data):
- Base URL: `https://connectapi.garmin.com`
- Endpoint: `/wellness-service/wellness/dailySummary`
- Method: `GET`
- Authentication: OAuth 1.0a signed requests

**Example request:**
```python
def get_garmin_daily_steps(access_token: str, token_secret: str, date: date) -> int:
    """Fetch daily step count from Garmin API"""
    from requests_oauthlib import OAuth1Session
    
    oauth = OAuth1Session(
        GARMIN_CLIENT_ID,
        client_secret=GARMIN_CLIENT_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=token_secret
    )
    
    url = f"https://connectapi.garmin.com/wellness-service/wellness/dailySummary"
    params = {"date": date.isoformat()}
    
    response = oauth.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    steps = data.get("steps", 0)
    
    return int(steps)
```

---

## Step 8: Testing Checklist

After completing setup:

- [ ] Garmin Developer Program account approved
- [ ] OAuth client created and approved
- [ ] Consumer Key and Consumer Secret obtained
- [ ] Environment variables set in Cloud Run
- [ ] OAuth 1.0a library installed (`oauthlib`, `requests-oauthlib`)
- [ ] OAuth 1.0a implementation completed in `garmin_client.py`
- [ ] Callback URL matches: `https://api.stepsquad.club/oauth/garmin/callback`
- [ ] Test OAuth authorization endpoint
- [ ] Test OAuth callback endpoint
- [ ] Test device connection from frontend
- [ ] Test step data fetching from Garmin API

---

## Troubleshooting

### "Consumer Key not found" Error

- Verify Consumer Key is correct in environment variables
- Check for extra spaces or typos
- Ensure environment variable is set correctly

### "Invalid Consumer Secret" Error

- Verify Consumer Secret is correct
- Check for typos or missing characters
- Ensure secret hasn't expired or been regenerated

### "Callback URL mismatch" Error

- Verify callback URL in Garmin app matches exactly:
  - `https://api.stepsquad.club/oauth/garmin/callback`
- Check for trailing slashes or protocol differences
- Ensure HTTPS is used (not HTTP)

### "OAuth 1.0a implementation not found" Error

- Install required libraries:
  ```bash
  pip install oauthlib requests-oauthlib
  ```
- Or add to `pyproject.toml` dependencies
- Restart the service

### "Request token failed" Error

- Verify Consumer Key and Secret are correct
- Check callback URL in Garmin app matches environment variable
- Ensure Garmin Developer Program access is approved
- Verify API access permissions are granted

---

## Quick Reference

### Garmin OAuth 1.0a URLs

- **Request Token URL**: `https://connectapi.garmin.com/oauth-service/oauth/request_token`
- **Authorization URL**: `https://connectapi.garmin.com/oauth-service/oauth/authorize`
- **Access Token URL**: `https://connectapi.garmin.com/oauth-service/oauth/access_token`
- **API Base URL**: `https://connectapi.garmin.com`

### Environment Variables Needed

**For Production:**
```
GARMIN_CLIENT_ID=your_consumer_key
GARMIN_CLIENT_SECRET=your_consumer_secret
GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback
```

**For Local Development:**
```
GARMIN_CLIENT_ID=your_consumer_key
GARMIN_CLIENT_SECRET=your_consumer_secret
GARMIN_REDIRECT_URI=http://localhost:8080/oauth/garmin/callback
```

### Python Dependencies

Add to `apps/api/pyproject.toml`:
```toml
dependencies = [
  # ... existing dependencies ...
  "oauthlib>=3.2.0",
  "requests-oauthlib>=1.3.1",
]
```

---

## Next Steps After Setup

1. ✅ Complete OAuth 1.0a implementation in `garmin_client.py`
2. ✅ Test OAuth flow end-to-end
3. ✅ Test step data fetching from Garmin API
4. ✅ Test device connection from frontend
5. ✅ Monitor for any errors or issues

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Garmin App Configuration

