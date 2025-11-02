# Firebase CI/CD Configuration Guide

Complete guide for setting up Firebase environment variables in GitHub Actions for production deployment.

---

## Problem

When deploying to production, you get:
```
Firebase not configured. Please set Firebase environment variables.
```

**Cause**: Firebase environment variables are not set in the CI/CD workflow during frontend build.

---

## Solution

Add Firebase environment variables as GitHub Secrets and update the CI/CD workflow to use them.

---

## Step 1: Add Firebase Secrets to GitHub

### Navigate to GitHub Repository Settings

1. Go to your GitHub repository: `https://github.com/datarake/stepsquad`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add Each Firebase Secret

Add the following secrets one by one:

1. **FIREBASE_API_KEY**
   - Value: `AIzaSyBAPgF7xzHOqKgGG8HkWgArtM4Luc_au1M`
   - Click **Add secret**

2. **FIREBASE_AUTH_DOMAIN**
   - Value: `stepsquad-46d14.firebaseapp.com`
   - Click **Add secret**

3. **FIREBASE_PROJECT_ID**
   - Value: `stepsquad-46d14`
   - Click **Add secret**

4. **FIREBASE_STORAGE_BUCKET**
   - Value: `stepsquad-46d14.firebasestorage.app`
   - Click **Add secret**

5. **FIREBASE_MESSAGING_SENDER_ID**
   - Value: `451432804996`
   - Click **Add secret**

6. **FIREBASE_APP_ID**
   - Value: `1:451432804996:web:72718bbe41e597a69008d1`
   - Click **Add secret**

7. **FIREBASE_MEASUREMENT_ID**
   - Value: `G-RDWR6NK1EN`
   - Click **Add secret**

---

## Step 2: Verify CI/CD Workflow

The CI/CD workflow has already been updated to:
- Read Firebase secrets from GitHub
- Add them to `.env.production` during build
- Include them in the Docker image build

**File**: `.github/workflows/deploy.yml`

The workflow now includes:
```yaml
env:
  VITE_FIREBASE_API_KEY: ${{ secrets.FIREBASE_API_KEY }}
  VITE_FIREBASE_AUTH_DOMAIN: ${{ secrets.FIREBASE_AUTH_DOMAIN }}
  # ... other Firebase env vars
```

---

## Step 3: Test the Deployment

After adding the secrets:

1. **Push a change** to trigger CI/CD
2. **Monitor the workflow** in GitHub Actions
3. **Check the build logs** to verify Firebase env vars are set
4. **Test production login** at `https://www.stepsquad.club/login`

---

## Complete List of Firebase Secrets

Add these to GitHub Secrets:

| Secret Name | Value |
|------------|-------|
| `FIREBASE_API_KEY` | `AIzaSyBAPgF7xzHOqKgGG8HkWgArtM4Luc_au1M` |
| `FIREBASE_AUTH_DOMAIN` | `stepsquad-46d14.firebaseapp.com` |
| `FIREBASE_PROJECT_ID` | `stepsquad-46d14` |
| `FIREBASE_STORAGE_BUCKET` | `stepsquad-46d14.firebasestorage.app` |
| `FIREBASE_MESSAGING_SENDER_ID` | `451432804996` |
| `FIREBASE_APP_ID` | `1:451432804996:web:72718bbe41e597a69008d1` |
| `FIREBASE_MEASUREMENT_ID` | `G-RDWR6NK1EN` |

---

## Quick Checklist

- [ ] Added `FIREBASE_API_KEY` to GitHub Secrets
- [ ] Added `FIREBASE_AUTH_DOMAIN` to GitHub Secrets
- [ ] Added `FIREBASE_PROJECT_ID` to GitHub Secrets
- [ ] Added `FIREBASE_STORAGE_BUCKET` to GitHub Secrets
- [ ] Added `FIREBASE_MESSAGING_SENDER_ID` to GitHub Secrets
- [ ] Added `FIREBASE_APP_ID` to GitHub Secrets
- [ ] Added `FIREBASE_MEASUREMENT_ID` to GitHub Secrets
- [ ] CI/CD workflow updated (already done)
- [ ] Pushed changes to trigger deployment
- [ ] Tested production login

