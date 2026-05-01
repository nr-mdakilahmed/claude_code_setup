---
name: sql
description: Reviews, refactors, and writes SQL for cloud data warehouses at senior data-engineering standards. Triggers when Claude writes Snowflake / BigQuery / Redshift queries, designs warehouse tables, builds dbt models, tunes query cost, or debugs slow queries. Covers partitioning, clustering, materialization choice, incremental strategies, and warehouse-specific tuning.
when_to_use: Auto-trigger when the user asks to write, review, optimize, or debug SQL for Snowflake, BigQuery, Redshift, or dbt. Invoke explicitly with /sql for a cost-and-performance pass.
paths:
  - "**/*.sql"
  - "**/models/**/*.sql"
  - "**/dbt_project.yml"
  - "**/schema.yml"
---

# Data Warehouse SQL

Turns Claude into a senior warehouse engineer: rejects full scans, enforces partition / cluster discipline, picks the right materialization for the access pattern, and sanity-checks cost before shipping a query.

**Freedom level: High** — query optimization admits many valid approaches and the warehouse engine picks tactics; the skill directs judgment with principles, not fixed recipes.

## 1. Filter Early, Project Late

**Prune rows before they hit a join; prune columns before they leave a CTE.**

- Put partition / cluster-key predicates in the **first** `WHERE` in every CTE — never rely on the planner to push them down through a `UNION` or window.
- "`SELECT *`" → "explicit column list" — every `SELECT *` in a production model is a review block.
- Filter in the subquery, not the outer join — fact-dim joins should hit a pre-filtered fact.
- "`WHERE cast(event_date AS string) = '2025-01-01'`" → "`WHERE event_date = DATE '2025-01-01'`" — type coercion on the left side kills partition pruning.

## 2. Pick Materialization For Access Pattern

**View for freshness, table for reuse, incremental for volume, ephemeral for composition.**

- Match materialization to how the model is **read**, not how it's built — a dashboard hit 10k/day needs a table, not a view over a view.
- Incrementals earn their complexity only above ~10M rows/day or when a full refresh exceeds the SLA.
- Ephemeral (dbt) inlines into the caller — use it for reusable CTE logic, never for anything a dashboard queries directly.
- Snapshots capture slowly-changing dims; do not fake them with `ROW_NUMBER() OVER (PARTITION BY … ORDER BY updated_at DESC)` if SCD-2 semantics matter.

## 3. Own The Query Plan

**Read the plan before blaming the warehouse. The plan tells the truth; intuition does not.**

- Inspect with `EXPLAIN` (Snowflake / BigQuery dry-run / Redshift `EXPLAIN`) before optimizing — never guess the bottleneck.
- Spot the four common plan failures: missing partition filter, broadcast-became-shuffle, skew in a join key, exploding CROSS JOIN via `UNNEST`.
- Re-run after every non-trivial edit and diff bytes-scanned / compile time — regressions that look like "same result" often double cost.
- If the plan shows re-scan of a wide table, CTE it once at the top and reference it — the planner will not always cache it.

## 4. Partition And Cluster Deliberately

**Partition by the filter column; cluster by the join / group-by column.**

- Partition by the column every query puts in `WHERE` — usually an event date. One partition column; avoid high-cardinality multi-column partitions.
- Cluster (Snowflake) / cluster-by (BigQuery) / sort-key (Redshift) on the column used in joins or `GROUP BY` after partition pruning narrows the scan.
- Enforce `require_partition_filter = TRUE` (BigQuery) / use search optimization (Snowflake) / set `COMPOUND SORTKEY` (Redshift) — see `references/warehouse-specific.md`.
- Re-cluster is not free: trigger only when `SYSTEM$CLUSTERING_INFORMATION` or `VACUUM` shows actual drift.

## 5. Incremental For Volume, Not For Novelty

**Incremental models trade simplicity for throughput; pick the strategy that matches the write pattern.**

- Append-only event streams → `incremental_strategy='append'` with watermark filter.
- Late-arriving updates on a stable grain → `merge` with `unique_key` + lookback window.
- Partition replacement (BigQuery / Databricks) → `insert_overwrite` to rewrite today's partition idempotently.
- See `references/incremental-strategies.md` for the full matrix and warehouse support.

