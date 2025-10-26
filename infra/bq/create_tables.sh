#!/usr/bin/env bash
set -euo pipefail
: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
DATASET="${1:-stepsquad}"
bq query --use_legacy_sql=false --parameter=DATASET::${DATASET} "$(cat create_tables.sql | sed 's/`\${DATASET}`/'\'${DATASET}\''/g)"
echo "Created dataset and tables in ${DATASET}"
