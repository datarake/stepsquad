# Monitoring & Observability Setup Guide

Complete guide to setting up monitoring, logging, and observability for StepSquad in production.

---

## 📊 Overview

StepSquad uses Google Cloud Platform services for monitoring and observability:
- **Cloud Logging** - Centralized logging
- **Cloud Monitoring** - Metrics and dashboards
- **Cloud Trace** - Distributed tracing (optional)
- **Error Reporting** - Automatic error detection (optional)

---

## 📝 Structured Logging

### Backend Logging

The backend uses Python's `logging` module with structured logging for Cloud Logging.

#### Log Levels

- **DEBUG** - Detailed information for debugging
- **INFO** - General informational messages
- **WARNING** - Warning messages (non-critical errors)
- **ERROR** - Error messages (needs attention)
- **CRITICAL** - Critical errors (requires immediate action)

#### Structured Logging Format

```python
import logging

logging.info(
    "User authenticated",
    extra={
        "user_id": user.uid,
        "email": user.email,
        "role": user.role,
        "action": "login",
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

#### Log Categories

- **Authentication** - Login/logout, token verification
- **Competition Management** - CRUD operations
- **Team Management** - Team creation/join/leave
- **Step Ingestion** - Step submission
- **Leaderboard** - Leaderboard queries
- **User Management** - User CRUD operations
- **System** - Health checks, errors

---

## 🔍 Cloud Logging Setup

### Enable Cloud Logging

Cloud Logging is automatically enabled for Cloud Run services.

### View Logs

```bash
# View all logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# View logs by service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stepsquad-api" --limit 50

# View error logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 50

# View authentication logs
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.action=login" --limit 50
```

### Log Queries

#### Find Authentication Errors

```bash
gcloud logging read 'resource.type=cloud_run_revision AND (
  textPayload=~"Firebase.*token" OR
  textPayload=~"Authentication.*failed" OR
  severity>=ERROR
)' --limit 50
```

#### Find Competition Activity

```bash
gcloud logging read 'resource.type=cloud_run_revision AND (
  jsonPayload.action=~"competition.*" OR
  textPayload=~"competition"
)' --limit 50
```

#### Find Step Ingestion Errors

```bash
gcloud logging read 'resource.type=cloud_run_revision AND (
  jsonPayload.action=~"step.*" OR
  textPayload=~"step.*ingest"
)' --limit 50 --severity>=WARNING
```

---

## 📊 Cloud Monitoring Setup

### Create Dashboard

1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Navigate to **Dashboards**
3. Click **"Create Dashboard"**
4. Add widgets for:
   - Request count
   - Error rate
   - Latency (p50, p95, p99)
   - Memory usage
   - CPU usage
   - Firebase auth errors
   - Competition activity

### Key Metrics

#### Request Metrics

- **Request Count** - Total number of requests
- **Request Rate** - Requests per second
- **Success Rate** - Percentage of successful requests (2xx, 3xx)
- **Error Rate** - Percentage of failed requests (4xx, 5xx)

#### Latency Metrics

- **P50 Latency** - 50th percentile latency
- **P95 Latency** - 95th percentile latency
- **P99 Latency** - 99th percentile latency
- **Average Latency** - Average response time

#### Resource Metrics

- **Memory Usage** - Memory consumption
- **CPU Usage** - CPU utilization
- **Instance Count** - Number of running instances

#### Application Metrics

- **Authentication Errors** - Failed login attempts
- **Competition CRUD Operations** - Create/read/update/delete counts
- **Step Ingestion Rate** - Steps submitted per hour
- **Leaderboard Queries** - Number of leaderboard requests

---

## 🚨 Alerting Setup

### Create Alerts

1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Navigate to **Alerting**
3. Click **"Create Policy"**
4. Add conditions for:
   - Error rate > 5%
   - Latency p95 > 1s
   - Memory usage > 80%
   - CPU usage > 80%
   - Firebase auth failures > 10 per minute
   - Health check failures

### Alert Conditions

#### Error Rate Alert

```
Condition: Error Rate > 5%
Time Window: 5 minutes
Evaluation Frequency: 1 minute
Notification: Email, PagerDuty, Slack
```

#### Latency Alert

```
Condition: P95 Latency > 1 second
Time Window: 5 minutes
Evaluation Frequency: 1 minute
Notification: Email
```

#### Resource Alert

```
Condition: Memory Usage > 80%
Time Window: 5 minutes
Evaluation Frequency: 1 minute
Notification: Email
```

#### Authentication Alert

```
Condition: Firebase Auth Failures > 10 per minute
Time Window: 1 minute
Evaluation Frequency: 30 seconds
Notification: Email, PagerDuty
```

---

## 📈 Health Check Monitoring

### Enhanced Health Endpoint

The `/health` endpoint provides system status:

```json
{
  "ok": true,
  "time": "2025-11-01T12:00:00",
  "tz": "Europe/Bucharest",
  "gcp_enabled": true,
  "firebase_initialized": true,
  "mode": "production"
}
```

### Monitor Health Checks

```bash
# Check health endpoint
curl https://your-api-url.run.app/health

