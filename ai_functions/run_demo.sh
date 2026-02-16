#!/bin/bash
# Run 7-Eleven AI Functions demo notebooks via Databricks CLI
# Uses ~/.databrickscfg (profile: fieldeng)
# Prerequisites: Valid token in databrickscfg, catalog 'renjiharold_demo' exists

set -e
PROFILE="${1:-fieldeng}"
WORKSPACE_PATH="/ai_functions_demo"  # Workspace path; adjust if needed
AI_FUNCTIONS_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1. Importing notebooks to workspace ==="
databricks workspace mkdirs "$WORKSPACE_PATH" -p "$PROFILE" 2>/dev/null || true

databricks workspace import "$WORKSPACE_PATH/01_setup_7eleven_demo_data" \
  --file "$AI_FUNCTIONS_DIR/01_setup_7eleven_demo_data.sql.ipynb" \
  --format JUPYTER --language SQL --overwrite -p "$PROFILE"

databricks workspace import "$WORKSPACE_PATH/02_ai_functions_demo" \
  --file "$AI_FUNCTIONS_DIR/02_ai_functions_demo.sql.ipynb" \
  --format JUPYTER --language SQL --overwrite -p "$PROFILE"

echo "=== 2. Submitting job to run notebooks ==="
# Get first available cluster (or set CLUSTER_ID manually)
CLUSTER_ID=$(databricks clusters list -p "$PROFILE" -o json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
clusters = data.get('clusters', [])
for c in clusters:
    if c.get('state') == 'RUNNING':
        print(c['cluster_id'])
        sys.exit(0)
print('', file=sys.stderr)
sys.exit(1)
" 2>/dev/null) || true

if [ -z "$CLUSTER_ID" ]; then
  echo "No running cluster found. Create a job with a new cluster instead."
  echo "Example: Create a job in the Databricks UI that runs:"
  echo "  - $WORKSPACE_PATH/01_setup_7eleven_demo_data"
  echo "  - $WORKSPACE_PATH/02_ai_functions_demo (after 01)"
  echo ""
  echo "Or start a cluster and set: export CLUSTER_ID=<your-cluster-id>"
  exit 0
fi

# Submit one-time run: setup first, then demo
databricks jobs submit -p "$PROFILE" --json "{
  \"run_name\": \"7-Eleven AI Functions Setup\",
  \"tasks\": [
    {
      \"task_key\": \"setup_data\",
      \"notebook_task\": {
        \"notebook_path\": \"$WORKSPACE_PATH/01_setup_7eleven_demo_data\"
      },
      \"existing_cluster_id\": \"$CLUSTER_ID\"
    },
    {
      \"task_key\": \"ai_functions_demo\",
      \"depends_on\": [{\"task_key\": \"setup_data\"}],
      \"notebook_task\": {
        \"notebook_path\": \"$WORKSPACE_PATH/02_ai_functions_demo\"
      },
      \"existing_cluster_id\": \"$CLUSTER_ID\"
    }
  ]
}"

echo "Job submitted. Check run status in the Databricks UI."
