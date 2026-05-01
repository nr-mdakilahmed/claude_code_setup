#!/usr/bin/env bash
# budget-set.sh — update ~/.claude/budget.json caps.

set -euo pipefail

DAILY=""
WEEKLY=""
MONTHLY=""
DOWNSHIFT=""

usage() {
  cat <<'EOF'
budget-set.sh — update budget caps

Usage:
  budget-set.sh [--daily N] [--weekly N] [--monthly N] [--downshift-pct N]

Any combination of flags; only passed flags are updated.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --daily) DAILY="${2:-}"; shift 2 ;;
    --weekly) WEEKLY="${2:-}"; shift 2 ;;
    --monthly) MONTHLY="${2:-}"; shift 2 ;;
    --downshift-pct) DOWNSHIFT="${2:-}"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

BUDGET="$HOME/.claude/budget.json"
[[ -f "$BUDGET" ]] || echo '{"daily_cap_usd":15,"weekly_cap_usd":75,"monthly_cap_usd":250,"auto_downshift_pct":80,"hard_warn_pct":100}' > "$BUDGET"

TMP=$(mktemp)
/usr/bin/jq \
  --arg d "$DAILY" --arg w "$WEEKLY" --arg m "$MONTHLY" --arg ds "$DOWNSHIFT" \
  '
  if $d != "" then .daily_cap_usd = ($d | tonumber) else . end
  | if $w != "" then .weekly_cap_usd = ($w | tonumber) else . end
  | if $m != "" then .monthly_cap_usd = ($m | tonumber) else . end
  | if $ds != "" then .auto_downshift_pct = ($ds | tonumber) else . end
  ' "$BUDGET" > "$TMP"
mv "$TMP" "$BUDGET"

echo "✓ Updated $BUDGET:"
/usr/bin/jq . "$BUDGET"
