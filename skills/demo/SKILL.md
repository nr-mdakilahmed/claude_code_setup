---
name: demo
description: Frames a 45-minute technical demo that leads with the problem, not the solution, and produces cheat sheet, full script, Q&A prep, and pre-demo checklist. Fires only on explicit /demo invocation with optional --reframe (post-bad-demo rewrite) or --objections (Q&A-only prep). Demo prep is intentional work the presenter starts, not ambient assistance Claude should guess at.
disable-model-invocation: false
---

# Demo Preparation

Turns Claude into a demo coach: makes the audience feel the problem before any product appears, structures 45 minutes into five acts, and scripts honest answers to the sharpest objections before Q&A.

**Freedom level: High** — demo narrative varies by audience, topic, and incident inventory. The skill directs judgment with principles, not a fixed script.

## 1. Lead With The Problem

**The audience must feel the pain before any product appears on screen.**

- Open with a question or real incident the audience has lived — no slides, no product for the first two minutes.
- Name real tables, teams, tools, and dollar / hour costs. Abstractions do not land; specifics do.
- If the presenter cannot quote a recent incident in discovery, pause prep until they find one.
- "Here's what we built" → "Here's the 3am page you got last Tuesday, and why it kept happening."

## 2. Five Acts, Not Slides

**Structure beats decks. Every beat maps to a gap the audience already feels.**

- Act 1 "World Is Broken" (8m) → Act 2 "Better Way" (15m) → Act 3 "See It Work" (12m) → Act 4 "Why This Matters" (5m) → Act 5 Q&A (5m).
- Each Act 2 capability cites the Act 1 gap it closes: "Remember the gap where X? Here's what it looks like now."
- Time-box strictly. A demo that overruns Act 3 kills Q&A, which is where buy-in actually forms.
- Full per-act timing and transitions in `references/narrative-templates.md`.

## 3. Objections Have Scripts

**Every sharp objection gets a rehearsed answer before the presenter walks in.**

- Write the top 10 likely objections and a "Short + Detailed + Yes-And" answer for each — do not improvise on stage.
- Identify the single Killer Question (the one that sinks the demo if unanswered) and draft a paragraph response that acknowledges, reframes, and cites a concrete example.
- Acknowledge the competing tool's real strengths honestly; then show what it cannot do. "Complementary, not replacement" disarms the turf objection.
- Full playbook in `references/objection-playbook.md`.

## 4. Reframe, Don't Defend

**When a demo bombs, the fix is almost always the opening, not the product.**

- In `--reframe` mode, run a post-mortem first: what feedback landed, which question hit hardest, what were the first 2 minutes. Do not touch Act 2+ until Act 1 is rebuilt.
- Symptoms map to specific act-level edits (see Quick reference).
- Defensive answers ("but we also…") lose the room. "Yes, and here's what that unlocks" keeps it.

## Quick reference

Mode selection and symptom-to-fix map — the lookup consulted on every invocation.

| Mode | When to use | Output |
|---|---|---|
| `/demo <topic>` | First-time prep for an upcoming demo | Full 5-act narrative, cheat sheet, Q&A, checklist |
| `/demo <topic> --reframe` | Previous demo landed badly, rewriting before next attempt | Post-mortem + Act 1 rebuild + updated Q&A |
| `/demo <topic> --objections` | Deck is fine; presenter wants only Q&A rehearsal | Top 10 objections, Killer Question paragraph, "Yes-And" responses |

| Post-demo symptom | Act-level fix |
|---|---|
| "Why do we need this when we have X?" | Differentiate in Act 1 before Act 2 shows product |
| "Seems like a lot of work" | Show output first in Act 2; machinery second |
| Disengagement after 10 min | Shorten Act 2 features; add pain callbacks to Act 1 gaps |
| Director asked a strategic question you had no answer for | Add cost / business-impact beat in Act 1 |
| "Can't we just extend X?" | Sharpen the "genuinely impossible with X" gap in Act 1 |

## Workflow

Copy this checklist and check off items as you complete them. Steps 1–2 are gating — do not skip.

- [ ] Discovery: confirm audience, their current workflow, and at least one real incident
- [ ] Discovery: name the sharpest "why not just X?" alternative and what it does better
- [ ] Act 1 draft (8m): hook + gap + cost, with real names and numbers
- [ ] Act 2 draft (15m): product capabilities each tied back to an Act 1 gap; competitor comparison honest
- [ ] Act 3 draft (12m): one happy-path demo scripted beat-by-beat, plus fallback if live demo breaks
- [ ] Act 4 draft (5m): 2–3 persona before/after scenarios and getting-started steps
- [ ] Act 5 draft (5m): 5–8 likely questions with Short + Detailed answers
- [ ] Generate one-page cheat sheet (for use during the demo)
- [ ] Generate full script (per beat: `[Screen]`, Say, Show, Transition)
- [ ] Generate Q&A prep (short / detailed / pushback answers)
- [ ] Generate pre-demo checklist (setup verification)
- [ ] Dry run against the checklist — cut anything that does not earn its minute

## References

- `references/narrative-templates.md` — full 45-minute outline with per-beat timing, plus three variant narratives (greenfield / retrofit / migration)
- `references/objection-playbook.md` — top 10 objections with scripted responses, Killer Question frame, `--objections` mode playbook

## Cross-references

| Skill | When |
|---|---|
| `python` / `sql` / `pyspark` | Topic is a code-heavy demo — pull real snippets from the repo, not toy examples |
| `nrql` / `nralert` | Topic is observability — use real incident queries in Act 1 |
