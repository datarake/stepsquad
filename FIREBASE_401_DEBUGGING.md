# Firebase 401 Unauthorized Error - Debugging Guide

## Problem

After successful Firebase login:
- ✅ Frontend gets Firebase ID token successfully
- ✅ Token is stored in localStorage
- ✅ `checkAuth()` is called
- ✅ `apiClient.getMe()` is called
- ❌ Backend returns `401 Unauthorized`

## Error in Browser Console

```
GET https://api.stepsquad.club/me 401 (Unauthorized)
Auth check failed: Error: Unauthorized
```

## Root Causes

### 1. Backend Token Verification Failing

**Possible causes:**
- Firebase Admin SDK not initialized with correct project ID
- Service account missing Firebase Admin role
- Token project mismatch

**Fixed in:**
- `apps/api/firebase_auth.py` - Explicit project ID set
- Service account granted Firebase Admin role

**Check:**
```bash
# Check backend health
curl https://api.stepsquad.club/health

# Should show:
{
  "ok": true,
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

### 2. Token Not Sent in Authorization Header

**Possible causes:**
- Token not retrieved from Firebase
- Token not stored in localStorage
- Token not sent in API request headers

**Fixed in:**
- `apps/web/src/api.ts` - Improved token retrieval
- `apps/web/src/auth.tsx` - Better token handling after login

**Check in browser console:**
```javascript
// Check if token is stored
localStorage.getItem('firebaseToken')

// Check if Firebase user is authenticated
// (from browser console, after importing firebase)
```

### 3. Token Expired or Invalid

**Possible causes:**
- Token expired (tokens expire in 1 hour)
- Token not refreshed
- Token corrupted in localStorage

**Check:**
- Token should be automatically refreshed by Firebase SDK
- Check Network tab for Authorization header

## Debugging Steps

### Step 1: Check Backend Deployment

```bash
# Check if backend has latest code
curl https://api.stepsquad.club/health | jq

# Check backend logs for errors
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stepsquad-api AND severity>=WARNING" \
  --limit 20 \
  --format="table(timestamp,severity,textPayload,jsonPayload.message)" \
  --project stepsquad-46d14
```

**Look for:**
- Firebase initialization errors
- Token verification errors
- Service account permission errors

### Step 2: Check Frontend Token Handling

**In browser console (after login):**

```javascript
// 1. Check if token is stored
console.log('Token in localStorage:', localStorage.getItem('firebaseToken'));

// 2. Check if Firebase user is authenticated
// (You'll need to import firebase functions in console)
// Check Network tab for Authorization header in /me request

// 3. Manually test token
const token = localStorage.getItem('firebaseToken');
if (token) {
  fetch('https://api.stepsquad.club/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
}
```

### Step 3: Check Network Tab

1. Open browser DevTools → Network tab
2. Filter by `/me` endpoint
3. Click on the failed request
4. Check **Headers** tab:
   - Look for `Authorization: Bearer <token>` header
   - Check if token is present and valid

5. Check **Response** tab:
   - Look for error message from backend
   - Example: `{"detail": "Invalid authentication token"}`

### Step 4: Check Backend Logs

```bash
# View recent backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stepsquad-api" \
  --limit 50 \
  --format="table(timestamp,severity,textPayload,jsonPayload.message)" \
  --project stepsquad-46d14

# Filter for Firebase errors
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stepsquad-api AND jsonPayload.message=~'Firebase|token'" \
  --limit 20 \
  --format=json \
  --project stepsquad-46d14
```

**Look for:**
- `Firebase Admin SDK initialized with Application Default Credentials (project: stepsquad-46d14)`
- `Invalid Firebase ID token`
- `Firebase Admin SDK not initialized`
- `Token verified successfully for user: burdibox@gmail.com`

## Fixes Applied

### Backend Fixes

1. **Explicit Project ID in Firebase Admin SDK**
   ```python
   project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID") or "stepsquad-46d14"
   _firebase_app = firebase_admin.initialize_app(options={'projectId': project_id})
   ```

2. **Service Account Permissions**
   ```bash
   # Grant Firebase Admin role
   gcloud projects add-iam-policy-binding stepsquad-46d14 \
     --member="serviceAccount:371825059669-compute@developer.gserviceaccount.com" \
     --role="roles/firebase.admin"
   ```

3. **Improved Error Handling**
   - Better logging for debugging
   - `check_revoked=False` to allow unverified emails
   - More descriptive error messages

### Frontend Fixes

1. **Improved Token Retrieval**
   - Try fresh token first
   - Fallback to stored token if fresh token unavailable
   - Better error handling

2. **Better Logging**
   - Console.debug messages for token operations
   - Clear error messages
   - Logs when using fresh vs stored token

3. **Token Handling After Login**
   - Store token immediately after login
   - Small delay before checking auth
   - Better error handling

## Verification

### Test Backend

```bash
# Test with a Firebase ID token
TOKEN="your-firebase-id-token"

curl -H "Authorization: Bearer $TOKEN" \
  https://api.stepsquad.club/me

# Should return:
{
  "uid": "CTUSFKKPJUQqgRHTk6UcocIeGs02",
  "email": "burdibox@gmail.com",
  "role": "MEMBER",
  "created_at": "...",
  "updated_at": "..."
}
```

### Test Frontend

1. Go to: https://www.stepsquad.club/login
2. Enter email: `burdibox@gmail.com`
3. Enter password: (your Firebase password)
4. Click "Sign in"
5. Should redirect to home page without 401 error

## Next Steps

1. **Wait for CI/CD Deployment**
   - Check GitHub Actions: https://github.com/datarake/stepsquad/actions
   - Wait for backend deployment to complete (~2-5 minutes)
   - Wait for frontend deployment to complete (~2-5 minutes)

2. **Test Again After Deployment**
   - Clear browser cache/localStorage
   - Try login again
   - Check browser console for errors
   - Check Network tab for Authorization header

3. **If Still Failing**
   - Check backend logs for detailed errors
   - Verify token is sent in Authorization header
   - Test token manually with curl
   - Check service account permissions

## Expected Behavior

### Successful Login Flow

1. User enters email/password
2. Frontend calls Firebase `signInWithEmailAndPassword`
3. Firebase returns ID token
4. Token stored in localStorage
5. `checkAuth()` is called
6. `apiClient.getMe()` is called with `Authorization: Bearer <token>` header
7. Backend verifies token with Firebase Admin SDK
8. Backend returns user data
9. Frontend stores user data
10. User redirected to home page ✅

### Current Issue

Step 7 is failing - backend returns 401 Unauthorized.

**Most likely cause:** Backend hasn't been redeployed with the fix yet, OR token is not being sent correctly.

## Quick Fixes

### If Token Not Sent

Check `apps/web/src/api.ts` - ensure token is retrieved and sent:

```typescript
const token = await firebaseGetIdToken();
if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}
```

### If Backend Can't Verify Token

Check `apps/api/firebase_auth.py` - ensure project ID is set:

```python
project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or "stepsquad-46d14"
_firebase_app = firebase_admin.initialize_app(options={'projectId': project_id})
```

---

**Last Updated**: November 3, 2025  
**Status**: Fixes applied, waiting for deployment

