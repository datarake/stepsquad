# Firebase Authentication Setup Guide

This guide explains how to set up Firebase Authentication for StepSquad in production.

## Overview

StepSquad supports two authentication modes:
- **Development Mode**: Simple email-based auth (no password, local only)
- **Production Mode**: Firebase Authentication with email/password

## Backend Setup

### 1. Install Firebase Admin SDK

The Firebase Admin SDK is already included in `pyproject.toml`. Install it:

```bash
cd apps/api
source venv/bin/activate
pip install firebase-admin
```

### 2. Configure GCP Credentials

For Cloud Run / GCP environments, use Application Default Credentials:

```bash
# In Cloud Run, credentials are automatically available
export GCP_ENABLED=true
```

For local testing with Firebase:

```bash
# Download service account key from Firebase Console
# https://console.firebase.google.com/project/YOUR_PROJECT/settings/serviceaccounts/adminsdk

export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
export GCP_ENABLED=true
```

### 3. Environment Variables

```bash
# Required for production
export GCP_ENABLED=true
export COMP_TZ=Europe/Bucharest

# Optional: override admin email
export ADMIN_EMAIL=admin@stepsquad.com
```

## Frontend Setup

### 1. Get Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. Go to Project Settings → General
4. Scroll to "Your apps" section
5. Click on the Web app icon (`</>`) or create a new web app
6. Copy the Firebase configuration object

### 2. Configure Environment Variables

Create/update `.env.local` in `apps/web/`:

**For Development (Dev Mode):**
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_USE_DEV_AUTH=true
VITE_ADMIN_EMAIL=admin@stepsquad.com
```

**For Production (Firebase):**
```env
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration (from Firebase Console)
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 3. Enable Firebase Authentication

1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Enable **Email/Password** provider
3. (Optional) Enable email verification if desired

### 4. Set Up Custom Claims (Optional)

To assign ADMIN role via Firebase custom claims:

1. Go to Firebase Console → Authentication → Users
2. Click on a user → Custom claims
3. Add custom claim: `{ "role": "ADMIN" }`

Or use Firebase Admin SDK:

```python
from firebase_admin import auth

# Set custom claim for user
user = auth.get_user_by_email('admin@stepsquad.com')
auth.set_custom_user_claims(user.uid, {'role': 'ADMIN'})
```

## How It Works

### Backend Flow

1. Frontend sends `Authorization: Bearer <Firebase ID token>` header
2. Backend receives token and calls `verify_id_token()`
3. Firebase Admin SDK verifies the token
4. Backend extracts user info (uid, email) from token
5. Backend determines role:
   - From custom claim `role` if present
   - From email (admin@stepsquad.com = ADMIN, else MEMBER)
6. Backend creates/updates user in Firestore
7. Backend returns user info to frontend

### Frontend Flow

1. User enters email and password
2. Frontend calls `firebaseSignIn()` or `firebaseSignUp()`
3. Firebase returns ID token
4. Frontend stores token in localStorage
5. Frontend calls API with `Authorization: Bearer <token>` header
6. Frontend automatically refreshes token when expired

## Testing Firebase Authentication

### Local Testing

1. Set up Firebase project and get credentials
2. Configure `.env.local` with Firebase config
3. Set `VITE_USE_DEV_AUTH=false`
4. Start frontend: `npm run dev`
5. Start backend with `GCP_ENABLED=true` and service account key
6. Test login with Firebase credentials

### Production Testing

1. Deploy backend to Cloud Run with `GCP_ENABLED=true`
2. Deploy frontend with production Firebase config
3. Test authentication flow end-to-end

## Troubleshooting

### "Firebase not configured" Error

- Check that all `VITE_FIREBASE_*` environment variables are set
- Verify Firebase configuration in `.env.local`
- Restart dev server after changing environment variables

### "Invalid authentication token" Error

- Check that Firebase Admin SDK is initialized
- Verify service account credentials
- Check that `GCP_ENABLED=true` is set
- Verify token is not expired

### "Authentication verification failed" Error

- Check Firebase project ID matches
- Verify service account has Firebase Admin permissions
- Check network connectivity to Firebase

## Security Notes

- Never commit `.env.local` or service account keys to git
- Use environment variables in Cloud Run
- Service account keys should have minimal required permissions
- Firebase ID tokens expire after 1 hour (auto-refreshed by frontend)
- Custom claims take effect immediately after setting

## Next Steps

After setting up Firebase Authentication:

1. Test authentication flow
2. Set up custom claims for admin users
3. Configure email verification (optional)
4. Set up password reset flow (optional)
5. Add social authentication (Google, etc.) if needed