---

## Verification

After adding secrets and deploying:

1. **Check build logs** in GitHub Actions:
   - Should see `.env.production` being created
   - Should see Firebase env vars being added

2. **Test production login**:
   - Go to `https://www.stepsquad.club/login`
   - Enter email: `burdibox@gmail.com`
   - Enter password: (your Firebase password)
   - Should login successfully without "Firebase not configured" error

3. **Check browser console**:
   - Open DevTools → Console
   - Should NOT see "Firebase not configured" warning
   - Should see Firebase initialized successfully

---

## Troubleshooting

### Still Getting "Firebase not configured" Error

**Check:**
1. ✅ All 7 Firebase secrets added to GitHub
2. ✅ Secrets have correct names (exactly as listed above)
3. ✅ Secrets have correct values (no extra spaces)
4. ✅ CI/CD workflow has been updated (already done)
5. ✅ New deployment triggered after adding secrets
6. ✅ Check build logs for Firebase env vars

**Verify secrets in GitHub:**
- Go to **Settings** → **Secrets and variables** → **Actions**
- Should see all 7 Firebase secrets listed

### Build Fails

**Check:**
1. ✅ All secrets are set (not empty)
2. ✅ Secret names match exactly (case-sensitive)
3. ✅ Check CI/CD workflow logs for errors
4. ✅ Verify `.env.production` is created correctly

---

## How It Works

### Build Process

1. **CI/CD triggers** on push to `main`
2. **GitHub Actions** reads Firebase secrets
3. **Workflow creates** `.env.production` file with:
   - `VITE_API_BASE_URL=https://api.stepsquad.club`
   - `VITE_USE_DEV_AUTH=false`
   - `VITE_FIREBASE_API_KEY=...`
   - `VITE_FIREBASE_AUTH_DOMAIN=...`
   - `VITE_FIREBASE_PROJECT_ID=...`
   - `VITE_FIREBASE_STORAGE_BUCKET=...`
   - `VITE_FIREBASE_MESSAGING_SENDER_ID=...`
   - `VITE_FIREBASE_APP_ID=...`
   - `VITE_FIREBASE_MEASUREMENT_ID=...`
4. **Vite builds** frontend with these env vars baked in
5. **Docker image** contains the built frontend with Firebase config
6. **Cloud Run** serves the frontend with Firebase configured

### Frontend Code

The frontend code (`apps/web/src/firebase.ts`) checks:
```typescript
const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
if (!apiKey) {
  console.warn('Firebase not configured - missing VITE_FIREBASE_API_KEY');
  return null;
}
```

If `VITE_FIREBASE_API_KEY` is not set, Firebase initialization returns `null`, causing the error.

---

## Security Notes

⚠️ **Important**: These Firebase config values are **public** and safe to include in frontend builds:

- ✅ **Firebase API keys** are public and safe to expose in client-side code
- ✅ They're used to identify your Firebase project
- ✅ They don't grant access without proper authentication
- ✅ They're meant to be included in frontend builds

**However:**
- ❌ **Never** commit `.env.production` files with secrets to Git
- ❌ **Never** expose Firebase Admin SDK private keys
- ✅ Use GitHub Secrets for CI/CD (already done)

---

## Next Steps After Adding Secrets

1. ✅ **Add all 7 Firebase secrets** to GitHub
2. ✅ **Push a commit** to trigger CI/CD (or manually trigger)
3. ✅ **Wait for deployment** to complete
4. ✅ **Test production login** at `https://www.stepsquad.club/login`
5. ✅ **Verify** Firebase authentication works

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Configuration

