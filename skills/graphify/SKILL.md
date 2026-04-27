---
name: graphify
description: >
  Scan codebase to generate a knowledge graph (graph.json, GRAPH_REPORT.md, graph.html).
  25x token reduction: replaces reading hundreds of source files with one report.
  Use opus model. Invoke with /graphify.
---

# /graphify — Knowledge Graph Generator

**Use opus model.** Scans the full codebase and generates a structured knowledge graph.
25x token reduction: replaces reading hundreds of source files with a single GRAPH_REPORT.md.

## Setup Variables

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPO_NAME=$(basename "$REPO_ROOT")
GRAPHS_DIR="$HOME/.claude/projects/$REPO_NAME/graphs"
mkdir -p "$GRAPHS_DIR"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
```

## Phase 1 — Discovery

Scan the repo (exclude: `node_modules`, `.git`, `build`, `dist`, `__pycache__`, `.venv`, `vendor`, `target`).

Detect: Languages (extensions + shebangs), Frameworks (package.json, pyproject.toml, etc.), Entry points (main.*, app.*, server.*), Config files, Test directories.

## Phase 2 — Dependency Analysis

For each source file (sample representative files per language):
- Parse import/require/use statements
- Identify internal vs external dependencies
- Find hotspots (most-imported files)
- Detect circular dependency candidates

## Phase 3 — Generate graph.json

Write `$GRAPHS_DIR/graph.json` with: repo metadata, stats, entry_points, nodes (files with type/language/import counts), edges (import relationships), external_deps, hotspots.

## Phase 4 — Generate GRAPH_REPORT.md

Write `$GRAPHS_DIR/GRAPH_REPORT.md` covering:
- Overview (languages, architecture, file counts, LOC)
- Tech Stack table
- Entry Points table
- Key Modules with responsibilities
- Dependency Hotspots (top 10 most-imported)
- Data Flow narrative
- Critical Paths
- Test Coverage Estimate
- External Dependencies
- Conventions Observed (naming, organization, error handling, config)
- Potential Issues (circular deps, orphaned files, large files)

## Phase 5 — Generate graph.html

Write `$GRAPHS_DIR/graph.html` — interactive D3.js force-directed graph:
- Nodes = files colored by language, hotspots = larger circles
- Edges = import relationships
- Hover tooltips, click to highlight, legend

## Completion

```
Graph generated for <REPO_NAME>
   Nodes:   N files
   Edges:   N dependencies
   Report:  ~/.claude/projects/<REPO_NAME>/graphs/GRAPH_REPORT.md
   Visual:  ~/.claude/projects/<REPO_NAME>/graphs/graph.html
```
