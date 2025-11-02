# Fitbit Integration Checklist

Complete checklist for Fitbit OAuth integration in StepSquad.

---

## ✅ What's Already Implemented

### Backend Implementation

1. ✅ **Fitbit OAuth Client** (`apps/api/fitbit_client.py`)
   - OAuth 2.0 authorization URL generation
   - Token exchange (code → access token)
   - Token refresh
   - Daily step fetching from Fitbit API
   - State token generation for security

2. ✅ **OAuth Endpoints** (`apps/api/main.py`)
   - `GET /oauth/fitbit/authorize` - Get authorization URL
   - `GET /oauth/fitbit/callback` - Handle OAuth callback

3. ✅ **Device Management Endpoints** (`apps/api/main.py`)
   - `GET /devices` - List connected devices
   - `POST /devices/{provider}/sync` - Manual device sync
   - `DELETE /devices/{provider}` - Unlink device

4. ✅ **Device Storage** (`apps/api/device_storage.py`)
   - Store OAuth tokens securely
   - Retrieve device tokens
   - Update device sync status
   - Remove device tokens

5. ✅ **Automatic Step Submission**
   - Device sync automatically submits steps to active competitions
   - Idempotency checks to prevent duplicates
   - Pub/Sub integration for async processing

### Frontend Implementation

1. ✅ **Device Settings Page** (`apps/web/src/DeviceSettingsPage.tsx`)
   - List connected devices
   - Connect Fitbit button
   - Manual sync button
   - Unlink device button
   - Display sync status

2. ✅ **OAuth Callback Page** (`apps/web/src/OAuthCallbackPage.tsx`)
   - Handle Fitbit OAuth callback
   - Display success/error messages
   - Redirect to devices page

3. ✅ **API Client** (`apps/web/src/api.ts`)
   - `getDevices()` - Fetch connected devices
   - `getFitbitAuthUrl()` - Get Fitbit authorization URL
   - `handleFitbitCallback()` - Process OAuth callback
   - `syncDevice()` - Manual device sync
   - `unlinkDevice()` - Unlink device

4. ✅ **Routing** (`apps/web/src/App.tsx`)
   - `/devices` route for device management
   - `/oauth/fitbit/callback` route for OAuth callback

5. ✅ **Navigation** (`apps/web/src/AppShell.tsx`)
   - "Devices" link in navigation menu

---

## ⚠️ What Needs to Be Done

### 1. Fitbit Developer Portal Configuration

**Status**: ⚠️ **Manual Step Required**

#### Step 1: Create/Configure Fitbit App

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Sign in with your Fitbit account
3. Go to **Manage** → **My Apps** → **Register a New App**
4. Fill in app details:
   - **Application Name**: `StepSquad`
   - **Description**: `Team-based step competition platform`
   - **Application Website**: `https://www.stepsquad.club`
   - **Organization**: `Tekolin` (or your organization)
   - **Organization Website**: `https://www.stepsquad.club`
   - **OAuth 2.0 Application Type**: `Server`
   - **Callback URL**: `https://api.stepsquad.club/oauth/fitbit/callback`
   - **Default Access Type**: `Read`
   - **Terms of Service URL**: `https://stepsquad.club/terms`
   - **Privacy Policy URL**: `https://stepsquad.club/privacy`

5. **Select Scopes**:
   - ✅ **Activity** (required for step data)
   - ✅ **Profile** (optional, for user info)

6. Click **Register**

#### Step 2: Get OAuth Credentials

After app registration:

1. Go to **Manage** → **My Apps** → **StepSquad**
2. You'll see:
   - **OAuth 2.0 Client ID** - Copy this
   - **Client Secret** - Copy this (keep it secure!)

#### Step 3: Update Redirect URI in Fitbit App

**Important**: Make sure the callback URL matches exactly:

1. Go to **Manage** → **My Apps** → **StepSquad** → **Edit**
2. Verify **Callback URL** is set to:
   ```
   https://api.stepsquad.club/oauth/fitbit/callback
   ```
3. Save changes

---

### 2. Environment Variables Configuration

**Status**: ⚠️ **Needs Verification/Update**

#### Check Current Environment Variables

Verify environment variables are set in Cloud Run:

```bash
gcloud run services describe stepsquad-api \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

#### Set Environment Variables

If not set, update Cloud Run service:

```bash
gcloud run services update stepsquad-api \
  --update-env-vars="FITBIT_CLIENT_ID=your_fitbit_client_id_here,FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here,FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback" \
  --region us-central1
```

**Replace:**
- `your_fitbit_client_id_here` with your actual Fitbit Client ID
- `your_fitbit_client_secret_here` with your actual Fitbit Client Secret

#### For Local Development

Create `apps/api/.env.local`:

```bash
FITBIT_CLIENT_ID=your_fitbit_client_id_here
FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here
FITBIT_REDIRECT_URI=http://localhost:8080/oauth/fitbit/callback
```

---

### 3. DNS Propagation (if not done yet)

**Status**: ⏳ **May Still Be Propagating**

Make sure custom domain is accessible:

1. **Wait 15-30 minutes** after adding DNS records
2. **Test API domain**:
   ```bash
   curl https://api.stepsquad.club/health
   ```
   Expected: `{"ok":true,"time":"...","tz":"...","gcp_enabled":true}`

3. **Test OAuth callback endpoint**:
   ```bash
   curl -I https://api.stepsquad.club/oauth/fitbit/callback
   ```
   Expected: HTTP status code (200, 400, or 401 - all indicate endpoint exists)

---

### 4. Testing Fitbit Integration

**Status**: 🧪 **Ready to Test**

#### Test 1: OAuth Authorization Flow

1. **Open frontend**: `https://www.stepsquad.club/devices`
2. **Click "Connect Fitbit"**
3. **Expected**: Redirect to Fitbit OAuth page
4. **Authorize** on Fitbit page
5. **Expected**: Redirect back to `https://www.stepsquad.club/oauth/fitbit/callback`
6. **Expected**: Success message, then redirect to `/devices`
7. **Verify**: Device appears in connected devices list

