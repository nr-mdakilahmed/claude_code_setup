# New Relic Terraform — HCL Resource Examples

> **When to load:** Phase 3 (Implement) — writing provider config, alert conditions, workflows, dashboards.

## Provider Configuration

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    newrelic = {
      source  = "newrelic/newrelic"
      version = "~> 3.0"
    }
  }
}

provider "newrelic" {
  account_id = var.newrelic_account_id
  api_key    = var.newrelic_api_key
  region     = var.newrelic_region # US or EU
}
```

## NRQL Alert Condition (Static)

```hcl
resource "newrelic_nrql_alert_condition" "error_rate" {
  account_id                     = var.account_id
  policy_id                      = newrelic_alert_policy.main.id
  type                           = "static"
  name                           = "${var.service_name} - High Error Rate"
  enabled                        = true
  violation_time_limit_seconds   = 86400

  nrql {
    query = "SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '${var.app_name}'"
  }

  critical {
    operator              = "above"
    threshold             = var.error_threshold_critical
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  warning {
    operator              = "above"
    threshold             = var.error_threshold_warning
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120
  fill_option        = "none"

  # Signal loss handling
  expiration_duration            = 600
  open_violation_on_expiration   = true
  close_violations_on_expiration = false
}
```

## NRQL Alert Condition (Baseline/Anomaly)

```hcl
resource "newrelic_nrql_alert_condition" "latency_anomaly" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.main.id
  type                         = "baseline"
  name                         = "${var.service_name} - Latency Anomaly"
  enabled                      = true
  baseline_direction           = "upper_only"
  violation_time_limit_seconds = 86400

  nrql {
    query = "SELECT average(duration) FROM Transaction WHERE appName = '${var.app_name}'"
  }

  critical {
    operator              = "above"
    threshold             = 3 # standard deviations
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120
}
```

## Alert Policy

```hcl
resource "newrelic_alert_policy" "main" {
  name                = "${var.service_name} Policy"
  incident_preference = "PER_CONDITION_AND_TARGET"
}
```

## Notification Destination

```hcl
resource "newrelic_notification_destination" "slack" {
  account_id = var.account_id
  name       = "${var.service_name} Slack"
  type       = "SLACK"

  auth_basic {
    user     = ""
    password = var.slack_webhook_url
  }

  property {
    key   = "url"
    value = var.slack_webhook_url
  }
}

resource "newrelic_notification_destination" "pagerduty" {
  account_id = var.account_id
  name       = "${var.service_name} PagerDuty"
  type       = "PAGERDUTY_SERVICE_INTEGRATION"

  property {
    key   = "service_key"
    value = var.pagerduty_integration_key
  }
}

resource "newrelic_notification_destination" "email" {
  account_id = var.account_id
  name       = "${var.service_name} Email"
  type       = "EMAIL"

  property {
    key   = "email"
    value = var.alert_email
  }
}
```

## Notification Channel

```hcl
resource "newrelic_notification_channel" "slack" {
  account_id     = var.account_id
  name           = "${var.service_name} Slack Channel"
  type           = "SLACK"
  destination_id = newrelic_notification_destination.slack.id
  product        = "IINT"

  property {
    key   = "channelId"
    value = var.slack_channel_id
  }

  property {
    key   = "customDetailsSlack"
    value = jsonencode({
      blocks = [
        {
          type = "section"
          text = {
            type = "mrkdwn"
            text = "*{{ issueTitle }}*\nPriority: {{ priority }} | State: {{ state }}"
          }
        }
      ]
    })
  }
}
```

## Workflow

```hcl
resource "newrelic_workflow" "main" {
  account_id            = var.account_id
  name                  = "${var.service_name} Workflow"
  muting_rules_handling = "NOTIFY_ALL_ISSUES"
  enabled               = true

  issues_filter {
    name = "PolicyFilter"
    type = "FILTER"

    predicate {
      attribute = "labels.policyIds"
      operator  = "EXACTLY_MATCHES"
      values    = [newrelic_alert_policy.main.id]
    }
  }

  destination {
    channel_id = newrelic_notification_channel.slack.id
  }

  enrichments {
    nrql {
      name = "RecentErrors"
      configuration {
        query = "SELECT count(*) FROM TransactionError WHERE appName = '${var.app_name}' SINCE 10 minutes ago"
      }
    }
  }
}
```

## Dashboard

```hcl
resource "newrelic_one_dashboard" "main" {
  name        = "${var.service_name} Dashboard"
  permissions = "public_read_only"

  page {
    name = "Overview"

    widget_billboard {
      title  = "Error Rate"
      row    = 1
      column = 1
      width  = 3
      height = 2

      nrql_query {
        account_id = var.account_id
        query      = "SELECT percentage(count(*), WHERE error IS true) as 'Error %' FROM Transaction WHERE appName = '${var.app_name}'"
      }

      critical = 5
      warning  = 2
    }

    widget_line {
      title  = "Response Time"
      row    = 1
      column = 4
      width  = 9
      height = 3

      nrql_query {
        account_id = var.account_id
        query      = "SELECT average(duration), percentile(duration, 95) FROM Transaction WHERE appName = '${var.app_name}' TIMESERIES AUTO"
      }
    }

    widget_table {
      title  = "Top Transactions"
      row    = 4
      column = 1
      width  = 6
      height = 3

      nrql_query {
        account_id = var.account_id
        query      = "SELECT count(*), average(duration) FROM Transaction WHERE appName = '${var.app_name}' FACET name LIMIT 10"
      }
    }
  }

  variable {
    name                 = "environment"
    title                = "Environment"
    type                 = "nrql"
    default_values       = ["production"]
    replacement_strategy = "default"

    nrql_query {
      account_ids = [var.account_id]
      query       = "SELECT uniques(tags.environment) FROM Transaction WHERE appName = '${var.app_name}'"
    }
  }
}
```

## Muting Rule

```hcl
resource "newrelic_alert_muting_rule" "maintenance" {
  account_id  = var.account_id
  name        = "${var.service_name} Maintenance Window"
  enabled     = true
  description = "Mute during scheduled maintenance"

  condition {
    conditions {
      attribute = "policyId"
      operator  = "EQUALS"
      values    = [newrelic_alert_policy.main.id]
    }
  }

  schedule {
    start_time = var.maintenance_start
    end_time   = var.maintenance_end
    time_zone  = "UTC"
  }
}
```

## Data Sources

```hcl
data "newrelic_entity" "app" {
  name   = var.app_name
  type   = "APPLICATION"
  domain = "APM"
}

data "newrelic_alert_policy" "existing" {
  name = "Existing Policy Name"
}
```

## Dynamic Alert Conditions (for_each)

```hcl
locals {
  alert_conditions = {
    error_rate = {
      query     = "SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '${var.app_name}'"
      critical  = 5
      warning   = 2
      operator  = "above"
    }
    latency = {
      query     = "SELECT average(duration) FROM Transaction WHERE appName = '${var.app_name}'"
      critical  = 2
      warning   = 1
      operator  = "above"
    }
    throughput = {
      query     = "SELECT rate(count(*), 1 minute) FROM Transaction WHERE appName = '${var.app_name}'"
      critical  = 10
      warning   = 50
      operator  = "below"
    }
  }
}

resource "newrelic_nrql_alert_condition" "dynamic" {
  for_each = local.alert_conditions

  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.main.id
  type                         = "static"
  name                         = "${var.service_name} - ${replace(title(each.key), "_", " ")}"
  enabled                      = true
  violation_time_limit_seconds = 86400

  nrql {
    query = each.value.query
  }

  critical {
    operator              = each.value.operator
    threshold             = each.value.critical
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  warning {
    operator              = each.value.operator
    threshold             = each.value.warning
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120
}
```

## Lifecycle Block Example

```hcl
resource "newrelic_alert_policy" "critical" {
  name                = "${var.service_name} Critical Policy"
  incident_preference = "PER_CONDITION_AND_TARGET"

  lifecycle {
    prevent_destroy = true
  }
}

resource "newrelic_nrql_alert_condition" "error_rate" {
  # ... condition config ...

  lifecycle {
    # Avoid destroy+recreate when only name changes
    ignore_changes = [name]
  }
}
```

## Alerting Module

```hcl
# modules/alerting/main.tf
resource "newrelic_alert_policy" "this" {
  name                = "${var.service_name}-${var.environment}"
  incident_preference = "PER_CONDITION_AND_TARGET"
}

resource "newrelic_nrql_alert_condition" "error_rate" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.this.id
  type                         = "static"
  name                         = "${var.service_name} - Error Rate"
  enabled                      = var.enabled
  violation_time_limit_seconds = 86400

  nrql {
    query = "SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '${var.app_name}'"
  }

  critical {
    operator              = "above"
    threshold             = var.error_threshold_critical
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  warning {
    operator              = "above"
    threshold             = var.error_threshold_warning
    threshold_duration    = 300
    threshold_occurrences = "all"
  }

  aggregation_window = 60
  aggregation_method = "event_flow"
  aggregation_delay  = 120

  expiration_duration            = 600
  open_violation_on_expiration   = true
  close_violations_on_expiration = false
}

# modules/alerting/variables.tf
variable "account_id"               { type = number }
variable "service_name"             { type = string }
variable "app_name"                 { type = string }
variable "environment"              { type = string }
variable "enabled"                  { type = bool, default = true }
variable "enable_baseline"          { type = bool, default = true }
variable "error_threshold_critical" { type = number, default = 5 }
variable "error_threshold_warning"  { type = number, default = 2 }
variable "latency_threshold_critical" { type = number, default = 2 }
variable "latency_threshold_warning"  { type = number, default = 1 }

# modules/alerting/outputs.tf
output "policy_id" {
  value = newrelic_alert_policy.this.id
}

output "condition_ids" {
  value = {
    error_rate = newrelic_nrql_alert_condition.error_rate.id
    latency    = newrelic_nrql_alert_condition.latency.id
    baseline   = try(newrelic_nrql_alert_condition.latency_baseline[0].id, null)
  }
}
```

## Workflow Module

```hcl
# modules/workflow/main.tf
resource "newrelic_notification_destination" "slack" {
  account_id = var.account_id
  name       = "${var.name}-slack"
  type       = "SLACK"

  auth_basic {
    user     = ""
    password = var.slack_webhook_url
  }

  property {
    key   = "url"
    value = var.slack_webhook_url
  }
}

resource "newrelic_notification_channel" "slack" {
  account_id     = var.account_id
  name           = "${var.name}-slack-channel"
  type           = "SLACK"
  destination_id = newrelic_notification_destination.slack.id
  product        = "IINT"

  property {
    key   = "channelId"
    value = var.slack_channel_id
  }
}

resource "newrelic_workflow" "this" {
  account_id            = var.account_id
  name                  = var.name
  muting_rules_handling = "NOTIFY_ALL_ISSUES"
  enabled               = var.enabled

  issues_filter {
    name = "PolicyFilter"
    type = "FILTER"

    predicate {
      attribute = "labels.policyIds"
      operator  = "EXACTLY_MATCHES"
      values    = var.policy_ids
    }
  }

  destination {
    channel_id = newrelic_notification_channel.slack.id
  }

  dynamic "enrichments" {
    for_each = var.enrichment_queries

    content {
      nrql {
        name = enrichments.value.name
        configuration {
          query = enrichments.value.query
        }
      }
    }
  }
}
```

## Root Module Usage

```hcl
# environments/prod/main.tf
provider "newrelic" {
  account_id = var.newrelic_account_id
  api_key    = var.newrelic_api_key
  region     = var.newrelic_region
}

locals {
  environment = "prod"

  services = {
    api    = { app_name = "production-api",    error_threshold = 5, latency_threshold = 1 }
    web    = { app_name = "production-web",    error_threshold = 3, latency_threshold = 2 }
    worker = { app_name = "production-worker", error_threshold = 2, latency_threshold = 5 }
  }
}

module "alerting" {
  source   = "../../modules/alerting"
  for_each = local.services

  account_id               = var.newrelic_account_id
  service_name             = each.key
  app_name                 = each.value.app_name
  environment              = local.environment
  enabled                  = true
  error_threshold_critical = each.value.error_threshold
  latency_threshold_critical = each.value.latency_threshold
}

module "workflow" {
  source = "../../modules/workflow"

  account_id        = var.newrelic_account_id
  name              = "${local.environment}-alerts"
  enabled           = true
  slack_webhook_url = var.slack_webhook_url
  slack_channel_id  = var.slack_channel_id
  policy_ids        = [for m in module.alerting : m.policy_id]

  enrichment_queries = [
    {
      name  = "RecentErrors"
      query = "SELECT count(*) FROM TransactionError SINCE 10 minutes ago FACET appName"
    }
  ]
}
```

## Validation Patterns

```hcl
variable "threshold" {
  type = number

  validation {
    condition     = var.threshold > 0 && var.threshold <= 100
    error_message = "Threshold must be between 0 and 100."
  }
}

resource "newrelic_nrql_alert_condition" "this" {
  # ...

  lifecycle {
    precondition {
      condition     = var.threshold_duration >= 60
      error_message = "Threshold duration must be at least 60 seconds."
    }
  }
}
```
