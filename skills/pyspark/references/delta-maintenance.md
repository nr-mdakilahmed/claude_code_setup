# Delta Lake Maintenance

## Contents

- MERGE (upsert) patterns
- OPTIMIZE and file compaction
- Z-ORDER clustering
- VACUUM and retention
- Schema evolution
- Time travel and rollback
- Change Data Feed (CDF)
- Anti-patterns

## MERGE (upsert) patterns

```python
from delta.tables import DeltaTable

target = DeltaTable.forPath(spark, "s3://lake/silver/users/")

(
    target.alias("t")
    .merge(
        updates.alias("s"),
        "t.user_id = s.user_id AND t.region = s.region",  # include partition cols
    )
    .whenMatchedUpdate(
        condition="s.updated_at > t.updated_at",  # idempotent on replay
        set={"email": "s.email", "updated_at": "s.updated_at"},
    )
    .whenNotMatchedInsertAll()
    .whenNotMatchedBySourceDelete(condition="t.tombstone = true")  # rare
    .execute()
)
```

Rules:
- Always include partition columns in the merge key — Delta prunes files by them.
- Use `condition` on `whenMatchedUpdate` to make the merge idempotent (re-run produces same result).
- For large targets, deduplicate the source first: `updates.dropDuplicates(["user_id"])`.

## OPTIMIZE and file compaction

Small-file problem: each streaming micro-batch writes files <10 MB. Queries spend more time on metadata than data.

```python
# Compact all small files
spark.sql("OPTIMIZE delta.`s3://lake/silver/events/`")

# Compact only recent partitions (cheap daily job)
spark.sql("""
    OPTIMIZE delta.`s3://lake/silver/events/`
    WHERE event_date >= current_date() - INTERVAL 7 DAYS
""")
```

Target file size is 1 GB by default. Override for analytical tables:

```python
spark.conf.set("spark.databricks.delta.optimize.maxFileSize", 268_435_456)  # 256 MB
```

Run `OPTIMIZE` daily on hot partitions; weekly on cold.

## Z-ORDER clustering

Co-locates rows by columns used in range filters, improving file-skipping.

```python
spark.sql("""
    OPTIMIZE delta.`s3://lake/silver/events/`
    WHERE event_date >= current_date() - INTERVAL 7 DAYS
    ZORDER BY (user_id, session_id)
""")
```

When to Z-ORDER:
- 1–4 columns frequently used in `WHERE user_id = ...` or range scans.
- Table has >10 GB per partition; Z-ORDER pays off at scale.

When not to:
- High-cardinality ID already used as a partition — partitions already prune.
- Tiny tables (<1 GB) — no file-skipping win.

Databricks: use Liquid Clustering (`CLUSTER BY`) instead of Z-ORDER for new tables — reclusters incrementally.

## VACUUM and retention

```python
# Default retention = 7 days; Delta refuses shorter without override
spark.sql("VACUUM delta.`s3://lake/silver/events/` RETAIN 168 HOURS")
```

- VACUUM deletes files no longer referenced by the Delta log beyond retention.
- Breaks time travel for any version older than retention.
- Never set retention <24h on tables with active streaming readers — checkpoints may reference older files.
- Run weekly; more often on high-churn tables.

## Schema evolution

```python
# Opt-in per write (safer than autoMerge)
(
    df.write
    .option("mergeSchema", "true")
    .format("delta")
    .mode("append")
    .save("s3://lake/bronze/events/")
)

# Global for streaming — only when source schemas are controlled upstream
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

Safe evolutions (backward compatible):
- Adding nullable columns.
- Widening types: int → long, float → double.

Unsafe (require manual migration):
- Renaming columns (unless column mapping enabled).
- Narrowing types, dropping columns.
- Changing nullability to `false`.

## Time travel and rollback

```python
# Read prior version
df_prior = (
    spark.read.format("delta")
    .option("versionAsOf", 12345)
    .load("s3://lake/silver/users/")
)

# Restore to a version (irreversible — creates a new commit)
spark.sql("RESTORE TABLE delta.`s3://lake/silver/users/` TO VERSION AS OF 12345")

# Inspect history
spark.sql("DESCRIBE HISTORY delta.`s3://lake/silver/users/`").show(truncate=False)
```

Time travel is bounded by VACUUM retention. Use `DESCRIBE HISTORY` to audit user, operation, metrics, and options for every commit — invaluable for incident post-mortems.

## Change Data Feed (CDF)

Enable to stream row-level changes downstream without re-scanning.

```python
# Enable once
spark.sql("""
    ALTER TABLE delta.`s3://lake/silver/users/`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Read changes between versions
changes = (
    spark.read.format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 100)
    .option("endingVersion", 200)
    .load("s3://lake/silver/users/")
)
```

Returned columns: `_change_type` (`insert` / `update_preimage` / `update_postimage` / `delete`), `_commit_version`, `_commit_timestamp`.

Storage cost: CDF roughly doubles write amplification. Enable only when a consumer needs it.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| `OPTIMIZE` on full table nightly | Filter to hot partitions; cold data rarely changes |
| Z-ORDER on >5 columns | Diminishing returns; 1–4 columns max |
| `VACUUM RETAIN 0 HOURS` on streaming source | Breaks active checkpoints; set ≥ longest consumer lag |
| `mergeSchema` always on | Surprises downstream; enable per-write intentionally |
| `MERGE` without `s.updated_at > t.updated_at` | Non-idempotent; replays regress data |
| No partition filter in `MERGE` condition | Full-table scan per merge |
| Treating time travel as backup | Retention-bounded; take real backups for DR |
