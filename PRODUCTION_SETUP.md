# StepSquad - Production Setup Guide

## Overview

This guide covers deploying StepSquad to production on Google Cloud Platform (GCP) using Cloud Run for both backend API and frontend web app.

---

## Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP project
   - Billing enabled
   - Required APIs enabled

2. **Firebase Project**
   - Firebase project created
   - Authentication enabled
   - Firestore database initialized

3. **Tools Installed**
   - `gcloud` CLI
   - `docker` (for local testing)
   - `firebase-tools` (optional)

---

## Step 1: Firebase Project Setup

### 1.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project** or select existing project
3. Enable Google Analytics (optional)
4. Complete project creation

### 1.2 Enable Authentication

1. Go to **Authentication** → **Get Started**
2. Enable **Email/Password** provider
3. (Optional) Configure email templates

### 1.3 Initialize Firestore

1. Go to **Firestore Database** → **Create Database**
2. Start in **production mode**
3. Choose location (recommended: same as Cloud Run region)

### 1.4 Get Service Account Key (For Backend)

1. Go to **Project Settings** → **Service Accounts**
2. Click **Generate New Private Key**
3. Download JSON file (save securely)
4. This will be used as `GOOGLE_APPLICATION_CREDENTIALS`

### 1.5 Get Firebase Web Config (For Frontend)

1. Go to **Project Settings** → **General**
2. Scroll to **"Your apps"** → Click **Web** icon (`</>`)
3. Register app and copy configuration
4. You'll need:
   - `apiKey`
   - `authDomain`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

---

## Step 2: Enable GCP Services

### 2.1 Enable Required APIs

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com
```

### 2.2 Set Up Firestore Indexes

1. Go to **Firestore** → **Indexes**
2. Create composite index:
   - Collection: `competitions`
   - Fields: `status` (Ascending), `created_at` (Descending)

---

## Step 3: Backend API Deployment

### 3.1 Build and Push Container Image

```bash
cd apps/api

# Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/stepsquad-api:latest

# Or using Docker directly
docker build -t gcr.io/$PROJECT_ID/stepsquad-api:latest .
docker push gcr.io/$PROJECT_ID/stepsquad-api:latest
```

### 3.2 Deploy to Cloud Run

```bash
gcloud run deploy stepsquad-api \
  --image gcr.io/$PROJECT_ID/stepsquad-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCP_ENABLED=true,COMP_TZ=Europe/Bucharest" \
  --set-secrets="GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json" \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### 3.3 Environment Variables

Set via Cloud Run console or CLI:

```bash
gcloud run services update stepsquad-api \
  --update-env-vars="GCP_ENABLED=true,COMP_TZ=Europe/Bucharest,ADMIN_EMAIL=admin@stepsquad.com"
```

**Required:**
- `GCP_ENABLED=true`
- `COMP_TZ=Europe/Bucharest` (or your timezone)
- `ADMIN_EMAIL=admin@stepsquad.com` (optional, default)

**Optional:**
- `BQ_DATASET=stepsquad`
- `PUBSUB_TOPIC_INGEST=steps-ingest`
- `PUBSUB_SUB_INGEST=steps-sub`
- `GRACE_DAYS=2`

### 3.4 Get API URL

After deployment:
```bash
gcloud run services describe stepsquad-api --format 'value(status.url)'
```

Save this URL - it's your `VITE_API_BASE_URL` for frontend.

---

## Step 4: Frontend Web Deployment

### 4.1 Build Frontend

Create production `.env` file:
```env
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 4.2 Build Container Image

```bash
cd apps/web

# Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/stepsquad-web:latest

# Or using Docker directly
docker build -t gcr.io/$PROJECT_ID/stepsquad-web:latest .
docker push gcr.io/$PROJECT_ID/stepsquad-web:latest
```

**Note**: Environment variables must be set at build time for Vite.

### 4.3 Deploy to Cloud Run

```bash
gcloud run deploy stepsquad-web \
  --image gcr.io/$PROJECT_ID/stepsquad-web:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5
```

---

## Step 5: CI/CD Pipeline Setup

### 5.1 GitHub Actions Workflow

Create `.github/workflows/deploy.yml` (see below)

### 5.2 Set Up Secrets

In GitHub repository settings → Secrets:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (Service Account JSON)
- `FIREBASE_CONFIG` (Optional - for frontend)

---

## Step 6: Monitoring & Observability

### 6.1 Cloud Logging

Logs are automatically available in Cloud Console:
- Backend: Cloud Run → Logs
- Frontend: Cloud Run → Logs

### 6.2 Health Checks

- Backend: `GET https://your-api-url.run.app/health`
- Frontend: Server health check configured in Cloud Run

### 6.3 Alerting (Optional)

Set up Cloud Monitoring alerts:
- High error rate
- Slow response times
- High memory/CPU usage

---

## Step 7: Security Configuration

### 7.1 CORS Configuration

Backend already configured for production origins:
- Update `allow_origins` in `main.py` if needed

### 7.2 Service Account Permissions

Ensure Cloud Run service account has:
- `Cloud Datastore User`
- `Firebase Admin` (if using Firebase Admin SDK)

### 7.3 Secrets Management

Use Cloud Secret Manager for sensitive values:
```bash
# Create secret
echo -n "value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 8: Post-Deployment Verification

### 8.1 Test API

```bash
# Health check
curl https://your-api-url.run.app/health

# Test authentication
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-api-url.run.app/me
```

### 8.2 Test Frontend

1. Open frontend URL in browser
2. Test login with Firebase authentication
3. Test creating/viewing competitions
4. Verify all features work

---

## Environment Variables Summary

### Backend (Cloud Run)
```env
GCP_ENABLED=true
COMP_TZ=Europe/Bucharest
ADMIN_EMAIL=admin@stepsquad.com
BQ_DATASET=stepsquad
PUBSUB_TOPIC_INGEST=steps-ingest
PUBSUB_SUB_INGEST=steps-sub
GRACE_DAYS=2
```

### Frontend (Build-time)
```env
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

---

## Troubleshooting

### API Won't Start
- Check service account permissions
- Verify Firestore is initialized
- Check Cloud Run logs

### Frontend Can't Connect to API
- Verify `VITE_API_BASE_URL` is correct
- Check CORS configuration
- Verify API is publicly accessible

### Authentication Fails
- Verify Firebase configuration
- Check service account key
- Verify token is being sent correctly

---

**Status**: ✅ **Production Setup Guide Complete**
