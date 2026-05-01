# OpenMetadata Test Definition Classes

## Contents

- Table-level tests (SDK classes)
- Column-level tests (SDK classes)
- YAML test types (workflow config)
- YAML parameter notes
- Test status values

## Table-Level Tests

| Class | Parameters |
|-------|------------|
| `TableRowCountToBeBetween` | `min_count`, `max_count` |
| `TableRowCountToEqual` | `row_count` |
| `TableColumnCountToBeBetween` | `min_count`, `max_count` |
| `TableColumnCountToEqual` | `column_count` |
| `TableColumnNameToExist` | `column_name` |
| `TableColumnToMatchSet` | `column_names`, `ordered` |
| `TableRowInsertedCountToBeBetween` | `min_count`, `max_count`, `range_type`, `range_interval` |
| `TableCustomSQLQuery` | `sql_expression`, `strategy` |
| `TableDiff` | `table2`, `key_columns`, `use_columns`, `threshold` |

## Column-Level Tests

| Class | Parameters |
|-------|------------|
| `ColumnValuesToBeNotNull` | `column` |
| `ColumnValuesToBeUnique` | `column` |
| `ColumnValuesToBeInSet` | `column`, `allowed_values` |
| `ColumnValuesToBeNotInSet` | `column`, `forbidden_values` |
| `ColumnValuesToMatchRegex` | `column`, `regex` |
| `ColumnValuesToNotMatchRegex` | `column`, `regex` |
| `ColumnValuesToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValueMaxToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValueMinToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValueMeanToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValueMedianToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValueStdDevToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValuesSumToBeBetween` | `column`, `min_value`, `max_value` |
| `ColumnValuesMissingCount` | `column`, `missing_count_value`, `missing_value_match` |
| `ColumnValueLengthsToBeBetween` | `column`, `min_length`, `max_length` |

## YAML Test Types (Workflow Config)

### Column-Level Tests

| Test Type | Description | Parameters |
|-----------|-------------|------------|
| `columnValuesToBeBetween` | Values within range | `minValue`, `maxValue` |
| `columnValuesToBeNotNull` | No NULL values | None |
| `columnValuesToBeUnique` | All values unique | None |
| `columnValuesToMatchRegex` | Match regex | `regex` |
| `columnValuesToNotMatchRegex` | Not match regex | `regex` |
| `columnValuesToBeInSet` | Values in set | `allowedValues` |
| `columnValuesToBeNotInSet` | Values not in set | `forbiddenValues` |
| `columnValueLengthsToBeBetween` | String length range | `minLength`, `maxLength` |
| `columnValuesMissingCount` | Missing count threshold | `missingCountValue` |
| `columnValuesSumToBeBetween` | Sum within range | `minValueForSumInCol`, `maxValueForSumInCol` |
| `columnValuesMeanToBeBetween` | Mean within range | `minValueForMeanInCol`, `maxValueForMeanInCol` |
| `columnValuesMedianToBeBetween` | Median within range | `minValueForMedianInCol`, `maxValueForMedianInCol` |
| `columnValuesStdDevToBeBetween` | Std dev within range | `minValueForStdDevInCol`, `maxValueForStdDevInCol` |
| `columnValueMaxToBeBetween` | Max within range | `minValueForMaxInCol`, `maxValueForMaxInCol` |
| `columnValueMinToBeBetween` | Min within range | `minValueForMinInCol`, `maxValueForMinInCol` |

### Table-Level Tests

| Test Type | Description | Parameters |
|-----------|-------------|------------|
| `tableRowCountToBeBetween` | Row count range | `minValue`, `maxValue` |
| `tableRowCountToEqual` | Exact row count | `value` |
| `tableColumnCountToBeBetween` | Column count range | `minColValue`, `maxColValue` |
| `tableColumnCountToEqual` | Exact column count | `columnCount` |
| `tableColumnToMatchSet` | Expected columns | `columnNames`, `ordered` |
| `tableColumnNameToExist` | Column exists | `columnName` |
| `tableCustomSQLQuery` | Custom SQL validation | `sqlExpression`, `strategy`, `threshold` |
| `tableDiff` | Compare two tables | `table2`, `keyColumns`, `useColumns` |
| `tableRowInsertedCountToBeBetween` | Freshness check | `minValue`, `maxValue`, `columnName`, `rangeType` |

## YAML Parameter Notes

All parameter values must be **strings** in YAML:

```yaml
# CORRECT
parameterValues:
  - name: minValue
    value: "100"  # String

# INCORRECT - will fail
parameterValues:
  - name: minValue
    value: 100    # Integer NOT supported
```

### Array Parameters (JSON format)

```yaml
parameterValues:
  - name: allowedValues
    value: "[\"A\", \"B\", \"C\"]"  # JSON array as string

  - name: keyColumns
    value: "[\"id\", \"date\"]"
```

## Test Status Values

| Status | Description |
|--------|-------------|
| `Success` | Test passed all validation criteria |
| `Failed` | Test did not meet validation criteria |
| `Aborted` | Test execution was interrupted |
