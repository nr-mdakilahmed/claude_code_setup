# New Relic Terraform — Project Structure & Operations

> **When to load:** Phase 2 (Structure) — setting up directory layout, backend, modules, naming, and import operations.

## Directory Layout

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── alerting/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   ├── dashboard/
│   └── workflow/
└── shared/
    └── backend.tf
```

## Backend Configuration

```hcl
# shared/backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "newrelic/${var.environment}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

## Provider Versions

```hcl
# versions.tf
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    newrelic = {
      source  = "newrelic/newrelic"
      version = "~> 3.0"
    }
  }
}
```

## Variables Pattern

```hcl
# variables.tf
variable "newrelic_account_id" {
  description = "New Relic account ID"
  type        = number
}

variable "newrelic_api_key" {
  description = "New Relic API key"
  type        = string
  sensitive   = true
}

variable "newrelic_region" {
  description = "New Relic region (US or EU)"
  type        = string
  default     = "US"

  validation {
    condition     = contains(["US", "EU"], var.newrelic_region)
    error_message = "Region must be US or EU."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "services" {
  description = "Services to monitor"
  type = list(object({
    name               = string
    app_name           = string
    error_threshold    = optional(number, 5)
    latency_threshold  = optional(number, 1)
    enable_baseline    = optional(bool, true)
  }))
}
```

## Naming Conventions

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = var.team
  }
}

# Resource naming
resource "newrelic_alert_policy" "main" {
  name = "${local.name_prefix}-alerts"
}

resource "newrelic_one_dashboard" "main" {
  name = "${local.name_prefix}-dashboard"
}
```

## Module Composition Strategy

```
modules/
├── alerting/          # Alert policy + NRQL conditions
├── workflow/          # Notification destination + channel + workflow
├── dashboard/         # Dashboard with standard widget layout
└── service_monitor/   # Composite: calls alerting/ + workflow/ + dashboard/
```

Composite modules call sub-modules internally, passing `policy_id` from alerting to workflow via `depends_on`.

## Import Existing Resources

### Import ID Formats

```bash
# Alert Policy
terraform import newrelic_alert_policy.main <policy_id>

# NRQL Alert Condition — requires both policy and condition ID
terraform import newrelic_nrql_alert_condition.error_rate <policy_id>:<condition_id>

# Notification Destination
terraform import newrelic_notification_destination.slack <destination_id>

# Notification Channel
terraform import newrelic_notification_channel.slack <channel_id>

# Workflow
terraform import newrelic_workflow.main <workflow_id>

# Dashboard — uses GUID, not numeric ID
terraform import newrelic_one_dashboard.main <dashboard_guid>

# Muting Rule
terraform import newrelic_alert_muting_rule.maintenance <rule_id>
```

## Debugging & State Commands

```bash
# Debug logging
TF_LOG=DEBUG TF_LOG_PATH=./debug.log terraform plan

# State inspection
terraform state list                          # All resources
terraform state show module.alerting["api"]   # Specific resource detail
terraform state list | grep newrelic          # List NR resources in state

# State operations
terraform state mv 'module.old' 'module.new'  # Rename after refactor
terraform state rm <resource>                 # Remove without destroying
terraform state rm newrelic_nrql_alert_condition.orphaned  # Remove orphaned

# Refresh & recovery
terraform apply -refresh-only                 # Sync state with reality
terraform init -backend=true -reconfigure     # Reset backend
TF_LOG=INFO terraform plan -no-color          # Verbose plan
```
