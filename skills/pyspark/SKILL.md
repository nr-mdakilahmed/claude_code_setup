---
name: pyspark
description: >
  Use when writing PySpark jobs, optimizing joins, handling data skew, tuning partitions,
  working with Delta Lake, or debugging Spark performance. Covers PB-scale patterns,
  AQE, broadcast joins, salting, window functions, and structured streaming.
  Auto-triggers when working with PySpark or Spark code.
---

# PySpark Optimization

## Session Config (Production Baseline)

```python
spark = (SparkSession.builder
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "auto")
    .config("spark.sql.files.maxPartitionBytes", "128m")
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    .getOrCreate())
```

## Partition Strategy

Target: **128MB per partition, 2-4 partitions per core**.

```python
# Repartition: full shuffle — use when INCREASING or rebalancing
df = df.repartition(400, "user_id")

# Coalesce: no shuffle — use when DECREASING (before write)
df = df.coalesce(100)
```

## Join Optimization

| Join Type | When | Trigger |
|---|---|---|
| Broadcast hash | Small side < 100MB | `broadcast(small_df)` |
| Sort-merge | Both sides large | Default for large-large |
| Bucket join | Repeated joins on same key | Pre-bucket both tables |

```python
from pyspark.sql.functions import broadcast
result = fact_df.join(broadcast(dim_df), "dim_key")
```

### Skew Handling (Salting)

```python
SALT_RANGE = 10
salted_left = (left_df
    .withColumn("salt", F.explode(F.array([F.lit(i) for i in range(SALT_RANGE)])))
    .withColumn("salted_key", F.concat("key", F.lit("_"), "salt")))

salted_right = (right_df
    .withColumn("salt", (F.rand() * SALT_RANGE).cast("int"))
    .withColumn("salted_key", F.concat("key", F.lit("_"), "salt")))

result = salted_left.join(salted_right, "salted_key").drop("salt", "salted_key")
```

## UDF Rules

**Always prefer built-in functions** (10-100x faster than UDFs).

```python
# BAD: Python UDF
@udf(StringType())
def clean_name(name): return name.strip().title()

# GOOD: Built-in
df = df.withColumn("name", F.initcap(F.trim("name")))

# OK: Pandas UDF when built-ins can't do it
@pandas_udf("double")
def custom_metric(values: pd.Series) -> pd.Series:
    return values.rolling(7).mean().fillna(0)
```

## Delta Lake

```python
# UPSERT (Merge)
target = DeltaTable.forPath(spark, "s3://lake/users/")
(target.alias("t")
    .merge(updates.alias("s"), "t.user_id = s.user_id")
    .whenMatchedUpdate(set={"email": "s.email", "updated_at": "s.updated_at"})
    .whenNotMatchedInsertAll()
    .execute())

# Maintenance
delta_table.optimize().executeCompaction()
delta_table.optimize().executeZOrderBy("user_id")
delta_table.vacuum(retentionHours=168)
```

## Testing (chispa)

```python
@pytest.fixture(scope="session")
def spark():
    return (SparkSession.builder
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate())

def test_transform(spark):
    input_df = spark.createDataFrame([("alice", 100)], ["name", "amount"])
    expected = spark.createDataFrame([("ALICE", 100)], ["name", "amount"])
    assert_df_equality(transform(input_df), expected, ignore_row_order=True)
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| `collect()` on large DataFrame | `.take(n)`, `.show()`, or write to storage |
| Python UDF for simple ops | Built-in functions: `F.when()`, `F.regexp_replace()` |
| `df.count()` in loop | Cache count once |
| `repartition(1)` before write | `coalesce()` or accept multiple files |
| No partition pruning on read | Add `WHERE date =` or `.filter()` |
| `toPandas()` on large DataFrame | Enable Arrow, limit rows |
| Unhandled skew in joins | Salt keys or enable AQE skew join |
| `SELECT *` from wide table | Select only needed columns |
| Nested `withColumn` calls | Use `select()` with all columns at once |
| No schema on read | Provide explicit `StructType` schema |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `OutOfMemoryError` heap | Increase memory, avoid `collect()`, reduce broadcast |
| Container killed by YARN | Increase `spark.executor.memoryOverhead` to 20% |
| One task 100x slower | Data skew — salt key or enable AQE |
| Task not serializable | Use broadcast variables or make class Serializable |
| Job hangs at last tasks | Enable `spark.speculation=true` |
| Slow writes, many small files | `coalesce()` before write or Delta OPTIMIZE |
