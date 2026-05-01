# Structured Streaming Patterns

## Contents

- Read / write baseline
- Watermarks and late data
- Output modes
- Stateful aggregations
- Stream-stream joins
- Checkpointing and recovery
- Trigger tuning
- Anti-patterns

## Read / write baseline

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType

schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("event_time", TimestampType(), False),
    StructField("amount", DoubleType(), True),
])

events = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "latest")  # "earliest" only for replay/backfill
    .option("maxOffsetsPerTrigger", 1_000_000)  # backpressure
    .load()
    .select(F.from_json(F.col("value").cast("string"), schema).alias("e"))
    .select("e.*")
)

query = (
    events.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3://lake/_checkpoints/events_raw/")
    .option("mergeSchema", "false")  # explicit schema evolution only
    .trigger(processingTime="30 seconds")
    .start("s3://lake/bronze/events/")
)
```

Always set `checkpointLocation`. Always set an explicit schema on `from_json` — inferring on streams is non-deterministic.

## Watermarks and late data

Watermarks bound state. Without one, stateful operators grow forever.

```python
with_wm = events.withWatermark("event_time", "15 minutes")

windowed = (
    with_wm
    .groupBy(F.window("event_time", "5 minutes"), "user_id")
    .agg(F.sum("amount").alias("total"))
)
```

- Pick watermark = longest acceptable late-arrival window. Too tight → data loss; too loose → state bloat.
- Watermark is a lower bound on completeness, not exact; data older than `max(event_time) - watermark` is dropped silently.
- Monitor `eventTime.watermark` in `StreamingQueryProgress`; alert when it lags wall-clock by >1 hour.

## Output modes

| Mode | Use when | Restrictions |
|---|---|---|
| `append` | Each record emitted once; immutable sinks | Aggregations need watermark + window; no update semantics |
| `update` | Emit only changed rows of aggregations | Sink must support upsert (Delta merge, JDBC) |
| `complete` | Small result set rewritten each batch | Full table fits in memory; dashboards only |

Delta sinks: `append` for raw, `update` (via `foreachBatch` + merge) for silver/gold aggregations.

## Stateful aggregations

Two knobs matter for state cost:

1. **Watermark tightness** — state retained until `watermark` passes the window end.
2. **Key cardinality** — 10M distinct users × 5-min windows × 24h retention = 2.88B state rows.

```python
# State store config (RocksDB recommended for large state)
spark.conf.set(
    "spark.sql.streaming.stateStore.providerClass",
    "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",
)
spark.conf.set("spark.sql.streaming.stateStore.rocksdb.compactOnCommit", "true")
```

Use RocksDB when state >1 GB per partition; the default HDFS-backed store OOMs.

## Stream-stream joins

Require watermarks on **both** sides and a time-range join predicate:

```python
impressions_wm = impressions.withWatermark("imp_time", "2 hours")
clicks_wm      = clicks.withWatermark("click_time", "3 hours")

joined = impressions_wm.join(
    clicks_wm,
    F.expr("""
        imp_id = click_imp_id
        AND click_time BETWEEN imp_time AND imp_time + INTERVAL 1 HOUR
    """),
    how="leftOuter",
)
```

Outer joins emit `null` on the unmatched side once the watermark passes the range — so there is always latency equal to the range bound.

## Checkpointing and recovery

- One checkpoint directory per query. Never share.
- Deleting the checkpoint restarts the query from `startingOffsets` — treat as destructive.
- Checkpoints encode the query plan; most plan changes (new aggregations, changed output schema) break recovery and require a new checkpoint.
- Safe changes: adding filters on existing columns, changing trigger interval, changing sink options.

## Trigger tuning

| Trigger | Latency | Use when |
|---|---|---|
| `processingTime="30 seconds"` | ~seconds | Steady throughput; most production |
| `processingTime="1 minute"` | minute | Cost-sensitive batch-like streams |
| `availableNow=True` | one-shot | Backfill / catch-up; replaces `Trigger.Once` |
| `continuous="1 second"` (experimental) | ms | Only map-only pipelines; limited sink support |

`availableNow` processes all data currently available then stops — ideal for scheduled "micro-batch-but-streaming" jobs in Airflow.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| No watermark on aggregation | Add `.withWatermark()`; otherwise state grows unbounded |
| Shared checkpoint between queries | One checkpoint per `writeStream` |
| `startingOffsets=earliest` in prod | Use `latest` for new streams; `earliest` only for backfill |
| `foreachBatch` without idempotency | Make the batch function idempotent — Spark may retry |
| Schema inference on JSON stream | Declare `StructType` explicitly |
| `complete` output mode on large aggregation | Switch to `update` with Delta merge |
| No `maxOffsetsPerTrigger` on Kafka | Add backpressure; otherwise first batch OOMs after outage |
