---
name: sql
description: >
  Use when writing SQL for Snowflake, BigQuery, or Redshift, optimizing queries,
  designing warehouse tables, building dbt models, or debugging slow queries.
  Covers partitioning, clustering, incremental strategies, window functions, and cost optimization.
  Auto-triggers for SQL files and dbt models.
---

# Data Warehouse SQL Patterns

## SQL Security (Non-Negotiable)

```python
# NEVER: f-strings for values = SQL injection
query = f"SELECT * FROM users WHERE id = {user_input}"  # VULNERABLE

# ALWAYS: Parameter placeholders
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## Bulk Operations

```python
# SLOW: Row by row (N round trips)
for r in records:
    cursor.execute("INSERT INTO t VALUES (%s)", (r,))

# FAST: executemany (single round trip)
cursor.executemany("INSERT INTO t (id, name) VALUES (%s, %s)",
    [(r["id"], r["name"]) for r in records])

# FASTEST: COPY INTO (Snowflake) or load from GCS (BigQuery)
```

## Snowflake Patterns

- **Warehouse sizing**: X-LARGE + AUTO_SUSPEND=60 for ETL; MEDIUM + MAX_CLUSTER=8 for BI
- **Dynamic Tables**: `CREATE DYNAMIC TABLE ... TARGET_LAG = '1 hour'` — replaces custom CDC
- **Clustering**: `ALTER TABLE ... CLUSTER BY (date, user_id)` for range queries
- **Search optimization**: `ADD SEARCH OPTIMIZATION ON EQUALITY(id)` for point lookups
- **Zero-copy clone**: `CREATE DATABASE dev CLONE prod` for dev/test

## BigQuery Patterns

- **Partition + Cluster**: `PARTITION BY DATE(event_time) CLUSTER BY user_id`
- **Require partition filter**: `OPTIONS (require_partition_filter = TRUE)`
- **Materialized views**: Auto-refresh aggregations for dashboards

## Redshift Patterns

- **Distribution**: `DISTSTYLE KEY DISTKEY (user_id)` to co-locate joins
- **Sort keys**: `COMPOUND SORTKEY (event_time, event_type)` for range + equality
- **Maintenance**: `VACUUM FULL ... TO 95 PERCENT; ANALYZE;`

## dbt Patterns

```sql
-- Incremental append
{{ config(materialized='incremental') }}
SELECT * FROM {{ ref('raw_events') }}
{% if is_incremental() %}
WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}

-- Merge (dedup) with lookback
{{ config(materialized='incremental', unique_key='event_id', incremental_strategy='merge') }}
```

| Materialization | When | Tradeoff |
|---|---|---|
| View | Small, always-fresh | Slow query, recomputes |
| Table | Base dims/facts | Fast query, stale until rebuild |
| Incremental | Large facts, append-heavy | Fast build, complex logic |
| Ephemeral | Reusable CTE | No table, inlined at compile |

## Window Functions

```sql
-- Dedup (latest record per user)
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn
    FROM users
) WHERE rn = 1;

-- Running total
SUM(amount) OVER (PARTITION BY user_id ORDER BY event_date) AS running_total

-- Period comparison
LAG(revenue, 1) OVER (ORDER BY event_date) AS prev_day_revenue
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| f-string SQL values | Parameterized queries always |
| `SELECT *` in production | Explicit column list |
| Row-by-row INSERT | `executemany` or COPY INTO |
| No partition filter | Add WHERE on partition column |
| Correlated subquery in SELECT | Rewrite as JOIN or window function |
| `ORDER BY` without `LIMIT` | Add LIMIT or remove ORDER BY |
| `DISTINCT` as a bandaid | Fix the source of duplicates |
| Nested subqueries (3+ deep) | Use CTEs for readability |
| Hardcoded dates | Use `CURRENT_DATE - INTERVAL` |
| `UNION` instead of `UNION ALL` | Use UNION ALL unless dedup needed |

## Cost Optimization

| Strategy | How |
|---|---|
| Right-size compute | Warehouse sizing + auto-suspend |
| Partition pruning | Clustering keys, partition filters |
| Avoid full scans | Select only needed columns |
| Cache results | Identical queries cached 24h |
| Monitor spend | WAREHOUSE_METERING_HISTORY / JOBS |
