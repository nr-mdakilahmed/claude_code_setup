# Gemini Redesign Prompts — DataOS Ingestion AI-Led Development Deck
# 17 individual slide prompts · Split into 2 batches (10 + 7)

---

## BRAND RULES — Copy this block into EVERY prompt

```
BRAND RULES (apply to every slide):
- Primary green: #00AC69 | Dark navy: #0D0D24 | Charcoal: #1F2937
- White backgrounds for content slides | Dark navy for hero/impact slides
- New Relic logo (green hexagon + "new relic." wordmark) — bottom-right, every slide
- Disclaimer bottom-left every slide (small grey font):
  "© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution."
- Typography: modern sans-serif (Inter or similar) | Bold headers | Clean hierarchy
- Slide size: 1920×1080px (16:9)
- Style: world-class executive presentation — hero numbers dominate, generous white space,
  full-width green header bars, card-based layouts, no bullet lists
- Output: single PNG image, named slide_01 (or matching slide number)
- Do NOT change any text, number, or metric — reproduce content exactly as described
```

---

## BATCH 1 — Upload slides 01–10 together, then use each prompt individually

---

### SLIDE 01 PROMPT
*(attach slide_01.png)*

```
Redesign this slide as slide_01.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: Dark navy full background. Left half: content. Right half: darker navy panel.

LEFT SIDE:
- New Relic logo top-left (large, 2")
- "Ingestion Team" — very large (38pt), white, bold
- "AI-Led Development" — very large (34pt), #00AC69 green, bold
- "Environment" — very large (34pt), white, bold
- Thin green divider line
- Italic grey subtitle: "Claude Code  +  GitHub Copilot  +  New Relic MCP"

RIGHT PANEL (darker navy):
Five horizontal chips, each with green left stripe, icon + text:
🚀  "8–12×  productivity for DE tasks"
⏱  "2–3 days → 2–6 hours per ticket"
🔍  "0–20 min alert issue diagnosis"
⚡  "5 parallel agents with /avengers"
📦  "Knowledge that compounds daily"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 02 PROMPT
*(attach slide_02.png)*

```
Redesign this slide as slide_02.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Full-width green header bar. 2×2 grid of cards.

HEADER: "The Challenge — Four Real Pains the DataOS Ingestion Team Was Living With"

FOUR CARDS (each has: top accent stripe, icon+title, large hero number, divider, grey description):

