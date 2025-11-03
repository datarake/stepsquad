# Aligning Dev and Prod Environments - Analysis & Guide

## Current State

### Dev Environment (`GCP_ENABLED=false`)
- **Database**: In-memory dictionaries (USERS, TEAMS, COMPETITIONS, etc.)
- **Authentication**: `X-Dev-User` header (no password required)
- **Storage**: Data lost on restart
- **Firebase**: Not initialized
- **Firestore**: Not used

### Prod Environment (`GCP_ENABLED=true`)
- **Database**: Firestore (persistent)
- **Authentication**: Firebase ID tokens (Bearer token)
- **Storage**: Persistent across restarts
- **Firebase**: Initialized with Admin SDK
- **Firestore**: Used for all data operations

## Architecture Analysis

### How It Works

The code is already designed to support both modes:

1. **Storage Layer** (`storage.py`):
   ```python
   # Writes to BOTH in-memory AND Firestore when GCP_ENABLED=true
   if GCP_ENABLED and _fs_coll("users"):
       _fs_coll("users").document(uid).set(data, merge=True)
   USERS[uid] = {**USERS.get(uid, {}), **data}
   ```

2. **Authentication** (`main.py`):
   ```python
   if not GCP_ENABLED and x_dev_user:
       # Dev mode: X-Dev-User header
   if GCP_ENABLED and authorization:
       # Prod mode: Firebase ID token
   ```

3. **GCP Clients** (`gcp_clients.py`):
   ```python
   if not GCP_ENABLED:
       return  # Skip Firestore initialization
   firestore_client = firestore.Client()
   ```

### Difficulty: **LOW** ✅

The code already supports using Firestore locally - you just need to:
1. Set `GCP_ENABLED=true`
2. Set `GOOGLE_APPLICATION_CREDENTIALS` to service account key
3. Optionally: Allow dev auth bypass for local testing

## Solution: Hybrid Mode

Create a "local production" mode that:
- Uses Firestore (same database as prod)
- Uses Firebase Auth (same auth as prod)
- Optionally allows dev auth bypass for easier testing

### Option 1: Full Production Mode Locally (Recommended)

**Use exact same setup as production:**

1. **Set environment variables in `apps/api/.env.local`:**
   ```bash
   # Enable GCP features
   GCP_ENABLED=true
   
   # Set Google Cloud project
   GOOGLE_CLOUD_PROJECT=stepsquad-46d14
   GCP_PROJECT_ID=stepsquad-46d14
   
   # Set service account credentials path
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   
   # Or use Application Default Credentials (if gcloud auth is configured)
   # GOOGLE_APPLICATION_CREDENTIALS= (leave empty)
   
   # Timezone
   COMP_TZ=Europe/Bucharest
   
   # OAuth credentials (same as prod)
   FITBIT_CLIENT_ID=23THXK
   FITBIT_CLIENT_SECRET=3f319445dd6e4824bd2f7f579440cd36
   FITBIT_REDIRECT_URI=http://localhost:8080/oauth/fitbit/callback
   ```

2. **Download service account key** (if not already):
   ```bash
   # The service account key should be at:
   # apps/api/service-account-key.json
   ```

