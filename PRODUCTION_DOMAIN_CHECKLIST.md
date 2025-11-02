# Production Domain Configuration Checklist

**Status**: Domain mappings created ✅  
**Domain**: `stepsquad.club`  
**Backend**: `https://api.stepsquad.club`  
**Frontend**: `https://www.stepsquad.club`

---

## ✅ Already Configured

### Backend (Cloud Run)

1. ✅ **OAuth Redirect URIs Updated**:
   - `FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback`
   - `GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback`
   - Already set in Cloud Run service environment variables

2. ✅ **CI/CD Workflow Updated**:
   - `.github/workflows/deploy.yml` configured to use `https://api.stepsquad.club`
   - Falls back to Cloud Run URL if custom domain not accessible yet

3. ✅ **OAuth Client Configuration**:
   - `apps/api/fitbit_client.py` uses `FITBIT_REDIRECT_URI` environment variable ✅
   - `apps/api/garmin_client.py` uses `GARMIN_REDIRECT_URI` environment variable ✅

### Frontend

1. ✅ **API Client Configuration**:
   - `apps/web/src/api.ts` uses `VITE_API_BASE_URL` environment variable
   - CI/CD builds with `https://api.stepsquad.club` ✅

2. ✅ **OAuth Callback Handlers**:
   - `apps/web/src/OAuthCallbackPage.tsx` uses API_BASE_URL (automatically uses custom domain) ✅
   - `apps/web/src/DeviceSettingsPage.tsx` uses API_BASE_URL ✅

---

## ⚠️ Manual Steps Required

### Step 1: Update Fitbit App Redirect URI

**Important**: Update your Fitbit app configuration in Fitbit Developer Portal.

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Log in
3. Go to **Manage** → **My Apps** → Select your app
4. Edit the app settings
5. Update **Redirect URI** to:
   ```
   https://api.stepsquad.club/oauth/fitbit/callback
   ```
6. Save changes

**Why**: Fitbit needs to know the exact callback URL. If it doesn't match, OAuth will fail.

---

### Step 2: Update Garmin App Callback URL (if applicable)

If you've set up Garmin OAuth:

1. Go to [Garmin Developer Portal](https://developer.garmin.com/)
2. Edit your OAuth client
3. Update **Callback URL** to:
   ```
   https://api.stepsquad.club/oauth/garmin/callback
   ```
4. Save changes

---

### Step 3: Verify Domain Accessibility

Wait 15-30 minutes for DNS propagation, then test:

**Test Backend:**
```bash
curl https://api.stepsquad.club/health
```

**Expected:**
```json
{"ok":true,"time":"...","tz":"Europe/Bucharest","gcp_enabled":true}
```

**Test Frontend:**
- Open `https://www.stepsquad.club` in browser
- Should load StepSquad web app

**Test OAuth Callback:**
```bash
curl -I https://api.stepsquad.club/oauth/fitbit/callback
```
- Should return HTTP status (200, 400, or 401 - all indicate endpoint exists)
- 401/400 is normal if called without OAuth parameters

---

## ✅ No Code Changes Needed

### Why No Changes Are Needed:

1. **Frontend API URL**: 
   - Uses `VITE_API_BASE_URL` environment variable ✅
   - CI/CD already builds with `https://api.stepsquad.club` ✅
   - No hardcoded URLs ✅

2. **Backend OAuth Redirect URIs**:
   - Use environment variables (`FITBIT_REDIRECT_URI`, `GARMIN_REDIRECT_URI`) ✅
   - Already set to `https://api.stepsquad.club/oauth/*/callback` ✅
   - No hardcoded URLs ✅

3. **OAuth Client Code**:
   - Reads from environment variables ✅
   - Dynamically uses configured redirect URIs ✅

---

## 📝 Optional: Update Documentation URLs

### Terms and Privacy Pages

These pages already have placeholder contact info. If you want to update:

**In `public/terms.html` and `public/privacy.html`:**

Search for and update:
- `support@stepsquad.club` (already correct)
- `https://stepsquad.club` (already correct)

These are already set correctly!

---

## 🧪 Testing After DNS Propagation

Once DNS propagates (15-30 minutes), test everything:

### 1. Backend Health Check
```bash
curl https://api.stepsquad.club/health
```

### 2. Frontend Load
```bash
curl https://www.stepsquad.club
```

### 3. OAuth Flow Test

1. Open `https://www.stepsquad.club/devices`
2. Click **"Connect Fitbit"**
3. Should redirect to Fitbit OAuth page
4. After authorization, should redirect back to:
   - `https://www.stepsquad.club/oauth/fitbit/callback`
   - Which then processes and redirects to `/devices`

### 4. API Endpoints Test

```bash
# Test OAuth authorize
curl https://api.stepsquad.club/oauth/fitbit/authorize

# Test devices endpoint
curl https://api.stepsquad.club/devices
```

---

## 🔍 Current Configuration Summary

### Backend Environment Variables (Cloud Run):

```
FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback ✅
GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback ✅
GCP_ENABLED=true ✅
COMP_TZ=Europe/Bucharest ✅
```

### Frontend Build Configuration (CI/CD):

```
VITE_API_BASE_URL=https://api.stepsquad.club ✅
VITE_USE_DEV_AUTH=false ✅
```

### OAuth App Configurations (External):

**Fitbit App** (Fitbit Developer Portal):
- ⚠️ **Needs Update**: Redirect URI should be `https://api.stepsquad.club/oauth/fitbit/callback`

**Garmin App** (Garmin Developer Portal):
- ⚠️ **Needs Update** (if using): Callback URL should be `https://api.stepsquad.club/oauth/garmin/callback`

---

## ✅ Final Checklist

- [x] Domain verified in Google Cloud ✅
- [x] Domain mappings created (api.stepsquad.club, www.stepsquad.club) ✅
- [x] DNS records added in GoDaddy ✅
- [x] Backend OAuth redirect URIs updated ✅
- [x] CI/CD workflow updated ✅
- [ ] **Update Fitbit app redirect URI** (Manual - Fitbit Developer Portal) ⚠️
- [ ] **Update Garmin app callback URL** (Manual - if using Garmin) ⚠️
- [ ] Wait 15-30 minutes for DNS propagation ⏳
- [ ] Test backend: `curl https://api.stepsquad.club/health`
- [ ] Test frontend: `https://www.stepsquad.club`
- [ ] Test OAuth flow: Connect Fitbit from devices page

---

## 🎉 Summary

**Good news**: Most things are already configured! ✅

**Only manual steps needed:**
1. ⚠️ **Update Fitbit app redirect URI** in Fitbit Developer Portal
2. ⚠️ **Update Garmin app callback** (if using Garmin) in Garmin Developer Portal
3. ⏳ **Wait for DNS propagation** (15-30 minutes)
4. 🧪 **Test domains** once DNS propagates

**No code changes needed** - everything uses environment variables! ✅

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Testing After DNS Propagation

