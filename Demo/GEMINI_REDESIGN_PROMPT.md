# Gemini Redesign Prompt — DataOS Ingestion AI-Led Development Deck

Paste this prompt into Google Gemini, then attach all 17 slide images from the `ingestion_ai/` folder.

---

## PROMPT

I am attaching 17 slides (slide_01.png through slide_17.png) from an existing PowerPoint presentation. I need you to redesign all 17 slides into a **stunning, modern, executive-level presentation** while keeping every piece of content exactly as shown. Do not invent, add, or remove any content.

---

### BRAND REQUIREMENTS — NON-NEGOTIABLE

**Colors:**
- Primary green: `#00AC69` (New Relic green — headers, accents, highlights, CTAs)
- Dark navy: `#0D0D24` (hero/title slides background)
- Charcoal: `#1F2937` (dark section headers)
- White: `#FFFFFF` (slide backgrounds, text on dark)
- Light green: `#E8F8F1` (subtle background tint for cards)
- Body grey: `#6B7280` (secondary text)
- Border grey: `#E5E7EB` (card borders, dividers)

**Logo:** Every slide must show the **New Relic logo** (green hexagon + "new relic." wordmark) in the bottom-right corner, exactly as it appears in the current slides.

**Disclaimer:** Every slide must show this exact text in the bottom-left, small grey font:
`© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution.`

**Typography:** Modern sans-serif (Inter, Calibri, or similar). Bold headers. Clean hierarchy.

**Slide dimensions:** 16:9 widescreen (1920×1080px or equivalent).

---

### DESIGN DIRECTION

Make this look like a **world-class executive presentation** — the kind you'd see at a Google or Stripe all-hands. Specific guidance:

- Use **large hero numbers** (80–100pt) for key metrics — they should dominate the slide
- Use **generous white space** — don't crowd every pixel
- Use **full-width green header bars** on content slides
- Use **dark navy backgrounds** for impact slides (Title, Knowledge Compounds, Thank You)
- Use **card-based layouts** with subtle shadows and rounded corners
- Use **color-coded accents** (green stripe on left of cards for AI/after, red for before/pain)
- **Avoid bullet point lists** — use visual cards, flow diagrams, and icons instead
- Each slide should have **one dominant visual focal point** that a viewer sees in 3 seconds

---

### SLIDE-BY-SLIDE CONTENT (do not change any text, numbers, or facts)

---

#### SLIDE 01 — Title (dark navy background)
**Left side (white text on navy):**
- Logo top-left
- "Ingestion Team" (large, white, bold)
- "AI-Led Development" (large, green, bold)
- "Environment" (large, white, bold)
- Divider line (green)
- Subtitle (italic, grey): "Claude Code  +  GitHub Copilot  +  New Relic MCP"

**Right side (dark panel):**
Five outcome chips, each with icon + text:
1. 🚀  "8–12×  productivity for DE tasks"
2. ⏱  "2–3 days → 2–6 hours per ticket"
3. 🔍  "0–20 min alert issue diagnosis"
4. ⚡  "5 parallel agents with /avengers"
5. 📦  "Knowledge that compounds daily"

---

#### SLIDE 02 — The Challenge (white background, green header)
**Header:** "The Challenge — Four Real Pains the DataOS Ingestion Team Was Living With"

**Four cards in 2×2 grid, each with:**
- Top accent stripe (color per card)
- Icon + title
- Large hero number (bold, colored)
- Divider line
- Description text (grey)

Card 1 (red accent): 🕐 "Slow Development Tickets" — **2–3 DAYS** — "per ticket — regardless of complexity or volume"
Card 2 (amber accent): 🔍 "Pipeline Debugging" — **30 MIN–3 HRS** — "backtracking alert issues one by one manually"
Card 3 (charcoal accent): 💥 "Hidden Blast Radius" — **5-DAY** — "incident caused by a change no one knew would break"
Card 4 (charcoal accent): 🗂 "No Historical Context" — **HOURS–DAYS** — "re-discovering repo structure and past decisions every time someone joined, left, or came back"

---

#### SLIDE 03 — How We Work (white background, green header)
**Header:** "DataOS Ingestion  —  How We Run AI-Led Development Today"

**Three columns:**

**Column 1 — What We Own (dark header):**
Label: "DATA SOURCES" → boxes: "Billing Platform · Kafka · SFDC · Zuora · etc."
Arrow ↓
Green box: "INGESTION — WE OWN THIS" — "FiveTran · Kafka · NRDB · Spark · Custom Pipelines"
Arrow ↓
Label: "DOWNSTREAM ZONE 2" → boxes: "Consumer · Data Lake · Dashboard"

