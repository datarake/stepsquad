# Garmin/Fitbit Integrations - Web-Based Implementation

**Date**: November 2, 2025  
**Approach**: ✅ **Web-Based (Backend + Frontend)**  
**Status**: 📋 **Recommended Architecture**

---

## ✅ Answer: Web-Based Integration is Recommended

**Yes, Garmin/Fitbit integrations can and should be implemented on the web** (backend + frontend), not requiring a mobile app. This is actually the more practical approach for your use case.

---

## 🏗️ Architecture Overview

### Recommended Approach: Web-Based OAuth Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Browser                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  StepSquad Web App (React)                            │  │
│  │  - "Connect Garmin" button                            │  │
│  │  - "Connect Fitbit" button                            │  │
│  │  - Link devices UI                                     │  │
│  │  - OAuth redirect handler                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              StepSquad Backend API (FastAPI)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OAuth Endpoints:                                     │  │
│  │  - GET  /oauth/garmin/authorize  → Redirect to Garmin│  │
│  │  - GET  /oauth/garmin/callback   → Handle OAuth code │  │
│  │  - GET  /oauth/fitbit/authorize  → Redirect to Fitbit │  │
│  │  - GET  /oauth/fitbit/callback   → Handle OAuth code │  │
│  │  - GET  /devices                 → List linked devices│  │
│  │  - POST /devices/{provider}/sync → Trigger sync      │  │
│  │  - DELETE /devices/{provider}    → Unlink device     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Background Workers:                                 │  │
│  │  - Periodic sync job (Cloud Scheduler)               │  │
│  │  - Fetch steps from Garmin/Fitbit APIs                │  │
│  │  - Store in Firestore                                 │  │
│  │  - Publish to Pub/Sub for processing                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           Garmin Connect API / Fitbit Web API               │
│  - OAuth 2.0 authentication                                 │
│  - Step data retrieval                                       │
│  - Activity data                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Details

### 1. Backend (FastAPI) - OAuth Flow

#### OAuth Endpoints

```python
# apps/api/main.py

@app.get("/oauth/garmin/authorize")
async def garmin_authorize(current_user: User = Depends(get_current_user)):
    """Initiate Garmin OAuth flow"""
    # Generate state token, store in session
    # Redirect to Garmin OAuth URL
    state = generate_state_token(current_user.uid)
    redirect_url = build_garmin_oauth_url(state)
    return {"authorization_url": redirect_url}

@app.get("/oauth/garmin/callback")
async def garmin_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user)
):
    """Handle Garmin OAuth callback"""
    # Verify state token
    # Exchange code for access token
    # Store tokens in Firestore (encrypted)
    # Return success
    tokens = exchange_garmin_code(code)
    store_device_tokens(current_user.uid, "garmin", tokens)
    return {"status": "connected", "provider": "garmin"}

@app.get("/oauth/fitbit/authorize")
async def fitbit_authorize(current_user: User = Depends(get_current_user)):
    """Initiate Fitbit OAuth flow"""
    # Similar to Garmin
    state = generate_state_token(current_user.uid)
    redirect_url = build_fitbit_oauth_url(state)
    return {"authorization_url": redirect_url}

@app.get("/oauth/fitbit/callback")
async def fitbit_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user)
):
    """Handle Fitbit OAuth callback"""
    # Similar to Garmin
    tokens = exchange_fitbit_code(code)
    store_device_tokens(current_user.uid, "fitbit", tokens)
    return {"status": "connected", "provider": "fitbit"}
```

#### Device Management

```python
@app.get("/devices")
async def list_devices(current_user: User = Depends(get_current_user)):
    """List user's linked devices"""
    devices = get_user_devices(current_user.uid)
    return {"devices": devices}

@app.post("/devices/{provider}/sync")
async def sync_device(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Manually trigger device sync"""
    sync_device_steps(current_user.uid, provider)
    return {"status": "syncing", "provider": provider}

@app.delete("/devices/{provider}")
async def unlink_device(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Unlink a device"""
    remove_device_tokens(current_user.uid, provider)
    return {"status": "unlinked", "provider": provider}
```

#### Background Sync Service

