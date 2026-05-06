---
name: wrap-up
description: Persists session context at end of work by appending to history.md, updating todo.md and lessons.md, and refreshing the code-review-graph (incremental update + regenerated GRAPH_REPORT.md). Fires only on explicit /wrap-up invocation.
when_to_use: Invoke explicitly with /wrap-up at the end of every session. Never runs implicitly — the user alone starts it.
allowed-tools: Read Grep Bash Write Edit
disable-model-invocation: false
---

# Wrap-Up — Session Persistence

Turns Claude into a session steward: captures corrections, writes durable notes to the four memory files seeded by `/bootstrap`, and refreshes the knowledge graph only when the repo has materially drifted.

**Freedom level: Low** — memory file paths and formats are contractual with `/bootstrap` and the code-review-graph schema. Claude follows the workflow exactly; judgment is limited to summary prose and lesson wording.

## 1. Audit Corrections First

**Scan the session for user corrections before touching any file.**

- Look for "no", "don't", "wrong", "that's not right", "use X instead", and any approach Claude abandoned mid-task.
- Each correction becomes one imperative rule in `lessons.md` with a **Why** clause — a rule without a reason gets ignored next session.
- "User said 'stop using `rm -rf`'" → "**Never chain `rm -rf` in automation** — it wiped the user's uncommitted work in session 2026-03-11."
- See `references/correction-patterns.md` for detection heuristics and the exact entry format.

## 2. Persist What Decays

**Route each artifact to the one file where it belongs; duplicate nothing.**

- Narrative of what happened → `history.md` (append-only, one entry per session).
- Tasks moved Active → Done; new follow-ups to Backlog → `todo.md`.
- New imperative rules, anti-patterns, wins → `lessons.md`.
- Structural changes (new module, renamed entry point, new language) → trigger a graph refresh, which rewrites `architecture.md`.
- Never write the same finding to two files.

## 3. Refresh Graph Incrementally

**Always run `code-review-graph update` — it's <2s incremental; no threshold check needed.**

- The graph lives in `$REPO_ROOT/.code-review-graph/` (SQLite); `update` re-parses only changed files via SHA-256 diff.
- After update, regenerate `GRAPH_REPORT.md` via `scripts/refresh-graph-report.sh --repo "$REPO_ROOT" --graphs-dir "$GRAPHS_DIR"`.
- If `architecture.md` sections reference entities that no longer exist, re-extract the narrative from the refreshed `GRAPH_REPORT.md`.
- If the graph DB is missing (`.code-review-graph/` absent), print "graph missing — run /bootstrap" and skip this phase.

## 4. Close The Loop

**Print a verifiable summary; never claim "done" without counts.**

- Report appended history entry, counts in `todo.md` (active/backlog/done), counts in `lessons.md` (patterns/wins), graph state (refreshed/skipped with file-change count).
- If any phase wrote nothing, say so explicitly ("No new corrections this session.") — silence reads as skipped work.

## Quick reference

| Finding type | Goes to | Format |
|---|---|---|
| Session narrative (what, decisions, next) | `history.md` | New `## <SESSION_DATE>` block appended; never edit prior entries |
| Task status change or new follow-up | `todo.md` | Move between `## Active` / `## Backlog` / `## Done`; add completion date |
| Correction, anti-pattern, or win | `lessons.md` | Imperative bullet under `## Patterns` / `## Anti-patterns` / `## Wins` with **Why** |
| Architectural / structural shift | `architecture.md` (re-extracted from refreshed `GRAPH_REPORT.md`) | Never hand-edit |
| Any code change | Refresh graph | `code-review-graph update` (incremental, <2s) + regenerate `GRAPH_REPORT.md` |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] Resolve `REPO_ROOT`, `REPO_NAME`, `MEMORY_DIR=$HOME/.claude/projects/$REPO_NAME/memory`, `GRAPHS_DIR=$HOME/.claude/projects/$REPO_NAME/graphs`, `SESSION_DATE=$(date '+%Y-%m-%d %H:%M')`.
- [ ] If `$MEMORY_DIR` does not exist: print "No memory found — run /bootstrap first." and stop.
- [ ] **Phase 0 — Corrections audit**: scan transcript using heuristics in `references/correction-patterns.md`; for each finding, append an imperative rule + Why to `$MEMORY_DIR/lessons.md`. If none, write "No new corrections this session." to the phase log.
- [ ] **Phase 1 — History**: run `scripts/append-history.sh --memory-dir "$MEMORY_DIR" --session-id "$SESSION_DATE"` with a prepared summary (Accomplished / Decisions / Blockers / Next).
- [ ] **Phase 2 — Todo**: edit `$MEMORY_DIR/todo.md` — move completed items from `## Active` to `## Done` with completion date; append new tasks from "Next" to `## Backlog`.
- [ ] **Phase 3 — Lessons**: dedupe and finalize `$MEMORY_DIR/lessons.md` — promote Phase 0 rules; if a pattern has appeared 2+ times across `history.md`, escalate it to `.claude/CLAUDE.md` under `## Key Conventions`.
- [ ] **Phase 3.5 — Golden save-worthiness check** (opt-in, not auto-save):
      Inspect the current session's transcript for **all three** signals:
        1. **Explicit success confirmation** by the user — phrases like "this worked", "ship it", "tests pass", "fixed", "perfect", "prod is green", "done", or user accepted a change without pushback after testing.
        2. **Non-trivial multi-step work** — ≥5 distinct tool uses on one coherent problem (not 5 typo fixes; 5 steps of one investigation).
        3. **Specific problem signature resolved** — a concrete error message, failing test, or regression that the session traced to root cause and fixed (not exploration, not refactoring for clarity).
      If all 3 present: propose a save. Surface to the user:
        > "This session looks golden-worthy.
        >   Proposed slug: `<kebab-case-slug>`
        >   Proposed tags: `tag1, tag2, tag3`
        >   Success criteria: `<one-sentence measurable outcome>`
        > Save? [y/n/edit]"
      On `y`: distill the session body per `~/.claude-kit/skills/golden/references/golden-schema.md` (Symptom → Root Cause → Steps That Worked → What NOT To Do → Files Touched) and run `~/.claude-kit/skills/golden/scripts/golden-save.sh --pattern <slug> --scope <scope> --tags <csv> --triggers <pipe> --success "<criteria>"` with the distilled body on stdin.
      On `n`: skip silently.
      On `edit`: let user correct slug/tags/scope before save.
      If any signal missing: skip this phase silently — do not prompt for fixes that aren't save-worthy.
