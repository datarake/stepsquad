# Domain Mapping - Click-by-Click Guide

Based on your current view of the Domain mappings page.

---

## Step 1: Create First Domain Mapping (Backend API)

### Click "+ Add mapping" button (top right)

You'll see a form or dialog to create a domain mapping.

### Fill in the form:

1. **Domain**: Enter `api.stepsquad.club`
2. **Service**: Select `stepsquad-api` from the dropdown
3. **Region**: Should show `us-central1` (or select it)
4. **Platform**: Should show `managed` (default)

### Click "Create" or "Continue"

**What happens next:**

**Option A: Domain verification required**
- Google will show you verification DNS records
- You need to add these to your registrar first
- See "Domain Verification" section below

**Option B: Direct to DNS records**
- Google will provide DNS records (CNAME) for the mapping
- Copy these records
- See "Add DNS Records" section below

---

## Step 2: Verify Domain (If Required)

If Google asks you to verify the domain first:

1. **Copy the verification record** provided by Google:
   - Usually a TXT record
   - Format: `Name: @` or verification string, `Value: verification string`

2. **Go to your domain registrar** (where you bought `stepsquad.club`):
   - Log in
   - Go to **DNS Management** or **Domain Settings**
   - Add the verification record:
     - **Type**: `TXT`
     - **Name**: As specified (usually `@` or verification string)
     - **Value**: The verification string from Google
     - **TTL**: 3600 (or default)
   - Save changes

3. **Wait 5-30 minutes** for DNS propagation

4. **Return to Google Cloud Console** and click "Verify" or wait for automatic verification

5. **After verification**, proceed with domain mapping again

---

## Step 3: Get DNS Records for Domain Mapping

After creating the mapping (or after verification), Google will provide DNS records:

**For `api.stepsquad.club`:**
- **Type**: `CNAME`
- **Name**: `api`
- **Value**: `ghs.googlehosted.com` (or value provided by Google)
- **TTL**: 3600

**Save these values** - you'll need them for your registrar.

---

## Step 4: Create Second Domain Mapping (Frontend)

1. Click **"+ Add mapping"** again
2. Fill in:
   - **Domain**: `www.stepsquad.club`
   - **Service**: `stepsquad-web`
   - **Region**: `us-central1`
   - **Platform**: `managed`
3. Click **"Create"**

Google will provide DNS records:
- **Type**: `CNAME`
- **Name**: `www`
- **Value**: `ghs.googlehosted.com` (or value provided)

---

## Step 5: Add DNS Records to Your Registrar

Go to your domain registrar and add both CNAME records:

**In your DNS Management:**

1. **Record 1: Backend**
   - Type: `CNAME`
   - Name: `api`
   - Value: `ghs.googlehosted.com` (or value from Google)
   - TTL: 3600

2. **Record 2: Frontend**
   - Type: `CNAME`
   - Name: `www`
   - Value: `ghs.googlehosted.com` (or value from Google)
   - TTL: 3600

3. **Optional: Root Domain Redirect**
   - To redirect `stepsquad.club` → `www.stepsquad.club`
   - Use your registrar's URL redirect feature (if available)
   - Or add an A record pointing to the same value as www

4. **Save changes**

---

## Step 6: Wait for DNS Propagation

- **DNS Propagation**: 1-48 hours (usually 1-2 hours)
- **SSL Certificate**: Automatically provisioned by Google (5-15 minutes after DNS propagates)

You can check status in the Domain mappings page - the domain will show status as "Active" when ready.

---

## Step 7: Verify Everything Works

After DNS propagates:

**Test Backend:**
```bash
curl https://api.stepsquad.club/health
```

Expected:
```json
{"ok":true,"time":"...","tz":"Europe/Bucharest","gcp_enabled":true}
```

**Test Frontend:**
- Open `https://www.stepsquad.club` in browser
- Should load the StepSquad web app

---

## What You Should See

After completing mappings, your Domain mappings page should show:

| Domain | Mapped to | Date added | Added by | Actions |
|--------|-----------|------------|----------|---------|
| api.stepsquad.club | stepsquad-api | [date] | [your account] | [actions] |
| www.stepsquad.club | stepsquad-web | [date] | [your account] | [actions] |

---

## Troubleshooting

**"Domain not verified" error:**
- Complete domain verification first (Step 2)
- Add verification DNS record to registrar
- Wait for verification to complete

**Can't see services in dropdown:**
- Make sure services exist and are deployed
- Check you're in the correct project
- Refresh the page

**DNS records not provided:**
- Domain mapping might still be creating
- Wait a few minutes and refresh
- Check domain verification status

---

**Last Updated**: November 2, 2025  
**Status**: Ready to Map Domains