**Column 2 — Daily Workflow (green header):**
6 numbered steps:
1. "Start with full context" — "Memory + codebase graph auto-load in seconds"
2. "Copilot: lines + blind spot check" — "Autocomplete in IDE · cross-model review catches what Claude misses"
3. "Skills trigger automatically" — "/airflow · /pyspark · /nrql · /terraform · /sql"
4. "Incidents diagnosed via NR MCP" — "30 min–3 hrs → 0–20 min for alert issues"
5. "/avengers for big tasks" — "5 parallel agents — 2–3 days → 2–6 hours"
6. "/wrap-up closes the loop" — "Jira updated · knowledge captured · graph refreshed"

**Column 3 — Tools in Use (dark green header):**
5 tool cards with left color stripe:
- Claude Code (green): "20 skills · memory · /avengers · Team environment AI"
- GitHub Copilot (charcoal): "Line completion · inline chat · Cross-model review (covers Claude blind spots)"
- NR MCP (blue): "Live logs · metrics · traces · Diagnose without leaving chat"
- Jira + Confluence (teal): "Tickets + docs auto-updated · on every /wrap-up"
- Code Graph (purple): "28 tools · blast radius · Impact analysis before coding"

---

#### SLIDE 04 — System Architecture (white background, green header)
**Header:** "System Architecture  —  How It All Connects Under One Environment"

**Full-width image:** Display the architecture diagram image exactly as provided. This is a detailed technical diagram showing all components — preserve it at maximum size filling the slide body.

---

#### SLIDE 05 — Lifecycle (white background, green header)
**Header:** "Full AI-Led Development Lifecycle  —  Time Savings at Every Phase"

**10 phase boxes in a horizontal flow (left to right), each showing:**
- Phase number (01–10)
- Phase name
- Who does it

**Phase data (phase name / who / before / after):**
01. Requirement / Manager/PM / — / —
02. Spec & Plan / AI-assisted / 4–6h / 20m–1h
03. Architect / AI + Graph / 2–4d / 1–2d
04. Build / Task & volume dep. / 2–3d / 2–6h
05. Review / 5-layer AI+Human / — / —
06. Test & Gate / AI automated / — / —
07. Deploy / Human initiates / — / —
08. Monitor / NR MCP (AI) / 1–10h / 0–20m
09. Document / AI auto-update / manual / auto
10. Learn / Golden patterns / — / auto

Below each phase box: red row (Before time), green row (After time). Phases with "—" show no timing row.

**Bottom green banner:** "Confirmed by engineer · Spec+Arch+Build: days → hours · Alert diagnosis: hours → 0–20 min · Overall: 8–12×"

---

#### SLIDE 06 — Faster Development (white background, green header)
**Header:** "Faster Development  —  Days Became Hours"

**Left card (before — red accent):**
Label: BEFORE
Hero: **2–3 DAYS**
Text: "Per development ticket — regardless of complexity. Context rebuilt from scratch every time."

**Right card (after — green accent, light green background):**
Label: AFTER
Hero: **2–6 HOURS**
Text: "Task & volume dependent. Full context auto-loaded · skills auto-trigger · graph aware"

**Three outcome cards below:**
1. "Spec & Plan 4–6h → 20m–1h" — "AI assists planning from existing codebase patterns — not from scratch"
2. "Architecture 2–4d → 1–2d" — "Code graph shows impact + CDD & Confluence auto-updated"
3. "Context always ready" — "Memory + graph auto-load. No archaeology every session"

---

#### SLIDE 07 — Parallel Build (white background, green header)
**Header:** "/avengers — Five AI Engineers Working in Parallel on One Task"
**Subtext (grey):** "Tasks that take one engineer one full day, completed in under 2 hours:"

**Orchestrator bar (dark charcoal):**
"Orchestrator (Opus model — plans, routes, validates, shuts down)"

**4 agent cards (green shades):**
1. Planner — "Researches codebase → implementation plan"
2. Coder ×N — "Parallel code writing, verifies build passes"
3. Code Reviewer — "Code standards + security checks"
4. Validator — "Tests + impact analysis before any merge"

**Right panel (light grey):**
Hero: **1 DAY** (red) → **2 HOURS** (green)
Text: "Airflow DAG + dbt model + NR alert — all in parallel"
Bold text: "Engineer reviews 1 PR instead of 5 files"

**4 numbered process steps below:**
1. "Orchestrator reads spec → spawns Planner + Coders simultaneously"
2. "Each agent works on an independent file — zero waiting"
3. "Reviewer + Validator run in parallel on all output"
4. "Human sees a single clean PR to approve"

---

#### SLIDE 08 — Incident Investigation (white background, green header)
**Header:** "Incident Investigation  —  AI Queries New Relic Directly, Instantly"

