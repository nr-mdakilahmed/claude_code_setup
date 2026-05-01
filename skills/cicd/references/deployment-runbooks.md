# Deployment Runbooks

## Contents

- [Rollback procedures](#rollback-procedures)
  - [Container service rollback (ECS / Cloud Run / k8s)](#container-service-rollback-ecs--cloud-run--k8s)
  - [Data pipeline rollback (Airflow / dbt)](#data-pipeline-rollback-airflow--dbt)
  - [Database migration rollback](#database-migration-rollback)
- [Canary promotion checklist](#canary-promotion-checklist)
- [Incident response playbook](#incident-response-playbook)
- [Post-incident review template](#post-incident-review-template)

---

## Rollback procedures

**Rule**: rollback must be a single command, tested in staging at least monthly. If it takes more than two commands or needs ad-hoc reasoning, the runbook is broken — fix it before shipping.

### Container service rollback (ECS / Cloud Run / k8s)

**ECS**:
```bash
# List previous task definitions
aws ecs list-task-definitions --family-prefix api --sort DESC --max-items 5

# Rollback to previous revision
aws ecs update-service \
  --cluster prod \
  --service api \
  --task-definition api:123 \
  --force-new-deployment

# Verify
aws ecs wait services-stable --cluster prod --services api
```

**Cloud Run**:
```bash
# List revisions
gcloud run revisions list --service=api --region=us-central1

# Route 100% to previous revision
gcloud run services update-traffic api \
  --to-revisions=api-00045-abc=100 \
  --region=us-central1
```

**Kubernetes**:
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/api -n prod

# Rollback to specific revision
kubectl rollout history deployment/api -n prod
kubectl rollout undo deployment/api -n prod --to-revision=42

# Verify
kubectl rollout status deployment/api -n prod
```

### Data pipeline rollback (Airflow / dbt)

**Airflow** — DAGs are stateless code, so rollback is a git revert + redeploy:
```bash
git revert <bad-commit-sha>
git push origin main
# CI redeploys DAG bundle; verify in Airflow UI
```

For partial task failures, clear and rerun:
```bash
airflow tasks clear <dag_id> -t <task_id> -s <start_date> -e <end_date>
```

**dbt** — revert models and rerun incremental from last known good:
```bash
git revert <bad-commit-sha>
cd dbt
dbt run --full-refresh --select my_model+  # rebuild downstream
dbt test --select my_model+
```

### Database migration rollback

**Irreversible migrations** (DROP COLUMN, NOT NULL added) require forward fix — never rollback blindly.

For reversible migrations (Alembic / Flyway):
```bash
# Alembic
alembic downgrade -1

# Flyway
flyway undo -target=12
```

**Before any migration**:
- [ ] Dual-read compatibility verified (both schema versions readable by app)
- [ ] Backup / snapshot taken, restore path tested
- [ ] Feature flag gates the writer cutover

---

## Canary promotion checklist

Run through this for every canary promotion (5% → 25% → 100%).

- [ ] **Pre-canary**: staging smoke tests green; data-quality checkpoint passed
- [ ] **5% deploy**: monitor for ≥10 min
  - [ ] Error rate (5xx) within 0.5% of baseline
  - [ ] p99 latency within 10% of baseline
  - [ ] No new exception types in logs (check structured log aggregator)
  - [ ] Downstream dependencies healthy (DB connections, queue depth)
- [ ] **25% deploy**: monitor for ≥15 min
  - [ ] All 5% criteria
  - [ ] User-facing metrics healthy (signup rate, conversion)
- [ ] **100% deploy**: monitor for ≥30 min
  - [ ] All 25% criteria
  - [ ] Full traffic sustained without degradation
- [ ] **Post-deploy**: alert channels quiet for 1 hour
- [ ] **Document**: deploy tag, duration, any anomalies in change log

**Abort criteria** (at any stage):
- Error rate jumps >2x baseline for >2 min → rollback
- p99 latency >30% above baseline for >5 min → rollback
- Any new critical exception (OOM, deadlock, cascading failure) → rollback immediately
- Downstream dependency exhausted (DB connections, rate limits) → rollback

---

## Incident response playbook

### Phase 1 — Triage (first 5 min)

- [ ] Acknowledge the page; post in `#incident-<name>` channel
- [ ] Assign Incident Commander (IC), Ops lead, Comms lead
- [ ] Determine severity (SEV-1 / SEV-2 / SEV-3)
  - SEV-1: customer-facing outage, data loss risk, security breach
  - SEV-2: degraded service, partial outage, SLO at risk
  - SEV-3: internal impact only
- [ ] **If recent deploy**: rollback immediately, investigate after
- [ ] Snapshot current dashboards (screenshots for timeline)

### Phase 2 — Mitigate (next 15 min)

- [ ] IC drives the response; no freelancing
- [ ] Rollback deploy OR feature flag off the risky path
- [ ] If infrastructure: scale out, failover, circuit-break noisy neighbors
- [ ] Comms lead posts status updates every 15 min (even if "no change")
- [ ] Preserve evidence: save logs, heap dumps, traces before they rotate

### Phase 3 — Resolve

- [ ] Verify recovery metrics: error rate, latency, queue depth back to baseline
- [ ] Monitor for 30 min post-recovery before standing down
- [ ] Close the incident channel; schedule post-incident review within 3 business days

### Commands for common mitigations

**Scale out quickly**:
```bash
# ECS
aws ecs update-service --cluster prod --service api --desired-count 20

# k8s
kubectl scale deployment/api --replicas=20 -n prod
```

**Circuit-break a noisy consumer**:
```bash
# Pause Kafka consumer group
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --group noisy-consumer --pause
```

**Rotate leaked credential** (if logged):
```bash
# AWS: delete access key immediately
aws iam delete-access-key --access-key-id <AKIA...> --user-name <user>
# Then rotate via IaC; do not manually recreate
```

---

## Post-incident review template

Fill within 3 business days of resolution. Blameless — focus on systems, not people.

```markdown
# Post-Incident Review — <incident-name> <YYYY-MM-DD>

## Summary
- Severity: SEV-<N>
- Duration: <start> → <resolve> (<total minutes>)
- Customer impact: <affected users, requests, revenue>
- Root cause: <one-line technical description>

## Timeline (UTC)
- HH:MM — <event>
- HH:MM — <event>
- HH:MM — <mitigation applied>
- HH:MM — <recovery verified>

## What went well
- <observation>
- <observation>

## What went poorly
- <observation>
- <observation>

## Root cause analysis
### Trigger
<What initiated the failure?>

### Contributing factors
- <factor>
- <factor>

### Why detection took <X> min
<Monitoring gap or signal noise issue>

### Why mitigation took <X> min
<Runbook clarity, on-call familiarity, tooling gaps>

## Action items
| # | Action | Owner | Priority | Due |
|---|---|---|---|---|
| 1 | <action> | <name> | P0 | <date> |
| 2 | <action> | <name> | P1 | <date> |

## Lessons learned
<2-3 durable lessons for `lessons.md`>
```
