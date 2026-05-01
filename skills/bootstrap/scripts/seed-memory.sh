#!/usr/bin/env bash
# seed-memory.sh — seed 5 skeleton memory files for a fresh repo
#
# Contract: creates ~/.claude/projects/<REPO_NAME>/memory/ with:
#   MEMORY.md, architecture.md, todo.md, lessons.md, history.md
# Does NOT overwrite existing files (except MEMORY.md, which always refreshes
# as a pure index). Safe to re-run.
#
# Usage:
#   seed-memory.sh --repo-name <name> --memory-dir <path>
#   seed-memory.sh --help

set -euo pipefail

REPO_NAME=""
MEMORY_DIR=""

usage() {
  cat <<'EOF'
seed-memory.sh — seed 5 skeleton memory files for a fresh repo

Usage:
  seed-memory.sh --repo-name <name> --memory-dir <path>
  seed-memory.sh --help

Options:
  --repo-name <name>     Repo basename; substituted into MEMORY.md headings and @ refs.
  --memory-dir <path>    Absolute path to the memory dir (e.g., ~/.claude/projects/<name>/memory).
  --help                 Show this help and exit 0.

Behavior:
  Creates the directory if missing.
  Writes each of these 5 files only if absent (preserves prior content):
    architecture.md  — stack, modules, entry points, conventions
    todo.md          — Active / Backlog / Done
    lessons.md       — Patterns / Anti-patterns / Wins
    history.md       — append-only log; seeded with bootstrap date
  Always rewrites MEMORY.md (it is a pure index derived from the other files).

Exit codes:
  0  success
  1  argument or path error

Examples:
  seed-memory.sh --repo-name myapp --memory-dir ~/.claude/projects/myapp/memory
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --repo-name)
      REPO_NAME="${2:-}"
      shift 2
      ;;
    --memory-dir)
      MEMORY_DIR="${2:-}"
      shift 2
      ;;
    *)
      echo "seed-memory.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_NAME" ]]; then
  echo "seed-memory.sh: --repo-name is required" >&2
  exit 1
fi
if [[ -z "$MEMORY_DIR" ]]; then
  echo "seed-memory.sh: --memory-dir is required" >&2
  exit 1
fi

mkdir -p "$MEMORY_DIR"

TODAY="$(date -u '+%Y-%m-%d')"

# --- architecture.md ------------------------------------------------------
if [[ ! -f "$MEMORY_DIR/architecture.md" ]]; then
  cat > "$MEMORY_DIR/architecture.md" <<EOF
# ${REPO_NAME} — Architecture

## Tech Stack
<!-- Populate from GRAPH_REPORT.md. Example:
| Layer | Tech |
|---|---|
| Orchestration | Airflow 2.x |
| Compute       | PySpark 3.4 |
| Warehouse     | Snowflake   |
-->

## Entry Points
<!-- List runnable entrypoints. Example:
- \`src/main.py\` — CLI application entrypoint
- \`dags/etl_daily.py\` — daily ETL DAG
-->

## Key Modules
<!-- Top 5-10 most-imported modules. Pull from graph hotspots. -->

## Data Flow
<!-- 3-5 bullet narrative of how data moves through the system. -->

## Conventions
<!-- Project-specific rules the codebase follows. Example:
- Config: env vars via python-dotenv; Vault for secrets
- Tests: pytest; fixtures in conftest.py; marker \`@pytest.mark.integration\` for DB tests
- Naming: snake_case modules, PascalCase classes, SCREAMING_SNAKE for constants
-->

## Known Risks
<!-- Debt, brittle spots, fragile integrations. Keep this honest. -->
EOF
fi

# --- todo.md --------------------------------------------------------------
if [[ ! -f "$MEMORY_DIR/todo.md" ]]; then
  cat > "$MEMORY_DIR/todo.md" <<EOF
# ${REPO_NAME} — Todo

## Active
<!-- In-progress tasks. Max 3. Move to Done when shipped. -->

## Backlog
<!-- Not started. Prioritized top-to-bottom. -->

## Done
<!-- Shipped. Append newest at the top. -->

- ${TODAY} — Ran /bootstrap; seeded memory and graph.
EOF
fi

# --- lessons.md -----------------------------------------------------------
if [[ ! -f "$MEMORY_DIR/lessons.md" ]]; then
  cat > "$MEMORY_DIR/lessons.md" <<EOF
# ${REPO_NAME} — Lessons

## Patterns
<!-- Rules this codebase enforces. Imperative. Example:
- **Use lazy imports inside Airflow task functions** — module-level imports break the scheduler.
- **Parameterize every SQL query** — f-strings are a security review blocker.
-->

## Anti-patterns
<!-- What NOT to do. Example:
- **No large XCom payloads** — pass S3/GCS paths instead.
- **No \`datetime.utcnow()\`** — use \`datetime.now(timezone.utc)\`.
-->

## Wins
<!-- Approaches that worked and should be repeated. Example:
- Switched daily reconciliation to incremental dbt model — 20x faster, same correctness.
-->
EOF
fi

# --- history.md -----------------------------------------------------------
if [[ ! -f "$MEMORY_DIR/history.md" ]]; then
  cat > "$MEMORY_DIR/history.md" <<EOF
# ${REPO_NAME} — Session History

<!-- Append-only. Newest at top. Not auto-loaded by the project CLAUDE.md —
     this file grows large and is only useful when you need recall. -->

## ${TODAY} — Bootstrap
- Ran /bootstrap; seeded memory and graph artifacts.
- Stack summary: <fill in after detect-stack.sh>.
EOF
fi

# --- MEMORY.md (always rewrite — pure index) ------------------------------
cat > "$MEMORY_DIR/MEMORY.md" <<EOF
# ${REPO_NAME} Memory Index

- [Architecture](~/.claude/projects/${REPO_NAME}/memory/architecture.md) — tech stack, modules, entry points, conventions
- [Todo](~/.claude/projects/${REPO_NAME}/memory/todo.md) — active tasks and backlog
- [Lessons](~/.claude/projects/${REPO_NAME}/memory/lessons.md) — patterns and anti-patterns
- [History](~/.claude/projects/${REPO_NAME}/memory/history.md) — session history (not auto-loaded)
- [Graph Report](~/.claude/projects/${REPO_NAME}/graphs/GRAPH_REPORT.md) — codebase knowledge graph

<!-- Auto-loaded via @ references in <repo>/.claude/CLAUDE.md on every session start. -->
EOF

echo "seed-memory.sh: seeded $MEMORY_DIR (MEMORY.md refreshed; others preserved if present)"
