# Custom Domain Setup - StepSquad

This guide will configure:
- **Frontend**: `https://www.stepsquad.club` → Cloud Run service `stepsquad-web`
- **Backend API**: `https://api.stepsquad.club` → Cloud Run service `stepsquad-api`

---

## Current Setup

### Deployed Services

**Backend API:**
- US Central: `https://stepsquad-api-okzm4oijzq-uc.a.run.app`
- Europe West: `https://stepsquad-api-okzm4oijzq-ew.a.run.app`

**Frontend Web:**
- US Central: `https://stepsquad-web-okzm4oijzq-uc.a.run.app`
- Europe West: `https://stepsquad-web-okzm4oijzq-ew.a.run.app`

---

## Step 1: Map Backend API Domain (`api.stepsquad.club`)

### Using Cloud Console (Easiest)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Run** → **Manage Custom Domains**
3. Click **Add Domain Mapping**
4. Configure:
   - **Domain**: `api.stepsquad.club`
   - **Region**: `us-central1` (or your preferred region)
   - **Service**: `stepsquad-api`
   - Click **Continue**
5. Google will provide DNS records to add

### Using gcloud CLI

```bash
# Map domain to Cloud Run service
gcloud run domain-mappings create \
  --service stepsquad-api \
  --domain api.stepsquad.club \
  --region us-central1 \
  --platform managed
```

### Get DNS Records

After mapping, get the DNS records:

```bash
gcloud run domain-mappings describe api.stepsquad.club \
  --region us-central1 \
  --format="value(status.resourceRecords)"
```

You'll see output like:
```
name: api.stepsquad.club
type: CNAME
rrdata: ghs.googlehosted.com.
```

---

## Step 2: Map Frontend Domain (`www.stepsquad.club`)

### Using Cloud Console

1. Go to **Cloud Run** → **Manage Custom Domains**
2. Click **Add Domain Mapping**
3. Configure:
   - **Domain**: `www.stepsquad.club`
   - **Region**: `us-central1`
   - **Service**: `stepsquad-web`
   - Click **Continue**

### Using gcloud CLI

```bash
gcloud run domain-mappings create \
  --service stepsquad-web \
  --domain www.stepsquad.club \
  --region us-central1 \
  --platform managed
```

### Get DNS Records

```bash
gcloud run domain-mappings describe www.stepsquad.club \
  --region us-central1 \
  --format="value(status.resourceRecords)"
```

---

## Step 3: Update DNS Records

In your domain registrar (where you bought `stepsquad.club`), add the DNS records provided by Google Cloud.

### Example DNS Records

**Backend (`api.stepsquad.club`):**
```
Type: CNAME
Name: api
Value: ghs.googlehosted.com
TTL: 3600
```

**Frontend (`www.stepsquad.club`):**
```
Type: CNAME
Name: www
Value: ghs.googlehosted.com
TTL: 3600
```

**Optional: Root Domain Redirect (`stepsquad.club` → `www.stepsquad.club`):**
```
Type: A
Name: @
Value: [IP address] (or use URL redirect in registrar)
```

### Where to Add DNS Records

1. Log in to your domain registrar
2. Navigate to **DNS Management** or **Domain Settings**
3. Find **DNS Records** or **Manage DNS**
4. Add the CNAME records provided by Google Cloud

---

## Step 4: Wait for DNS Propagation

- DNS changes can take 1-48 hours to propagate (usually 1-2 hours)
- SSL certificates are automatically provisioned by Google Cloud (takes 5-15 minutes)

### Verify DNS Propagation

```bash
# Check if DNS records are set
dig api.stepsquad.club
dig www.stepsquad.club
```

### Verify SSL Certificate

```bash
# Check if SSL certificate is issued (after 5-15 minutes)
curl -I https://api.stepsquad.club/health
curl -I https://www.stepsquad.club
```

---

## Step 5: Update Frontend to Use Custom API Domain

The frontend needs to be rebuilt with the new API URL.

### Step 5.1: Update Frontend Environment Variables

Create `apps/web/.env.production`:

```bash
VITE_API_BASE_URL=https://api.stepsquad.club
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration
VITE_FIREBASE_API_KEY=AIzaSyBAPgF7xzHOqKgGG8HkWgArtM4Luc_au1M
VITE_FIREBASE_AUTH_DOMAIN=stepsquad-46d14.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=stepsquad-46d14
VITE_FIREBASE_STORAGE_BUCKET=stepsquad-46d14.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=451432804996
VITE_FIREBASE_APP_ID=1:451432804996:web:72718bbe41e597a69008d1
VITE_FIREBASE_MEASUREMENT_ID=G-RDWR6NK1EN
```

### Step 5.2: Rebuild and Redeploy Frontend

**Option A: Update CI/CD (Recommended)**

Update `.github/workflows/deploy.yml` to use the custom domain:

