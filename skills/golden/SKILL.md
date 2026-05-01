---
name: golden
description: Captures a successful session as a reusable "golden path" — a distilled, tag-indexed sequence of steps that solved a specific problem. Stores at ~/.claude/golden/<pattern>.md. Invoke with /golden save <pattern> after a win to make it replayable next time.
when_to_use: Invoke explicitly with /golden save <pattern>, /golden list, or /golden validate <pattern>. Never auto-invokes.
allowed-tools: Read Grep Bash Write Edit
disable-model-invocation: true
model: opus
---

# Golden — Capture Reusable Session Patterns

Turns a successful session into a replayable template. Rules capture what NOT to do; goldens capture what TO do, in order.

**Freedom level: Low** — the golden file schema is contractual with `/replay`. Claude follows the template exactly; judgment is limited to the distillation prose (Symptom, Root Cause, Steps).

## 1. Capture Only Proven Wins

**A golden is the record of a session that actually worked, end-to-end. No aspirational templates.**

- Invoke only after the user confirms the fix worked (prod-validated, tests green, DAG stable for 3 cycles).
- If uncertain whether the fix is durable → do not save. Premature goldens rot.
- "I think this is the right approach" → don't save. "This fixed the prod incident on 2026-05-01" → save.

## 2. Distill, Do Not Dump

**A golden is a distillation, not a transcript. Target: 200-500 lines max per golden.**

- Extract: Symptom, Root Cause, Steps That Worked, What NOT to Do, Files Typically Touched.
- Strip: chit-chat, dead ends Claude abandoned, tool-call noise, intermediate exploration.
- A reader opening the golden six months later should be able to replicate the fix without re-reading the original transcript.

## 3. Tag Precisely For Retrieval

**Trigger hints are how `/replay` decides which golden applies. Bad tags → wrong replay → worse than no golden.**

- Use 3-5 concrete noun phrases the user would actually say when hitting the same problem.
- "airflow DAG timeout", "SLA miss on daily ETL", "task retries exhausted" — not "debugging" or "airflow issues".
- Include negative hints when useful: `not_for: ["DAG scheduling delays", "DAG parsing errors"]` — prevents false matches.

## 4. Validate Before Trusting

**A golden rots silently. Every 30 days, re-run `validate` or downgrade its confidence.**

- `/golden validate <pattern>` reads the golden's referenced files; if any moved, renamed, or deleted → flag as stale.
- Stale goldens are NOT deleted — user decides whether to fix, re-capture, or archive.

## Quick reference

| Need | Command | Output |
|---|---|---|
| Save this session's win | `/golden save <pattern>` | Writes `~/.claude/golden/<pattern>.md` + updates index |
| See all goldens | `/golden list` | Table with pattern, tags, last_validated, scope |
| Filter by tag | `/golden list --tag airflow` | Table of matches |
| Check staleness | `/golden validate <pattern>` | Exit 0 (fresh) or 1 (stale) with reasons |
| Update a golden's tags | edit `~/.claude/golden/<pattern>.md` frontmatter directly | Manual |

## Workflow — save

Copy this checklist and check off items as you complete them:

- [ ] Confirm the session's fix is validated in prod or equivalent (user explicitly says "this worked" / "ship it" / tests pass + 3 cycles stable).
- [ ] Ask user for pattern slug (kebab-case, 2-4 words): "What should this golden be called? e.g., `airflow-dag-timeout-fix`".
- [ ] Ask user for scope: `global` (pattern-level, any repo) or `repo:<name>` (company/repo-specific).
- [ ] Distill the session into the schema: Symptom (1 para) → Root Cause Pattern (2-3 bullets) → Steps That Worked (numbered, with exact commands) → What NOT to Do (anti-patterns from this investigation) → Files Typically Touched.
- [ ] Extract 3-5 trigger_hints as phrases the user would say when hitting the same problem.
- [ ] Run `scripts/golden-save.sh --pattern <slug> --scope <scope>` with the distilled markdown on stdin.
- [ ] Print confirmation: path + "Run /replay <pattern> next time to load this."

## Workflow — validate

- [ ] Run `scripts/golden-validate.sh --pattern <slug>`.
- [ ] If exit 1 (stale), report which files are missing/moved.
- [ ] Ask user: update the golden, re-capture from a fresh session, or archive?

## Validation loop

1. After writing the golden, re-read it.
2. **Validate immediately**: `scripts/golden-validate.sh --pattern <slug>` — all referenced files must exist.
3. If validation fails: fix the golden (remove bad paths, update step). Loop up to 3 times.
4. If still failing: golden is not worth saving; delete and ask user for more info.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Saving a golden before the fix is validated in prod | Wait for user to explicitly confirm; premature goldens rot fastest |
| Dumping the full session transcript verbatim | Distill to <500 lines; steps only, no narrative filler |
| Using vague tags like "bug fix" or "debugging" | Use concrete trigger hints — phrases the user would actually say |
| Overwriting an existing golden without diffing | `golden-save.sh` refuses to overwrite unless `--force` or the old golden failed validation |
| Goldens for one-off quirks (works only on this repo at this commit) | Scope to `repo:<name>` and add `fragile: true` to frontmatter |
| Not referencing real files in Steps That Worked | Steps must include exact paths; `/replay` validates them |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `golden-save.sh` says "pattern exists" | Run `/golden validate <existing>` first; decide to update, rename, or force |
| Golden produces different results on replay | `/golden validate` — if files still exist, the golden's assumptions changed; re-capture from a fresh successful session |
| Can't find a golden when the problem recurs | Tags were too narrow; edit frontmatter `trigger_hints` to add the phrase you actually used |

## References

- `references/golden-schema.md` — canonical frontmatter + section layout for `<pattern>.md` files.
- `scripts/golden-save.sh` — `--pattern <slug> --scope <scope> [--force]`; reads distilled markdown on stdin, writes file + updates index.json.
- `scripts/golden-validate.sh` — `--pattern <slug>`; checks file references for staleness. Exit 0 fresh, 1 stale.
- `scripts/golden-list.sh` — `[--tag <tag>] [--scope <scope>] [--stale-only]`; prints tabular view.

## Cross-references

- `/replay <pattern>` — loads a saved golden as prior-art context for the current task.
- `/wrap-up` — good moment to ask "save this as a golden?" when lessons.md gets a new Win.
