# OpenMetadata Database Connectors

Relational, OLAP, and NoSQL database connectors. Use the connector `type` value shown for the `source.type` and `source.serviceConnection.config.type` fields in your ingestion YAML.

## Cloud warehouses

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Snowflake | `Snowflake` | key-pair (preferred) or username/password | Uppercase DB/schema names in FQN; set `role` + `warehouse` |
| BigQuery | `BigQuery` | service-account JSON | `projectId` is the serviceName prefix in FQN, not GCP project |
| Redshift | `Redshift` | username/password or IAM | Serverless needs `clusterSource: serverless` |
| Databricks | `Databricks` | PAT token | `httpPath` required; set `catalog` explicitly for Unity |
| Azure Synapse | `AzureSQL` (dedicated pool) | SQL auth / AD | Use `driver: ODBC Driver 18 for SQL Server` |
| Google Cloud SQL | Postgres/MySQL variant | IAM / password | Connect via Cloud SQL Auth Proxy or private IP |

## On-prem RDBMS

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| PostgreSQL | `Postgres` | username/password | `sslmode` defaults to `disable` — override for managed |
| MySQL | `Mysql` | username/password | Case-sensitivity depends on `lower_case_table_names` |
| Oracle | `Oracle` | username/password | Use `oracleServiceName` not SID for PDBs |
| SQL Server | `Mssql` | SQL auth / Windows | Requires `pyodbc` + ODBC driver 18 |
| MariaDB | `MariaDB` | username/password | Treat as MySQL; version affects lineage parsing |
| DB2 | `Db2` | username/password | Needs `ibm_db` driver license accept step |
| SAP HANA | `SapHana` | username/password | Use HDI container schema for lineage |
| SAP ERP | `SapErp` | OAuth2 + API key | Slow first run — cache `metadataVersion` |
| SQLite | `Sqlite` | path only | No usage/lineage workflow; metadata only |
| CockroachDB | `Cockroach` | username/password | Protocol-compatible with Postgres driver |
| YugabyteDB | `Yugabyte` | username/password | Postgres-compatible; use `Postgres` if Yugabyte unavailable |

## OLAP / analytics engines

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Trino | `Trino` | JWT / basic | `catalog` is required and becomes part of FQN |
| Presto | `Presto` | basic / LDAP | Prefer Trino for new deployments |
| ClickHouse | `Clickhouse` | username/password | HTTPS port `8443` not `9000` |
| Druid | `Druid` | basic | `SQL-over-HTTP` endpoint only |
| Pinot | `Pinot` | none / basic | Use controller URL for metadata, broker for usage |
| Doris | `Doris` | username/password | MySQL-wire protocol — use port 9030 |
| StarRocks | `StarRocks` | username/password | Same as Doris; treat as MySQL-wire |
| Impala | `Impala` | LDAP / Kerberos | Keytab path must be container-readable |
| Hive | `Hive` | LDAP / Kerberos | HiveServer2 port 10000; not Metastore port |
| Vertica | `Vertica` | username/password | `searchPath` affects schema discovery |
| Greenplum | `Greenplum` | username/password | Postgres-compatible |
| Teradata | `Teradata` | username/password + LDAP | Requires `teradatasql` driver |
| AWS Athena | `Athena` | IAM | `s3StagingDir` must be writeable by role |
| AWS Glue | `Glue` | IAM | Treat Glue catalog as the database in FQN |

## Specialty / time-series / document

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| MongoDB | `MongoDB` | username/password | Sampling needed — set `sampleDataCount` |
| Cassandra | `Cassandra` | username/password | Contact points list required |
| Couchbase | `Couchbase` | username/password | Bucket becomes schema in FQN |
| Elasticsearch | `ElasticSearch` | basic / API key | Index patterns map to tables |
| Neo4j | `Neo4j` | basic | Labels map to tables; relationships ignored in lineage |
| DynamoDB (AWS) | `DynamoDB` | IAM | Metadata only; no column types until sampled |
| InfluxDB | `InfluxDb` | token | v1.x uses basic auth; v2.x uses token |
| TimescaleDB | `Postgres` (extension) | username/password | Use Postgres connector; hypertables show as tables |
| QuestDB | `Questdb` | basic | Postgres-wire port 8812 |
| DuckDB | `DuckDb` | file path | Read-only mode recommended for ingestion |
| SingleStore | `SingleStore` | username/password | MySQL-wire; `databasetype: mysql` in connection |