```yaml
# In the frontend build step, set:
env:
  VITE_API_BASE_URL: https://api.stepsquad.club
```

Then push to trigger redeployment:
```bash
git add .github/workflows/deploy.yml
git commit -m "chore: update frontend API URL to custom domain"
git push origin main
```

**Option B: Manual Rebuild and Deploy**

```bash
cd apps/web

# Build with production environment
pnpm build

# Deploy to Cloud Run (if using source-based deployment)
cd ../..
gcloud run deploy stepsquad-web \
  --source apps/web \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_BASE_URL=https://api.stepsquad.club,VITE_USE_DEV_AUTH=false"
```

**Option C: Update Existing Service**

If you're using a Dockerfile-based deployment, rebuild the image with the new environment variable:

```bash
# Build with new API URL
cd apps/web
docker build --build-arg VITE_API_BASE_URL=https://api.stepsquad.club -t gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest .

# Push and deploy
docker push gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest
gcloud run deploy stepsquad-web \
  --image gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest \
  --region us-central1
```

---

## Step 6: Update Backend CORS (if needed)

If your backend has CORS restrictions, ensure it allows requests from `https://www.stepsquad.club`:

Check `apps/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.stepsquad.club",
        "https://stepsquad.club",
        "http://localhost:5174",  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Update if needed:
```bash
cd apps/api
# Edit main.py to add custom domain to allow_origins
```

---

## Step 7: Update OAuth Redirect URIs

### Fitbit

1. Go to [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Edit your application
3. Update **Redirect URI** to: `https://api.stepsquad.club/oauth/fitbit/callback`
4. Save changes

### Garmin

1. Go to [Garmin Developer Portal](https://developer.garmin.com/)
2. Edit your OAuth client
3. Update **Callback URL** to: `https://api.stepsquad.club/oauth/garmin/callback`
4. Save changes

### Update Environment Variables

Update your backend environment variables:

```bash
gcloud run services update stepsquad-api \
  --update-env-vars="FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback,GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback" \
  --region us-central1
```

---

## Step 8: Test Everything

### Test Backend

```bash
# Health check
curl https://api.stepsquad.club/health

# Should return:
# {"ok":true,"time":"...","tz":"Europe/Bucharest","gcp_enabled":true}
```

### Test Frontend

1. Open `https://www.stepsquad.club` in browser
2. Verify it loads correctly
3. Check browser console for API calls (should go to `api.stepsquad.club`)
4. Test login functionality
5. Test API endpoints

### Test OAuth

1. Go to `https://www.stepsquad.club/devices`
2. Click "Connect Fitbit" or "Connect Garmin"
3. Verify redirect goes to correct domain
4. Complete OAuth flow
5. Verify callback redirects back correctly

---

## Quick Commands Reference

### Map Domains
```bash
# Backend
gcloud run domain-mappings create \
  --service stepsquad-api \
  --domain api.stepsquad.club \
  --region us-central1

# Frontend
gcloud run domain-mappings create \
  --service stepsquad-web \
  --domain www.stepsquad.club \
  --region us-central1
```

### List Domain Mappings
```bash
gcloud run domain-mappings list --region us-central1
```

### Get DNS Records
```bash
gcloud run domain-mappings describe api.stepsquad.club --region us-central1
gcloud run domain-mappings describe www.stepsquad.club --region us-central1
```

### Update Backend Environment Variables
```bash
gcloud run services update stepsquad-api \
  --update-env-vars="FITBIT_REDIRECT_URI=https://api.stepsquad.club/oauth/fitbit/callback,GARMIN_REDIRECT_URI=https://api.stepsquad.club/oauth/garmin/callback" \
  --region us-central1
```

---

## Troubleshooting

### DNS Not Propagating

1. Check DNS records are correct in your registrar
2. Use `dig` or `nslookup` to verify DNS resolution
3. Wait up to 48 hours for full propagation

### SSL Certificate Not Issued

1. Verify DNS records are correct
2. Wait 5-15 minutes after DNS propagation
3. Check Cloud Run domain mapping status in console
4. Ensure domain is accessible and resolving correctly

### Frontend Can't Reach Backend

1. Check `VITE_API_BASE_URL` is set correctly in frontend build
2. Verify CORS settings in backend allow `www.stepsquad.club`
3. Check browser console for CORS errors
4. Verify both domains are accessible

### OAuth Callbacks Failing

1. Verify redirect URIs are updated in Fitbit/Garmin apps
2. Check environment variables are set correctly
3. Verify callback URLs match exactly (including https)
4. Check backend logs for OAuth errors

---

## Next Steps After Setup

1. ✅ Test all functionality with custom domains
2. ✅ Update any hardcoded URLs in code
3. ✅ Update documentation with new URLs
4. ✅ Set up monitoring for both domains
5. ✅ Configure backup/restore procedures
6. ✅ Set up CDN if needed (for frontend static assets)

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Domain Configuration

