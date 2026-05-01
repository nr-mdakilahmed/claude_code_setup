#!/usr/bin/env bash
# golden-save.sh — write a distilled golden-path markdown file + update index.
#
# Reads the distilled markdown body on stdin (sections: Symptom, Root Cause
# Pattern, Steps That Worked, What NOT To Do, Files Typically Touched).
# Composes frontmatter from flags, writes file to ~/.claude/golden/<pattern>.md,
# updates ~/.claude/golden/index.json.
#
# Usage:
#   cat body.md | golden-save.sh --pattern <slug> --scope <scope> \
#     --tags <t1,t2> --triggers <h1|h2|h3> --success "<criteria>" [--force]
#   golden-save.sh --help

set -euo pipefail

PATTERN=""
SCOPE=""
TAGS=""
TRIGGERS=""
NOT_FOR=""
SUCCESS=""
FRAGILE="false"
REPO_HINT=""
FORCE="false"

usage() {
  cat <<'EOF'
golden-save.sh — save a distilled golden-path to ~/.claude/golden/

Usage:
  <distilled-body> | golden-save.sh --pattern <slug> --scope <scope> \
    --tags <csv> --triggers <pipe-sep> --success "<criteria>" \
    [--not-for <pipe-sep>] [--fragile] [--captured-from <repo>] [--force]

Required:
  --pattern   kebab-case slug, e.g., airflow-dag-timeout-fix
  --scope     "global" or "repo:<name>"
  --tags      comma-separated, e.g., "airflow,dag,timeout"
  --triggers  pipe-separated phrases, e.g., "DAG timing out|SLA miss|retry exhausted"
  --success   1-2 sentence measurable success criteria

Optional:
  --not-for          pipe-separated negative filter phrases
  --fragile          mark this golden as known-fragile (rot risk)
  --captured-from    repo name where golden originated (informational)
  --force            overwrite existing file

Input:
  Read distilled markdown body on stdin — sections per golden-schema.md.

Exit codes:
  0  success
  1  argument error
  2  file already exists (no --force)
  3  stdin empty
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --pattern) PATTERN="${2:-}"; shift 2 ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --tags) TAGS="${2:-}"; shift 2 ;;
    --triggers) TRIGGERS="${2:-}"; shift 2 ;;
    --not-for) NOT_FOR="${2:-}"; shift 2 ;;
    --success) SUCCESS="${2:-}"; shift 2 ;;
    --fragile) FRAGILE="true"; shift ;;
    --captured-from) REPO_HINT="${2:-}"; shift 2 ;;
    --force) FORCE="true"; shift ;;
    *) echo "golden-save.sh: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

for req in PATTERN SCOPE TAGS TRIGGERS SUCCESS; do
  if [[ -z "${!req}" ]]; then
    echo "golden-save.sh: --${req,,} is required" >&2
    exit 1
  fi
done

if [[ ! "$PATTERN" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "golden-save.sh: --pattern must be kebab-case (lowercase, hyphens): got '$PATTERN'" >&2
  exit 1
fi

GOLDEN_DIR="$HOME/.claude/golden"
TARGET="$GOLDEN_DIR/$PATTERN.md"
INDEX="$GOLDEN_DIR/index.json"
mkdir -p "$GOLDEN_DIR"
[[ -f "$INDEX" ]] || echo '{"goldens": [], "version": "1.0"}' > "$INDEX"

if [[ -f "$TARGET" && "$FORCE" != "true" ]]; then
  echo "golden-save.sh: $TARGET already exists. Use --force to overwrite." >&2
  exit 2
fi

BODY=$(cat)
if [[ -z "$BODY" ]]; then
  echo "golden-save.sh: empty stdin — no body to save" >&2
  exit 3
fi

TODAY=$(date -u +%Y-%m-%d)

# Build YAML array from CSV
csv_to_yaml_array() {
  local csv="$1"
  local sep="$2"
  IFS="$sep" read -ra items <<< "$csv"
  for item in "${items[@]}"; do
    # Trim whitespace
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    printf '  - %s\n' "\"$item\""
  done
}

TAGS_YAML=$(csv_to_yaml_array "$TAGS" ",")
TRIGGERS_YAML=$(csv_to_yaml_array "$TRIGGERS" "|")
NOT_FOR_YAML=""
if [[ -n "$NOT_FOR" ]]; then
  NOT_FOR_YAML=$(csv_to_yaml_array "$NOT_FOR" "|")
fi

# Preserve created date if overwriting
CREATED="$TODAY"
if [[ -f "$TARGET" && "$FORCE" == "true" ]]; then
  EXISTING=$(grep -E '^created:' "$TARGET" | head -1 | sed 's/created:[[:space:]]*//')
  [[ -n "$EXISTING" ]] && CREATED="$EXISTING"
fi

{
  echo "---"
  echo "pattern: $PATTERN"
  echo "scope: $SCOPE"
  echo "tags:"
  echo "$TAGS_YAML"
  echo "trigger_hints:"
  echo "$TRIGGERS_YAML"
  if [[ -n "$NOT_FOR_YAML" ]]; then
    echo "not_for:"
    echo "$NOT_FOR_YAML"
  fi
  echo "success_criteria: >"
  echo "  $SUCCESS"
  echo "last_validated: $TODAY"
  echo "fragile: $FRAGILE"
  echo "created: $CREATED"
  [[ -n "$REPO_HINT" ]] && echo "captured_from_repo: $REPO_HINT"
  echo "---"
  echo ""
  echo "$BODY"
} > "$TARGET"

# Update index.json atomically
TMP_INDEX=$(mktemp)
/usr/bin/jq --arg pattern "$PATTERN" \
   --arg scope "$SCOPE" \
   --arg today "$TODAY" \
   --arg created "$CREATED" \
   --argjson tags "$(printf '%s\n' "$TAGS" | /usr/bin/jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))')" \
   --argjson fragile "$FRAGILE" \
   '
   .goldens = ([.goldens[] | select(.pattern != $pattern)] + [{
     pattern: $pattern,
     scope: $scope,
     tags: $tags,
     last_validated: $today,
     created: $created,
     fragile: $fragile
   }])
   ' "$INDEX" > "$TMP_INDEX"
mv "$TMP_INDEX" "$INDEX"

echo "✓ Saved: $TARGET"
echo "✓ Index: $INDEX ($(/usr/bin/jq '.goldens | length' "$INDEX") goldens total)"
echo ""
echo "Next: /replay $PATTERN  (load this golden on a future similar task)"
