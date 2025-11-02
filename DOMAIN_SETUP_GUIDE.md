# Domain Setup Guide - StepSquad

This guide will help you configure:
- **Frontend**: `https://www.stepsquad.club` (React app)
- **Backend API**: `https://api.stepsquad.club` (FastAPI)

---

## Overview

### Current Setup
- **Backend API**: Deployed on Google Cloud Run (already configured)
- **Frontend**: Needs to be deployed (React build from `apps/web`)

### Required Services
1. **Cloud Run** - For backend API (already deployed)
2. **Cloud Run** or **Cloud Storage + Cloud CDN** - For frontend
3. **Cloud Load Balancer** (recommended) or **Cloud Run Custom Domains** - For custom domain mapping
4. **Google Domains DNS** or **Cloud DNS** - For DNS configuration

---

## Part 1: Backend API Setup (`api.stepsquad.club`)

### Option A: Cloud Run Custom Domains (Easiest)

This is the simplest way to map a custom domain to your Cloud Run service.

#### Step 1: Verify Domain Ownership

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Run** → **Manage Custom Domains**
3. Click **Add Domain Mapping**
4. Enter your domain: `api.stepsquad.club`
5. Select your Cloud Run service: `stepsquad-api`
6. Click **Continue**
7. Google will provide DNS records (CNAME or A records) to add to your domain

#### Step 2: Update DNS Records

In your domain registrar (where you bought `stepsquad.club`):

1. Add the DNS records provided by Google Cloud
2. Typically:
   - **Type**: `CNAME` or `A`
   - **Name**: `api`
   - **Value**: The value provided by Google Cloud (e.g., `ghs.googlehosted.com` or an IP address)

#### Step 3: SSL Certificate

Google Cloud automatically provisions SSL certificates for custom domains. Wait 5-15 minutes for the certificate to be issued.

#### Step 4: Verify

After DNS propagation (can take up to 48 hours, usually 1-2 hours):

```bash
curl https://api.stepsquad.club/health
```

### Option B: Cloud Load Balancer (More Control)

If you need more control or want to use both frontend and backend through a load balancer:

1. Go to **Cloud Load Balancing**
2. Create a new load balancer
3. Configure backend service pointing to your Cloud Run service
4. Configure frontend with your domain
5. Update DNS records as provided

---

## Part 2: Frontend Setup (`www.stepsquad.club`)

You have several options for hosting the React frontend:

### Option A: Cloud Run (Recommended - Same Platform)

Host your frontend on Cloud Run for consistency and easy scaling.

#### Step 1: Build Frontend

```bash
cd apps/web
pnpm install
pnpm build
```

This creates a `dist/` directory with static files.

#### Step 2: Create Dockerfile for Frontend

Create `apps/web/Dockerfile`:

