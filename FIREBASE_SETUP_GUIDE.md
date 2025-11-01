# Firebase Setup Guide - Step by Step

Complete guide to setting up Firebase Authentication for StepSquad production deployment.

---

## 📋 Prerequisites

1. Google Cloud Project (same as your GCP project)
2. Firebase project (can be same as GCP project or separate)
3. Access to Firebase Console
4. Access to Cloud Run service account

---

## 🚀 Step 1: Create/Configure Firebase Project

### Option A: Use Existing GCP Project

If your GCP project already has Firebase enabled:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your GCP project
3. Skip to Step 2

### Option B: Create New Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name (e.g., "StepSquad")
4. Select your Google Cloud project (or create new)
5. Disable Google Analytics (optional)
6. Click **"Create project"**
7. Wait for project creation (30-60 seconds)

---

## 🔐 Step 2: Enable Firebase Authentication

1. In Firebase Console, go to **Authentication** (left sidebar)
2. Click **"Get started"** (if first time)
3. Go to **"Sign-in method"** tab
4. Click on **"Email/Password"**
5. Toggle **"Enable"** to ON
6. (Optional) Toggle **"Email link (passwordless sign-in)"** if desired
7. Click **"Save"**

---

## 📱 Step 3: Register Web App

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Scroll to **"Your apps"** section
3. Click on **Web app icon** (`</>`) or **"Add app"** → **Web**
4. Enter app nickname (e.g., "StepSquad Web")
5. (Optional) Check **"Also set up Firebase Hosting"**
6. Click **"Register app"**
7. **Copy the Firebase configuration object** - you'll need these values:
   ```javascript
   {
     apiKey: "AIza...",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abcdef"
   }
   ```

---

## 🔑 Step 4: Configure Service Account (Backend)

The backend needs Firebase Admin SDK access. You can use the same service account as Cloud Run.

### For Cloud Run (Automatic - Recommended)

1. Cloud Run automatically uses the service account attached to the service
2. Ensure the service account has **Firebase Admin** role:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com" \
     --role="roles/firebase.admin"
   ```

### For Local Testing (Optional)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Go to **Project Settings** → **Service accounts**
3. Click **"Generate new private key"**
4. Save the JSON file securely (e.g., `firebase-service-account.json`)
5. **DO NOT commit this file to git!**
6. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
   ```

---

## ⚙️ Step 5: Configure Environment Variables

### Backend (apps/api/.env or Cloud Run)

```bash
# Required
GCP_ENABLED=true
COMP_TZ=Europe/Bucharest

# Optional
ADMIN_EMAIL=admin@stepsquad.com
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Local only
```

### Frontend (apps/web/.env.local or Cloud Run)

```bash
# Required
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration (from Step 3)
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

---

## 👤 Step 6: Set Up Admin User

### Option A: Using Custom Claims (Recommended)

1. Create admin user in Firebase:
   ```bash
   # Using Firebase Admin SDK (Python)
   from firebase_admin import auth
   
   user = auth.create_user(
       email='admin@stepsquad.com',
       password='secure-password-here',
       email_verified=True
   )
   
   # Set custom claim for ADMIN role
   auth.set_custom_user_claims(user.uid, {'role': 'ADMIN'})
   ```

2. Or use Firebase Console:
   - Go to **Authentication** → **Users**
   - Click **"Add user"**
   - Enter email and password
   - After creation, click on the user
   - Go to **"Custom claims"** tab
   - Add claim: `{"role": "ADMIN"}`

### Option B: Using Email-Based Role Assignment

1. Create admin user with email `admin@stepsquad.com` (or whatever `ADMIN_EMAIL` is set to)
2. Backend will automatically assign ADMIN role based on email

---

## ✅ Step 7: Verify Setup

### Run Setup Verification Script

```bash
cd apps/api
python scripts/check_firebase_setup.py
```

This will check:
- ✅ Firebase Admin SDK installed
- ✅ Environment variables configured
- ✅ Firebase initialization works
- ✅ Frontend configuration correct

### Test Authentication

1. **Start Backend** (with `GCP_ENABLED=true`):
   ```bash
   cd apps/api
   export GCP_ENABLED=true
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

