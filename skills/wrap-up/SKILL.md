---
name: wrap-up
description: >
  Run at end of EVERY session. Persists context to history.md, updates todo.md
  and lessons.md, conditionally refreshes knowledge graph if >5 files changed.
  Invoke with /wrap-up.
---

# /wrap-up — Session End

**Run at end of EVERY session.** Persists context, updates memory, conditionally refreshes graph.

## Setup Variables

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPO_NAME=$(basename "$REPO_ROOT")
MEMORY_DIR="$HOME/.claude/projects/$REPO_NAME/memory"
GRAPHS_DIR="$HOME/.claude/projects/$REPO_NAME/graphs"
SESSION_DATE=$(date '+%Y-%m-%d %H:%M')
```

If `$MEMORY_DIR` doesn't exist: print "No memory found — run /bootstrap first." and stop.

## Phase 0 — Corrections Audit (Self-Healing)

Before doing anything else, scan this session's conversation for:
- Any moment the user said "no", "don't", "stop doing X", "wrong", "that's not right", "use Y instead"
- Any approach you tried that failed before finding the right one
- Any tool or command that needed a workaround
- Any assumption you made that turned out to be incorrect

For EACH finding, append to `$MEMORY_DIR/lessons.md`:
```
- **<imperative rule>** — <why: the actual mistake and what the correct approach is>
```

If nothing new: write "No new corrections this session." and continue.
This step is MANDATORY — not optional. The whole point of self-healing is that this happens every time.

---

## Phase 1-2 — Git Diff + Session Summary

```bash
# Get changed file count and diff stat
FILES_CHANGED=$(git -C "$REPO_ROOT" diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo 0)
git -C "$REPO_ROOT" diff --stat HEAD 2>/dev/null | head -50
```

Generate structured summary:
- **Accomplished**: what was built/fixed/investigated
- **Key decisions**: architectural or design choices made
- **Blockers**: anything unresolved
- **Next steps**: immediate follow-up tasks

## Phase 3 — Append to history.md

Add entry to `$MEMORY_DIR/history.md`:

```markdown
## <SESSION_DATE>
**Summary**: <1-2 sentence summary>
**Files changed**: <count from git diff stat>
**Accomplished**: <bullet list>
**Decisions**: <bullet list>
**Next**: <bullet list>
---
```

## Phase 3.5 — Update todo.md + lessons.md

**todo.md** (`$MEMORY_DIR/todo.md`):
- Move completed Active items to Done (with completion date)
- Add new tasks from "Next steps" to Backlog

**lessons.md** (`$MEMORY_DIR/lessons.md`):
- Promote any Phase 0 corrections that weren't yet written (dedup — don't add duplicates)
- If a pattern appeared 2+ times across history → escalate to `.claude/CLAUDE.md` Key Conventions
- If a workaround was needed → add to `## Anti-patterns`
- If an approach worked especially well → add to `## Wins`
- Every lesson must have a **Why** — a rule without a reason gets ignored next session

## Phase 4 — Conditional Graph Refresh

Use `$FILES_CHANGED` from Phase 1-2:

| `$FILES_CHANGED` | Action |
|---|---|
| > 5 | Run `/graphify` → rewrites `$GRAPHS_DIR/GRAPH_REPORT.md`, then re-extract `$MEMORY_DIR/architecture.md` from it (same condensed extraction as bootstrap Phase 3) |
| <= 5 | Skip — graph still accurate |

## Phase 5 — Handoff

Print:
```
Wrap-up complete — <REPO_NAME>
  History: appended to ~/.claude/projects/<REPO_NAME>/memory/history.md
  Todo:    <N active> active, <N backlog> backlog, <N done> done
  Lessons: <N patterns> patterns, <N wins> wins
  Graph:   <refreshed / skipped — N files changed>
```
