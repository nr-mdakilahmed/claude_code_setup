# YAML-Driven Alert Module (service_alerts_v5)

> **When to load:** Phase 3 (Implement) — building per-entity alerting with YAML config files and threshold maps.

## Module Structure

```
modules/service_alerts_v5/
├── main.tf           # Alert conditions, policies, workflows
├── variables.tf      # entity_names, thresholds, slack config
├── outputs.tf
└── versions.tf
```

## Module Variables

```hcl
# modules/service_alerts_v5/variables.tf
variable "rule_file_name" {
  description = "YAML file name (without .yaml) in config/alert-configurations/"
  type        = string
}

variable "entity_names" {
  description = "List of entity names for per-entity alert conditions"
  type        = list(string)
}

variable "thresholds" {
  description = "Map of 'entity**alert_name' => threshold value"
  type        = map(number)
  default     = {}
}

variable "slack_webhook_url" {
  type      = string
  sensitive = true
}

variable "slack_block_kit_enabled" {
  type    = bool
  default = true
}

variable "slack_block_kit_header" {
  description = "Header for Slack Block Kit message"
  type        = string
  default     = "Alert"
}
```

## YAML Alert Definition

```yaml
# config/alert-configurations/billing_ingestion_health_late_arrival.yaml
account_id: 11605296

defaults:
  late_arrival_defaults: &late_arrival_defaults
    aggregation_window: 600
    aggregation_method: event_flow
    aggregation_delay: 120
    fill_option: none
    violation_time_limit_seconds: 259200
    expiration_duration: 3600
    open_violation_on_expiration: true
    close_violations_on_expiration: true

alerts:
  late_arrival_critical:
    <<: *late_arrival_defaults
    description: "Data ingestion is delayed. P95 latency exceeded threshold."
    type: static
    policy:
      staging:
        - slack
    critical:
      operator: above
      threshold: $threshold           # Replaced per-entity from thresholds map
      threshold_duration: 600
      threshold_occurrences: all
    nrql: |
      SELECT latest(ingestion_delay_p95)
      FROM IngestionTablesHealthMonitor
      WHERE late_arrival_detection_enabled = true
      AND config_name = '$ENTITY_NAME'  # Replaced per-entity
    title_template: "$ENTITY_NAME"
```

## Per-Entity Config YAML

```yaml
# config/billing_config.yaml
config_tables:
  - config_name: DB.SCHEMA.USAGE_METRICS_LSE
    monitoring_threshold_minutes: 30
    late_arrival_detection_enabled: true
    late_arrival_threshold_minutes: 15

  - config_name: DB.SCHEMA.USAGE_COMPUTE_LSE
    monitoring_threshold_minutes: 30
    late_arrival_detection_enabled: true
    late_arrival_threshold_minutes: 15
```

## Module Usage with Per-Entity Thresholds

```hcl
# billing_ingestion_health_alerts.tf
locals {
  config = yamldecode(file("${path.module}/../config/alert-configurations/billing_config.yaml"))

  # Build per-alert thresholds map: "entity**alert_name" => threshold_value
  late_arrival_thresholds = {
    for item in local.config.config_tables :
    "${item.config_name}**late_arrival_critical" => tonumber(item.late_arrival_threshold_minutes)
    if lookup(item, "late_arrival_detection_enabled", false) == true
  }

  # Volume thresholds: merge warning + critical
  volume_thresholds = merge(
    { for item in local.config.config_tables :
      "${item.config_name}**volume_drop_warning" => tonumber(item.drop_warning_stddev)
      if lookup(item, "drop_warning_enabled", false) == true
    },
    { for item in local.config.config_tables :
      "${item.config_name}**volume_drop_critical" => tonumber(item.drop_critical_stddev)
      if lookup(item, "drop_critical_enabled", false) == true
    }
  )

  # Entity names (filtered by feature flag)
  late_arrival_entity_names = [
    for item in local.config.config_tables : item.config_name
    if lookup(item, "late_arrival_detection_enabled", false) == true
  ]
}

module "billing_late_arrival_alerts" {
  source         = "../modules/service_alerts_v5"
  rule_file_name = "billing_ingestion_health_late_arrival"
  entity_names   = local.late_arrival_entity_names
  thresholds     = local.late_arrival_thresholds

  slack_block_kit_enabled = true
  slack_block_kit_header  = "Billing Tables Health Alert - Late Arrival"
}

module "billing_volume_alerts" {
  source         = "../modules/service_alerts_v5"
  rule_file_name = "billing_ingestion_health_volume_alerts"
  entity_names   = local.all_entity_names
  thresholds     = local.volume_thresholds

  slack_block_kit_enabled = true
  slack_block_kit_header  = "Billing Tables Health Alert - Volume"
}
```
