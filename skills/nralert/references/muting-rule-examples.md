# Muting Rule Examples

> **When to load:** Authoring a non-trivial muting rule — recurring windows, multi-attribute scope, faceted conditions, incident-response one-shots, or when debugging why a rule isn't matching.

## Contents

- Filter DSL reference
- Scope patterns (account / policy / condition / entity / tag)
- Faceted-condition mutes
- Recurring maintenance windows
- Incident-response one-shots
- Dynamic scope via tag queries
- Edge cases and gotchas
- Validation and debugging

## Filter DSL reference

Muting rule `condition` is a boolean tree of attribute comparisons.

| Attribute | Example values | Notes |
|---|---|---|
| `accountId` | `"1234567"` | Numeric strings; use for multi-account setups |
| `policyName` | `"payments-prod"` | Exact match; case-sensitive |
| `policyIds` | `["123", "456"]` | Prefer IDs over names — survives renames |
| `conditionName` | `"HTTP 5xx error rate"` | Mutes all facets of a faceted condition |
| `conditionType` | `"STATIC"`, `"BASELINE"` | Filter by condition kind |
| `entity.guid` | `"MXxBUE18..."` | Single entity; most precise |
| `entity.name` | `"payments-api"` | Use with `CONTAINS` for fleets |
| `tags.<NAME>` | `tags.team = "payments"` | Entity tag; case-sensitive on key and value |
| `targetName` | `"my-service"` | Legacy; prefer `entity.*` |

### Operators

| Operator | Multi-value? | Use for |
|---|---|---|
| `EQUALS` | no | Exact single match |
| `NOT_EQUALS` | no | Exclude one value |
| `IN` | yes (≤500) | Whitelist of values |
| `NOT_IN` | yes (≤500) | Blacklist of values |
| `CONTAINS` | no | Substring match (entity name patterns) |
| `STARTS_WITH` | no | Prefix match |
| `ENDS_WITH` | no | Suffix match |
| `ANY` | — | Match if attribute exists |

### Boolean composition

```graphql
condition: {
  operator: AND
  conditions: [
    { attribute: "tags.environment", operator: EQUALS, values: ["prod"] }
    { attribute: "tags.team",        operator: EQUALS, values: ["payments"] }
  ]
}
```

Only one level of nesting — no nested `AND`/`OR` trees. If you need OR across independent filter sets, create separate rules.

## Scope patterns

### 1. Account-wide (emergency brake)

Do **not** do this casually — use only during major incidents and set a short `endTime`.

```graphql
condition: { operator: AND, conditions: [
  { attribute: "accountId", operator: EQUALS, values: ["ACCOUNT_ID"] }
]}
```

### 2. Single policy

```graphql
condition: { operator: AND, conditions: [
  { attribute: "policyIds", operator: IN, values: ["POLICY_ID"] }
]}
```

### 3. Specific condition inside a policy

```graphql
condition: { operator: AND, conditions: [
  { attribute: "policyIds",     operator: IN, values: ["POLICY_ID"] }
  { attribute: "conditionName", operator: EQUALS, values: ["Checkout latency"] }
]}
```

### 4. Single entity (host, service, browser app)

```graphql
condition: { operator: AND, conditions: [
  { attribute: "entity.guid", operator: EQUALS, values: ["MXxBUE18QVBQTENDQVRJT058..."] }
]}
```

### 5. Fleet by name pattern

```graphql
condition: { operator: AND, conditions: [
  { attribute: "entity.name", operator: STARTS_WITH, values: ["prod-worker-"] }
]}
```

### 6. Tag-based (team ownership)

```graphql
condition: { operator: AND, conditions: [
  { attribute: "tags.team",        operator: EQUALS, values: ["data-platform"] }
  { attribute: "tags.environment", operator: EQUALS, values: ["staging"] }
]}
```

## Faceted-condition mutes

A faceted condition fires one issue per facet (e.g., per host, per URL). Muting `conditionName` silences the whole condition across all facets. Muting one facet needs the facet attribute.

```graphql
# Silence only the "checkout" facet of a FACET'd condition
condition: { operator: AND, conditions: [
  { attribute: "conditionName",        operator: EQUALS, values: ["HTTP latency by endpoint"] }
  { attribute: "tags.endpoint",        operator: EQUALS, values: ["checkout"] }
]}
```

The facet attribute appears as `tags.<FACET_NAME>` on the incident. Look it up in `Alerts > Issues & activity > Alert events` to confirm the exact key.

## Recurring maintenance windows

### Weekly — every Sunday 02:00–06:00 ET