```dockerfile
FROM nginx:alpine

# Copy built files
COPY dist/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Create `apps/web/nginx.conf`:

```nginx
server {
    listen 80;
    server_name www.stepsquad.club stepsquad.club;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

#### Step 3: Build and Push Docker Image

```bash
# Build image
cd apps/web
docker build -t gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest
```

#### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy stepsquad-web \
  --image gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80
```

#### Step 5: Map Custom Domain

1. Go to **Cloud Run** → **Manage Custom Domains**
2. Click **Add Domain Mapping**
3. Enter: `www.stepsquad.club`
4. Select service: `stepsquad-web`
5. Add DNS records as provided

### Option B: Cloud Storage + Cloud CDN (Cheaper, More Complex)

Host static files in Cloud Storage with Cloud CDN for better performance.

#### Step 1: Build Frontend

```bash
cd apps/web
pnpm build
```

#### Step 2: Create Cloud Storage Bucket

```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://www.stepsquad.club

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://www.stepsquad.club

# Upload files
gsutil -m cp -r dist/* gs://www.stepsquad.club/
```

#### Step 3: Configure Bucket for Website Hosting

```bash
# Set bucket website configuration
echo '{"mainPageSuffix": "index.html", "notFoundPage": "index.html"}' > website-config.json
gsutil web set -m index.html -e index.html gs://www.stepsquad.club
```

#### Step 4: Set Up Cloud Load Balancer

1. Go to **Cloud Load Balancing**
2. Create HTTP(S) Load Balancer
3. Configure:
   - **Backend**: Cloud Storage bucket (`www.stepsquad.club`)
   - **Frontend**: HTTPS with domain `www.stepsquad.club`
   - **SSL Certificate**: Create or use existing

#### Step 5: Update DNS

Add A record pointing to the load balancer IP address.

### Option C: Firebase Hosting (Easiest for Frontend)

Firebase Hosting is very easy for React apps and integrates well with Firebase Authentication.

#### Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

#### Step 2: Initialize Firebase

```bash
cd apps/web
firebase init hosting
```

#### Step 3: Configure Firebase

- **Public directory**: `dist`
- **Single-page app**: Yes
- **Set up automatic builds**: Yes (optional)

#### Step 4: Build and Deploy

```bash
pnpm build
firebase deploy --only hosting
```

#### Step 5: Configure Custom Domain

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Hosting** → **Add Custom Domain**
4. Enter: `www.stepsquad.club`
5. Add DNS records as provided

---

## Part 3: DNS Configuration

### Required DNS Records

In your domain registrar (where you bought `stepsquad.club`), add:

#### For Cloud Run Custom Domains:

1. **Backend** (`api.stepsquad.club`):
   - **Type**: `CNAME` or `A`
   - **Name**: `api`
   - **Value**: Provided by Google Cloud (e.g., `ghs.googlehosted.com`)

2. **Frontend** (`www.stepsquad.club`):
   - **Type**: `CNAME` or `A`
   - **Name**: `www`
   - **Value**: Provided by Google Cloud or Firebase

#### For Cloud Load Balancer:

1. **Backend** (`api.stepsquad.club`):
   - **Type**: `A`
   - **Name**: `api`
   - **Value**: Load balancer IP address

2. **Frontend** (`www.stepsquad.club`):
   - **Type**: `A`
   - **Name**: `www`
   - **Value**: Load balancer IP address

### Root Domain (stepsquad.club)

You may also want to redirect `stepsquad.club` to `www.stepsquad.club`:

- **Type**: `A`
- **Name**: `@`
- **Value**: Same as `www` record

Or set up redirect in your hosting solution.

---

## Part 4: Environment Variables Update

After setting up domains, update your frontend environment variables:

### Frontend Environment Variables

Create `apps/web/.env.production`:

```bash
VITE_API_BASE_URL=https://api.stepsquad.club
VITE_USE_DEV_AUTH=false
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
VITE_FIREBASE_APP_ID=your_firebase_app_id
```

### Backend Environment Variables

Update Cloud Run service:

```bash
gcloud run services update stepsquad-api \
  --update-env-vars="GCP_ENABLED=true,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
  --region us-central1
```

---

## Part 5: Verify Setup

### Test Backend

```bash
# Health check
curl https://api.stepsquad.club/health

# Test endpoint
curl https://api.stepsquad.club/
```

### Test Frontend

1. Open `https://www.stepsquad.club` in browser
2. Verify it loads correctly
3. Test API calls from frontend
4. Test authentication flow

---

## Part 6: Recommended Architecture

For production, I recommend:

```
Frontend (www.stepsquad.club)
  ↓
  Cloud Run (nginx serving React build)
  OR
  Firebase Hosting (easiest)
  OR
  Cloud Storage + Cloud CDN (cheapest)

Backend (api.stepsquad.club)
  ↓
  Cloud Run (FastAPI)
  ↓
  Firestore, Pub/Sub, etc.
```

---

## Quick Start Commands

### Deploy Backend (if not already deployed)

```bash
# Already done via CI/CD, but manual command:
cd apps/api
gcloud run deploy stepsquad-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Deploy Frontend (Cloud Run)

```bash
# Build
cd apps/web
pnpm build

# Create Dockerfile (see Option A above)
# Build and push image
docker build -t gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest .
docker push gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest

# Deploy
gcloud run deploy stepsquad-web \
  --image gcr.io/YOUR_PROJECT_ID/stepsquad-web:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80
```

### Map Custom Domains

1. Go to **Cloud Run** → **Manage Custom Domains**
2. Add `api.stepsquad.club` → `stepsquad-api`
3. Add `www.stepsquad.club` → `stepsquad-web`

---

## Cost Estimate

- **Cloud Run**: Pay per request (very cheap for low traffic)
- **Firebase Hosting**: Free tier available, then pay as you go
- **Cloud Storage + CDN**: Pay per GB stored and transferred (very cheap)
- **Cloud Load Balancer**: ~$18/month base cost (only if using Load Balancer)

**Recommendation**: Start with **Cloud Run for backend** and **Firebase Hosting for frontend** - both are very cost-effective for small to medium traffic.

---

## Next Steps

1. ✅ Choose frontend hosting option (I recommend Firebase Hosting for simplicity)
2. ✅ Build and deploy frontend
3. ✅ Map custom domains in Cloud Run
4. ✅ Update DNS records in your domain registrar
5. ✅ Update environment variables
6. ✅ Test both domains
7. ✅ Update Terms/Privacy URLs to use `stepsquad.club`

---

**Last Updated**: November 2, 2025  
**Status**: Ready for Setup

