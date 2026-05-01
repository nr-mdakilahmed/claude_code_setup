---
name: nralert
description: Configures New Relic alert intelligence — correlation decisions, muting rules, issue preferences, signal loss, gap filling, and Smart Alerts coverage. Triggers when the user asks about alert correlation, muting rules, issue preferences, Smart Alerts, topology correlation, signal loss, gap filling, suppression, or noise reduction.
when_to_use: Auto-trigger for New Relic alert configuration, correlation strategy, or noise-reduction work. Pairs with /terraform when the resulting conditions/workflows are authored in HCL.
---

# New Relic Alert Intelligence

Turns Claude into an alert-intelligence configurator: picks correlation scope, muting scope, and signal-loss tuning before wiring anything up, and routes condition/workflow authoring to Terraform when appropriate.

**Freedom level: Medium** — A preferred pattern exists for each decision (issue preference, correlation window, signal-loss threshold) but numbers and scope depend on service topology and data cadence.

## 1. Correlate Before Paging

**Group related incidents into one issue; route the issue, not each incident.**

- Set Layer 1 (per policy) to `PER_CONDITION_AND_SIGNAL` — most granular; prevents unrelated signals from merging into one noisy issue.
- Set Layer 2 (cross-policy correlation decisions) to group issues sharing cause: same entity, same error class, same downstream service.
- Keep correlation windows tight: 5–20 min. Wider windows merge unrelated incidents.
- "One policy for everything" → "Policy per team or service; correlate across policies with decisions".

## 2. Mute With Expiration

**Every muting rule has an end time. No permanent mutes.**

- Use `endTime` for one-shot maintenance; `endRepeat` for recurring windows.
- Scope narrowly: filter by `policyName`, `conditionName`, `entity.guid`, or `tags.<NAME>` — never mute a whole account.
- Faceted conditions need `tags.FACETED_ATTRIBUTE` to mute one facet; muting `conditionName` silences all facets.
- "Mute forever" → "Schedule with `endRepeat: WEEKLY` + `weeklyRepeatDays` and revisit every quarter".

## 3. Signal Loss Needs A Baseline

**Set `expirationDuration` to 2–3× the reporting interval; never leave at default.**

- Pair `expirationDuration` with `openViolationOnExpiration: true` so silence triggers a page when the service crashed.
- For sparse data (health checks, batch jobs), add `fillOption: STATIC, fillValue: 0` to stop flapping.
- Validate: query the condition's NRQL over 24 h; pick a duration that covers 99th-percentile gap between data points.
- "Default 60 s on a 5-min reporting source" → "`expirationDuration: 900` (3× the cadence)".

## 4. Topology Over Tags

**Correlate via entity relationships (service map) before reaching for tag filters.**

- Topology correlation is auto-discovered from distributed tracing, infra agent, K8s integration — it survives renames and ownership changes.
- Use tag filters only when topology is incomplete or when grouping crosses entity types (APM + infra + synthetic).
- Custom vertices/edges via NerdGraph (`aiTopologyCollectorCreateVertices/Edges`) when auto-discovery misses a link.
- Simulate every new decision against 7 days of history before activating.

## Quick reference — Signal-loss tuning

| Reporting cadence | `expirationDuration` | `fillOption` | When |
|---|---|---|---|
| Every 10–30 s (APM, infra) | 60–120 s | none | Default; tight detection |
| Every 1 min (custom metric) | 180–300 s | none | Allow one missed report |
| Every 5 min (batch, cloud integration) | 900 s | `STATIC, fillValue: 0` | Prevent flapping on sparse data |
| Hourly (job completion) | 3600–7200 s | none | Signal loss = job failed |
| Synthetic monitor | 2× monitor period | none | One missed run triggers |

## Two-layer architecture

```
Incidents -> [Layer 1: Issue Preference] -> Issues -> [Layer 2: Correlation] -> Merged Issues -> Workflow -> Notifications
```

- **Layer 1** (per policy): `PER_CONDITION_AND_SIGNAL` recommended. Alternatives: `PER_POLICY` (one issue per policy; loud) or `PER_CONDITION` (one per condition; medium).
- **Layer 2** (global): 12 built-in correlation decisions + custom decisions (basic or advanced builder).

## Feature decision guide

| Need | Feature | Authored in |
|---|---|---|
| Reduce notification volume | Issue preference | Terraform |
| Group related cross-policy issues | Correlation decisions | NerdGraph |
| Silence during maintenance | Muting rules | Terraform or NerdGraph |
| Auto-detect coverage gaps | Smart Alerts | New Relic UI only |
| Detect one entity deviating from peers | Outlier condition | Terraform |
| Prevent false silences on crash | Signal loss config | Terraform |
| Smooth sparse / flappy data | Gap filling | Terraform |

## Terraform vs NerdGraph — decision rule

**Author in Terraform when**: the resource is a policy, NRQL condition, workflow, destination, or muting rule that belongs in version control. Terraform covers ~80 % of day-to-day alert config and gives review/rollback.

