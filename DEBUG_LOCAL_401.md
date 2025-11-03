# Debugging Local 401 Unauthorized Error

## Problem

When trying to login locally with Firebase auth (`burdibox@gmail.com | aloha1`):
- ✅ Frontend gets Firebase ID token successfully
- ✅ Token is stored in localStorage
- ✅ Frontend calls `/me` endpoint
- ❌ Backend returns `401 Unauthorized`

## Root Causes

### 1. Service Account Key Missing

**Symptom:** Backend can't initialize Firebase Admin SDK

**Check:**
```bash
ls -la apps/api/service-account-key.json
```

**Fix:**
1. Download service account key from Firebase Console
2. Save as `apps/api/service-account-key.json`
3. Restart backend

### 2. Backend Not Restarted

**Symptom:** Backend still using old config (`GCP_ENABLED=false`)

**Check:**
```bash
curl http://localhost:8080/health | jq
# Should show: "firebase_initialized": true
```

**Fix:**
1. Stop backend (Ctrl+C)
2. Restart: `cd apps/api && uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload`

### 3. Firebase Admin SDK Initialization Failed

**Symptom:** Backend logs show Firebase initialization errors

**Check Backend Logs:**
Look for:
- `Firebase Admin SDK initialized with Application Default Credentials`
- `Firebase Admin SDK initialization failed`
- `Failed to initialize Firebase with credentials file`

**Fix:**
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure service account key is valid JSON
- Check file permissions

### 4. Token Verification Failing

**Symptom:** Backend initialized but token verification fails

**Check:**
- Token might be expired
- Token might be for wrong project
- Backend might have wrong project ID

## Quick Fixes

### Option A: Use Dev Auth Bypass (Quick Test)

Since `ALLOW_DEV_AUTH_LOCAL=true` is set, you can test with dev auth:

1. **In browser console:**
   ```javascript
   // Test with X-Dev-User header
   fetch('http://localhost:8080/me', {
     headers: {
       'X-Dev-User': 'burdibox@gmail.com'
     }
   })
   .then(r => r.json())
   .then(console.log)
   .catch(console.error);
   ```

2. **Or test with curl:**
   ```bash
   curl -H "X-Dev-User: burdibox@gmail.com" http://localhost:8080/me
   ```

This bypasses Firebase auth and uses Firestore directly.

### Option B: Fix Firebase Auth

1. **Ensure service account key exists:**
   ```bash
   # Check if file exists
   ls -la apps/api/service-account-key.json
   
   # If not, download from Firebase Console
   # Firebase Console > Project Settings > Service Accounts
   # Click "Generate new private key"
   # Save as apps/api/service-account-key.json
   ```

2. **Check backend logs:**
   ```bash
   # When you start the backend, look for:
   # - "Firebase Admin SDK initialized with Application Default Credentials (project: stepsquad-46d14)"
   # - "Firebase Admin SDK initialization failed"
   ```

3. **Test backend health:**
   ```bash
   curl http://localhost:8080/health | jq
   ```
   
   Should show:
   ```json
   {
     "ok": true,
     "gcp_enabled": true,
     "firebase_initialized": true
   }
   ```

4. **Test token verification:**
   ```bash
   # Get token from browser console
   # localStorage.getItem('firebaseToken')
   
   TOKEN="your-firebase-token"
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/me
   ```

## Step-by-Step Debugging

### Step 1: Check Backend Status

```bash
curl http://localhost:8080/health | jq
```

**Expected:**
```json
{
  "ok": true,
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

**If `firebase_initialized: false`:**
- Backend can't initialize Firebase Admin SDK
- Check service account key exists
- Check backend logs for errors

### Step 2: Check Service Account Key

```bash
ls -la apps/api/service-account-key.json
```

**If missing:**
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Click "Generate new private key"
4. Save as `apps/api/service-account-key.json`

### Step 3: Check Backend Logs

When starting backend, look for:
```
Firebase Admin SDK initialized with Application Default Credentials (project: stepsquad-46d14)
```

Or errors like:
```
Firebase Admin SDK initialization failed: ...
Failed to initialize Firebase with credentials file: ...
```

### Step 4: Test Dev Auth Bypass

Since `ALLOW_DEV_AUTH_LOCAL=true`, test with dev auth:

```bash
curl -H "X-Dev-User: burdibox@gmail.com" http://localhost:8080/me
```

Should return user data if Firestore is working.

### Step 5: Test Firebase Auth

If dev auth works, Firebase auth should work too. Check:
1. Token is stored: `localStorage.getItem('firebaseToken')` in browser console
2. Token is sent: Check Network tab for `Authorization: Bearer <token>` header
3. Backend receives token: Check backend logs for token verification

## Common Errors

### Error: "Firebase Admin SDK not initialized"

**Cause:** Service account key not found or invalid

**Fix:**
1. Ensure `apps/api/service-account-key.json` exists
2. Check file permissions
3. Restart backend

### Error: "Invalid authentication token"

**Cause:** Token verification failing

**Possible reasons:**
1. Token expired (tokens expire in 1 hour)
2. Token for wrong project
3. Backend project ID mismatch

**Fix:**
1. Get fresh token (re-login)
2. Check backend project ID: `GOOGLE_CLOUD_PROJECT=stepsquad-46d14`
3. Verify token is for correct project

### Error: "Authentication required"

**Cause:** Token not sent in Authorization header

**Fix:**
1. Check browser console for token: `localStorage.getItem('firebaseToken')`
2. Check Network tab for `Authorization` header
3. Ensure frontend is configured with Firebase auth

## Recommended Approach

### For Testing (Quick)

Use dev auth bypass:
```bash
# Test with X-Dev-User header
curl -H "X-Dev-User: burdibox@gmail.com" http://localhost:8080/me
```

### For Production-Like Testing

Fix Firebase auth:
1. ✅ Ensure service account key exists
2. ✅ Restart backend
3. ✅ Check backend health endpoint
4. ✅ Test with Firebase token

## Next Steps

1. **Check backend health**: `curl http://localhost:8080/health`
2. **Check service account key**: `ls apps/api/service-account-key.json`
3. **Check backend logs**: Look for Firebase initialization messages
4. **Test dev auth**: `curl -H "X-Dev-User: burdibox@gmail.com" http://localhost:8080/me`
5. **Test Firebase auth**: Login again and check Network tab

---

**Last Updated**: November 3, 2025  
**Status**: Debugging Guide