```python
# apps/workers/sync_worker.py

def sync_garmin_steps(uid: str, tokens: dict):
    """Fetch steps from Garmin API"""
    garmin_client = GarminAPI(tokens["access_token"])
    steps = garmin_client.get_daily_steps(date)
    # Store via existing /ingest/steps endpoint or directly
    write_daily_steps(uid, date, steps, provider="garmin")

def sync_fitbit_steps(uid: str, tokens: dict):
    """Fetch steps from Fitbit API"""
    fitbit_client = FitbitAPI(tokens["access_token"])
    steps = fitbit_client.get_daily_steps(date)
    write_daily_steps(uid, date, steps, provider="fitbit")

# Cloud Scheduler job (runs daily)
@app.post("/cron/sync-devices")
async def sync_all_devices():
    """Sync all linked devices"""
    all_devices = get_all_linked_devices()
    for device in all_devices:
        if device.provider == "garmin":
            sync_garmin_steps(device.uid, device.tokens)
        elif device.provider == "fitbit":
            sync_fitbit_steps(device.uid, device.tokens)
```

---

### 2. Frontend (React) - Device Linking UI

#### Device Settings Page

```typescript
// apps/web/src/pages/DeviceSettings.tsx

export function DeviceSettings() {
  const [devices, setDevices] = useState<Device[]>([]);
  
  const handleConnectGarmin = async () => {
    // Get authorization URL from backend
    const { authorization_url } = await api.getGarminAuthUrl();
    // Redirect to Garmin OAuth page
    window.location.href = authorization_url;
  };
  
  const handleConnectFitbit = async () => {
    const { authorization_url } = await api.getFitbitAuthUrl();
    window.location.href = authorization_url;
  };
  
  const handleSync = async (provider: string) => {
    await api.syncDevice(provider);
    toast.success(`Syncing ${provider}...`);
  };
  
  const handleUnlink = async (provider: string) => {
    await api.unlinkDevice(provider);
    toast.success(`${provider} unlinked`);
    loadDevices();
  };
  
  return (
    <div>
      <h2>Connected Devices</h2>
      
      {/* Linked Devices */}
      {devices.map(device => (
        <DeviceCard key={device.provider}>
          <div>{device.provider}</div>
          <div>Last sync: {device.last_sync}</div>
          <Button onClick={() => handleSync(device.provider)}>
            Sync Now
          </Button>
          <Button onClick={() => handleUnlink(device.provider)}>
            Unlink
          </Button>
        </DeviceCard>
      ))}
      
      {/* Connect New Devices */}
      <div>
        <Button onClick={handleConnectGarmin}>
          Connect Garmin
        </Button>
        <Button onClick={handleConnectFitbit}>
          Connect Fitbit
        </Button>
      </div>
    </div>
  );
}
```

#### OAuth Callback Handler

```typescript
// apps/web/src/pages/OAuthCallback.tsx

export function OAuthCallback() {
  useEffect(() => {
    // Handle OAuth callback from URL params
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');
    const provider = params.get('provider'); // or from URL path
    
    // Backend will verify and store tokens
    api.handleOAuthCallback(provider, code, state)
      .then(() => {
        toast.success(`${provider} connected!`);
        navigate('/devices');
      });
  }, []);
}
```

---

## ✅ Advantages of Web-Based Approach

### 1. **No Mobile App Required**
- ✅ Works on any device (desktop, mobile browser)
- ✅ No App Store approval needed
- ✅ Faster to implement
- ✅ Easier to test and debug

### 2. **Standard OAuth Flow**
- ✅ Well-documented OAuth 2.0 flows
- ✅ Both Garmin and Fitbit support web OAuth
- ✅ Secure token storage on backend
- ✅ Standard HTTP redirects

### 3. **Reuses Existing Infrastructure**
- ✅ Same backend API
- ✅ Same authentication system
- ✅ Same Firestore storage
- ✅ Same Pub/Sub processing

### 4. **Better User Experience**
- ✅ Link devices from any browser
- ✅ No need to download mobile app
- ✅ Works on iOS, Android, Desktop
- ✅ Easy to manage multiple devices

### 5. **Easier Implementation**
- ✅ No Flutter SDK needed
- ✅ No platform-specific code
- ✅ Web-based testing is easier
- ✅ Can use existing React components

---

## 📋 Implementation Steps

### Phase 1: Backend OAuth (4-6 hours)