#### Test 2: Manual Device Sync

1. **Go to**: `https://www.stepsquad.club/devices`
2. **Click "Sync"** next to Fitbit device
3. **Expected**: Steps fetched and submitted to active competitions
4. **Verify**: Sync status updated (last_sync timestamp)

#### Test 3: Automatic Step Submission

1. **Create active competition**
2. **Join a team** in the competition
3. **Sync Fitbit device** (manual or automatic)
4. **Verify**: Steps submitted to competition
5. **Check leaderboard**: Steps should appear in team total

#### Test 4: Unlink Device

1. **Go to**: `https://www.stepsquad.club/devices`
2. **Click "Unlink"** next to Fitbit device
3. **Expected**: Device removed from list
4. **Verify**: OAuth tokens removed from storage

---

### 5. Backend Testing (Optional)

**Status**: 🧪 **Can Add Tests**

Consider adding backend tests for Fitbit integration:

1. **OAuth URL generation test**
2. **Token exchange test** (mock Fitbit API)
3. **Daily step fetching test** (mock Fitbit API)
4. **Token refresh test** (mock Fitbit API)
5. **Device storage test**
6. **Callback handler test**

---

### 6. Error Handling Improvements (Optional)

**Status**: 🔧 **Enhancement Opportunity**

Consider adding:

1. **Better error messages** for OAuth failures
2. **Token expiration handling** (automatic refresh)
3. **Rate limiting** for API calls
4. **Retry logic** for failed API calls
5. **Logging** for debugging OAuth issues

---

## 📋 Complete Checklist

### Fitbit Developer Portal

- [ ] Create Fitbit app in Developer Portal
- [ ] Get OAuth 2.0 Client ID
- [ ] Get Client Secret
- [ ] Set Callback URL: `https://api.stepsquad.club/oauth/fitbit/callback`
- [ ] Select scopes: Activity (required), Profile (optional)
- [ ] Verify app settings are saved

### Environment Variables

- [ ] `FITBIT_CLIENT_ID` set in Cloud Run
- [ ] `FITBIT_CLIENT_SECRET` set in Cloud Run
- [ ] `FITBIT_REDIRECT_URI` set to `https://api.stepsquad.club/oauth/fitbit/callback`
- [ ] Local `.env.local` configured (for local testing)

### Domain Configuration

- [ ] DNS records added (CNAME for `api.stepsquad.club`)
- [ ] DNS propagated (15-30 minutes)
- [ ] SSL certificate issued (automatic, 5-15 minutes)
- [ ] `https://api.stepsquad.club/health` accessible

### Testing

- [ ] OAuth authorization flow works
- [ ] Device connects successfully
- [ ] Manual sync works
- [ ] Steps submitted to active competitions
- [ ] Leaderboard updates correctly
- [ ] Unlink device works

### Code Implementation

- [x] Backend OAuth endpoints implemented
- [x] Device management endpoints implemented
- [x] Device storage implemented
- [x] Frontend device settings page implemented
- [x] OAuth callback handler implemented
- [x] API client methods implemented

---

## 🚀 Quick Start Guide

### If You Haven't Configured Fitbit App Yet:

1. **Go to [Fitbit Developer Portal](https://dev.fitbit.com/)**
2. **Register new app** with these settings:
   - Name: `StepSquad`
   - Callback URL: `https://api.stepsquad.club/oauth/fitbit/callback`
   - Scopes: `Activity`
3. **Get credentials** (Client ID and Secret)
4. **Set environment variables** in Cloud Run:
   ```bash
   gcloud run services update stepsquad-api \
     --update-env-vars="FITBIT_CLIENT_ID=YOUR_CLIENT_ID,FITBIT_CLIENT_SECRET=YOUR_CLIENT_SECRET,FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback" \
     --region us-central1
   ```
5. **Test**: Go to `https://www.stepsquad.club/devices` and click "Connect Fitbit"

### If You Already Configured Fitbit App:

1. **Verify redirect URI** matches exactly: `https://api.stepsquad.club/oauth/fitbit/callback`
2. **Verify environment variables** are set in Cloud Run
3. **Test the integration** from frontend
4. **Check logs** if there are any errors

---

## 🔍 Troubleshooting

### "Invalid redirect URI" Error

- **Problem**: Redirect URI doesn't match Fitbit app settings
- **Solution**: Verify callback URL in Fitbit app matches exactly: `https://api.stepsquad.club/oauth/fitbit/callback`

### "Invalid client credentials" Error

- **Problem**: Client ID or Secret incorrect
- **Solution**: Verify environment variables are set correctly in Cloud Run

### "Callback endpoint not found" Error

- **Problem**: DNS not propagated or SSL certificate not issued
- **Solution**: Wait 15-30 minutes for DNS propagation, check `https://api.stepsquad.club/health`

### "OAuth callback failed" Error

- **Problem**: OAuth flow interrupted or invalid state token
- **Solution**: Check browser console for errors, try connecting again

---

## 📚 Documentation References

- **Fitbit OAuth Setup Guide**: `OAUTH_SETUP_GUIDE.md`
- **Production Domain Checklist**: `PRODUCTION_DOMAIN_CHECKLIST.md`
- **Device Integration Docs**: `apps/api/README.md`

---

**Last Updated**: November 2, 2025  
**Status**: ✅ Code Complete, ⚠️ Configuration Needed

