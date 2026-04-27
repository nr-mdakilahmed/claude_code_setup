---
name: nralert
description: >
  Use when configuring alert correlation decisions, muting rules, issue preferences,
  topology correlation, or Smart Alerts coverage. Covers New Relic alert intelligence,
  signal loss, gap filling, suppression, and noise reduction.
  Auto-triggers for New Relic alert configuration or correlation.
---

# New Relic Alert Intelligence

## Phased Workflow

**Phase 1 — Design**: Choose issue preference, correlation approach, alert philosophy.
**Phase 2 — Configure**: Set up correlation decisions, muting rules, signal loss.
> Read `references/correlation-details.md` for similarity algorithms, custom decision builders, topology.
> Read `references/nerdgraph-mutations.md` for muting rule and signal loss NerdGraph APIs.
**Phase 3 — Tune**: Review alert quality, reduce noise, adjust thresholds.

## Two-Layer Architecture

```
Incidents -> [Layer 1: Issue Preference] -> Issues -> [Layer 2: Correlation] -> Merged Issues -> Notifications
```

**Layer 1** (per policy): `PER_CONDITION_AND_SIGNAL` recommended (most granular).
**Layer 2** (cross-policy): Groups related issues using 12 built-in global decisions.

## Signal Loss & Gap Filling

**Signal Loss** (service crashes, data stops): Set `expirationDuration: 90` + `openViolationOnExpiration: true`.
**Gap Filling** (sparse data causes flapping): `fillOption: STATIC` + `fillValue: 0`.

## Muting Rules

Suppress notifications (not data). Alert events still recorded.

**Key filters**: `conditionName`, `policyName`, `entity.guid`, `tags.<NAME>`, `targetName`
**Operations**: `EQUALS`, `IN` (up to 500), `CONTAINS`, `STARTS_WITH`
**Always set expiration**: `endTime` or `endRepeat` — never permanent mutes.
**Faceted conditions**: Use `tags.FACETED_ATTRIBUTE` to mute specific facets.

## Decision Guide

| Need | Feature | Terraform? |
|---|---|---|
| Reduce notification volume | Issue Creation Preference | Yes |
| Group related cross-policy | Correlation Decisions | No (NerdGraph) |
| Silence during maintenance | Muting Rules | Yes |
| Auto-detect coverage gaps | Smart Alerts | No (UI only) |
| Detect entity vs peers | Outlier Detection | Yes (NRQL condition) |
| Prevent false silences | Signal Loss config | Yes |
| Smooth sparse data | Gap Filling | Yes |

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Overly broad correlation | Scope with filters; tight window (5-20 min) |
| No signal loss config | `expirationDuration: 90`, `openViolationOnExpiration: true` |
| Muting without expiration | Always set `endTime` or `endRepeat` |
| Alert on every metric | Smart Alerts coverage; 80/20 rule |
| Static thresholds for variable workloads | Use baseline conditions |
| One giant policy | Policy per team/service; `PER_CONDITION_AND_SIGNAL` |
| Not testing correlation | Always simulate (7-day replay) before activating |

## Troubleshooting

| Issue | Fix |
|---|---|
| Alert not firing | Check muting rules; verify query in Query Builder; confirm `expirationDuration` |
| Too many false positives | Baseline condition; increase window; use `average()`/`percentile()` |
| Correlation grouping wrong | Disable broad globals; tighten filters; reduce window |
| Muting rule not working | Verify attributes (case-sensitive); check timezone |
| Signal loss triggering wrong | 2-3x reporting interval; enable gap filling |
| Notifications not delivering | Test destination; check Alert Quality Management |

## Cross-References

| Skill | When |
|---|---|
| `nrql` | Optimizing NRQL for alert conditions |
| `terraform` | Deploying conditions, policies, workflows |
