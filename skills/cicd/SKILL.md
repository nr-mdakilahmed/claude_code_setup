---
name: cicd
description: Configures CI/CD for data pipelines and services — GitHub Actions workflows, OIDC auth, canary and blue-green deployments, secrets management, pre-commit hooks, and data quality gates. Triggers when Claude edits workflow files, sets up deployment pipelines, debugs flaky CI jobs, or designs release strategies.
when_to_use: Auto-trigger when files under .github/workflows/ or .pre-commit-config.yaml are edited. Invoke explicitly when planning deployment strategy, adding OIDC auth, or diagnosing pipeline failures (OIDC token errors, cache misses, matrix failures, concurrency deadlocks).
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
  - ".pre-commit-config.yaml"
---

# CI/CD for Data Pipelines

Turns Claude into a pipeline engineer: enforces OIDC over stored secrets, data-quality gates before promotion, canary rollouts with fast rollback, and pre-commit hooks that catch issues before CI ever starts.

**Freedom level: High** — CI/CD admits many valid shapes (trunk-based vs GitFlow, canary vs blue-green, GHA vs Buildkite). The skill directs judgment with principles and decision tables, not prescribed workflows.

## 1. OIDC Over Secrets

**Federated identity beats stored credentials. Never put long-lived keys in GitHub.**

- Use `id-token: write` + `aws-actions/configure-aws-credentials` / `google-github-actions/auth` — no `AWS_ACCESS_KEY_ID` in secrets.
- Scope the trust policy to `repo:org/name:ref:refs/heads/main` — never wildcard the subject.
- "Static AWS keys in `secrets`" → "OIDC role assumption with session duration ≤1h".
- Rotate any remaining static secrets via env-scoped reusable workflows; audit with `gh secret list` per environment.

## 2. Gate On Data Quality

**Code passing tests is not enough. Data must pass checkpoints before promotion.**

- Run `dbt test` / `great_expectations checkpoint` / DAG integrity checks (`DagBag().import_errors`) as required status checks.
- Block promotion on row-count deltas, schema drift, and freshness SLAs — not just unit tests.
- "Deploy then hope" → "Deploy to staging → run data-quality checkpoint → promote only on pass".
- Schema migrations gate on dual-read compatibility before switching writes.

## 3. Deploy Canary, Rollback Fast

**Release confidence comes from blast radius, not bravery. Every deploy needs a reversible path.**

- Default to canary (5% → 25% → 100%) with automated rollback on error-rate or latency SLO breach.
- Blue-green for zero-downtime DB migrations; feature flags for risky code paths.
- Rollback must be a single command or button — never "redeploy the old tag manually".
- "No rollback plan" → "Documented runbook with exact revert command + monitor dashboard link".

## 4. Pre-Commit Saves CI

**Every failure caught locally is a CI minute saved and a context switch avoided.**

- Run `ruff`, `ruff-format`, `detect-secrets`, `check-yaml`, `end-of-file-fixer` as pre-commit hooks.
- Install via `pre-commit install` in onboarding; enforce in CI with `pre-commit run --all-files`.
- "Bypass with `--no-verify`" → "Fix the hook; never skip. If the hook is wrong, fix the hook config."
- Pin hook revisions (`rev: v0.4.0`) — never track `main`.

## Deployment strategy

The single lookup consulted every invocation.

| Scenario | Strategy | Why |
|---|---|---|
| Zero-downtime app, schema stable | Blue-green | Instant flip via traffic switch |
| Gradual confidence, SLO-monitored | Canary (5→25→100%) | Bound blast radius, auto-rollback on SLO |
| Stateless workers, horizontal fleet | Rolling update | Minimal infra, native to k8s |
| Risky code path, targeted audience | Feature flag | Decouple deploy from release; toggle per user |
| DB migration or breaking change | Blue-green + feature flag | Dual-read window, flag gates writer cutover |

## Feedback loop

The promotion pipeline Claude enforces: `lint → test → build → canary → verify → promote`.

