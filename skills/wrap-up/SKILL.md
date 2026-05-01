---
name: wrap-up
description: Persists session context at end of work by appending to history.md, updating todo.md and lessons.md, and conditionally refreshing the knowledge graph when repo structure drifts. Fires only on explicit /wrap-up invocation.
when_to_use: Invoke explicitly with /wrap-up at the end of every session. Never runs implicitly — the user alone starts it.
allowed-tools: Read Grep Bash Write Edit
disable-model-invocation: true
---

# Wrap-Up — Session Persistence

Turns Claude into a session steward: captures corrections, writes durable notes to the four memory files seeded by `/bootstrap`, and refreshes the knowledge graph only when the repo has materially drifted.

**Freedom level: Low** — memory file paths and formats are contractual with `/bootstrap` and `/graphify`. Claude follows the workflow exactly; judgment is limited to summary prose and lesson wording.

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

## 3. Refresh Graph When Drift

**Only re-run `/graphify` when >5 source files changed; treat the graph as a cache, not a log.**

- Use `scripts/should-refresh-graph.sh` to compute the structural diff. It exits 0 (refresh) or 1 (skip).
- Skip on doc edits, formatting-only diffs, test-only changes.
- After `/graphify` writes the new `GRAPH_REPORT.md`, re-extract the condensed `architecture.md` the same way `/bootstrap` Phase 3 did.

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
| Architectural / structural shift | `architecture.md` (via `/graphify`) | Regenerate only when >5 files changed; never hand-edit |
| Files changed > 5 since last wrap-up | Refresh graph | `scripts/should-refresh-graph.sh` exits 0 → run `/graphify` |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] Resolve `REPO_ROOT`, `REPO_NAME`, `MEMORY_DIR=$HOME/.claude/projects/$REPO_NAME/memory`, `GRAPHS_DIR=$HOME/.claude/projects/$REPO_NAME/graphs`, `SESSION_DATE=$(date '+%Y-%m-%d %H:%M')`.
- [ ] If `$MEMORY_DIR` does not exist: print "No memory found — run /bootstrap first." and stop.
- [ ] **Phase 0 — Corrections audit**: scan transcript using heuristics in `references/correction-patterns.md`; for each finding, append an imperative rule + Why to `$MEMORY_DIR/lessons.md`. If none, write "No new corrections this session." to the phase log.
- [ ] **Phase 1 — History**: run `scripts/append-history.sh --memory-dir "$MEMORY_DIR" --session-id "$SESSION_DATE"` with a prepared summary (Accomplished / Decisions / Blockers / Next).
- [ ] **Phase 2 — Todo**: edit `$MEMORY_DIR/todo.md` — move completed items from `## Active` to `## Done` with completion date; append new tasks from "Next" to `## Backlog`.
- [ ] **Phase 3 — Lessons**: dedupe and finalize `$MEMORY_DIR/lessons.md` — promote Phase 0 rules; if a pattern has appeared 2+ times across `history.md`, escalate it to `.claude/CLAUDE.md` under `## Key Conventions`.
- [ ] **Phase 4 — Conditional graph refresh**: run `scripts/should-refresh-graph.sh --repo "$REPO_ROOT" --since "<last wrap-up timestamp>"`; if exit 0, invoke `/graphify`, then re-extract condensed `$MEMORY_DIR/architecture.md` from the new `$GRAPHS_DIR/GRAPH_REPORT.md`.
- [ ] **Phase 5 — Handoff**: print the summary block (history path, todo counts, lesson counts, graph state).

## Anti-patterns

| Pattern | Fix |
|---|---|
| Skipping the corrections audit because "nothing important happened" | Phase 0 is mandatory — at minimum log "No new corrections this session." |
| Editing prior `history.md` entries | Append-only; each session is a new `## <SESSION_DATE>` block |
| Writing a vague lesson like "be more careful" | Imperative rule + **Why** — "Quote globs in Bash: `find . -name '*.py'`, because unquoted globs expanded before invocation in session 2026-04-02." |
| Duplicating a finding across `lessons.md` and `history.md` | Rule goes to lessons; narrative goes to history; never both |
| Running `/graphify` on every wrap-up regardless of diff | Gate on `scripts/should-refresh-graph.sh` — refresh is a cache, not a log |
| Hand-editing `architecture.md` instead of regenerating via `/graphify` | `architecture.md` is derived from `GRAPH_REPORT.md`; edits lose on next refresh |
| Reporting "wrap-up complete" without counts | Phase 5 must show todo/lesson counts + graph state; silence reads as skipped |

## References

- `references/correction-patterns.md` — detection heuristics for user corrections in transcripts and the exact `lessons.md` entry format. Read during Phase 0.
- `scripts/append-history.sh` — appends a deterministic `## <SESSION_DATE>` block to `history.md`. Args: `--memory-dir <path> --session-id <id>`.
- `scripts/should-refresh-graph.sh` — computes structural file-count diff; exit 0 if refresh needed, 1 if skip. Args: `--repo <path> --since <timestamp>`.

## Cross-references

- `/bootstrap` — seeds the four memory files this skill updates; must run before first `/wrap-up`.
- `/graphify` — invoked by Phase 4 when the structural-change threshold trips; rewrites `GRAPH_REPORT.md` which re-seeds `architecture.md`.
