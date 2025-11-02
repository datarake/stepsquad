# Development vs Production Environment Guide

Complete explanation of the differences between local/dev and production environments in StepSquad.

---

## Overview

StepSquad supports **two modes** of operation:

1. **Development/Local Mode** (`GCP_ENABLED=false`)
2. **Production Mode** (`GCP_ENABLED=true`)

The main differences are in:
- **Authentication** (dev bypass vs Firebase)
- **Database** (in-memory vs Firestore)
- **Cloud Services** (disabled vs enabled)

---

## Authentication

### Development Mode (`GCP_ENABLED=false` / `VITE_USE_DEV_AUTH=true`)

**How it works:**
- **No password required** - just enter an email address
- Uses `X-Dev-User` header for authentication
- Email `admin@stepsquad.com` gets ADMIN role
- All other emails get MEMBER role
- Users are created automatically on first login

**Frontend:**
- `VITE_USE_DEV_AUTH=true` in `.env.local`
- Stores email in `localStorage.getItem('devEmail')`
- Sends `X-Dev-User: <email>` header with all API requests

**Backend:**
- `GCP_ENABLED=false` (or not set)
- Accepts `X-Dev-User` header
- Creates users on-the-fly in in-memory storage

### Production Mode (`GCP_ENABLED=true` / `VITE_USE_DEV_AUTH=false`)

**How it works:**
- **Password required** - Firebase Email/Password authentication
- Uses Firebase ID tokens (`Authorization: Bearer <token>`)
- Roles determined by Firebase custom claims or email
- Users managed through Firebase Authentication

**Frontend:**
- `VITE_USE_DEV_AUTH=false` in production
- Uses Firebase Authentication SDK
- Sends `Authorization: Bearer <firebase-token>` header

**Backend:**
- `GCP_ENABLED=true`
- Verifies Firebase ID tokens
- Creates users in Firestore on first login

---

## Database Storage

### Development Mode (In-Memory Storage)

**What it uses:**
- **In-memory dictionaries** (Python dictionaries)
- Data stored in process memory
- **Lost when server restarts**

**Where it's stored:**
- **No database** - everything in RAM
- Users: `USERS = {}` dictionary
- Competitions: `COMPETITIONS = {}` dictionary
- Teams: `TEAMS = {}` dictionary
- Daily Steps: `DAILY_STEPS = {}` dictionary

**Persistence:**
- ❌ **NOT persisted** - data is lost on restart
- ✅ **Fast** - no network calls
- ✅ **Easy testing** - clean slate each time

**Example Code** (`apps/api/storage.py`):
```python
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"

# In-memory storage for dev
USERS = {}
COMPETITIONS = {}
TEAMS = {}
DAILY_STEPS = {}

def upsert_user(uid, user_data):
    if GCP_ENABLED and _fs_coll("users"):
        # Use Firestore
        _fs_coll("users").document(uid).set(user_data, merge=True)
    else:
        # Use in-memory storage
        USERS[uid] = user_data
```

### Production Mode (Firestore Database)

**What it uses:**
- **Google Cloud Firestore** (NoSQL document database)
- Data stored in Google Cloud
- **Persistent** across restarts

**Where it's stored:**
- **Google Cloud Firestore** (cloud database)
- Users: `users` collection
- Competitions: `competitions` collection
- Teams: `teams` collection
- Daily Steps: `daily_steps` collection

**Persistence:**
- ✅ **Persisted** - data survives restarts
- ✅ **Scalable** - handles many users
- ✅ **Real-time** - can subscribe to changes
- ⚠️ **Network calls** - requires internet connection

**Example Code** (`apps/api/storage.py`):
```python
def upsert_user(uid, user_data):
    if GCP_ENABLED and _fs_coll("users"):
        # Use Firestore
        _fs_coll("users").document(uid).set(user_data, merge=True)
    else:
        # Use in-memory storage
        USERS[uid] = user_data
```

---

## Key Differences Summary

| Feature | Development Mode | Production Mode |
|---------|------------------|-----------------|
| **Authentication** | Email only (no password) | Firebase Email/Password |
| **Auth Header** | `X-Dev-User: <email>` | `Authorization: Bearer <token>` |
| **Database** | In-memory (RAM) | Firestore (Google Cloud) |
| **Data Persistence** | ❌ Lost on restart | ✅ Persisted |
| **Cloud Services** | Disabled | Enabled |
| **Pub/Sub** | Disabled | Enabled |
| **BigQuery** | Disabled | Enabled |
| **OAuth Devices** | In-memory | Firestore |

---

## Environment Variables

