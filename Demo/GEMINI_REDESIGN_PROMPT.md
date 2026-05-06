# Gemini Redesign Prompts — DataOS Ingestion AI-Led Development Deck
# 17 fully self-contained prompts — copy-paste each one directly, no editing needed
# BATCH 1: Slides 01–10 | BATCH 2: Slides 11–17

---

# ═══════════════════════════════════════════════════
# BATCH 1 — Upload slide_01.png through slide_10.png
# ═══════════════════════════════════════════════════

---

## SLIDE 01
> Upload: slide_01.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_01.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• Background: deep navy #0D0D24 (this is a dark hero slide)
• Accent green: #00AC69
• White text on dark backgrounds
• Font: modern sans-serif (Inter or similar), bold headers
• New Relic logo (green hexagon + "new relic." wordmark) — bottom-right corner
• Disclaimer bottom-left (tiny grey text): "© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution."

━━━ SLIDE LAYOUT ━━━
SPLIT LAYOUT: Left 65% content | Right 35% darker navy panel

LEFT SIDE (navy background):
- New Relic logo top-left (large, prominent)
- Headline stack:
    "Ingestion Team" — 42pt, white, bold
    "AI-Led Development" — 38pt, #00AC69 green, bold
    "Environment" — 38pt, white, bold
- Thin #00AC69 horizontal divider line
- Italic grey subtitle: "Claude Code  +  GitHub Copilot  +  New Relic MCP"

RIGHT PANEL (slightly darker navy, subtle border):
Five stacked chips — each has a thin green left stripe, icon, white text:
    🚀  "8–12×  productivity for DE tasks"
    ⏱  "2–3 days → 2–6 hours per ticket"
    🔍  "0–20 min alert issue diagnosis"
    ⚡  "5 parallel agents with /avengers"
    📦  "Knowledge that compounds daily"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 02
