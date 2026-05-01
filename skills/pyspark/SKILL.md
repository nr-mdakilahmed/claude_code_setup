---
name: pyspark
description: Writes, optimizes, and debugs PySpark jobs at PB scale. Triggers when Claude edits Spark code, tunes joins or partitions, handles data skew, configures Delta Lake operations, writes structured streaming, or debugs Spark performance on Databricks or open-source clusters.
when_to_use: Auto-trigger on PySpark files. Invoke explicitly when diagnosing slow stages, skewed joins, small-file problems, AQE tuning, or Delta maintenance (OPTIMIZE/VACUUM/Z-ORDER).
paths:
  - "**/spark/**/*.py"
  - "**/*_spark.py"
  - "**/databricks/**/*.py"
---

# PySpark Optimization

Turns Claude into a senior Spark engineer: picks the right join strategy, kills skew, validates in notebooks but ships in jobs, and runs Delta maintenance before shipping.

**Freedom level: Medium** — Spark has preferred patterns (broadcast thresholds, salting, AQE, Delta ops) with known parameters. Claude selects between known options guided by decision tables, not free-form judgment.

## 1. Partition Before You Join

**Right-size partitions first; joins that follow become cheap.**

- Target **128 MB per partition, 2–4 partitions per core**. Deviation is the root cause of most "my Spark job is slow" tickets.
- `repartition(n, col)` when increasing or rebalancing (full shuffle). `coalesce(n)` when decreasing before a write (no shuffle).
- Set `spark.sql.files.maxPartitionBytes=128m` on reads; set `spark.sql.shuffle.partitions` to ~2–4× total cores (or `auto` with AQE).
- "No partition pruning on read" → "`.filter('date = ...')` before any join; verify with `explain()` for `PartitionFilters`".

## 2. Kill Skew With Salt

**Measure skew in the UI first; salt only the keys that hurt.**

- Check Spark UI → Stages → task duration p75/max ratio. >3 after AQE = real skew.
- AQE's `skewJoin.enabled` handles most cases in 3.2+. Salt only when AQE demonstrably fails (non-inner joins, post-window skew, or partition > `skewedPartitionThresholdInBytes`).
- Prefer **asymmetric salting**: identify the 1–10 offender keys, salt only those, `union` back with the normal-key join.
- "Salt every key with `SALT_RANGE=100`" → "Measure first; asymmetric salt at `SALT_RANGE=20`; retune only if p75/max still >3".

## 3. Prefer Broadcast, Then Built-Ins

**Small side <100 MB? Broadcast. Transform? Built-in functions. UDF is the last resort.**

- Broadcast hash join when the small side fits in memory post-filter. Built-ins beat Python UDFs 10–100×.
- Python UDF only when built-ins genuinely cannot express the logic. Use `pandas_udf` for vectorized paths.
- "`@udf` cleaning a string" → "`F.initcap(F.trim(col))`".
- "`collect()` on a large DataFrame" → "`.take(n)`, `.show()`, or write to storage".

## 4. Validate In Notebooks, Ship In Jobs

**Prototype in a notebook, but the merged artifact is a tested `.py` module with `chispa` assertions.**

- Use `chispa.assert_df_equality` with `ignore_row_order=True` for deterministic unit tests; never assert on `collect()` output order.
- Session fixture: `local[2]`, `spark.sql.shuffle.partitions=2`, `spark.ui.enabled=false` — tests run in seconds.
- Assert row counts, schema, and idempotency (re-running produces identical output) — not just "it ran".
- Delta maintenance (`OPTIMIZE`, `VACUUM`, `Z-ORDER`) belongs in a separately scheduled job, never inline with the write.

## Join-strategy selector

The single lookup consulted on every join.

| Situation | Strategy | How |
|---|---|---|
| Small side < 100 MB post-filter | Broadcast hash | `fact.join(F.broadcast(dim), "k")` |
| Both sides large, same key | Sort-merge (default) | AQE + adequate `shuffle.partitions` |
| Repeated joins on same key | Bucket join | Pre-bucket both tables on key |
| One key dominates the join | Salt (asymmetric) | See `references/salting-patterns.md` |
| Row-level lookup across small lookup table | Broadcast + `filter` | Broadcast the lookup, not the fact |

## AQE tuning

