# How to Find Google Verification String

This guide shows you exactly where to find the domain verification string in Google Cloud Console.

---

## Where to Find It

### Option 1: When Adding Domain Mapping

When you click **"+ Add mapping"** and try to map a domain:

1. **Click "+ Add mapping"** in Domain mappings page
2. Enter domain: `api.stepsquad.club` (or `www.stepsquad.club`)
3. Select service: `stepsquad-api` (or `stepsquad-web`)
4. Click **"Create"** or **"Continue"**

**If domain is not verified:**
- Google will show a dialog/page with **domain verification options**
- Look for **"Verify domain ownership"** or **"Add a verification record"**
- The verification string will be displayed there

### Option 2: Direct Domain Verification

1. In **Domain mappings** page, look for a **"Verify Domain"** button or link
2. Or click **"+ Verify Domain"** button (if visible)
3. Enter your domain: `stepsquad.club`
4. Click **"Start Verification"** or **"Verify"**
5. Google will provide verification options

**Verification options include:**
- **HTML file** upload
- **TXT record** (DNS) ← **Use this one**
- **HTML tag**
- **Google Analytics**

**Choose "TXT record"** - this will show you the verification string.

---

## What the Verification String Looks Like

The verification string will look something like:

```
google-site-verification=AbCdEf123456GhIjKlMnOpQrStUvWxYz7890123456789
```

Or it might be shown as:

**Type:** `TXT`
**Name:** `@` (or `google-site-verification`)
**Value:** `google-site-verification=AbCdEf123456GhIjKlMnOpQrStUvWxYz7890123456789`

**Important:**
- Copy the **entire** string (including `google-site-verification=`)
- No spaces before or after
- Usually 60-80 characters long

---

## Step-by-Step: Finding It Now

### From Domain Mappings Page:

1. **Make sure you're on the Domain mappings page** (Cloud Run → Domain mappings)
2. **Look for one of these:**
   - **"Verify Domain"** button (top of page or in empty state)
   - **"+ Verify Domain"** button
   - **"Verify"** link next to domain list
3. **Click it** and enter `stepsquad.club`
4. **Choose "TXT record" verification method**
5. **Copy the verification string** shown

### Alternative: Through Domain Mapping Flow:

1. Click **"+ Add mapping"**
2. Enter domain: `api.stepsquad.club`
3. Select service
4. Click **"Create"**
5. **If verification is required**, Google will show a page with:
   - Instructions
   - **The verification record** (TXT record details)
   - Copy the **Value** field (the full string)

---

## Visual Guide: What You Should See

**In the verification page/dialog, you should see:**

```
Verify domain ownership

Choose a verification method:
○ HTML file
● TXT record (Recommended) ← Select this
○ HTML tag
○ Google Analytics

Add the following TXT record to your domain's DNS settings:

Type: TXT
Name: @
Value: google-site-verification=AbCdEf123456GhIjKlMnOpQrStUvWxYz7890123456789
TTL: 3600
```

**Copy the Value:** `google-site-verification=AbCdEf123456GhIjKlMnOpQrStUvWxYz7890123456789`

---

## If You Don't See Verification String

### Try These Steps:

1. **Check if verification already exists:**
   - Look for any existing verification records in Google Cloud Console
   - Domain mappings page might show verification status

2. **Try a different verification method:**
   - HTML file upload (if your domain has web hosting)
   - Google Analytics (if you have GA set up)

3. **Use gcloud CLI to get verification string:**
   ```bash
   # This might trigger verification
   gcloud beta run domain-mappings create \
     --service stepsquad-api \
     --domain api.stepsquad.club \
     --region us-central1
   ```
   The error output might include verification instructions.

4. **Check Search Console (if previously verified):**
   - If domain was verified for Google Search Console before
   - The verification might carry over
   - Check: https://search.google.com/search-console

---

## Quick Actions You Can Try

### Action 1: Direct Verification Link

In Google Cloud Console, try:
1. Go to **Cloud Run** → **Domain mappings**
2. Look for **"Verify Domain"** button (should be visible on empty state)
3. Click it
4. Enter: `stepsquad.club`
5. Select **"TXT record"** method
6. Copy the verification string

### Action 2: Through Search Console

If you have Google Search Console:
1. Go to https://search.google.com/search-console
2. Add property: `stepsquad.club`
3. Choose **"Domain"** verification
4. Select **"TXT record"** method
5. Copy the verification string shown

**Note:** Search Console verification might work for Cloud Run domain mappings too.

---

## What to Copy Exactly

When you find the verification string, copy **everything** shown:

```
google-site-verification=AbCdEf123456GhIjKlMnOpQrStUvWxYz7890123456789
```

**Do NOT copy:**
- ❌ Just the part after `=` 
- ❌ With extra spaces
- ❌ Only `AbCdEf...` (missing the prefix)

**DO copy:**
- ✅ The entire string from `google-site-verification=` to the end
- ✅ Exactly as shown (case-sensitive)
- ✅ No spaces or line breaks

---

## If Still Can't Find It

### Contact/Alternative Methods:

1. **Use HTML file verification** (if you have web hosting):
   - Download the HTML file
   - Upload to your website's root directory
   - Verify through file

2. **Check if domain was verified elsewhere:**
   - Google Search Console
   - Google Workspace
   - Other Google services

3. **Use gcloud CLI to get more details:**
   ```bash
   # List domain mappings
   gcloud beta run domain-mappings list --region us-central1
   
   # Try creating mapping to trigger verification
   gcloud beta run domain-mappings create \
     --service stepsquad-api \
     --domain api.stepsquad.club \
     --region us-central1 \
     --verbose
   ```

---

## After You Have the Verification String

1. **Copy it completely** (from `google-site-verification=` to end)
2. **Go to GoDaddy** → My Products → stepsquad.club → DNS
3. **Add TXT record**:
   - Type: `TXT`
   - Name: `@`
   - Value: [paste the full verification string]
4. **Save**
5. **Wait 15-30 minutes**
6. **Re-verify in Google Cloud Console**

---

**Last Updated**: November 2, 2025  
**Status**: Guide for Finding Verification String

