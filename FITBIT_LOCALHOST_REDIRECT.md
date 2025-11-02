# Adding Localhost Redirect URI to Fitbit App

## Problem

When testing Fitbit OAuth locally, you get this error:
```
The app you're trying to connect did not provide valid information to Fitbit.
Developer information: invalid_request - Invalid redirect_uri parameter value
```

**Cause**: The redirect URI `http://localhost:8080/oauth/fitbit/callback` is not registered in your Fitbit app settings.

## Solution

You need to add the localhost redirect URI to your Fitbit app in the Fitbit Developer Portal.

---

## Step-by-Step Instructions

### Step 1: Go to Fitbit Developer Portal

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Sign in with your Fitbit account
3. Navigate to **Manage** → **My Apps**
4. Find your **StepSquad** app and click on it

### Step 2: Edit App Settings

1. Click **"Edit"** or **"Manage"** button
2. Scroll down to **"OAuth 2.0 Settings"** section
3. Find **"Redirect URL"** or **"Callback URL"** field

### Step 3: Add Localhost Redirect URI

**Option A: Multiple Redirect URIs (if supported)**

If Fitbit supports multiple redirect URIs:

1. Look for **"Add Redirect URI"** or **"Additional Redirect URIs"** section
2. Add: `http://localhost:8080/oauth/fitbit/callback`
3. Keep the existing production URI: `https://api.stepsquad.club/oauth/fitbit/callback`
4. Click **"Save"**

**Option B: Single Redirect URI (most common)**

If Fitbit only supports one redirect URI, you have two options:

#### Option B1: Use Localhost for Development (Temporary)

1. Change **"Redirect URL"** to: `http://localhost:8080/oauth/fitbit/callback`
2. Click **"Save"**
3. **⚠️ Important**: Remember to change it back to production URL (`https://api.stepsquad.club/oauth/fitbit/callback`) before deploying to production!

#### Option B2: Switch Between Development and Production

1. For local development: Set to `http://localhost:8080/oauth/fitbit/callback`
2. For production: Set to `https://api.stepsquad.club/oauth/fitbit/callback`
3. Switch between them as needed

---

## Current Configuration

**Local Development:**
- Redirect URI: `http://localhost:8080/oauth/fitbit/callback`
- Client ID: `23THXK`
- Client Secret: `3f319445dd6e4824bd2f7f579440cd36`

**Production:**
- Redirect URI: `https://api.stepsquad.club/oauth/fitbit/callback`
- Client ID: `23THXK`
- Client Secret: `3f319445dd6e4824bd2f7f579440cd36`

---

## After Adding Redirect URI

Once you've added the localhost redirect URI:

1. **Save the changes** in Fitbit Developer Portal
2. **Wait 1-2 minutes** for changes to propagate
3. **Try the OAuth flow again**:
   - Go to `http://localhost:5174/devices`
   - Click **"Connect Fitbit"**
   - Should redirect to Fitbit authorization page
   - Click **"Allow"**
   - Should redirect back to `http://localhost:5174/oauth/fitbit/callback`

---

## Troubleshooting

### Still Getting "Invalid redirect_uri" Error

**Check:**
1. ✅ Redirect URI matches **exactly** (case-sensitive, no trailing slash)
2. ✅ Saved changes in Fitbit Developer Portal
3. ✅ Waited 1-2 minutes for changes to propagate
4. ✅ Redirect URI is: `http://localhost:8080/oauth/fitbit/callback` (not `https://`)

### Redirect URI Not Saving

**Try:**
1. Refresh the Fitbit Developer Portal page
2. Make sure you're editing the correct app (StepSquad)
3. Check for error messages on the page
4. Try logging out and back in

### OAuth Flow Works but Callback Fails

**Check:**
1. Backend is running on `http://localhost:8080`
2. Backend endpoint `/oauth/fitbit/callback` is accessible
3. Check backend logs for errors: `tail -f /tmp/stepsquad-api.log`

---

## Best Practices

### Development

1. ✅ Use `http://localhost:8080/oauth/fitbit/callback` for local testing
2. ✅ Test OAuth flow locally before deploying
3. ✅ Use different redirect URIs for dev and production

### Production

1. ✅ Use `https://api.stepsquad.club/oauth/fitbit/callback` for production
2. ✅ Don't expose localhost URLs in production
3. ✅ Ensure HTTPS for all production URLs

---

## Quick Reference

**Fitbit Developer Portal:**
- URL: https://dev.fitbit.com/
- Navigate: **Manage** → **My Apps** → **StepSquad** → **Edit**

**Current Redirect URIs:**
- Local Dev: `http://localhost:8080/oauth/fitbit/callback`
- Production: `https://api.stepsquad.club/oauth/fitbit/callback`

**Fitbit App Credentials:**
- Client ID: `23THXK`
- Client Secret: `3f319445dd6e4824bd2f7f579440cd36`

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Configuration