| Symptom | Knob | Value |
|---|---|---|
| Too many small shuffle partitions | `spark.sql.adaptive.coalescePartitions.enabled` | `true` (default in 3.2+) |
| Hot task after shuffle | `spark.sql.adaptive.skewJoin.enabled` | `true` + `skewedPartitionFactor=5` |
| AQE miscounts broadcast-eligibility | `spark.sql.adaptive.autoBroadcastJoinThreshold` | `100m` (raise cautiously) |
| Streaming query | AQE off | Not supported for continuous processing |

## Salting teaser

```python
# Inline teaser — full pattern (asymmetric, two-stage agg, verification) in
# references/salting-patterns.md
from pyspark.sql import functions as F
SALT_RANGE = 20
salted_left = (left_df
    .withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_RANGE)])))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt")))
salted_right = (right_df
    .withColumn("salt", (F.rand() * SALT_RANGE).cast("int"))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt")))
```

## Feedback loop

1. Write the transform; run `pytest` with `chispa` assertions locally.
2. **Validate immediately**: `spark.read.parquet(out).count()` matches expected; `explain("formatted")` shows broadcast/sort-merge as planned.
3. If skew or OOM: open Spark UI → Stages → fix the worst task first (partition, broadcast, or salt); rerun.
4. Ship only when row-count, schema, and idempotency assertions pass.

## Anti-patterns

| Pattern | Fix |
|---|---|
| `collect()` on large DataFrame | `.take(n)` / `.show()` / write to storage |
| Python UDF for simple ops | Built-ins: `F.when`, `F.regexp_replace`, `F.initcap` |
| `df.count()` inside a loop | Materialize once; cache if reused |
| `repartition(1)` before write | `coalesce(n)` or accept multiple files |
| No partition pruning on read | `.filter('date = ...')` before anything else |
| `toPandas()` on large DataFrame | Enable Arrow, `.limit(n)` first, or rethink |
| Unhandled skew in joins | Measure p75/max; AQE skewJoin → asymmetric salt |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `OutOfMemoryError` heap | Drop `collect()`/`toPandas()`; lower broadcast threshold; raise executor memory |
| Container killed by YARN/K8s | Raise `spark.executor.memoryOverhead` to 20% of executor memory |
| One task 100× slower than peers | Data skew — AQE `skewJoin`, then asymmetric salt |
| `Task not serializable` | Broadcast the object or make the class `Serializable` |
| Job hangs on final tasks | Speculation: `spark.speculation=true` (idempotent writes only) |
| Slow write, thousands of small files | `coalesce(n)` before write; `OPTIMIZE` on Delta hot partitions |
| Merge is slow and rewrites every file | Add partition cols to merge predicate; deduplicate source first |
| Streaming state grows unbounded | Add `.withWatermark()`; switch state store to RocksDB |
| AQE not kicking in | Confirm `spark.sql.adaptive.enabled=true`; AQE off for streaming |
| Delta `VACUUM` refuses <168h | `spark.databricks.delta.retentionDurationCheck.enabled=false` only if you own all readers |

## Checklist

- [ ] Partition size ~128 MB; `shuffle.partitions` ≈ 2–4× cores (or AQE `auto`)
- [ ] Filters pushed down before joins; `explain()` shows `PartitionFilters`
- [ ] Small-side join broadcast when <100 MB post-filter
- [ ] Skew measured in UI before salting; asymmetric salt when needed
- [ ] No `collect()` / `toPandas()` on large DataFrames
- [ ] Built-in functions used; UDFs only when built-ins fail
- [ ] Explicit schema on every `read` / `from_json` (streaming non-negotiable)
- [ ] Delta MERGE: partition cols in predicate + idempotent `whenMatched` condition
- [ ] OPTIMIZE + VACUUM scheduled as separate jobs, not inline
- [ ] `chispa` tests assert rows, schema, and idempotency — not execution success

## References

- `references/salting-patterns.md` — symmetric vs asymmetric salting, two-stage aggregation, verification
- `references/streaming-patterns.md` — structured streaming, watermarks, output modes, checkpoints
- `references/delta-maintenance.md` — MERGE, OPTIMIZE, Z-ORDER, VACUUM, schema evolution, CDF

## Cross-references

- See `/python` for general code-quality standards (typing, testing, SOLID).
- See `/sql` for warehouse-side query tuning and dbt patterns.
- See `/airflow` for scheduling Spark jobs and handling retries.
