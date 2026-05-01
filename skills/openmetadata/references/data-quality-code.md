# OpenMetadata — Data Quality as Code (1.11+)

> **When to load:** Phase 2 (Data Quality) — programmatic test building, running, and inline ETL validation using the Python SDK.

## Contents

- Requirements & configuration
- TestRunner API (table-level testing)
- Test metadata customization (fluent API)
- TestRunner configuration
- Processing results
- DataFrameValidator (inline ETL validation)
- Loading tests from YAML
- Best practices

**Requirements:** Python 3.10+, `openmetadata-ingestion>=1.11.0.0`, OpenMetadata 1.11.0+

```bash
pip install "openmetadata-ingestion[postgres,mysql,snowflake]>=1.11.0.0"
```

```python
from metadata.sdk import configure
configure(host="http://localhost:8585/api", jwt_token="your-jwt-token")
# Or use env vars: OPENMETADATA_HOST, OPENMETADATA_JWT_TOKEN
```

---

## TestRunner API (Table-Level Testing)

Executes data quality tests against tables cataloged in OpenMetadata.

```python
from metadata.sdk import configure
from metadata.sdk.data_quality import TestRunner
from metadata.sdk.data_quality import (
    TableRowCountToBeBetween,
    ColumnValuesToBeNotNull,
    ColumnValuesToBeUnique,
    ColumnValuesToMatchRegex,
    ColumnValuesToBeBetween,
)

configure(host="http://localhost:8585/api", jwt_token="your-token")

# Create runner for a table
runner = TestRunner.for_table("MySQL.ecommerce.public.customers")

# Add multiple tests
runner.add_tests(
    TableRowCountToBeBetween(min_count=1000, max_count=1000000),
    ColumnValuesToBeNotNull(column="customer_id"),
    ColumnValuesToBeNotNull(column="email"),
    ColumnValuesToBeUnique(column="customer_id"),
    ColumnValuesToMatchRegex(
        column="email",
        regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    ),
    ColumnValuesToBeBetween(column="age", min_value=18, max_value=120),
)

# Run all tests defined in UI (no add_tests needed)
runner = TestRunner.for_table("BigQuery.analytics.customer_360")
results = runner.run()
```

### Test Metadata Customization (Fluent API)

```python
test = ColumnValuesToBeNotNull(column="email") \
    .with_name("email_not_null_check") \
    .with_display_name("Email Not Null Validation") \
    .with_description("Ensures all customer records have email") \
    .with_compute_row_count(True)
```

### TestRunner Configuration

```python
from metadata.generated.schema.metadataIngestion.workflow import LogLevels

runner.setup(
    force_test_update=True,
    log_level=LogLevels.DEBUG,
    raise_on_error=False,
    success_threshold=90,
    enable_streamable_logs=True,
)
```

### Processing Results

```python
results = runner.run()

for result in results:
    test_case = result.testCase
    test_result = result.testCaseResult

    print(f"Test: {test_case.name.root}")
    print(f"Type: {test_case.testDefinition.name}")
    print(f"Status: {test_result.testCaseStatus}")  # Success, Failed, Aborted
    print(f"Result: {test_result.result}")

    if test_result.passedRows is not None:
        print(f"Passed: {test_result.passedRows} ({test_result.passedRowsPercentage}%)")
        print(f"Failed: {test_result.failedRows}")

all_passed = all(r.testCaseResult.testCaseStatus == "Success" for r in results)
```

---

## DataFrameValidator (Inline ETL Validation)

Validates pandas DataFrames before loading to destinations.

```python
import pandas as pd
from metadata.sdk import configure
from metadata.sdk.data_quality.dataframes.dataframe_validator import DataFrameValidator
from metadata.sdk.data_quality import (
    ColumnValuesToBeNotNull,
    ColumnValuesToBeUnique,
    ColumnValuesToBeBetween,
    ColumnValuesToMatchRegex,
)

configure(host="http://localhost:8585/api", jwt_token="your-token")

validator = DataFrameValidator()

validator.add_tests(
    ColumnValuesToBeNotNull(column="customer_id"),
    ColumnValuesToBeUnique(column="customer_id"),
    ColumnValuesToBeBetween(column="age", min_value=0, max_value=120),
    ColumnValuesToMatchRegex(
        column="email",
        regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    ),
)

# Load tests from OpenMetadata UI
validator.add_openmetadata_table_tests("BigQuery.analytics.staging.customers")

# Validate DataFrame
df = pd.read_csv("customers.csv")
result = validator.validate(df)

if result.success:
    load_to_warehouse(df)
else:
    for test_case, test_result in result.test_cases_and_results:
        if test_result.testCaseStatus != "Success":
            print(f"FAILED: {test_case.name.root}: {test_result.result}")

# Publish results to OpenMetadata
result.publish("Postgres.warehouse.public.customers")
```

---

## Loading Tests from YAML

```python
from metadata.sdk.data_quality import TestRunner

# From file
runner = TestRunner.from_yaml(file_path="tests/quality.yaml")

# From string
yaml_config = """
source:
  type: TestSuite
  serviceName: local_postgres
  sourceConfig:
    config:
      type: TestSuite
      entityFullyQualifiedName: Postgres.warehouse.public.customers

processor:
  type: orm-test-runner
  config:
    testCases:
      - name: email_not_null
        testDefinitionName: columnValuesToBeNotNull
        columnName: email

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://localhost:8585/api
    authProvider: openmetadata
    securityConfig:
      jwtToken: ${OPENMETADATA_JWT_TOKEN}
"""

runner = TestRunner.from_yaml(yaml_string=yaml_config)
results = runner.run()
```

---

## Best Practices

1. Use descriptive test names with `.with_name()` and `.with_description()`
2. Leverage UI-defined tests — let data stewards define criteria, run with `runner.run()`
3. Always publish results — `result.publish("Table.FQN")` enables tracking and alerting
4. Use transactional chunk processing with callbacks and rollback
5. Two-phase validation — column tests during ETL, table tests after load
6. Never hardcode credentials — use environment variables or `{{ ctx.secret }}` templates
