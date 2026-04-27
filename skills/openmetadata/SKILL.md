---
name: openmetadata
description: >
  Use when configuring ingestion pipelines, data quality tests, lineage tracking,
  profiling, dbt integration, or working with the OpenMetadata API/SDK.
  Covers the OpenMetadata data catalog and governance platform.
  Auto-triggers for OpenMetadata configuration, SDK code, or data catalog workflows.
---

# OpenMetadata Reference

## Phased Workflow

**Phase 1 — Catalog Setup**: Configure service connections and ingestion pipelines.
> Read `references/workflow-configs.md` for all 6 YAML workflow configs.

**Phase 2 — Data Quality**: Set up tests, validation, and quality-as-code.
> Read `references/data-quality-code.md` for TestRunner API and DataFrameValidator.
> Read `references/test-definitions.md` for full test type/class reference.

**Phase 3 — Advanced**: SDK access and Airflow orchestration.
> Read `references/sdk-examples.md` for Python SDK CRUD, search, lineage.
> Read `references/airflow-integration.md` for DAG patterns and pipeline mapping.

Additional: `references/connectors.md` (84+ connectors), `references/validation-patterns.md` (chunk-based validation).

## Workflow Order

| Step | Workflow | Type | Schedule |
|---|---|---|---|
| 1 | Metadata | `DatabaseMetadata` | Daily |
| 2 | DBT | `DBT` | After dbt runs |
| 3 | Lineage | `DatabaseLineage` | Daily |
| 4 | Usage | `DatabaseUsage` | Weekly |
| 5 | Profiler | `Profiler` | Daily (critical only) |
| 6 | Test Suite | `TestSuite` | 15 min or daily |

## Filter Patterns

```yaml
databaseFilterPattern:
  includes: ["^PRODUCTION$", ".*_PROD$"]
  excludes: ["^snowflake$", "DEV", "^TEMP_.*"]
schemaFilterPattern:
  includes: ["^public$", "analytics"]
  excludes: ["^information_schema$", "^pg_.*"]
tableFilterPattern:
  includes: ["^fact_.*", "^dim_.*"]
  excludes: [".*_backup$", "^tmp_.*"]
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Profiler on all tables | `tableFilterPattern`; `profileSample: 10` |
| No filter patterns | Always set database/schema/table filters |
| Missing incremental ingestion | `incremental: { enabled: true, lookbackDays: 4 }` |
| Hardcoded JWT tokens | Use env vars or `{{ ctx.secret }}` templates |
| No `markDeletedTables: true` | Enable on metadata config |
| Wrong FQN format | `service.database.schema.table` (4 parts, case-sensitive) |
| All workflows same schedule | Stagger: metadata 2AM, lineage 3AM, profiler 4AM |
| No test suite for critical tables | Test suites for tier-1 tables |

## Troubleshooting

| Issue | Fix |
|---|---|
| Connection refused | Check `hostPort` URL |
| 401 Unauthorized | Regenerate JWT token |
| Entity not found | Use exact FQN: `service.database.schema.table` |
| No tables found | Check filter patterns |
| Profiler timeout | Reduce `profileSample` |
| Lineage missing | `processViewLineage: true` |

## Cross-References

| Skill | When |
|---|---|
| `airflow` | Orchestrating ingestion workflows |
| `python` | SDK scripts and ETL code |
| `sql` | Custom SQL data quality tests |
