# TaskFlow API Deep Patterns

Reference for advanced TaskFlow usage. Read when a DAG needs custom XCom, deferrable sensors, dynamic fan-out, task groups, or dataset-driven scheduling.

## Contents

- Minimal TaskFlow DAG
- XCom: when it is fine, when to switch backends
- Sensors vs deferrable operators
- Dynamic task mapping (`.expand()`)
- Task groups for visual clustering
- Dataset triggers (data-aware scheduling)
- Callbacks (failure, SLA, retry)
- Branching with TaskFlow
- Mixing TaskFlow and classic operators

## Minimal TaskFlow DAG

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
        "execution_timeout": timedelta(hours=1),
    },
    tags=["production"],
)
def daily_etl():
    @task
    def extract() -> dict:
        # Lazy import keeps scheduler parse fast
        import pandas as pd  # noqa: F401
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

## XCom: when it is fine, when to switch backends

**Fine in default XCom**:

- Primitive values (int, str, bool)
- Small dicts / lists of URIs, row counts, job IDs
- Anything under ~1 KB

**Needs a custom backend** (S3XComBackend, GCSXComBackend):

- DataFrames, NumPy arrays, sklearn models
- Any blob over a few KB
- Cross-DAG payloads that must survive metadata DB pruning

Rule: **pass a URI or path, not a payload**. Write the DataFrame to S3 in one task; pass the S3 URI to the next.

## Sensors vs deferrable operators

| Wait pattern | Best choice | Why |
|---|---|---|
| Short (<2 min), frequent | Sensor `mode='poke'` | Poll overhead is cheap |
| Medium (2 min – 1 h) | Sensor `mode='reschedule'` + `timeout` | Frees worker slot between pokes |
| Long (hours) or deferrable exists | `deferrable=True` | Zero worker-slot cost; triggerer handles |

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

# Preferred form for modern deployments
wait = S3KeySensor(
    task_id="wait_for_file",
    bucket_key="s3://raw/data/{{ ds }}/_SUCCESS",
    deferrable=True,
    timeout=60 * 60 * 6,  # 6 h cap
    poke_interval=60,
)
```

## Dynamic task mapping (`.expand()`)

```python
@task
def get_partitions() -> list[str]:
    return ["us", "eu", "apac"]

@task
def process(partition: str) -> dict:
    return {"partition": partition, "status": "done"}

results = process.expand(partition=get_partitions())
```

Use `.expand_kwargs()` to vary multiple arguments per mapped task. Set `max_active_tis_per_dag` on the task to limit concurrency when the fan-out is large.

## Task groups for visual clustering

```python
from airflow.utils.task_group import TaskGroup

with TaskGroup("extract_group") as extract_group:
    extract_orders = extract_orders_task()
    extract_customers = extract_customers_task()
```

Task groups are UI-only — they do not change execution. Use them to keep large DAGs readable.

## Dataset triggers (data-aware scheduling)

Chain DAGs on data, not cron:

```python
from airflow import Dataset

sales_raw = Dataset("s3://raw/sales/")

@dag(schedule=[sales_raw], start_date=datetime(2024, 1, 1), catchup=False)
def transform_sales():
    @task(outlets=[Dataset("s3://clean/sales/")])
    def clean(): ...
```

Downstream DAG runs when any upstream task with a matching `outlets` finishes. Replaces fragile `ExternalTaskSensor` chains.

## Callbacks (failure, SLA, retry)

```python
def alert_slack(context: dict) -> None:
    # Keep import inside the callback body
    from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
    hook = SlackWebhookHook(slack_webhook_conn_id="slack_alerts")
    hook.send(text=f"Task failed: {context['task_instance_key_str']}")

@dag(
    ...,
    default_args={
        "on_failure_callback": alert_slack,
        "sla": timedelta(hours=2),
    },
)
def my_dag(): ...
```

- `on_failure_callback` — fires on task failure (not on retry)
- `on_retry_callback` — fires on each retry
- `sla_miss_callback` — fires when SLA exceeded
- `on_success_callback` — rarely useful; avoid for pager hygiene

## Branching with TaskFlow

```python
from airflow.decorators import task

@task.branch
def choose_path(data: dict) -> str:
    return "full_reload" if data["count"] > 1_000_000 else "incremental"

@task
def full_reload(): ...

@task
def incremental(): ...

choose_path(extract()) >> [full_reload(), incremental()]
```

Downstream tasks not on the chosen branch are marked `skipped`, not `failed`.

## Mixing TaskFlow and classic operators

```python
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

@task
def extract() -> str:
    return "s3://raw/data/{{ ds }}/"

load = SQLExecuteQueryOperator(
    task_id="load",
    conn_id="snowflake_default",
    sql="COPY INTO clean.sales FROM '{{ ti.xcom_pull(task_ids='extract') }}'",
)

extract() >> load
```

TaskFlow tasks push XCom automatically; classic operators pull via `{{ ti.xcom_pull(...) }}` in templates. Both interoperate freely.
