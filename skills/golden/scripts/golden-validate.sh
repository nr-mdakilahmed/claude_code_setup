#!/usr/bin/env bash
# golden-validate.sh — check a golden for staleness.
#
# Validation checks:
#   1. File exists at ~/.claude/golden/<pattern>.md
#   2. Frontmatter parses (required fields present)
#   3. All paths in "## Files Typically Touched" resolve for at least one
#      candidate repo (scope=global → check against home); scope=repo:<name>
#      → check against that repo if we can find it
#   4. last_validated within 30 days
#
# Usage:
#   golden-validate.sh --pattern <slug> [--update] [--repo-search-root <path>]
#   golden-validate.sh --help

set -euo pipefail

PATTERN=""
UPDATE="false"
REPO_SEARCH_ROOT="$HOME/Documents/GitHub"
STALE_DAYS=30

usage() {
  cat <<'EOF'
golden-validate.sh — check a golden for staleness

Usage:
  golden-validate.sh --pattern <slug> [--update] [--repo-search-root <path>]

Options:
  --pattern <slug>       Golden pattern to validate. Required.
  --update               On success, bump last_validated in frontmatter + index.
  --repo-search-root     Where to look for repo:<name> scope (default: ~/Documents/GitHub).
  --help                 Show this help.

Exit codes:
  0  fresh (within staleness window, all file refs resolve)
  1  stale (either >30d since validation, or file refs broken)
  2  missing (golden file does not exist)
  3  malformed (frontmatter missing required fields)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --pattern) PATTERN="${2:-}"; shift 2 ;;
    --update) UPDATE="true"; shift ;;
    --repo-search-root) REPO_SEARCH_ROOT="${2:-}"; shift 2 ;;
    *) echo "golden-validate.sh: unknown argument: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$PATTERN" ]] && { echo "golden-validate.sh: --pattern is required" >&2; exit 1; }

GOLDEN="$HOME/.claude/golden/$PATTERN.md"
INDEX="$HOME/.claude/golden/index.json"

if [[ ! -f "$GOLDEN" ]]; then
  echo "golden-validate.sh: not found: $GOLDEN"
  exit 2
fi

# Extract frontmatter between the first two `---` lines
FM=$(awk 'BEGIN {n=0} /^---$/ {n++; next} n==1 {print}' "$GOLDEN")
SCOPE=$(echo "$FM" | grep -E '^scope:' | head -1 | sed 's/scope:[[:space:]]*//')
LAST_VAL=$(echo "$FM" | grep -E '^last_validated:' | head -1 | sed 's/last_validated:[[:space:]]*//')

for req in SCOPE LAST_VAL; do
  [[ -z "${!req}" ]] && { echo "golden-validate.sh: frontmatter missing $req"; exit 3; }
done

# Staleness check
TODAY_EPOCH=$(date -u +%s)
VAL_EPOCH=$(date -u -j -f "%Y-%m-%d" "$LAST_VAL" "+%s" 2>/dev/null || date -u -d "$LAST_VAL" "+%s" 2>/dev/null || echo 0)
if [[ "$VAL_EPOCH" == "0" ]]; then
  echo "golden-validate.sh: could not parse last_validated='$LAST_VAL'"
  exit 3
fi
AGE_DAYS=$(( (TODAY_EPOCH - VAL_EPOCH) / 86400 ))

# Determine target repo for file-ref checks
TARGET_REPO=""
if [[ "$SCOPE" == "global" ]]; then
  TARGET_REPO=""
elif [[ "$SCOPE" =~ ^repo:(.+)$ ]]; then
  REPO_NAME="${BASH_REMATCH[1]}"
  if [[ -d "$REPO_SEARCH_ROOT/$REPO_NAME" ]]; then
    TARGET_REPO="$REPO_SEARCH_ROOT/$REPO_NAME"
  else
    echo "golden-validate.sh: repo '$REPO_NAME' not found under $REPO_SEARCH_ROOT — cannot validate file refs"
    echo "  (age: ${AGE_DAYS}d; staleness threshold: ${STALE_DAYS}d)"
    [[ "$AGE_DAYS" -gt "$STALE_DAYS" ]] && exit 1 || exit 0
  fi
fi

# Extract paths from "## Files Typically Touched" section
PATHS=$(awk '
  /^## Files Typically Touched/ { in_section = 1; next }
  /^## / && in_section { in_section = 0 }
  in_section && /^- `[^`]+`/ {
    match($0, /`[^`]+`/)
    print substr($0, RSTART + 1, RLENGTH - 2)
  }
' "$GOLDEN")

MISSING=0
TOTAL=0
while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  TOTAL=$((TOTAL + 1))
  # Strip any " — description" suffix if present; paths are just `<path>`
  path=$(echo "$path" | sed 's/ —.*//')
  if [[ -n "$TARGET_REPO" ]]; then
    full="$TARGET_REPO/$path"
  else
    full="$path"
  fi
  # Skip placeholder patterns like <dag_name>
  if [[ "$path" =~ \<[^\>]+\> ]]; then
    continue
  fi
  # Expand ~ to $HOME for existence check
  expanded_full="${full/#\~/$HOME}"
  if [[ ! -e "$expanded_full" ]]; then
    echo "  ✗ missing: $path"
    MISSING=$((MISSING + 1))
  fi
done <<< "$PATHS"

STATUS=0
if [[ "$AGE_DAYS" -gt "$STALE_DAYS" ]]; then
  echo "⚠ stale: last_validated=$LAST_VAL (${AGE_DAYS}d ago, threshold=${STALE_DAYS}d)"
  STATUS=1
fi
if [[ "$MISSING" -gt 0 ]]; then
  echo "⚠ $MISSING of $TOTAL file refs missing"
  STATUS=1
fi

if [[ "$STATUS" == "0" ]]; then
  echo "✓ fresh: $PATTERN (age=${AGE_DAYS}d, $TOTAL file refs OK)"
  if [[ "$UPDATE" == "true" ]]; then
    TODAY=$(date -u +%Y-%m-%d)
    /usr/bin/sed -i.bak "s/^last_validated:.*/last_validated: $TODAY/" "$GOLDEN"
    rm -f "$GOLDEN.bak"
    TMP_INDEX=$(mktemp)
    /usr/bin/jq --arg pattern "$PATTERN" --arg today "$TODAY" \
      '(.goldens[] | select(.pattern == $pattern) | .last_validated) |= $today' \
      "$INDEX" > "$TMP_INDEX" && mv "$TMP_INDEX" "$INDEX"
    echo "✓ bumped last_validated to $TODAY"
  fi
fi

exit $STATUS
