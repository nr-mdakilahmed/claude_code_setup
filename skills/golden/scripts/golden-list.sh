#!/usr/bin/env bash
# golden-list.sh — list all goldens with optional filters.
#
# Reads ~/.claude/golden/index.json and prints a tabular view.
#
# Usage:
#   golden-list.sh [--tag <tag>] [--scope <scope>] [--stale-only] [--json]
#   golden-list.sh --help

set -euo pipefail

TAG_FILTER=""
SCOPE_FILTER=""
STALE_ONLY="false"
JSON_OUT="false"
STALE_DAYS=30

usage() {
  cat <<'EOF'
golden-list.sh — list goldens with filters

Usage:
  golden-list.sh [--tag <tag>] [--scope <scope>] [--stale-only] [--json]

Options:
  --tag <tag>      Show only goldens with this tag
  --scope <scope>  Show only goldens matching this scope ("global" or "repo:<name>")
  --stale-only     Show only goldens whose last_validated is >30 days old
  --json           Emit JSON instead of table
  --help           Show this help

Output columns: pattern | scope | tags | last_validated | age_days | fragile
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --tag) TAG_FILTER="${2:-}"; shift 2 ;;
    --scope) SCOPE_FILTER="${2:-}"; shift 2 ;;
    --stale-only) STALE_ONLY="true"; shift ;;
    --json) JSON_OUT="true"; shift ;;
    *) echo "golden-list.sh: unknown argument: $1" >&2; exit 1 ;;
  esac
done

INDEX="$HOME/.claude/golden/index.json"
if [[ ! -f "$INDEX" ]]; then
  echo "golden-list.sh: no index at $INDEX (no goldens saved yet)"
  exit 0
fi

TODAY_EPOCH=$(date -u +%s)

# Filter via jq
FILTERED=$(/usr/bin/jq \
  --arg tag "$TAG_FILTER" \
  --arg scope "$SCOPE_FILTER" \
  --arg stale_only "$STALE_ONLY" \
  --argjson today "$TODAY_EPOCH" \
  --argjson stale_days "$STALE_DAYS" \
  '
  .goldens
  | map(. + {
      age_days: (
        ((($today - (.last_validated | strptime("%Y-%m-%d") | mktime)) / 86400) | floor)
      )
    })
  | map(select($tag == "" or (.tags | contains([$tag]))))
  | map(select($scope == "" or .scope == $scope))
  | map(select($stale_only != "true" or .age_days > $stale_days))
  | sort_by(.age_days) | reverse
  ' "$INDEX")

if [[ "$JSON_OUT" == "true" ]]; then
  echo "$FILTERED"
  exit 0
fi

COUNT=$(echo "$FILTERED" | /usr/bin/jq 'length')
if [[ "$COUNT" == "0" ]]; then
  echo "(no goldens match filters)"
  exit 0
fi

printf '%-35s %-20s %-25s %-15s %-10s %s\n' \
  "pattern" "scope" "tags" "last_validated" "age_days" "fragile"
printf '%.s-' {1..115}
echo ""
echo "$FILTERED" | /usr/bin/jq -r '.[] |
  [.pattern, .scope, (.tags | join(",")), .last_validated, (.age_days | tostring), (.fragile | tostring)]
  | @tsv' | \
while IFS=$'\t' read -r pat scope tags lv age frag; do
  printf '%-35s %-20s %-25s %-15s %-10s %s\n' "$pat" "$scope" "$tags" "$lv" "$age" "$frag"
done

echo ""
echo "Total: $COUNT golden(s)"
