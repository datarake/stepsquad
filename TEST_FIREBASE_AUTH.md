# Test Firebase Authentication - Step by Step

**Date**: November 1, 2025  
**Status**: Ready to Test

---

## ✅ What's Already Configured

- ✅ Service account key saved securely
- ✅ Backend `.env` configured
- ✅ Frontend `.env.local` configured
- ✅ Custom claims set (`role: ADMIN`)
- ✅ Service account has Firebase Admin role
- ✅ Admin user created: `admin@stepsquad.com`

---

## 🧪 Test Steps

### Step 1: Verify Backend Health ✅

```bash
# Terminal 1: Start Backend
cd apps/api
export GCP_ENABLED=true
export GOOGLE_APPLICATION_CREDENTIALS=/Users/bogdan/.config/stepsquad/firebase-service-account.json
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

**Test Health Endpoint:**
```bash
# Terminal 2: Test Health
curl http://localhost:8080/health
```

**Expected Response:**
```json
{
  "ok": true,
  "time": "2025-11-01T...",
  "tz": "Europe/Bucharest",
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

**✅ If `firebase_initialized: true` → Backend is ready!**

---

### Step 2: Verify Frontend Can Start ✅

```bash
# Terminal 3: Start Frontend
cd apps/web
pnpm dev
```

**Expected Output:**
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5174/
➜  Network: use --host to expose
```

**Open Browser:**
- Go to http://localhost:5174
- Should show the login page

**✅ If login page loads → Frontend is ready!**

---

### Step 3: Test Authentication Flow ✅

#### 3.1: Sign In

1. Click **"Sign in"** button
2. Enter email: `admin@stepsquad.com`
3. Enter password: (your Firebase password)
4. Click **"Sign in"**

**Expected:**
- Should redirect to home page (`/`)
- Should show admin features
- No error messages

**✅ If redirected to home → Authentication works!**

#### 3.2: Verify User Role

After signing in, check browser console or network tab:
- Look for request to `/me` endpoint
- Response should show:
  ```json
  {
    "uid": "12oy8e2D0NY45UPP4zCsPqhhyVF3",
    "email": "admin@stepsquad.com",
    "role": "ADMIN"
  }
  ```

**✅ If `role: ADMIN` → Role assignment works!**

#### 3.3: Test Admin Features

1. Try to create a competition:
   - Should see **"Create Competition"** button
   - Should be able to create a competition
2. Try to view users:
   - Should see **"Users"** link/menu
   - Should be able to view all users

**✅ If admin features work → Role-based access works!**

---

### Step 4: Test API Directly (Optional) ✅

```bash
# Get Firebase ID token (from browser console after signing in)
# Or use this to test:

# Test /me endpoint (should require authentication)
curl http://localhost:8080/me
```

**Expected Response (without token):**
```json
{
  "detail": "Authentication required"
}
```

**✅ If `401` error → Authentication is enforced!**

---

## 🔍 Troubleshooting

### Backend Issues

#### Error: "Firebase Admin SDK not initialized"

**Solution:**
```bash
# Check environment variables
echo $GCP_ENABLED
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify service account key exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Check service account key is valid
python3 -c "
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('$GOOGLE_APPLICATION_CREDENTIALS')
app = firebase_admin.initialize_app(cred)
print('✅ Key is valid')
firebase_admin.delete_app(app)
"
```

#### Error: "firebase_initialized: false"

**Solution:**
- Check `GCP_ENABLED=true` is set
- Verify service account key path is correct
- Check service account has Firebase Admin role
- Look at backend logs for specific error

### Frontend Issues

#### Error: "Firebase not configured"

**Solution:**
```bash
# Check .env.local file exists
cat apps/web/.env.local

# Verify VITE_USE_DEV_AUTH=false
grep VITE_USE_DEV_AUTH apps/web/.env.local

# Restart dev server after changing .env.local
pnpm dev
```

#### Error: "Sign in failed"

**Solution:**
- Verify Email/Password authentication is enabled in Firebase Console
- Check user exists in Firebase Authentication
- Verify email/password are correct
- Check browser console for specific error message

#### Error: "Invalid authentication token"

**Solution:**
- User needs to sign out and sign in again (custom claims need fresh token)
- Check token expiration (tokens expire after 1 hour)
- Verify backend is receiving the token correctly

---

## ✅ Success Checklist

- [ ] Backend health endpoint shows `firebase_initialized: true`
- [ ] Frontend login page loads
- [ ] Can sign in with `admin@stepsquad.com`
- [ ] Redirects to home page after sign in
- [ ] `/me` endpoint returns `role: ADMIN`
- [ ] Admin features are accessible (create competition, view users)
- [ ] Can create a competition (admin feature)
- [ ] Can view users (admin feature)

---

## 📋 Quick Test Commands

```bash
# Test backend health
curl http://localhost:8080/health | jq

# Test authentication required
curl http://localhost:8080/me

# Check Firebase setup
cd apps/api
python scripts/check_firebase_setup.py

# Set custom claims (if needed again)
python scripts/set_admin_claim.py admin@stepsquad.com
```

---

## 🎯 Next Steps After Testing

Once everything works:

1. **Test User Management**
   - Create regular member user
   - Verify member features work (read-only)
   - Verify member cannot access admin features

2. **Test Competition Features**
   - Create competition as admin
   - View competitions as member
   - Test team creation
   - Test step ingestion

3. **Test Leaderboards**
   - Submit steps
   - View individual leaderboard
   - View team leaderboard

4. **Production Deployment**
   - Deploy to Cloud Run
   - Test production authentication
   - Set up monitoring

---

**Status**: ✅ **Ready to Test**