### Backend (`apps/api/`)

**Development Mode:**
```bash
GCP_ENABLED=false  # or not set (defaults to false)
COMP_TZ=Europe/Bucharest
```

**Production Mode:**
```bash
GCP_ENABLED=true
COMP_TZ=Europe/Bucharest
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
FIREBASE_WEB_CLIENT_ID=your-firebase-client-id
```

### Frontend (`apps/web/`)

**Development Mode:**
```bash
VITE_USE_DEV_AUTH=true
VITE_API_BASE_URL=http://localhost:8080
```

**Production Mode:**
```bash
VITE_USE_DEV_AUTH=false
VITE_API_BASE_URL=https://api.stepsquad.club
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-auth-domain
# ... other Firebase config ...
```

---

## Database Behavior

### Development Mode

**Storage:**
```python
# All data in Python dictionaries (in-memory)
USERS = {}           # uid -> user_data
COMPETITIONS = {}    # comp_id -> competition_data
TEAMS = {}           # team_id -> team_data
DAILY_STEPS = {}     # key -> step_data
```

**Characteristics:**
- ✅ **Fast** - no network latency
- ✅ **Simple** - no setup required
- ❌ **Not persistent** - lost on restart
- ❌ **Not shared** - each process has its own data
- ❌ **Limited size** - RAM limits

### Production Mode

**Storage:**
```python
# All data in Firestore (cloud database)
users_collection = fs.collection("users")
competitions_collection = fs.collection("competitions")
teams_collection = fs.collection("teams")
daily_steps_collection = fs.collection("daily_steps")
```

**Characteristics:**
- ✅ **Persistent** - survives restarts
- ✅ **Shared** - multiple instances can access same data
- ✅ **Scalable** - handles millions of documents
- ✅ **Real-time** - can subscribe to changes
- ⚠️ **Network calls** - requires internet
- ⚠️ **Costs money** - Firestore charges per operation

---

## Common Issues

### Issue 1: 401 Unauthorized in Dev Mode

**Symptom:**
- Getting `401 Unauthorized` on `/me` endpoint
- Even with email entered

**Causes:**
1. Backend has `GCP_ENABLED=true` but frontend uses dev auth
2. Frontend not sending `X-Dev-User` header
3. Backend not configured for dev mode

**Fix:**
1. Set backend `GCP_ENABLED=false` (or don't set it)
2. Set frontend `VITE_USE_DEV_AUTH=true`
3. Restart both services

### Issue 2: Data Lost on Restart (Dev Mode)

**Symptom:**
- All users/competitions disappear when backend restarts

**Cause:**
- Development mode uses in-memory storage (not persisted)

**Fix:**
- This is expected behavior in dev mode
- Use production mode (Firestore) if you need persistence
- Or save data to files if needed for dev

### Issue 3: Different Data in Dev vs Production

**Symptom:**
- Data created locally doesn't appear in production (or vice versa)

**Cause:**
- Dev mode and production use different databases
- Dev = in-memory, Production = Firestore

**Fix:**
- This is expected - they're separate systems
- Use production mode if you want same database

---

## Switching Between Modes

### From Development to Production

1. **Backend:**
   ```bash
   export GCP_ENABLED=true
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

2. **Frontend:**
   ```bash
   # Update .env.production
   VITE_USE_DEV_AUTH=false
   VITE_API_BASE_URL=https://api.stepsquad.club
   # Add Firebase config...
   ```

### From Production to Development

1. **Backend:**
   ```bash
   export GCP_ENABLED=false
   # or unset it
   ```

2. **Frontend:**
   ```bash
   # Update .env.local
   VITE_USE_DEV_AUTH=true
   VITE_API_BASE_URL=http://localhost:8080
   ```

---

## Best Practices

### Development Mode

- ✅ Use for local development and testing
- ✅ Fast iteration - no database setup needed
- ✅ Clean slate each restart
- ❌ Don't use for production data

### Production Mode

- ✅ Use for production deployments
- ✅ Persistent, scalable database
- ✅ Real authentication with Firebase
- ❌ Requires Google Cloud setup

---

## Summary

**Development Mode:**
- No password auth (email only)
- In-memory database (not persisted)
- Fast, simple, no setup
- Data lost on restart

**Production Mode:**
- Firebase authentication (password required)
- Firestore database (persistent)
- Scalable, shared, real-time
- Data persists across restarts

**Key Point:** Development and production use **completely separate databases**. Data in dev mode is not in production, and vice versa. They are independent systems.

---

**Last Updated**: November 2, 2025  
**Status**: Complete Guide

