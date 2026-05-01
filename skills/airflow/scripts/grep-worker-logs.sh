#!/usr/bin/env bash
# grep-worker-logs.sh — emits the canonical kubectl command to grep Airflow
# worker logs for a given (run_id, task_id).
#
# This is a printer script: it does not execute kubectl. The operator copies
# the printed command, fills in <namespace> for their deployment, and runs it.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: grep-worker-logs.sh --run-id <id> --task-id <id> [--help]

Prints the canonical kubectl command to grep Airflow worker logs for a
specific run_id and task_id. Replace <namespace> with your Airflow namespace
before executing.

Options:
  --run-id <id>       Airflow DAG run ID (e.g., scheduled__2024-01-15T00:00:00+00:00).
  --task-id <id>      Airflow task ID (e.g., transform_sales).
  --help              Show this message and exit 0.

Example:
  bash grep-worker-logs.sh --run-id scheduled__2024-01-15 --task-id transform_sales
EOF
}

RUN_ID=""
TASK_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --task-id)
      TASK_ID="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$RUN_ID" || -z "$TASK_ID" ]]; then
  echo "error: --run-id and --task-id are both required" >&2
  usage >&2
  exit 2
fi

cat <<EOF
# Canonical kubectl commands — replace <namespace> with your Airflow namespace.

# 1. Grep every worker pod for the run + task
for pod in \$(kubectl get pods -n <namespace> -l component=worker -o name); do
  echo "=== \$pod ==="
  kubectl logs -n <namespace> "\$pod" --tail=500 \\
    | grep -E "${RUN_ID}|${TASK_ID}"
done

# 2. Follow live logs on all workers, filtering for this task
kubectl logs -n <namespace> -l component=worker -f --max-log-requests=10 \\
  | grep -E "${RUN_ID}|${TASK_ID}"

# 3. Scheduler logs (use if the DAG itself failed to parse)
kubectl logs -n <namespace> deploy/airflow-scheduler --tail=200 \\
  | grep -i "error\\|import\\|traceback"

# 4. Task state via Airflow CLI (needs a running worker pod)
kubectl exec -n <namespace> deploy/airflow-worker -- \\
  airflow tasks state <dag_id> ${TASK_ID} ${RUN_ID}

# See references/k8s-log-protocol.md for the full protocol.
EOF
