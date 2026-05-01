# Kubernetes Log Access Protocol for Airflow

Full command set for accessing Airflow logs in a Kubernetes deployment. Read only when the inline troubleshooting table does not resolve the issue, or when a user reports a task failure on K8s-deployed Airflow.

## Contents

- Overview: what lives in which pod
- Scheduler pod logs (DAG parse errors)
- Worker pod logs (task runtime errors)
- Multi-pod fan-out (Celery / Kubernetes executor)
- Task-state inspection via `kubectl exec`
- Multi-date state loop (rerun/backfill debugging)
- Executor-specific differences
- Worker pod log paths on disk
- Common namespace and label conventions
- Escalation: when logs alone are not enough

## Overview: what lives in which pod

| Log source | What it contains | Pod selector |
|---|---|---|
| Scheduler | DAG parse errors, import errors, scheduler health | `deploy/airflow-scheduler` or `-l component=scheduler` |
| Webserver | UI access logs, auth errors | `deploy/airflow-webserver` or `-l component=webserver` |
| Worker (Celery) | Task runtime stdout/stderr | `-l component=worker` |
| Worker (K8s executor) | One pod per task; short-lived | `-l dag_id=<dag>,task_id=<task>` |
| Triggerer | Deferrable operator callbacks | `deploy/airflow-triggerer` or `-l component=triggerer` |

If a DAG does not show up in the UI, check **scheduler** logs. If a task failed, check **worker** (or per-task) logs. If a deferrable sensor is stuck, check **triggerer** logs.

## Scheduler pod logs (DAG parse errors)

DAG parse errors never appear in task logs — they surface in the scheduler.

```bash
# Last 200 lines filtered for errors
kubectl logs -n <namespace> deploy/airflow-scheduler --tail=200 \
  | grep -i "error\|import\|syntax\|traceback"

# Follow live parse activity
kubectl logs -n <namespace> deploy/airflow-scheduler -f \
  | grep -i "error\|import"

# From a specific DAG file name
kubectl logs -n <namespace> deploy/airflow-scheduler --tail=500 \
  | grep -A 20 "<dag_filename>.py"
```

Also available via the Airflow CLI:

```bash
kubectl exec -n <namespace> deploy/airflow-scheduler -- \
  airflow dags list-import-errors
```

## Worker pod logs (task runtime errors)

```bash
# All worker pods, recent errors
kubectl logs -n <namespace> -l component=worker --tail=500 \
  | grep -i "error\|exception\|failed\|traceback"

# Follow live logs on a specific worker pod
kubectl logs -n <namespace> <worker-pod-name> -f \
  | grep -i "<dag_id>\|<task_id>"

# Logs since a time window
kubectl logs -n <namespace> -l component=worker --since=1h \
  | grep "<run_id>"
```

## Multi-pod fan-out (Celery / Kubernetes executor)

Celery and KubernetesExecutor distribute tasks across many pods. One pod's logs are rarely enough.

```bash
# Iterate every worker pod, grep each
for pod in $(kubectl get pods -n <namespace> -l component=worker -o name); do
  echo "=== $pod ==="
  kubectl logs -n <namespace> "$pod" --tail=200 \
    | grep -i "<task_id>\|error"
done
```

For the Kubernetes executor specifically, each task gets its own pod and the pod is deleted by default after completion:

```bash
# Find pods for a specific DAG + task (need labels; confirm your chart's label scheme)
kubectl get pods -n <namespace> -l dag_id=<dag_id>,task_id=<task_id>

# Describe a failed pod if it is still around
kubectl describe pod -n <namespace> <pod-name>
```

If pods are auto-deleted, set `delete_worker_pods=False` in the config, or enable remote logging (S3/GCS/Elasticsearch) so the logs survive pod cleanup.

## Task-state inspection via `kubectl exec`

```bash
# List task-instance states for a specific run
kubectl exec -n <namespace> deploy/airflow-worker -- \
  airflow tasks states-for-dag-run <dag_id> <run_id>

# State of one task at one execution date
kubectl exec -n <namespace> deploy/airflow-worker -- \
  airflow tasks state <dag_id> <task_id> <execution_date>

# Rerender logs from the metadata DB via CLI
kubectl exec -n <namespace> deploy/airflow-worker -- \
  airflow tasks test <dag_id> <task_id> <execution_date>
```

## Multi-date state loop (rerun/backfill debugging)

Useful when a task fails only for some logical dates:

```bash
for dt in $(seq 0 6); do
  DATE=$(date -v-${dt}d +%Y-%m-%d 2>/dev/null || date -d "$dt days ago" +%Y-%m-%d)
  echo "=== $DATE ==="
  kubectl exec -n <namespace> deploy/airflow-worker -- \
    airflow tasks state <dag_id> <task_id> "${DATE}T00:00:00+00:00" \
    2>/dev/null || echo "not found"
done
```

## Executor-specific differences

| Executor | Log location | Quirk |
|---|---|---|
| `LocalExecutor` | Scheduler pod (combined) | Everything goes to the scheduler pod's stdout |
| `CeleryExecutor` | Many long-lived worker pods | Task logs on whichever pod picked it up — iterate all workers |
| `KubernetesExecutor` | One pod per task, often deleted | Enable remote logging (S3/GCS) or `delete_worker_pods=False` |
| `CeleryKubernetesExecutor` | Mix of above | Check `queue` on the task to know which system ran it |

## Worker pod log paths on disk

Inside a worker pod, task logs are at:

```
/opt/airflow/logs/dag_id=<dag>/run_id=<run>/task_id=<task>/attempt=<n>.log
```

Useful when `kubectl logs` is truncated by the container runtime:

```bash
kubectl exec -n <namespace> <worker-pod> -- \
  ls -la /opt/airflow/logs/dag_id=<dag_id>/run_id=<run_id>/

kubectl exec -n <namespace> <worker-pod> -- \
  cat /opt/airflow/logs/dag_id=<dag_id>/run_id=<run_id>/task_id=<task_id>/attempt=1.log
```

## Common namespace and label conventions

Different Helm charts label pods differently. Verify with one of:

```bash
kubectl get pods -n <namespace> --show-labels | head -5
```

Typical selectors:

- Official Airflow chart: `component=scheduler|worker|webserver|triggerer`, `release=<release-name>`
- Astronomer: `component=...`, `tier=airflow`
- Custom: check your chart's values file

Replace `<namespace>` in all examples — common values are `airflow`, `data`, or a product-specific namespace.

## Escalation: when logs alone are not enough

If logs do not explain the failure:

1. **Pod events**: `kubectl describe pod -n <ns> <pod>` — shows OOM kills, image pull failures, volume mount errors.
2. **Node pressure**: `kubectl top nodes` and `kubectl top pods -n <ns>` — worker may be resource-starved.
3. **Metadata DB**: task-instance row may reveal state transitions not in logs (ask a platform engineer).
4. **Triggerer queue**: deferrable tasks that hang — check triggerer logs and Redis/queue backend health.