Card 1 — top-left (RED #E53E3E accent):
🕐  "Slow Development Tickets"
Hero: 2–3 DAYS (red, ~48pt bold)
"per ticket — regardless of complexity or volume"

Card 2 — top-right (AMBER #FFC107 accent):
🔍  "Pipeline Debugging"
Hero: 30 MIN–3 HRS (amber, ~44pt bold)
"backtracking alert issues one by one manually"

Card 3 — bottom-left (CHARCOAL #1F2937 accent):
💥  "Hidden Blast Radius"
Hero: 5-DAY (charcoal, ~48pt bold)
"incident caused by a change no one knew would break"

Card 4 — bottom-right (CHARCOAL #1F2937 accent):
🗂  "No Historical Context"
Hero: HOURS–DAYS (charcoal, ~44pt bold)
"re-discovering repo structure and past decisions every time someone joined, left, or came back"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 03 PROMPT
*(attach slide_03.png)*

```
Redesign this slide as slide_03.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. Three equal columns.

HEADER: "DataOS Ingestion  —  How We Run AI-Led Development Today"

COLUMN 1 — "What We Own" (dark charcoal header):
Vertical data flow diagram:
  Label "DATA SOURCES" (small, grey)
  Box: "Billing Platform · Kafka · SFDC · Zuora · etc."
  Green arrow ↓
  Green filled box: "INGESTION — WE OWN THIS" + "FiveTran · Kafka · NRDB · Spark · Custom Pipelines"
  Green arrow ↓
  Label "DOWNSTREAM ZONE 2" (small, grey)
  Box: "Consumer · Data Lake · Dashboard"

COLUMN 2 — "Daily Workflow" (green header):
6 numbered steps (alternating light green / white rows):
1  "Start with full context" — "Memory + codebase graph auto-load in seconds"
2  "Copilot: lines + blind spot check" — "Autocomplete in IDE · cross-model review catches what Claude misses"
3  "Skills trigger automatically" — "/airflow · /pyspark · /nrql · /terraform · /sql"
4  "Incidents diagnosed via NR MCP" — "30 min–3 hrs → 0–20 min for alert issues"
5  "/avengers for big tasks" — "5 parallel agents — 2–3 days → 2–6 hours"
6  "/wrap-up closes the loop" — "Jira updated · knowledge captured · graph refreshed"

COLUMN 3 — "Tools in Use" (dark green header):
5 tool cards (white bg, colored left stripe):
Claude Code (green stripe): "20 skills · memory · /avengers · Team environment AI"
GitHub Copilot (charcoal stripe): "Line completion · inline chat · Cross-model review (covers Claude blind spots)"
NR MCP (blue stripe): "Live logs · metrics · traces · Diagnose without leaving chat"
Jira + Confluence (teal stripe): "Tickets + docs auto-updated · on every /wrap-up"
Code Graph (purple stripe): "28 tools · blast radius · Impact analysis before coding"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 04 PROMPT
*(attach slide_04.png)*

```
Redesign this slide as slide_04.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Full-width green header. Body = full-size image.

HEADER: "System Architecture  —  How It All Connects Under One Environment"

BODY: The architecture diagram from the attached image must be reproduced at maximum size,
filling the entire slide body below the header. Preserve every label, arrow, box, and color
from the original diagram exactly. Do not simplify or alter it.

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 05 PROMPT
*(attach slide_05.png)*

```
Redesign this slide as slide_05.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. 10 phase boxes in horizontal flow + timing rows below.

HEADER: "Full AI-Led Development Lifecycle  —  Time Savings at Every Phase"

10 PHASE BOXES (left to right, each: phase number, phase name, who does it):
01 Requirement — Manager/PM — charcoal fill
02 Spec & Plan — AI-assisted — green fill
03 Architect — AI + Graph — dark green fill
04 Build — Task & volume dep. — green fill
05 Review — 5-layer AI+Human — dark green fill
06 Test & Gate — AI automated — green fill
07 Deploy — Human initiates — charcoal fill
08 Monitor — NR MCP (AI) — blue fill
09 Document — AI auto-update — teal fill
10 Learn — Golden patterns — purple fill

TIMING ROWS below each box (skip row if value is "—"):
Before row (light red bg, red text): 02=4–6h, 03=2–4d, 04=2–3d, 08=1–10h, 09=manual
After row (light green bg, green text): 02=20m–1h, 03=1–2d, 04=2–6h, 08=0–20m, 09=auto, 10=auto

Left labels: "Before:" (red) and "After:" (green)

BOTTOM GREEN BANNER:
"Confirmed by engineer · Spec+Arch+Build: days → hours · Alert diagnosis: hours → 0–20 min · Overall: 8–12×"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 06 PROMPT
*(attach slide_06.png)*

```
Redesign this slide as slide_06.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. Before/After hero split top half. 3 cards bottom half.

HEADER: "Faster Development  —  Days Became Hours"

BEFORE panel (left, white bg, red top bar):
Label: BEFORE
Hero number: 2–3 DAYS (red, ~64pt bold, centered)
Text: "Per development ticket — regardless of complexity. Context rebuilt from scratch every time."

Arrow → between panels

AFTER panel (right, light green bg, green border + top bar):
Label: AFTER
Hero number: 2–6 HOURS (green, ~58pt bold, centered)
Text: "Task & volume dependent. Full context auto-loaded · skills auto-trigger · graph aware"

THREE OUTCOME CARDS (bottom, equal width, green top bar each):
1. "Spec & Plan 4–6h → 20m–1h" — "AI assists planning from existing codebase patterns — not from scratch"
2. "Architecture 2–4d → 1–2d" — "Code graph shows impact + CDD & Confluence auto-updated"
3. "Context always ready" — "Memory + graph auto-load. No archaeology every session"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 07 PROMPT
*(attach slide_07.png)*

```
Redesign this slide as slide_07.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. Left: orchestration diagram. Right: hero metric.

HEADER: "/avengers — Five AI Engineers Working in Parallel on One Task"
Subtext (grey): "Tasks that take one engineer one full day, completed in under 2 hours:"

ORCHESTRATOR BAR (full-width charcoal):
"Orchestrator  (Opus model — plans, routes, validates, shuts down)"

4 AGENT CARDS (green shades, side by side):
Planner (dark green): "Researches codebase → implementation plan"
Coder ×N (green): "Parallel code writing, verifies build passes"
Code Reviewer (green): "Code standards + security checks"
Validator (dark green): "Tests + impact analysis before any merge"

RIGHT HERO PANEL (light grey):
1 DAY (red, ~54pt) ↓ 2 HOURS (green, ~54pt)
"Airflow DAG + dbt model + NR alert — all in parallel"
Bold: "Engineer reviews 1 PR instead of 5 files"

4 PROCESS STEPS (numbered, alternating light green / white):
1. "Orchestrator reads spec → spawns Planner + Coders simultaneously"
2. "Each agent works on an independent file — zero waiting"
3. "Reviewer + Validator run in parallel on all output"
4. "Human sees a single clean PR to approve"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 08 PROMPT
*(attach slide_08.png)*

```
Redesign this slide as slide_08.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. Left panel: before. Right panel: after. Arrow between.

HEADER: "Incident Investigation  —  AI Queries New Relic Directly, Instantly"

BEFORE panel (left, white bg, red top bar):
Label: BEFORE — Manual hunt
Hero: 2–3 HOURS (red, ~56pt bold, centered)
"Log in to NR UI · navigate to entity · scroll logs · switch tabs · compare charts · Slack teammates"
Divider line
Red text: "Form hypothesis → test → repeat → still uncertain. Customer impact growing every minute."

Arrow → between panels (green)

AFTER panel (right, light green bg, green border + top bar):
Label: AFTER — AI-powered diagnosis
Hero: 0–20 MIN (green, ~56pt bold, centered)
"Claude queries NR, returns structured analysis"
Divider line (green)
Dark green: "Alert data · affected services · root cause — fix scoped immediately"
Bold: "12 New Relic tools · Jira auto-updated · root cause in minutes"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 09 PROMPT
*(attach slide_09.png)*

```
Redesign this slide as slide_09.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Full-width green hero banner. Before/after cards. 4 metric cards bottom.

GREEN HERO BANNER (top, white text, bold):
"We see the full impact of every change  BEFORE  it touches production."

BEFORE card (left, white bg, red top bar):
"⚠  Before: Invisible blast radius"
"Engineer changes a pipeline file. Deploys. A downstream consumer breaks silently.
5-day incident — all from one undetected dependency."

Arrow → (green)

AFTER card (right, light green bg, green border):
"✅  After: Instant clarity"
"Impact analysis runs before coding. Sees 3 callers, 1 downstream consumer.
Fix scoped. Ships confidently. Zero incident."

4 METRIC CARDS (bottom row, equal width):
1. "~1 sprint/qtr" (red) — "absorbed in surprise rework — before"
2. "< 1 day" (green) — "rework after impact-aware development"
3. "0 blind deploys" (dark green) — "every change impact-checked first"
4. "Auto-updates" (dark green) — "dependency map rebuilt on every file save"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 10 PROMPT
*(attach slide_10.png)*

```
Redesign this slide as slide_10.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. Flow diagram top. Two columns below.

HEADER: "Documentation That Writes Itself  —  Jira & Confluence Always Up to Date"

TOP FLOW (5 boxes with arrows between):
"Work session completes" → "/wrap-up fires (~30s)" → "Claude drafts summary" → "Jira ticket auto-updated" → "Confluence published"
(Color: white → light green → light green → blue → teal)

LEFT COLUMN — "Jira — What gets auto-updated" (blue header, white text):
4 rows (alternating light/white):
Status: "In Review → Done  ·  automatically"
Comment: "What was done + decisions made"
Worklog: "Time logged from session duration"
Links: "Commits linked via branch name"

RIGHT COLUMN — "Confluence — What gets published" (teal header, white text):
4 rows:
Architecture: "Decisions logged after every session"
Postmortem: "Incident page auto-created on wrap-up"
Release: "Notes from git history — auto-versioned"
Runbooks: "Updated as team learns new patterns"

BOTTOM BOLD TEXT (centered, large):
"Zero manual effort.  Every session documented.  Every time."

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

## BATCH 2 — Upload slides 11–17 together, then use each prompt individually

---

### SLIDE 11 PROMPT
*(attach slide_11.png)*

```
Redesign this slide as slide_11.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: Dark navy (#0D0D24) full background. No header bar — title centered at top.

TITLE (white, large, centered): "Knowledge That Compounds"
SUBTITLE (green, italic, centered): "Every session makes every future session smarter — knowledge never leaves the team"

THREE HORIZONTAL LAYERS (dark panels, each with colored left stripe + small badge):

Layer 1 (GREEN stripe + badge):
Badge: "ALWAYS LOADED"
Title: "Session memory — auto-loads at every session start"
Desc (grey): "Active priorities + recent lessons + architecture summary loaded automatically. No manual setup. Zero tokens wasted."

Layer 2 (DARK GREEN stripe + badge):
Badge: "PULL ON DEMAND"
Title: "Team knowledge — retrieved only when relevant"
Desc (grey): "Patterns · architecture decisions · session history · past plans. Fetched on demand — only what's needed, when it's needed."

Layer 3 (PURPLE stripe + badge):
Badge: "REPLAYABLE WINS"
Title: "Validated fixes — saved as reusable templates"
Desc (grey): "After a confirmed fix: the steps are captured and indexed. Next time the same problem appears, the proven solution loads instantly."

BOTTOM GREEN BANNER:
"Every session: team knowledge grows.  Every fix: the next one is faster.  The system gets smarter, not staler."

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 12 PROMPT
*(attach slide_12.png)*

```
Redesign this slide as slide_12.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. 4 large hero cards. Secondary stats bar. Green banner.

HEADER: "The Results  —  Numbers the Team Has Measured"

4 HERO NUMBER CARDS (side by side, each with colored top bar):
1. 8–12× (green) — "overall productivity for DE tasks"
2. 2–6h (bright green) — "dev ticket vs 2–3 days before"
3. 0–20m (blue) — "Alert issue diagnosis vs 1–10 hours before"
4. 25+ SP (dark green) — "sprint capacity + adhoc on top"

SECONDARY STATS BAR (light grey bg):
Label: "More measurements" (bold grey)
4 stats side by side:
"5–15 min" — "context reset after absence (vs hours/days before)"
"3–5h" — "new pipeline (full cycle) vs 2–4 days before"
"4–6h → 20m–1h" — "spec & plan phase"
"2–4d → 1–2d" — "architecture + CDD + Confluence"

BOTTOM GREEN BANNER:
"8–12× overall for DE tasks  ·  All metrics reported directly by Ingestion Team engineers"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 13 PROMPT
*(attach slide_13.png)*

```
Redesign this slide as slide_13.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. 3-column comparison table.

HEADER: "Before & After  —  Ingestion Team  ·  3 Repos  ·  3 Months"

TABLE — 3 columns:
Col 1 header (light grey bg): "What We Measured"
Col 2 header (charcoal bg, white): "Before"
Col 3 header (green bg, white): "After (AI-Led)"

9 DATA ROWS (alternating light grey / white):
1. Spec & Plan | 4–6 hours | 20 min – 1 hour ✅
2. Architecture + CDD | 2–4 days | 1–2 days ✅
3. Development ticket | 2–3 days | 2–6 hours (task-dependent) ✅
4. New pipeline (full cycle) | 2–4 days | 3–5 hours ✅
5. Alert issue diagnosis | 30 min – 3 hours | 0–20 minutes (NR MCP) ✅
6. Context after absence | Hours / days | 5–15 min via /bootstrap ✅
7. Sprint throughput | 25 SP (at capacity) | 25 SP + additional + adhoc ✅
8. Documentation effort | Manual, often skipped | Automatic via /wrap-up ✅
9. Code review layers | Manual review only | CC Opus + Copilot GPT (blind spots) + agents + human ✅

Before column: grey text | After column: bold, dark green text

FOOTER ROW (small, centered):
"✅ = confirmed by Ingestion Team engineers  ·  om-airflow-dags · spark-kafka-apps · tf-dataos-new-relic"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 14 PROMPT
*(attach slide_14.png)*

```
Redesign this slide as slide_14.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. 5 numbered gate rows.

HEADER: "AI Does the Work.  Humans Stay in Control.  Always."

5 GATE ROWS (full width, numbered, Gate 3 highlighted):

Gate 1 (white bg, charcoal left block):
Number circle: 1
Title bold: "Requirements"
Detail grey: "Human writes the spec — AI reads it, asks clarifying questions"

Gate 2 (white bg, charcoal left block):
Number circle: 2
Title bold: "Architecture"
Detail grey: "Human approves the implementation plan — before a line is written"

Gate 3 ★ HIGHLIGHTED (light green bg, GREEN border, green left block):
Number circle: 3 (green)
Title bold: "Security Review"
Detail grey: "AI flags every security vulnerability — any critical issue blocks the pipeline"

Gate 4 (white bg, charcoal left block):
Number circle: 4
Title bold: "PR Merge"
Detail grey: "Human reviews every PR — agent output treated like any other code"

Gate 5 (white bg, charcoal left block):
Number circle: 5
Title bold: "Deploy"
Detail grey: "Human initiates the deploy — AI writes release notes + monitors"

FOOTER ROW (light grey, italic, centered):
"Agent PRs treated identically to human PRs — same review, same standards, same gates."

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 15 PROMPT
*(attach slide_15.png)*

```
Redesign this slide as slide_15.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: White background. Green header. 4 step cards top. Compounding effect bottom.

HEADER: "Getting Started  —  From Zero to Productive in 4 Steps"

4 STEP CARDS (side by side, each with colored time badge at top):

Step 1 — Badge: 15 MIN (green):
"Install & Setup" — "One-time per engineer"
"Claude Code + MCP servers + Budget dial. Multi-orchestration + hooks + 20 skills. Fully automated — one script."

Step 2 — Badge: 5 MIN (dark green):
"Bootstrap New Repo" — "First visit to any repo"
"Detects your stack, seeds team memory, builds codebase graph, wires all MCPs. Runs once — context ready forever."

Step 3 — Badge: ALWAYS (green):
"AI-Led Development" — "Single agent or multi agent"
"Single task: Claude Code works alongside you. Complex task: /avengers spawns parallel agents. Copilot handles lines. Claude handles investigations."

Step 4 — Badge: 30 SEC (dark green):
"Wrap-Up" — "Every session end"
"Jira auto-updated · lessons captured. Knowledge persisted · graph refreshed. The habit that makes everything compound."

GREEN DIVIDER LINE + Label: "The Compounding Effect"

3 PROGRESSIVE CARDS (bottom, side by side):
Day 1 (light grey): "Full codebase context ready. Development tickets: days → hours."
Month 1 (medium green, dark green text): "Lessons accumulate. Patterns reused. Alert diagnosis: hours → 0–20 min."
Month 3+ (solid green, white text): "Knowledge never leaves the team. 8–12× productivity — sustained."

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 16 PROMPT
*(attach slide_16.png)*

```
Redesign this slide as slide_16.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: Dark navy (#0D0D24) background. Left: asks. Right: metrics panel.

TOP LEFT: New Relic logo (large)
TITLE (white, large, bold): "What We're Asking"
GREEN DIVIDER LINE (below title)

3 ASK CARDS (dark navy panels, green left stripe, full width to right edge of left section):

Card 1:
Label (green bold): "Support adoption"
Text (white): "Drive AI-led workflows across all Data Engineering & Management in DTM."

Card 2:
Label (green bold): "Allocate time"
Text (white): "Support the daily wrap-up habit — 30 seconds per session. Knowledge compounds automatically."

Card 3:
Label (green bold): "Endorse the model"
Text (white): "Establish this as the standard template for all DE teams at New Relic."

RIGHT METRICS PANEL (darker navy, 4 stats stacked):
8–12× / "Productivity"
2–6h / "Dev ticket"
0–20m / "Alert diagnosis"
25+ SP / "Sprint capacity"
(each: large green value, small italic grey label, centered)

BOTTOM LEFT (grey, large): "Thank You  ·  Questions?"

FOOTER: NR logo bottom-right + disclaimer bottom-left.
```

---

### SLIDE 17 PROMPT
*(attach slide_17.png)*

```
Redesign this slide as slide_17.png using the brand rules below.

[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display

LAYOUT: Dark navy (#0D0D24) full background. Centered content.

Green top border line (full width, 6px)
Green bottom border line (full width, 6px)

CENTER:
"Thank You" — very large (60pt+), white, centered, clean weight
"Questions?" — 26pt, italic, grey, centered

Green horizontal divider line (centered, 60% width)

FOOTER: NR logo bottom-right + disclaimer bottom-left (same as all slides).
```

---

## HOW TO USE

**Batch 1 (slides 01–10):**
1. Go to gemini.google.com
2. Upload: slide_01.png through slide_10.png (10 files)
3. Paste the BRAND RULES block once
4. Then paste SLIDE 01 PROMPT → get image → save as slide_01.png
5. Repeat for slides 02–10 (reference the correct attached image each time)

**Batch 2 (slides 11–17):**
1. New conversation in Gemini
2. Upload: slide_11.png through slide_17.png (7 files)
3. Paste BRAND RULES block once
4. Then paste SLIDE 11 PROMPT → get image → save as slide_11.png
5. Repeat for slides 12–17

**Tip:** In each prompt, replace `[PASTE BRAND RULES BLOCK HERE]

QUALITY REQUIREMENTS:
- Output must be 2752×1536px minimum (or 1920×1080px at 2× density) — high resolution, print quality
- Do NOT add any Gemini logo, Google watermark, AI generation notice, or any platform branding
- The ONLY logos on the slide are the New Relic logo (bottom-right) as specified
- Crisp vector-style text rendering — no blurry or compressed artifacts
- Professional presentation quality — suitable for CEO boardroom display` with the full brand rules block at the top of this file.
