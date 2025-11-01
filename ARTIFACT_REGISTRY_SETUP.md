# Artifact Registry Setup

## Quick Fix for CI/CD Error

If you see the error:
```
ERROR: Repository "stepsquad" not found
```

This means the Artifact Registry repository doesn't exist in the `us-central1` region.

**Note**: The CI/CD service account may not have permissions to create repositories automatically. If the automated creation fails, you need to create it manually.

## Prerequisites

1. **Enable Artifact Registry API** (requires `Service Usage Admin` or project owner permissions):
   ```bash
   gcloud services enable artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
   ```

2. **Create the repository** (requires `Artifact Registry Admin` or project owner permissions):

### Option 1: Create via gcloud CLI

```bash
gcloud artifacts repositories create stepsquad \
  --repository-format=docker \
  --location=us-central1 \
  --project=YOUR_PROJECT_ID
```

### Option 2: Create via Console

1. Go to [Artifact Registry Console](https://console.cloud.google.com/artifacts)
2. Select your project
3. Click **"+ Create repository"**
4. Fill in:
   - **Name**: `stepsquad`
   - **Format**: `Docker`
   - **Mode**: `Standard`
   - **Region**: `us-central1`
5. Click **"Create"**

### Option 3: Let CI/CD Create It

The CI/CD workflow now includes a step that automatically creates the repository if it doesn't exist. Just run the workflow again.

---

## Manual Setup (One-Time)

If you're setting up manually:

```bash
# Set your project
export GOOGLE_CLOUD_PROJECT=fluent-coder-476318-n0
export GCP_REGION=us-central1

# Create Artifact Registry repository
gcloud artifacts repositories create stepsquad \
  --repository-format=docker \
  --location=$GCP_REGION \
  --project=$GOOGLE_CLOUD_PROJECT

# Verify it was created
gcloud artifacts repositories list --location=$GCP_REGION
```

---

## Verify Repository Exists

```bash
gcloud artifacts repositories describe stepsquad \
  --location=us-central1 \
  --project=YOUR_PROJECT_ID
```

Expected output:
```
name: projects/YOUR_PROJECT_ID/locations/us-central1/repositories/stepsquad
format: DOCKER
```

---

## Permissions Required

The service account used for CI/CD needs:
- `Artifact Registry Writer` role (to push images)
- Or `Artifact Registry Admin` role (full access)

The CI/CD service account should already have these permissions if configured correctly.

