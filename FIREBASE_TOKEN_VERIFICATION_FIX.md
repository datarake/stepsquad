# Firebase Token Verification Fix

## Problem

When trying to login in production, you get:
```
{"detail":"Invalid authentication token"}
```

**But Firebase authentication is working:**
- ✅ Frontend successfully gets Firebase ID token
- ✅ Token is sent to backend with `Authorization: Bearer <token>` header
- ❌ Backend returns "Invalid authentication token"

## Root Cause

The backend Firebase Admin SDK is not properly initialized or configured to verify tokens. This can happen when:

1. **Firebase Admin SDK not initialized** - `GCP_ENABLED=true` but Firebase Admin SDK failed to initialize
2. **Missing service account credentials** - `GOOGLE_APPLICATION_CREDENTIALS` not set or invalid
3. **Token verification failing** - Firebase Admin SDK can't verify the token

## Solution

### Step 1: Verify Backend Environment Variables

Check if backend has correct environment variables:

```bash
gcloud run services describe stepsquad-api \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

**Required:**
- ✅ `GCP_ENABLED=true`
- ✅ `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json` (or use Application Default Credentials)

### Step 2: Check Firebase Admin SDK Initialization

The backend needs Firebase Admin SDK initialized. Check:

1. **Service account credentials**:
   - Service account key should be mounted in Cloud Run, OR
   - Use Application Default Credentials (ADC) with service account attached to Cloud Run

2. **Firebase Admin SDK initialization**:
   - Check if `init_firebase()` is called
   - Check if it succeeds

### Step 3: Update Backend to Use Service Account

#### Option A: Use Application Default Credentials (Recommended)

If the Cloud Run service has a service account attached with Firebase Admin role:

1. **Verify service account is attached**:
   ```bash
   gcloud run services describe stepsquad-api \
     --region us-central1 \
     --format="value(spec.template.spec.serviceAccountName)"
   ```

2. **Grant Firebase Admin role** (if not already granted):
   ```bash
   SERVICE_ACCOUNT=$(gcloud run services describe stepsquad-api \
     --region us-central1 \
     --format="value(spec.template.spec.serviceAccountName)")
   
   gcloud projects add-iam-policy-binding stepsquad-46d14 \
     --member="serviceAccount:${SERVICE_ACCOUNT}" \
     --role="roles/firebase.admin"
   ```

3. **Update backend code** to use ADC:
   - Already done in `firebase_auth.py` - it tries ADC first

#### Option B: Mount Service Account Key

1. **Upload service account key to Secret Manager**:
   ```bash
   # Create secret
   echo -n "$(cat path/to/service-account-key.json)" | \
     gcloud secrets create firebase-admin-key \
     --data-file=- \
     --replication-policy="automatic"
   ```

2. **Mount secret in Cloud Run**:
   ```bash
   gcloud run services update stepsquad-api \
     --update-secrets="GOOGLE_APPLICATION_CREDENTIALS=firebase-admin-key:latest" \
     --region us-central1
   ```

### Step 4: Verify Token Verification Logic

The backend code (`apps/api/firebase_auth.py`) should:
1. Initialize Firebase Admin SDK
2. Verify the ID token
3. Extract user information
4. Return user data

**Current implementation**:
```python
def verify_id_token(id_token: str) -> Dict:
    global _firebase_app
    
    if _firebase_app is None:
        init_firebase()
    
    if _firebase_app is None:
        raise ValueError("Firebase Admin SDK not initialized")
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError as e:
        raise ValueError("Invalid authentication token")
    except Exception as e:
        raise ValueError(f"Authentication verification failed: {str(e)}")
```

---

## Troubleshooting

### Error: "Firebase Admin SDK not initialized"

**Cause**: Firebase Admin SDK failed to initialize.

**Check:**
1. ✅ `GCP_ENABLED=true` in backend
2. ✅ Service account credentials available
3. ✅ Service account has Firebase Admin role

**Fix:**
- Grant Firebase Admin role to service account
- Or mount service account key as secret

### Error: "Invalid authentication token"

**Cause**: Token verification failed.

**Possible reasons:**
1. ❌ Token expired (tokens expire in 1 hour)
2. ❌ Token is for wrong project
3. ❌ Firebase Admin SDK not properly initialized
4. ❌ Service account doesn't have permission to verify tokens

**Fix:**
1. Ensure Firebase Admin SDK is initialized
2. Ensure service account has Firebase Admin role
3. Check token is not expired
4. Verify token is for correct project

### Check Backend Logs

View Cloud Run logs to see detailed errors:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stepsquad-api" \
  --limit 50 \
  --format json \
  --project stepsquad-46d14
```

Look for:
- Firebase initialization errors
- Token verification errors
- Service account permission errors

---

## Verification Steps

### 1. Check Backend Health

```bash
curl https://api.stepsquad.club/health
```

Should show:
```json
{
  "ok": true,
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

### 2. Test Token Verification

```bash
# Get a Firebase ID token (from frontend)
TOKEN="your-firebase-id-token"

# Test backend endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://api.stepsquad.club/me
```

Should return:
```json
{
  "uid": "...",
  "email": "burdibox@gmail.com",
  "role": "MEMBER"
}
```

---

## Quick Fix Checklist

- [ ] Backend has `GCP_ENABLED=true`
- [ ] Service account attached to Cloud Run service
- [ ] Service account has Firebase Admin role
- [ ] Backend logs show Firebase initialized successfully
- [ ] Test token verification endpoint
- [ ] Verify user creation works

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Troubleshooting

