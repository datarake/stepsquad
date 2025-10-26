#!/usr/bin/env bash
set -euo pipefail
PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-europe-west1}
REPO=${AR_REPO:-stepsquad}
IMAGE="api"
SERVICE="stepsquad-api"

gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest apps/api
gcloud run deploy ${SERVICE} --image ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest   --region ${REGION} --platform managed --allow-unauthenticated   --set-env-vars GCP_ENABLED=true,GOOGLE_CLOUD_PROJECT=${PROJECT},BQ_DATASET=stepsquad,PUBSUB_TOPIC_INGEST=steps.ingest,COMP_TZ=Europe/Bucharest,GRACE_DAYS=2,PORT=8004   --port 8004
