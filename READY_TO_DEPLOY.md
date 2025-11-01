# Ready to Deploy! ✅

## What's Ready

1. ✅ **GitHub Secrets Configured:**
   - `GCP_PROJECT_ID` = `fluent-coder-476318-n0`
   - `GCP_SA_KEY` = Service Account JSON key

2. ✅ **GCP APIs Enabled:**
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API

3. ✅ **Dockerfiles Exist:**
   - `apps/api/Dockerfile` ✓
   - `apps/web/Dockerfile` ✓

4. ✅ **CI/CD Workflow:**
   - `.github/workflows/deploy.yml` configured

## Next Steps

### Option 1: Test the Workflow (Recommended)

1. **Push a commit to trigger the workflow:**
   ```bash
   git add .
   git commit -m "docs: add GCP setup guides"
   git push origin main
   ```

2. **Or manually trigger in GitHub:**
   - Go to: Actions tab → "Deploy StepSquad to Cloud Run" → "Run workflow"

3. **Monitor the deployment:**
   - Watch the workflow run in GitHub Actions
   - Check for any errors

### Option 2: Verify Prerequisites First

Before deploying, you may want to check:

1. **Firestore indexes** (optional, but recommended):
   - Go to: https://console.cloud.google.com/firestore/indexes?project=fluent-coder-476318-n0
   - Create composite index:
     - Collection: `competitions`
     - Fields: `status` (Ascending), `created_at` (Descending)

2. **Test locally** (optional):
   ```bash
   # Test backend
   cd apps/api
   python -m uvicorn main:app --port 8080

   # Test frontend
   cd apps/web
   npm run dev
   ```

## What the Workflow Will Do

1. **Build API Image** → Push to `gcr.io/fluent-coder-476318-n0/stepsquad-api`
2. **Deploy API** → Cloud Run service `stepsquad-api` in `us-central1`
3. **Build Web Image** → Push to `gcr.io/fluent-coder-476318-n0/stepsquad-web`
4. **Deploy Web** → Cloud Run service `stepsquad-web` in `us-central1`
5. **Test Deployment** → Health checks on both services

## Expected Deployment URLs

After successful deployment:
- **API:** `https://stepsquad-api-xxxxx-uc.a.run.app`
- **Web:** `https://stepsquad-web-xxxxx-uc.a.run.app`

## Troubleshooting

If the workflow fails:
1. Check GitHub Actions logs
2. Verify service account has required permissions
3. Check Cloud Console for error messages
4. See `CICD_TROUBLESHOOTING.md` for common issues

---

**Ready to deploy?** Push a commit or manually trigger the workflow!