1. **Garmin OAuth Integration** (2-3 hours)
   - Register Garmin app, get OAuth credentials
   - Implement `/oauth/garmin/authorize` endpoint
   - Implement `/oauth/garmin/callback` endpoint
   - Store tokens in Firestore (encrypted)

2. **Fitbit OAuth Integration** (2-3 hours)
   - Register Fitbit app, get OAuth credentials
   - Implement `/oauth/fitbit/authorize` endpoint
   - Implement `/oauth/fitbit/callback` endpoint
   - Store tokens in Firestore (encrypted)

### Phase 2: API Integration (4-6 hours)

3. **Garmin API Client** (2-3 hours)
   - Create Garmin API wrapper
   - Implement step data fetching
   - Handle token refresh
   - Error handling

4. **Fitbit API Client** (2-3 hours)
   - Create Fitbit API wrapper
   - Implement step data fetching
   - Handle token refresh
   - Error handling

### Phase 3: Background Sync (2-3 hours)

5. **Sync Worker** (2-3 hours)
   - Create Cloud Scheduler job
   - Implement daily sync logic
   - Handle multiple devices per user
   - Error handling and retries

### Phase 4: Frontend UI (3-4 hours)

6. **Device Settings Page** (2-3 hours)
   - Device list component
   - Connect buttons
   - Sync buttons
   - Unlink buttons

7. **OAuth Callback Handler** (1 hour)
   - Handle OAuth redirect
   - Show success/error messages
   - Redirect to device settings

**Total Time**: **13-19 hours** (much less than mobile app!)

---

## 🔐 Security Considerations

### Token Storage
- ✅ Store OAuth tokens encrypted in Firestore
- ✅ Use Google Cloud Secret Manager for API keys
- ✅ Implement token refresh logic
- ✅ Revoke tokens on unlink

### OAuth Security
- ✅ Use state tokens to prevent CSRF
- ✅ Verify state on callback
- ✅ Use HTTPS for all OAuth flows
- ✅ Set proper redirect URIs

### API Security
- ✅ Rate limiting for API calls
- ✅ Retry logic with exponential backoff
- ✅ Error handling and logging
- ✅ User permission checks

---

## 📊 Comparison: Web vs Mobile

| Aspect | Web-Based | Mobile App |
|--------|-----------|------------|
| **Development Time** | 13-19 hours | 40-52 hours |
| **Platform Support** | All browsers | iOS + Android |
| **OAuth Flow** | ✅ Standard web OAuth | ⚠️ Platform-specific |
| **Testing** | ✅ Browser-based | ⚠️ Device testing |
| **Deployment** | ✅ No App Store | ❌ App Store approval |
| **User Experience** | ✅ Works everywhere | ⚠️ App download needed |
| **Maintenance** | ✅ Single codebase | ❌ Two platforms |

**Winner**: ✅ **Web-Based** (faster, easier, better UX)

---

## 🎯 Recommended Architecture

### User Flow

1. **User clicks "Connect Garmin"** in web app
2. **Backend generates OAuth URL** and redirects to Garmin
3. **User authorizes** on Garmin website
4. **Garmin redirects back** to StepSquad with code
5. **Backend exchanges code** for access token
6. **Backend stores token** in Firestore
7. **Background job syncs** steps daily (Cloud Scheduler)
8. **User can manually trigger** sync from web UI

### Data Flow

```
User → Web UI → Backend OAuth → Garmin/Fitbit → OAuth Callback → Backend
  ↓
Token Storage (Firestore)
  ↓
Daily Sync Job → Garmin/Fitbit API → Step Data → /ingest/steps → Firestore
```

---

## ✅ Conclusion

**Yes, web-based integration is the correct and recommended approach!**

**Benefits**:
- ✅ No mobile app needed
- ✅ Faster to implement (13-19 hours vs 40-52 hours)
- ✅ Works on all devices
- ✅ Better user experience
- ✅ Easier to maintain

**Implementation**:
- Backend: OAuth endpoints, API clients, sync workers
- Frontend: Device settings page, OAuth callbacks
- Infrastructure: Cloud Scheduler, token storage

**This is the way to go!** 🚀

---

**Last Updated**: November 2, 2025  
**Status**: ✅ **Recommended Architecture**

