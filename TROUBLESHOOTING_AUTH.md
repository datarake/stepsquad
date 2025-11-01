# Troubleshooting: gcloud Authentication Error

## The Issue
The workflow shows: `ERROR: (gcloud.builds.submit) You do not currently have an active account selected.`

This happens when the `setup-gcloud` action doesn't properly authenticate with the service account key.

## What Was Fixed

1. **Upgraded to setup-gcloud@v2** - Latest version with better authentication handling
2. **Added `export_default_credentials: true`** - Ensures credentials are exported for all gcloud commands
3. **Added authentication verification** - Checks if authentication works before proceeding

## Verify Service Account Key

If authentication still fails, verify your `GCP_SA_KEY` secret:

### 1. Check Key Format
The service account key must be:
- Valid JSON format
- Complete (all fields present)
- No extra whitespace or formatting issues

### 2. Verify Key Content
In GitHub, edit the `GCP_SA_KEY` secret and verify it starts with:
```json
{
  "type": "service_account",
  "project_id": "fluent-coder-476318-n0",
  ...
}
```

### 3. Test Key Locally (Optional)
If you still have the JSON file, you can test it:
```bash
# Set the key file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Test authentication
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud auth list  # Should show the service account
```

### 4. Recreate Key if Needed
If the key is invalid:
1. Go to GCP Console → Service Accounts
2. Find your service account (e.g., `github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com`)
3. Click on it → "Keys" tab
4. Delete the old key
5. Create a new key → JSON
6. Copy the entire JSON content
7. Update the `GCP_SA_KEY` secret in GitHub

## Verify Service Account Permissions

Ensure your service account has these roles:
- `Cloud Run Admin` - Deploy services
- `Cloud Build Editor` - Build container images
- `Service Account User` - Use service accounts
- `Artifact Registry Writer` - Push images (if using Artifact Registry)

## Check Workflow Logs

After pushing the fix, check the workflow logs for:
1. "Verify authentication" step - Should show the service account email
2. `gcloud auth list` output - Should show an active account
3. `gcloud config list` output - Should show the project ID

If these all pass, authentication is working correctly.
