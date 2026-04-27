---
name: cicd
description: >
  Use when setting up CI/CD for data pipelines, configuring GitHub Actions,
  deployment strategies, testing gates, secrets management, or pipeline observability.
  Covers OIDC auth, canary/blue-green deploys, pre-commit hooks, and data quality gates.
  Auto-triggers for GitHub Actions workflows (.yml) or deployment pipelines.
---

# Data Pipeline CI/CD

## Basic Pipeline CI

```yaml
name: Data Pipeline CI
on:
  pull_request:
    paths: ['dags/**', 'spark_jobs/**', 'dbt/**', 'tests/**']
  push:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11', cache: 'pip' }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check . && ruff format --check .
      - run: mypy dags/ spark_jobs/ --ignore-missing-imports
      - run: pytest tests/ -v --tb=short --cov=dags --cov=spark_jobs
```

## Deployment Strategies

| Scenario | Strategy | Why |
|---|---|---|
| Zero-downtime | Blue-green | Instant rollback via traffic switch |
| Gradual confidence | Canary | Limit blast radius, monitor error rate |
| Simple, low-risk | Rolling update | Minimal infra |
| Database migration | Blue-green + feature flags | Schema changes need both versions |
| Data pipeline (DAGs/dbt) | Direct deploy + data quality gate | Stateless code, verify data post-deploy |

## Secrets Management (OIDC preferred)

```yaml
# PREFERRED: Assume role via OIDC — no stored secrets
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-deploy
      aws-region: us-east-1
```

## Testing Strategy

| Layer | Tool | When |
|---|---|---|
| Lint | ruff, mypy | Every PR |
| Unit | pytest | Every PR |
| DAG integrity | `DagBag().import_errors` | Every PR |
| Integration | pytest + testcontainers | Merge to main |
| Data quality | great_expectations, dbt tests | Post-deploy |

## Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

## Observability

Use `structlog` for JSON logging with pipeline context. Add Prometheus counters/histograms for pipeline metrics.

## Anti-Patterns

| Pattern | Fix |
|---|---|
| No CI on data pipeline PRs | Add DAG integrity + pytest |
| Static AWS keys in GitHub | Use OIDC role assumption |
| `--no-verify` on git push | Fix the hook, don't skip it |
| Manual deployments | Automate with GitHub Actions |
| No data quality gate | dbt test / GX checkpoint post-deploy |
| Single long CI job (30+ min) | Split into parallel jobs |
| No rollback strategy | Blue-green or canary with auto-rollback |
| `pip install` without pins | Use `pip-compile` or `uv pip compile` |
