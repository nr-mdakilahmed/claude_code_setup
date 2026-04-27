# New Relic Alert Intelligence — NerdGraph Mutations

> **When to load:** Phase 3 (Tune) — automating muting rules, signal loss, and gap filling via NerdGraph API.

## Muting Rules

```graphql
# Create muting rule
mutation {
  alertsMutingRuleCreate(
    accountId: ACCOUNT_ID
    rule: {
      name: "Maintenance Window"
      enabled: true
      condition: {
        operator: AND
        conditions: [{
          attribute: "policyName"
          operator: EQUALS
          values: ["my-policy"]
        }]
      }
      schedule: {
        startTime: "2024-01-01T02:00:00"
        endTime: "2024-01-01T06:00:00"
        timeZone: "America/New_York"
        repeat: WEEKLY
        weeklyRepeatDays: [SUNDAY]
      }
    }
  ) { id }
}

# Query muting rules
{
  actor {
    account(id: ACCOUNT_ID) {
      alerts {
        mutingRules {
          name
          enabled
          condition { operator conditions { attribute operator values } }
          schedule { startTime endTime repeat timeZone }
        }
      }
    }
  }
}

# Delete muting rule
mutation {
  alertsMutingRuleDelete(accountId: ACCOUNT_ID, id: RULE_ID) { id }
}
```

## Signal Loss + Gap Filling

```graphql
# Update condition with Signal Loss + Gap Filling
mutation {
  alertsNrqlConditionStaticUpdate(
    accountId: ACCOUNT_ID
    id: CONDITION_ID
    condition: {
      expiration: {
        expirationDuration: 90
        openViolationOnExpiration: true
        closeViolationsOnExpiration: false
      }
      signal: {
        fillOption: STATIC
        fillValue: "0"
      }
    }
  ) { id name }
}
```
