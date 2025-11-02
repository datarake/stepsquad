# Fitbit OAuth Scope Selection Guide

## Where to Find Scopes in Fitbit Developer Portal

### Option 1: Scopes May Appear After Saving the Form

**Step 1**: Save the current form first (click **"Save"** button)

**Step 2**: After saving, the app details page may show:
- A **"Scopes"** or **"Permissions"** section
- An **"Edit Scopes"** or **"Manage Scopes"** button
- A section labeled **"OAuth 2.0 Scopes"** or **"API Access"**

### Option 2: Scopes Are Selected During OAuth Flow

Fitbit scopes might **NOT** be selected in the app registration form. Instead, they are:
- **Automatically requested** when users authorize the app
- **Defined in the authorization URL** when your backend calls the OAuth endpoint

In your code (`apps/api/fitbit_client.py`), the scope is already set:
```python
"scope": "activity",  # Required scope for step data
```

So when users authorize your app, Fitbit will request the **"activity"** scope automatically.

---

## Required Scopes for StepSquad

### Primary Scope (Required)
- **`activity`** - Access to activity data (steps, distance, calories, etc.)

### Optional Scopes (if needed)
- **`profile`** - Access to basic profile information
- **`settings`** - Access to user settings (optional)

---

## What to Do

### If You See the Current Form:

1. **Fill out all required fields:**
   - ✅ Organization Website URL: `https://stepsquad.club`
   - ✅ Terms of Service URL: `https://stepsquad.club/terms`
   - ✅ Privacy Policy URL: `https://stepsquad.club/privacy`
   - ✅ OAuth 2.0 Application Type: **Server** (selected)
   - ✅ Redirect URL: `https://api.stepsquad.club/oauth/fitbit/callback`
   - ✅ Default Access Type: **Read Only** (selected)

2. **Click "Save"** button

3. **After saving**, look for:
   - A new section or tab for **"Scopes"**, **"Permissions"**, or **"API Access"**
   - An **"Edit"** or **"Manage"** button next to the app name
   - A dropdown or checkbox list for selecting scopes

### If You Don't See Scopes After Saving:

**Don't worry!** Scopes are automatically requested when your app makes the OAuth authorization request. Your backend code already specifies the scope:

```python
# In apps/api/fitbit_client.py
"scope": "activity",  # This is automatically requested
```

So when users authorize your app, Fitbit will ask for the **"activity"** scope automatically.

---

## How Fitbit Scopes Work

### During OAuth Flow:

1. Your backend generates an authorization URL with `scope=activity`
2. User clicks "Connect Fitbit" on your website
3. User is redirected to Fitbit authorization page
4. Fitbit shows a consent screen asking: **"Allow StepSquad to access your activity data?"**
5. User clicks **"Allow"**
6. User is redirected back with an authorization code
7. Your backend exchanges the code for an access token with `activity` scope

**The scope is requested during the OAuth flow, not in the app registration form!**

---

## Verification

After saving the form, you should be able to:

1. **See your app** in "My Apps" list
2. **Get your OAuth 2.0 Client ID** and **Client Secret**
3. **Use these credentials** to set environment variables

The scope (`activity`) will be automatically requested when users authorize the app.

---

## Next Steps After Registration

1. ✅ **Save the form** with all the fields you've filled
2. ✅ **Get your Client ID** and **Client Secret** from the app details page
3. ✅ **Set environment variables** in Cloud Run:
   ```bash
   gcloud run services update stepsquad-api \
     --update-env-vars="FITBIT_CLIENT_ID=your_client_id_here,FITBIT_CLIENT_SECRET=your_client_secret_here,FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback" \
     --region us-central1
   ```
4. ✅ **Test the OAuth flow** - the scope will be automatically requested

---

## Summary

**Good news**: You don't need to find a scope selection in the registration form! 

The **"activity"** scope is:
- ✅ Already configured in your backend code (`fitbit_client.py`)
- ✅ Automatically requested during the OAuth authorization flow
- ✅ Shown to users in the Fitbit consent screen when they authorize your app

**Just save the form and continue with getting your Client ID and Secret!**

---

**Last Updated**: November 2, 2025  
**Status**: Scope is handled automatically during OAuth flow

