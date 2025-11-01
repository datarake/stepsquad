# Service Account Setup - Detailed Guide

**Date**: November 1, 2025  
**Project**: stepsquad-46d14

Complete step-by-step guide for setting up service accounts for Firebase Authentication.

---

## 📋 Overview

The backend needs Firebase Admin SDK access to verify Firebase ID tokens. You can set this up in two ways:

1. **For Cloud Run (Production)** - Grant Firebase Admin role to the existing Cloud Run service account
2. **For Local Testing** - Download a service account key JSON file

---

## 🚀 Option A: Cloud Run Service Account Setup (Production)

This is the recommended approach for production deployments on Cloud Run.

### Step 1: Find Your Cloud Run Service Account

#### Method 1: Check Existing Cloud Run Service

```bash
# Get your Cloud Run service details
gcloud run services describe stepsquad-api \
  --region=us-central1 \
  --format="value(spec.template.spec.serviceAccountName)"
```

If this returns a service account email (e.g., `stepsquad-api@stepsquad-46d14.iam.gserviceaccount.com`), use that.

#### Method 2: Check Default Compute Service Account

If no custom service account is set, Cloud Run uses the default Compute Engine service account:

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe stepsquad-46d14 --format="value(projectNumber)")

# Default Compute Engine service account
echo "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
```

#### Method 3: Check in Cloud Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service (e.g., `stepsquad-api`)
3. Go to **"YAML"** tab
4. Look for `spec.template.spec.serviceAccountName`
5. If empty, it uses the default Compute Engine service account

### Step 2: Grant Firebase Admin Role

Once you have the service account email, grant it the Firebase Admin role:

```bash
# Replace SERVICE_ACCOUNT_EMAIL with your actual service account email
SERVICE_ACCOUNT_EMAIL="YOUR_SERVICE_ACCOUNT@stepsquad-46d14.iam.gserviceaccount.com"

# Grant Firebase Admin role
gcloud projects add-iam-policy-binding stepsquad-46d14 \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/firebase.admin"
```

**Example Commands:**

If using default Compute Engine service account:
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe stepsquad-46d14 --format="value(projectNumber)")

# Grant Firebase Admin role to default service account
gcloud projects add-iam-policy-binding stepsquad-46d14 \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/firebase.admin"
```

If using a custom service account:
```bash
gcloud projects add-iam-policy-binding stepsquad-46d14 \
  --member="serviceAccount:stepsquad-api@stepsquad-46d14.iam.gserviceaccount.com" \
  --role="roles/firebase.admin"
```

### Step 3: Verify the Role Was Granted

```bash
# List IAM policies for the project
gcloud projects get-iam-policy stepsquad-46d14 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/firebase.admin" \
  --format="table(bindings.role,bindings.members)"
```

You should see your service account in the list with `roles/firebase.admin` role.

### Step 4: Update Cloud Run Service (if needed)

If you want to use a specific service account, update your Cloud Run service:

```bash
# Update Cloud Run service to use specific service account
gcloud run services update stepsquad-api \
  --service-account=SERVICE_ACCOUNT_EMAIL \
  --region=us-central1
```

### Step 5: Verify in Cloud Console

1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
2. Select project: **stepsquad-46d14**
3. Find your service account in the list
4. Check that it has the **Firebase Admin** role

---

## 💻 Option B: Local Testing Service Account Key (Development)

This approach is for local development and testing.

### Step 1: Go to Firebase Console

