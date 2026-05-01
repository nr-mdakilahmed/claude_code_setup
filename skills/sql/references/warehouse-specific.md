# Warehouse-Specific Tuning

## Contents

- Snowflake
  - Micro-partitions and pruning
  - Clustering keys
  - Search optimization
  - Result cache and warehouse cache
  - Warehouse sizing and auto-suspend
  - Dynamic tables
  - Zero-copy clone
  - Diagnostic queries
- BigQuery
  - Partition + cluster
  - `require_partition_filter`
  - Approximate aggregation functions
  - Materialized views
  - Slot tuning and reservations
  - Diagnostic views
- Redshift
  - Distribution styles and dist keys
  - Sort keys — compound vs interleaved
  - Vacuum and analyze
  - WLM and query queues
  - Diagnostic views

## Snowflake

### Micro-partitions and pruning

- Snowflake auto-partitions into 16MB compressed micro-partitions by ingest order. Pruning works when the filter column correlates with ingest order (event dates do; random UUIDs do not).
- Check pruning: `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_USER(...))` → look at `partitions_scanned` vs `partitions_total`. Ratio should be small.
- If a date column was ingested out of order, queries won't prune on it — reclustering is the fix.

### Clustering keys

- `ALTER TABLE events CLUSTER BY (event_date, user_id)` — declare keys that match your filter + group-by pattern.
- Monitor drift: `SELECT SYSTEM$CLUSTERING_INFORMATION('events', '(event_date, user_id)')`. `average_depth > 4` suggests reclustering is worthwhile.
- Reclustering runs automatically but consumes credits — enable only on tables large enough to justify it (>1TB, or query selectivity matters).
- Avoid clustering on columns with <1000 distinct values, or on columns queries rarely filter on.

### Search optimization

- `ALTER TABLE users ADD SEARCH OPTIMIZATION ON EQUALITY(email)` — for point lookups on large tables.
- Costs ongoing maintenance credits; use only when equality lookups dominate the workload (support tools, identity resolution).
- Not useful for range queries, substring searches, or aggregates.

### Result cache and warehouse cache

- **Result cache** (24h): identical query text + same role + no changed source → free. `USE ROLE …` inconsistencies defeat it.
- **Warehouse cache** (local SSD): same warehouse running the same query gets SSD hits. Suspend kills the cache.
- Set `AUTO_SUSPEND = 60` for ETL (cache is cheap to warm); `AUTO_SUSPEND = 600` for BI (cache worth preserving).

### Warehouse sizing and auto-suspend

- Start at X-SMALL. Double size only when the query spills to disk (`bytes_spilled_to_local_storage > 0` in `QUERY_HISTORY`).
- `MAX_CLUSTER_COUNT = N` with `SCALING_POLICY = STANDARD` for BI — auto-scales out on concurrent dashboards, scales in on idle.
- ETL: single cluster, larger size. BI: multi-cluster, smaller size.

### Dynamic tables

- `CREATE DYNAMIC TABLE daily_orders TARGET_LAG = '1 hour' WAREHOUSE = etl_wh AS SELECT …` — replaces custom CDC and scheduled refreshes.
- Snowflake figures out incremental refresh; you declare the query and the lag tolerance.
- Use for downstream aggregates where freshness SLA is >5 minutes. For sub-minute, stick with streams + tasks.

### Zero-copy clone

- `CREATE DATABASE dev CLONE prod` — instant, no storage cost until divergence.
- Ideal for dev/test environments and backfill dry-runs.

### Diagnostic queries

```sql
-- Slowest queries in the last day
SELECT query_id, query_text, execution_time, bytes_scanned, partitions_scanned, partitions_total
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE start_time > DATEADD(day, -1, CURRENT_TIMESTAMP)
ORDER BY execution_time DESC
LIMIT 20;

-- Warehouse spend
SELECT warehouse_name, SUM(credits_used) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time > DATEADD(day, -7, CURRENT_TIMESTAMP)
GROUP BY 1 ORDER BY 2 DESC;

-- Clustering health
SELECT SYSTEM$CLUSTERING_INFORMATION('my_table');
```

## BigQuery

### Partition + cluster

```sql
CREATE TABLE events (
    event_id STRING,
    event_time TIMESTAMP,
    user_id STRING,
    payload JSON
)
PARTITION BY DATE(event_time)
CLUSTER BY user_id, event_type
OPTIONS (
    require_partition_filter = TRUE,
    partition_expiration_days = 400
);
```

