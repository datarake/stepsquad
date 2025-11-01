# How to Get GCP Service Account Key for CI/CD

## Step-by-Step Guide

### Step 1: Create a New Service Account for CI/CD

1. On the Service Accounts page you're on, click **"+ Create service account"** (top right)

2. Fill in the details:
   - **Service account name:** `github-actions` (or `ci-cd`)
   - **Service account ID:** Will auto-generate (e.g., `github-actions`)
   - **Description:** `Service account for GitHub Actions CI/CD`
   - Click **"Create and continue"**

3. **Grant roles** (permissions):
   - Add these roles one by one:
     - `Cloud Run Admin` - For deploying to Cloud Run
     - `Cloud Build Editor` - For building container images
     - `Service Account User` - For using service accounts
     - `Artifact Registry Writer` - For pushing images to Artifact Registry (if using)
   - Click **"Continue"**

4. Click **"Done"**

### Step 2: Create a JSON Key

1. Find your newly created service account in the list (should be `github-actions@fluent-coder-476318-n0.iam.gserviceaccount.com`)

2. Click on the service account email (to open its details)

3. Go to the **"Keys"** tab (top of the page)

4. Click **"Add key"** → **"Create new key"**

5. Select **Key type:** `JSON`

6. Click **"Create"**

7. A JSON file will download automatically (e.g., `fluent-coder-476318-n0-xxxxx.json`)

### Step 3: Get the Key Content

1. **Open the downloaded JSON file** in a text editor

2. **Copy the entire content** of the JSON file (it should start with something like):
   ```json
   {
     "type": "service_account",
     "project_id": "fluent-coder-476318-n0",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     ...
   }
   ```

3. **Important:** Copy the ENTIRE file content (all the JSON)

### Step 4: Add to GitHub Secrets

1. Go back to GitHub: Settings → Secrets and variables → Actions

2. Click **"New repository secret"**

3. **Name:** `GCP_SA_KEY`

4. **Secret:** Paste the entire JSON content you copied

5. Click **"Add secret"**

## Important Security Notes

- ⚠️ **Never commit the JSON key file to git** (it's already in .gitignore)
- ⚠️ **Never share the key publicly**
- ✅ The JSON key file on your computer can be deleted after adding to GitHub (GitHub will store it securely)
- ✅ If the key is compromised, delete it in GCP and create a new one

## Alternative: Using Existing Service Account

If you prefer to use an existing service account:

1. Find it in the service accounts list
2. Click on it → "Keys" tab
3. Click "Add key" → "Create new key" → "JSON"
4. Download and copy the content as above

## Required Permissions Summary

The service account needs these roles:
- `Cloud Run Admin` - Deploy services
- `Cloud Build Editor` - Build container images  
- `Service Account User` - Use service accounts
- `Artifact Registry Writer` - Push images (if using Artifact Registry)
