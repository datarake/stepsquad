# Public Assets

This directory contains public-facing HTML pages for StepSquad.

## Files

- `terms.html` - Terms of Service page
- `privacy.html` - Privacy Policy page

## Hosting Instructions

These pages should be hosted on your domain at:

- `https://stepsquad.club/terms.html` or `https://stepsquad.club/terms`
- `https://stepsquad.club/privacy.html` or `https://stepsquad.club/privacy`

### Option 1: Static Hosting (Recommended)

Upload these files to your web server's public directory:

```bash
# Example: Upload to your web server
scp terms.html privacy.html user@stepsquad.club:/var/www/html/
```

### Option 2: GitHub Pages

If using GitHub Pages:

1. Move these files to `docs/` directory
2. Enable GitHub Pages in repository settings
3. Set custom domain to `stepsquad.club`

### Option 3: Cloud Storage (Google Cloud Storage)

```bash
# Upload to GCS bucket
gsutil cp terms.html gs://your-bucket/terms.html
gsutil cp privacy.html gs://your-bucket/privacy.html

# Make publicly accessible
gsutil acl ch -u AllUsers:R gs://your-bucket/terms.html
gsutil acl ch -u AllUsers:R gs://your-bucket/privacy.html
```

### Option 4: Serve from API (FastAPI)

If your API serves static files, add these routes:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/terms")
async def terms():
    return FileResponse("public/terms.html")

@app.get("/privacy")
async def privacy():
    return FileResponse("public/privacy.html")
```

## URL Configuration

Ensure these URLs are accessible:

- `https://stepsquad.club/terms.html` → `https://stepsquad.club/terms`
- `https://stepsquad.club/privacy.html` → `https://stepsquad.club/privacy`

Configure URL rewrites on your web server if needed (e.g., `.htaccess` for Apache, `nginx.conf` for Nginx).

