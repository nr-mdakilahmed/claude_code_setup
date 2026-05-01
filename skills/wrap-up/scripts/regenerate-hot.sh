#!/usr/bin/env bash
# regenerate-hot.sh — rebuild the curated hot.md digest from other memory files.
#
# hot.md is the ONLY memory file auto-loaded at session start (~2k tokens max).
# Everything else (architecture, todo, lessons, history) is pull-on-demand.
# This script is deterministic — same inputs produce same output.
#
# Contents:
#   - Active todos (up to 10)
#   - Recent lessons (last 10, newest first)
#   - Architecture one-paragraph summary (first paragraph of architecture.md)
#   - Stable conventions (anything tagged pinned: true in lessons.md, optional)

set -euo pipefail

MEMORY_DIR=""
MAX_ACTIVE_TODOS=10
MAX_LESSONS=10

usage() {
  cat <<'EOF'
regenerate-hot.sh — rebuild the curated hot.md session-start digest

Usage:
  regenerate-hot.sh --memory-dir <path>
  regenerate-hot.sh --help

Reads:
  <memory-dir>/architecture.md  (first paragraph)
  <memory-dir>/todo.md          (## Active section, top 10)
  <memory-dir>/lessons.md       (## Patterns section, last 10)

Writes:
  <memory-dir>/hot.md           (overwrites; ~2k tokens target)

Exit codes:
  0  success
  1  argument error
  2  memory-dir missing or incomplete
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --memory-dir) MEMORY_DIR="${2:-}"; shift 2 ;;
    *) echo "regenerate-hot.sh: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -z "$MEMORY_DIR" ]] && { echo "regenerate-hot.sh: --memory-dir is required" >&2; exit 1; }
[[ ! -d "$MEMORY_DIR" ]] && { echo "regenerate-hot.sh: memory dir not found: $MEMORY_DIR" >&2; exit 2; }

ARCH="$MEMORY_DIR/architecture.md"
TODO="$MEMORY_DIR/todo.md"
LESSONS="$MEMORY_DIR/lessons.md"
HOT="$MEMORY_DIR/hot.md"

# Extract first paragraph of architecture (skip blank/header lines, stop at blank after content)
arch_summary=""
if [[ -f "$ARCH" ]]; then
  arch_summary=$(awk '
    BEGIN { found = 0 }
    /^#/ { next }
    /^[[:space:]]*$/ { if (found) exit; else next }
    { found = 1; print }
  ' "$ARCH" | head -10)
fi
[[ -z "$arch_summary" ]] && arch_summary="_architecture.md not populated yet — run /bootstrap_"

# Extract top N items from ## Active section of todo.md
active_todos=""
if [[ -f "$TODO" ]]; then
  active_todos=$(awk -v max="$MAX_ACTIVE_TODOS" '
    /^## Active/ { in_active = 1; next }
    /^## / { in_active = 0 }
    in_active && /^- / { print; count++; if (count >= max) exit }
  ' "$TODO")
fi
[[ -z "$active_todos" ]] && active_todos="_no active todos_"

# Extract last N items from ## Patterns section of lessons.md (most-recent first)
recent_lessons=""
if [[ -f "$LESSONS" ]]; then
  recent_lessons=$(awk '
    /^## Patterns/ { in_p = 1; next }
    /^## / { in_p = 0 }
    in_p && /^- / { print }
  ' "$LESSONS" | tail -"$MAX_LESSONS" | tac 2>/dev/null || \
  awk '
    /^## Patterns/ { in_p = 1; next }
    /^## / { in_p = 0 }
    in_p && /^- / { print }
  ' "$LESSONS" | tail -r 2>/dev/null)
fi
[[ -z "$recent_lessons" ]] && recent_lessons="_no patterns logged yet_"

REPO_NAME=$(basename "$(dirname "$MEMORY_DIR")")

{
  echo "# Hot Memory — $REPO_NAME"
  echo ""
  echo "_Regenerated: $(date -u +%Y-%m-%dT%H:%M:%SZ) by regenerate-hot.sh. Auto-loaded at session start (~2k tokens target)._"
  echo ""
  echo "## Architecture (one-paragraph summary)"
  echo ""
  echo "$arch_summary"
  echo ""
  echo "## Active todos (top $MAX_ACTIVE_TODOS)"
  echo ""
  echo "$active_todos"
  echo ""
  echo "## Recent patterns (last $MAX_LESSONS, newest first)"
  echo ""
  echo "$recent_lessons"
  echo ""
  echo "## Deeper memory — pull on demand"
  echo ""
  echo "For more than the digest above, read directly:"
  echo "- \`$MEMORY_DIR/architecture.md\` — full architecture"
  echo "- \`$MEMORY_DIR/todo.md\` — full todo (active + backlog + done)"
  echo "- \`$MEMORY_DIR/lessons.md\` — full lessons (patterns + anti-patterns + wins)"
  echo "- \`$MEMORY_DIR/history.md\` — session-by-session log (grep for keywords)"
  echo ""
  echo "For plans from past sessions:"
  echo "- \`$(dirname "$MEMORY_DIR")/plans/\` — mirrored from ~/.claude/plans/"
} > "$HOT"

BYTES=$(wc -c < "$HOT" | tr -d ' ')
APPROX_TOKENS=$((BYTES / 4))
echo "✓ Regenerated $HOT ($BYTES bytes, ~$APPROX_TOKENS tokens)"
