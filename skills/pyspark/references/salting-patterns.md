# Salting Patterns for Skewed Joins

## Contents

- When to salt
- Symmetric salting (explode + random)
- Asymmetric salting (only-skewed-keys)
- Salt-range tuning
- Aggregation after salting
- Verifying the fix
- Anti-patterns

## When to salt

Salt when one or more keys dominates the join:

- One task runs 10x–100x longer than the p50 task in the same stage.
- Spark UI shows a single reducer reading >5 GB while peers read <100 MB.
- AQE's `skewJoin.enabled` is on but the skewed partition exceeds `skewedPartitionThresholdInBytes` (default 256MB) and AQE still can't split it (e.g., inside a non-inner join, or after a window).

AQE handles most skew automatically in Spark 3.2+. Salt only when AQE has demonstrably failed.

## Symmetric salting (explode + random)

Use when both sides have the skewed key and you need a full join. Each left row is duplicated `SALT_RANGE` times; each right row picks one random bucket.

```python
from pyspark.sql import functions as F

SALT_RANGE = 20  # rule of thumb: 10–50; larger = more parallelism, more shuffle

salted_left = (
    left_df
    .withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_RANGE)])))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt"))
)

salted_right = (
    right_df
    .withColumn("salt", (F.rand() * SALT_RANGE).cast("int"))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt"))
)

result = (
    salted_left.join(salted_right, "salted_key")
    .drop("salt", "salted_key")
)
```

Cost: left side grows `SALT_RANGE`x. Do not salt every key — only the skewed ones. Use asymmetric salting below for that.

## Asymmetric salting (only-skewed-keys)

Far more efficient when 1–10 keys cause all the pain. Detect skewed keys first, then salt only those.

```python
# 1. Identify skew (one-time diagnostic)
skewed_keys = (
    left_df.groupBy("key").count()
    .filter("count > 1000000")  # tune threshold to your data
    .select("key")
    .rdd.map(lambda r: r[0])
    .collect()
)
skewed_broadcast = spark.sparkContext.broadcast(set(skewed_keys))

# 2. Split each side into skewed + normal
def is_skewed(col):
    return F.col(col).isin(*skewed_keys) if skewed_keys else F.lit(False)

left_skew  = left_df.filter(is_skewed("key"))
left_norm  = left_df.filter(~is_skewed("key"))
right_skew = right_df.filter(is_skewed("key"))
right_norm = right_df.filter(~is_skewed("key"))

# 3. Salt only the skewed side; union back
left_skew_salted = (
    left_skew
    .withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_RANGE)])))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt"))
)
right_skew_salted = (
    right_skew
    .withColumn("salt", (F.rand() * SALT_RANGE).cast("int"))
    .withColumn("salted_key", F.concat_ws("_", "key", "salt"))
)

skew_join   = left_skew_salted.join(right_skew_salted, "salted_key").drop("salt", "salted_key")
normal_join = left_norm.join(right_norm, "key")

result = skew_join.unionByName(normal_join)
```

## Salt-range tuning

| Symptom | SALT_RANGE |
|---|---|
| Still one hot task | double (20 → 40) |
| Shuffle bytes doubled with no speedup | halve (20 → 10) |
| Join output has duplicates | salt logic error — verify left explode, right random |
| Memory pressure after salt | reduce range; switch to asymmetric |

Start at 20. Re-measure p50 and p95 task duration; stop when the ratio is <3x.

## Aggregation after salting

For `groupBy + agg` on a skewed key, two-stage aggregation is usually faster than salting the join:

```python
# Stage 1: aggregate within salt buckets
stage1 = (
    df
    .withColumn("salt", (F.rand() * SALT_RANGE).cast("int"))
    .groupBy("key", "salt")
    .agg(F.sum("amount").alias("partial"))
)

# Stage 2: combine across buckets
final = stage1.groupBy("key").agg(F.sum("partial").alias("total"))
```

Each stage shuffles less data than a single skewed `groupBy`. Only valid for associative aggregations (`sum`, `count`, `max`, `min`).

## Verifying the fix

1. Re-run. Spark UI → Stages tab → find the join stage.
2. Check "Summary Metrics" for the shuffle read stage: p75/max duration ratio should be <3 after salting (often >100 before).
3. Confirm total job time dropped. Salting always adds shuffle cost; if wall time didn't improve, revert.
4. Compare row counts pre- and post- fix (sanity — salt errors silently duplicate or drop rows).

## Anti-patterns

| Anti-pattern | Why it hurts |
|---|---|
| Salting every key | Explodes left side globally; pays skew cost on non-skewed keys for nothing |
| Static `SALT_RANGE = 100` | Over-shuffling; tune to actual skew ratio |
| Using `F.rand()` without `seed` in tests | Non-deterministic output; tests become flaky |
| Forgetting to drop `salt` / `salted_key` | Downstream joins fail on extra columns |
| Salting with AQE's skewJoin already handling it | Wasted effort; measure AQE first |
| Salting a broadcast-eligible join | Just broadcast the small side |
