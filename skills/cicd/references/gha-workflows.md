# GitHub Actions — Full Workflow Examples

## Contents

- [OIDC + AWS — Assume role, no stored keys](#oidc--aws--assume-role-no-stored-keys)
- [OIDC + GCP — Workload Identity Federation](#oidc--gcp--workload-identity-federation)
- [Canary deploy with SLO monitor + auto-rollback](#canary-deploy-with-slo-monitor--auto-rollback)
- [Matrix test across Python versions](#matrix-test-across-python-versions)
- [Monorepo selective runs — path-filter](#monorepo-selective-runs--path-filter)
- [Data-pipeline CI (lint → test → DAG integrity → dbt)](#data-pipeline-ci-lint--test--dag-integrity--dbt)
- [Reusable workflow — shared test job](#reusable-workflow--shared-test-job)

---

## OIDC + AWS — Assume role, no stored keys

Trust-policy prerequisite (IAM role): `sub = repo:org/name:ref:refs/heads/main`, `aud = sts.amazonaws.com`.

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

permissions:
  id-token: write       # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          role-session-name: gha-${{ github.run_id }}
          aws-region: us-east-1
          role-duration-seconds: 3600

      - name: Deploy
        run: |
          aws s3 sync ./dist s3://my-bucket/ --delete
          aws ecs update-service --cluster prod --service api --force-new-deployment
```

## OIDC + GCP — Workload Identity Federation

Prerequisite: WIF pool + provider bound to GitHub OIDC issuer.

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gha/providers/github
          service_account: gha-deployer@project-id.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - run: gcloud run deploy api --image gcr.io/project-id/api:${{ github.sha }} --region us-central1
```

## Canary deploy with SLO monitor + auto-rollback

```yaml
name: Canary Deploy
on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  canary:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        weight: [5, 25, 100]
      max-parallel: 1
      fail-fast: true
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: us-east-1

      - name: Shift traffic to ${{ matrix.weight }}%
        run: |
          aws elbv2 modify-rule \
            --rule-arn ${{ secrets.ALB_RULE_ARN }} \
            --actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=${{ secrets.CANARY_TG }},Weight=${{ matrix.weight }}},{TargetGroupArn=${{ secrets.STABLE_TG }},Weight=$((100 - ${{ matrix.weight }}))}]}"

      - name: Monitor SLO for 10 min
        run: |
          for i in {1..10}; do
            ERROR_RATE=$(aws cloudwatch get-metric-statistics \
              --namespace AWS/ApplicationELB \
              --metric-name HTTPCode_Target_5XX_Count \
              --dimensions Name=TargetGroup,Value=canary \
              --start-time $(date -u -d '1 minute ago' +%Y-%m-%dT%H:%M:%SZ) \
              --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
              --period 60 --statistics Sum --query 'Datapoints[0].Sum' --output text)
            if (( $(echo "$ERROR_RATE > 5" | bc -l) )); then
              echo "::error::Canary failing SLO (errors=$ERROR_RATE); aborting"
              exit 1
            fi
            sleep 60
          done

      - name: Rollback on failure
        if: failure()
        run: |
          aws elbv2 modify-rule --rule-arn ${{ secrets.ALB_RULE_ARN }} \
            --actions "Type=forward,TargetGroupArn=${{ secrets.STABLE_TG }}"
          echo "::error::Rolled back to stable"
```

## Matrix test across Python versions

```yaml
name: Test
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          cache-dependency-path: 'uv.lock'

      - name: Install uv
        run: pip install uv

      - name: Install deps
        run: uv sync --frozen

      - name: Lint
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Type check
        run: uv run pyright

      - name: Test
        run: uv run pytest -v --tb=short --cov --cov-report=xml
        timeout-minutes: 15

      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          files: ./coverage.xml
```

## Monorepo selective runs — path-filter

```yaml
name: Monorepo CI
on: [pull_request]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      dags: ${{ steps.filter.outputs.dags }}
      spark: ${{ steps.filter.outputs.spark }}
      dbt: ${{ steps.filter.outputs.dbt }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            dags:
              - 'dags/**'
            spark:
              - 'spark_jobs/**'
            dbt:
              - 'dbt/**'

  test-dags:
    needs: changes
    if: needs.changes.outputs.dags == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/dags/

  test-spark:
    needs: changes
    if: needs.changes.outputs.spark == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/spark/

  test-dbt:
    needs: changes
    if: needs.changes.outputs.dbt == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          cd dbt
          dbt deps
          dbt compile
          dbt test
```

## Data-pipeline CI (lint → test → DAG integrity → dbt)

```yaml
name: Data Pipeline CI
on:
  pull_request:
    paths: ['dags/**', 'spark_jobs/**', 'dbt/**', 'tests/**']

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install ruff
      - run: ruff check . && ruff format --check .

  dag-integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install apache-airflow==2.10.*
      - name: Check DAG imports
        run: |
          python -c "
          from airflow.models import DagBag
          dag_bag = DagBag(dag_folder='dags/', include_examples=False)
          if dag_bag.import_errors:
              for path, err in dag_bag.import_errors.items():
                  print(f'::error file={path}::{err}')
              exit(1)
          print(f'Loaded {len(dag_bag.dags)} DAGs successfully')
          "

  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ -v --cov --cov-fail-under=80
        timeout-minutes: 10

  dbt-compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install dbt-snowflake
      - run: |
          cd dbt
          dbt deps
          dbt compile --target ci
```

## Reusable workflow — shared test job

`.github/workflows/reusable-test.yml`:

```yaml
name: Reusable test
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: 'pip'
      - run: pip install -e ".[dev]"
      - run: pytest
```

Caller `.github/workflows/ci.yml`:

```yaml
jobs:
  test-py312:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.12'
  test-py313:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.13'
```
