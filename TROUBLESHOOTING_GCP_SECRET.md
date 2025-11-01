# Troubleshooting: GCP_PROJECT_ID Secret Not Found

## The Issue
The workflow shows: `Error: GCP_PROJECT_ID secret is not set`

This happens when the GitHub secret either:
1. **Doesn't exist** - Secret was never created
2. **Wrong name** - Secret name doesn't match (case-sensitive!)
3. **Wrong repository** - Secret was added to a different repo
4. **Empty value** - Secret was created but left empty

## How to Fix

### Step 1: Verify Secret Exists
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Look for a secret named exactly: **`GCP_PROJECT_ID`** (case-sensitive!)
   - If you see it: ✅ Secret exists
   - If you don't see it: ❌ Need to create it

### Step 2: Check Secret Name (Case-Sensitive!)
The secret name must be **exactly**: `GCP_PROJECT_ID`
- ✅ Correct: `GCP_PROJECT_ID`
- ❌ Wrong: `gcp_project_id`, `GCP_PROJECT_ID_`, `GCP_PROJECT_ID `, `gcp-project-id`

### Step 3: Verify Secret Value
1. Click on the `GCP_PROJECT_ID` secret
2. Click **Update** to see/edit the value
3. Value should be: `fluent-coder-476318-n0`
4. Make sure there are **no spaces** before/after the value

### Step 4: Check Repository
Make sure you're adding the secret to the **correct repository**:
- Repository: `your-username/stepsquad` (or wherever your code is)

### Step 5: Create Secret if Missing
If the secret doesn't exist:

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. **Name:** `GCP_PROJECT_ID` (exactly, case-sensitive)
4. **Secret:** `fluent-coder-476318-n0`
5. Click **"Add secret"**

## Quick Verification Commands

After setting the secret, you can verify the workflow will see it:
1. Go to **Actions** tab
2. Click **"Deploy StepSquad to Cloud Run"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Check the logs for the "Set project" step
5. You should see: `Project ID: fluent-coder-476318-n0`

## Common Mistakes

1. **Secret name typo:**
   - ❌ `GCP_PROJECT` (missing `_ID`)
   - ❌ `gcp_project_id` (wrong case)
   - ✅ `GCP_PROJECT_ID` (correct)

2. **Secret in wrong place:**
   - ❌ Repository → Settings → Secrets (old location)
   - ✅ Repository → Settings → Secrets and variables → Actions

3. **Secret value has spaces:**
   - ❌ ` fluent-coder-476318-n0 ` (spaces)
   - ✅ `fluent-coder-476318-n0` (no spaces)

## Still Not Working?

If the secret still isn't recognized:
1. **Delete and recreate** the secret
2. Make sure you're on the **main branch** (workflow might only run on main)
3. Check if the workflow is running in the correct repository
4. Verify the workflow file has: `${{ secrets.GCP_PROJECT_ID }}`
