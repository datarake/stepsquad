# Domain Verification and Mapping Setup

The domain `stepsquad.club` needs to be verified in Google Cloud before we can map it to Cloud Run services.

---

## Step 1: Verify Domain Ownership

### Option A: Using Google Cloud Console (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Run** → **Manage Custom Domains**
3. Click **Verify Domain**
4. Enter your domain: `stepsquad.club`
5. Click **Start Verification**

Google will provide **verification records** to add to your DNS:
- **Type**: `TXT` or `CNAME`
- **Name**: Usually `@` or a specific verification string
- **Value**: A verification string provided by Google

### Option B: Using gcloud CLI

```bash
# Start domain verification
gcloud domains verify stepsquad.club
```

This will provide DNS records to add.

---

## Step 2: Add Verification DNS Records

1. Log in to your domain registrar (where you bought `stepsquad.club`)
2. Navigate to **DNS Management** or **Domain Settings**
3. Add the verification record provided by Google:
   - **Type**: `TXT` or `CNAME`
   - **Name**: As specified by Google
   - **Value**: Verification string from Google
   - **TTL**: 3600 (or default)

4. Wait for DNS propagation (usually 5-30 minutes)
5. Verify in Google Cloud Console that verification is complete

---

## Step 3: Map Domains to Cloud Run Services

### After Verification, Map Domains

**Backend API:**
```bash
gcloud beta run domain-mappings create \
  --service stepsquad-api \
  --domain api.stepsquad.club \
  --region us-central1
```

**Frontend:**
```bash
gcloud beta run domain-mappings create \
  --service stepsquad-web \
  --domain www.stepsquad.club \
  --region us-central1
```

### Or Use Cloud Console

1. Go to **Cloud Run** → **Manage Custom Domains**
2. Click **Add Domain Mapping**
3. Configure:
   - **Domain**: `api.stepsquad.club`
   - **Service**: `stepsquad-api`
   - **Region**: `us-central1`
4. Repeat for `www.stepsquad.club` → `stepsquad-web`

---

## Step 4: Get DNS Records for Domain Mapping

After mapping, Google will provide DNS records (usually CNAME):

**For `api.stepsquad.club`:**
- **Type**: `CNAME`
- **Name**: `api`
- **Value**: `ghs.googlehosted.com` (or value provided by Google)
- **TTL**: 3600

**For `www.stepsquad.club`:**
- **Type**: `CNAME`
- **Name**: `www`
- **Value**: `ghs.googlehosted.com` (or value provided by Google)
- **TTL**: 3600

---

## Step 5: Add DNS Records to Registrar

Add these CNAME records in your domain registrar:

1. Log in to your domain registrar
2. Go to **DNS Management**
3. Add both CNAME records
4. Save changes

---

## Step 6: Wait for DNS Propagation and SSL

- **DNS Propagation**: 1-48 hours (usually 1-2 hours)
- **SSL Certificate**: Automatically provisioned (5-15 minutes after DNS propagation)

---

## Step 7: Verify Everything Works

After DNS propagates and SSL is issued:

```bash
# Test backend
curl https://api.stepsquad.club/health

# Test frontend
curl https://www.stepsquad.club
```

---

## Already Completed ✅

1. ✅ **Backend OAuth redirect URIs updated**:
   - `FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback`
   - `GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback`

2. ✅ **CI/CD workflow updated** to use `https://api.stepsquad.club` for frontend builds

---

## Next Steps

1. **Verify domain ownership** in Google Cloud Console (Step 1-2)
2. **Map domains** to Cloud Run services (Step 3)
3. **Add DNS records** to your registrar (Step 4-5)
4. **Wait for propagation** (Step 6)
5. **Test domains** (Step 7)

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Domain Verification

