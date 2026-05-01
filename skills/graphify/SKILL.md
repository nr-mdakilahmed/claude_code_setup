---
name: graphify
description: Generates a codebase knowledge graph as graph.json plus a Markdown GRAPH_REPORT.md and optional interactive graph.html, giving Claude a compressed map of the repo that replaces reading hundreds of source files on later turns. Writes outputs to ~/.claude/projects/<REPO_NAME>/graphs/. Fires only on explicit /graphify. Bootstrap invokes this as a sub-step; wrap-up refreshes it when structure drifts materially.
when_to_use: Invoke explicitly with /graphify on first visit to a repo, after a large refactor, or when memory artifacts are stale. Never invoke on incidental prompts.
allowed-tools: Read Grep Bash Write
disable-model-invocation: true
model: opus
---

# Graphify — Codebase Knowledge Graph

Turns Claude into a map-maker: emits a structured graph of files, imports, hotspots, and entry points so future sessions navigate by summary instead of re-reading source.

**Freedom level: Low** — outputs feed `bootstrap` and `wrap-up`, so the schema and file paths are contractual. Claude follows the workflow exactly; judgment is limited to grouping nodes and writing the Markdown narrative.

## 1. Scan Without Reading

**Traverse the repo with `find` and `grep`; never `Read` files in bulk.**

- Enumerate files with `find -type f` and exclusion globs (`node_modules`, `.git`, `dist`, `build`, `__pycache__`, `.venv`, `vendor`, `target`).
- Collect imports with `grep -E '^(import|from|require|use|include) '`; do not open each file.
- Sample one file per language only if a parse ambiguity blocks the graph.
- "Read every `.py` to find imports" → "`grep -rE '^(from|import) ' --include='*.py' $REPO_ROOT`".

## 2. JSON Before Report

**Write `graph.json` first; all downstream artifacts derive from it.**

- Populate the schema in `references/graph-schema.md` completely — do not emit partial nodes.
- Validate with `jq -e` before writing the Markdown report.
- The Markdown report and HTML are views over the JSON; never re-derive them from raw files.
- `bootstrap` and `wrap-up` depend on this schema — breaking it breaks them.

## 3. HTML Is Optional

**Skip `graph.html` unless the user asks, or node count exceeds 30 and the user will browse it.**

- HTML adds cost but no information — the JSON and Markdown are load-bearing.
- Render via `scripts/render-graph-html.sh` so the template stays consistent.
- Never inline D3/vis.js into the Markdown report — HTML is a separate file.

## 4. Refresh On Structural Change

**Regenerate only when the graph would materially differ. Treat it as a cached artifact, not a log.**

- Trigger refresh: >5 source files added/removed/renamed, new top-level directory, new entry point, new language.
- Skip refresh: typo fixes, doc edits, test-only changes, formatting-only diffs.
- `wrap-up` calls this heuristic; graphify itself runs on explicit invocation only.

## Quick reference

| User goal | Artifact | How |
|---|---|---|
| Seed a fresh repo for bootstrap | `graph.json` + `GRAPH_REPORT.md` | `scripts/scan-repo.sh --repo "$REPO_ROOT" --output "$GRAPHS_DIR/graph.json"` then render the report |
| Show the team a visual map | `graph.html` | `scripts/render-graph-html.sh --input "$GRAPHS_DIR/graph.json" --output "$GRAPHS_DIR/graph.html"` |
| Refresh after large refactor | all three | Re-run both scripts; overwrite existing files |
| Quick sanity check on structure | `graph.json` only | Scan script; skip report + HTML |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] Resolve `REPO_ROOT`, `REPO_NAME`, `GRAPHS_DIR=$HOME/.claude/projects/$REPO_NAME/graphs`; `mkdir -p "$GRAPHS_DIR"`.
- [ ] Run `scripts/scan-repo.sh --repo "$REPO_ROOT" --output "$GRAPHS_DIR/graph.json"`.
- [ ] Validate JSON: `jq '.schema_version, (.nodes | length), (.edges | length)' "$GRAPHS_DIR/graph.json"`.
- [ ] Write `$GRAPHS_DIR/GRAPH_REPORT.md` using `references/report-template.md` (Overview → Tech Stack → Entry Points → Key Modules → Hotspots → Data Flow → Critical Paths → Test Coverage → External Deps → Conventions → Potential Issues).
- [ ] If the user asked for HTML or node count >30: run `scripts/render-graph-html.sh --input "$GRAPHS_DIR/graph.json" --output "$GRAPHS_DIR/graph.html"`.
- [ ] Print summary: repo name, node count, edge count, paths to all artifacts.

## Feedback loop

1. Emit `graph.json`.
2. **Validate immediately**: `jq -e '.schema_version and .repo.name and (.nodes | type == "array") and (.edges | type == "array")' "$GRAPHS_DIR/graph.json"`.
3. If validation fails: fix scanner output → re-emit → revalidate. Do not render the Markdown report on invalid JSON.
4. After writing the report, re-open it and confirm section count matches `references/report-template.md`. If sections are missing, extend and rewrite — do not ship partial.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Re-running graphify on every trivial commit | Refresh only on structural change (principle 4) |
| `Read`-ing full source files to discover imports | `grep -E "^(import\|from\|require)"` on the file list |
| Writing `GRAPH_REPORT.md` before `graph.json` is valid | JSON first, validate, then render |
| Nesting outputs under `$REPO_ROOT/.claude/graphs/` | Write to `~/.claude/projects/$REPO_NAME/graphs/` (user-global, never committed) |
| Inlining D3 JS into the Markdown report | HTML is a separate `graph.html`; keep the report text-only |
| Emitting partial nodes (missing `language` or `path`) | Schema is contract — fill every required field |
| Firing on casual prompts | `disable-model-invocation: true` blocks auto-invoke; only `/graphify` fires |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `jq: error: Cannot iterate over null` | Scanner emitted no nodes — check exclusion globs; repo root may be wrong |
| HTML renders empty | `graph.json` edges array is empty; re-run scan with language filters widened |
| Report missing "Hotspots" section | `nodes[].in_degree` not populated; recompute in scanner and re-render |
| Bootstrap can't find `GRAPH_REPORT.md` | Wrong `GRAPHS_DIR` — must be `~/.claude/projects/$REPO_NAME/graphs/`, not repo-local |
| `schema_version` mismatch | Consumer expects 1.x — re-run `scripts/scan-repo.sh` |

## References

- `references/graph-schema.md` — full JSON schema for `graph.json` (nodes, edges, repo, stats, hotspots) with TOC and examples. Read before writing the scanner or changing emit format.
- `references/report-template.md` — canonical section layout for `GRAPH_REPORT.md` with example prose. Read before composing the Markdown narrative.
- `scripts/scan-repo.sh` — one-liner scanner: `scripts/scan-repo.sh --repo <path> --output <path>`. Emits schema-conformant `graph.json`.
- `scripts/render-graph-html.sh` — one-liner renderer: `scripts/render-graph-html.sh --input <json> --output <html>`. Produces interactive force-directed visualization.

## Cross-references

- `/bootstrap` — invokes `/graphify` as a sub-step during first-visit setup; depends on `graph.json` schema and `GRAPH_REPORT.md` section names.
- `/wrap-up` — runs the refresh heuristic; calls `/graphify` only when the structural-change threshold is met.
