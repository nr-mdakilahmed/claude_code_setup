---
name: openmetadata
description: Configures and troubleshoots OpenMetadata ingestion workflows, data quality tests, lineage, profiling, and dbt integration for the OpenMetadata catalog and governance platform. Triggers when Claude edits ingestion YAML, writes OpenMetadata SDK code, debugs missing lineage or failed tests, or designs a catalog rollout.
when_to_use: Auto-trigger on ingestion-config YAML files and OpenMetadata SDK Python. Invoke explicitly with /openmetadata for a workflow-design review.
paths:
  - "**/ingestion*.yaml"
  - "**/ingestion*.yml"
  - "**/*openmetadata*.yaml"
  - "**/*openmetadata*.yml"
---

# OpenMetadata Workflows

Turns Claude into an OpenMetadata workflow reviewer: chooses the right workflow type for the job, writes FQN-safe YAML, staggers schedules, and fixes the filter/auth/lineage failures that burn the first day on the platform.

**Freedom level: Medium** — ingestion is pattern-driven YAML. Claude picks between known workflow types and parameterizes them; the shape of each config rarely varies.

## 1. FQN Is Identity

**A fully qualified name is `service.database.schema.table` — case-sensitive, four parts, period-separated.**

- Use the exact casing the source system reports. Snowflake returns uppercase; Postgres returns lowercase. Do not normalize.
- `serviceName` in the YAML is the first segment of every FQN that workflow produces. Name it once and reuse; renaming later orphans all downstream lineage and tests.
- `entityFullyQualifiedName` in test-suite configs must match what the metadata workflow produced, character for character.
- "Renamed serviceName to fix a typo" → "Create a new service and re-ingest; keep the old one until consumers migrate".

## 2. Filter Before You Ingest

**Every workflow gets `databaseFilterPattern` + `schemaFilterPattern` + `tableFilterPattern`. No exceptions.**

- Exclude system schemas explicitly: `^information_schema$`, `^pg_.*`, `^snowflake$`, `^sys.*`.
- Use anchored regex (`^prod$`, not `prod`) — substring matches catch `DEV_prod_copy`.
- Profiler on an unfiltered catalog is the fastest way to melt a warehouse. Scope to tier-1 tables and set `profileSample: 10` (percent).
- "No filters — we want everything" → "Start with a whitelist of 5–10 tables; widen after one successful run".

## 3. Stagger Workflow Schedules

**Six workflow types compete for the same warehouse; running them all at 2 AM means none finish.**

- Metadata 2 AM · dbt 2:30 AM · lineage 3 AM · usage 3:30 AM · profiler 4 AM · test suite 15-min cadence.
- Run dbt **after** the dbt build that produced its `manifest.json`, not on a fixed catalog clock.
- Usage workflows read query history — expensive. Weekly is usually enough.
- Put schedules in version control, not the UI. Drifted schedules are invisible until they collide.

## 4. Lineage Is Automatic Or Absent

**Lineage comes from query logs and dbt manifests, never from manual entry except as a last resort.**

- Database connectors need `processViewLineage: true` and a populated query log (`queryLogDuration: 1`+).
- Cross-database lineage requires `processCrossDatabaseLineage: true` **and** `crossDatabaseServiceNames: [...]` listing every partner service by its exact serviceName.
- BI lineage requires the upstream database service to already be ingested under the serviceName the BI tool uses.
- "Lineage is missing for table X" → check (a) is X in the tableFilterPattern? (b) has a query referenced X in the last `queryLogDuration` days? (c) is the upstream service ingested with the matching name?

## 5. Test What You Publish

**Every tier-1 table gets a test suite before it's trusted by consumers.**

- Minimum battery: `tableRowCountToBeBetween`, `columnValuesToBeNotNull` on PKs, `columnValuesToBeUnique` on PKs, `tableRowInsertedCountToBeBetween` (freshness).
- YAML parameter values are **strings** — `value: "100"`, not `value: 100`. Integers silently fail.
- Publish DataFrame test results back to the catalog with `result.publish("FQN")` so Airflow/CI can alert on drift.

## Quick reference

One decision lookup consulted on every invocation.

| Need | Workflow type | `sourceConfig.type` | Cadence |
|---|---|---|---|
| Tables, schemas, tags | Metadata | `DatabaseMetadata` | Daily |
| Transformation context | dbt | `DBT` | After each dbt build |
| Column lineage | Lineage | `DatabaseLineage` | Daily |
| Popular tables / query cost | Usage | `DatabaseUsage` | Weekly |
| Column stats / distributions | Profiler | `Profiler` | Daily (tier-1 only) |
| Row-level data quality | Test Suite | `TestSuite` | 15 min or daily |

## Minimal metadata workflow (inline teaser)

