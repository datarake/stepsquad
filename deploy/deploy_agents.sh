#!/usr/bin/env bash
set -euo pipefail
PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-europe-west1}
REPO=${AR_REPO:-stepsquad}
IMAGE="agents"
SERVICE="stepsquad-agents"

gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest apps/agents
gcloud run deploy ${SERVICE} --image ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest   --region ${REGION} --platform managed --no-allow-unauthenticated   --set-env-vars PORT=8004   --port 8004
