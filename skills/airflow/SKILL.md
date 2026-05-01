---
name: airflow
description: Writes, reviews, and debugs Apache Airflow DAGs at data-engineering standards. Enforces TaskFlow API, idempotency, lazy imports, deferrable sensors, and failure callbacks. Triggers when writing DAGs, using the TaskFlow API, configuring sensors or branching, investigating DAG import errors, or debugging task failures in Kubernetes-deployed Airflow.
when_to_use: Auto-triggers when editing files under dags/ or plugins/, or when the user mentions Airflow orchestration, executor selection, XCom, dynamic task mapping, or scheduler parse errors.
paths:
  - "**/dags/**/*.py"
  - "**/plugins/**/*.py"
  - "airflow.cfg"
---

# Airflow DAG Patterns

Turns Claude into a data-pipeline reviewer for Airflow: enforces idempotent tasks, module-load hygiene, deferrable sensors over blocking pokes, failure callbacks, and Kubernetes log access before guessing at task failures.

**Freedom level: High** — DAG design admits many shapes. The skill directs judgment with principles and a decision table, not fixed recipes.

## 1. DAGs Are Idempotent

**Re-running a task for the same logical date must produce the same result.**

- DELETE-then-INSERT, MERGE, or partition-overwrite — never append-without-key.
- Parameterize every SQL on `{{ ds }}` or `{{ data_interval_start }}`; never `CURRENT_DATE`.
- Name targets deterministically (`dt=2024-01-15` partition), not by wall-clock.
- "Append new rows" → "MERGE on `(date, id)` or overwrite partition `dt={{ ds }}`".

## 2. Lazy Imports In Tasks

**Top-level imports run on every scheduler parse — heavy imports stall the whole scheduler.**

- Import `pandas`, `pyspark`, `tensorflow`, cloud SDKs **inside** the `@task` function.
- `Variable.get()` and `Connection.get()` go inside tasks, not at module scope.
- Keep the module body to: decorators, DAG definition, task wiring — nothing that touches I/O or heavy libs.
- "top-level `import pandas as pd`" → "move `import pandas as pd` inside the `@task` body".

## 3. Sensors Block; Deferrable Frees

**A poking sensor holds a worker slot for hours. A deferrable operator holds nothing.**

- Prefer `deferrable=True` when the operator supports it (most 2.7+ provider sensors do).
- If no deferrable variant exists, use `mode='reschedule'` + `poke_interval >= 60`.
- Always set `timeout` — unbounded sensors fill the queue.
- "`S3KeySensor(mode='poke')` for 4h wait" → "`S3KeySensor(deferrable=True)` or `mode='reschedule'`".

## 4. Callbacks For Failure

**Silent task failures become 3 AM pages. Wire callbacks at DAG creation.**

- Set `on_failure_callback` for Slack/PagerDuty; `sla_miss_callback` for latency SLOs.
- Set `retries=3, retry_exponential_backoff=True, retry_delay=timedelta(minutes=5)` in `default_args`.
- Set `execution_timeout` on every task — no task should hang forever.
- Log structured context (`dag_id`, `task_id`, `run_id`) in the callback body.

## 5. K8s Logs First

**When a task fails on a Kubernetes-deployed Airflow, read the logs before theorizing.**

- Scheduler pod logs show DAG parse errors; worker pod logs show task runtime errors.
- Celery/KubernetesExecutor spreads tasks across worker pods — check all of them.
- See `references/k8s-log-protocol.md` for the full kubectl command set; use `scripts/grep-worker-logs.sh` to emit the canonical command.

## Quick reference

The single decision lookup consulted on every invocation.

| Scenario | Use | Why |
|---|---|---|
| Pure Python ETL | TaskFlow (`@task`) | Clean syntax, automatic XCom |
| Cloud provider ops (S3, Snowflake, GCS) | Classic operators (`SQLExecuteQueryOperator`, `GCSToGCSOperator`, `KubernetesPodOperator`) | Already optimized, battle-tested |
| Long wait, deferrable available | `deferrable=True` | Zero worker-slot cost |
| Long wait, no deferrable | Sensor `mode='reschedule'` + `timeout` | Frees slot between pokes |
| Runtime-determined fan-out | `.expand()` dynamic mapping | Parallel, dependency-aware |

## Feedback loop

