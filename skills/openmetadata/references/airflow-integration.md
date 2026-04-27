# OpenMetadata — Airflow Integration

> **When to load:** Phase 3 (Advanced) — orchestrating OpenMetadata ingestion in Airflow DAGs.

## Pipeline Type Mapping

| Task Name | Pipeline Type |
|-----------|---------------|
| `ingestion_task` | `metadata` |
| `usage_task` | `usage` |
| `lineage_task` | `lineage` |
| `profiler_task` | `profiler` |
| `dbt_task` | `dbt` |
| `test_suite_task` | `TestSuite` |
| `data_insight_task` | `dataInsight` |
| `application_task` | `application` |

## Dynamic Test Suite DAG Pattern

```python
from airflow.decorators import dag, task
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.models import Variable
from datetime import datetime

@dag(
    dag_id='openmetadata_test_suites',
    start_date=datetime(2024, 1, 1),
    schedule_interval='*/15 * * * *',
    catchup=False,
    tags=["openmetadata", "data-quality"],
)
def test_suite_dag():
    @task
    def generate_configs() -> list[str]:
        fqns = ["snowflake.DB.SCHEMA.TABLE1", "snowflake.DB.SCHEMA.TABLE2"]
        configs = []
        for fqn in fqns:
            config = build_test_suite_config(fqn)
            configs.append(config)
        return configs

    @task
    def create_env_vars(config: str) -> list[dict]:
        return [
            {"name": "config", "value": config},
            {"name": "pipelineType", "value": "TestSuite"},
        ]

    configs = generate_configs()
    env_vars = create_env_vars.expand(config=configs)

    KubernetesPodOperator.partial(
        task_id="run_test_suite",
        arguments=["python", "main.py"],
        image=f"openmetadata/ingestion-base:{Variable.get('om_ver', '1.9.5')}",
        namespace="dataos",
        kubernetes_conn_id="kubernetes_default",
    ).expand(env_vars=env_vars)

test_suite_dag()
```

## Required Airflow Variables

| Variable | Description |
|----------|-------------|
| `OPENMETADATA_HOST_PORT` | Server URL (e.g., `http://om-server:8585/api`) |
| `OPENMETADATA_AUTH_PROVIDER` | Auth provider (e.g., `openmetadata`) |
| `OPENMETADATA_JWT_TOKEN` | JWT authentication token |
| `om_ver` | OpenMetadata version (default: `1.9.5`) |
| `OPENMETADATA_CTX_{SERVICE}_SECRET` | Service credentials as JSON |
