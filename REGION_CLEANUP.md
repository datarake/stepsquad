# Single Region Setup - StepSquad

This guide will help you clean up duplicate deployments and keep only one region (`us-central1`).

---

## Current Status

You currently have services deployed in **both regions**:
- ✅ **us-central1** (keeping - used by CI/CD)
- ❌ **europe-west1** (will be deleted - old manual deployments)

**Services deployed in both regions:**
- `stepsquad-api` (Backend API)
- `stepsquad-web` (Frontend)
- `stepsquad-workers` (Background workers)
- `stepsquad-agents` (AI agents)

---

## Step 1: Delete Services in europe-west1

### Option A: Use Cleanup Script (Recommended)

Run the provided cleanup script:

```bash
./cleanup_duplicate_regions.sh
```

This will:
1. ✅ Check each service in `europe-west1`
2. 🗑️ Delete it if found
3. ✅ Verify service exists in `us-central1`
4. 📊 Show final service list

### Option B: Manual Deletion

Delete services manually one by one:

```bash
# Delete API
gcloud run services delete stepsquad-api --region europe-west1 --quiet

# Delete Web
gcloud run services delete stepsquad-web --region europe-west1 --quiet

# Delete Workers
gcloud run services delete stepsquad-workers --region europe-west1 --quiet

# Delete Agents
gcloud run services delete stepsquad-agents --region europe-west1 --quiet
```

### Option C: Delete All at Once

```bash
REGION="europe-west1"
for SERVICE in stepsquad-api stepsquad-web stepsquad-workers stepsquad-agents; do
  echo "Deleting ${SERVICE} from ${REGION}..."
  gcloud run services delete "${SERVICE}" --region "${REGION}" --quiet || true
done
```

---

## Step 2: Verify Configuration

### CI/CD Configuration ✅

Your GitHub Actions workflow (`.github/workflows/deploy.yml`) is already configured correctly:

```yaml
env:
  REGION: us-central1  # ✅ Single region
```

All deployments will go to `us-central1` only.

### Manual Deployment Scripts ✅

Your manual deployment scripts (in `deploy/`) default to `us-central1`:

```bash
REGION=${GCP_REGION:-us-central1}  # ✅ Defaults to us-central1
```

---

## Step 3: Verify Final Setup

After cleanup, verify all services are in `us-central1` only:

```bash
# List all services
gcloud run services list --format="table(metadata.name,status.url)"

# Should show only us-central1 URLs (ending in -uc.a.run.app)
```

Expected output:
```
NAME               URL
stepsquad-agents   https://stepsquad-agents-...-uc.a.run.app
stepsquad-api      https://stepsquad-api-...-uc.a.run.app
stepsquad-web      https://stepsquad-web-...-uc.a.run.app
stepsquad-workers  https://stepsquad-workers-...-uc.a.run.app
```

---

## Step 4: Update Domain Mappings

When setting up custom domains, use `us-central1`:

```bash
# Map backend domain
gcloud run domain-mappings create \
  --service stepsquad-api \
  --domain api.stepsquad.club \
  --region us-central1

# Map frontend domain
gcloud run domain-mappings create \
  --service stepsquad-web \
  --domain www.stepsquad.club \
  --region us-central1
```

---

## Benefits of Single Region

1. ✅ **Simpler Management**: Only one region to manage
2. ✅ **Lower Costs**: No duplicate deployments
3. ✅ **Easier Debugging**: All services in one place
4. ✅ **Consistent Configuration**: Same region for all services

---

## Region Selection: us-central1

We're keeping `us-central1` because:
- ✅ Already configured in CI/CD
- ✅ Default for most Google Cloud services
- ✅ Good performance globally
- ✅ All deployment scripts default to this region

---

## After Cleanup

Once cleanup is complete:

1. ✅ All services will be in `us-central1` only
2. ✅ CI/CD will continue deploying to `us-central1`
3. ✅ Custom domains will map to `us-central1` services
4. ✅ No more duplicate deployments

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Cleanup

