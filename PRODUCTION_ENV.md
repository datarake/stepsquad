# Production Environment Configuration

## Backend API Environment Variables

### Required
```bash
GCP_ENABLED=true
COMP_TZ=Europe/Bucharest
```

### Optional
```bash
ADMIN_EMAIL=admin@stepsquad.com
BQ_DATASET=stepsquad
PUBSUB_TOPIC_INGEST=steps-ingest
PUBSUB_SUB_INGEST=steps-sub
GRACE_DAYS=2
```

### Service Account
- Cloud Run service account needs:
  - `Cloud Datastore User` role (for Firestore)
  - `Firebase Admin` role (for Firebase Admin SDK)
  - Secret Manager access (if using secrets)

---

## Frontend Web Environment Variables

### Required (Build-time)
```env
VITE_API_BASE_URL=https://your-api-url.run.app
VITE_USE_DEV_AUTH=false
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

**Important**: Frontend environment variables must be set at **build time** because Vite embeds them in the bundle.

---

## Cloud Run Configuration

### Backend API
- **Memory**: 512Mi (minimum)
- **CPU**: 1 (or higher for better performance)
- **Port**: 8080
- **Min Instances**: 0 (for cost savings)
- **Max Instances**: 10 (adjust based on load)
- **Timeout**: 300s (default)

### Frontend Web
- **Memory**: 256Mi (sufficient for Nginx)
- **CPU**: 1
- **Port**: 8080
- **Min Instances**: 0
- **Max Instances**: 5

---

## Security Best Practices

1. **Use Secret Manager** for sensitive values (API keys, credentials)
2. **Enable Cloud Armor** for DDoS protection
3. **Set up IAM** properly - least privilege principle
4. **Enable Cloud Logging** for audit trails
5. **Use HTTPS** (default for Cloud Run)
6. **Set CORS** properly (only allow your frontend domain)
7. **Enable Cloud CDN** for frontend static assets
8. **Use Cloud Load Balancing** for high availability

---

## Scaling Configuration

### Backend
- **CPU Allocation**: Always allocate (for consistent performance)
- **Concurrency**: 80 requests per instance (default)
- **Auto-scaling**: Based on CPU/memory usage

### Frontend
- **Static serving**: Nginx serves static files efficiently
- **CDN**: Use Cloud CDN for global distribution

---

## Monitoring Setup

### Cloud Monitoring
1. Go to **Cloud Monitoring** → **Dashboards**
2. Create dashboard with:
   - Request count
   - Error rate
   - Latency (p50, p95, p99)
   - Memory/CPU usage

### Alerting
Create alerts for:
- Error rate > 5%
- Latency p95 > 1s
- Memory usage > 80%
- CPU usage > 80%

### Logging
- All logs automatically go to Cloud Logging
- Query with: `resource.type="cloud_run_revision"`
- Set up log-based metrics for error tracking

---

## Backup & Recovery

### Firestore Backup
```bash
# Manual backup
gcloud firestore export gs://your-bucket/firestore-backup

# Scheduled backups (via Cloud Scheduler)
gcloud scheduler jobs create firestore-backup \
  --schedule="0 2 * * *" \
  --time-zone="Europe/Bucharest" \
  --description="Daily Firestore backup"
```

### Disaster Recovery
1. Keep service account keys secure
2. Document all environment variables
3. Maintain infrastructure as code
4. Regular backups of Firestore data

---

**Last Updated**: November 1, 2025
