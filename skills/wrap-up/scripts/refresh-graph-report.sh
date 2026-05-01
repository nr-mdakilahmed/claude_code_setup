#!/usr/bin/env bash
# refresh-graph-report.sh — incrementally update the code-review-graph and
# regenerate GRAPH_REPORT.md for session-start @ reference loading.
#
# Called from wrap-up Phase 4. Assumes /bootstrap already ran and
# $REPO_ROOT/.code-review-graph/ exists.
#
# Usage:
#   refresh-graph-report.sh --repo <path> --graphs-dir <path>
#   refresh-graph-report.sh --help

set -euo pipefail

REPO=""
GRAPHS_DIR=""

usage() {
  cat <<'EOF'
refresh-graph-report.sh — update code-review-graph + regenerate GRAPH_REPORT.md

Usage:
  refresh-graph-report.sh --repo <path> --graphs-dir <path>
  refresh-graph-report.sh --help

Options:
  --repo         Absolute path to repo root. Required.
  --graphs-dir   Absolute path to graphs output dir (typically
                 ~/.claude/projects/<REPO_NAME>/graphs). Required.
  --help         Show this help and exit 0.

Behavior:
  Runs `code-review-graph update` (incremental via SHA-256 diff, <2s) then
  regenerates `$GRAPHS_DIR/GRAPH_REPORT.md` with fresh stats + wiki content.
  Skips (exit 3) if <repo>/.code-review-graph/ is missing — run /bootstrap.

Exit codes:
  0  success
  1  argument error
  2  code-review-graph update failure
  3  graph DB missing (bootstrap not run)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --graphs-dir) GRAPHS_DIR="${2:-}"; shift 2 ;;
    *) echo "refresh-graph-report.sh: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -z "$REPO" ]] && { echo "refresh-graph-report.sh: --repo is required" >&2; exit 1; }
[[ -z "$GRAPHS_DIR" ]] && { echo "refresh-graph-report.sh: --graphs-dir is required" >&2; exit 1; }
[[ ! -d "$REPO" ]] && { echo "refresh-graph-report.sh: repo does not exist: $REPO" >&2; exit 1; }

if ! command -v code-review-graph >/dev/null 2>&1; then
  echo "refresh-graph-report.sh: code-review-graph not installed" >&2
  exit 2
fi

if [[ ! -d "$REPO/.code-review-graph" ]]; then
  echo "refresh-graph-report.sh: graph DB missing at $REPO/.code-review-graph — run /bootstrap first" >&2
  exit 3
fi

mkdir -p "$GRAPHS_DIR"
cd "$REPO"

# Incremental update (SHA-256 diff, typically <2s)
code-review-graph update

# Regenerate wiki (community markdown)
code-review-graph wiki --force >/dev/null 2>&1 || true
WIKI_INDEX="$REPO/.code-review-graph/wiki/index.md"

# Compose fresh GRAPH_REPORT.md
REPORT="$GRAPHS_DIR/GRAPH_REPORT.md"
{
  echo "# Graph Report — $(basename "$REPO")"
  echo ""
  echo "_Refreshed: $(date -u +%Y-%m-%dT%H:%M:%SZ) by code-review-graph update_"
  echo ""
  echo "## Graph Stats"
  echo ""
  echo '```'
  code-review-graph status 2>&1 || echo "(status unavailable)"
  echo '```'
  echo ""
  echo "## How Claude Should Use This Graph"
  echo ""
  echo "This repo exposes a code-review-graph via MCP. **Prefer graph tools over raw Grep/Glob:**"
  echo ""
  echo "| Need | MCP Tool |"
  echo "|---|---|"
  echo "| Find functions/classes by name | \`semantic_search_nodes\` |"
  echo "| Callers / callees / imports / tests | \`query_graph\` |"
  echo "| Blast radius of a change | \`get_impact_radius\` |"
  echo "| Compact PR review context | \`get_review_context\` |"
  echo "| Risk-scored change analysis | \`detect_changes\` |"
  echo "| Community / architecture overview | \`get_architecture_overview\` |"
  echo "| Hub / bridge nodes | \`get_hub_nodes\`, \`get_bridge_nodes\` |"
  echo ""
  echo "Fall back to Grep/Glob/Read **only** when the graph does not cover the query."
  echo ""
  echo "## Communities & Architecture"
  echo ""
  if [[ -f "$WIKI_INDEX" ]]; then
    cat "$WIKI_INDEX"
  else
    echo "_Wiki not generated. Run \`code-review-graph wiki --force\` inside the repo._"
  fi
} > "$REPORT"

echo "✓ Graph updated:   $REPO/.code-review-graph/"
echo "✓ GRAPH_REPORT.md: $REPORT"