1. Open [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **stepsquad-46d14**
3. Click on the **gear icon** (⚙️) → **Project settings**
4. Go to the **"Service accounts"** tab

### Step 2: Generate New Private Key

1. In the **"Service accounts"** tab, you'll see options for:
   - **Node.js**: For Node.js applications
   - **Python**: For Python applications (we need this one)
2. Click **"Generate new private key"** button
3. A dialog will appear warning you about keeping the key secure
4. Click **"Generate key"**
5. A JSON file will be downloaded automatically (e.g., `stepsquad-46d14-firebase-adminsdk-xxxxx.json`)

**⚠️ Security Warning:**
- **DO NOT** commit this file to git
- Keep it secure and private
- Add it to `.gitignore` if not already there

### Step 3: Save the Key Securely

1. Move the downloaded JSON file to a secure location:
   ```bash
   # Create a secure directory (outside of your project)
   mkdir -p ~/.config/stepsquad
   
   # Move the downloaded file there
   mv ~/Downloads/stepsquad-46d14-firebase-adminsdk-*.json ~/.config/stepsquad/firebase-service-account.json
   ```

2. Or keep it in your project directory (but ensure it's in `.gitignore`):
   ```bash
   # Move to project directory
   mv ~/Downloads/stepsquad-46d14-firebase-adminsdk-*.json apps/api/firebase-service-account.json
   ```

### Step 4: Update Backend Environment File

Edit `apps/api/.env` and add the path to the service account key:

```bash
# apps/api/.env
GCP_ENABLED=true
COMP_TZ=Europe/Bucharest
ADMIN_EMAIL=admin@stepsquad.com

# Service Account Credentials (for local testing)
GOOGLE_APPLICATION_CREDENTIALS=/Users/your-username/.config/stepsquad/firebase-service-account.json

# Or if in project directory:
# GOOGLE_APPLICATION_CREDENTIALS=/Users/your-username/Development/others/stepsquad/apps/api/firebase-service-account.json
```

### Step 5: Verify the Service Account Key Works

Test that the service account key is correctly configured:

```bash
cd apps/api

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json

# Test Firebase Admin SDK initialization
python3 -c "
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/firebase-service-account.json'
from firebase_auth import init_firebase
app = init_firebase()
if app:
    print('✅ Firebase Admin SDK initialized successfully')
else:
    print('❌ Firebase Admin SDK initialization failed')
"
```

### Step 6: Add to .gitignore (Important!)

Ensure the service account key is not committed to git:

```bash
# Check if already in .gitignore
cat apps/api/.gitignore | grep firebase-service-account.json || echo "firebase-service-account.json" >> apps/api/.gitignore

# Also add to root .gitignore if it exists
cat .gitignore | grep firebase-service-account.json || echo "**/firebase-service-account.json" >> .gitignore 2>/dev/null || echo "firebase-service-account.json" >> .gitignore
```

---

## ✅ Verification Steps

### Test Backend Health Endpoint

```bash
# Start backend
cd apps/api
export GCP_ENABLED=true

# If using service account key locally:
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json

# Start server
uvicorn main:app --host 0.0.0.0 --port 8080
```

In another terminal:
```bash
# Test health endpoint
curl http://localhost:8080/health
```

Expected response:
```json
{
  "ok": true,
  "time": "2025-11-01T...",
  "tz": "Europe/Bucharest",
  "gcp_enabled": true,
  "firebase_initialized": true
}
```

If `firebase_initialized: false`, check:
- Service account has Firebase Admin role
- `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Service account key file exists and is readable

### Test Authentication

```bash
# Test authentication endpoint (should require Firebase token)
curl http://localhost:8080/me
```

Expected response:
```json
{
  "detail": "Authentication required"
}
```

This confirms Firebase authentication is enabled.

---

## 🔍 Troubleshooting

### Error: "Firebase Admin SDK not initialized"

**Possible Causes:**
1. Service account key path is incorrect
2. Service account key file doesn't exist
3. Service account doesn't have Firebase Admin role
4. `GCP_ENABLED` is not set to `true`

**Solution:**
```bash
# Verify environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $GCP_ENABLED

# Check if file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test service account key
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud projects get-iam-policy stepsquad-46d14 --flatten="bindings[].members" --filter="bindings.role:roles/firebase.admin"
```

### Error: "Permission denied" or "Access denied"

**Possible Causes:**
1. Service account doesn't have Firebase Admin role
2. Service account key is from wrong project
3. Service account is disabled

**Solution:**
```bash
# Verify service account has Firebase Admin role
gcloud projects get-iam-policy stepsquad-46d14 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/firebase.admin" \
  --format="table(bindings.members)"

# Re-grant the role
gcloud projects add-iam-policy-binding stepsquad-46d14 \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@stepsquad-46d14.iam.gserviceaccount.com" \
  --role="roles/firebase.admin"
```

### Error: "Invalid service account key"

**Possible Causes:**
1. Service account key file is corrupted
2. Service account key is from wrong project
3. Service account key has been revoked

**Solution:**
1. Go back to Firebase Console
2. Generate a new private key
3. Update `GOOGLE_APPLICATION_CREDENTIALS` path

---

## 📋 Checklist

### For Cloud Run (Production)

- [ ] Found Cloud Run service account email
- [ ] Granted Firebase Admin role to service account
- [ ] Verified role appears in IAM policies
- [ ] Updated Cloud Run service (if using custom service account)
- [ ] Tested backend health endpoint shows `firebase_initialized: true`

### For Local Testing

- [ ] Downloaded service account key from Firebase Console
- [ ] Saved key to secure location
- [ ] Updated `apps/api/.env` with `GOOGLE_APPLICATION_CREDENTIALS` path
- [ ] Added service account key to `.gitignore`
- [ ] Verified service account key works
- [ ] Tested backend health endpoint shows `firebase_initialized: true`

---

## 🔒 Security Best Practices

1. **Never commit service account keys to git**
   - Always add to `.gitignore`
   - Use environment variables
   - Use Secret Manager in production

2. **Use least privilege principle**
   - Only grant Firebase Admin role (not Owner)
   - Use separate service accounts for different services

3. **Rotate keys periodically**
   - Regenerate service account keys every 90 days
   - Revoke old keys after rotation

4. **Monitor service account usage**
   - Check Cloud Logging for service account activity
   - Set up alerts for unusual activity

5. **For Production:**
   - Use Cloud Run service accounts (not downloaded keys)
   - Use Secret Manager for sensitive values
   - Enable audit logging

---

## 📚 Additional Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Cloud Run Service Accounts](https://cloud.google.com/run/docs/configuring/service-accounts)
- [IAM Roles for Firebase](https://cloud.google.com/iam/docs/understanding-roles#firebase)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/service-accounts)

---

**Status**: ✅ **Ready for Service Account Setup**