## Materialization quick reference

| When model is | Use | Trade-off |
|---|---|---|
| Small, always-fresh, read rarely | `view` | Slow query, zero storage, recomputes every read |
| Base fact / dim, read often | `table` | Fast read, stale until rebuild |
| Large append-heavy fact (>10M rows/day) | `incremental` | Fast build, complex logic, late-data risk |
| Reusable CTE inside other models | `ephemeral` | No object, inlined at compile, no perms to grant |
| SCD-2 dimension with history | `snapshot` | Captures change over time, requires `updated_at` column |

## Anti-patterns

| Pattern | Fix |
|---|---|
| `SELECT *` in production model | Explicit column list — reject the PR |
| String concat over join key (`a.id \|\| b.region = …`) | Multi-column `JOIN … ON a.id = b.id AND a.region = b.region` |
| Correlated subquery in `SELECT` against a large fact | Rewrite as `JOIN` or window function |
| Missing partition filter on the largest fact | Add `WHERE partition_col >= …` in every CTE that touches it |
| Type coercion on the left of `WHERE` | Cast the literal, not the column — preserves index / partition pruning |
| CTE defined but never referenced | Delete; the optimizer still parses and costs it in some engines |
| `ORDER BY` without `LIMIT` in a model | Drop the `ORDER BY` — models are unordered; order at the BI layer |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Query scans full table despite `WHERE event_date = '…'` | Column is `STRING`, not `DATE`; or filter is in outer query only — push into CTE |
| BigQuery "Resources exceeded: shuffle bytes" | Filter earlier; add cluster-by on join key; split into two stages |
| Snowflake query compile time > 10s | Too many CTEs or views stacked; materialize intermediate result as a `TRANSIENT` table |
| Redshift "out of memory" on sort | Add `DISTKEY` on join key to avoid redistribution; check skew with `SVV_DISKUSAGE` |
| Column-level permission error in production | Column added by an upstream model without a grant — check the `schema.yml` meta |
| dbt incremental shows duplicate rows | `incremental_strategy` is `append` but data has late updates — switch to `merge` with `unique_key` |
| dbt full-refresh works, incremental returns wrong rows | `is_incremental()` filter uses a column that isn't in the source — check source has watermark |
| BigQuery job uses 10× expected slots | `GROUP BY` on high-cardinality column without cluster-by; add cluster or approximate aggregation |
| Snowflake clustering depth > 4 | Table drifted; run `ALTER TABLE … RECLUSTER` or rethink cluster key |
| Test fails only on Jan 1 / month boundary | Date-window logic uses `CURRENT_DATE` without timezone; pin with `AT TIME ZONE 'UTC'` |

## Checklist

- [ ] No `SELECT *` in any production model
- [ ] Partition column filter in every CTE that touches the largest fact
- [ ] Joins hit pre-filtered subqueries, not raw tables
- [ ] Type-safe predicates — literals cast, columns untouched
- [ ] Materialization matches access pattern (not author preference)
- [ ] Incremental strategy matches write pattern — append / merge / insert_overwrite
- [ ] Cluster / sort / dist keys chosen for the actual join + group-by columns
- [ ] `EXPLAIN` / dry-run reviewed; bytes scanned within expected range
- [ ] Tests cover empty partition, late-arriving rows, and boundary dates
- [ ] No `ORDER BY` without `LIMIT`; no `UNION` where `UNION ALL` suffices

## References

- `references/incremental-strategies.md` — dbt `append` / `merge` / `insert_overwrite` / `delete+insert` selection, warehouse support matrix, late-arrival patterns
- `references/warehouse-specific.md` — Snowflake (micro-partitions, clustering, result cache), BigQuery (partition + cluster, approximate functions, slot tuning), Redshift (dist/sort keys, vacuum, WLM)

## Cross-references

| Skill | When |
|---|---|
| `python` | SQL embedded in Python — parameterize, never f-string |
| `airflow` | Scheduling dbt runs, sensors on warehouse tables |
| `nrql` | New Relic telemetry queries (NRQL is not SQL; do not mix) |
