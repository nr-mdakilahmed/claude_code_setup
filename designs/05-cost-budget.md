# Design: Cost Budget + Statusline Enforcement

## Problem

Current `CLAUDE.md` has a Model × Effort routing matrix, but enforcement is
manual. A session can easily burn $20+ on Opus + xhigh before the user
notices. Mistakes compound: one bad session sets the session floor, and
every subagent inherits it.

## Proposed approach

### Primitives needed

1. **Daily budget file**: `~/.claude/budget.json`
   ```json
   {
     "daily_cap_usd": 15.0,
     "weekly_cap_usd": 75.0,
     "auto_downshift_pct": 80,
     "hard_stop_pct": 100
   }
   ```

2. **Cost tracker**: `~/.claude/telemetry/cost.jsonl` — one line per turn with
   model, input tokens, output tokens, computed cost.
   - Hook: PostToolUse on the main LLM turn (if exposed; else on session end)
   - Prices hardcoded per model in a lookup.

3. **Statusline integration**: existing `~/.claude/hooks/statusline.sh` reads
   today's total from `cost.jsonl`, shows `$X.XX / $Y.XX (Z%)` in live view.

4. **Enforcement wrapper**: `~/.claude/hooks/budget-guard.sh` — PreToolUse hook.
   - If today's cost ≥ `auto_downshift_pct`, inject a warning banner into
     tool output reminding Claude to switch to Haiku.
   - If today's cost ≥ `hard_stop_pct`, block the tool call with a message
     asking for explicit user override via `/budget override`.

### Interfaces

- `/budget status` — show today's spend + remaining cap
- `/budget set --daily 20 --weekly 100` — update budget
- `/budget override 5` — grant +$5 emergency buffer for this session

## Open questions

1. **Cost data source**: Claude Code doesn't currently expose per-turn token
   counts to hooks in a stable way. May need to proxy via the statusline's
   existing API token counter or wrap the anthropic CLI.
2. **Subagent cost attribution**: subagent costs roll up to the parent session,
   but we don't get itemized counts. Rough approximation OK.
3. **Hard stop UX**: blocking a tool call is disruptive. Soft nudge (warning
   banner) may be sufficient; hard stop only at 120%.

## Rollout

1. Add `budget.json` + parser. (20 lines)
2. Add cost tracker hook. (Exposed-data-dependent; may need wrapper.)
3. Extend statusline to render budget state. (Existing file edit.)
4. Add `/budget` skill (low-freedom, script-backed). (30 lines)
5. Test for a week; tune downshift threshold.

## Risk

- If cost data is unreliable (can't hook per-turn), the budget enforcer
  becomes guesswork. Verify telemetry works end-to-end before building on it.
- Anthropic may ship a native budget feature that invalidates this. Track:
  https://github.com/anthropics/claude-code/issues (search "budget", "cost cap")
