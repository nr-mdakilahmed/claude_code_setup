# OpenMetadata Data Lake & Storage Connectors

Object storage, table formats, and data-lake connectors. Set `source.serviceConnection.config.configSource` based on format/bucket.

## Table formats

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Delta Lake | `DeltaLake` | IAM / service-account | Metastore-backed vs path-based — pick one `configSource` |
| Apache Iceberg | `Iceberg` | IAM / service-account | Catalog type must match (Glue, REST, Nessie, Hive) |
| Apache Hudi | `Hudi` | IAM / service-account | Requires `.hoodie` folder visibility; no COW vs MOR distinction in catalog |

## Cloud object storage

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| S3 (AWS) | `Datalake` with `S3Config` | IAM role (preferred) or access key | `bucketName` is required; prefix filter is applied at list time |
| GCS (Google) | `Datalake` with `GCSConfig` | service-account JSON | `projectId` must match bucket project |
| ADLS (Azure) | `Datalake` with `AzureConfig` | SAS / service principal | Gen2 only — Gen1 unsupported since 1.5 |
| MinIO | `Datalake` with `S3Config` | access key | Set `endPointURL` to MinIO URL; path-style required |

## Lake engines / query layers

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Databricks File System (DBFS) | via `Databricks` | PAT token | Listed under the Databricks service, not Datalake |
| Unity Catalog volumes | via `Databricks` | PAT + Unity enabled | Needs `catalog` with `VOLUMES` permissions |
| DataLake (generic) | `Datalake` | per configSource | Used for unmanaged file-based tables (Parquet/CSV/Avro/ORC) |

## File format support (applies to `Datalake` connector)

| Format | Metadata | Profiler | Lineage | Notes |
|---|---|---|---|---|
| Parquet | yes | yes | via Spark/Presto | Infer schema from footer; partition keys become columns |
| CSV | yes | yes | limited | `hasHeader: true` required for column names |
| Avro | yes | yes | limited | Schema resolved from file; registry not used |
| ORC | yes | yes | via Spark/Presto | — |
| JSON / NDJSON | yes | sampled | none | Large nested JSON slows profiler |

## Common gotchas across lake connectors

- Use a single partition scan per table — `bucketName + prefix + tableName`. A wildcard prefix explodes listing cost.
- Profiler on lake tables is **read-heavy**. Scope it to `tableFilterPattern` for a handful of critical tables.
- Lineage from lake to warehouse requires a query engine (Trino/Spark/Databricks) with `processQueryLineage: true` — it never comes from the lake connector alone.