- [ ] **Phase 4 — Graph refresh**: run `scripts/refresh-graph-report.sh --repo "$REPO_ROOT" --graphs-dir "$GRAPHS_DIR"` (executes `code-review-graph update` + regenerates `GRAPH_REPORT.md`). Skip if `$REPO_ROOT/.code-review-graph/` absent (print "graph missing — run /bootstrap"). If `GRAPH_REPORT.md` content changed materially (new communities, new hubs), re-extract condensed `$MEMORY_DIR/architecture.md` from it.
- [ ] **Phase 5 — Mirror plans + regenerate hot.md**:
      run `scripts/mirror-plans.sh --repo-name "$REPO_NAME"` to copy this session's plans from `~/.claude/plans/` into `$MEMORY_DIR/../plans/`.
      run `scripts/regenerate-hot.sh --memory-dir "$MEMORY_DIR"` to rebuild the curated 2k-token session-start digest from active todos + recent lessons + architecture summary.
- [ ] **Phase 6 — Handoff**: print the summary block (history path, todo counts, lesson counts, graph state, plans mirrored, hot.md token count).

## Validation loop

1. After each phase, verify the expected artifact exists and changed:
   - Phase 0: if corrections found → lessons.md line count increased.
   - Phase 1: `tail -1 history.md` shows today's block.
   - Phase 2: todo.md Active/Backlog/Done counts reflect the move.
   - Phase 3: no duplicate lessons; promoted rules present in `.claude/CLAUDE.md`.
   - Phase 3.5: either a new file in `~/.claude/golden/` OR explicit user skip logged.
   - Phase 4: `$GRAPHS_DIR/GRAPH_REPORT.md` mtime newer than session start.
   - Phase 5: hot.md byte count 1-3k; plans mirrored count reported.
2. If any validation fails: report which phase, explain expected vs actual, ask whether to re-run or skip.
3. Do not print "wrap-up complete" if any phase was silently skipped.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Skipping the corrections audit because "nothing important happened" | Phase 0 is mandatory — at minimum log "No new corrections this session." |
| Editing prior `history.md` entries | Append-only; each session is a new `## <SESSION_DATE>` block |
| Writing a vague lesson like "be more careful" | Imperative rule + **Why** — "Quote globs in Bash: `find . -name '*.py'`, because unquoted globs expanded before invocation in session 2026-04-02." |
| Duplicating a finding across `lessons.md` and `history.md` | Rule goes to lessons; narrative goes to history; never both |
| Skipping graph refresh to "save time" | `code-review-graph update` is <2s incremental — always run it unless the graph DB is absent |
| Hand-editing `architecture.md` instead of re-extracting from `GRAPH_REPORT.md` | `architecture.md` is derived from `GRAPH_REPORT.md`; edits lose on next refresh |
| Auto-saving a golden without user confirmation | Phase 3.5 requires all 3 signals + explicit `y` — premature goldens pollute `/replay` |
| Proposing a golden save when the session was exploration/discussion | Skip silently unless a concrete error was traced to root cause AND fixed AND confirmed |
| Saving a session where Claude abandoned approaches mid-stream | The golden records "steps that worked" — abandoned paths mean the narrative isn't clean |
| Reporting "wrap-up complete" without counts | Phase 5 must show todo/lesson counts + graph state; silence reads as skipped |

## References

- `references/correction-patterns.md` — detection heuristics for user corrections in transcripts and the exact `lessons.md` entry format. Read during Phase 0.
- `scripts/append-history.sh` — appends a deterministic `## <SESSION_DATE>` block to `history.md`. Args: `--memory-dir <path> --session-id <id>`.
- `scripts/refresh-graph-report.sh` — runs `code-review-graph update` + regenerates `$GRAPHS_DIR/GRAPH_REPORT.md`. Args: `--repo <path> --graphs-dir <path>`.
- `scripts/mirror-plans.sh` — copies plans from `~/.claude/plans/` into `~/.claude/projects/<repo>/plans/` for per-repo isolation. Args: `--repo-name <name> [--since <iso>]`.
- `scripts/regenerate-hot.sh` — rebuilds the 2k-token `hot.md` digest from active todos, recent lessons, and architecture summary. Args: `--memory-dir <path>`.

## Cross-references

- `/bootstrap` — seeds the four memory files this skill updates and performs the initial graph build; must run before first `/wrap-up`.
- `code-review-graph` — the graph backend. `update` is incremental via SHA-256 diff; `wiki` regenerates community markdown consumed by the `GRAPH_REPORT.md` composer.
