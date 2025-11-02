# Add DNS Records to GoDaddy - Step-by-Step

You're currently seeing the DNS record you need to add. Follow these steps:

---

## Current Status ✅

You're mapping `www.stepsquad.club` to `stepsquad-web` service.

**DNS Record to Add:**
- **Name**: `www`
- **Type**: `CNAME`
- **Data**: `ghs.googlehosted.com.`

---

## Step 1: Copy the DNS Record

From the Google Cloud dialog you're currently viewing:

1. **Copy the Data value**: Click the copy icon next to `ghs.googlehosted.com.`
   - Or manually copy: `ghs.googlehosted.com.` (including the trailing dot)

2. **Note the details:**
   - Name: `www`
   - Type: `CNAME`
   - Data: `ghs.googlehosted.com.`

---

## Step 2: Add CNAME Record in GoDaddy

### In GoDaddy:

1. **Open a new tab/window** and go to [GoDaddy.com](https://www.godaddy.com)
2. **Sign In**
3. **Go to My Products**
4. **Find stepsquad.club** and click on it
5. **Click "DNS" tab** or **"Manage DNS"** button

### Add the CNAME Record:

1. Scroll to **CNAME Records** section (or find where to add records)
2. Click **"Add"** or **"+"** button to add a new record
3. Fill in the form:
   - **Type**: Select `CNAME`
   - **Name**: Enter `www`
   - **Value**: Paste `ghs.googlehosted.com.` (with the trailing dot)
   - **TTL**: `600` (10 minutes) or `3600` (1 hour - default)
4. Click **"Save"** or **"Add Record"**

**Important:**
- Make sure to include the **trailing dot** (`.`) at the end of `ghs.googlehosted.com.`
- The Name should be exactly `www` (not `www.stepsquad.club`)

---

## Step 3: Complete Current Mapping

After adding the DNS record in GoDaddy:

1. **Go back to the Google Cloud dialog**
2. Click **"Done"** button (bottom right)
3. The mapping will be created

**Note:** The mapping will show as "Pending" or "Active" after DNS propagates (15-30 minutes).

---

## Step 4: Create Second Mapping (Backend API)

Now you need to map `api.stepsquad.club` to `stepsquad-api`:

1. **In Domain mappings page**, click **"+ Add mapping"** again
2. Fill in:
   - **Domain**: `api.stepsquad.club`
   - **Service**: `stepsquad-api` (or select from dropdown)
   - **Region**: `us-central1`
3. Click **"Create"** or **"Continue"**

**Since domain is already verified**, it should go directly to Step 3 (Update DNS records).

4. **You'll see another DNS record table:**
   - **Name**: `api`
   - **Type**: `CNAME`
   - **Data**: `ghs.googlehosted.com.`

5. **Copy this record** (same process)

---

## Step 5: Add Second CNAME Record in GoDaddy

1. **Go back to GoDaddy DNS Management** (same place as before)
2. Click **"Add"** again to add another CNAME record
3. Fill in:
   - **Type**: `CNAME`
   - **Name**: Enter `api`
   - **Value**: Paste `ghs.googlehosted.com.` (with trailing dot)
   - **TTL**: `600` or `3600`
4. Click **"Save"**

---

## Step 6: Complete Second Mapping

1. **Go back to Google Cloud dialog**
2. Click **"Done"**
3. Second mapping will be created

---

## Step 7: Verify Both DNS Records in GoDaddy

After adding both records, your GoDaddy DNS page should show:

**CNAME Records:**
- `api` → `ghs.googlehosted.com.`
- `www` → `ghs.googlehosted.com.`

**TXT Records** (if still there from verification):
- `@` → `google-site-verification=...` (verification record)

---

## Step 8: Wait for DNS Propagation

- **DNS Propagation**: 15 minutes to 2 hours (usually 15-30 minutes)
- **SSL Certificates**: Automatically provisioned by Google (5-15 minutes after DNS propagates)

You can check status in Google Cloud Console → Domain mappings page:
- Domains will show status as "Active" when ready
- May show "Pending" or "Configuring" until DNS propagates

---

## Step 9: Verify Everything Works

After DNS propagates (wait at least 15-30 minutes):

### Test Backend API:
```bash
curl https://api.stepsquad.club/health
```

**Expected:**
```json
{"ok":true,"time":"...","tz":"Europe/Bucharest","gcp_enabled":true}
```

### Test Frontend:
1. Open `https://www.stepsquad.club` in browser
2. Should load StepSquad web app

---

## Quick Checklist

- [ ] Copy CNAME record for `www` from Google dialog (`ghs.googlehosted.com.`)
- [ ] Add CNAME record in GoDaddy: `www` → `ghs.googlehosted.com.`
- [ ] Click "Done" in Google Cloud dialog for www mapping
- [ ] Click "+ Add mapping" again in Domain mappings page
- [ ] Map `api.stepsquad.club` → `stepsquad-api`
- [ ] Copy CNAME record for `api` (`ghs.googlehosted.com.`)
- [ ] Add CNAME record in GoDaddy: `api` → `ghs.googlehosted.com.`
- [ ] Click "Done" in Google Cloud dialog for api mapping
- [ ] Verify both records in GoDaddy DNS management
- [ ] Wait 15-30 minutes for DNS propagation
- [ ] Test `https://api.stepsquad.club/health`
- [ ] Test `https://www.stepsquad.club`

---

## Summary

**Right now, do this:**

1. **Copy** `ghs.googlehosted.com.` from the Google dialog (click copy icon)
2. **Open GoDaddy** in new tab → My Products → stepsquad.club → DNS
3. **Add CNAME record**:
   - Type: `CNAME`
   - Name: `www`
   - Value: `ghs.googlehosted.com.`
4. **Save** in GoDaddy
5. **Click "Done"** in Google Cloud dialog
6. **Then repeat** for `api.stepsquad.club` mapping

---

**Last Updated**: November 2, 2025  
**Status**: Ready to Add DNS Records

