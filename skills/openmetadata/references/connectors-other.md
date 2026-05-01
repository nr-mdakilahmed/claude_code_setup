# OpenMetadata Other Connectors — Pipelines, Messaging, ML, Search, dbt

Connectors that don't fit DB/lake/dashboard. Cover orchestration tools, streaming, ML platforms, search backends, and dbt.

## Contents

- Pipeline / orchestration
- dbt / transformation
- Messaging / streaming
- ML / model registries
- Search / document stores

## Pipeline / orchestration

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Airflow | `Airflow` | basic / DB-backed | Uses metadata DB connection string — not Airflow REST API |
| Dagster | `Dagster` | GraphQL token | `host` must be reachable from ingestion pod |
| Prefect | `Prefect` | API key | Cloud vs OSS have different connector configs |
| Fivetran | `Fivetran` | API key + secret | Connector-level granularity; tasks map to Fivetran connectors |
| Airbyte | `Airbyte` | basic | OSS and cloud configs differ; prefer service account |
| Stitch | `Stitch` | API token | Source/destination pairs map to pipelines |
| NiFi | `Nifi` | basic / cert | Flow-level lineage only — process group granularity |
| AWS Glue (pipelines) | `GluePipeline` | IAM | Distinct from Glue catalog connector — uses Glue jobs |
| Databricks Workflows | `DatabricksPipeline` | PAT | Same workspace as the Databricks DB connector |
| Kafka Connect | `KafkaConnect` | basic | Needs `messagingServiceNames` to link source/sink lineage |
| Spark (standalone) | `Spark` | basic / none | History server URL required |
| Flink | `Flink` | JobManager REST | Job graph becomes lineage |
| Kinesis Firehose | `KinesisFirehose` | IAM | Reports delivery streams as pipelines |

## dbt / transformation

| Source | `type` | Auth | Common gotcha |
|---|---|---|---|
| dbt Cloud | `DBT` with `dbtConfigType: cloud` | dbt Cloud service token | Requires `dbtCloudProjectId` + `dbtCloudJobId` |
| dbt Core (local files) | `DBT` with `dbtConfigType: local` | filesystem path | `manifest.json` + `catalog.json` must be present |
| dbt Core (S3/GCS/ADLS) | `DBT` with `dbtConfigType: s3/gcs/azure` | cloud creds | Bucket path points to `target/` folder |
| dbt Core (HTTP) | `DBT` with `dbtConfigType: http` | URL + headers | Cache-bust on `manifest.json` URL |

dbt ingestion runs **against the database serviceName** it enriches — not a standalone service.

## Messaging / streaming

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Apache Kafka | `Kafka` | SASL/SSL | Schema Registry URL optional but needed for schema capture |
| Confluent Kafka | `Kafka` | API key + secret | Cloud endpoints require SASL_SSL |
| Redpanda | `Redpanda` | SASL | Kafka-wire compatible; use Kafka connector if Redpanda unavailable |
| Apache Pulsar | `Pulsar` | JWT / token | Tenant/namespace become part of FQN |
| AWS Kinesis | `Kinesis` | IAM | Streams map to topics |

## ML / model registries

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| MLflow | `Mlflow` | basic / token | Tracking URI must be reachable; registry URI often differs |
| SageMaker | `SageMaker` | IAM | Model packages ingested, not training jobs |
| Vertex AI | `VertexAI` | service-account | `location` must match model region |

## Search / document stores

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Elasticsearch (search service) | `ElasticSearch` | basic / API key | Distinct from using ES as a database — serviceType is `SearchService` |
| OpenSearch | `OpenSearch` | basic / AWS SigV4 | AWS-managed needs `awsConfig` block |

## When to use pipeline vs dbt connector

- **Pipeline connector** (Airflow, Dagster, Fivetran) models the **orchestration** layer — tasks, schedules, status.
- **dbt connector** enriches the **database** layer — adds descriptions, lineage, tests to already-ingested tables.
- Most teams run both: pipeline connector for job status, dbt connector for transformation context.
