# Quick Fix: Grant Missing Permissions

## Your Service Account
- **Email:** `github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com`
- **Missing:** `Service Usage Consumer` role (and possibly others)

## Grant Permissions via GCP Console

1. Go to: https://console.cloud.google.com/iam-admin/iam?project=fluent-coder-476318-n0
2. Find: `github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com`
3. Click the **pencil icon** (Edit) next to it
4. Click **"ADD ANOTHER ROLE"**
5. Add these roles:
   - ✅ `Service Usage Consumer` ⚠️ **Critical - This is missing!**
   - ✅ `Storage Admin` (for Cloud Build buckets)
   - ✅ `Cloud Build Service Account` (if not already added)
6. Click **"SAVE"**

## Or Grant via gcloud CLI (Quick)

Run these commands locally (you're already authenticated):

```bash
# Set variables
PROJECT_ID="fluent-coder-476318-n0"
SERVICE_ACCOUNT="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Service Usage Consumer (CRITICAL!)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/serviceusage.serviceUsageConsumer"

# Grant Storage Admin (for Cloud Build buckets)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.admin"

# Grant Cloud Build Service Account (if not already added)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.builder"
```

After granting these permissions, re-run the GitHub Actions workflow.

## Verify Permissions

Check what roles the service account has:

```bash
gcloud projects get-iam-policy fluent-coder-476318-n0 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

You should see at least:
- `roles/serviceusage.serviceUsageConsumer`
- `roles/storage.admin`
- `roles/cloudbuild.builds.editor`
- `roles/cloudbuild.builds.builder`
- `roles/run.admin`