1. Write or edit the DAG.
2. **Validate immediately**: `bash scripts/check-dag-import.sh --dag-file dags/<file>.py` (AST + Airflow import check).
3. If import fails: read the traceback, fix, rerun the check.
4. After deploy: `kubectl logs -n <ns> deploy/airflow-scheduler --tail=200 | grep -i "error\|import"` for parse errors; `scripts/grep-worker-logs.sh` for runtime errors.
5. Loop until both scheduler parse and first task run are clean.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Heavy `import` at module top | Move inside the `@task` body |
| Large DataFrame in XCom | Pass S3/GCS URI; use custom XCom backend for real state |
| `Variable.get("x")` at module scope | Move inside the task function |
| `catchup=True` with old `start_date` | `catchup=False` or a recent `start_date` |
| Hardcoded DB password in DAG | Airflow Connection via `conn_id` |
| Sensor `mode='poke'` for multi-hour wait | `deferrable=True`, or `mode='reschedule'` |
| 50 unrelated tasks in one DAG | Split into focused DAGs wired by `Dataset` triggers |

## Troubleshooting

| Symptom | Fix |
|---|---|
| DAG not appearing in UI | `airflow dags list-import-errors`; check scheduler pod logs |
| DAG parse error at import | Run `scripts/check-dag-import.sh --dag-file <path>`; read traceback |
| Task stuck in `queued` | Worker logs; raise `parallelism` / `max_active_tasks_per_dag` |
| Task stuck in `scheduled` | Scheduler not running, or DAG paused — unpause, check scheduler pod |
| Task received SIGTERM | Raise worker memory limits; set `execution_timeout` to a sane value |
| `XCom too large` | Pass file path or S3 URI; configure custom XCom backend |
| Scheduler CPU pinned | Lazy-import rule violated — move heavy imports into tasks |
| Duplicate DAG runs on first deploy | `catchup=False` and bump `start_date` forward |
| Task ran on wrong executor/queue | Check `executor_config` and `queue` on the operator |
| Kubernetes pod stuck `Pending` | `kubectl describe pod` — usually image pull, resource quota, or node selector |

## Executor selection

| Executor | Use when |
|---|---|
| `LocalExecutor` | Single-node dev; ≤50 concurrent tasks |
| `CeleryExecutor` | Steady workload, predictable concurrency, Redis/RabbitMQ available |
| `KubernetesExecutor` | Bursty workload, per-task isolation, resource-heavy tasks |
| `CeleryKubernetesExecutor` | Mix: default Celery, route heavy tasks to K8s via `queue='kubernetes'` |

## Checklist

- [ ] TaskFlow `@task` for pure-Python steps; classic operators for provider integrations
- [ ] Every task idempotent (MERGE / partition overwrite / `{{ ds }}` parameterization)
- [ ] No top-level heavy imports; no `Variable.get()` at module scope
- [ ] `retries`, `retry_exponential_backoff`, `execution_timeout` set
- [ ] `on_failure_callback` wired for Slack/PagerDuty
- [ ] Sensors use `deferrable=True` or `mode='reschedule'` with `timeout`
- [ ] XCom carries URIs/paths, not DataFrames
- [ ] `catchup=False` unless a backfill is actively intended
- [ ] Credentials via Airflow Connections, never hardcoded
- [ ] DAG imports cleanly: `bash scripts/check-dag-import.sh --dag-file <path>`
- [ ] Executor chosen to match workload shape (see Executor selection table)

## References

- `references/k8s-log-protocol.md` — full kubectl command set for scheduler/worker logs, multi-pod grep, multi-date state loops, and executor-specific differences
- `references/taskflow-patterns.md` — XCom backends, deferrable operator patterns, dynamic task mapping, task groups, dataset triggers
- `scripts/check-dag-import.sh` — validates a DAG file with `ast.parse` + Airflow import; usage: `bash scripts/check-dag-import.sh --dag-file dags/my_dag.py`
- `scripts/grep-worker-logs.sh` — emits the canonical kubectl command to grep logs for a run/task; usage: `bash scripts/grep-worker-logs.sh --run-id <id> --task-id <id>`

## Cross-references

| Skill | When |
|---|---|
| `python` | Code quality inside `@task` bodies (types, testing, error handling) |
| `pyspark` | Tasks that launch Spark jobs via `SparkSubmitOperator` |
| `sql` | Idempotent MERGE / partition patterns for warehouse targets |
| `docker` | Image design for `KubernetesPodOperator` task containers |
