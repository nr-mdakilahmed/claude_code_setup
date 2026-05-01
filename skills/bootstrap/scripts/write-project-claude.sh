#!/usr/bin/env bash
# write-project-claude.sh — generate <repo>/.claude/CLAUDE.md with @ refs to memory
#
# Contract: creates <repo>/.claude/CLAUDE.md with 5 @ references to the user's
# ~/.claude/projects/<REPO_NAME>/ memory + graph artifacts. Adds .claude/ to
# <repo>/.gitignore if not already present (this CLAUDE.md contains ~/ paths
# and MUST NOT be committed).
#
# Usage:
#   write-project-claude.sh --repo <path> --memory-dir <path>
#   write-project-claude.sh --help

set -euo pipefail

REPO=""
MEMORY_DIR=""

usage() {
  cat <<'EOF'
write-project-claude.sh — generate <repo>/.claude/CLAUDE.md with @ refs

Usage:
  write-project-claude.sh --repo <path> --memory-dir <path>
  write-project-claude.sh --help

Options:
  --repo <path>        Absolute path to the repo root. Required.
  --memory-dir <path>  Absolute path to the memory dir. Required. The repo name
                       is derived from the parent of this dir when building
                       @ references (i.e., ~/.claude/projects/<REPO_NAME>/).
  --help               Show this help and exit 0.

Behavior:
  1. Ensures <repo>/.claude/ exists.
  2. Appends ".claude/" to <repo>/.gitignore if not already listed.
  3. Writes <repo>/.claude/CLAUDE.md containing:
       - 5 @ references to user-global memory and graph
         (MEMORY.md index, architecture.md, todo.md, lessons.md, GRAPH_REPORT.md;
          history.md is intentionally excluded — large and append-only)
       - Project header and placeholder sections for stack, entry points,
         conventions, and recommended skills.

  Overwrites existing <repo>/.claude/CLAUDE.md — re-run is safe but the file
  is regenerated from the current memory layout.

Exit codes:
  0  success
  1  argument or path error

Examples:
  write-project-claude.sh --repo "$(pwd)" \
    --memory-dir ~/.claude/projects/myapp/memory
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --memory-dir)
      MEMORY_DIR="${2:-}"
      shift 2
      ;;
    *)
      echo "write-project-claude.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "write-project-claude.sh: --repo is required" >&2
  exit 1
fi
if [[ -z "$MEMORY_DIR" ]]; then
  echo "write-project-claude.sh: --memory-dir is required" >&2
  exit 1
fi
if [[ ! -d "$REPO" ]]; then
  echo "write-project-claude.sh: --repo path does not exist: $REPO" >&2
  exit 1
fi

REPO_ABS="$(cd "$REPO" && pwd)"
# Derive REPO_NAME from the memory-dir parent (i.e., projects/<REPO_NAME>/memory).
REPO_NAME="$(basename "$(dirname "$MEMORY_DIR")")"

# --- .claude dir ---------------------------------------------------------
PROJECT_CLAUDE_DIR="$REPO_ABS/.claude"
PROJECT_CLAUDE="$PROJECT_CLAUDE_DIR/CLAUDE.md"
mkdir -p "$PROJECT_CLAUDE_DIR"

# --- .gitignore ----------------------------------------------------------
GITIGNORE="$REPO_ABS/.gitignore"
if [[ ! -f "$GITIGNORE" ]] || ! grep -qE '^\.claude/?$' "$GITIGNORE"; then
  {
    [[ -f "$GITIGNORE" ]] && echo ""
    echo "# Claude Code per-project memory — contains ~/ paths, do not commit"
    echo ".claude/"
  } >> "$GITIGNORE"
fi

# --- write CLAUDE.md -----------------------------------------------------
cat > "$PROJECT_CLAUDE" <<EOF
@~/.claude/projects/${REPO_NAME}/memory/MEMORY.md
@~/.claude/projects/${REPO_NAME}/memory/architecture.md
@~/.claude/projects/${REPO_NAME}/memory/todo.md
@~/.claude/projects/${REPO_NAME}/memory/lessons.md
@~/.claude/projects/${REPO_NAME}/graphs/GRAPH_REPORT.md

# ${REPO_NAME}

## Stack

<!-- Populate from detect-stack.sh output and graph report. Example:
| Layer | Tech |
|-------|------|
| Language   | Python 3.12 |
| Framework  | Airflow 2.x |
| Warehouse  | Snowflake   |
-->

## Entry Points

<!-- Auto-fill from GRAPH_REPORT.md "Entry Points" section. Example:
- \`src/main.py\` — application entrypoint
- \`dags/\` — Airflow DAG definitions
-->

## Key Conventions

<!-- Project-specific rules. Pull from architecture.md "Conventions". Example:
- Config via env vars (python-dotenv); secrets in Vault
- Tests in \`tests/\`, fixtures in \`conftest.py\`
- Naming: snake_case modules, PascalCase classes
-->

## Skills

<!-- List the skills most relevant to this stack. Keep to 5–8 entries.
     Runtime-universal picks:
- \`/python\` — code review, ruff/uv/pyright, pytest
- \`/wrap-up\` — run at end of every session
- \`superpowers:systematic-debugging\` — hypothesis-driven debugging

     Add from this menu based on detected stack:
- \`/airflow\`      — DAGs, TaskFlow, scheduler debugging
- \`/pyspark\`      — joins, partitioning, AQE, Delta
- \`/sql\`          — Snowflake/BigQuery/Redshift/dbt
- \`/cicd\`         — GitHub Actions, OIDC, deployment gates
- \`/docker\`       — multi-stage, non-root, healthchecks
- \`/terraform\`    — New Relic alerts/dashboards via IaC
- \`/profiling\`    — cProfile, py-spy, tracemalloc
- \`/nrql\`         — New Relic query optimization
- \`/nralert\`      — alert correlation and muting
- \`/openmetadata\` — ingestion, lineage, data quality
- \`/shell\`        — bash strict mode, arg parsing
- \`/mcp-builder\`  — MCP servers for tool integration
-->

## Notes

<!-- Free-form. Links to runbooks, dashboards, owner contacts, on-call rotations. -->
EOF

echo "write-project-claude.sh: wrote $PROJECT_CLAUDE"
echo "write-project-claude.sh: ensured .claude/ in $GITIGNORE"
