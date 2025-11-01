# CI/CD Troubleshooting Guide

## Common Issues and Solutions

### Issue: "The project property is set to the empty string"

**Cause:** The `GCP_PROJECT_ID` GitHub secret is not set or is empty.

**Solution:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add or update the `GCP_PROJECT_ID` secret with your GCP project ID
3. Verify the secret name matches exactly (case-sensitive)

### Issue: "argument VALUE: Must be specified"

**Cause:** The `GCP_PROJECT_ID` secret is not being expanded correctly.

**Solution:**
- The workflow now includes validation to check if the secret is set
- If the error persists, verify the secret exists in GitHub Secrets
- Check that the secret name matches: `GCP_PROJECT_ID`

### Required GitHub Secrets

The workflow requires these secrets to be set:

1. **GCP_PROJECT_ID** - Your Google Cloud Project ID
   - Example: `my-project-123456`
   - Where to find: GCP Console → Project Settings → Project ID

2. **GCP_SA_KEY** - Service Account JSON Key
   - The service account key file as JSON
   - Required permissions:
     - Cloud Run Admin
     - Cloud Build Editor
     - Service Account User
     - Artifact Registry Writer (if using Artifact Registry)

### How to Set Secrets

1. Go to your GitHub repository
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret:
   - Name: `GCP_PROJECT_ID`
   - Value: Your GCP project ID
   
   - Name: `GCP_SA_KEY`
   - Value: Paste the entire JSON content of your service account key file

### Verify Secrets are Set

You can verify secrets are set by checking the workflow logs:
- The "Set project" step should show the project ID
- The "gcloud config list" output should show the project

### Alternative: Use Environment Variables

If secrets aren't working, you can also use environment variables:
- Set `GCP_PROJECT_ID` as a repository variable (Settings → Secrets and variables → Actions → Variables tab)
- Variables are less secure but can be used for non-sensitive data like project IDs
