# Advanced NRQL Functions

## Contents

- Funnel queries — multi-step conversion analysis
- Histogram bucketing — distribution analysis with `histogram()` and `FACET CASES`
- Eventstream replay — raw event reconstruction from Log / Span / CustomEvent
- Percentile calculations — latency SLOs, `percentile()` vs `average()` pitfalls
- Percentage calculations — ratios, NULL handling, denominator filters
- Rate and derivative — `rate()`, `derivative()`, `earliest()`/`latest()` deltas
- Subqueries and joins — `WITH` clause, nested aggregations, `JOIN` alternatives

---

## Funnel queries

Funnel measures sequential step conversion. Each `WHERE` inside `funnel()` is a step; the engine counts sessions that complete steps in order.

```sql
SELECT funnel(session,
  WHERE pageUrl LIKE '/product%'       AS 'Viewed product',
  WHERE pageUrl LIKE '/cart%'          AS 'Added to cart',
  WHERE pageUrl LIKE '/checkout%'      AS 'Started checkout',
  WHERE pageUrl LIKE '/confirmation%'  AS 'Completed purchase'
) FROM PageView
WHERE appName = 'Shop'
SINCE 1 day ago
```

Returns: absolute count per step + % of prior step + % of first step.

Rules:
- Identifier (`session`) must be present on every event in the chain. Sessions missing the ID are dropped from the funnel.
- Max 10 steps per funnel.
- Steps run in the **order written**, not the order events occurred — reorder to match the user journey.
- Use `funnel()` in dashboards only; not supported in alert conditions.

## Histogram bucketing

`histogram()` builds a distribution of a numeric attribute across a range; width determines bucket count.

```sql
SELECT histogram(duration, 10, 20) FROM Transaction
WHERE appName = 'MyApp' AND transactionType = 'Web'
SINCE 1 hour ago
```

Args: `(attribute, max_value, bucket_count)`. The above creates 20 buckets between 0 and 10 seconds.

When `histogram()` is not flexible enough (e.g., non-linear buckets), use `FACET CASES`:

```sql
SELECT count(*) FROM Transaction WHERE appName = 'MyApp'
FACET CASES(
  WHERE duration < 0.1  AS 'P50-ish (<100ms)',
  WHERE duration < 0.5  AS 'Normal (<500ms)',
  WHERE duration < 1    AS 'Slow (<1s)',
  WHERE duration < 5    AS 'Very slow (<5s)',
  WHERE duration >= 5   AS 'Pathological (≥5s)'
)
SINCE 1 hour ago
```

Rules:
- `histogram()` clips values above `max_value` into the top bucket — pick `max_value` from the actual p99, not a guess.
- `FACET CASES` evaluates top-to-bottom and assigns each row to the FIRST matching bucket. Order matters — widest (fallback) buckets last.
- Neither form works in alert NRQL; move bucketing to the alert threshold if needed (e.g., separate conditions for p95 vs p99).

## Eventstream replay

Eventstream is `SELECT attribute1, attribute2, … FROM <Event> LIMIT N` — raw rows, no aggregation. Only form where raw attributes are allowed in SELECT.

```sql
SELECT timestamp, level, message, entity.name, traceId
FROM Log
WHERE entity.name = 'payment-service' AND level = 'ERROR'
SINCE 30 minutes ago
LIMIT 1000
```

Rules:
- Always cap with `LIMIT` — max 2000 rows per query.
- Narrow to one entity and short `SINCE` before adding message filters; `LIKE '%timeout%'` on a 1-day window scans hard.
- For distributed tracing replay, pair with `FROM Span WHERE trace.id = 'X'` to reconstruct the request path.
- Eventstream is never valid in an alert condition — use `filter()` or `count()` with a threshold instead.

## Percentile calculations

`percentile(attribute, p1, p2, …)` returns one value per percentile requested.

```sql
SELECT percentile(duration, 50, 95, 99) FROM Transaction
WHERE appName = 'MyApp'
SINCE 1 hour ago
TIMESERIES 1 minute
```

Pitfalls:
- `average(duration)` hides tail latency. A p99 of 4s with an avg of 200ms is a real user problem that `average()` silently masks.
- `percentile()` is an approximation (HDR histogram); do not expect exact values on small samples (<1000 rows).
- In alerts, use `percentile()` with a single percentile arg: `percentile(duration, 95)`. Multiple percentiles in alert NRQL return a list and break threshold evaluation.
- For SLO alerts, baseline condition on p95/p99 beats static threshold on variable workloads.

## Percentage calculations

`percentage(numerator, WHERE filter)` = (filtered count / total count) * 100.

```sql
SELECT percentage(count(*), WHERE error IS true) AS 'Error rate'
FROM Transaction
WHERE appName = 'MyApp'
SINCE 5 minutes ago
```

Pitfalls:
- Outer count zero → `percentage()` returns NULL. Wrap: `coalesce(percentage(count(*), WHERE error IS true), 0)`.
- `WHERE` at the query level applies to BOTH numerator and denominator. Filter `appName = 'MyApp'` at query level, `error IS true` inside `percentage()`.
- For apdex-like ratios (satisfied / total), prefer `apdex(duration, t: 0.5)` over manual percentage math — it handles tolerating zone correctly.
- `filter()` is the multi-metric variant: `filter(count(*), WHERE httpResponseCode >= 500) AS '5xx'` + `filter(count(*), WHERE httpResponseCode < 400) AS '2xx/3xx'` in a single SELECT.

## Rate and derivative

`rate(count(*), 1 minute)` — normalized count per unit time. Useful when the aggregation window varies.

```sql
SELECT rate(count(*), 1 minute) FROM Transaction
WHERE appName = 'MyApp'
SINCE 1 hour ago
TIMESERIES
```

`derivative(attribute, 1 minute)` — change per unit time of a gauge metric (counter deltas).

```sql
SELECT derivative(sum.incoming_bytes, 1 minute) FROM Metric
WHERE hostname = 'web-01'
SINCE 30 minutes ago
TIMESERIES
```

Pitfalls:
- `rate()` on a counter that resets (pod restart, counter wrap) produces negative spikes — filter with `WHERE <counter> > 0` when needed.
- `derivative()` requires the metric to be monotonic within the window; if the source resets, use `rate()` on the delta event instead.
- In alerts, `rate()` is fine; `derivative()` works but is sensitive to missed data points — pair with signal-loss config.

## Subqueries and joins

NRQL has no true `JOIN`. Use `WITH` for named subquery or the nested `SELECT ... FROM (SELECT ...)` pattern.

```sql
-- Top 10 hosts by error count, then their p95 latency
WITH top_error_hosts AS (
  SELECT count(*) FROM Transaction
  WHERE error IS true
  FACET host
  SINCE 1 hour ago
  LIMIT 10
)
SELECT percentile(duration, 95)
FROM Transaction
WHERE host IN (FROM top_error_hosts SELECT host)
SINCE 1 hour ago
FACET host
```

Rules:
- `WITH` subqueries do not work in alert conditions — keep alert NRQL flat.
- For cross-event-type "joins", use `FROM Event1, Event2` with a common attribute (e.g., `traceId`). Not a true join — it unions and filters.
- When needing real joins, pull data via NerdGraph and join in the consuming code instead.
