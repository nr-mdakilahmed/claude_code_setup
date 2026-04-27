# Terraform CI/CD Pipeline for New Relic

> **When to load:** Phase 4 (Deploy) — setting up CI/CD for validate, plan, and apply.

## GitHub Actions Workflow

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    branches: [main]
    paths: ['terraform/**']
  push:
    branches: [main]
    paths: ['terraform/**']

env:
  TF_VERSION: '1.6.0'
  NEW_RELIC_API_KEY: ${{ secrets.NEW_RELIC_API_KEY }}
  NEW_RELIC_ACCOUNT_ID: ${{ secrets.NEW_RELIC_ACCOUNT_ID }}

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Format Check
        run: terraform fmt -check -recursive terraform/

      - name: Validate
        working-directory: terraform/environments/prod
        run: |
          terraform init -backend=false
          terraform validate

  plan:
    needs: validate
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Plan
        working-directory: terraform/environments/prod
        run: |
          terraform init
          terraform plan -no-color -out=tfplan

      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = '${{ steps.plan.outputs.stdout }}';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `### Terraform Plan\n\`\`\`hcl\n${output}\n\`\`\``
            });

  apply:
    needs: validate
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Apply
        working-directory: terraform/environments/prod
        run: |
          terraform init
          terraform apply -auto-approve
```

## Plan-Based Testing in CI (Matrix Strategy)

```yaml
# .github/workflows/terraform-test.yml — validates all environments
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: '1.6.0'
      - name: Init, Validate, Plan
        working-directory: terraform/environments/${{ matrix.environment }}
        run: |
          terraform init -backend=false
          terraform validate
          terraform plan -input=false -no-color
        env:
          TF_VAR_newrelic_api_key: ${{ secrets.NEW_RELIC_API_KEY }}
          TF_VAR_newrelic_account_id: ${{ secrets.NEW_RELIC_ACCOUNT_ID }}
```

## Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.88.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
```