```yaml
source:
  type: snowflake
  serviceName: snowflake_prod   # becomes the FQN root forever
  serviceConnection:
    config:
      type: Snowflake
      username: "{{ ctx.snowflake.username }}"
      account: "{{ ctx.snowflake.account }}"
      warehouse: "{{ ctx.snowflake.warehouse }}"
      role: "{{ ctx.snowflake.role }}"
  sourceConfig:
    config:
      type: DatabaseMetadata
      markDeletedTables: true
      databaseFilterPattern: { includes: ["^PROD$"] }
      schemaFilterPattern:   { excludes: ["^INFORMATION_SCHEMA$"] }
      incremental: { enabled: true, lookbackDays: 4 }
sink:
  type: metadata-rest
  config: {}
workflowConfig:
  openMetadataServerConfig:
    hostPort: "{{ ctx.openmetadata.host }}"
    authProvider: openmetadata
    securityConfig:
      jwtToken: "{{ ctx.openmetadata.jwt }}"
```

Validate before shipping: `scripts/validate-ingestion-yaml.sh --file <path>`.

## Anti-patterns

| Pattern | Fix |
|---|---|
| No filter patterns set | Whitelist 5–10 tables; anchored regex |
| Profiler on every table | `tableFilterPattern` + `profileSample: 10` |
| Hardcoded JWT in YAML | `{{ ctx.secret }}` template or env var |
| All workflows on same cron | Stagger by 30 min; profiler last |
| Renamed serviceName | Create new service; never rename |
| YAML test param as integer | Quote it: `value: "100"` |
| Missing `markDeletedTables` | Set true; otherwise deleted tables linger |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `401 Unauthorized` | JWT expired — regenerate in UI; update secret store |
| `Connection refused` | `hostPort` missing `/api` suffix or wrong port |
| `Entity not found` when creating test | FQN mismatch; check casing of `entityFullyQualifiedName` |
| `No tables found` in log | `tableFilterPattern` excludes everything; test regex against real names |
| Lineage panel empty | `processViewLineage: true`? `queryLogDuration` > 0? Upstream service ingested under the right name? |
| Profiler times out | Cut `profileSample`, narrow `tableFilterPattern`, raise `threads` cautiously |
| dbt shows zero models | `manifest.json` path wrong, or dbt project + database serviceName don't match |
| Tests report `Aborted` | Worker OOM or connector driver mismatch; check pod logs |
| Cross-database lineage missing | Every partner service listed in `crossDatabaseServiceNames` exactly |
| Filter regex matches nothing | `^` and `$` on anchored literals; test with `grep -E` on a source listing |

## Checklist

- [ ] serviceName is permanent, FQN-safe, documented in repo
- [ ] `databaseFilterPattern`, `schemaFilterPattern`, `tableFilterPattern` all set
- [ ] System schemas explicitly excluded
- [ ] `markDeletedTables: true` on metadata workflow
- [ ] `incremental: { enabled: true }` set on large services
- [ ] Credentials via `{{ ctx.secret }}` or env — no plaintext
- [ ] Schedules staggered (no two workflows at the same minute)
- [ ] `processViewLineage: true` on lineage workflows
- [ ] Profiler scoped to tier-1 with `profileSample: 10`
- [ ] Test suites defined for all tier-1 tables
- [ ] YAML validated with `scripts/validate-ingestion-yaml.sh`

## References

- `references/workflow-configs.md` — full YAML for all six workflow types (metadata, usage, lineage, profiler, dbt, test suite)
- `references/connectors-db.md` — relational, OLAP, NoSQL database connectors + auth patterns
- `references/connectors-lake.md` — S3/GCS/ADLS, Delta, Iceberg, Hudi, DBFS
- `references/connectors-dashboard.md` — Tableau, Looker, PowerBI, Superset, Metabase, QuickSight, etc.
- `references/connectors-other.md` — Airflow, dbt, Fivetran, Dagster, Kafka, MLflow, Elasticsearch
- `references/test-definitions.md` — all table- and column-level test types and YAML parameter format
- `references/data-quality-code.md` — TestRunner API and DataFrameValidator for inline ETL validation
- `references/validation-patterns.md` — chunk-based validation with transactional rollback
- `references/sdk-examples.md` — Python SDK for CRUD, lineage, search
- `references/airflow-integration.md` — orchestrating ingestion DAGs, pipeline type mapping
- `scripts/validate-ingestion-yaml.sh` — structural check before shipping a workflow YAML

## Cross-references

| Skill | When |
|---|---|
| `airflow` | Orchestrating ingestion DAGs |
| `python` | SDK scripts, DataFrame validation ETL |
| `sql` | Custom SQL data-quality tests (`tableCustomSQLQuery`) |
