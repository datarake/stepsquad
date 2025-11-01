# Firebase Configuration - Next Steps

**Date**: November 1, 2025  
**Status**: ✅ **Environment Variables Configured**

---

## ✅ What Was Done

1. **Frontend Environment Variables** ✅
   - Updated `apps/web/.env.local` with Firebase configuration
   - Set `VITE_USE_DEV_AUTH=false` to enable Firebase authentication
   - Configured all Firebase variables from your Firebase project

2. **Backend Environment Variables** ✅
   - Created `apps/api/.env` with Firebase configuration
   - Set `GCP_ENABLED=true` to enable Firebase authentication
   - Configured timezone and admin email

---

## 🔧 Next Steps to Complete Firebase Setup

### Step 1: Enable Firebase Authentication ✅

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **stepsquad-46d14**
3. Go to **Authentication** → **Sign-in method**
4. Enable **Email/Password** provider:
   - Click on **"Email/Password"**
   - Toggle **"Enable"** to ON
   - Click **"Save"**

### Step 2: Set Up Service Account (For Backend) ⚠️

The backend needs Firebase Admin SDK access. You have two options:

**📖 For detailed step-by-step instructions with troubleshooting, see [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md)**

#### Option A: Use Cloud Run Service Account (Recommended for Production)

1. Find your Cloud Run service account (see detailed guide for how to find it)
2. Grant Firebase Admin role:
   ```bash
   # Replace SERVICE_ACCOUNT_EMAIL with your actual service account email
   gcloud projects add-iam-policy-binding stepsquad-46d14 \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/firebase.admin"
   ```
3. Verify the role was granted (see detailed guide)

**See [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md) for:**
- How to find your Cloud Run service account email
- Verification steps
- Troubleshooting common issues

#### Option B: Download Service Account Key (For Local Testing)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **stepsquad-46d14**
3. Go to **Project Settings** → **Service accounts** tab
4. Click **"Generate new private key"** (choose Python)
5. Save the JSON file securely (see detailed guide for recommended location)
6. **DO NOT commit this file to git!**
7. Update `apps/api/.env`:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
   ```
8. Add to `.gitignore` to prevent committing it

**See [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md) for:**
- Recommended file locations
- Security best practices
- Verification steps
- Complete troubleshooting guide

### Step 3: Create Admin User ⚠️

You need to create an admin user in Firebase. Choose one of these methods:

#### Method A: Using Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Go to **Authentication** → **Users**
3. Click **"Add user"**
4. Enter email: `admin@stepsquad.com` (or your admin email)
5. Enter password (choose a strong password)
6. Click **"Add user"**
7. After creation, you need to set custom claims programmatically
   - **Custom claims cannot be set via Firebase Console UI**
   - See [SET_CUSTOM_CLAIMS.md](SET_CUSTOM_CLAIMS.md) for instructions
   - Or use email-based assignment (already configured - see below)
   
**Note**: Since `admin@stepsquad.com` matches your `ADMIN_EMAIL` configuration, 
the user will automatically get ADMIN role when they authenticate. Custom claims 
are optional but recommended for production. See [SET_CUSTOM_CLAIMS.md](SET_CUSTOM_CLAIMS.md) 
for details.

#### Method B: Using Firebase Admin SDK (Script)

Create a script to set up the admin user:

```python
# setup_admin.py
import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)

# Create admin user
email = "admin@stepsquad.com"
password = "your-secure-password-here"

try:
    user = auth.create_user(
        email=email,
        password=password,
        email_verified=True
    )
    print(f"✅ User created: {user.uid}")
    
    # Set custom claim for ADMIN role
    auth.set_custom_user_claims(user.uid, {'role': 'ADMIN'})
    print(f"✅ Admin role assigned to {email}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
cd apps/api
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
python setup_admin.py
```

### Step 4: Verify Setup ✅

Run the setup verification script:

```bash
cd apps/api
python scripts/check_firebase_setup.py
```

This should show:
- ✅ GCP_ENABLED=true
- ✅ firebase-admin package installed
- ✅ Firebase Admin SDK initialized successfully
- ✅ All Firebase configuration variables found

### Step 5: Test Authentication Flow ✅

#### Test Backend Health

```bash
# Start backend
cd apps/api
export GCP_ENABLED=true
# If using service account key:
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
uvicorn main:app --host 0.0.0.0 --port 8080
```

In another terminal:
```bash
curl http://localhost:8080/health
```

Should return:
```json
{
  "ok": true,
  "time": "2025-11-01T...",
  "tz": "Europe/Bucharest",
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

#### Test Frontend Login

```bash
# Start frontend
cd apps/web
pnpm dev
```

1. Open http://localhost:5174
2. Click **"Sign in"**
3. Enter your admin email and password
4. Should successfully authenticate and redirect to home page

---

## 🔍 Troubleshooting

### Backend Issues

**Error: "Firebase Admin SDK not initialized"**
- Check `GCP_ENABLED=true` is set
- Verify service account key path is correct
- Ensure service account has Firebase Admin role

**Error: "Invalid authentication token"**
- Verify Firebase project ID matches (`stepsquad-46d14`)
- Check token is not expired
- Ensure Email/Password authentication is enabled

### Frontend Issues

**Error: "Firebase not configured"**
- Check all `VITE_FIREBASE_*` variables are set
- Verify `.env.local` file exists
- Restart dev server after changing environment variables

**Error: "Sign in failed"**
- Verify Email/Password authentication is enabled in Firebase Console
- Check user exists in Firebase Authentication
- Verify email/password are correct

---

## ✅ Checklist

Before deploying to production, verify:

- [ ] Email/Password authentication enabled in Firebase Console
- [ ] Service account has Firebase Admin role (for Cloud Run)
- [ ] Admin user created in Firebase Authentication
- [ ] Custom claim `role: ADMIN` set for admin user
- [ ] Backend health check shows `firebase_initialized: true`
- [ ] Frontend can successfully authenticate
- [ ] Admin user can access admin features
- [ ] Regular users can access member features

---

## 🚀 Production Deployment

### Backend (Cloud Run)

Set environment variables in Cloud Run:
```bash
gcloud run services update stepsquad-api \
  --set-env-vars="GCP_ENABLED=true,COMP_TZ=Europe/Bucharest,ADMIN_EMAIL=admin@stepsquad.com"
```

Ensure Cloud Run service account has Firebase Admin role.

### Frontend (Cloud Run)

Build with production environment variables:
```bash
cd apps/web

# Create .env.production file
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com
VITE_FIREBASE_API_KEY=AIzaSyBAPgF7xzHOqKgGG8HkWgArtM4Luc_au1M
VITE_FIREBASE_AUTH_DOMAIN=stepsquad-46d14.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=stepsquad-46d14
VITE_FIREBASE_STORAGE_BUCKET=stepsquad-46d14.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=451432804996
VITE_FIREBASE_APP_ID=1:451432804996:web:72718bbe41e597a69008d1
VITE_FIREBASE_MEASUREMENT_ID=G-RDWR6NK1EN
EOF

# Build
pnpm build

# Deploy
gcloud run deploy stepsquad-web --source .
```

---

## 📚 Additional Resources

- [Firebase Setup Guide](FIREBASE_SETUP_GUIDE.md) - Complete setup guide
- [Monitoring Setup](MONITORING_SETUP.md) - Monitoring configuration
- [Production Environment](PRODUCTION_ENV.md) - Production configuration

---

**Status**: ✅ **Environment Variables Configured** - Ready for Firebase Authentication Setup

