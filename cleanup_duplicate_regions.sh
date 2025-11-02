#!/usr/bin/env bash
set -euo pipefail

# Script to delete duplicate Cloud Run services in europe-west1
# Keeping only us-central1 deployments

REGION_TO_DELETE="europe-west1"
REGION_TO_KEEP="us-central1"

SERVICES=("stepsquad-api" "stepsquad-web" "stepsquad-workers" "stepsquad-agents")

echo "🗑️  Deleting duplicate services in ${REGION_TO_DELETE}..."
echo "✅ Keeping services in ${REGION_TO_KEEP}"
echo ""

for SERVICE in "${SERVICES[@]}"; do
    echo "Checking ${SERVICE} in ${REGION_TO_DELETE}..."
    
    # Check if service exists in europe-west1
    if gcloud run services describe "${SERVICE}" --region="${REGION_TO_DELETE}" &>/dev/null; then
        echo "  ❌ Found ${SERVICE} in ${REGION_TO_DELETE}"
        echo "  🗑️  Deleting..."
        
        # Delete the service
        if gcloud run services delete "${SERVICE}" \
            --region="${REGION_TO_DELETE}" \
            --quiet; then
            echo "  ✅ Deleted ${SERVICE} from ${REGION_TO_DELETE}"
        else
            echo "  ⚠️  Failed to delete ${SERVICE} from ${REGION_TO_DELETE}"
        fi
    else
        echo "  ✅ ${SERVICE} not found in ${REGION_TO_DELETE} (already cleaned up)"
    fi
    
    # Verify service exists in us-central1
    if gcloud run services describe "${SERVICE}" --region="${REGION_TO_KEEP}" &>/dev/null; then
        echo "  ✅ ${SERVICE} exists in ${REGION_TO_KEEP}"
    else
        echo "  ⚠️  Warning: ${SERVICE} not found in ${REGION_TO_KEEP}"
    fi
    
    echo ""
done

echo "✅ Cleanup complete!"
echo ""
echo "Current services:"
gcloud run services list --format="table(metadata.name,status.url)" | grep stepsquad

