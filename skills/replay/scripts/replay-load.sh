#!/usr/bin/env bash
# replay-load.sh — validate a golden and print it for /replay context loading.
#
# Called by /replay <pattern>. Refuses to print if the golden is stale,
# unless --force is passed. On success, prints the full golden markdown
# so Claude can adopt it as the plan.
#
# Usage:
#   replay-load.sh --pattern <slug> [--dry-run] [--force]
#   replay-load.sh --help

set -euo pipefail

PATTERN=""
DRY_RUN="false"
FORCE="false"

usage() {
  cat <<'EOF'
replay-load.sh — validate + print a golden for replay

Usage:
  replay-load.sh --pattern <slug> [--dry-run] [--force]

Options:
  --pattern <slug>  Golden to load. Required.
  --dry-run         Print the golden but emit "DRY RUN" header — do not adopt as plan.
  --force           Print even if the golden is stale (use with care).
  --help            Show this help.

Exit codes:
  0  success (golden printed)
  1  argument error
  2  golden not found
  3  golden stale (no --force)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --pattern) PATTERN="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN="true"; shift ;;
    --force) FORCE="true"; shift ;;
    *) echo "replay-load.sh: unknown argument: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$PATTERN" ]] && { echo "replay-load.sh: --pattern is required" >&2; exit 1; }

GOLDEN="$HOME/.claude/golden/$PATTERN.md"
VALIDATE="$HOME/.claude-kit/skills/golden/scripts/golden-validate.sh"

if [[ ! -f "$GOLDEN" ]]; then
  echo "replay-load.sh: golden not found: $PATTERN"
  echo "  Run: golden-list.sh   (to see available goldens)"
  exit 2
fi

# Run validation unless forced
if [[ "$FORCE" != "true" ]]; then
  if [[ -x "$VALIDATE" ]]; then
    VALID_OUT=$("$VALIDATE" --pattern "$PATTERN" 2>&1) || VALID_EXIT=$?
    VALID_EXIT=${VALID_EXIT:-0}
    if [[ "$VALID_EXIT" != "0" ]]; then
      echo "replay-load.sh: golden is stale or broken:"
      echo "$VALID_OUT" | sed 's/^/  /'
      echo ""
      echo "To proceed anyway: replay-load.sh --pattern $PATTERN --force"
      echo "To refresh:        golden-validate.sh --pattern $PATTERN --update"
      exit 3
    fi
  fi
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "=== DRY RUN — Golden: $PATTERN ==="
  echo "(The following is shown for inspection; do NOT adopt as plan)"
  echo ""
fi

cat "$GOLDEN"

if [[ "$DRY_RUN" != "true" ]]; then
  echo ""
  echo "=== END GOLDEN: $PATTERN ==="
  echo ""
  echo "Instructions for Claude:"
  echo "  1. Restate the plan from this golden in 1-3 sentences."
  echo "  2. For each step, verify referenced files still exist before running."
  echo "  3. Track any divergences for /golden save update after task completion."
fi
