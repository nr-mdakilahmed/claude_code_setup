# OpenMetadata Chunk-Based Validation Patterns

## Contents

- Method 1: manual chunk processing
- Method 2: using `run()` with callbacks
- Transaction-safe processing
- Chunk-based validation warnings
- Two-phase approach

## Method 1: Manual Chunk Processing

```python
import pandas as pd
from metadata.sdk.data_quality.dataframes.dataframe_validator import DataFrameValidator
from metadata.sdk.data_quality.dataframes.validation_results import ValidationResult

validator = DataFrameValidator()
validator.add_openmetadata_table_tests("Postgres.warehouse.staging.transactions")

results = []
for chunk in pd.read_csv("large_file.csv", chunksize=10000):
    result = validator.validate(chunk)
    results.append(result)

    if result.success:
        load_chunk_to_database(chunk)
    else:
        rollback_all_chunks()
        break

# Merge and publish
final_result = ValidationResult.merge(*results)
final_result.publish("Postgres.warehouse.staging.transactions")
```

## Method 2: Using run() with Callbacks

```python
from metadata.sdk.data_quality.dataframes.dataframe_validator import DataFrameValidator
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, insert, delete

validator = DataFrameValidator()
validator.add_openmetadata_table_tests("Postgres.warehouse.staging.orders")

engine = create_engine("postgresql://user:pass@localhost/warehouse")

def load_chunk(df, validation_result):
    """Called on successful validation"""
    with engine.connect() as conn:
        table = Table("orders", MetaData(), autoload_with=conn)
        conn.execute(insert(table), df.to_dict(orient="records"))

def handle_failure(df, validation_result):
    """Called on validation failure - rollback"""
    with engine.connect() as conn:
        table = Table("orders", MetaData(), autoload_with=conn)
        conn.execute(delete(table))
    print(f"Validation failed: {validation_result}")

# Run with callbacks
result = validator.run(
    pd.read_csv("orders.csv", chunksize=5000),
    on_success=load_chunk,
    on_failure=handle_failure,
)

result.publish("Postgres.warehouse.staging.orders")
```

## Transaction-Safe Processing

```python
class DatabaseSession:
    def __init__(self, connection_string, table_name):
        self.engine = create_engine(connection_string)
        self.table_name = table_name

    def __enter__(self):
        self._conn = self.engine.connect()
        self._trans = self._conn.begin()
        self.table = Table(self.table_name, MetaData(), autoload_with=self._conn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._trans.rollback()
        else:
            self._trans.commit()
        self._conn.close()

    def load_chunk(self, df, result):
        self._conn.execute(insert(self.table), df.to_dict(orient="records"))

    def rollback(self, df, result):
        self._trans.rollback()

# Usage
with DatabaseSession("postgresql://...", "sales") as session:
    result = validator.run(
        pd.read_csv("data.csv", chunksize=10000),
        on_success=session.load_chunk,
        on_failure=session.rollback,
    )
```

## Chunk-Based Validation Warnings

Some tests require full dataset and may give incorrect results on chunks:
- `TableRowCountToBeBetween` - counts per chunk, not total
- `ColumnValuesSumToBeBetween` - sums per chunk, not total

**Recommended: Two-Phase Approach**

```python
# Phase 1: Column-level validation during ETL
chunk_validator = DataFrameValidator()
chunk_validator.add_tests(
    ColumnValuesToBeNotNull(column="id"),
    ColumnValuesToBeUnique(column="id"),
)
result = chunk_validator.run(chunks, on_success=load, on_failure=rollback)

# Phase 2: Table-level validation after loading
if result.success:
    table_validator = TestRunner.for_table("Postgres.warehouse.transactions")
    table_validator.add_tests(
        TableRowCountToBeBetween(min_count=10000),
        ColumnValuesSumToBeBetween(column="amount", min_value=1000000),
    )
    table_results = table_validator.run()
```