1. **Lint**: `ruff check`, `ruff format --check`, `yamllint .github/workflows/`. Fail fast (<1 min).
2. **Test**: unit + DAG import + integration (testcontainers). Required status check.
3. **Build**: container image with immutable tag (`sha-$GITHUB_SHA`), push to registry.
4. **Canary deploy**: 5% of traffic or one partition; monitor error rate + p99 latency for ≥10 min.
5. **Verify**: data-quality checkpoint (`dbt test`, `great_expectations`); SLO dashboard green.
6. **Promote**: roll to 100% only after verify passes. Any failure → auto-rollback to previous tag.
7. If any step fails: fix → rerun from that step. Never skip forward.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Static AWS/GCP keys in `secrets` | OIDC federated identity with short-lived tokens |
| `git push --no-verify` bypassing hooks | Fix the hook config or the code — never skip |
| Single 30-min CI job | Split into parallel jobs, matrix strategy, cache deps |
| `pip install` without pins | `uv pip compile` or `pip-compile` → lockfile in VCS |
| No rollback plan | Canary or blue-green with documented one-command revert |
| Deploying without data-quality gate | `dbt test` / GX checkpoint as required status check |
| Echoing secrets in workflow logs | `::add-mask::` + `echo "::add-mask::$VAR"` before use |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Error: Could not assume role with OIDC` | Check trust policy `sub` matches `repo:org/name:ref:refs/heads/<branch>`; `aud` = `sts.amazonaws.com`; `permissions: id-token: write` set |
| GHA cache miss every run | Key includes volatile input (timestamp, `github.run_id`); stabilize with `hashFiles('**/uv.lock')` |
| Flaky test fails only in CI | Race condition or ordering assumption; run `pytest -p no:randomly` locally; add `pytest-xdist` with `--dist loadscope` |
| Secret appears in workflow logs | Add `::add-mask::$VALUE` before first use; review `echo`/`set -x` lines; rotate the secret immediately |
| Matrix job fails for one Python version only | Version-specific API change; pin in `pyproject.toml` or add conditional skip with `sys.version_info` |
| Workflow timeout after 6h | Split into smaller jobs; add `timeout-minutes: 30` per job; check for hanging subprocesses (`pytest --timeout=60`) |
| Dependency cache restores stale lockfile | Invalidate key on lockfile hash: `key: deps-${{ hashFiles('uv.lock') }}` |
| Concurrency deadlock (jobs queue forever) | `concurrency: group: ${{ github.ref }}, cancel-in-progress: true`; check for circular `needs:` dependencies |
| `Permission denied` pushing to registry | OIDC role missing `ecr:BatchCheckLayerAvailability` or GCP artifact-registry writer binding |
| Pre-commit hook runs but CI still fails | `pre-commit run --all-files` locally; version skew between local and CI — pin `rev:` in `.pre-commit-config.yaml` |

## Checklist

- [ ] OIDC federated auth configured; no static cloud keys in secrets
- [ ] `permissions:` block sets least privilege (`contents: read` default)
- [ ] Lint + type-check + test run in parallel jobs, not sequential
- [ ] Dependency cache keyed on lockfile hash
- [ ] Concurrency group cancels in-progress runs on same ref
- [ ] Data-quality gate (`dbt test` / GX checkpoint) as required status check
- [ ] Deploy strategy documented (canary / blue-green / feature flag)
- [ ] Rollback is a single command or button, tested in staging
- [ ] Pre-commit hooks installed; `rev:` pinned; `detect-secrets` baseline committed
- [ ] Secrets masked with `::add-mask::`; no `echo $SECRET` in steps
- [ ] Workflow timeout set per job (`timeout-minutes`); no infinite hangs
- [ ] Monitor dashboard linked in deploy runbook

## References

- `references/gha-workflows.md` — full workflow examples (OIDC + AWS, OIDC + GCP, canary deploy, matrix test, monorepo selective runs). Read when building a new workflow from scratch.
- `references/deployment-runbooks.md` — rollback procedures, canary promotion checklist, incident response playbook. Read during incident or when drafting a release runbook.

## Cross-references

| Skill | When |
|---|---|
| `docker` | Building images referenced by workflows |
| `terraform` | Provisioning OIDC roles, IAM policies, secrets |
| `python` | Pre-commit hook choices (ruff, pytest) |
| `airflow` | DAG integrity checks as CI gate |
