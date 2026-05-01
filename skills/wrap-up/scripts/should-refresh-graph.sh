#!/usr/bin/env bash
# should-refresh-graph.sh — decide whether /graphify should be re-run
#
# Contract: inspects git diff since a given timestamp (or ref) and reports
# whether the structural change exceeds the threshold that would invalidate
# the cached graph.
#
# Exit codes:
#   0  refresh needed (>THRESHOLD source files changed, or new top-level dir)
#   1  skip refresh (change is below threshold, or doc-only / test-only)
#   2  argument or repo error
#
# Prints a short one-line summary to stdout in both cases so the caller can log
# the reason.
#
# Usage:
#   should-refresh-graph.sh --repo <path> --since <timestamp-or-ref>
#   should-refresh-graph.sh --help

set -euo pipefail

REPO=""
SINCE=""
THRESHOLD="${WRAPUP_GRAPH_REFRESH_THRESHOLD:-5}"

usage() {
  cat <<'EOF'
should-refresh-graph.sh — gate on structural drift before invoking /graphify

Usage:
  should-refresh-graph.sh --repo <path> --since <ref-or-timestamp>
  should-refresh-graph.sh --help

Options:
  --repo <path>              Absolute path to the repo root. Required.
  --since <ref-or-timestamp> Anything `git log --since=` or `git diff` accepts:
                             a timestamp ("2026-04-01"), a relative time
                             ("7.days.ago"), a ref ("HEAD~10"), or a tag.
                             Required.
  --help                     Show this help and exit 0.

Environment:
  WRAPUP_GRAPH_REFRESH_THRESHOLD   Override the default file-count threshold.
                                   Default: 5.

Behavior:
  1. Runs `git diff --name-only <since>..HEAD` inside --repo.
  2. Filters out doc-only, test-only, and formatting-only paths
     (*.md, docs/**, tests/**, .github/**, *.lock, *.sum).
  3. Counts remaining structural files.
  4. Also flags a refresh when a new top-level directory appears in the diff.
  5. Exits 0 if count > THRESHOLD or a new top-level dir appeared.
     Exits 1 otherwise.

Output:
  One line summary on stdout, e.g.:
    refresh: 8 structural files changed since 2026-04-01 (threshold=5)
    skip:    2 structural files changed since HEAD~10 (threshold=5)

Exit codes:
  0  refresh needed
  1  skip refresh
  2  argument or git error

Examples:
  should-refresh-graph.sh --repo "$(pwd)" --since "HEAD~20" && /graphify
  should-refresh-graph.sh --repo "$(pwd)" --since "2026-04-01" \
    || echo "graph still fresh"
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --since)
      SINCE="${2:-}"
      shift 2
      ;;
    *)
      echo "should-refresh-graph.sh: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$REPO" || -z "$SINCE" ]]; then
  echo "should-refresh-graph.sh: --repo and --since are required" >&2
  exit 2
fi

if [[ ! -d "$REPO/.git" ]]; then
  echo "should-refresh-graph.sh: not a git repo: $REPO" >&2
  exit 2
fi

# --- compute diff --------------------------------------------------------
# Prefer a ref-based diff if --since looks like a ref; otherwise use --since=
CHANGED_FILES=""
if git -C "$REPO" rev-parse --verify "$SINCE" >/dev/null 2>&1; then
  CHANGED_FILES=$(git -C "$REPO" diff --name-only "$SINCE"..HEAD 2>/dev/null || true)
else
  # Timestamp / relative-time path — use log to list commits, diff their tree.
  OLDEST=$(git -C "$REPO" log --since="$SINCE" --reverse --format='%H' \
    | head -n 1 || true)
  if [[ -z "$OLDEST" ]]; then
    echo "skip: no commits since $SINCE"
    exit 1
  fi
  CHANGED_FILES=$(git -C "$REPO" diff --name-only "${OLDEST}^..HEAD" 2>/dev/null || true)
fi

# --- filter out non-structural paths -------------------------------------
STRUCTURAL=$(printf '%s\n' "$CHANGED_FILES" \
  | awk 'NF' \
  | grep -Ev '(^|/)docs?/' \
  | grep -Ev '(^|/)tests?/' \
  | grep -Ev '(^|/)\.github/' \
  | grep -Ev '\.(md|lock|sum|txt)$' \
  || true)

STRUCT_COUNT=$(printf '%s\n' "$STRUCTURAL" | awk 'NF' | wc -l | tr -d ' ')

# --- new top-level directory check --------------------------------------
PRIOR_TOPLEVEL=""
if git -C "$REPO" rev-parse --verify "$SINCE" >/dev/null 2>&1; then
  PRIOR_TOPLEVEL=$(git -C "$REPO" ls-tree --name-only "$SINCE" \
    | awk '{print $1}' | sort -u || true)
fi
CURRENT_TOPLEVEL=$(git -C "$REPO" ls-tree --name-only HEAD \
  | awk '{print $1}' | sort -u || true)

NEW_TOPLEVEL=""
if [[ -n "$PRIOR_TOPLEVEL" ]]; then
  NEW_TOPLEVEL=$(comm -13 <(printf '%s\n' "$PRIOR_TOPLEVEL") \
                         <(printf '%s\n' "$CURRENT_TOPLEVEL") || true)
fi

# --- decide --------------------------------------------------------------
if [[ -n "$NEW_TOPLEVEL" ]]; then
  echo "refresh: new top-level dir(s) since $SINCE: $(echo "$NEW_TOPLEVEL" | tr '\n' ' ')"
  exit 0
fi

if [[ "$STRUCT_COUNT" -gt "$THRESHOLD" ]]; then
  echo "refresh: $STRUCT_COUNT structural files changed since $SINCE (threshold=$THRESHOLD)"
  exit 0
fi

echo "skip: $STRUCT_COUNT structural files changed since $SINCE (threshold=$THRESHOLD)"
exit 1