3. **Run backend:**
   ```bash
   cd apps/api
   # The .env.local will be automatically loaded by main.py
   uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

**Pros:**
- ✅ Exact same environment as production
- ✅ Same database (Firestore)
- ✅ Same authentication (Firebase)
- ✅ Easy to debug production issues locally

**Cons:**
- ❌ Need service account key file
- ❌ Writes to production Firestore (but you said you don't care)
- ❌ Need Firebase token for testing (but frontend handles this)

### Option 2: Hybrid Mode with Dev Auth Bypass

**Use Firestore but allow dev auth bypass for easier testing:**

1. **Add a new environment variable `ALLOW_DEV_AUTH_LOCAL=true`**
2. **Modify `main.py` to allow dev auth even when `GCP_ENABLED=true` (only when `ALLOW_DEV_AUTH_LOCAL=true`)**

This would let you:
- Use Firestore (same data as prod)
- Use `X-Dev-User` header for testing (no Firebase token needed)
- Still test Firebase auth when needed

### Option 3: Separate Firestore Database for Dev

**Use a different Firestore database for local dev:**

1. Create a separate Firestore database: `stepsquad-dev`
2. Set project ID to use dev database
3. Keep prod database untouched

**Pros:**
- ✅ Don't pollute production data
- ✅ Can reset dev database easily

**Cons:**
- ❌ More complex setup
- ❌ Different database might hide prod issues

## Recommended: Option 1 (Full Production Mode Locally)

Since you said "I don't care about the date, I can manually reset the db if I want", Option 1 is perfect.

### Implementation Steps

1. **Update `apps/api/.env.local`:**
   ```bash
   GCP_ENABLED=true
   GOOGLE_CLOUD_PROJECT=stepsquad-46d14
   GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
   COMP_TZ=Europe/Bucharest
   ```

2. **Ensure service account key exists:**
   ```bash
   # Should be at: apps/api/service-account-key.json
   # (The Firebase Admin SDK key you saved earlier)
   ```

3. **Update frontend `apps/web/.env.local`:**
   ```bash
   VITE_USE_DEV_AUTH=false
   VITE_API_BASE_URL=http://localhost:8080
   # Firebase config should already be in .env.local
   ```

4. **Test:**
   ```bash
   # Backend will now use Firestore
   cd apps/api
   uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   
   # Frontend will now use Firebase auth
   cd apps/web
   pnpm dev
   ```

## Code Changes Required

### Minimal Changes Needed

The code already supports this! Just need to:

1. **Ensure `.env.local` loading works** (already done ✅)
2. **Optional: Add dev auth bypass when local** (if you want easier testing)

### Optional: Dev Auth Bypass

If you want to test without Firebase tokens locally, add this to `main.py`:

```python
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_dev_user: Optional[str] = Header(None)
) -> User:
    GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
    ALLOW_DEV_AUTH_LOCAL = os.getenv("ALLOW_DEV_AUTH_LOCAL", "false").lower() == "true"
    
    # Allow dev auth when ALLOW_DEV_AUTH_LOCAL=true (for local testing)
    if (not GCP_ENABLED or ALLOW_DEV_AUTH_LOCAL) and x_dev_user:
        # Dev mode authentication
        ...
    
    # Firebase authentication (production mode)
    if GCP_ENABLED and authorization:
        ...
```

Then in `.env.local`:
```bash
GCP_ENABLED=true
ALLOW_DEV_AUTH_LOCAL=true  # Allow X-Dev-User header even with GCP_ENABLED=true
```

## Testing Strategy

### Before Switching

1. **Backup current dev data** (if any):
   - Export from in-memory storage (or just restart with new setup)

### After Switching

1. **Test Firestore connection:**
   ```bash
   curl http://localhost:8080/health
   # Should show: "firebase_initialized": true
   ```

2. **Test authentication:**
   - Option A: Use Firebase auth (same as prod)
   - Option B: Use `X-Dev-User` header if `ALLOW_DEV_AUTH_LOCAL=true`

3. **Test data operations:**
   - Create a user/competition
   - Restart backend
   - Data should persist (in Firestore)

## Reset Database

If you want to reset the Firestore database:

```python
# Create a script: apps/api/scripts/reset_firestore.py
from google.cloud import firestore

client = firestore.Client()
collections = ['users', 'teams', 'competitions', 'daily_steps', 'team_members', 'device_tokens']

for coll_name in collections:
    coll = client.collection(coll_name)
    docs = coll.stream()
    for doc in docs:
        doc.reference.delete()
    print(f"Deleted all documents from {coll_name}")

print("✅ Firestore database reset complete")
```

Run it:
```bash
cd apps/api
GCP_ENABLED=true GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json \
  uv run python scripts/reset_firestore.py
```

## Summary

**Difficulty**: **LOW** ✅

The code already supports using Firestore locally. You just need to:

1. ✅ Set `GCP_ENABLED=true` in `.env.local`
2. ✅ Set `GOOGLE_APPLICATION_CREDENTIALS` to service account key path
3. ✅ Restart backend
4. ✅ Update frontend to use Firebase auth (already done)

**No code changes required!** The architecture already supports this.

---

**Next Steps:**
1. Update `apps/api/.env.local` with `GCP_ENABLED=true`
2. Test backend health endpoint
3. Test authentication with Firebase
4. Verify data persists in Firestore

