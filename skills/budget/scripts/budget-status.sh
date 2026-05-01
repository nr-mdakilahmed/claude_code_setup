#!/usr/bin/env bash
# budget-status.sh — print today/week/month spend vs caps.
#
# Sources (in priority order, per range):
#   1. /tmp/claude_daily_<today>.cost  (cached by statusline; today only)
#   2. JSONL project transcripts in ~/.claude/projects/**/*.jsonl
#   3. ~/.claude/telemetry/cost.jsonl  (session-end records + overrides)

set -euo pipefail

usage() {
  cat <<'EOF'
budget-status.sh — print today/week/month spend vs caps with traffic-light icons

Usage:
  budget-status.sh

No arguments. Reads ~/.claude/budget.json for caps and computes spend from:
  1. /tmp/claude_daily_<today>.cost  (cached by statusline)
  2. ~/.claude/projects/**/*.jsonl   (Claude Code transcripts)
  3. ~/.claude/telemetry/cost.jsonl  (session-end records + overrides)

Exit codes:
  0  always (advisory skill)
  1  if ~/.claude/budget.json is missing
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

BUDGET="$HOME/.claude/budget.json"

if [[ ! -f "$BUDGET" ]]; then
  echo "budget-status.sh: no budget at $BUDGET — run: budget-set.sh --daily 15 --weekly 75"
  exit 1
fi

DAILY_CAP=$(/usr/bin/jq -r '.daily_cap_usd' "$BUDGET")
WEEKLY_CAP=$(/usr/bin/jq -r '.weekly_cap_usd' "$BUDGET")
MONTHLY_CAP=$(/usr/bin/jq -r '.monthly_cap_usd' "$BUDGET")
DOWNSHIFT_PCT=$(/usr/bin/jq -r '.auto_downshift_pct' "$BUDGET")

# ---------------------------------------------------------------------------
# Compute spend for a given date range from JSONL transcripts.
# Mirrors the statusline's fallback logic.
# Args: $1=start_date (YYYY-MM-DD inclusive), $2=end_date (YYYY-MM-DD inclusive)
# ---------------------------------------------------------------------------
jsonl_spend() {
  local since="$1"
  local until="$2"
  python3 - "$since" "$until" <<'PYEOF'
import sys, json, os, glob
since, until = sys.argv[1], sys.argv[2]

def cost(u, model):
    m = (model or "").lower()
    if "opus" in m:
        p = (15.00, 75.00, 18.75, 1.50)
    elif "haiku" in m:
        p = (0.80, 4.00, 1.00, 0.08)
    else:
        p = (3.00, 15.00, 3.75, 0.30)
    return (
        (u.get("input_tokens", 0) or 0) * p[0]
        + (u.get("output_tokens", 0) or 0) * p[1]
        + (u.get("cache_creation_input_tokens", 0) or 0) * p[2]
        + (u.get("cache_read_input_tokens", 0) or 0) * p[3]
    ) / 1_000_000

total = 0.0
for f in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
    try:
        with open(f, errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line.strip())
                    ts = d.get("timestamp", "")[:10]
                    if not (since <= ts <= until):
                        continue
                    msg = d.get("message") or {}
                    u = msg.get("usage")
                    if not isinstance(u, dict):
                        continue
                    total += cost(u, msg.get("model", ""))
                except Exception:
                    pass
    except Exception:
        pass

# Also include any session/override rows in ~/.claude/telemetry/cost.jsonl
log = os.path.expanduser("~/.claude/telemetry/cost.jsonl")
if os.path.exists(log):
    try:
        with open(log, errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line.strip())
                    date = d.get("date", "")
                    if not (since <= date <= until):
                        continue
                    c = d.get("cost_usd", 0) or 0
                    total += float(c)
                except Exception:
                    pass
    except Exception:
        pass

print(f"{total:.2f}")
PYEOF
}

TODAY=$(date -u +%Y-%m-%d)
WEEK_START=$(date -u -v-6d +%Y-%m-%d 2>/dev/null || date -u -d "6 days ago" +%Y-%m-%d)
MONTH_START=$(date -u -v-29d +%Y-%m-%d 2>/dev/null || date -u -d "29 days ago" +%Y-%m-%d)

# Daily: prefer the statusline cache (it already queried NR MCP)
DAILY_CACHE="/tmp/claude_daily_${TODAY}.cost"
if [[ -f "$DAILY_CACHE" ]]; then
  DAILY=$(awk '{printf "%.2f", $1}' "$DAILY_CACHE")
else
  DAILY=$(jsonl_spend "$TODAY" "$TODAY")
fi

# Weekly/monthly: scan JSONL + cost.jsonl
WEEKLY=$(jsonl_spend "$WEEK_START" "$TODAY")
MONTHLY=$(jsonl_spend "$MONTH_START" "$TODAY")

pct() { awk -v a="$1" -v b="$2" 'BEGIN{ if (b==0) print 0; else printf "%.0f", 100*a/b }'; }
DAILY_PCT=$(pct "$DAILY" "$DAILY_CAP")
WEEKLY_PCT=$(pct "$WEEKLY" "$WEEKLY_CAP")
MONTHLY_PCT=$(pct "$MONTHLY" "$MONTHLY_CAP")

status_icon() {
  local pct="$1"
  if   [[ "$pct" -ge 100 ]]; then echo "🔴"
  elif [[ "$pct" -ge "$DOWNSHIFT_PCT" ]]; then echo "🟡"
  else echo "🟢"; fi
}

echo "=== Budget Status — ${TODAY} ==="
printf "  %s Daily    (today):        \$%7.2f / \$%6.2f  (%3d%%)\n"   "$(status_icon "$DAILY_PCT")"   "$DAILY"   "$DAILY_CAP"   "$DAILY_PCT"
printf "  %s Weekly   (last 7d):      \$%7.2f / \$%6.2f  (%3d%%)\n"   "$(status_icon "$WEEKLY_PCT")"  "$WEEKLY"  "$WEEKLY_CAP"  "$WEEKLY_PCT"
printf "  %s Monthly  (last 30d):     \$%7.2f / \$%6.2f  (%3d%%)\n"   "$(status_icon "$MONTHLY_PCT")" "$MONTHLY" "$MONTHLY_CAP" "$MONTHLY_PCT"

if [[ "$DAILY_PCT" -ge 100 || "$WEEKLY_PCT" -ge 100 || "$MONTHLY_PCT" -ge 100 ]]; then
  echo ""
  echo "🔴 Over cap. Use Haiku/Sonnet only; /budget override <usd> --reason \"...\" if urgent."
elif [[ "$DAILY_PCT" -ge "$DOWNSHIFT_PCT" || "$WEEKLY_PCT" -ge "$DOWNSHIFT_PCT" || "$MONTHLY_PCT" -ge "$DOWNSHIFT_PCT" ]]; then
  echo ""
  echo "🟡 Approaching cap. Consider /model haiku for the next mechanical tasks."
fi
