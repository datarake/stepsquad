#!/usr/bin/env bash
set -euo pipefail
set -x
PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-us-central1}
REPO=${AR_REPO:-stepsquad}
IMAGE="workers"
SERVICE="stepsquad-workers"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC="${ROOT_DIR}/apps/workers"

gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest" "${SRC}"

gcloud run deploy "${SERVICE}" \
  --image "${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest" \
  --region "${REGION}" --platform managed --no-allow-unauthenticated \
  --remove-env-vars=PORT || true

gcloud run deploy "${SERVICE}" \
  --image "${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest" \
  --region "${REGION}" --platform managed --no-allow-unauthenticated \
  --set-env-vars "GCP_ENABLED=true,GOOGLE_CLOUD_PROJECT=${PROJECT},BQ_DATASET=stepsquad,PUBSUB_SUB_INGEST=steps.ingest.sub"