**Left panel (before — light grey, red top bar):**
Label: BEFORE — Manual hunt
Hero: **2–3 HOURS** (red, large)
Text: "Log in to NR UI · navigate to entity · scroll logs · switch tabs · compare charts · Slack teammates"
Divider
Text (red): "Form hypothesis → test → repeat → still uncertain. Customer impact growing every minute."

**Right panel (after — light green, green top bar):**
Label: AFTER — AI-powered diagnosis
Hero: **30 MINS** (green, large) → corrected below to **0–20 MIN**
Text: "Claude queries NR, returns structured analysis"
Divider
Text (dark green): "Alert data · affected services · root cause identified — fix scoped immediately"
Bold: "12 New Relic tools · Jira auto-updated · root cause in minutes"

---

#### SLIDE 09 — Impact Analysis (white background)
**Full-width green banner:** "We see the full impact of every change BEFORE it touches production."

**Left card (before — red accent):**
"⚠ Before: Invisible blast radius"
"Engineer changes a pipeline file. Deploys. A downstream consumer breaks silently. 5-day incident — all from one undetected dependency."

**Right card (after — green accent, light green):**
"✅ After: Instant clarity"
"Impact analysis runs before coding. Sees 3 callers, 1 downstream consumer. Fix scoped. Ships confidently. Zero incident."

**Four metric cards at bottom:**
1. "~1 sprint/qtr" — "absorbed in surprise rework — before" (red)
2. "< 1 day" — "rework after impact-aware development" (green)
3. "0 blind deploys" — "every change impact-checked first" (dark green)
4. "Auto-updates" — "dependency map rebuilt on every file save" (dark green)

---

#### SLIDE 10 — Auto-Documentation (white background, green header)
**Header:** "Documentation That Writes Itself  —  Jira & Confluence Always Up to Date"

**Top flow (5 steps with arrows):**
Work session completes → /wrap-up fires (~30s) → Claude drafts summary → Jira ticket auto-updated → Confluence published

**Two columns below:**

**Jira column (blue header):**
"Jira — What gets auto-updated"
Rows: Status (In Review → Done), Comment (What was done + decisions), Worklog (Time logged), Links (Commits via branch)

**Confluence column (teal header):**
"Confluence — What gets published"
Rows: Architecture (Decisions logged), Postmortem (Incident page auto-created), Release (Notes from git history), Runbooks (Updated as team learns)

**Full-width bottom text (bold):** "Zero manual effort.  Every session documented.  Every time."

---

#### SLIDE 11 — Knowledge Compounds (dark navy background)
**Title (white, large):** "Knowledge That Compounds"
**Subtitle (green, italic):** "Every session makes every future session smarter — knowledge never leaves the team"

**Three horizontal layers (dark panels with colored left stripe and badge):**

Layer 1 (green stripe): "ALWAYS LOADED"
Title: "Session memory — auto-loads at every session start"
Desc: "Active priorities + recent lessons + architecture summary loaded automatically. No manual setup. Zero tokens wasted."

Layer 2 (dark green stripe): "PULL ON DEMAND"
Title: "Team knowledge — retrieved only when relevant"
Desc: "Patterns · architecture decisions · session history · past plans. Fetched on demand — only what's needed, when it's needed."

Layer 3 (purple stripe): "REPLAYABLE WINS"
Title: "Validated fixes — saved as reusable templates"
Desc: "After a confirmed fix: the steps are captured and indexed. Next time the same problem appears, the proven solution loads instantly."

**Bottom green banner:** "Every session: team knowledge grows. Every fix: the next one is faster. The system gets smarter, not staler."

---

#### SLIDE 12 — The Results (white background, green header)
**Header:** "The Results  —  Numbers the Team Has Measured"

**Four hero number cards (2×2 or 4 across):**
1. **8–12×** (green) — "overall productivity for DE tasks"
2. **2–6h** (bright green) — "dev ticket vs 2–3 days before"
3. **0–20m** (blue) — "Alert issue diagnosis vs 1–10 hours before"
4. **25+ SP** (dark green) — "sprint capacity + adhoc on top"

**Secondary stats bar (light grey):**
Label: "More measurements"
- "5–15 min" — "context reset after absence (vs hours/days before)"
- "3–5h" — "new pipeline (full cycle) vs 2–4 days before"
- "4–6h → 20m–1h" — "spec & plan phase"
- "2–4d → 1–2d" — "architecture + CDD + Confluence"

**Full-width green banner:** "8–12× overall for DE tasks · All metrics reported directly by Ingestion Team engineers"

---

#### SLIDE 13 — Before & After (white background, green header)
**Header:** "Before & After  —  Ingestion Team · 3 Repos · 3 Months"

**Three-column table:**
Columns: "What We Measured" | "Before" | "After (AI-Led)"

