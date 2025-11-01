# Setup Artifact Registry Repository (One-Time)

## The Problem

CI/CD service account doesn't have permission to create Artifact Registry repositories. You need to create it manually once.

## Solution

Run these commands **once** to set up the Artifact Registry:

### 1. Enable Artifact Registry API

```bash
gcloud services enable artifactregistry.googleapis.com --project=fluent-coder-476318-n0
```

### 2. Create the Repository

```bash
gcloud artifacts repositories create stepsquad \
  --repository-format=docker \
  --location=us-central1 \
  --project=fluent-coder-476318-n0
```

### 3. Verify It Was Created

```bash
gcloud artifacts repositories describe stepsquad \
  --location=us-central1 \
  --project=fluent-coder-476318-n0
```

Expected output should show the repository details.

---

## Alternative: Via Console

1. Go to [Artifact Registry Console](https://console.cloud.google.com/artifacts)
2. Select project: `fluent-coder-476318-n0`
3. Click **"+ Create repository"**
4. Fill in:
   - **Name**: `stepsquad`
   - **Format**: `Docker`
   - **Mode**: `Standard`
   - **Region**: `us-central1`
5. Click **"Create"**

---

## After Setup

Once the repository is created, CI/CD will be able to:
- ✅ Build and push images to the repository
- ✅ Deploy services using those images

The CI/CD workflow will now continue even if the API enable step fails (it's non-fatal).

---

## Check if Already Exists

If you're not sure if it exists:

```bash
gcloud artifacts repositories list --location=us-central1 --project=fluent-coder-476318-n0
```

Look for `stepsquad` in the list.

