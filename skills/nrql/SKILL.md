---
name: nrql
description: >
  Use when writing NRQL queries, optimizing alert conditions, or debugging slow/empty queries
  in New Relic. Covers query patterns, aggregation functions, FACET, subqueries,
  alert-specific rules, and performance optimization.
  Auto-triggers when writing or optimizing NRQL queries.
---

# NRQL Optimization Patterns

## Query Structure

```sql
SELECT function(attribute)
FROM event_type
WHERE condition
SINCE time_range
FACET attribute
LIMIT number
```

## Performance: Filter Early with Indexed Attributes

Indexed (fast): `appId`, `appName`, `host`, `entityGuid`, `transactionType`, `name`

```sql
-- GOOD: Filter on indexed attributes first
SELECT average(duration) FROM Transaction
WHERE appName = 'MyApp' AND transactionType = 'Web'
SINCE 1 hour ago

-- AVOID: Broad queries without indexed filters
SELECT average(duration) FROM Transaction WHERE duration > 1
```

## Alert Query Patterns

```sql
-- Error rate
SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = 'MyApp'

-- Latency
SELECT average(duration) FROM Transaction WHERE appName = 'MyApp'

-- Throughput
SELECT rate(count(*), 1 minute) FROM Transaction WHERE appName = 'MyApp'

-- Conditional aggregation
SELECT filter(count(*), WHERE httpResponseCode >= 500) as 'Server Errors',
       filter(count(*), WHERE httpResponseCode < 400) as 'Success'
FROM Transaction WHERE appName = 'MyApp'

-- Infrastructure
SELECT average(cpuPercent) FROM SystemSample WHERE hostname LIKE 'prod-%'
```

## Alert-Specific Rules (CRITICAL)

- **No TIMESERIES** — alert engine evaluates single value per window
- **No LIMIT in FACET alerts** — silently truncates; keep cardinality under 100
- **No COMPARE WITH** — not supported in alerts; use baseline conditions
- **No SINCE** — overridden by aggregation window setting
- **No nested subqueries** in alerts — keep NRQL simple

## Time Windows for Alerts

| Alert Type | Window |
|---|---|
| Error spikes | 1-5 min |
| Latency degradation | 5-15 min |
| Throughput changes | 5-10 min |
| Resource usage | 5-15 min |
| Business metrics | 15-60 min |

## FACET Patterns

```sql
-- Custom buckets
SELECT count(*) FROM Transaction WHERE appName = 'MyApp'
FACET CASES(
  WHERE duration < 0.1 AS 'Fast',
  WHERE duration < 0.5 AS 'Normal',
  WHERE duration < 1 AS 'Slow',
  WHERE duration >= 1 AS 'Very Slow'
)
```

## Decision Guide

| Need | Approach |
|---|---|
| Error rate | `percentage()` with error filter |
| Throughput | `rate()` function |
| Latency percentiles | `percentile(duration, 50, 95, 99)` |
| Week-over-week (dashboards only) | `COMPARE WITH 1 week ago` |
| Custom event monitoring | `FROM CustomEvent` |
| Infrastructure | `FROM SystemSample` / `StorageSample` |
| Log analysis | `FROM Log WHERE level = 'ERROR'` |
| Funnel | `funnel(session, WHERE ...)` |

## Anti-Patterns

| Pattern | Fix |
|---|---|
| `TIMESERIES` in alert | Remove; use simple aggregation |
| `LIMIT` in alert FACET | Remove; keep cardinality < 100 |
| Short window (<30s) | 1-5 min minimum for stability |
| `SELECT *` | Select needed columns; use aggregations |
| No `SINCE` clause (dashboards) | Always include; reduces scan scope |
| `RLIKE` on high-volume events | Replace with `LIKE`; filter with indexed attrs first |
| `uniqueCount()` high cardinality | Use `count(*)` if exact uniqueness not needed |
| `latest()` on sparse attributes | `coalesce(latest(attr), 0)` |

## Troubleshooting

| Issue | Fix |
|---|---|
| Query returns no data | Verify event type: `SHOW EVENT TYPES`; check attrs: `SELECT uniques(appName)` |
| Unexpected NULL | `WHERE attr IS NOT NULL`; `coalesce(attr, 0)` |
| Query timeout | Add indexed filters; shorten time range; avoid `RLIKE` |
| FACET too many groups | `FACET CASES()`; add WHERE filters; `LIMIT` (max 5000) |
| percentage() wrong values | Test filter independently; `coalesce()` for NULL outer |
| Aggregation window mismatch | Don't include `SINCE` in alert NRQL — use condition config |

## Diagnostic Queries

```sql
SHOW EVENT TYPES
SELECT keyset() FROM Transaction SINCE 1 day ago
SELECT uniques(appName, 100) FROM Transaction SINCE 1 hour ago
```
