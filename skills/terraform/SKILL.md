---
name: terraform
description: >
  Use when creating NRQL alert conditions, notification channels, workflows, dashboards,
  Terraform project structure, modules, or CI/CD for New Relic. Covers the New Relic
  Terraform provider, HCL patterns, and infrastructure as code.
  Auto-triggers for .tf files or New Relic infrastructure as code.
---

# New Relic Terraform

## Phased Workflow

**Phase 1 — Design**: Choose condition types, plan alert strategy, decide project structure.
**Phase 2 — Structure**: Set up layout, backend, modules, naming.
> Read `references/project-structure.md` for directory layouts, backend config, module patterns, naming.
**Phase 3 — Implement**: Write provider config, alert conditions, workflows, dashboards.
> Read `references/provider-hcl.md` for all HCL resource examples.
> Read `references/yaml-alerts.md` for YAML-driven per-entity alert module patterns.
**Phase 4 — Deploy**: CI/CD pipeline for validate, plan, apply.
> Read `references/cicd-pipeline.md` for GitHub Actions workflows and pre-commit hooks.

## Condition Type Selection

| Need | Type | Unit |
|---|---|---|
| Known fixed threshold (error > 5%) | Static | Absolute value |
| Variable workload | Baseline | Std deviations |
| Compare instances (host fleet) | Outlier | Std deviations |
| Error rate | Static + `percentage()` | Percentage (0-100) |
| Latency | Baseline (`upper_only`) | Std deviations |
| Throughput drop | Static (`below`) | Requests/min |
| Batch job completion | Static + signal loss | `expiration_duration` |

## Project Structure

**Use directory-based environments** (not workspaces) — thresholds/channels differ between envs.
**Use modules** when same pattern applies to 5+ services. Inline for one-offs.

```
modules/
  alerting/          # Policy + NRQL conditions
  workflow/          # Destination + channel + workflow
  dashboard/         # Standard widget layout
  service_monitor/   # Composite: alerting + workflow + dashboard
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Hardcoded `account_id` | `var.account_id` via `terraform.tfvars` |
| No `lifecycle` on critical resources | `lifecycle { prevent_destroy = true }` |
| Not pinning provider version | `version = "~> 3.0"` |
| `count` instead of `for_each` | `for_each` with map key (avoids reindex destroy) |
| Legacy `newrelic_alert_channel` | Migrate to destination + channel + workflow |
| Monolithic root module | Split by domain; use modules |
| State file in git | Remote backend; `*.tfstate` in `.gitignore` |
| No remote state backend | S3/GCS with locking from day one |

## Troubleshooting

| Error | Fix |
|---|---|
| 401/403 on apply | Verify `NEW_RELIC_API_KEY` is User key; check account ID |
| Resource already exists | `terraform import <type>.<name> <id>` |
| Invalid NRQL | Test in Query Builder first |
| Workflow not triggering | Verify `labels.policyIds`; check `product = "IINT"` |
| Signal lost false positives | Increase `expiration_duration` to 900-3600s |
| Too many requests (429) | `-parallelism=5`; use `-target` |
| Error acquiring state lock | `terraform force-unlock <LOCK_ID>` |

## Checklist

- [ ] Pin provider version (`~> 3.0`)
- [ ] NRQL conditions over legacy APM conditions
- [ ] Set `aggregation_method` explicitly on every condition
- [ ] Configure signal loss (`expiration_duration`)
- [ ] `for_each` for multiple similar conditions
- [ ] Use workflows (not legacy notification channels)
- [ ] Remote state with locking (S3/GCS + DynamoDB)
- [ ] Separate environments by directory
- [ ] `terraform fmt` + `terraform validate` in CI

## Cross-References

| Skill | When |
|---|---|
| `nrql` | Writing/optimizing NRQL for conditions or dashboards |
| `nralert` | Alert correlation, muting rules, Smart Alerts |
| `cicd` | GitHub Actions patterns beyond Terraform |
