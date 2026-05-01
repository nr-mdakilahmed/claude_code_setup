#!/usr/bin/env bash
# budget-override.sh — log a one-time buffer with reason.

set -euo pipefail

USD=""
REASON=""

usage() {
  cat <<'EOF'
budget-override.sh — add one-time buffer

Usage:
  budget-override.sh <USD> --reason "<why>"
  budget-override.sh --help

Writes an override entry to ~/.claude/telemetry/cost.jsonl with type=override.
budget-status.sh counts these toward "overrides this week" for discipline.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --reason) REASON="${2:-}"; shift 2 ;;
    *)
      if [[ -z "$USD" && "$1" =~ ^[0-9]+\.?[0-9]*$ ]]; then
        USD="$1"
        shift
      else
        echo "unknown arg: $1" >&2; exit 1
      fi
      ;;
  esac
done

[[ -z "$USD" ]] && { echo "budget-override.sh: USD amount required" >&2; exit 1; }
[[ -z "$REASON" ]] && { echo "budget-override.sh: --reason required" >&2; exit 1; }

LOG="$HOME/.claude/telemetry/cost.jsonl"
mkdir -p "$(dirname "$LOG")"
TODAY=$(date -u +%Y-%m-%d)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

/usr/bin/jq -n -c \
  --arg date "$TODAY" \
  --arg ts "$TS" \
  --arg reason "$REASON" \
  --argjson usd "$USD" \
  '{date: $date, ts: $ts, type: "override", cost_usd: $usd, reason: $reason}' \
  >> "$LOG"

echo "✓ Logged override: +\$$USD today — \"$REASON\""
echo "  Remember: if you override >2x/week, raise your caps instead."
