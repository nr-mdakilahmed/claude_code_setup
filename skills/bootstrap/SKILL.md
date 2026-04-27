---
name: bootstrap
description: >
  Run ONCE per new repo. Scans codebase, seeds memory at ~/.claude/projects/<REPO_NAME>/,
  creates <repo>/.claude/CLAUDE.md that references memory via @.
  Use opus model. Invoke with /bootstrap.
---

# /bootstrap — First Visit Setup

**Run ONCE per new repo.** Scans codebase, seeds memory, generates project CLAUDE.md.
Use **opus** model.

## Setup Variables

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPO_NAME=$(basename "$REPO_ROOT")
MEMORY_DIR="$HOME/.claude/projects/$REPO_NAME/memory"
GRAPHS_DIR="$HOME/.claude/projects/$REPO_NAME/graphs"
PROJECT_CLAUDE_DIR="$REPO_ROOT/.claude"
PROJECT_CLAUDE="$PROJECT_CLAUDE_DIR/CLAUDE.md"
mkdir -p "$MEMORY_DIR" "$GRAPHS_DIR" "$PROJECT_CLAUDE_DIR"
```

## Phase 1 — Detect Repo

1. Check `$MEMORY_DIR/MEMORY.md` exists — if yes, warn and confirm before overwriting
2. Check `$GRAPHS_DIR/graph.json` — if exists, skip Phase 2
3. Detect stack: scan for pyproject.toml, requirements.txt, package.json, go.mod, Cargo.toml, dags/, Dockerfile, docker-compose.yml, *.tf, dbt_project.yml, airflow.cfg, Makefile
4. Classify as Data Engineering repo if: Python + any of (airflow, pyspark, dbt, kafka, snowflake, bigquery, redshift)
5. Print status: Repo, Root, Stack detected, Memory (new/exists), Graph (new/exists)

## Phase 2 — /graphify

Invoke `/graphify` to scan codebase and produce graph.json, GRAPH_REPORT.md, graph.html in `$GRAPHS_DIR`.
Skip if graph.json exists and user confirms it's current.

## Phase 3 — Seed Memory Files

Create files in `$MEMORY_DIR/` (skip if already exists, except MEMORY.md which always refreshes).
**Substitute actual `$REPO_NAME` value everywhere** — never write the literal string `<REPO_NAME>`.

- **architecture.md** — extracted from `$GRAPHS_DIR/GRAPH_REPORT.md`: tech stack, key modules, entry points, data flow, conventions (100-200 lines max)
- **todo.md** — three sections: `## Active`, `## Backlog`, `## Done`
- **lessons.md** — three sections: `## Patterns` (rules), `## Anti-patterns` (what not to do), `## Wins` (approaches that worked)
- **history.md** — append-only; first entry: bootstrap date + stack summary
- **MEMORY.md** — index linking all files (write actual `$REPO_NAME`, not placeholder):
  ```markdown
  # $REPO_NAME Memory Index

  - [Architecture](~/.claude/projects/$REPO_NAME/memory/architecture.md) — tech stack, modules, entry points
  - [Todo](~/.claude/projects/$REPO_NAME/memory/todo.md) — active tasks and backlog
  - [Lessons](~/.claude/projects/$REPO_NAME/memory/lessons.md) — patterns and anti-patterns
  - [History](~/.claude/projects/$REPO_NAME/memory/history.md) — session history (not auto-loaded)
  - [Graph Report](~/.claude/projects/$REPO_NAME/graphs/GRAPH_REPORT.md) — codebase knowledge graph
  ```

## Phase 4 — Generate Project CLAUDE.md + .gitignore

### 4a — .gitignore

Add `.claude/` to `$REPO_ROOT/.gitignore` if not already present. The project CLAUDE.md contains personal `~/` paths and must never be committed.

### 4b — Write `$PROJECT_CLAUDE`

Top section MUST be `@` references to ALL project artifacts (write actual `$REPO_NAME`, not placeholder).
**history.md is intentionally excluded** — it's large and append-only; not useful every session.

### Base template (all repos):

```markdown
@~/.claude/projects/$REPO_NAME/memory/MEMORY.md
@~/.claude/projects/$REPO_NAME/memory/architecture.md
@~/.claude/projects/$REPO_NAME/memory/todo.md
@~/.claude/projects/$REPO_NAME/memory/lessons.md
@~/.claude/projects/$REPO_NAME/graphs/GRAPH_REPORT.md

# $REPO_NAME

## Stack
| Layer | Tech |
|-------|------|
<auto-detected rows>

## Entry Points
<list from graph, e.g.:>
- `src/main.py` — application entrypoint
- `dags/` — Airflow DAG definitions

## Key Conventions
<auto-detected from graph, e.g.:>
- Config: environment variables via python-dotenv
- Tests: pytest in `tests/`, fixtures in `conftest.py`
- Naming: snake_case modules, PascalCase classes

## Skills
<relevant subset based on detected stack — use actual skill names>
- `/python` — code review, ruff/uv/pyright, pytest
- `/systematic-debugging` — hypothesis-driven debugging
- `/wrap-up` — run at end of every session
```

### Additional section for Data Engineering repos:

```markdown
## Data Engineering Rules
- **No large XCom** — pass S3/GCS paths, not data payloads
- **Idempotent tasks** — every Airflow task must be safe to re-run
- **Parameterized SQL** — never f-string values into queries; use bind params
- **Schema-first** — define Pydantic/dataclass contracts before writing transforms
- **Test pyramid** — unit (pure functions) → integration (with fixtures) → E2E (staging only)
- **Lazy imports in DAGs** — no heavy imports at DAG module level
- **Secrets via env** — use Airflow Connections, Vault, or env vars; never hardcode

## DE Skills
- `/airflow` — DAG patterns, TaskFlow API, debugging pipeline runs
- `/pyspark` — optimization, joins, Delta Lake, partitioning
- `/sql` — Snowflake/BigQuery/Redshift/dbt patterns
- `/cicd` — pipeline CI/CD, deployment strategies
- `/docker` — multi-stage builds, non-root, security
- `/profiling` — Python performance profiling
```

## Phase 5 — Summary

```
Bootstrap complete — $REPO_NAME
  Memory:  ~/.claude/projects/$REPO_NAME/memory/
  Graph:   ~/.claude/projects/$REPO_NAME/graphs/
  Rules:   $REPO_ROOT/.claude/CLAUDE.md  (5 @ refs load full context on session open)
  Stack:   <detected stack summary>

Next: run /wrap-up at end of every session.
```
