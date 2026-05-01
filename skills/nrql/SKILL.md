---
name: nrql
description: Writes, optimizes, and debugs NRQL for New Relic dashboards and alert conditions. Triggers when the user asks about writing NRQL queries, optimizing alert conditions, debugging slow NRQL queries, NRQL FACET, or NRQL aggregation — including empty results, timeouts, percentile/rate/percentage math, and alert-window tuning.
when_to_use: Auto-trigger for NRQL authoring or troubleshooting. Pairs with /nralert for correlation/muting wiring and /terraform when the condition/dashboard is authored in HCL.
---

# NRQL Query Craft

Turns Claude into an NRQL author: filters early with indexed attributes, picks the right aggregation before writing the query, and enforces alert-specific NRQL rules (no `TIMESERIES`, no `LIMIT` inside FACET alerts, no `SINCE`, no `COMPARE WITH`).

**Freedom level: Medium** — A preferred pattern exists per query shape (count, rate, percentile, funnel, eventstream), but thresholds, windows, and FACET cardinality depend on event volume and service topology.

## 1. SELECT Only What You Aggregate

**Every SELECT is an aggregation function over a filtered event set — never `SELECT *` and never raw attributes without a function.**

- Pick the function first: `count()` / `rate()` / `average()` / `percentile()` / `percentage()` / `filter()` / `funnel()`.
- `SELECT duration FROM Transaction` (row scan) → `SELECT percentile(duration, 50, 95, 99) FROM Transaction` (aggregated).
- `uniqueCount()` is expensive at high cardinality — use `count(*)` when exact uniqueness is not required.
- `latest()` on sparse attributes returns NULL — wrap with `coalesce(latest(attr), 0)`.

## 2. FACET Costs Cardinality

**Every FACET multiplies scan cost by the number of groups; keep it under 100 in dashboards, under 100 in alerts (LIMIT is silently ignored in alert FACETs).**

- Bucket continuous values with `FACET CASES(WHERE … AS 'Fast', WHERE … AS 'Slow')` rather than faceting raw latency.
- High-cardinality attributes (`request.id`, `userId`, `traceId`) never belong in FACET — filter on them in WHERE instead.
- Alert FACETs need the faceted attribute exposed as `tags.<NAME>` for muting rules to target one facet.
- `FACET appName, host` (cross-product) → separate charts or `FACET concat(appName, ':', host)` when the intent is a single series per pair.

## 3. Alert Windows Match Signal

**Aggregation window and evaluation offset are the alert; the NRQL is just the signal producer.**

- Error spike 1–5 min; latency 5–15 min; throughput 5–10 min; resource 5–15 min; business metric 15–60 min.
- Never include `SINCE` in alert NRQL — overridden by the condition's aggregation window and produces stale evaluations.
- Remove `TIMESERIES` — alert engine evaluates one value per window, not a series.
- Remove `COMPARE WITH` — not supported in alert conditions; use a baseline condition with std-deviation threshold.
- Pair signal-loss tuning (`expiration_duration`, `fill_option`) on the condition, not in NRQL (see `/nralert`).

## 4. Index Your WHERE

**Put an indexed attribute as the first WHERE predicate on every query that hits high-volume events.**

> Indexed attributes (fast filters): `appId`, `appName`, `entityGuid`, `host`, `hostname`, `transactionType`, `name`. Filter on these BEFORE any function call, `LIKE`, `RLIKE`, or arithmetic comparison.

- `WHERE duration > 1` alone → scans every Transaction row. `WHERE appName = 'MyApp' AND duration > 1` → scans only that app's slice.
- `RLIKE` is 3–10× slower than `LIKE`; replace with `LIKE 'prefix%'` or narrow by indexed filter first.
- Validate the keyset when unsure: `SELECT keyset() FROM Transaction SINCE 1 day ago`.
- Always include `SINCE` in dashboard queries — no `SINCE` defaults to a huge scan window.

## Query-shape chooser

Single lookup consulted on every invocation.

| Shape | Use | When |
|---|---|---|
| Count / rate | `count(*)` or `rate(count(*), 1 minute)` | Throughput, request volume, event frequency |
| Percentile | `percentile(duration, 50, 95, 99)` | Latency SLOs, tail-sensitive metrics |
| Percentage | `percentage(count(*), WHERE error IS true)` | Error rate, success rate, apdex-like ratios |
| Funnel | `funnel(session, WHERE step1, WHERE step2, …)` | Conversion, multi-step workflow drop-off |
| Eventstream | `SELECT ... FROM Log WHERE ... LIMIT 1000` | Raw log inspection, debugging, audit trail |

## Anti-patterns

| Pattern | Fix |
|---|---|
| `SELECT *` or raw attribute without aggregation | `SELECT count(*)` / `percentile()` / `average()` |
| `TIMESERIES` in alert NRQL | Remove; alert produces one value per window |
| `LIMIT` inside FACET alert | Remove; cap cardinality at the data source instead |
| `SINCE` in alert NRQL | Remove; use condition's aggregation window |
| `COMPARE WITH` in alert | Switch to baseline condition (`upper_only`, std deviations) |
| `RLIKE` on high-volume events | `LIKE 'prefix%'`, or filter indexed attrs first |
| `uniqueCount()` on high-cardinality attr | `count(*)` if exact uniqueness not required |
| Missing `SINCE` in dashboard | Add `SINCE 1 hour ago` — default scan is huge |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Query returns no data | `SHOW EVENT TYPES`; `SELECT uniques(appName, 100) FROM <Event> SINCE 1 day ago`; verify attribute casing (`appName` not `appname`) |
| Query timeout | Add indexed filter first; shorten `SINCE`; drop `RLIKE` for `LIKE`; avoid `uniqueCount()` on high cardinality |
| FACET explosion (thousands of groups) | `FACET CASES(…)` bucketing; narrow WHERE; confirm attribute is not an ID/UUID |
| Alert has NRQL but no data points | NRQL valid in Query Builder but empty in window → check casing, `SINCE` removed, event type agent is reporting |
| `percentage()` returns NULL | Outer `count(*)` is zero for the window — `coalesce(percentage(...), 0)` |
| `latest()` returns NULL | Sparse attribute in window — `coalesce(latest(attr), 0)` or widen window |
| Timezone confusion in `SINCE '2024-…'` | NRQL uses UTC by default; add `WITH TIMEZONE 'America/New_York'` at end of query |
| Indexed-attribute filter not applying | Verify spelling + case via `SELECT keyset() FROM <Event>`; `host` vs `hostname` varies by event type |
| Alert muting rule targets condition but not facet | Mute `tags.<FACETED_ATTR>` not `conditionName` (see `/nralert`) |
| `TIMESERIES` works in UI but alert silently fails | Alerts reject series output — remove `TIMESERIES`; use aggregation window |

## Diagnostic queries

```sql
SHOW EVENT TYPES SINCE 1 day ago
SELECT keyset() FROM Transaction SINCE 1 day ago
SELECT uniques(appName, 100) FROM Transaction SINCE 1 hour ago
SELECT count(*) FROM Transaction WHERE appName = 'MyApp' FACET name SINCE 1 hour ago LIMIT 10
```

## References

- `references/advanced-functions.md` — funnel queries, histogram bucketing, eventstream replay, percentile and percentage calculations with worked examples

## Cross-references

| Skill | When |
|---|---|
| `nralert` | Correlation, muting rules, signal-loss tuning around the condition |
| `terraform` | Author the NRQL condition/dashboard as HCL (`newrelic_nrql_alert_condition`, `newrelic_one_dashboard`) |
