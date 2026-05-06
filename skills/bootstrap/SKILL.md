---
name: bootstrap
description: Performs first-visit repo setup — detects stack, seeds memory artifacts at ~/.claude/projects/<REPO_NAME>/, builds a code-review-graph (Tree-sitter + 28 MCP tools) with per-repo .mcp.json, and writes <repo>/.claude/CLAUDE.md with @ references. Fires only on explicit /bootstrap. Runs once per repo; re-runs are safe but preserve existing memory. Opus-routed because judgment on stack classification and conventions benefits from stronger reasoning.
when_to_use: Invoke explicitly with /bootstrap on first visit to a new repo, or after a structural rewrite that invalidates architecture.md. Never invoke on incidental prompts.
allowed-tools: Read Grep Bash Write
disable-model-invocation: false
model: opus
effort: high
---

# Bootstrap — First Visit Setup

Turns Claude into a repo on-boarder: detects the tech stack, seeds five memory files, generates a knowledge graph, and wires project-local `@` references so every future session auto-loads full context.

**Freedom level: Low** — the memory layout and CLAUDE.md `@` contract feed `wrap-up` and every future session, so the sequence and output shape are not negotiable. Claude follows the workflow exactly; judgment is limited to stack classification and writing the architecture narrative.

**Graph backend**: bootstrap builds a [code-review-graph](https://github.com/tirth8205/code-review-graph) per repo — Tree-sitter AST + SQLite + 28 MCP tools. Replaces the former grep-based graphify skill. The graph's live MCP tools are Claude's primary code-navigation mechanism in future sessions; `GRAPH_REPORT.md` is the cheap session-start overview.

## 1. Detect Stack First

**Classify languages and frameworks before touching memory — the result drives every later step.**

- Run `scripts/detect-stack.sh --repo "$REPO_ROOT"` and parse the JSON; do not re-implement detection inline.
- Never guess from a single file (`package.json` alone does not make a Node service — check for TypeScript, framework deps).
- Data Engineering classification: Python + any of `airflow`, `pyspark`, `dbt`, `kafka`, `snowflake`, `bigquery`, `redshift` from the detector's `frameworks` array.
- Print `{languages, frameworks, primary}` to the user and confirm before proceeding if ambiguous.

## 2. Seed Memory Before Work

**All five skeleton files exist before the graph build runs.**

- Run `scripts/seed-memory.sh --repo-name "$REPO_NAME" --memory-dir "$MEMORY_DIR"`; it creates the directory and the 5 files idempotently.
- Re-runs preserve prior `architecture.md` / `todo.md` / `lessons.md` / `history.md`; only `MEMORY.md` is rewritten.
- Populate `architecture.md` from `$GRAPHS_DIR/GRAPH_REPORT.md` after `scripts/build-graph.sh` completes — do not write stack guesses before the graph exists.
- Seed content templates in `references/memory-templates.md`; read it before hand-editing any memory file.

## 3. Link Project To Global

**The per-repo `.claude/CLAUDE.md` contains only `@` references to user-global memory — never duplicated content.**

- Run `scripts/write-project-claude.sh --repo "$REPO_ROOT" --memory-dir "$MEMORY_DIR"`; it emits the 5 `@` lines and ensures `.claude/` is in `.gitignore`.
- `history.md` is intentionally **excluded** from `@` refs — it grows unboundedly and isn't useful on every session.
- The file contains `~/` paths, which leak home-directory layout — it must never be committed.
- "Paste architecture table inline in CLAUDE.md" → "`@~/.claude/projects/$REPO_NAME/memory/architecture.md`".

## 4. Run Once Per Repo

**Bootstrap is a seeder, not a maintainer. After the first run, `/wrap-up` owns ongoing updates.**

- If `$MEMORY_DIR/MEMORY.md` already exists: warn, show the last-modified date, and require user confirmation before any overwrite.
- If `$REPO_ROOT/.code-review-graph/` exists: skip the build step unless the user opts into a rebuild (CRG auto-updates incrementally via hooks).
- For structural rewrites (large refactor, language swap), re-run bootstrap with explicit consent; `/wrap-up` refreshes less invasively for incremental drift.

## Quick reference

The single lookup consulted on every invocation — which memory file to touch for which need.

| Memory file | When Claude writes it | Loaded on session start? |
|---|---|---|
| `MEMORY.md` | Bootstrap only — pure index | yes |
| `architecture.md` | Bootstrap (from graph) + wrap-up on structural change | yes |
| `todo.md` | Bootstrap seeds; wrap-up appends | yes |
| `lessons.md` | Bootstrap seeds; wrap-up appends corrections | yes |
| `history.md` | Bootstrap seeds; wrap-up prepends every session | **no** (append-only) |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] **Phase 1 — Resolve paths**: `REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)`, `REPO_NAME=$(basename "$REPO_ROOT")`, `MEMORY_DIR=$HOME/.claude/projects/$REPO_NAME/memory`, `GRAPHS_DIR=$HOME/.claude/projects/$REPO_NAME/graphs`.
- [ ] **Phase 1 — Detect stack**: run `scripts/detect-stack.sh --repo "$REPO_ROOT"`; capture `primary`, `languages`, `frameworks`. Confirm classification with the user if `primary` is `unknown`.
- [ ] **Phase 2 — Seed memory**: run `scripts/seed-memory.sh --repo-name "$REPO_NAME" --memory-dir "$MEMORY_DIR"`.
- [ ] **Phase 3 — Write project CLAUDE.md**: run `scripts/write-project-claude.sh --repo "$REPO_ROOT" --memory-dir "$MEMORY_DIR"`. Fill in the Stack, Entry Points, Conventions, and Skills sections using detector output; pick 5–8 relevant skills.
- [ ] **Phase 4 — Build graph**: run `scripts/build-graph.sh --repo "$REPO_ROOT" --graphs-dir "$GRAPHS_DIR"`. Skip if `$REPO_ROOT/.code-review-graph/` exists unless user opted into rebuild. Produces `<repo>/.code-review-graph/` (SQLite), `<repo>/.mcp.json` (MCP config), `$GRAPHS_DIR/GRAPH_REPORT.md`, and optional `$GRAPHS_DIR/graph.html`.
- [ ] **Phase 5 — Link**: populate `architecture.md` narrative from `GRAPH_REPORT.md` (stack from detector, entry points, communities, hub nodes). Append first entry to `history.md` with stack summary.
- [ ] Print summary: repo name, stack, memory dir, graph dir, project CLAUDE.md path.

