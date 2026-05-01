---
name: replay
description: Loads a saved golden-path markdown into context as prior-art for the current task, so Claude follows proven steps instead of re-deriving the fix. Golden must exist at ~/.claude/golden/<pattern>.md. Invoke with /replay <pattern>.
when_to_use: Invoke explicitly with /replay <pattern> when starting a task that matches a past success. Run /golden list first to find the slug. Never auto-invokes.
allowed-tools: Read Grep Bash
disable-model-invocation: true
---

# Replay — Load A Golden Path

Turns prior-art into active context. A golden is a record of steps that worked last time; replay makes Claude follow them first rather than re-deriving.

**Freedom level: Low** — the golden's Steps section is the plan. Claude executes it; judgment is limited to adapting exact file paths / function names if the repo has renamed things since the golden was saved.

## 1. Validate Before Applying

**Every replay starts with a staleness check.**

- Run `scripts/replay-load.sh --pattern <slug>`; the script calls `golden-validate` internally and refuses to load if the golden is stale.
- If stale: report which files/steps are broken, ask user whether to proceed with manual adaptation or bail.

## 2. Load, Then Adapt

**Treat the golden as a strong prior, not a script to execute blindly.**

- After loading, restate the plan from the golden in your own words (1-3 sentences) to confirm you understood.
- Check each step against the current repo before running: file paths may have moved, functions renamed, dependencies upgraded.
- If a step references a file that no longer exists at the given path → search for the renamed equivalent using the graph (`query_graph` MCP tool) before falling back to Grep.

## 3. Record Divergences

**If the golden needed adaptation, note what changed — this improves the golden for next time.**

- At end of the task, if the replay deviated from the golden's steps, suggest `/golden validate <pattern>` and then an update.
- Do not silently drift — the whole point of goldens is that they stay accurate.

## Quick reference

| Need | Command | Behavior |
|---|---|---|
| Load a golden into context | `/replay <pattern>` | Reads + validates + announces "following golden X" |
| See what goldens exist before replaying | `/golden list` | From the `/golden` skill |
| Dry-run (show golden without applying) | `/replay <pattern> --dry-run` | Prints the golden; does not adopt as plan |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] Run `scripts/replay-load.sh --pattern "$PATTERN"` — this validates + prints the golden.
- [ ] If the script exits non-zero (stale), stop and report which files moved. Ask user to proceed or bail.
- [ ] Restate the plan in 1-3 sentences (confirms comprehension to the user).
- [ ] For each step in "Steps That Worked", verify referenced files/functions still exist in the current repo.
- [ ] Execute the adapted plan. At each step, assert the invariant the golden expected.
- [ ] Track any divergences in a running note; at task end, report them to the user for golden update consideration.

## Validation loop

1. After loading the golden, verify one randomly-chosen file reference still resolves.
2. **Validate immediately**: `Read <path>` on one "Files Typically Touched" entry. If it fails, re-run `scripts/replay-load.sh`.
3. If the golden is too stale to adapt: stop, surface the issue, ask user for a fresh diagnostic session.
4. Proceed to execution only when at least one file reference is confirmed current.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Executing golden steps literally without checking current state | Steps are a strong prior; always verify each referenced file/function exists before running |
| Loading a golden and not announcing the match to the user | Always state: "Loaded golden `<slug>` — plan: <1-sentence summary>". User can redirect if wrong match. |
| Loading a stale golden and hoping it still works | `replay-load.sh` blocks stale loads; if user forces, note fragility in response |
| Silently diverging from the golden's steps | Record divergences; suggest golden update at task end |
| Using `/replay` when no matching golden exists | `/golden list --tag <topic>` first; don't guess a pattern name |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `replay-load.sh` says "golden not found" | `/golden list` to find exact slug; names are kebab-case |
| Golden's file paths are all wrong | Golden scoped to a different repo; check frontmatter `scope:` |
| After loading, the plan doesn't match the current problem | Wrong golden matched; `/golden list --tag <better-keyword>`; do not force-fit |

## References

- `scripts/replay-load.sh` — `--pattern <slug> [--dry-run]`; validates + prints golden. Exits non-zero on stale.

## Cross-references

- `/golden` — creates the goldens this skill replays. Invoke `/golden save` after a successful replay if the adaptation was non-trivial.
