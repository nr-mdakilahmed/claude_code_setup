---
name: terraform
description: Authors New Relic infrastructure as code with the Terraform provider — NRQL alert conditions, notification destinations and channels, workflows, muting rules, dashboards, modules, and CI/CD pipelines. Triggers when the user is writing Terraform, editing .tf or .tfvars files, picking a condition type, wiring notification channels or workflows, structuring a Terraform project, or reviewing HCL for New Relic resources.
when_to_use: Auto-trigger on .tf / .tfvars / .terraform.lock.hcl edits. Invoke explicitly for plan/apply reviews, module refactors, or when paired with /nrql and /nralert during alert work.
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/.terraform.lock.hcl"
---

# New Relic Terraform

Turns Claude into a New Relic IaC author: picks the right condition type, encodes alert policy in YAML + HCL modules, keeps state safe, and validates every change with `plan` before `apply`.

**Freedom level: Medium** — one preferred pattern exists per decision (condition type, module boundary, state backend) but numbers and scope depend on service topology and deploy cadence.

## 1. Modules Encapsulate Decisions

**Build a module when the same pattern ships to 5+ services; inline otherwise.**

- Split by domain: `modules/alerting`, `modules/workflow`, `modules/dashboard`, `modules/service_monitor` (composite).
- Module inputs are service-level facts (name, tier, owners); thresholds live in YAML or `tfvars`, not in the module body.
- Use `for_each` with a map key, never `count`. `count` reindexes on reorder and destroys live resources.
- "Monolithic root module" → "One module per domain; root composes them".

## 2. YAML For Data HCL For Logic

**Encode per-service alert data in YAML; let HCL iterate and enforce structure.**

- `locals { services = yamldecode(file("services.yaml")) }` then `for_each = local.services`.
- Non-engineers can edit YAML; the HCL module stays under review.
- Keep thresholds, facets, and owners in YAML. Keep aggregation method, provider version, and lifecycle in HCL.
- See `references/yaml-alerts.md` for the full per-entity pattern.

## 3. State Is Sacred

**Remote backend with locking from day one. Never commit state, never edit state by hand.**

- S3 + DynamoDB (AWS) or GCS (GCP) backend; `*.tfstate*` in `.gitignore`.
- `lifecycle { prevent_destroy = true }` on production policies and workflows.
- Pin the provider: `version = "~> 3.0"` — matching `.terraform.lock.hcl` is committed.
- Separate environments by **directory** (`environments/prod/`, `environments/staging/`), not workspaces — thresholds and channels differ.
- `terraform import <type>.<name> <id>` before adopting a resource created in the UI; never `taint` + `apply` to "reset".

## 4. Plan Before Apply

**No apply without a reviewed plan. No merge without `validate` + `fmt` green.**

- Local loop: `terraform init` → `fmt` → `validate` → `plan -out=tfplan` → review diff → `apply tfplan`.
- CI runs `fmt -check`, `validate`, and `plan` on every PR; `apply` only on merge to the environment branch.
- Review the plan output line-by-line for any `destroy` or `replace` on an alert policy, workflow, or dashboard — those are production-visible.

## Quick reference — condition type selector

| Need | Type | Unit |
|---|---|---|
| Fixed threshold (error > 5%, latency > 500ms) | Static | Absolute / percent |
| Variable workload where "normal" shifts | Baseline (`upper_only`) | Std deviations |
| One host deviating from a fleet | Outlier | Std deviations |
| Throughput drop detection | Static (`below`) | Requests / min |
| Batch job completion / heartbeat | Static + signal loss (`expiration_duration`) | Seconds of silence |

Full HCL for each type: `references/provider-hcl.md`.

## Feedback loop

1. Edit `.tf` — then **validate immediately**: `terraform fmt -recursive && terraform validate`.
2. `terraform plan -out=tfplan` — **read the diff before proceeding**. Flag any destroy/replace on live alert resources.
3. If the plan is not what was intended: fix HCL, re-validate, re-plan. Loop until clean.
4. `terraform apply tfplan` — apply the exact plan file, not a fresh `apply`.
5. After apply: spot-check in the New Relic UI (one condition, one workflow, one dashboard) before closing the task.

