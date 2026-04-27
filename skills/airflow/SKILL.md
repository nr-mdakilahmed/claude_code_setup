---
name: airflow
description: >
  Use when creating DAGs, using TaskFlow API, sensors, branching, dynamic tasks,
  or debugging Airflow issues. Covers DAG patterns, idempotency, lazy imports,
  error callbacks, and executor selection.
  Auto-triggers when working with Airflow DAGs or pipeline orchestration.
---

# Airflow DAG Patterns

## TaskFlow API

```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(
    dag_id="daily_etl",
    schedule="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
    },
    tags=["production"],
)
def daily_etl():
    @task
    def extract() -> dict:
        return {"path": "s3://raw/data/", "count": 1000}

    @task
    def transform(data: dict) -> dict:
        return {"path": data["path"].replace("raw", "transformed")}

    @task
    def load(data: dict) -> None:
        pass

    load(transform(extract()))

daily_etl()
```

## Dynamic Task Mapping

```python
@task
def get_partitions() -> list[str]:
    return ["us", "eu", "apac"]

@task
def process(partition: str) -> dict:
    return {"partition": partition, "status": "done"}

results = process.expand(partition=get_partitions())
```

## Decision Guide

| Scenario | Use | Why |
|---|---|---|
| Pure Python ETL | TaskFlow (`@task`) | Cleaner, automatic XCom |
| Provider operators (S3, Snowflake) | Classic operators | Already optimized |
| Short wait (<5 min) | Sensor `mode='poke'` | Less overhead |
| Long/unknown wait | Sensor `mode='reschedule'` | Frees worker slot |
| Deferrable sensor available | `deferrable=True` | Zero worker usage |
| Runtime-determined tasks | `expand()` / dynamic mapping | Parallel execution |
| Config-driven DAG variations | DAG Factory | Loop over YAML configs |

## Critical Rules

- **Lazy imports**: Never import heavy libraries at module level — move inside `@task`
- **Idempotent tasks**: DELETE then INSERT, or MERGE/overwrite by partition
- **No large XCom**: Pass file paths/S3 URIs, never DataFrames
- **Always set retries**: `retries=3, retry_exponential_backoff=True`
- **Always set timeouts**: `timeout` on sensors, `execution_timeout` on tasks
- **Use Connections**: Never hardcode credentials — use `snowflake_conn_id` etc.

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Heavy imports at top level | Lazy imports inside `@task` |
| Processing 10GB in worker | Offload to Snowflake/Spark/external compute |
| No retries | `retries=3` with exponential backoff |
| Large objects in XCom | Pass S3 paths, not data |
| 50 tasks in one DAG | Split into focused DAGs with Dataset triggers |
| Hardcoded connections | Use Airflow Connections (UI or env vars) |
| No timeout on sensors | `timeout=7200, poke_interval=300, mode='reschedule'` |
| `catchup=True` with old start_date | Set `catchup=False` or recent start_date |

## Troubleshooting

| Issue | Fix |
|---|---|
| DAG not appearing | `airflow dags list-import-errors`; check file location |
| Task stuck in queued | Check worker logs; increase `parallelism` / `max_active_tasks_per_dag` |
| Task stuck in scheduled | Verify scheduler running; unpause DAG |
| XCom size exceeded | Pass file paths instead of data; custom XCom backend |
| Import error | Run `python dags/my_dag.py` locally |
| Scheduler lag | Enable lazy imports; reduce top-level computation |
| Task received SIGTERM | Increase worker memory; set `execution_timeout` |
| Duplicate runs | Set `catchup=False`; use recent `start_date` |

## Log Checking Protocol (Kubernetes)

### Quick Task State Check
```bash
# List recent task instances for a DAG
kubectl exec -n <namespace> deploy/airflow-worker -- \
  airflow tasks states-for-dag-run <dag_id> <run_id>

# Check a specific task's state
kubectl exec -n <namespace> deploy/airflow-worker -- \
  airflow tasks state <dag_id> <task_id> <execution_date>
```

### Grep Worker Logs
```bash
# Search logs for errors across all workers
kubectl logs -n <namespace> -l component=worker --tail=500 | grep -i "error\|exception\|failed"

# Follow live logs from a specific worker pod
kubectl logs -n <namespace> <worker-pod-name> -f | grep -i "task_id\|error"
```

### Multi-Date Log Loop
```bash
for dt in $(seq 0 6); do
  DATE=$(date -v-${dt}d +%Y-%m-%d 2>/dev/null || date -d "$dt days ago" +%Y-%m-%d)
  echo "=== $DATE ==="
  kubectl exec -n <namespace> deploy/airflow-worker -- \
    airflow tasks state <dag_id> <task_id> "${DATE}T00:00:00+00:00" 2>/dev/null || echo "not found"
done
```

### Always Check Both Workers
Celery/KubernetesExecutor may run tasks on different worker pods — always check all:
```bash
for pod in $(kubectl get pods -n <namespace> -l component=worker -o name); do
  echo "=== $pod ==="
  kubectl logs -n <namespace> "$pod" --tail=100 | grep -i "error\|exception"
done
```

### Scheduler Logs
```bash
# DAG parse errors surface here, not in task logs
kubectl logs -n <namespace> deploy/airflow-scheduler --tail=200 | grep -i "error\|import\|syntax"
```
