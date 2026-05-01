#!/usr/bin/env bash
# mirror-plans.sh — copy this session's plans from ~/.claude/plans/ into the
# project-local plans/ dir so each repo has isolated plan history.
#
# Anthropic hardcodes plan writes to ~/.claude/plans/ (global). This script
# mirrors plans touched since the last wrap-up into the project folder.
# Called from /wrap-up Phase 6.
#
# Usage:
#   mirror-plans.sh --repo-name <name> --since <ISO8601>
#   mirror-plans.sh --help

set -euo pipefail

REPO_NAME=""
SINCE=""

usage() {
  cat <<'EOF'
mirror-plans.sh — mirror global plans into project-local plans/

Usage:
  mirror-plans.sh --repo-name <name> [--since <ISO8601>]
  mirror-plans.sh --help

Options:
  --repo-name   Repo basename (e.g. "om-airflow-dags"). Required.
  --since       Only mirror plans modified after this timestamp. Default: 24h ago.
  --help        Show this help and exit 0.

Behavior:
  Reads from  ~/.claude/plans/*.md
  Writes to   ~/.claude/projects/<repo-name>/plans/*.md

  Existing destination files are NOT overwritten unless the source is newer
  (mtime comparison). Mirroring is additive — the global dir remains the
  authoritative audit trail.

Exit codes:
  0  success (0 or more plans mirrored)
  1  argument error
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --repo-name) REPO_NAME="${2:-}"; shift 2 ;;
    --since) SINCE="${2:-}"; shift 2 ;;
    *) echo "mirror-plans.sh: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -z "$REPO_NAME" ]] && { echo "mirror-plans.sh: --repo-name is required" >&2; exit 1; }

SRC="$HOME/.claude/plans"
DEST="$HOME/.claude/projects/$REPO_NAME/plans"

if [[ ! -d "$SRC" ]]; then
  echo "mirror-plans.sh: no global plans dir at $SRC (nothing to mirror)"
  exit 0
fi

mkdir -p "$DEST"

# Default lookback: 24h if --since not given
FIND_ARGS=()
if [[ -n "$SINCE" ]]; then
  # Convert ISO to a temp file for -newer comparison
  TMPREF=$(mktemp)
  touch -t "$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SINCE" "+%Y%m%d%H%M.%S" 2>/dev/null || date -d "$SINCE" "+%Y%m%d%H%M.%S" 2>/dev/null)" "$TMPREF" 2>/dev/null || touch -t "$(date -v-24H +%Y%m%d%H%M.%S)" "$TMPREF"
  FIND_ARGS=(-newer "$TMPREF")
else
  FIND_ARGS=(-mtime -1)
fi

COUNT=0
while IFS= read -r -d '' plan; do
  fname=$(basename "$plan")
  target="$DEST/$fname"
  if [[ ! -f "$target" ]] || [[ "$plan" -nt "$target" ]]; then
    cp -p "$plan" "$target"
    COUNT=$((COUNT + 1))
  fi
done < <(find "$SRC" -maxdepth 1 -type f -name "*.md" "${FIND_ARGS[@]}" -print0 2>/dev/null)

[[ -n "${TMPREF:-}" ]] && rm -f "$TMPREF"

echo "✓ Mirrored $COUNT plan(s) to $DEST"
