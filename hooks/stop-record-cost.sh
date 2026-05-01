#!/usr/bin/env bash
# stop-record-cost.sh — Stop hook that appends this session's cost to cost.jsonl.
#
# Input (stdin JSON): includes .cost.total_cost_usd as provided by Claude Code.
# Silent on error; best-effort telemetry.

set -euo pipefail

LOG="$HOME/.claude/telemetry/cost.jsonl"
mkdir -p "$(dirname "$LOG")"

PAYLOAD=$(cat)
COST=$(echo "$PAYLOAD" | /usr/bin/jq -r '.cost.total_cost_usd // .cost // 0' 2>/dev/null || echo "0")
SESSION_ID=$(echo "$PAYLOAD" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null || echo "")
MODEL=$(echo "$PAYLOAD" | /usr/bin/jq -r '.model.id // .model // empty' 2>/dev/null || echo "")

# Only record if we got a numeric cost
if [[ "$COST" =~ ^[0-9]+\.?[0-9]*$ ]] && awk -v c="$COST" 'BEGIN{exit !(c>0)}'; then
  TODAY=$(date -u +%Y-%m-%d)
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  /usr/bin/jq -n -c \
    --arg date "$TODAY" \
    --arg ts "$TS" \
    --arg session "$SESSION_ID" \
    --arg model "$MODEL" \
    --argjson cost "$COST" \
    '{date: $date, ts: $ts, session: $session, model: $model, cost_usd: $cost, type: "session"}' \
    >> "$LOG" 2>/dev/null || true
fi

# Pass through (don't block Stop)
exit 0