## Feedback loop

1. After `seed-memory.sh` runs, verify the 5 files exist and the index lists all 5 links.
2. **Validate immediately**: `ls "$MEMORY_DIR" | wc -l` is `5` and `grep -c '^- \[' "$MEMORY_DIR/MEMORY.md"` is `5`.
3. After `write-project-claude.sh` runs, verify `grep -c '^@~/.claude/projects' "$REPO_ROOT/.claude/CLAUDE.md"` is `5`.
4. If any count is off: delete the file, re-run the script. Never hand-edit to match — schema mismatch means a script bug or wrong argument, and silent edits leave the next session reading a broken layout.
5. Confirm `.claude/` is in `$REPO_ROOT/.gitignore`. If not, `write-project-claude.sh` will add it — rerun.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Writing `architecture.md` before the graph built | Seed skeletons first, run `build-graph.sh`, then populate the narrative from `GRAPH_REPORT.md` |
| Duplicating architecture content inside `.claude/CLAUDE.md` | Use `@` references only — content lives in `~/.claude/projects/<REPO_NAME>/memory/` |
| Including `history.md` in the CLAUDE.md `@` refs | Exclude it — the file grows unboundedly and bloats every session start |
| Running bootstrap twice without checking | Detect existing `MEMORY.md`; require explicit user confirmation to overwrite |
| Committing `<repo>/.claude/CLAUDE.md` | Ensure `.claude/` is in `.gitignore`; the file contains `~/` paths that must not leak |
| Inlining 50+ lines of detection bash in SKILL.md | Extract to `scripts/detect-stack.sh`; SKILL.md invokes, never re-implements |
| Writing the literal string `<REPO_NAME>` into memory files | Substitute the actual repo name — scripts handle this with `--repo-name` arg |

## References

- `references/memory-templates.md` — skeletons and example content for all 5 memory files, plus wrap-up's mutation rules. Read before hand-editing any memory file.
- `scripts/detect-stack.sh` — `--repo <path>`; emits JSON `{"languages":[], "frameworks":[], "primary":"..."}`.
- `scripts/seed-memory.sh` — `--repo-name <name> --memory-dir <path>`; creates all 5 skeleton files idempotently.
- `scripts/write-project-claude.sh` — `--repo <path> --memory-dir <path>`; emits `<repo>/.claude/CLAUDE.md` with 5 `@` refs and updates `.gitignore`.
- `scripts/build-graph.sh` — `--repo <path> --graphs-dir <path>`; wires code-review-graph (MCP config + hooks), builds the graph, emits `GRAPH_REPORT.md` and optional `graph.html`. Requires `code-review-graph` CLI (`pipx install code-review-graph`).

## Cross-references

- `code-review-graph` — installed as a pipx package; its 28 MCP tools become Claude's primary code-navigation mechanism once bootstrap wires it in. `.mcp.json` in each repo activates the tools per-session.
- `/wrap-up` — owns ongoing mutation of `todo.md`, `lessons.md`, `history.md`, and refreshes `GRAPH_REPORT.md` via `code-review-graph update` + `wiki`. Run at the end of every session.