```graphql
schedule: {
  startTime: "2024-01-01T02:00:00"
  endTime:   "2024-01-01T06:00:00"
  timeZone:  "America/New_York"
  repeat:    WEEKLY
  weeklyRepeatDays: [SUNDAY]
}
```

### Daily — every night 23:00–01:00 UTC

```graphql
schedule: {
  startTime: "2024-01-01T23:00:00"
  endTime:   "2024-01-02T01:00:00"
  timeZone:  "UTC"
  repeat:    DAILY
}
```

### Monthly — first of month, 00:00–02:00

```graphql
schedule: {
  startTime: "2024-01-01T00:00:00"
  endTime:   "2024-01-01T02:00:00"
  timeZone:  "UTC"
  repeat:    MONTHLY
}
```

### Bounded recurrence — end after 6 months

```graphql
schedule: {
  startTime: "2024-01-01T02:00:00"
  endTime:   "2024-01-01T06:00:00"
  timeZone:  "UTC"
  repeat:    WEEKLY
  weeklyRepeatDays: [SATURDAY]
  endRepeat: "2024-07-01T00:00:00"
}
```

## Incident-response one-shots

Created during active incidents. **Always** set a tight `endTime` (≤4 h) and include the incident ID in the name for audit.

```graphql
mutation {
  alertsMutingRuleCreate(accountId: ACCOUNT_ID, rule: {
    name: "INC-4821: suppress checkout pages during DB failover"
    description: "Slack thread: https://slack.com/..."
    enabled: true
    condition: { operator: AND, conditions: [
      { attribute: "policyIds",      operator: IN,     values: ["123", "456"] }
      { attribute: "tags.service",   operator: EQUALS, values: ["checkout"] }
    ]}
    schedule: {
      startTime: "2024-03-15T14:00:00"
      endTime:   "2024-03-15T17:00:00"
      timeZone:  "UTC"
    }
  }) { id }
}
```

## Dynamic scope via tag queries

Prefer tag-based rules over hard-coded entity GUIDs. When the fleet grows, the rule still applies without edits.

```graphql
# Mute everything tagged as "canary" — new canaries inherit automatically
condition: { operator: AND, conditions: [
  { attribute: "tags.deployment_tier", operator: EQUALS, values: ["canary"] }
]}
```

Works when entities carry consistent tags via Terraform or agent config. If tags drift, the rule quietly mis-scopes — audit tags quarterly.

## Edge cases and gotchas

| Case | Behavior |
|---|---|
| Muting rule created after an issue opened | Existing open issue still notifies on close; only new incidents are muted |
| Rule disabled mid-window | Active mute ends immediately; pending incidents fire |
| Overlapping rules | Most permissive wins — if any active rule matches, the incident is muted |
| Rule matches but workflow has `mutingRulesHandling: NOTIFY_ALL_ISSUES` | Workflow overrides mute; incident notifies anyway |
| Time zone with DST | Use IANA names (`America/New_York`) — handles DST. Fixed offsets (`-05:00`) drift |
| `endTime` in the past at create | API accepts but rule never activates — validate client-side |
| Tag value with special chars (`/`, `:`) | Quote correctly; test with `alertsMutingRule` query before trusting |
| Rule name duplicate | API allows duplicates — enforce uniqueness in your Terraform/automation layer |

## Validation and debugging

### 1. Query the rule back

```graphql
{
  actor { account(id: ACCOUNT_ID) { alerts { mutingRule(id: RULE_ID) {
    name enabled status
    condition { operator conditions { attribute operator values } }
    schedule   { startTime endTime timeZone repeat weeklyRepeatDays nextStartTime nextEndTime }
  }}}}
}
```

`status` is `ACTIVE` / `INACTIVE` / `SCHEDULED` / `ENDED`. `nextStartTime` / `nextEndTime` confirm the scheduler parsed your input correctly.

### 2. Test against a known incident

Copy an incident's attributes from `Alerts > Issues & activity > Alert events` (use **View attributes**). Walk them through the rule's filter tree by hand. Every condition in the `AND` must match.

### 3. Check attribute case

`policyName` matches; `policyname` does not. `tags.Team` matches; `tags.team` does not. Copy the attribute key from the event, never retype.

### 4. Verify the schedule in the target time zone

```graphql
# `nextStartTime` is returned in UTC — confirm it matches your intent
schedule { nextStartTime nextEndTime }
```

### 5. Simulate before enabling for recurring rules

Set `enabled: false`, wait one recurrence, query the rule and confirm `nextStartTime` advanced. Then enable.
