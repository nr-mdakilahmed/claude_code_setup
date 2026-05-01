# Design: Golden-Path Replay

## Problem

Every successful session ends. Tomorrow you solve a similar problem from
scratch. Memory captures lessons (rules) but not **sequences** (the exact
chain of tool calls and files touched that produced the fix). A sequence is
worth 100× more than a rule for repeat tasks.

## Proposed approach

### Structure

```
~/.claude/golden/
├── index.json                       # lookup: pattern → golden file
├── airflow-dag-timeout-fix.md       # example pattern
├── snowflake-ingestion-retry.md
└── nr-alert-signal-loss.md
```

### Golden file schema (~500 lines max per golden)

```markdown
---
pattern: airflow-dag-timeout-fix
tags: [airflow, dag, timeout, retry]
trigger_hints: ["DAG timing out", "task exceeded execution_timeout", "SLA miss"]
success_criteria: "DAG completes within SLA on 3 consecutive runs"
last_validated: 2026-05-01
---

# Airflow DAG Timeout Fix

## Symptom
<what the user saw>

## Root cause pattern
<what was actually wrong>

## Steps that worked
1. Check DAG logs: `code-review-graph query_graph --pattern "callers_of" --node "<task_fn>"`
2. Identify upstream retry config: ...
3. Add `retry_exponential_backoff=True` + `max_retry_delay=timedelta(...)`
4. Validate: re-run on staging, watch 3 cycles

## What NOT to do
- Don't just increase `execution_timeout` — hides the root cause
- Don't disable retries on transient network failures

## Files typically touched
- `dags/<dag_name>.py`
- `include/sql/<related_query>.sql` (if the query is slow)
```

### Capture mechanism

Opt-in at wrap-up:
> "This session fixed an Airflow DAG timeout. Save as golden `airflow-dag-timeout-fix`? [y/N]"

If yes:
1. Distill the transcript (Opus one-shot) into the schema above.
2. Write to `~/.claude/golden/<pattern>.md`.
3. Update `index.json`.

### Replay mechanism

`/replay <pattern>` slash command:
1. Loads the golden into context as a skill-style one-shot.
2. Claude treats it as "prior art" for the current task.
3. Much cheaper than re-deriving the fix from scratch.

Auto-detect: on session start, scan user's opening prompt for trigger hints;
suggest matching golden. User approves with one keystroke.

## Interfaces

- `/golden save <pattern>` — distill current session into a golden
- `/golden list` — show all goldens with tags + last_validated
- `/golden validate <pattern>` — replay in a scratch repo to verify still works
- `/replay <pattern>` — load golden for current task

## Open questions

1. **Distillation quality**: can Claude write a good golden from its own
   transcript? Needs testing. Plan: hand-write 3 goldens first; see if auto
   distillation matches.
2. **Staleness**: goldens rot as APIs change. `validate` command should
   re-run periodically. How automated?
3. **Privacy**: goldens can capture internal logic, secrets, repo names.
   Default: golden dir is private (`~/.claude/golden/`, gitignored).
4. **Cross-repo goldens vs per-repo**: some goldens are pattern-level
   (Airflow timeout = universal), others are company-specific (our dbt
   conventions). Allow tagging `scope: global|repo:<name>` and filter on
   replay.

## Rollout

1. Create dir + index schema. Hand-write 3 goldens from recent wins.
2. Add `/golden save` — Opus distillation skill (low-freedom, exact template).
3. Add `/replay` — Sonnet load + apply.
4. Add auto-detect nudge at session start (check trigger_hints against prompt).
5. After 10 goldens: measure repeat-task completion time before/after replay.

## Risk

- Goldens that rot silently cause worse sessions than no goldens. Aggressive
  validation or timestamp staleness warnings required.
- Tag taxonomy ossifies. Allow free-form tags; dedupe via fuzzy match in index.