**State-safety rules inside the loop:**

- If `plan` shows a `destroy` on `newrelic_alert_policy`, `newrelic_workflow`, or `newrelic_one_dashboard`: stop and explain before continuing.
- On lock errors (`Error acquiring state lock`): investigate the holder first (`terraform force-unlock` only after confirming no apply is running).
- After a failed apply with partial state: run `terraform plan` again to see reconciled diff; never re-run `apply` blind.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Hardcoded `account_id` in resources | `var.account_id` via `terraform.tfvars` (gitignored) |
| `count` on a changing list | `for_each` with a stable map key |
| Provider unpinned or lockfile uncommitted | `version = "~> 3.0"` + commit `.terraform.lock.hcl` |
| Legacy `newrelic_alert_channel` | Migrate to `newrelic_notification_destination` + `_channel` + `newrelic_workflow` |
| `*.tfstate` in git, or local-only backend | Remote backend with locking from day one |
| Workspaces for prod/staging split | Directory-per-env (`environments/prod/`, `/staging/`) |
| No `lifecycle { prevent_destroy }` on critical policies | Add on prod policies, workflows, destinations |

## Troubleshooting

| Symptom | Fix |
|---|---|
| 401 / 403 on apply | Verify `NEW_RELIC_API_KEY` is a **User key** (not Ingest); confirm account ID matches the key's scope |
| `Resource already exists` (409) | `terraform import <type>.<name> <id>` from the New Relic UI, then re-plan |
| Invalid NRQL error | Paste the query into the NRQL Query Builder; fix there first, then copy back |
| Workflow not triggering on an incident | Check `issues_filter` predicates; confirm `labels.policyIds` matches; set `product = "IINT"` on destination |
| Signal-loss condition flapping | Raise `expiration_duration` to 2–3× reporting cadence (900–3600 s for batch) |
| `Too many requests` (429) during apply | `terraform apply -parallelism=5`; narrow scope with `-target` |
| `Error acquiring state lock` | Confirm no concurrent apply, then `terraform force-unlock <LOCK_ID>` |
| Plan diff shows destroy on a working policy | Stop. Inspect `for_each` key change or module input drift before proceeding |
| Drift between UI edits and state | Decide source of truth; either `import` UI changes or `apply` to overwrite — never both uncoordinated |

## Checklist

- [ ] Provider pinned (`~> 3.0`) and `.terraform.lock.hcl` committed
- [ ] Remote state with locking (S3+DynamoDB or GCS) configured
- [ ] NRQL conditions over legacy APM conditions
- [ ] `aggregation_method` set explicitly on every condition
- [ ] Signal loss (`expiration_duration`) configured where applicable
- [ ] `for_each` (not `count`) for multiple similar resources
- [ ] Workflows + destinations (not legacy notification channels)
- [ ] Environments separated by directory
- [ ] `terraform fmt` + `validate` pass in CI
- [ ] Plan reviewed before apply; `prevent_destroy` on production resources

## References

- `references/provider-hcl.md` — full HCL examples for every resource type (policies, conditions, workflows, destinations, dashboards, muting rules). Read when writing new resources.
- `references/project-structure.md` — directory layouts, backend config, module patterns, naming conventions. Read when starting or refactoring a project.
- `references/yaml-alerts.md` — YAML-driven per-entity alert module pattern with `yamldecode` + `for_each`. Read when onboarding 5+ services to a common alert template.
- `references/cicd-pipeline.md` — GitHub Actions workflows for `fmt` / `validate` / `plan` / `apply`, pre-commit hooks, OIDC auth. Read when wiring CI.

## Cross-references

| Skill | When |
|---|---|
| `/nrql` | Writing or optimizing the NRQL for a condition, dashboard widget, or alert |
| `/nralert` | Picking correlation scope, muting rules, signal-loss tuning — this skill applies the resulting HCL |
| `/cicd` | GitHub Actions patterns beyond Terraform-specific steps |
