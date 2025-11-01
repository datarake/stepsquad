# Service Account Permissions Required

## The Error
```
ERROR: (gcloud.builds.submit) The user is forbidden from accessing the bucket [***_cloudbuild]. 
Please check your organization's policy or if the user has the "serviceusage.services.use" permission.
```

This means the service account is missing required permissions.

## Required Roles

Your service account needs these **IAM roles**:

### 1. Cloud Build Roles
- **Cloud Build Editor** (`roles/cloudbuild.builds.editor`) - Submit builds
- **Cloud Build Service Account** (`roles/cloudbuild.builds.builder`) - Run builds
- **Service Usage Consumer** (`roles/serviceusage.serviceUsageConsumer`) - Use Cloud Build service ⚠️ **This is likely missing!**

### 2. Cloud Run Roles
- **Cloud Run Admin** (`roles/run.admin`) - Deploy and manage services
- **Service Account User** (`roles/iam.serviceAccountUser`) - Use service accounts

### 3. Storage Roles (for Cloud Build buckets)
- **Storage Admin** (`roles/storage.admin`) - Access Cloud Build storage buckets

### 4. Artifact Registry (if using)
- **Artifact Registry Writer** (`roles/artifactregistry.writer`) - Push images

## How to Fix

### Option 1: Grant Individual Roles (Recommended)

1. Go to: https://console.cloud.google.com/iam-admin/iam?project=fluent-coder-476318-n0
2. Find your service account (e.g., `github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com`)
3. Click the **pencil icon** (Edit) next to it
4. Click **"ADD ANOTHER ROLE"**
5. Add these roles one by one:
   - `Service Usage Consumer`
   - `Storage Admin` (or at least access to Cloud Build buckets)
6. Click **"SAVE"**

### Option 2: Grant via gcloud CLI

```bash
# Set variables
PROJECT_ID="fluent-coder-476318-n0"
SERVICE_ACCOUNT="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.editor"
```

### Option 3: Quick Fix - Grant Owner Role (Not Recommended for Production)

If you want to test quickly (not recommended for production):

```bash
gcloud projects add-iam-policy-binding fluent-coder-476318-n0 \
  --member="serviceAccount:github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com" \
  --role="roles/owner"
```

**Warning:** Owner role has full access. Only use for testing.

## Recommended Roles Summary

For a production-ready setup, grant these roles to your service account:

| Role | Purpose |
|------|---------|
| `roles/serviceusage.serviceUsageConsumer` | Use Cloud Build service ⚠️ **Critical!** |
| `roles/cloudbuild.builds.editor` | Submit and manage builds |
| `roles/cloudbuild.builds.builder` | Execute builds |
| `roles/storage.admin` | Access Cloud Build storage |
| `roles/run.admin` | Deploy to Cloud Run |
| `roles/iam.serviceAccountUser` | Use service accounts |
| `roles/artifactregistry.writer` | Push images (if using Artifact Registry) |

## Verify Permissions

After granting roles, verify them:

```bash
gcloud projects get-iam-policy fluent-coder-476318-n0 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

You should see all the roles listed above.
