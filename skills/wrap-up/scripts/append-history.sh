#!/usr/bin/env bash
# append-history.sh — append a session entry to history.md
#
# Contract: writes one deterministic `## <SESSION_DATE>` block to
# $MEMORY_DIR/history.md. Idempotent guard: refuses to write if the same
# session-id already appears as a top-level heading in the file.
#
# The summary body is read from stdin so the caller can compose multi-line
# Markdown without shell-quoting hazards. Stdin format is free-form Markdown;
# the script wraps it with a heading line and a trailing separator.
#
# Usage:
#   append-history.sh --memory-dir <path> --session-id <id> < summary.md
#   append-history.sh --help

set -euo pipefail

MEMORY_DIR=""
SESSION_ID=""

usage() {
  cat <<'EOF'
append-history.sh — append a session entry to history.md

Usage:
  append-history.sh --memory-dir <path> --session-id <id> < summary.md
  append-history.sh --help

Options:
  --memory-dir <path>   Path to the memory directory that contains history.md.
                        Typically $HOME/.claude/projects/<REPO_NAME>/memory.
                        Required.
  --session-id <id>     Human-readable session identifier, usually a timestamp
                        like "2026-05-01 14:32". Becomes the `## ` heading.
                        Required. Must not already exist as a heading in
                        history.md.
  --help                Show this help and exit 0.

Input:
  Free-form Markdown on stdin — typically the Accomplished / Decisions /
  Blockers / Next sections prepared by the /wrap-up workflow.

Output:
  Appends a block shaped like:

    ## <SESSION_ID>
    <stdin contents>
    ---

  Creates history.md if it does not exist. Always writes a trailing blank line
  so the next append starts cleanly.

Exit codes:
  0  success
  1  argument error
  2  duplicate session-id already in history.md
  3  I/O failure (memory-dir missing, not writable)

Examples:
  printf '%s\n' '**Accomplished**: fixed DAG import error' \
    | append-history.sh --memory-dir ~/.claude/projects/myrepo/memory \
        --session-id "2026-05-01 14:32"
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --memory-dir)
      MEMORY_DIR="${2:-}"
      shift 2
      ;;
    --session-id)
      SESSION_ID="${2:-}"
      shift 2
      ;;
    *)
      echo "append-history.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$MEMORY_DIR" ]]; then
  echo "append-history.sh: --memory-dir is required" >&2
  exit 1
fi

if [[ -z "$SESSION_ID" ]]; then
  echo "append-history.sh: --session-id is required" >&2
  exit 1
fi

if [[ ! -d "$MEMORY_DIR" ]]; then
  echo "append-history.sh: memory-dir does not exist: $MEMORY_DIR" >&2
  exit 3
fi

HISTORY_FILE="$MEMORY_DIR/history.md"

# --- idempotency guard ---------------------------------------------------
if [[ -f "$HISTORY_FILE" ]] && grep -Fxq "## $SESSION_ID" "$HISTORY_FILE"; then
  echo "append-history.sh: session-id already present in history.md: $SESSION_ID" >&2
  exit 2
fi

# --- write ---------------------------------------------------------------
{
  if [[ -f "$HISTORY_FILE" ]]; then
    # Ensure a blank line between prior content and the new block.
    if [[ -s "$HISTORY_FILE" ]]; then
      tail -c 1 "$HISTORY_FILE" | od -An -c | grep -q '\\n' || echo ""
    fi
  fi
  echo "## $SESSION_ID"
  cat -  # stdin body
  echo ""
  echo "---"
  echo ""
} >> "$HISTORY_FILE"

echo "append-history.sh: appended session '$SESSION_ID' to $HISTORY_FILE"
exit 0