# Monitor health status
gcloud logging read 'resource.type=cloud_run_revision AND textPayload=~"health"' --limit 10
```

### Alert on Health Failures

```
Condition: Health Check Failures (ok=false)
Time Window: 1 minute
Evaluation Frequency: 30 seconds
Notification: Email, PagerDuty
```

---

## 🔐 Security Monitoring

### Monitor Authentication

1. **Failed Login Attempts**
   - Track failed authentication attempts
   - Alert on suspicious activity
   - Set threshold: > 10 failures per minute from same IP

2. **Token Verification Failures**
   - Track invalid/expired tokens
   - Alert on token verification errors
   - Monitor for token replay attacks

3. **Unauthorized Access Attempts**
   - Track 401/403 errors
   - Alert on repeated unauthorized access
   - Monitor for privilege escalation attempts

### Monitor API Access

1. **Rate Limiting**
   - Track API request rates
   - Alert on excessive requests
   - Monitor for DDoS attacks

2. **Unusual Activity**
   - Track competition creation/deletion
   - Alert on bulk operations
   - Monitor for data exfiltration

---

## 📊 Log-Based Metrics

### Create Log-Based Metrics

1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Navigate to **Metrics**
3. Click **"Create Metric"**
4. Select **"Log-based metric"**
5. Define metric:
   - **Type**: Counter, Distribution, or Gauge
   - **Log Filter**: `resource.type=cloud_run_revision AND textPayload=~"pattern"`
   - **Value Extraction**: Extract numeric values if needed

### Example Metrics

#### Authentication Errors Metric

```
Type: Counter
Log Filter: resource.type=cloud_run_revision AND textPayload=~"Authentication.*failed"
Metric Name: authentication_errors
```

#### Competition Creation Metric

```
Type: Counter
Log Filter: resource.type=cloud_run_revision AND jsonPayload.action="create_competition"
Metric Name: competitions_created
```

#### Step Ingestion Metric

```
Type: Counter
Log Filter: resource.type=cloud_run_revision AND jsonPayload.action="ingest_steps"
Metric Name: steps_ingested
```

---

## 🎯 Custom Metrics

### Track Custom Metrics

Use Cloud Monitoring API to track custom metrics:

```python
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import MetricServiceClient
import time

def track_custom_metric(metric_name: str, value: float, labels: dict = None):
    """Track custom metric in Cloud Monitoring"""
    client = MetricServiceClient()
    project_id = os.getenv("GCP_PROJECT_ID")
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_name}"
    series.resource.type = "cloud_run_revision"
    series.resource.labels["service_name"] = "stepsquad-api"
    series.resource.labels["revision_name"] = "stepsquad-api-001"
    
    point = monitoring_v3.Point()
    point.value.double_value = value
    point.interval.end_time.seconds = int(time.time())
    
    if labels:
        for key, value in labels.items():
            series.metric.labels[key] = str(value)
    
    series.points = [point]
    
    client.create_time_series(
        name=f"projects/{project_id}",
        time_series=[series]
    )
```

### Example Usage

```python
# Track step ingestion
track_custom_metric("steps_ingested", steps_count, {
    "comp_id": comp_id,
    "user_id": user_id
})

# Track competition creation
track_custom_metric("competitions_created", 1, {
    "created_by": admin_email
})
```

---

## 📋 Monitoring Checklist

Before production deployment, verify:

- [ ] Cloud Logging enabled
- [ ] Dashboard created with key metrics
- [ ] Alerts configured for critical errors
- [ ] Health check monitoring set up
- [ ] Authentication monitoring configured
- [ ] Log-based metrics created
- [ ] Custom metrics tracked (if needed)
- [ ] Notification channels configured (email, PagerDuty, Slack)
- [ ] Alert policies tested
- [ ] Log retention configured (30 days recommended)

---

## 🔍 Troubleshooting

### No Logs Appearing

1. Check service account has logging permissions
2. Verify Cloud Logging API is enabled
3. Check log retention settings

### Metrics Not Showing

1. Verify metrics are being sent
2. Check metric filters are correct
3. Wait 2-3 minutes for metrics to appear

### Alerts Not Firing

1. Check alert conditions are correct
2. Verify notification channels are configured
3. Test alert manually

---

## 📚 Additional Resources

- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Cloud Trace Documentation](https://cloud.google.com/trace/docs)
- [Alerting Policies](https://cloud.google.com/monitoring/alerts)
- [Log-Based Metrics](https://cloud.google.com/logging/docs/logs-based-metrics)

---

**Last Updated**: November 1, 2025

