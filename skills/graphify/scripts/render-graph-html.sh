#!/usr/bin/env bash
# render-graph-html.sh — render an interactive HTML visualization from graph.json
#
# Contract: reads a graph.json that conforms to references/graph-schema.md
# (schema_version 1.0) and writes a self-contained HTML file to --output.
# The HTML uses D3.js via CDN and renders a force-directed graph:
#   - nodes colored by language
#   - hotspots (high in_degree) sized larger
#   - edges are import relationships
#   - hover shows file path + LOC + import counts
#
# Usage:
#   render-graph-html.sh --input <path> [--output <path>]
#   render-graph-html.sh --help

set -euo pipefail

INPUT=""
OUTPUT=""

usage() {
  cat <<'EOF'
render-graph-html.sh — render graph.html from graph.json

Usage:
  render-graph-html.sh --input <path> [--output <path>]
  render-graph-html.sh --help

Options:
  --input  <path>  Path to graph.json (must conform to schema_version 1.0). Required.
  --output <path>  Path to write graph.html. Default: ./graph.html
  --help           Show this help and exit 0.

Output:
  Self-contained HTML page with embedded D3.js force-directed graph rendering.
  Open in any modern browser; no local server needed.

Exit codes:
  0  success
  1  argument error
  2  input JSON missing or fails schema check
  3  render failure

Examples:
  render-graph-html.sh \
    --input  ~/.claude/projects/myrepo/graphs/graph.json \
    --output ~/.claude/projects/myrepo/graphs/graph.html
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --input)
      INPUT="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT="${2:-}"
      shift 2
      ;;
    *)
      echo "render-graph-html.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$INPUT" ]]; then
  echo "render-graph-html.sh: --input is required" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "render-graph-html.sh: --input file does not exist: $INPUT" >&2
  exit 2
fi

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$(pwd)/graph.html"
fi

mkdir -p "$(dirname "$OUTPUT")"

# --- dependency check ----------------------------------------------------
if ! command -v jq >/dev/null 2>&1; then
  echo "render-graph-html.sh: jq is required but not installed" >&2
  exit 3
fi

# --- validate input schema ----------------------------------------------
if ! jq -e '.schema_version and .repo.name and (.nodes | type == "array") and (.edges | type == "array")' "$INPUT" >/dev/null; then
  echo "render-graph-html.sh: input failed schema check — regenerate with scan-repo.sh" >&2
  exit 2
fi

SCHEMA_VERSION=$(jq -r '.schema_version' "$INPUT")
MAJOR="${SCHEMA_VERSION%%.*}"
if [[ "$MAJOR" != "1" ]]; then
  echo "render-graph-html.sh: unsupported schema_version '$SCHEMA_VERSION' (this renderer expects 1.x)" >&2
  exit 2
fi

REPO_NAME=$(jq -r '.repo.name' "$INPUT")
NODE_COUNT=$(jq '.nodes | length' "$INPUT")
EDGE_COUNT=$(jq '.edges | length' "$INPUT")

# --- render --------------------------------------------------------------
# TODO(graphify): replace inline template with a richer D3 visualization.
#
# Minimum viable implementation:
#   1. Read the full graph.json, embed as a JSON blob in the HTML.
#   2. Use D3.js v7 force-directed graph (via CDN).
#   3. Color-code nodes by `language` field.
#   4. Scale node radius by `in_degree` (hotspots render larger).
#   5. Render edges as lines; source→target from the edges array.
#   6. Tooltip on hover: path, language, LOC, in_degree, out_degree.
#   7. Click a node → highlight its neighbors; click empty space to clear.
#   8. Legend in the corner mapping colors to languages.
#
# For now, emit a valid HTML scaffold that embeds the graph data and
# renders a minimal node list. Callers can enhance later without
# changing the script interface.

# Read the JSON blob safely — pipe through jq to compact it.
GRAPH_JSON_COMPACT=$(jq -c '.' "$INPUT")

cat > "$OUTPUT" <<HTML_EOF
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${REPO_NAME} — Knowledge Graph</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body { font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 1.5rem; color: #222; }
  h1 { margin: 0 0 0.25rem 0; font-size: 1.25rem; }
  .meta { color: #666; font-size: 0.875rem; margin-bottom: 1rem; }
  #graph { width: 100%; height: 70vh; border: 1px solid #ddd; border-radius: 6px; background: #fafafa; }
  .fallback { padding: 1rem; background: #f4f4f4; border-radius: 4px; font-family: ui-monospace, monospace; font-size: 0.8rem; overflow: auto; max-height: 40vh; }
</style>
</head>
<body>
  <h1>${REPO_NAME} — Knowledge Graph</h1>
  <div class="meta">schema_version ${SCHEMA_VERSION} · ${NODE_COUNT} nodes · ${EDGE_COUNT} edges</div>
  <div id="graph"></div>
  <details>
    <summary>Raw graph.json (fallback)</summary>
    <pre class="fallback" id="raw"></pre>
  </details>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
  // Graph data embedded at render time.
  const GRAPH = ${GRAPH_JSON_COMPACT};

  // Populate the fallback view so users always see the data.
  document.getElementById('raw').textContent = JSON.stringify(GRAPH, null, 2);

  // TODO: replace this minimal renderer with a full D3 force-directed graph.
  const container = document.getElementById('graph');
  const svg = d3.select(container).append('svg')
    .attr('width', '100%')
    .attr('height', '100%');

  const width = container.clientWidth;
  const height = container.clientHeight;

  const nodes = (GRAPH.nodes || []).map(n => Object.assign({}, n));
  const links = (GRAPH.edges || []).map(e => ({ source: e.source, target: e.target }));

  if (nodes.length === 0) {
    svg.append('text')
      .attr('x', width / 2).attr('y', height / 2)
      .attr('text-anchor', 'middle').attr('fill', '#999')
      .text('No nodes — regenerate with scan-repo.sh');
  } else {
    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(40))
      .force('charge', d3.forceManyBody().strength(-80))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g').attr('stroke', '#bbb').selectAll('line')
      .data(links).enter().append('line').attr('stroke-width', 1);

    const node = svg.append('g').selectAll('circle')
      .data(nodes).enter().append('circle')
      .attr('r', d => 3 + Math.sqrt(d.in_degree || 0))
      .attr('fill', '#4f7fbf');

    node.append('title').text(d => d.path + ' (' + d.language + ', LOC ' + d.loc + ')');

    sim.on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('cx', d => d.x).attr('cy', d => d.y);
    });
  }
</script>
</body>
</html>
HTML_EOF

echo "render-graph-html.sh: wrote $OUTPUT (nodes=$NODE_COUNT, edges=$EDGE_COUNT)"