2. **Start Frontend** (with Firebase config):
   ```bash
   cd apps/web
   # Ensure .env.local has VITE_USE_DEV_AUTH=false and Firebase config
   pnpm dev
   ```

3. **Test Login**:
   - Open http://localhost:5174
   - Click "Sign in"
   - Enter admin email and password
   - Should successfully authenticate

4. **Check Health Endpoint**:
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

---

## 🚀 Step 8: Deploy to Production

### Deploy Backend to Cloud Run

1. Ensure service account has Firebase Admin role (Step 4)
2. Set environment variables in Cloud Run:
   ```bash
   gcloud run services update stepsquad-api \
     --set-env-vars="GCP_ENABLED=true,COMP_TZ=Europe/Bucharest,ADMIN_EMAIL=admin@stepsquad.com"
   ```

### Deploy Frontend to Cloud Run

1. Build with production environment variables:
   ```bash
   cd apps/web
   
   # Create .env.production file
   cat > .env.production << EOF
   VITE_API_BASE_URL=https://your-api-url.run.app
   VITE_USE_DEV_AUTH=false
   VITE_ADMIN_EMAIL=admin@stepsquad.com
   VITE_FIREBASE_API_KEY=AIza...
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
   VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
   EOF
   
   # Build
   pnpm build
   
   # Deploy
   gcloud run deploy stepsquad-web --source .
   ```

---

## 🔍 Troubleshooting

### Backend Issues

**Error: "Firebase Admin SDK not initialized"**

- Check `GCP_ENABLED=true` is set
- Verify service account has Firebase Admin role
- Check Cloud Run service account is correct

**Error: "Invalid authentication token"**

- Verify Firebase project ID matches
- Check token hasn't expired (tokens expire after 1 hour)
- Ensure backend and frontend use same Firebase project

### Frontend Issues

**Error: "Firebase not configured"**

- Check all `VITE_FIREBASE_*` environment variables are set
- Verify `.env.local` file exists and is correct
- Restart dev server after changing environment variables

**Error: "Sign in failed"**

- Verify Email/Password authentication is enabled in Firebase Console
- Check user exists in Firebase Authentication
- Verify email is not already in use

### Authentication Flow Issues

**Error: "Authentication required"**

- Check frontend is sending `Authorization: Bearer <token>` header
- Verify token is not expired
- Check backend is in production mode (`GCP_ENABLED=true`)

---

## 🔒 Security Best Practices

1. **Never commit** `.env.local` or service account keys to git
2. **Use Secret Manager** in Cloud Run for sensitive values
3. **Rotate credentials** periodically
4. **Use custom claims** for role assignment (more secure than email-based)
5. **Enable email verification** for production (optional but recommended)
6. **Set password requirements** in Firebase Console (min length, etc.)
7. **Monitor authentication** via Cloud Logging

---

## 📊 Monitoring

### Check Authentication Status

```bash
# Check health endpoint
curl https://your-api-url.run.app/health

# Should show:
# {
#   "ok": true,
#   "firebase_initialized": true,
#   ...
# }
```

### View Firebase Authentication Logs

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Go to **Authentication** → **Users**
3. View active users and their roles

### Cloud Logging

```bash
# View authentication errors
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'Firebase'" --limit 50
```

---

## ✅ Checklist

Before deploying to production, verify:

- [ ] Firebase project created
- [ ] Email/Password authentication enabled
- [ ] Web app registered in Firebase
- [ ] Firebase configuration copied to frontend `.env.local`
- [ ] Backend service account has Firebase Admin role
- [ ] Admin user created with ADMIN role (custom claim or email)
- [ ] Environment variables configured (backend and frontend)
- [ ] Setup verification script passes
- [ ] Local authentication flow tested
- [ ] Health endpoint shows `firebase_initialized: true`
- [ ] Production environment variables set in Cloud Run
- [ ] Frontend built with production environment variables

---

## 📚 Additional Resources

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/reference/admin/python)
- [Cloud Run Environment Variables](https://cloud.google.com/run/docs/configuring/environment-variables)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)

---

**Last Updated**: November 1, 2025