> Upload: slide_02.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_02.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• Background: white slide with full-width #00AC69 green header bar
• Cards: white background, subtle shadow, colored top accent stripe
• Hero numbers: large (48–56pt), bold, colored to match accent
• Font: modern sans-serif (Inter or similar)
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (full-width, #00AC69, white bold text):
"The Challenge — Four Real Pains the DataOS Ingestion Team Was Living With"

BODY: 2×2 grid of cards. Each card has: colored top accent stripe, emoji + title, large hero number, thin divider, grey description text.

CARD 1 — top-left (top stripe: #E53E3E red):
Emoji + title: 🕐  "Slow Development Tickets"
Hero: 2–3 DAYS  (color: #E53E3E, ~52pt bold, centered)
Description: "per ticket — regardless of complexity or volume"

CARD 2 — top-right (top stripe: #FFC107 amber):
Emoji + title: 🔍  "Pipeline Debugging"
Hero: 30 MIN–3 HRS  (color: #FFC107, ~44pt bold, centered)
Description: "backtracking alert issues one by one manually"

CARD 3 — bottom-left (top stripe: #1F2937 charcoal):
Emoji + title: 💥  "Hidden Blast Radius"
Hero: 5-DAY  (color: #1F2937, ~52pt bold, centered)
Description: "incident caused by a change no one knew would break"

CARD 4 — bottom-right (top stripe: #1F2937 charcoal):
Emoji + title: 🗂  "No Historical Context"
Hero: HOURS–DAYS  (color: #1F2937, ~44pt bold, centered)
Description: "re-discovering repo structure and past decisions every time someone joined, left, or came back"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 03
> Upload: slide_03.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_03.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header bar | Three-column layout
• Cards with colored left accent stripes | Modern sans-serif font
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"DataOS Ingestion  —  How We Run AI-Led Development Today"

THREE EQUAL COLUMNS:

COLUMN 1 — "What We Own" (dark charcoal header):
Vertical pipeline flow diagram:
  ┌─ Small grey label: "DATA SOURCES"
  │  White box: "Billing Platform · Kafka · SFDC · Zuora · etc."
  ↓  Green arrow
  │  LARGE GREEN BOX (#00AC69, white text, bold):
  │  "INGESTION — WE OWN THIS"
  │  "FiveTran · Kafka · NRDB · Spark · Custom Pipelines"
  ↓  Green arrow
  │  Small grey label: "DOWNSTREAM ZONE 2"
  └─ White box: "Consumer · Data Lake · Dashboard"

COLUMN 2 — "Daily Workflow" (#00AC69 header):
6 numbered step rows (alternating #E8F8F1 light green / white):
1  bold: "Start with full context"
   grey: "Memory + codebase graph auto-load in seconds"
2  bold: "Copilot: lines + blind spot check"
   grey: "Autocomplete in IDE · cross-model review catches what Claude misses"
3  bold: "Skills trigger automatically"
   grey: "/airflow · /pyspark · /nrql · /terraform · /sql"
4  bold: "Incidents diagnosed via NR MCP"
   grey: "30 min–3 hrs → 0–20 min for alert issues"
5  bold: "5 parallel agents for complex tasks"
   grey: "2–3 days → 2–6 hours"
6  bold: "/wrap-up closes the loop"
   grey: "Jira updated · knowledge captured · graph refreshed"

COLUMN 3 — "Tools in Use" (dark green header):
5 white cards, each with colored left stripe (4px), tool name (bold, colored), description (grey):
  Green stripe — Claude Code: "20 skills · memory · multi-agent · Team environment AI"
  Charcoal stripe — GitHub Copilot: "Line completion · inline chat · Cross-model review"
  Blue stripe — NR MCP: "Live logs · metrics · traces · Diagnose without leaving chat"
  Teal stripe — Jira + Confluence: "Auto-updated every session"
  Purple stripe — Code Graph: "28 tools · blast radius · Impact analysis before coding"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 04
> Upload: slide_04.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_04.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header bar
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"System Architecture  —  How It All Connects Under One Environment"

BODY (fills entire area below header):
Reproduce the architecture diagram from the attached image at maximum size.
Preserve EVERY detail: all text labels, arrows, boxes, colors, sections exactly as shown.
Do not simplify, summarize, or redesign the diagram itself — only improve visual polish.

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 05
> Upload: slide_05.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_05.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header | Phase boxes in green/charcoal/blue/purple/teal
• Timing rows: light red bg (#FFF0F0) for Before | light green bg (#F0FBF5) for After
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Full AI-Led Development Lifecycle  —  Time Savings at Every Phase"

10 PHASE BOXES in a horizontal flow (left to right) with arrow connectors:
Each box shows: phase number (top-left, small), phase name (center, bold white), who does it (bottom, small)

01 — Requirement    | Manager / PM        | fill: #1F2937 charcoal
02 — Spec & Plan    | AI-assisted         | fill: #00AC69 green
03 — Architect      | AI + Graph          | fill: #006B40 dark green
04 — Build          | Task & volume dep.  | fill: #00AC69 green
05 — Review         | 5-layer AI+Human    | fill: #006B40 dark green
06 — Test & Gate    | AI automated        | fill: #00AC69 green
07 — Deploy         | Human initiates     | fill: #1F2937 charcoal
08 — Monitor        | NR MCP (AI)         | fill: #0052CC blue
09 — Document       | AI auto-update      | fill: #068290 teal
10 — Learn          | Golden patterns     | fill: #7C3AED purple

BELOW EACH PHASE BOX — two small timing rows (show only where values exist, skip where "—"):
Before row (light red bg, red text):
  02=4–6h | 03=2–4d | 04=2–3d | 08=1–10h | 09=manual
After row (light green bg, dark green text):
  02=20m–1h | 03=1–2d | 04=2–6h | 08=0–20m | 09=auto | 10=auto

Side labels: "Before:" in red | "After:" in dark green (left of rows)

BOTTOM FULL-WIDTH GREEN BANNER (#00AC69, white bold text):
"Confirmed by engineer  ·  Spec+Arch+Build: days → hours  ·  Alert diagnosis: hours → 0–20 min  ·  Overall: 8–12×"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 06
> Upload: slide_06.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_06.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Before card: white bg, red (#E53E3E) top bar | After card: #F0FBF5 light green bg, #00AC69 border
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Faster Development  —  Days Became Hours"

TOP HALF — BEFORE / AFTER HERO COMPARISON:

BEFORE card (left, white bg, thin red top bar):
  Label "BEFORE" (small, grey)
  Hero number: 2–3 DAYS  (#E53E3E red, ~64pt bold, centered)
  Description: "Per development ticket — regardless of complexity
  Context rebuilt from scratch every time"

  ──→ (large green arrow between cards)

AFTER card (right, #F0FBF5 bg, #00AC69 green border + top bar):
  Label "AFTER" (small, dark green)
  Hero number: 2–6 HOURS  (#00AC69 green, ~58pt bold, centered)
  Description: "Task & volume dependent
  Full context auto-loaded · skills auto-trigger · graph aware"

BOTTOM HALF — THREE OUTCOME CARDS (equal width, each with green top bar):
Card 1: "Spec & Plan  4–6h → 20m–1h"
  grey: "AI assists planning from existing codebase patterns — not from scratch"

Card 2: "Architecture  2–4d → 1–2d"
  grey: "Code graph shows impact + CDD & Confluence auto-updated"

Card 3: "Context always ready"
  grey: "Memory + graph auto-load. No archaeology every session"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 07
> Upload: slide_07.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_07.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Orchestrator bar: #1F2937 charcoal | Agent cards: green shades
• Right panel: light grey bg
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"/avengers — Five AI Engineers Working in Parallel on One Task"
Sub-text (grey, below header): "Tasks that take one engineer one full day, completed in under 2 hours:"

LEFT SECTION (65% width):

ORCHESTRATOR BAR (full-width, #1F2937 charcoal bg, white text):
"Orchestrator  (Opus model — plans, routes, validates, shuts down)"

4 AGENT CARDS below (side by side, green shades):
  Planner (#006B40 dark green): "Researches codebase → implementation plan"
  Coder ×N (#00AC69 green): "Parallel code writing, verifies build passes"
  Code Reviewer (#00AC69 green): "Code standards + security checks"
  Validator (#006B40 dark green): "Tests + impact analysis before any merge"

4 NUMBERED STEPS (alternating #F0FBF5 / white rows):
  1. "Orchestrator reads spec → spawns Planner + Coders simultaneously"
  2. "Each agent works on an independent file — zero waiting"
  3. "Reviewer + Validator run in parallel on all output"
  4. "Human sees a single clean PR to approve"

RIGHT PANEL (35% width, light grey bg):
  1 DAY    (large ~54pt, #E53E3E red, centered)
    ↓      (green arrow)
  2 HOURS  (large ~54pt, #00AC69 green, centered)

  "Airflow DAG + dbt model + NR alert — all in parallel"
  Bold dark green: "Engineer reviews 1 PR instead of 5 files"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 08
> Upload: slide_08.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_08.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Before panel: white bg, red top bar | After panel: #F0FBF5 light green, #00AC69 border
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Incident Investigation  —  AI Queries New Relic Directly, Instantly"

SIDE-BY-SIDE PANELS (with green arrow → between them):

BEFORE PANEL (left, white bg, thin #E53E3E red top bar):
  Label "BEFORE — Manual hunt" (bold)
  Hero: 2–3 HOURS  (#E53E3E red, ~56pt bold, centered)
  "Log in to NR UI · navigate to entity · scroll logs
  switch tabs · compare charts · Slack teammates"
  ─── thin divider ───
  Red italic text: "Form hypothesis → test → repeat → still uncertain
  Customer impact growing every minute"

AFTER PANEL (right, #F0FBF5 bg, #00AC69 border + top bar):
  Label "AFTER — AI-powered diagnosis" (bold, dark green)
  Hero: 0–20 MIN  (#00AC69 green, ~56pt bold, centered)
  "Claude queries New Relic, returns structured analysis"
  ─── thin green divider ───
  Dark green: "Alert data · affected services · root cause — fix scoped immediately"
  Bold: "12 New Relic tools · Jira auto-updated · root cause in minutes"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 09
> Upload: slide_09.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_09.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | Full-width #00AC69 hero banner at top
• Cards with accent stripes | Metric cards at bottom
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
TOP HERO BANNER (full-width, #00AC69 bg, white bold text, ~22pt):
"We see the full impact of every change  BEFORE  it touches production."

MIDDLE — BEFORE / AFTER SCENARIO CARDS (side by side):
BEFORE card (left, white bg, thin #E53E3E red top stripe):
  "⚠  Before: Invisible blast radius"  (bold, red)
  "Engineer changes a pipeline file.
  Deploys. A downstream consumer breaks silently.
  5-day incident — all from one undetected dependency."  (grey)

  ──→  green arrow between cards

AFTER card (right, #F0FBF5 bg, #00AC69 green border):
  "✅  After: Instant clarity"  (bold, dark green)
  "Impact analysis runs before coding.
  Sees 3 callers, 1 downstream consumer.
  Fix scoped. Ships confidently. Zero incident."  (dark text)

BOTTOM ROW — 4 METRIC CARDS (equal width, each with colored top bar):
Card 1 (#E53E3E top bar): "~1 sprint/qtr"  grey: "absorbed in surprise rework — before"
Card 2 (#00AC69 top bar): "< 1 day"        grey: "rework after impact-aware development"
Card 3 (#006B40 top bar): "0 blind deploys" grey: "every change impact-checked first"
Card 4 (#006B40 top bar): "Auto-updates"   grey: "dependency map rebuilt on every file save"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 10
> Upload: slide_10.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_10.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Flow arrows: green | Jira column: #0052CC blue header | Confluence column: #068290 teal header
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Documentation That Writes Itself  —  Jira & Confluence Always Up to Date"

TOP FLOW (5 boxes left to right, connected by → arrows):
  [Work session completes]  →  [/wrap-up fires (~30s)]  →  [Claude drafts summary]  →  [Jira ticket auto-updated]  →  [Confluence published]
  Colors: white | #E8F8F1 | #E8F8F1 | #0052CC blue (white text) | #068290 teal (white text)

TWO COLUMNS BELOW:

JIRA COLUMN (left, #0052CC blue header, white text):
Title: "Jira — What gets auto-updated"
4 rows alternating light/white:
  Status     | "In Review → Done  ·  automatically"
  Comment    | "What was done + decisions made"
  Worklog    | "Time logged from session duration"
  Links      | "Commits linked via branch name"

CONFLUENCE COLUMN (right, #068290 teal header, white text):
Title: "Confluence — What gets published"
4 rows:
  Architecture | "Decisions logged after every session"
  Postmortem   | "Incident page auto-created on wrap-up"
  Release      | "Notes from git history — auto-versioned"
  Runbooks     | "Updated as team learns new patterns"

BOTTOM BOLD TEXT (centered, large, #1F2937):
"Zero manual effort.  Every session documented.  Every time."

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

# ════════════════════════════════════════════════════
# BATCH 2 — Upload slide_11.png through slide_17.png
# ════════════════════════════════════════════════════

---

## SLIDE 11
> Upload: slide_11.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_11.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• Full dark navy #0D0D24 background (this is a hero/impact slide)
• Layer stripes: green | dark green | purple
• White text on dark | Green accent text
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
TITLE (large, white, centered, ~36pt bold):
"Knowledge That Compounds"

SUBTITLE (green, italic, centered, ~18pt):
"Every session makes every future session smarter — knowledge never leaves the team"

THREE HORIZONTAL LAYERS (stacked, each is a dark panel with colored left stripe + small badge chip):

LAYER 1 (left stripe: #00AC69 green, badge: "ALWAYS LOADED"):
  Title (white, bold): "Session memory — auto-loads at every session start"
  Body (grey): "Active priorities + recent lessons + architecture summary loaded automatically. No manual setup. Zero tokens wasted."

LAYER 2 (left stripe: #006B40 dark green, badge: "PULL ON DEMAND"):
  Title (white, bold): "Team knowledge — retrieved only when relevant"
  Body (grey): "Patterns · architecture decisions · session history · past plans. Fetched on demand — only what's needed, when it's needed."

LAYER 3 (left stripe: #7C3AED purple, badge: "REPLAYABLE WINS"):
  Title (white, bold): "Validated fixes — saved as reusable templates"
  Body (grey): "After a confirmed fix: the steps are captured and indexed. Next time the same problem appears, the proven solution loads instantly."

BOTTOM GREEN BANNER (#00AC69, white bold text):
"Every session: team knowledge grows.  Every fix: the next one is faster.  The system gets smarter, not staler."

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 12
> Upload: slide_12.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_12.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Hero numbers: very large (76–80pt), colored, centered in cards
• Secondary stats: clean row with large green values
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"The Results  —  Numbers the Team Has Measured"

4 HERO CARDS (side by side, equal width, each with colored top bar, white bg):

Card 1 (top bar: #00AC69 green):
  Hero: 8–12×  (#00AC69, ~80pt bold, centered)
  Label: "overall productivity for DE tasks"  (grey, centered)

Card 2 (top bar: #00D084 bright green):
  Hero: 2–6h  (#00D084, ~80pt bold, centered)
  Label: "dev ticket vs 2–3 days before"  (grey, centered)

Card 3 (top bar: #0052CC blue):
  Hero: 0–20m  (#0052CC, ~80pt bold, centered)
  Label: "Alert issue diagnosis vs 1–10 hours before"  (grey, centered)

Card 4 (top bar: #006B40 dark green):
  Hero: 25+ SP  (#006B40, ~80pt bold, centered)
  Label: "sprint capacity + adhoc on top"  (grey, centered)

SECONDARY STATS BAR (light grey bg):
  Label "More measurements" (bold grey, left-aligned)
  4 stats side by side (large green value + small grey label below each):
    "5–15 min"       | "context reset after absence (vs hours/days before)"
    "3–5h"           | "new pipeline (full cycle) vs 2–4 days before"
    "4–6h → 20m–1h" | "spec & plan phase"
    "2–4d → 1–2d"   | "architecture + CDD + Confluence"

BOTTOM GREEN BANNER (#00AC69, white bold text):
"8–12× overall for DE tasks  ·  All metrics reported directly by Ingestion Team engineers"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 13
> Upload: slide_13.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_13.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Table: 3 columns | Alternating row colors | Before column grey | After column bold dark green
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Before & After  —  Ingestion Team  ·  3 Repos  ·  3 Months"

3-COLUMN TABLE:

Column headers:
  Col 1 (#F3F4F6 light grey bg): "What We Measured"  (bold)
  Col 2 (#1F2937 charcoal bg, white): "Before"  (bold, centered)
  Col 3 (#00AC69 green bg, white): "After (AI-Led)"  (bold, centered)

9 DATA ROWS (alternating #F3F4F6 / white):
  Spec & Plan              | 4–6 hours              | 20 min – 1 hour  ✅
  Architecture + CDD       | 2–4 days               | 1–2 days  ✅
  Development ticket       | 2–3 days               | 2–6 hours (task-dependent)  ✅
  New pipeline (full cycle)| 2–4 days               | 3–5 hours  ✅
  Alert issue diagnosis    | 30 min – 3 hours       | 0–20 minutes (NR MCP)  ✅
  Context after absence    | Hours / days           | 5–15 min via /bootstrap  ✅
  Sprint throughput        | 25 SP (at capacity)    | 25 SP + additional + adhoc  ✅
  Documentation effort     | Manual, often skipped  | Automatic via /wrap-up  ✅
  Code review layers       | Manual review only     | CC Opus + Copilot GPT (blind spots) + agents + human  ✅

Col 1 text: bold dark | Col 2 text: grey | Col 3 text: bold #006B40 dark green

BOTTOM NOTE (small, centered, grey):
"✅ = confirmed by Ingestion Team engineers  ·  om-airflow-dags  ·  spark-kafka-apps  ·  tf-dataos-new-relic"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 14
> Upload: slide_14.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_14.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Gates 1,2,4,5: white bg, charcoal left block | Gate 3: #F0FBF5 bg, #00AC69 green border + left block (highlighted)
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"AI Does the Work.  Humans Stay in Control.  Always."

5 GATE ROWS (full width, equal height):

Gate 1 (white bg, #1F2937 charcoal left block):
  Circle number: 1  |  Bold: "Requirements"  |  Grey: "Human writes the spec — AI reads it, asks clarifying questions"

Gate 2 (white bg, #1F2937 charcoal left block):
  Circle number: 2  |  Bold: "Architecture"  |  Grey: "Human approves the implementation plan — before a line is written"

Gate 3 ★ HIGHLIGHTED (#F0FBF5 bg, #00AC69 green border all sides, #00AC69 left block):
  Circle number: 3 (green bg)  |  Bold: "Security Review"  |  Grey: "AI flags every security vulnerability — any critical issue blocks the pipeline"

Gate 4 (white bg, #1F2937 charcoal left block):
  Circle number: 4  |  Bold: "PR Merge"  |  Grey: "Human reviews every PR — agent output treated like any other code"

Gate 5 (white bg, #1F2937 charcoal left block):
  Circle number: 5  |  Bold: "Deploy"  |  Grey: "Human initiates the deploy — AI writes release notes + monitors"

BOTTOM NOTE ROW (light grey bg, italic grey centered text):
"Agent PRs treated identically to human PRs — same review, same standards, same gates."

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 15
> Upload: slide_15.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_15.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• White background | #00AC69 green header
• Step cards: white bg, colored time-badge at top
• Compounding effect: 3 progressive cards (light → medium green → solid green)
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
HEADER BAR (#00AC69, white bold text):
"Getting Started  —  From Zero to Productive in 4 Steps"

4 STEP CARDS (side by side, equal width, white bg):

Step 1 — time badge "15 MIN" (#00AC69 green badge, white text):
  Title: "Install & Setup"  (bold #00AC69)
  When: "One-time per engineer"  (italic grey)
  Body: "Claude Code + MCP servers + Budget dial
  Multi-orchestration + hooks + 20 skills
  Fully automated — one script."

Step 2 — time badge "5 MIN" (#006B40 dark green badge):
  Title: "Bootstrap New Repo"  (bold #006B40)
  When: "First visit to any repo"  (italic grey)
  Body: "Detects your stack, seeds team memory,
  builds codebase graph, wires all MCPs.
  Runs once — context ready forever."

Step 3 — time badge "ALWAYS" (#00AC69 green badge):
  Title: "AI-Led Development"  (bold #00AC69)
  When: "Single agent or multi agent"  (italic grey)
  Body: "Single task: Claude Code works alongside you.
  Complex task: multi-agent system spawns parallel specialists.
  Copilot handles lines. Claude handles investigations."

Step 4 — time badge "30 SEC" (#006B40 dark green badge):
  Title: "Wrap-Up"  (bold #006B40)
  When: "Every session end"  (italic grey)
  Body: "Jira auto-updated · lessons captured
  Knowledge persisted · graph refreshed
  The habit that makes everything compound."

DIVIDER LINE + LABEL "The Compounding Effect" (#00AC69 bold)

3 PROGRESSIVE CARDS (bottom row):
  Day 1    (light grey bg, dark text): "Full codebase context ready. Development tickets: days → hours."
  Month 1  (medium #D0F0E2 green bg, #006B40 text): "Lessons accumulate. Patterns reused. Alert diagnosis: hours → 0–20 min."
  Month 3+ (solid #00AC69 bg, white text, bold): "Knowledge never leaves the team. 8–12× productivity — sustained."

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 16
> Upload: slide_16.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_16.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• Full dark navy #0D0D24 background (hero/closing slide)
• Ask cards: slightly lighter navy panels, #00AC69 green left stripe
• Right metrics panel: even darker navy
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
SPLIT: Left 75% (asks) | Right 25% (metrics panel)

TOP LEFT:
  New Relic logo (large, top-left)
  Title: "What We're Asking"  (white, ~34pt bold)
  Thin #00AC69 horizontal divider line

3 ASK CARDS (dark navy panels, #00AC69 green left stripe, full width of left section):

Card 1:
  Label (green bold): "Support adoption"
  Body (white): "Drive AI-led workflows across all Data Engineering & Management in DTM."

Card 2:
  Label (green bold): "Allocate time"
  Body (white): "Support the daily wrap-up habit — 30 seconds per session. Knowledge compounds automatically."

Card 3:
  Label (green bold): "Endorse the model"
  Body (white): "Establish this as the standard template for all DE teams at New Relic."

BOTTOM LEFT (grey, ~28pt):
"Thank You  ·  Questions?"

RIGHT METRICS PANEL (darker navy, centered content):
4 stacked metrics (large green value + small italic grey label):
  8–12× / "Productivity"
  2–6h  / "Dev ticket"
  0–20m / "Alert diagnosis"
  25+ SP / "Sprint capacity"

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

## SLIDE 17
> Upload: slide_17.png — then paste this entire prompt

```
You are a world-class presentation designer creating a CEO-level executive slide deck for New Relic's DataOS Ingestion Team.

Redesign the attached slide (slide_17.png) into a stunning, modern, high-quality version.

━━━ OUTPUT REQUIREMENTS ━━━
• Resolution: 2752×1536px (16:9), PNG format
• Quality: print-quality, crisp vector-style text, no blur or compression artifacts
• Do NOT add any Gemini logo, Google watermark, AI-generated badge, or any platform branding anywhere
• The ONLY footer elements are: New Relic logo bottom-right + disclaimer text bottom-left

━━━ BRAND ━━━
• Full dark navy #0D0D24 background
• Thin #00AC69 lines top and bottom edge of slide (full width, 6px)
• All text centered
• New Relic logo bottom-right | Disclaimer bottom-left

━━━ SLIDE LAYOUT ━━━
TOP EDGE: Thin #00AC69 line (full width)

CENTER (vertically and horizontally centered):
  "Thank You"  (white, ~72pt, clean weight, centered)
  "Questions?"  (grey, ~28pt, italic, centered, below title)
  Thin #00AC69 horizontal divider (60% width, centered, between title and questions)

BOTTOM EDGE: Thin #00AC69 line (full width)

FOOTER: NR logo bottom-right + disclaimer bottom-left
```

---

# HOW TO USE — QUICK REFERENCE

| Batch | Upload these files | Slides |
|---|---|---|
| Batch 1 | slide_01.png → slide_10.png | 01 to 10 |
| Batch 2 | slide_11.png → slide_17.png | 11 to 17 |

**For each slide:**
1. Go to gemini.google.com
2. Upload the single reference image for that slide
3. Copy the entire prompt block (between the triple backticks)
4. Paste and send
5. Download the output → save as `slide_XX.png` in `ingestion_ai/Updated/`
