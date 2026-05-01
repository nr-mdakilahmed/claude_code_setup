# Correction Patterns — Detecting and Recording User Feedback

## Contents

- When to read this file
- Detection heuristics (explicit signals)
- Detection heuristics (implicit signals)
- Triage: what earns a lesson entry
- `lessons.md` entry format
- Section routing (Patterns / Anti-patterns / Wins)
- Dedup and escalation
- Worked examples

## When to read this file

During **Phase 0** of `/wrap-up`. Skim this once per session before scanning the transcript; the whole detection pipeline lives here so `SKILL.md` stays lean.

## Detection heuristics (explicit signals)

Scan the session messages for these tokens from the user. Any single hit triggers a lesson candidate.

| Signal | Example | Likely lesson class |
|---|---|---|
| Direct negation | "no", "don't", "stop", "nope" | Anti-pattern |
| Correction verb | "actually", "instead", "rather", "use X not Y" | Pattern |
| Judgment | "wrong", "that's not right", "that's broken", "incorrect" | Anti-pattern |
| Reset | "start over", "revert that", "undo" | Anti-pattern |
| Constraint reminder | "remember we agreed", "per the convention", "in this repo we…" | Pattern (convention) |
| Approval of an alternative | "yes, that one works", "good, keep that approach" | Win |

## Detection heuristics (implicit signals)

These are softer — scan Claude's own messages for these behaviors, then check whether the user corrected them silently by re-asking or rewording.

| Signal | What to look for |
|---|---|
| Tool flip | Claude switched tools mid-task (e.g., `Bash grep` → `Grep` tool) |
| Retry loop | Same command re-run 2+ times with tweaked flags |
| Unfinished approach | Claude abandoned a plan partway through without the user objecting |
| Silent redirect | User re-asked the same question with different phrasing |
| Permission denied / workaround | A command failed and Claude found a detour; the detour is the lesson |

Implicit signals produce lessons only when the outcome was non-trivially different from the initial attempt. Noise reduction: a single typo fix is not a lesson.

## Triage: what earns a lesson entry

A lesson is worth recording when **all three** hold:

1. **Durable** — the rule will apply in future sessions (not a one-off repo quirk that is already captured in `architecture.md`).
2. **Actionable** — it changes what Claude *does*, not just what it *knows*.
3. **Surprising to a sharp engineer** — if a senior would have made the same mistake, it earns a lesson. If only a junior would miss it, it is noise.

If any of the three fails, drop it.

## `lessons.md` entry format

Every entry is a single bullet in imperative voice with a **Why** clause. Format:

```markdown
- **<imperative rule>** — <why: the actual mistake and what the correct approach is>
```

Required elements:

- **Imperative verb** at the start ("Quote", "Prefer", "Never", "Validate").
- **Specific subject** — name the tool, file, pattern, or command.
- **Why clause** after the em dash — one sentence explaining the failure that motivated the rule. Include a date stamp when the correction is memorable so `history.md` cross-reference is easy.

Reject any candidate entry that reads like:

- "Be more careful" (not actionable).
- "Python is important" (not a rule).
- "User prefers X" without saying *why* X is correct.

## Section routing (Patterns / Anti-patterns / Wins)

`lessons.md` has three sections seeded by `/bootstrap`:

| User signal | Section | Rationale |
|---|---|---|
| "do this" / "prefer X" / convention reminder | `## Patterns` | Prescriptive rule — what to do |
| "don't do this" / "that broke" / failed approach | `## Anti-patterns` | Proscriptive rule — what to avoid |
| "that worked great" / "keep that approach" | `## Wins` | Approach that paid off — replicate it |

If the correction fits two sections (e.g., prescribe a new approach AND forbid the old one), write two entries — one in each section. They cross-reference naturally via the **Why** clause.

## Dedup and escalation

Before writing a new entry:

1. `grep -i` the bolded rule fragment in `lessons.md`. If a near-duplicate exists, extend the **Why** clause instead of adding a second line.
2. If the same rule has appeared 2+ times in `history.md` over distinct sessions, it is a convention, not a lesson. Promote it to `.claude/CLAUDE.md` under `## Key Conventions` and remove the duplicates from `lessons.md`.
3. Escalated conventions are then loaded automatically on every session via the `@` references `/bootstrap` wrote into project `CLAUDE.md`.

## Worked examples

**Explicit correction (Anti-pattern)**

User said: "No, don't use `rm -rf` in that script — it wiped my working directory last time."

Entry:

```markdown
- **Never chain `rm -rf` in automation scripts** — cost the user uncommitted work in session 2026-03-11; prefer `trash` or a dry-run flag that requires explicit confirmation.
```

**Implicit correction (Pattern)**

Claude tried `grep -r "foo"` in Bash, got a permission error, then switched to the `Grep` tool which worked. User did not comment but kept using the task. The switch is the lesson.

Entry:

```markdown
- **Prefer the `Grep` tool over `grep -r` in Bash** — `grep -r` failed on sandbox permission boundaries in session 2026-03-14; the built-in `Grep` tool respects the harness permission model and is faster.
```

**Convention escalation**

`lessons.md` has had three entries about parameterized SQL across different sessions. On the fourth wrap-up, the rule is promoted to `.claude/CLAUDE.md`:

```markdown
## Key Conventions

- **Parameterized SQL always** — never interpolate values into queries; use bind params. (Escalated 2026-04-02 after 3 repeat lessons.)
```

The three source lessons are deleted from `lessons.md` with a single pointer line:

```markdown
- **See `.claude/CLAUDE.md` §Key Conventions for parameterized SQL rule** — escalated 2026-04-02.
```

## Smell tests

After writing entries, skim the `lessons.md` diff once more:

- Does every bullet start with an imperative verb?
- Does every bullet have a **Why** clause with at least one concrete detail (file, command, date, tool)?
- Would a new Claude session reading only this file know what to do differently?

If any answer is no, rewrite before finishing Phase 3.
