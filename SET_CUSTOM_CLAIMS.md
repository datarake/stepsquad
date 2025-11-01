# Setting Firebase Custom Claims - Guide

**Date**: November 1, 2025  
**Issue**: Custom claims cannot be set via Firebase Console UI

---

## 📋 Overview

Firebase Custom Claims cannot be set directly through the Firebase Console web interface. They must be set programmatically using the Firebase Admin SDK.

**Your user details:**
- **Email**: `admin@stepsquad.com`
- **User UID**: `12oy8e2D0NY45UPP4zCsP`

---

## 🔧 Solution: Use Script to Set Custom Claims

I've created a Python script to set custom claims for your admin user.

### Option A: Using the Script (Recommended)

#### Step 1: Download Service Account Key (if you haven't already)

1. Go to [Firebase Console](https://console.firebase.google.com/project/stepsquad-46d14)
2. Go to **Project Settings** → **Service accounts** tab
3. Click **"Generate new private key"** (choose Python)
4. Save the JSON file (e.g., `firebase-service-account.json`)
5. **DO NOT commit this file to git!**

#### Step 2: Set Up Environment Variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
```

#### Step 3: Run the Script

```bash
cd apps/api

# Using default email (admin@stepsquad.com)
python scripts/set_admin_claim.py

# Or specify a different email
python scripts/set_admin_claim.py user@example.com
```

**Expected Output:**
```
============================================================
Firebase Custom Claims Setup
============================================================

Setting ADMIN role for: admin@stepsquad.com

✅ Found user: admin@stepsquad.com (UID: 12oy8e2D0NY45UPP4zCsP)
✅ Custom claim 'role: ADMIN' set for admin@stepsquad.com
✅ Verified: Custom claim is set correctly
   User: admin@stepsquad.com
   UID: 12oy8e2D0NY45UPP4zCsP
   Custom Claims: {'role': 'ADMIN'}

============================================================
✅ Setup Complete!
============================================================
```

---

### Option B: Use Python Interactive Script

If you prefer to run it interactively:

```python
import firebase_admin
from firebase_admin import credentials, auth

# Initialize with your service account key
cred = credentials.Certificate('/path/to/firebase-service-account.json')
firebase_admin.initialize_app(cred)

# Get user by email
user = auth.get_user_by_email('admin@stepsquad.com')

# Set custom claim
auth.set_custom_user_claims(user.uid, {'role': 'ADMIN'})

# Verify
user = auth.get_user(user.uid)
print(f"Custom claims: {user.custom_claims}")
```

---

### Option C: Use Email-Based Role Assignment (Alternative)

If you don't want to use custom claims, you can use email-based role assignment. The backend already supports this!

**How it works:**
- If a user's email matches `ADMIN_EMAIL` (default: `admin@stepsquad.com`), they get ADMIN role
- This happens automatically when they authenticate
- No custom claims needed

**Current configuration:**
- `ADMIN_EMAIL=admin@stepsquad.com` (in `apps/api/.env`)
- Your user email: `admin@stepsquad.com`
- **Result**: User will automatically get ADMIN role when they authenticate!

**To verify:**
1. Sign in with `admin@stepsquad.com`
2. Check the `/me` endpoint - it should return `role: ADMIN`

---

## ✅ Verification Steps

### Method 1: Test Authentication

After setting custom claims (or using email-based assignment):

1. **Start Backend**:
   ```bash
   cd apps/api
   export GCP_ENABLED=true
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

2. **Sign In via Frontend**:
   ```bash
   cd apps/web
   pnpm dev
   ```
   - Open http://localhost:5174
   - Sign in with `admin@stepsquad.com`
   - Should redirect to home page

3. **Check User Role**:
   ```bash
   # Get Firebase ID token from frontend (check browser console or localStorage)
   # Then test /me endpoint
   curl -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" http://localhost:8080/me
   ```
   
   Should return:
   ```json
   {
     "uid": "12oy8e2D0NY45UPP4zCsP",
     "email": "admin@stepsquad.com",
     "role": "ADMIN"
   }
   ```

### Method 2: Verify in Code

You can verify custom claims were set by checking the user:

```python
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('/path/to/firebase-service-account.json')
firebase_admin.initialize_app(cred)

user = auth.get_user('12oy8e2D0NY45UPP4zCsP')
print(f"Email: {user.email}")
print(f"Custom Claims: {user.custom_claims}")
```

---

## 📝 Important Notes

### Custom Claims vs Email-Based Assignment

**Custom Claims (Recommended for Production):**
- ✅ More secure (claims are in the token)
- ✅ Can be updated without changing email
- ✅ Standard Firebase practice
- ❌ Requires Admin SDK to set
- ❌ User must sign out/in for changes to take effect

**Email-Based Assignment (Simpler for Development):**
- ✅ No setup needed
- ✅ Works immediately
- ✅ Good for development
- ❌ Less flexible
- ❌ Email changes require reconfiguration

### Token Refresh

**Important**: After setting custom claims, the user needs to:
1. Sign out from the application
2. Sign in again

This is because the ID token caches the claims. A new sign-in will include the updated claims.

---

## 🔍 Troubleshooting

### Error: "firebase-admin not installed"

```bash
cd apps/api
pip install firebase-admin
```

### Error: "GOOGLE_APPLICATION_CREDENTIALS not set"

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
```

### Error: "User not found"

- Verify the user exists in Firebase Console → Authentication → Users
- Check the email is correct
- The user was created: `admin@stepsquad.com` ✅

### Custom claims not appearing in token

- User must sign out and sign in again
- Tokens are cached - new token will have updated claims
- Check token in browser: `localStorage.getItem('firebaseToken')`

---

## ✅ Quick Summary

Since your user email (`admin@stepsquad.com`) matches the `ADMIN_EMAIL` configuration, you **don't need custom claims** - the user will automatically get ADMIN role when they authenticate!

**To test:**
1. Start backend with `GCP_ENABLED=true`
2. Start frontend
3. Sign in with `admin@stepsquad.com`
4. Check `/me` endpoint - should show `role: ADMIN`

**If you want to use custom claims instead** (recommended for production):
- Run the script: `python apps/api/scripts/set_admin_claim.py`
- User signs out and signs in again
- Token will now include the custom claim

---

**Status**: ✅ **Ready to Set Custom Claims** (or use email-based assignment)

