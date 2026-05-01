# dbt Incremental Strategies

## Contents

- When to go incremental
- Strategy selection matrix
- `append` — append-only event streams
- `merge` — late-arriving updates on a stable grain
- `insert_overwrite` — partition replacement
- `delete+insert` — unique-key rebuild on warehouses without MERGE
- Warehouse support matrix
- Late-arrival and lookback windows
- Backfill and full-refresh patterns
- Common failure modes

## When to go incremental

Incremental earns its complexity only when **one** of the following holds:

- Source volume exceeds roughly 10M rows/day.
- A full refresh takes longer than the SLA window (e.g., hourly pipeline, 40-min full build).
- Cost of a full table scan to rebuild is material ($/run tracked).

If none hold, stay with `table`. Incremental models have more failure modes — late data, schema drift, idempotency — and those cost engineer-hours.

## Strategy selection matrix

| Write pattern | Strategy | Needs `unique_key` | Key warehouses |
|---|---|---|---|
| Append-only event stream, no updates | `append` | No | All |
| Late-arriving updates, stable PK | `merge` | Yes | Snowflake, BigQuery, Databricks, Postgres |
| Rebuild whole partition (idempotent) | `insert_overwrite` | No (needs `partition_by`) | BigQuery, Spark, Databricks |
| Unique-key replace, engine lacks MERGE | `delete+insert` | Yes | Redshift, Postgres |
| SCD-2 history | `snapshot` (not incremental) | `unique_key` + `updated_at` | All |

## `append` — append-only event streams

Use when upstream is strictly append-only (web events, click logs, raw Kafka dumps) and has a monotonically increasing watermark column.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

SELECT *
FROM {{ ref('raw_events') }}
{% if is_incremental() %}
  WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}
```

- **Watermark choice**: use the source's ingestion timestamp, not event time, when late-arriving events are possible.
- **Risk**: duplicates if the upstream ever re-emits. Mitigate with a downstream dedup step or switch to `merge`.

## `merge` — late-arriving updates on a stable grain

Use when rows may be updated hours or days after insert and you have a stable unique key (order_id, user_id + event_id). Requires warehouse-native `MERGE`.

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    merge_exclude_columns=['created_at']
) }}

SELECT *
FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
  WHERE updated_at > (SELECT DATEADD(day, -3, MAX(updated_at)) FROM {{ this }})
{% endif %}
```

- **Lookback window** (`DATEADD(day, -3, …)`) catches updates arriving up to 3 days late. Size it to your 99th percentile late-arrival.
- **`merge_exclude_columns`** preserves the original `created_at` on update — without this, MERGE overwrites it.
- **Composite key**: `unique_key=['user_id', 'event_id']` — dbt will generate `ON target.user_id = source.user_id AND target.event_id = source.event_id`.

## `insert_overwrite` — partition replacement

Use when you can idempotently rebuild a whole partition (typically today's date). Strongest for hourly / daily batch patterns on BigQuery, Databricks, Spark.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    partitions=['date(current_date)']
) }}

SELECT *
FROM {{ ref('stg_events') }}
WHERE event_date = CURRENT_DATE
```

- **Idempotent**: re-running overwrites the same partition; no duplicate risk.
- **`partitions` config** tells dbt which partitions to replace — avoid recomputing every partition each run.
- **Not available on Snowflake**; use `merge` with a date predicate instead.

## `delete+insert` — unique-key rebuild on warehouses without MERGE

Use on Redshift or older Postgres where `MERGE` is unavailable or slow. dbt deletes matching rows then inserts.

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='delete+insert'
) }}
```

- **Slower than MERGE on large tables** — two round trips.
- **Non-atomic on some engines** — a failure between delete and insert leaves the table partially updated. Use transactions where the adapter supports them.

## Warehouse support matrix

| Strategy | Snowflake | BigQuery | Redshift | Databricks | Postgres |
|---|---|---|---|---|---|
| `append` | Yes | Yes | Yes | Yes | Yes |
| `merge` | Yes (default) | Yes (default) | No (falls back) | Yes (default) | Yes (PG15+) |
| `insert_overwrite` | No | Yes | No | Yes | No |
| `delete+insert` | Yes | Yes | Yes (default) | Yes | Yes (default) |

Defaults shown are dbt's default `incremental_strategy` when unset on that adapter.

## Late-arrival and lookback windows

Every `merge`-based incremental needs a lookback to catch late-arriving updates:

```sql
{% if is_incremental() %}
  WHERE updated_at >= (SELECT DATEADD(day, -{{ var('lookback_days', 3) }}, MAX(updated_at)) FROM {{ this }})
{% endif %}
```

- Measure actual late-arrival distribution in production (`SELECT DATEDIFF(day, event_time, _loaded_at) …`) before picking a lookback.
- Too short → missed updates; too long → recompute cost creeps up.
- Log `max(updated_at)` per run to catch silent watermark drift.

## Backfill and full-refresh patterns

- `dbt run --full-refresh --select my_model` rebuilds from scratch — use after schema changes or when a backfill is needed.
- Guard against accidental full refresh on huge tables with `{{ config(full_refresh=false) }}` on the model (dbt 1.4+).
- For partial backfills on BigQuery / Databricks, pass `--vars '{"start_date": "2025-01-01", "end_date": "2025-01-31"}'` and use `insert_overwrite` with a computed `partitions` list.

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Duplicates in incremental table | `append` used with late updates | Switch to `merge` with `unique_key` |
| Incremental misses rows | Watermark column has NULLs | Coalesce to a safe epoch or use ingestion time |
| First run after schema change fails | New column not in existing table | `dbt run --full-refresh` or use `on_schema_change='append_new_columns'` |
| MERGE shows "ambiguous column" | Source query exposes column that also exists in target with different type | Cast in source CTE to match target schema |
| Incremental takes longer than full refresh | Lookback window too wide + no cluster/partition pruning | Add partition filter inside `is_incremental()` block and tighten lookback |
| `insert_overwrite` creates tiny partitions | `partitions` config lists too many fine-grained partitions | Partition by date, not timestamp; coalesce in the model |
