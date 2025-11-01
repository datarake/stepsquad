# Deployment Methods - StepSquad

**Date**: November 1, 2025

---

## 📊 Deployment Overview

StepSquad uses two deployment methods:

1. **CI/CD (GitHub Actions)** - Automated deployments on push to `main`
2. **Manual (Makefile)** - Manual deployments using `make` commands

---

## 🚀 CI/CD Deployments (GitHub Actions)

### Location
- **Workflow**: `.github/workflows/deploy.yml`
- **Trigger**: Push to `main` branch or manual workflow dispatch
- **Deployed by**: `github-actions@476318-n0.iam.gserviceaccount.com`
- **Region**: `us-central1`

### Services Deployed
- ✅ **stepsquad-api** - Backend API (deployed "Just now")
- ✅ **stepsquad-web** - Frontend web app (deployed "3 hours ago")

### What It Does

1. **Authenticates to Google Cloud** using service account
2. **Builds Docker images** using Cloud Build
3. **Deploys to Cloud Run** with:
   - Region: `us-central1`
   - Environment variables set
   - Port: 8080
   - Memory/CPU configured
   - Public access enabled

### Environment Variables Set

**Backend API:**
- `GCP_ENABLED=true`
- `COMP_TZ=Europe/Bucharest`

**Frontend Web:**
- `VITE_API_BASE_URL` (fetched from deployed API URL)
- `VITE_USE_DEV_AUTH=false`

### Recent Deployments
- `stepsquad-api`: "Just now" ✅
- `stepsquad-web`: "3 hours ago" ✅

---

## 🛠️ Manual Deployments (Makefile)

### Location
- **Makefile**: `Makefile`
- **Scripts**: `deploy/*.sh`
- **Deployed by**: `bogdan.burdale`
- **Region**: `europe-west1` (default, can be overridden)

### Services Deployed
- ✅ **stepsquad-api** - Backend API
- ✅ **stepsquad-web** - Frontend web app
- ✅ **stepsquad-workers** - Background workers
- ✅ **stepsquad-agents** - AI agents

### Commands

```bash
# Deploy API
make deploy_api

# Deploy Web
make deploy_web

# Deploy Workers
make deploy_workers

# Deploy Agents
make deploy_agents
```

These commands call scripts in `deploy/` directory:
- `deploy/deploy_api.sh`
- `deploy/deploy_web.sh`
- `deploy/deploy_workers.sh`
- `deploy/deploy_agents.sh`

### Older Deployments
- `stepsquad-agents`: "6 days ago"
- `stepsquad-api`: "5 days ago" (older deployment)
- `stepsquad-web`: "5 days ago" (older deployment)
- `stepsquad-workers`: "5 days ago"

---

## 🔍 Differences

### CI/CD (GitHub Actions)

**Pros:**
- ✅ Automated on every push to `main`
- ✅ Consistent deployment process
- ✅ No manual steps required
- ✅ Deployment history tracked in GitHub Actions

**Cons:**
- ⚠️ Only deploys `api` and `web` services
- ⚠️ Does not deploy `workers` or `agents`

**Region:** `us-central1`

---

### Manual (Makefile)

**Pros:**
- ✅ Deploys all services (`api`, `web`, `workers`, `agents`)
- ✅ Full control over deployment process
- ✅ Can deploy to different regions
- ✅ Can test deployment changes before pushing

**Cons:**
- ⚠️ Requires manual execution
- ⚠️ Easy to forget to deploy
- ⚠️ No automatic deployment on code changes

**Region:** `europe-west1` (default)

---

## 📋 Current Deployment Status

Based on Cloud Run console:

### Recent (CI/CD) ✅
- **stepsquad-api**: Deployed "Just now" by `github-actions@476318-n0.iam.gserviceaccount.com`
- **stepsquad-web**: Deployed "3 hours ago" by `github-actions@476318-n0.iam.gserviceaccount.com`

### Older (Manual) 📅
- **stepsquad-api**: Deployed "5 days ago" by `bogdan.burdale`
- **stepsquad-web**: Deployed "5 days ago" by `bogdan.burdale`
- **stepsquad-workers**: Deployed "5 days ago" by `bogdan.burdale`
- **stepsquad-agents**: Deployed "6 days ago" by `bogdan.burdale`

