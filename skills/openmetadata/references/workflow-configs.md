# OpenMetadata — Workflow Configuration Examples

> **When to load:** Phase 1 (Catalog Setup) — configuring ingestion pipelines for metadata, usage, lineage, profiler, dbt, and test suites.

All workflows require a `sink` (type: `metadata-rest`) and `workflowConfig` with `openMetadataServerConfig` (hostPort, authProvider, JWT token).

---

## 1. Metadata Workflow (DatabaseMetadata)

Extracts schema metadata: tables, views, stored procedures, tags.

```yaml
source:
  type: snowflake
  serviceName: snowflake
  serviceConnection:
    config:
      type: Snowflake
      username: "{{ ctx.snowflake.username }}"
      account: "{{ ctx.snowflake.account }}"
      privateKey: "{{ ctx.snowflake.private_key }}"
      snowflakePrivatekeyPassphrase: "{{ ctx.snowflake.passphrase }}"
      role: "{{ ctx.snowflake.role }}"
      warehouse: "{{ ctx.snowflake.warehouse }}"
  sourceConfig:
    config:
      type: DatabaseMetadata
      markDeletedTables: true
      markDeletedStoredProcedures: true
      includeTables: true
      includeViews: true
      includeTags: true
      includeOwners: true
      includeStoredProcedures: true
      includeDDL: true
      overrideMetadata: true
      useFqnForFiltering: false
      queryLogDuration: 1
      queryParsingTimeoutLimit: 298
      databaseFilterPattern:
        includes: ["^MY_DATABASE$"]
        excludes: ["^snowflake$", "DEV"]
      schemaFilterPattern:
        includes: ["^public$"]
        excludes: ["^information_schema$"]
      tableFilterPattern:
        includes: [".*"]
        excludes: ["^temp_.*"]
      incremental:
        enabled: true
        lookbackDays: 4
        safetyMarginDays: 1
      threads: 2

ingestionPipelineFQN: snowflake.metadata
```

## 2. Usage Workflow (DatabaseUsage)

Analyzes query logs for usage patterns and popular tables.

```yaml
source:
  type: snowflake-usage
  sourceConfig:
    config:
      type: DatabaseUsage
      resultLimit: 1000000
      queryLogDuration: 3
      filterCondition: "query_text not ilike '%QUERY_HISTORY%'"
      processQueryCostAnalysis: true

processor:
  type: query-parser
  config: {}

ingestionPipelineFQN: snowflake.usage
```

## 3. Lineage Workflow (DatabaseLineage)

Extracts data lineage from query history.

```yaml
source:
  type: snowflake-lineage
  sourceConfig:
    config:
      type: DatabaseLineage
      queryLogDuration: 1
      processViewLineage: true
      processQueryLineage: true
      processCrossDatabaseLineage: true
      crossDatabaseServiceNames: ["aws-glue-use1", "aws-glue-use2"]
      threads: 2
      resultLimit: 100000

ingestionPipelineFQN: snowflake.lineage
```

## 4. Profiler Workflow (Profiler)

Computes statistical profiles for tables and columns.

```yaml
source:
  type: snowflake
  sourceConfig:
    config:
      type: Profiler
      tableFilterPattern:
        includes: ["stg_sfdc_opportunity"]
      profileSample: 10
      profileSampleType: PERCENTAGE

processor:
  type: "orm-profiler"
  config: {}

ingestionPipelineFQN: snowflake.profiler
```

## 5. DBT Workflow (DBT)

Ingests dbt project metadata, models, tests, and lineage.

```yaml
source:
  type: dbt
  serviceName: snowflake
  serviceConnection:
    config:
      type: Snowflake
      # ... credentials via ctx templates ...
  sourceConfig:
    config:
      type: DBT
      dbtConfigSource:
        dbtConfigType: cloud
        dbtCloudAuthToken: "{{ ctx.snowflake.dbt_auth_token }}"
        dbtCloudAccountId: "{{ ctx.snowflake.dbt_account_id }}"
        dbtCloudUrl: "{{ ctx.snowflake.dbt_url }}"
        dbtCloudProjectId: "96622"
        dbtCloudJobId: "86368"
      searchAcrossDatabases: false
      dbtUpdateDescriptions: true
      dbtUpdateOwners: true
      includeTags: true
      dbtClassificationName: dbtTags
      parsingTimeoutLimit: 600

ingestionPipelineFQN: snowflake.dbt
```

## 6. Test Suite Workflow (TestSuite)

Runs data quality tests defined in OpenMetadata.

```yaml
source:
  type: TestSuite
  serviceName: testsuite
  sourceConfig:
    config:
      type: TestSuite
      entityFullyQualifiedName: "snowflake.DATABASE.SCHEMA.TABLE"
      serviceConnections:
        - serviceName: "snowflake"
          serviceConnection:
            config:
              type: Snowflake
              # ... credentials ...

processor:
  type: orm-test-runner
  config: {}  # Empty runs ALL tests; specify testCases[] for specific tests

ingestionPipelineFQN: snowflake.testsuite_tablename
```
