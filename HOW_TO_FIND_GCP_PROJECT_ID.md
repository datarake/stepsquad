# How to Find Your GCP Project ID

## Quick Answer
Based on your local gcloud configuration, your GCP Project ID is:
**`fluent-coder-476318-n0`**

## How to Find/Verify Your GCP Project ID

### Method 1: From GCP Console (Web)
1. Go to: https://console.cloud.google.com/
2. Sign in with: `bogdan.burdalescu@proton.me`
3. Look at the top bar - you'll see the project name "StepSquad"
4. Click on the project selector (top bar)
5. The **Project ID** is shown as: `fluent-coder-476318-n0`
   - Note: Project ID is different from Project Name
   - Project ID is the unique identifier (cannot be changed)
   - Project Name is "StepSquad" (can be changed)

### Method 2: From Project Settings (GCP Console)
1. Go to: https://console.cloud.google.com/home/dashboard?project=fluent-coder-476318-n0
2. Click on the hamburger menu (☰) → "IAM & Admin" → "Project Settings"
3. You'll see:
   - **Project name:** StepSquad
   - **Project ID:** `fluent-coder-476318-n0`
   - **Project number:** 371825059669

### Method 3: Using gcloud CLI (already found)
```bash
gcloud config get-value project
# Returns: fluent-coder-476318-n0
```

### Method 4: List all your projects
```bash
gcloud projects list
# Shows: fluent-coder-476318-n0  StepSquad  371825059669
```

## What to Set in GitHub Secret
- **Secret Name:** `GCP_PROJECT_ID`
- **Secret Value:** `fluent-coder-476318-n0`

## Important Notes
- **Project ID** vs **Project Name**:
  - Project ID: `fluent-coder-476318-n0` (this is what you need)
  - Project Name: `StepSquad` (this is just a display name)
- The Project ID is unique and cannot be changed
- Use the Project ID (not the Project Name) in GitHub secrets
