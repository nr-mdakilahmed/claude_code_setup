---
name: budget
description: Tracks Claude Code daily/weekly/monthly spend against caps defined in ~/.claude/budget.json. Shows status, updates caps, grants one-time overrides. Warn-only — does not hard-block tool calls, since Claude Code doesn't expose pre-turn cost reliably. Invoke with /budget status, /budget set, /budget override, /budget report.
when_to_use: Invoke explicitly. Check /budget status at session start on heavy days; adjust caps via /budget set when your workload shifts.
allowed-tools: Read Grep Bash Write Edit
disable-model-invocation: false
---

# Budget — Spend Awareness + Caps

Turns Claude's cost data into a daily dial. Session cost is already shown in the statusline; this skill adds **cumulative** awareness + warns when you cross budget.

**Freedom level: Low** — the subcommand surface is small and mechanical. Claude runs the script with flags.

## 1. Warn, Do Not Block

**Claude Code doesn't expose per-turn cost to a PreToolUse hook in a stable way, so budget enforcement is advisory.**

- Statusline renders a spend indicator (daily %).
- Stop hook appends session cost to `~/.claude/telemetry/cost.jsonl` at session end.
- When aggregate spend crosses `auto_downshift_pct` (default 80%), the statusline turns yellow. Claude should switch to Haiku for mechanical work.
- When spend crosses `hard_warn_pct` (default 100%), statusline turns red. Continue only on explicit user confirmation.

## 2. Per-Day, Not Per-Session

**Cost dashboards show per-session dollars. That's the wrong unit — you spend across sessions.**

- `/budget status` rolls up today's sessions, this week's, this month's.
- Daily is the tightest loop — tune `daily_cap_usd` first.
- Weekly and monthly catch slow-burn patterns (always below daily, but adds up).

## 3. Override Is A Decision, Not A Habit

**`/budget override <usd>` grants a one-time buffer. If you override more than twice in a week, your cap is wrong — raise it explicitly.**

- Overrides are logged with a reason.
- `/budget report --days 7` shows how often you overrode; if ≥3, raise caps via `/budget set`.

## Quick reference

| Need | Command | Output |
|---|---|---|
| See today's spend + cap | `/budget status` | Daily, weekly, monthly totals + % of cap |
| Update caps | `/budget set --daily 20 --weekly 100` | Writes to `~/.claude/budget.json` |
| Grant one-time buffer | `/budget override 5 --reason "prod incident"` | Adds $5 to today's cap; logs reason |
| Weekly report | `/budget report --days 7` | Per-day totals, override count, peak session |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] `/budget status` at session start if you expect heavy work — knowing you have $8 left shapes model choice.
- [ ] If status shows yellow (≥80%), set session default to Haiku: `/model haiku`.
- [ ] If status shows red (≥100%), stop unless the work is truly urgent. `/budget override <usd> --reason "..."` if urgent.
- [ ] End of day: `/budget report --days 1` to see peak session, override count, any surprises.

## Validation loop

1. After `/budget set`, confirm `cat ~/.claude/budget.json` reflects the change.
2. **Validate immediately**: `/budget status` prints the new cap in the output header.
3. If the cap didn't update, check JSON syntax (`jq . ~/.claude/budget.json`) and re-run.
4. Proceed only when the new cap is live.

## Anti-patterns

| Pattern | Fix |
|---|---|
| Ignoring yellow statusline | Switch to Haiku for the next few mechanical tasks |
| Overriding every day | Caps are wrong — raise them, don't bypass them |
| Treating per-session cost as the metric | Per-day matters more; a single "cheap" session after 10 expensive ones still blows the cap |
| Setting monthly cap without weekly/daily | You'll hit monthly on day 12 if daily is uncapped |
| Not recording override reason | Future you can't tune caps without seeing why past you overrode |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/budget status` shows $0 despite usage | Cost.jsonl not being written — check Stop hook registration in `~/.claude/settings.json` |
| Spend much higher than cap after one day | Session model is leaking (Opus at xhigh). Check routing rules in `CLAUDE.md`. |
| Statusline doesn't show budget | `~/.claude/budget.json` missing or malformed — run `/budget set --daily 15` to regenerate |

## References

- `scripts/budget-status.sh` — prints daily/weekly/monthly spend vs caps.
- `scripts/budget-set.sh` — edits `~/.claude/budget.json`. Flags: `--daily`, `--weekly`, `--monthly`, `--downshift-pct`.
- `scripts/budget-override.sh` — adds a one-time buffer to today's cap. Logged in `cost.jsonl`.
- `scripts/budget-report.sh` — tabular report over N days with override history.
- `~/.claude/hooks/stop-record-cost.sh` — appends session cost to `cost.jsonl` on Stop event.

## Cross-references

- `CLAUDE.md § Model × Effort Routing` — budget state should drive model choice. Yellow = Haiku/Sonnet default, red = explicit override only.