**Author in NerdGraph when**: the resource is a correlation decision, custom topology vertex/edge, or a one-shot muting rule created during an incident. These are not covered by the Terraform provider as of today.

**Inline example — Terraform muting rule**:

```hcl
resource "newrelic_alert_muting_rule" "maintenance" {
  name        = "Nightly ETL Window"
  enabled     = true
  account_id  = var.account_id
  schedule {
    start_time = "2024-01-01T02:00:00"
    end_time   = "2024-01-01T06:00:00"
    time_zone  = "America/New_York"
    repeat     = "WEEKLY"
    weekly_repeat_days = ["SUNDAY"]
  }
  condition {
    operator = "AND"
    conditions {
      attribute = "policyName"
      operator  = "EQUALS"
      values    = ["etl-pipeline"]
    }
  }
}
```

**Inline example — NerdGraph muting rule** (one-shot, created during an incident):

```graphql
mutation {
  alertsMutingRuleCreate(accountId: ACCOUNT_ID, rule: {
    name: "Incident INC-1234 Hotfix", enabled: true
    condition: { operator: AND, conditions: [
      { attribute: "entity.guid", operator: EQUALS, values: ["MXxBUE18..."] }
    ]}
    schedule: { startTime: "2024-03-15T14:00:00", endTime: "2024-03-15T18:00:00", timeZone: "UTC" }
  }) { id }
}
```

**Inline example — Signal loss via NerdGraph**:

```graphql
mutation {
  alertsNrqlConditionStaticUpdate(accountId: ACCOUNT_ID, id: CONDITION_ID, condition: {
    expiration: { expirationDuration: 900, openViolationOnExpiration: true, closeViolationsOnExpiration: false }
    signal:     { fillOption: STATIC, fillValue: "0" }
  }) { id name }
}
```

**Inline example — Issue preference workflow** (NerdGraph):

```graphql
mutation {
  aiWorkflowsCreateWorkflow(accountId: ACCOUNT_ID, createWorkflowData: {
    name: "Payments team pager"
    issuesFilter: { type: FILTER, predicates: [
      { attribute: "labels.policyIds", operator: EXACTLY_MATCHES, values: ["POLICY_ID"] }
    ]}
    destinationConfigurations: [{ channelId: "CHANNEL_ID", notificationTriggers: [ACTIVATED, CLOSED] }]
    mutingRulesHandling: NOTIFY_ALL_ISSUES
  }) { id }
}
```

## Anti-patterns

| Pattern | Fix |
|---|---|
| Overly broad correlation (matches unrelated issues) | Scope with tag/entity filters; window 5–20 min |
| No signal-loss config on critical conditions | `expirationDuration: 2–3× cadence` + `openViolationOnExpiration: true` |
| Muting rule without expiration | Always set `endTime` or `endRepeat` |
| Alert on every metric | Smart Alerts coverage + 80/20: page on symptoms, ticket on causes |
| Static thresholds on variable workloads | Baseline condition (`upper_only`, std deviations) |
| One giant policy for the whole org | Policy per team/service; correlate across via decisions |
| Activating a correlation decision without simulation | Simulate against 7 days of history first |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Alert not firing | Check muting rules (`alertsMutingRules` query); verify NRQL in Query Builder; confirm condition is enabled |
| Too many false positives | Switch to baseline; widen aggregation window; use `percentile()` over `average()` |
| Correlation grouping wrong (unrelated issues merge) | Disable broad built-in decisions; tighten filter scope; drop window to 10 min; re-simulate |
| Muting rule "not working" | Verify attribute names (case-sensitive: `policyName` not `policyname`); check schedule time zone; confirm rule is enabled |
| Signal loss triggering on healthy service | `expirationDuration` < reporting cadence; raise to 2–3× the 95th-percentile gap |
| Topology correlation not propagating | Check `aiTopologyVertex`/`aiTopologyEdge` via NerdGraph; verify entity agent is reporting; add custom edges if link missing |
| Workflow ignores issue preference | Workflow filter matches raw `labels.policyIds`; verify policy IDs and that `mutingRulesHandling` is set correctly |
| Faceted condition mutes too much | Mute `tags.<FACET>` not `conditionName` |
| Smart Alerts created duplicate conditions | Add tag-based exclusion filters (e.g., `environment != dev`) before applying coverage |
| Gap filling hides real outages | Use `STATIC, fillValue: 0` only for sparse data; never on critical error-rate conditions |

## References

- `references/correlation-details.md` — custom decision builders, 9 similarity algorithms, topology correlation, Smart Alerts, Correlation Platform roadmap
- `references/nerdgraph-mutations.md` — full muting rule and signal loss mutation bodies (create, query, delete)
- `references/muting-rule-examples.md` — filter DSL, scope patterns, faceted-condition mutes, recurring schedules, incident-response examples

## Cross-references

| Skill | When |
|---|---|
| `terraform` | Author NRQL conditions, policies, workflows, destinations, and most muting rules as code. This skill picks the correlation/mute pattern; terraform applies it. |
| `nrql` | Write or optimize the condition query before wiring alert config around it |
