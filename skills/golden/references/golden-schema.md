# Golden File Schema

Canonical structure for `~/.claude/golden/<pattern>.md`. Consumed by `/replay` and `golden-validate.sh` — breaking this schema breaks both. Treat it as a contract.

## Contents

- Frontmatter fields
- Body sections
- Minimal valid example
- Full example

## Frontmatter fields

```yaml
---
pattern: airflow-dag-timeout-fix      # REQUIRED — kebab-case slug, matches filename
scope: global                          # REQUIRED — "global" | "repo:<repo-name>"
tags:                                  # REQUIRED — 1-5 concrete topic tags
  - airflow
  - dag
  - timeout
trigger_hints:                         # REQUIRED — 3-5 phrases user would say when hitting this problem
  - "DAG timing out"
  - "task exceeded execution_timeout"
  - "SLA miss on daily ETL"
not_for:                               # OPTIONAL — phrases that should NOT match
  - "DAG scheduling delays"
  - "DAG parsing errors"
success_criteria: >                    # REQUIRED — how we know the fix worked
  DAG completes within SLA on 3 consecutive runs; no retry exhaustion alerts.
last_validated: 2026-05-01             # REQUIRED — ISO date; checked against 30-day staleness
fragile: false                         # OPTIONAL — true if known to break with minor repo changes
created: 2026-05-01                    # REQUIRED — ISO date of first capture
captured_from_repo: om-airflow-dags    # OPTIONAL — helpful for debugging scope issues
---
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `pattern` | string | yes | kebab-case; must match filename stem |
| `scope` | string | yes | `global` or `repo:<name>` |
| `tags` | array | yes | 1-5 concrete topic nouns |
| `trigger_hints` | array | yes | 3-5 phrases user would type when facing this problem |
| `not_for` | array | no | negative filter phrases |
| `success_criteria` | string | yes | 1-2 sentences; measurable |
| `last_validated` | ISO date | yes | bumped by `golden-validate --update` |
| `fragile` | bool | no | default false; true flags "may rot fast" |
| `created` | ISO date | yes | set on first save, never changes |
| `captured_from_repo` | string | no | informational |

## Body sections (required unless noted)

All sections use H2 (`##`). Order is fixed.

### `## Symptom`
1 paragraph, 3-5 sentences. What the user saw: error message, unexpected behavior, log excerpt. Written in the voice of the user reporting a problem.

### `## Root Cause Pattern`
2-4 bullet points. What was actually wrong, at the structural level — not just the one file that needed changing. The **pattern**, not the instance.

### `## Steps That Worked`
Numbered list. Each step has a `**Step N**` bold title + 1-2 lines of prose + optional fenced code block with the exact command or code change. Reference real file paths with line numbers where possible. 3-8 steps typical.

Example:
```
1. **Check DAG run logs for retry exhaustion**
   Identify which task failed and whether retries were attempted:
   ```bash
   astro dev logs --task <task_id> | grep -i "retry\|exhausted"
   ```

2. **Identify upstream bottleneck via the graph**
   ```
   MCP tool: query_graph
   pattern: callers_of
   node: <task_function>
   ```
```

### `## What NOT To Do`
Bulleted list of anti-patterns specifically surfaced during this investigation. Short, imperative, with **Why** clause.

Example:
```
- **Do not just increase `execution_timeout`** — hides the real bottleneck; SLA will keep slipping.
- **Do not disable retries on transient network failures** — masks upstream instability.
```

### `## Files Typically Touched`
Bulleted list of file paths. `/replay` validates these exist before loading.

```
- `dags/<dag_name>.py` — task definition and retry config
- `include/sql/<related_query>.sql` — if the query itself is the bottleneck
```

### `## Validation` (OPTIONAL)
If the fix has a deterministic validation command, put it here.

```bash
pytest tests/integration/test_dag_timeout.py -v
# Expected: all tests pass, task completes within execution_timeout.
```

### `## Notes` (OPTIONAL)
Anything else worth preserving — links to tickets, incident post-mortems, team discussions.

## Minimal valid example

```markdown
---
pattern: ruff-lint-preview-true
scope: repo:om-airflow-dags
tags: [ruff, lint, ci]
trigger_hints:
  - "ruff check failing on import order"
  - "pre-commit rejecting imports"
success_criteria: "ruff check --preview passes; pre-commit hook succeeds."
last_validated: 2026-05-01
created: 2026-05-01
---

## Symptom
`ruff check` passes locally but fails on CI with I001 errors on import blocks.

## Root Cause Pattern
- Local ruff uses preview rules; CI ruff doesn't.
- `pyproject.toml` missing `preview = true` under `[tool.ruff]`.

## Steps That Worked
1. **Add `preview = true` to pyproject.toml under `[tool.ruff]`**
   ```toml
   [tool.ruff]
   preview = true
   ```

2. **Run `ruff check --fix` locally** to apply preview rules consistently.

3. **Commit pyproject.toml + fixed files** in one PR.

## What NOT To Do
- **Do not downgrade ruff locally** — preview rules are worth keeping; align CI instead.

## Files Typically Touched
- `pyproject.toml`

## Validation
```bash
ruff check --preview . && pre-commit run --all-files
```
```
