#!/usr/bin/env bash
set -euo pipefail
set -x

PROJECT=${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}
REGION=${GCP_REGION:-europe-west1}
REPO=${AR_REPO:-stepsquad}
IMAGE="web"
SERVICE="stepsquad-web"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC="${ROOT_DIR}/apps/web"

API_URL="$(gcloud run services describe stepsquad-api --region "${GCP_REGION:-europe-west1}" --format 'value(status.url)')"

gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest" "${SRC}"

gcloud run deploy "${SERVICE}" \
  --image "${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE}:latest" \
  --region "${REGION}" --platform managed --allow-unauthenticated \
  --set-env-vars "VITE_API_BASE_URL=${API_URL}"