- Partition by the primary filter column (usually event date). One partition column; BigQuery supports one.
- Cluster by up to 4 columns in priority order — most-selective first.
- Clustering on a partitioned table only affects rows within the partition; effectiveness depends on partition size.

### `require_partition_filter`

- Set on every large table. Queries without a partition filter fail at compile time, protecting against accidental full scans.
- Override in dbt models with `WHERE _PARTITIONTIME IS NOT NULL AND event_time >= …`.

### Approximate aggregation functions

- `APPROX_COUNT_DISTINCT(user_id)` — HyperLogLog, ~1% error, 10–100× faster than exact on large cardinalities.
- `APPROX_QUANTILES(latency, 100)` — for percentiles on long-tail data.
- `APPROX_TOP_COUNT(page, 10)` — top-N without a full sort.
- Use for dashboards where exact counts don't matter; never for billing, compliance, or financial reporting.

### Materialized views

```sql
CREATE MATERIALIZED VIEW daily_active_users
PARTITION BY event_date
AS SELECT event_date, COUNT(DISTINCT user_id) AS dau
FROM events
GROUP BY event_date;
```

- BigQuery refreshes automatically on base-table writes.
- Query planner transparently rewrites queries against the base table to use the MV when it helps.
- Works best for aggregate-heavy, low-cardinality group-by patterns.

### Slot tuning and reservations

- On-demand billing: pay per byte scanned. Good for intermittent workloads.
- Reservations (flat-rate): buy slots; share across projects. Good for steady ETL + BI workloads.
- Use `--dry_run` / `bq query --dry_run` to estimate bytes scanned before running.
- Inspect slot usage: `INFORMATION_SCHEMA.JOBS_BY_PROJECT` → `total_slot_ms / TIMESTAMP_DIFF(end_time, start_time, MILLISECOND)`.

### Diagnostic views

```sql
-- Most expensive queries today
SELECT job_id, total_bytes_processed, total_slot_ms, query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND state = 'DONE'
ORDER BY total_bytes_processed DESC LIMIT 20;

-- Partition pruning health
SELECT table_name, total_rows, total_partitions, total_logical_bytes
FROM `my_dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'events';
```

## Redshift

### Distribution styles and dist keys

- `DISTSTYLE KEY DISTKEY (user_id)` — co-locates rows with matching `user_id` on the same node; speeds up joins on that key.
- `DISTSTYLE ALL` — replicates the table on every node; use for small dim tables (<3M rows) that join often.
- `DISTSTYLE EVEN` — round-robin; default; use when there's no dominant join key.
- `DISTSTYLE AUTO` — Redshift picks and switches as the table grows.
- Wrong dist key → "distribution" step dominates `EXPLAIN`; check with `SVV_TABLE_INFO.skew_rows`.

### Sort keys — compound vs interleaved

- `COMPOUND SORTKEY (event_time, event_type)` — best when queries filter on a prefix (event_time first, then event_type). Most common.
- `INTERLEAVED SORTKEY (event_time, user_id, event_type)` — when queries filter on any single column. More expensive to maintain.
- Inspect sort health: `SVV_TABLE_INFO.unsorted` should stay below 10%.

### Vacuum and analyze

- `VACUUM FULL events TO 95 PERCENT;` — reclaim space and re-sort after heavy writes. Run weekly for large append-heavy tables.
- `ANALYZE events;` — refresh stats for the planner. Run after large loads.
- Skip `VACUUM` on tables where `unsorted` stays low and nothing is being deleted.

### WLM and query queues

- Split workloads into queues: `etl` (high memory, low concurrency), `bi` (low memory, high concurrency), `default` (everything else).
- Set query monitoring rules (QMR) to abort queries exceeding `query_execution_time` or `scan_row_count` to protect the cluster from runaways.
- Enable short query acceleration (SQA) — Redshift auto-detects sub-second queries and routes to a dedicated queue.

### Diagnostic views

```sql
-- Slow queries today
SELECT query, elapsed, rows, bytes
FROM SVL_QLOG
WHERE starttime > GETDATE() - INTERVAL '1 day'
ORDER BY elapsed DESC LIMIT 20;

-- Table skew and unsorted ratio
SELECT "table", size, skew_rows, unsorted
FROM SVV_TABLE_INFO
WHERE schema = 'public' ORDER BY size DESC;

-- Disk usage per query
SELECT query, SUM(blocks_to_disk) AS spilled_mb
FROM SVL_QUERY_SUMMARY
WHERE is_diskbased = 't'
GROUP BY query ORDER BY spilled_mb DESC LIMIT 10;
```
