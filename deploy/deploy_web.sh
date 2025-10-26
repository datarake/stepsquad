#!/usr/bin/env bash
set -euo pipefail
PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-europe-west1}
REPO=${AR_REPO:-stepsquad}
IMAGE="web"
SERVICE="stepsquad-web"

gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest apps/web
gcloud run deploy ${SERVICE} --image ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest   --region ${REGION} --platform managed --allow-unauthenticated   --set-env-vars VITE_API_BASE_URL=https://YOUR_API_URL
