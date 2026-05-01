#!/usr/bin/env bash
# grep-telemetry-report.sh — weekly summary of Grep/Glob usage.
# Run manually: ~/.claude/hooks/grep-telemetry-report.sh [--days N]
#
# Shows per-repo fallback rate (Grep when CRG graph existed). High fallback
# rate → either the graph is missing coverage, or Claude isn't preferring
# graph tools. Either is actionable.

set -euo pipefail

DAYS=7
while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="${2:-7}"; shift 2 ;;
    --help|-h)
      echo "Usage: grep-telemetry-report.sh [--days N]"
      echo "Shows Grep/Glob telemetry from last N days (default: 7)."
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

LOG="$HOME/.claude/telemetry/greps.jsonl"
[[ ! -f "$LOG" ]] && { echo "No telemetry yet at $LOG"; exit 0; }

SINCE=$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "${DAYS} days ago" +%Y-%m-%dT%H:%M:%SZ)

echo "=== Grep/Glob Telemetry — last ${DAYS}d (since $SINCE) ==="
echo ""

echo "--- Per-repo usage + fallback rate ---"
/usr/bin/jq -r --arg since "$SINCE" '
  select(.ts >= $since) | .repo
' "$LOG" | sort | uniq -c | sort -rn | head -20

echo ""
echo "--- Fallback rate (Grep when CRG graph exists) ---"
/usr/bin/jq -r --arg since "$SINCE" '
  select(.ts >= $since and .fallback == true) | .repo
' "$LOG" | sort | uniq -c | sort -rn | head -20

echo ""
echo "--- Top patterns searched ---"
/usr/bin/jq -r --arg since "$SINCE" '
  select(.ts >= $since) | .pattern
' "$LOG" | grep -v '^$' | sort | uniq -c | sort -rn | head -20

echo ""
echo "Tip: high fallback count on a repo with a graph means either the"
echo "graph is missing coverage OR Claude is not preferring graph tools."
echo "Tune via <repo>/.code-review-graphignore or CLAUDE.md guidance."
