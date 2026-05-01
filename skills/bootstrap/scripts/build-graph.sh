#!/usr/bin/env bash
# build-graph.sh — wire code-review-graph into a repo and emit GRAPH_REPORT.md
#
# Replaces the former /graphify invocation. Builds a Tree-sitter-based graph
# stored in <repo>/.code-review-graph/ (SQLite), exposes 28 MCP tools to Claude
# Code via <repo>/.mcp.json, and writes a markdown overview to $GRAPHS_DIR for
# session-start @ reference loading.
#
# Usage:
#   build-graph.sh --repo <path> --graphs-dir <path>
#   build-graph.sh --help

set -euo pipefail

REPO=""
GRAPHS_DIR=""

usage() {
  cat <<'EOF'
build-graph.sh — build code-review-graph + emit GRAPH_REPORT.md

Usage:
  build-graph.sh --repo <path> --graphs-dir <path>
  build-graph.sh --help

Options:
  --repo         Absolute path to repo root. Required.
  --graphs-dir   Absolute path to graphs output dir (typically
                 ~/.claude/projects/<REPO_NAME>/graphs). Required.
  --help         Show this help and exit 0.

Outputs:
  <repo>/.code-review-graph/         SQLite graph DB (gitignored)
  <repo>/.mcp.json                   Claude Code MCP server config
  <repo>/.claude/settings.json       PostToolUse / SessionStart hooks
  <graphs-dir>/GRAPH_REPORT.md       markdown overview for session-start load
  <graphs-dir>/graph.html            optional interactive visualization

Exit codes:
  0  success
  1  argument error
  2  code-review-graph build failure
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --graphs-dir) GRAPHS_DIR="${2:-}"; shift 2 ;;
    *) echo "build-graph.sh: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -z "$REPO" ]] && { echo "build-graph.sh: --repo is required" >&2; exit 1; }
[[ -z "$GRAPHS_DIR" ]] && { echo "build-graph.sh: --graphs-dir is required" >&2; exit 1; }
[[ ! -d "$REPO" ]] && { echo "build-graph.sh: repo does not exist: $REPO" >&2; exit 1; }

if ! command -v code-review-graph >/dev/null 2>&1; then
  echo "build-graph.sh: code-review-graph not installed. Run: pipx install code-review-graph" >&2
  exit 2
fi

mkdir -p "$GRAPHS_DIR"
cd "$REPO"

# Phase A: install per-repo MCP config + hooks (idempotent)
code-review-graph install --platform claude-code

# Phase B: build/update the graph
code-review-graph build

# Phase C: generate wiki (community markdown)
code-review-graph wiki --force >/dev/null 2>&1 || true
WIKI_INDEX="$REPO/.code-review-graph/wiki/index.md"

# Phase D: compose GRAPH_REPORT.md
REPORT="$GRAPHS_DIR/GRAPH_REPORT.md"
{
  echo "# Graph Report — $(basename "$REPO")"
  echo ""
  echo "_Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) by code-review-graph_"
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
    echo "_Wiki not generated. Run \`code-review-graph wiki --force\` inside the repo to populate._"
  fi
} > "$REPORT"

# Phase E: optional HTML visualization
code-review-graph visualize --format html >/dev/null 2>&1 || true
VIZ_HTML="$REPO/.code-review-graph/visualize/graph.html"
[[ ! -f "$VIZ_HTML" ]] && VIZ_HTML="$REPO/.code-review-graph/graph.html"
if [[ -f "$VIZ_HTML" ]]; then
  cp "$VIZ_HTML" "$GRAPHS_DIR/graph.html"
fi

echo "✓ Graph DB:        $REPO/.code-review-graph/"
echo "✓ MCP config:      $REPO/.mcp.json"
echo "✓ GRAPH_REPORT.md: $REPORT"
[[ -f "$GRAPHS_DIR/graph.html" ]] && echo "✓ graph.html:      $GRAPHS_DIR/graph.html"
