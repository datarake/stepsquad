# Quick Domain Setup Guide

## Step-by-Step Instructions

### Step 1: Go to Domain Mappings

From the Cloud Run Services page you're currently on:

1. **Click "Domain mappings"** in the left sidebar (under Cloud Run section)
2. You'll see a page to manage custom domains

---

### Step 2: Verify Domain Ownership (First Time Only)

If you haven't verified `stepsquad.club` yet:

1. Click **"Verify Domain"** or **"+ Verify Domain"**
2. Enter your domain: `stepsquad.club`
3. Click **Start Verification**
4. Google will provide **verification DNS records** (usually TXT record)
5. Copy these DNS records

**Then in your domain registrar:**
1. Log in to where you bought `stepsquad.club`
2. Go to **DNS Management** or **Domain Settings**
3. Add the **verification record** provided by Google:
   - Type: `TXT` (or as specified)
   - Name: As specified by Google (usually `@` or verification string)
   - Value: The verification string from Google
   - TTL: 3600 (or default)
4. Save changes
5. Wait 5-30 minutes for DNS propagation
6. Return to Google Cloud Console and verify it's complete

---

### Step 3: Map Backend Domain (api.stepsquad.club)

After domain is verified:

1. Click **"+ Add Domain Mapping"** or **"Create Domain Mapping"**
2. Configure:
   - **Domain**: `api.stepsquad.club`
   - **Service**: Select `stepsquad-api` from dropdown
   - **Region**: `us-central1`
   - **Platform**: `managed`
3. Click **Continue** or **Create**
4. Google will provide **DNS records** (usually CNAME):
   - Type: `CNAME`
   - Name: `api`
   - Value: `ghs.googlehosted.com` (or value provided)

---

### Step 4: Map Frontend Domain (www.stepsquad.club)

1. Click **"+ Add Domain Mapping"** again
2. Configure:
   - **Domain**: `www.stepsquad.club`
   - **Service**: Select `stepsquad-web` from dropdown
   - **Region**: `us-central1`
   - **Platform**: `managed`
3. Click **Continue** or **Create**
4. Google will provide **DNS records** (usually CNAME):
   - Type: `CNAME`
   - Name: `www`
   - Value: `ghs.googlehosted.com` (or value provided)

---

### Step 5: Add DNS Records to Your Registrar

For each domain mapping, add the DNS records provided:

**In your domain registrar:**

1. Log in to your domain registrar
2. Go to **DNS Management**
3. Add **both CNAME records**:

   **Record 1: Backend**
   - Type: `CNAME`
   - Name: `api`
   - Value: `ghs.googlehosted.com` (or value from Google)
   - TTL: 3600

   **Record 2: Frontend**
   - Type: `CNAME`
   - Name: `www`
   - Value: `ghs.googlehosted.com` (or value from Google)
   - TTL: 3600

4. **Optional: Root Domain Redirect**
   - To redirect `stepsquad.club` → `www.stepsquad.club`:
   - Most registrars have a URL redirect feature (use that)
   - Or add A record pointing to same value as www

5. Save changes

---

### Step 6: Wait for DNS Propagation and SSL

- **DNS Propagation**: 1-48 hours (usually 1-2 hours)
- **SSL Certificate**: Automatically provisioned by Google (5-15 minutes after DNS propagates)

---

### Step 7: Verify Everything Works

Once DNS propagates and SSL is issued:

**Test Backend:**
```bash
curl https://api.stepsquad.club/health
```

**Expected response:**
```json
{"ok":true,"time":"...","tz":"Europe/Bucharest","gcp_enabled":true}
```

**Test Frontend:**
- Open `https://www.stepsquad.club` in browser
- Should load the StepSquad web app

---

## Visual Guide

**From Services page:**
1. Look at **left sidebar** → Click **"Domain mappings"**
2. You'll see a page with domain management options
3. Click **"+ Verify Domain"** (if needed)
4. Then **"+ Add Domain Mapping"** for each domain

---

## What's Already Done ✅

- ✅ Backend OAuth redirect URIs updated to use `api.stepsquad.club`
- ✅ CI/CD workflow configured to use custom domain
- ✅ All services deployed in `us-central1` only
- ✅ Services ready for domain mapping

---

## Troubleshooting

**"Domain not verified" error:**
- Go to **Domain mappings** → **Verify Domain** first
- Add verification DNS record to registrar
- Wait for verification to complete

**Domain mapping not working:**
- Verify DNS records are correct in registrar
- Wait for DNS propagation (can take up to 48 hours)
- Check that SSL certificate is issued (automatic, takes 5-15 minutes)

**Can't find "Domain mappings":**
- Make sure you're in **Cloud Run** section (left sidebar)
- Click on **"Domain mappings"** link

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Domain Mapping