Rows:
1. Spec & Plan | 4–6 hours | 20 min – 1 hour ✅
2. Architecture + CDD | 2–4 days | 1–2 days ✅
3. Development ticket | 2–3 days | 2–6 hours (task-dependent) ✅
4. New pipeline (full cycle) | 2–4 days | 3–5 hours ✅
5. Alert issue diagnosis | 30 min – 3 hours | 0–20 minutes (NR MCP) ✅
6. Context after absence | Hours / days | 5–15 min via /bootstrap ✅
7. Sprint throughput | 25 SP (at capacity) | 25 SP + additional + adhoc ✅
8. Documentation effort | Manual, often skipped | Automatic via /wrap-up ✅
9. Code review layers | Manual review only | CC Opus + Copilot GPT (blind spots) + agents + human ✅

**Footer note:** "✅ = confirmed by Ingestion Team engineers · Repos: om-airflow-dags · spark-kafka-apps · tf-dataos-new-relic"

---

#### SLIDE 14 — Humans in Control (white background, green header)
**Header:** "AI Does the Work.  Humans Stay in Control.  Always."

**5 numbered gates (rows), Gate 3 highlighted in green:**
1. Requirements — "Human writes the spec — AI reads it, asks clarifying questions"
2. Architecture — "Human approves the implementation plan — before a line is written"
3. ★ Security Review — "AI flags every security vulnerability — any critical issue blocks the pipeline" (highlighted row)
4. PR Merge — "Human reviews every PR — agent output treated like any other code"
5. Deploy — "Human initiates the deploy — AI writes release notes + monitors"

**Footer note (italic, grey):** "Agent PRs treated identically to human PRs — same review, same standards, same gates."

---

#### SLIDE 15 — Getting Started (white background, green header)
**Header:** "Getting Started  —  From Zero to Productive in 4 Steps"

**4 step cards (side by side):**

Step 1 — 15 MIN (green header): "Install & Setup"
When: "One-time per engineer"
Desc: "Claude Code + MCP servers + Budget dial. Multi-orchestration + hooks + 20 skills. Fully automated — one script."

Step 2 — 5 MIN (dark green header): "Bootstrap New Repo"
When: "First visit to any repo"
Desc: "Detects your stack, seeds team memory, builds codebase graph, wires all MCPs. Runs once — context ready forever."

Step 3 — ALWAYS (green header): "AI-Led Development"
When: "Single agent or multi agent"
Desc: "Single task: Claude Code works alongside you. Complex task: /avengers spawns parallel agents. Copilot handles lines. Claude handles investigations."

Step 4 — 30 SEC (dark green header): "Wrap-Up"
When: "Every session end"
Desc: "Jira auto-updated · lessons captured. Knowledge persisted · graph refreshed. The habit that makes everything compound."

**Bottom section — "The Compounding Effect" (with divider):**
Three progressive cards:
- **Day 1** (light): "Full codebase context ready. Development tickets: days → hours."
- **Month 1** (medium green): "Lessons accumulate. Patterns reused. Alert diagnosis: hours → 0–20 min."
- **Month 3+** (dark green, white text): "Knowledge never leaves the team. 8–12× productivity — sustained."

---

#### SLIDE 16 — What We're Asking (dark navy background)
**Logo top-left**
**Title (white, large):** "What We're Asking"
**Green divider line**

**3 ask cards (dark navy panels, green left stripe):**
1. "Support adoption" — "Drive AI-led workflows across all Data Engineering & Management in DTM."
2. "Allocate time" — "Support the daily wrap-up habit — 30 seconds per session. Knowledge compounds automatically."
3. "Endorse the model" — "Establish this as the standard template for all DE teams at New Relic."

**Right panel (darker navy) — 4 verified metrics:**
- **8–12×** / Productivity
- **2–6h** / Dev ticket
- **0–20m** / Alert diagnosis
- **25+ SP** / Sprint capacity

**Bottom left:** "Thank You · Questions?"

---

#### SLIDE 17 — Thank You (dark navy background)
Same dark navy style as slide 16.
Centered: "Thank You" (very large, white)
Below: "Questions?" (italic, grey)
Bottom: NR logo + full disclaimer text

---

### OUTPUT REQUIREMENTS

- Deliver all 17 slides as individual high-resolution images (1920×1080px, PNG)
- Name them slide_01 through slide_17
- Every slide must have the NR logo bottom-right and the disclaimer text bottom-left
- Do not use lorem ipsum or placeholder text — every word shown above must appear exactly
- Preserve all verified metrics exactly as written — do not round, change, or embellish any number
- The green (#00AC69) and white theme must be consistent across all slides
- Make it stunning — this is a CEO-level presentation

---

*End of prompt. Attach slide_01.png through slide_17.png from the ingestion_ai/ folder when submitting to Gemini.*
