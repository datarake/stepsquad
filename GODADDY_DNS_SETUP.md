# GoDaddy DNS Setup Guide - StepSquad

This guide will help you add DNS records to your GoDaddy domain for StepSquad.

---

## Step 1: Log In to GoDaddy

1. Go to [GoDaddy.com](https://www.godaddy.com)
2. Click **Sign In** (top right)
3. Enter your credentials

---

## Step 2: Access DNS Management

### Method 1: From My Products

1. After logging in, click **My Products** (top navigation)
2. Find **stepsquad.club** in your domain list
3. Click on **stepsquad.club**
4. Scroll down and click **DNS** tab or **Manage DNS** button

### Method 2: Quick Access

1. Go to **My Products** → **Domains**
2. Find **stepsquad.club**
3. Click the **DNS** button or **Manage** → **DNS**

---

## Step 3: Add Verification TXT Record

You need to add the **verification TXT record** that Google provided.

### Locate the Verification Record

From the Google Cloud Console error/verification page:
- **Type**: `TXT`
- **Name**: Usually `@` or a verification string like `google-site-verification=...`
- **Value**: A long verification string provided by Google
- **TTL**: `600` seconds (or 1 hour)

### Add Record in GoDaddy

1. In GoDaddy DNS Management page, scroll to **Records** section
2. Find the **TXT Records** section (or click **Add** button)
3. Click **Add** or **+** button to add a new record
4. Fill in:
   - **Type**: Select `TXT`
   - **Name**: Enter `@` (for root domain) or the name specified by Google
   - **Value**: Paste the **entire verification string** from Google (including `google-site-verification=` part)
   - **TTL**: `600` (1 hour) or `3600` (default)
5. Click **Save** or **Add Record**

**Important Notes:**
- The **Value** field might have a character limit - if your verification string is very long, ensure you paste it completely
- Make sure there are **no extra spaces** before or after the value
- The value should start with `google-site-verification=...` and include the entire string

---

## Step 4: Wait for DNS Propagation

- **DNS Propagation**: Can take 5 minutes to 48 hours (usually 15-60 minutes)
- GoDaddy DNS changes typically propagate within **15-30 minutes**

### Check DNS Propagation

You can verify the record is live using online tools:

```bash
# Using dig command (if you have it)
dig TXT stepsquad.club

# Or use online tools:
# - https://www.whatsmydns.net/#TXT/stepsquad.club
# - https://dnschecker.org/#TXT/stepsquad.club
```

The verification record should appear in the results.

---

## Step 5: Re-verify in Google Cloud

After DNS propagation (wait at least 15-30 minutes):

1. **Go back to Google Cloud Console**
2. Navigate to **Cloud Run** → **Domain mappings**
3. **Try verification again**:
   - If you see a "Verify" button, click it
   - Or start the domain mapping process again
   - Google will check for the TXT record again

**If verification succeeds:**
- You'll see a success message
- You can proceed with domain mapping

**If verification still fails:**
- Wait longer (DNS can take up to 48 hours)
- Double-check the TXT record in GoDaddy:
  - Correct type (TXT)
  - Correct name (@)
  - Complete value (full verification string)
  - No extra spaces

---

## Step 6: Add Domain Mappings (After Verification)

Once verification succeeds:

### Backend API Mapping

1. Click **"+ Add mapping"**
2. Fill in:
   - **Domain**: `api.stepsquad.club`
   - **Service**: `stepsquad-api`
   - **Region**: `us-central1`
3. Click **Create**
4. Google will provide **CNAME record**:
   - Type: `CNAME`
   - Name: `api`
   - Value: `ghs.googlehosted.com` (or value provided)

### Frontend Mapping

1. Click **"+ Add mapping"** again
2. Fill in:
   - **Domain**: `www.stepsquad.club`
   - **Service**: `stepsquad-web`
   - **Region**: `us-central1`
3. Click **Create**
4. Google will provide **CNAME record**:
   - Type: `CNAME`
   - Name: `www`
   - Value: `ghs.googlehosted.com` (or value provided)

---

## Step 7: Add CNAME Records in GoDaddy

For each domain mapping, add the CNAME record in GoDaddy:

### Add CNAME Record 1: Backend (api)

1. In GoDaddy DNS Management
2. Find **CNAME Records** section
3. Click **Add** or **+**
4. Fill in:
   - **Type**: `CNAME`
   - **Name**: `api`
   - **Value**: `ghs.googlehosted.com` (or value from Google)
   - **TTL**: `600` (or default)
5. Click **Save**

### Add CNAME Record 2: Frontend (www)

1. Click **Add** again
2. Fill in:
   - **Type**: `CNAME`
   - **Name**: `www`
   - **Value**: `ghs.googlehosted.com` (or value from Google)
   - **TTL**: `600` (or default)
3. Click **Save**

### Optional: Root Domain Redirect

To redirect `stepsquad.club` to `www.stepsquad.club`:

**Option A: URL Redirect (Recommended in GoDaddy)**

1. In GoDaddy, go to **My Products** → **Domains** → **stepsquad.club**
2. Look for **Forwarding** or **Redirect** section
3. Enable forwarding:
   - Forward `stepsquad.club` → `https://www.stepsquad.club`
   - Set as **Permanent (301)** redirect

**Option B: A Record**

1. Add A record pointing to same IP as www (less common)

---

## Step 8: Verify DNS Records in GoDaddy

After adding all records, your GoDaddy DNS page should show:

**TXT Records:**
- `@` → `google-site-verification=...` (verification record)

**CNAME Records:**
- `api` → `ghs.googlehosted.com` (or Google's value)
- `www` → `ghs.googlehosted.com` (or Google's value)

---

## Step 9: Wait for DNS Propagation

- **CNAME Records**: 15 minutes to 2 hours (usually 15-30 minutes)
- **SSL Certificates**: Automatically provisioned by Google (5-15 minutes after DNS propagates)

---

## Step 10: Test Your Domains

After DNS propagates:

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

---

## Troubleshooting

### Verification TXT Record Not Found

**Common Issues:**

1. **Record not saved properly:**
   - Double-check you clicked "Save" or "Add Record"
   - Verify record appears in GoDaddy DNS list

2. **Wrong name:**
   - Use `@` for root domain verification
   - Some verifications use a specific subdomain name

3. **Incomplete value:**
   - Ensure you copied the **entire** verification string
   - Check for any character limits in GoDaddy's form
   - No extra spaces or line breaks

4. **DNS not propagated:**
   - Wait 15-30 minutes minimum
   - Check with DNS lookup tools:
     - https://www.whatsmydns.net/#TXT/stepsquad.club
     - https://dnschecker.org/#TXT/stepsquad.club

5. **TXT record format:**
   - Should include `google-site-verification=` prefix
   - Value should be the complete string Google provided

### CNAME Records Not Working

1. **Check record exists in GoDaddy:**
   - Verify both `api` and `www` CNAME records are saved

2. **Wait for propagation:**
   - Can take up to 2 hours
   - Check with: `dig CNAME api.stepsquad.club`

3. **Verify values:**
   - Both should point to `ghs.googlehosted.com` (or Google's provided value)
   - No typos in the value

---

## Quick Reference: GoDaddy DNS Record Types

When adding records in GoDaddy:

- **TXT**: For verification records
- **CNAME**: For subdomain mappings (api, www)
- **A**: For IP addresses (usually not needed here)
- **@**: Means root domain (stepsquad.club)
- **Subdomain name**: `api`, `www`, etc.

---

## Step-by-Step Checklist

- [ ] Log in to GoDaddy
- [ ] Go to DNS Management for stepsquad.club
- [ ] Add verification TXT record (`@` → verification string)
- [ ] Wait 15-30 minutes for DNS propagation
- [ ] Re-verify domain in Google Cloud Console
- [ ] Create domain mappings in Google Cloud:
  - [ ] Map `api.stepsquad.club` → `stepsquad-api`
  - [ ] Map `www.stepsquad.club` → `stepsquad-web`
- [ ] Get CNAME records from Google
- [ ] Add CNAME records in GoDaddy:
  - [ ] `api` → `ghs.googlehosted.com`
  - [ ] `www` → `ghs.googlehosted.com`
- [ ] Wait 1-2 hours for DNS propagation
- [ ] Test domains:
  - [ ] `https://api.stepsquad.club/health`
  - [ ] `https://www.stepsquad.club`

---

**Last Updated**: November 2, 2025  
**Status**: GoDaddy DNS Setup Guide