---

## 🔍 Key Differences

### Regions
- **CI/CD**: Deploys to `us-central1`
- **Manual**: Deploys to `europe-west1` (default)

### Image Registries
- **CI/CD**: Uses `gcr.io/PROJECT_ID/service:sha` (Google Container Registry)
- **Manual**: Uses `REGION-docker.pkg.dev/PROJECT/REPO/image:latest` (Artifact Registry)

### Services Deployed
- **CI/CD**: Only `api` and `web`
- **Manual**: All services (`api`, `web`, `workers`, `agents`)

### Environment Variables
- **CI/CD API**: `GCP_ENABLED=true,COMP_TZ=Europe/Bucharest`
- **Manual API**: `GCP_ENABLED=true,GOOGLE_CLOUD_PROJECT=...,BQ_DATASET=...,PUBSUB_TOPIC_INGEST=...,COMP_TZ=...,GRACE_DAYS=2`

---

## 🔧 Recommendations

### Option 1: Use CI/CD for All Services (Recommended)

Update `.github/workflows/deploy.yml` to also deploy `workers` and `agents`:

```yaml
deploy-workers:
  name: Deploy Workers
  runs-on: ubuntu-latest
  needs: deploy-api
  # ... similar to deploy-api

deploy-agents:
  name: Deploy Agents
  runs-on: ubuntu-latest
  needs: deploy-api
  # ... similar to deploy-api
```

**Benefits:**
- All services automatically deployed on push
- Consistent deployment process
- Less manual work

### Option 2: Keep Current Setup

- Use CI/CD for `api` and `web` (frequent deployments)
- Use manual deployment for `workers` and `agents` (less frequent)

### Option 3: Hybrid Approach

- CI/CD deploys `api` and `web` automatically
- Manual deployment for `workers` and `agents` when needed
- Use different regions if needed

---

## 🎯 Current Setup Analysis

**What's Working:**
- ✅ CI/CD is automatically deploying `api` and `web` on every push
- ✅ Recent deployments are from CI/CD (most up-to-date)
- ✅ Manual deployment scripts exist for all services

**What Could Be Improved:**
- ⚠️ `workers` and `agents` are not in CI/CD (only manual)
- ⚠️ Different regions: CI/CD uses `us-central1`, Makefile defaults to `europe-west1`
- ⚠️ Older manual deployments may be outdated

---

## ✅ Unified Deployment (Current Setup)

**Both CI/CD and manual scripts now deploy to the same services:**

### Standardized Configuration

- **Region**: `us-central1` (both methods)
- **Registry**: Artifact Registry (`REGION-docker.pkg.dev/PROJECT/REPO/image`)
- **Services**: All 4 services (`api`, `web`, `workers`, `agents`)
- **Environment Variables**: Consistent across both methods

### How It Works

1. **CI/CD (Automatic)**: On every push to `main`, all 4 services are deployed automatically
2. **Manual (Redundant)**: Can be used for ad-hoc deployments, testing, or when CI/CD is not available

### Benefits

- ✅ **Redundancy**: Both methods available
- ✅ **No Duplicates**: Same services, same region
- ✅ **Consistency**: Same configuration and environment variables
- ✅ **Flexibility**: Use either method as needed

## 📝 Migration Notes

If you have old deployments in `europe-west1`:
1. They will continue to run until manually deleted
2. New deployments will all go to `us-central1`
3. To clean up old deployments:
   ```bash
   gcloud run services delete stepsquad-api --region europe-west1
   gcloud run services delete stepsquad-web --region europe-west1
   gcloud run services delete stepsquad-workers --region europe-west1
   gcloud run services delete stepsquad-agents --region europe-west1
   ```

---

## 📚 Files Reference

- **CI/CD Workflow**: `.github/workflows/deploy.yml`
- **Makefile**: `Makefile`
- **Deploy Scripts**: `deploy/*.sh`
- **Deploy Docs**: `deploy/README.md`

---

**Status**: ✅ **CI/CD Working** - Automatic deployments for `api` and `web`

