#!/usr/bin/env bash
# budget-report.sh — tabular spend report over N days.

set -euo pipefail

DAYS=7
while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="${2:-7}"; shift 2 ;;
    --help|-h)
      echo "Usage: budget-report.sh [--days N]"
      echo "Shows per-day spend, overrides, session counts for last N days."
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

LOG="$HOME/.claude/telemetry/cost.jsonl"
[[ -f "$LOG" ]] || { echo "No records at $LOG."; exit 0; }

SINCE=$(date -u -v-"${DAYS}"d +%Y-%m-%d 2>/dev/null || date -u -d "${DAYS} days ago" +%Y-%m-%d)

echo "=== Budget Report — last ${DAYS}d (since $SINCE) ==="
echo ""
echo "Per-day spend:"
/usr/bin/jq -r --arg since "$SINCE" '
  select(.date >= $since and .type != "override")
  | "\(.date)\t\(.cost_usd)"
' "$LOG" | awk '
  { totals[$1] += $2; counts[$1] += 1 }
  END {
    for (d in totals) printf "  %s  \$%6.2f  (%d session%s)\n", d, totals[d], counts[d], (counts[d]==1?"":"s")
  }
' | sort

echo ""
echo "Overrides:"
OVERRIDE_COUNT=$(/usr/bin/jq -r --arg since "$SINCE" '
  select(.date >= $since and .type == "override")
  | "\(.date)  +\$\(.cost_usd)  — \(.reason)"
' "$LOG" | tee /dev/tty | wc -l | tr -d ' ')

if [[ "$OVERRIDE_COUNT" == "0" ]]; then
  echo "  (none)"
fi

echo ""
if (( OVERRIDE_COUNT >= 3 )); then
  echo "⚠ $OVERRIDE_COUNT overrides in ${DAYS}d — your caps are too low. Run: /budget set --daily <higher>"
fi
