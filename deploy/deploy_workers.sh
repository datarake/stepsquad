#!/usr/bin/env bash
set -euo pipefail
PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-europe-west1}
REPO=${AR_REPO:-stepsquad}
IMAGE="workers"
SERVICE="stepsquad-workers"

gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest apps/workers
gcloud run deploy ${SERVICE} --image ${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest   --region ${REGION} --platform managed   --set-env-vars GCP_ENABLED=true,GOOGLE_CLOUD_PROJECT=${PROJECT},BQ_DATASET=stepsquad,PUBSUB_SUB_INGEST=steps.ingest.sub   --no-allow-unauthenticated
