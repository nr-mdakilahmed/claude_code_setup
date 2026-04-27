---
name: demo
description: >
  Use when preparing demos, show-and-tells, or reframing after a bad presentation.
  Frames a 45-minute technical demo that leads with the problem, not the solution.
  Supports --reframe (post-bad-demo) and --objections (Q&A prep only).
  Auto-triggers when preparing demos or presentations.
---

# Demo Prep Skill

## Usage

- `/demo <topic>` — Full demo prep
- `/demo <topic> --reframe` — Rewrite after bad demo with feedback
- `/demo <topic> --objections` — Focus only on Q&A prep

**Golden rule**: The audience must FEEL the problem before you show the solution.

## Phase 1: Discovery (ask before generating)

### 1.1 — The Basics
- What are you demoing?
- Who's in the room? (engineers, managers, directors)
- What's their current workflow?

### 1.2 — The Problem
- What breaks today without your solution? Get a real incident.
- Who gets hurt? Name the persona.
- How do they find out today? Later discovery = stronger pitch.

### 1.3 — The Objections
- What's the "why not just X?" alternative?
- What does existing tool do BETTER? (acknowledge honestly)
- What's genuinely impossible with existing tool? (sharpest argument)

### 1.4 — Live Demo
- Single most impressive thing in under 3 minutes?
- Fallback if demo breaks?

## Phase 2: Narrative Structure (45 min)

### Act 1: "The World Is Broken" (8 min)
- **Hook (2 min)**: Question the audience has felt. No slides. No product.
- **Gap (3 min)**: What's covered today vs NOT covered. Name real tables/tools/teams.
- **Cost (3 min)**: Quantify impact for audience personas. Use real incidents.

### Act 2: "There's a Better Way" (15 min)
- **Product (10 min)**: Show output first, explain machinery later. Each capability maps to a gap from Act 1: "Remember gap? Here's what it looks like now."
- **Comparison (5 min)**: Address "why not X?" head-on. Acknowledge X's strengths. Show what X can't do. Say "complementary, not replacement."

### Act 3: "See It Work" (12 min)
- **Live Demo (8 min)**: One happy path, narrate the WHY. Time-box strictly.
- **"One More Thing" (2 min)**: Show flexibility — change/add something.
- **Close the Loop (2 min)**: Path from demo to production in 3-4 steps.

### Act 4: "Why This Matters" (5 min)
- **Use Cases (3 min)**: 2-3 persona-specific before/after scenarios.
- **Getting Started (2 min)**: Step table with What/Who. Show current adoption numbers.

### Act 5: Q&A (5 min)
- 5-8 likely questions with Short + Detailed answers
- **"Yes, And" technique**: Agree with valid part, then extend

## Phase 3: Output (generate all)

1. **One-Page Cheat Sheet** — Quick-reference during demo
2. **Full Demo Script** — Per-beat: [Screen], Say, Show, Transition
3. **Q&A Prep** — 5-8 questions with short/detailed/pushback answers
4. **Pre-Demo Checklist** — Setup verification

## Phase 4: Reframe Mode (`--reframe`)

Post-mortem first: What feedback? Which question hit hardest? What did you open with?

| Symptom | Fix |
|---|---|
| "Why do we need this when we have X?" | Differentiate BEFORE showing product |
| "Can't we just extend X?" | Sharpen gaps X can't fill |
| Disengagement after 10 min | Shorten features, add pain callbacks |
| "Seems like a lot of work" | Show results first, machinery later |
| Director strategic question | Add cost beat for directors |

## Phase 5: Objections-Only (`--objections`)

8-10 questions with Short + Detailed + "Yes, And" responses.
Identify the single Killer Question with a paragraph answer that acknowledges, reframes, and gives concrete example.
