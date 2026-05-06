# Gemini Prompt — Architecture Diagram (Modern Design)

Paste this entire prompt into Gemini. No reference image needed.

---

```
Create a professional, modern software architecture diagram. Output as a single high-resolution PNG image, 2800×2000px.

━━━ DESIGN STYLE ━━━
• Modern tech architecture diagram — like AWS/GCP architecture diagrams or Notion/Linear system design docs
• Dark navy background (#0D0D24) with colour-coded zone panels
• Clean sharp-cornered or softly-rounded panels — NOT hand-drawn, NOT sketch style
• Modern sans-serif font (Inter or SF Pro) — crisp, readable at all sizes
• Thin clean arrows with arrowheads — solid for always-on flows, dashed for on-demand/one-time
• Each zone: semi-transparent darker panel with a coloured left border stripe (4px) and bold zone title
• Minimum font size: 13px equivalent — all text must be readable
• NO watermarks, NO AI labels, NO hand-drawn elements
• Colour palette: dark navy base + accent colours per zone (listed below)

━━━ TITLE (top-centre) ━━━
Large bold white text: "Claude Code AI-Led Dev Environment"
Smaller italic grey text below: "hot/cold memory  ·  code-review-graph  ·  golden/replay  ·  budget dial"

━━━ CANVAS LAYOUT — 4 ROWS ━━━
ROW 1 (top):     4 equal columns → Session Boot | Hooks Layer | Per-Project Memory | /golden + /replay
ROW 2 (middle):  Left third = /bootstrap | Centre half = /avengers (LARGE) | Right sixth = Processing Pipeline
ROW 3 (lower):   3 equal columns → Domain Skills | Model × Effort Routing | /budget — Spend Dial
ROW 3 right:     Plugins (small, stacked right of budget)
ROW 4 (bottom):  Full-width session flow timeline strip

DO NOT move any zone from its stated position. If a zone does not fit, make it smaller, not displaced.

━━━ ROW 1 — COLUMN 1 (accent: #4A9EFF blue): "Session Boot" ━━━
• Claude Code starts
• Load ~/.claude/CLAUDE.md — global rules + 20 skills
• Load repo/.claude/CLAUDE.md — project context
• Load hooks · Load MCPs · Load plugins

━━━ ROW 1 — COLUMN 2 (accent: #FFB84A amber): "Hooks Layer" ━━━
Six hook items (stacked):
• Token Optimization (RTK) — 60–90% Bash savings
• OAuth Token Refresh — auto-refreshes MCP tokens
• Telemetry Logging — grep fallback rate tracking
• Self-Heal + Lesson Capture — corrections → lessons.md
• Stop Record Cost — session $ → cost.jsonl
• Daily Statusline — model · context % · session $ · 🟢🟡🔴

━━━ ROW 1 — COLUMN 3 (accent: #A855F7 purple): "Per-Project Memory (Hot/Cold)" ━━━
HOT — auto-loaded on boot (bright highlighted sub-panel):
  • hot.md — active todos + recent lessons + architecture summary
  • GRAPH_REPORT.md — code graph summary + MCP tool hints

COLD — pull on demand via memory MCP (dimmer sub-panel):
  • lessons.md · architecture.md · history.md · todo.md
  • plans/ — session plans mirrored per repo

Self-improvement loop note on lessons.md:
  "corrections → append → 3× = Pattern rule"

━━━ ROW 1 — COLUMN 4 (accent: #10B981 green): "/golden + /replay  — The Compounding Layer" ━━━
LEFT HALF:
  /golden save <slug>
  → distills validated session
  → Symptom · Root Cause · Steps That Worked · What NOT To Do
  → stores ~/.claude/golden/<slug>.md

RIGHT HALF:
  /replay <slug>
  → validates staleness (files exist)
  → loads proven steps as prior-art plan
  Badge: "avoids re-deriving proven fixes"

BOTTOM: cylinder icon — ~/.claude/golden/ + index.json
Dashed arrow from /wrap-up: "auto-prompts save-worthy sessions [y/n/edit]"

━━━ ROW 2 — LEFT THIRD (accent: #F97316 orange): "/bootstrap — First Visit Only" ━━━
Sub-label: "runs once per repo · Opus + high effort"

5 phases (numbered list):
Phase 1: Detect stack — language + framework
Phase 2: Seed memory — 6 files + plans/
Phase 3: Write project CLAUDE.md + .mcp.json + .gitignore
Phase 4: build-graph.sh
  · code-review-graph install (wire MCP)
  · code-review-graph build (SQLite graph)
  · compose GRAPH_REPORT.md
Phase 5: Populate architecture.md from GRAPH_REPORT.md

Dashed arrows out:
  → memory zone: "seeds hot.md + cold files + plans/"
  → CRG: "builds SQLite graph"
  → repo CLAUDE.md: "@ hot.md + @ GRAPH_REPORT.md"

━━━ ROW 2 — CENTRE HALF (accent: #3B82F6 blue, LARGE ZONE): "/avengers — Multi-Agent Orchestration" ━━━
Subtitle: "Fury (Opus) orchestrates specialists (Sonnet) in parallel"

This zone contains FIVE sub-panels arranged left to right, then a bottom row:

SUB-PANEL 1 — amber (#FDE68A): "Nick Fury — Captain (Opus)"
  Numbered steps (use EXACTLY this text):
  1. Get Jira ticket or requirement
  2. Research codebase → write implementation plan
  3. Ask user to review plan
  4. Once approved → spawn parallel subagents
  5. Validates gates · blocks bad code · shuts down on completion

SUB-PANEL 2 — light orange (#FED7AA): "Coders ×N (Sonnet)"
  • Parallel code writing
  • Different task batches
  • Write code per plan · verify build

SUB-PANEL 3 — light green (#BBF7D0): "Pipeline Specialists (Sonnet)"
  [Reviewer / Contact SME] → [Validator] → [Pre-Validation Agent]
  • Code standards + security review
  • Tests + blast radius check
  • Final gate before human review

SUB-PANEL 4 — light pink (#FECDD3): "Human Review"
  • PR review required before merge
  • Human approves or requests changes
  • AI-assisted PR description generated
  Arrow in: "Pre-Validation passes → Human Review"
  Arrow out: "Approved → merge"

SUB-PANEL 5 — teal (#99F6E4): "/wrap-up on Completion"
  • Update Jira tickets
  • Append to session history
  • Summarize session
  • /golden save for future reference

BOTTOM ROW inside /avengers (three items, do not place outside the zone):
  Left box (amber): "Agent Dashboard" — live mission view
  Centre box (teal): "State File" — /tmp/avengers-{TEAM}.json — phase · agents · tasks · blocked
  Right label: "Domain + Context"

DEDICATED SUB-AGENTS ROW (below bottom row, inside zone, tiny):
  Label: "Spawned on-demand by Fury:"
  [Solution-Architect]  [DE-Specialist]  [DevOps]  [NR-Expert]

━━━ ROW 2 — RIGHT SIXTH (accent: #6366F1 indigo): "Processing Pipeline" ━━━
TOP — cylinder icon: "code-review-graph"
  • Tree-sitter AST + SQLite
  • 28 MCP tools
  • auto-updates on every Edit (<2s)
  Tools: semantic_search · get_impact_radius · detect_changes · query_graph

MIDDLE — cylinder icon: "memory MCP server"
  • pull-on-demand cold memory
  • 5 tools: get_memory · search_memory · list_lessons · get_todo · recall_plan

BOTTOM — box: "/wrap-up"
  Session end ritual — 6 phases:
  0: corrections audit
  1: append-history
  2: todo update
  3: lessons dedupe
  3.5: golden auto-prompt
  4: CRG graph refresh
  5: mirror-plans + regen hot.md
  6: handoff summary

━━━ ROW 3 — COLUMN 1 (accent: #34D399 mint): "Domain Skills (20 total)" ━━━
Auto-trigger on keyword or file path:
  /airflow · /pyspark · /python · /sql · /shell
  /docker · /cicd · /nrql · /nralert · /terraform
  /openmetadata · /mcp-builder · /profiling

Explicit invoke using /skill_name:
  /bootstrap · /wrap-up · /avengers
  /golden · /replay · /budget · /demo

Superpowers:
  ⚡ brainstorming · ⚡ systematic-debugging

━━━ ROW 3 — COLUMN 2 (accent: #8B5CF6 violet): "Model × Effort Routing" ━━━
Sub-label: "default = sonnet+medium, escalate per-turn not per-session"

Four rows:
  Haiku 4.5    → lookups · NRQL · doc search · mechanical transforms     (cheapest)
  Sonnet 4.6   → coding · testing · debugging · refactoring              ★ DEFAULT
  Opus 4.7     → architecture · code review · multi-agent orchestration · brainstorming
  Opus + max   → novel research only (rare)

Note: "Avengers: Fury = Opus · Specialists = Sonnet"

━━━ ROW 3 — COLUMN 3 (accent: #EF4444 red): "/budget — Spend Dial" ━━━
Traffic light icons: 🟢🟡🔴

Caps: daily / weekly / monthly (budget.json)
  🟢 <80%  — normal work
  🟡 80–100% — switch to Haiku for mechanical tasks
  🔴 >cap  — override required

Sources: cost.jsonl · Claude transcripts · NR MCP cache
Commands: /budget status · set · override · report

━━━ ROW 3 — FAR RIGHT (accent: #64748B slate): "Plugins" ━━━
Pill badges (enabled):
  nr-mcp · nr-kafka · terraform
  code-review-graph · superpowers
  jira · confluence · bedrock-retrieval

━━━ ROW 4 — FULL WIDTH TIMELINE STRIP ━━━
Five connected steps (horizontal flow with arrows):

[First Visit]              [Session Boot]              [During Work]                    [Session End]                [Next Session]
/bootstrap →               Load hooks +                graph-first work ·               /wrap-up (6 phases) ·        smarter context ·
memory + CRG               MCPs + plugins +            MCP tools ·                      golden auto-prompt ·         golden library grows ·
build + seed               hot.md +                    /golden save ·                   mirror-plans +               stay in budget
                           GRAPH_REPORT                /replay · /avengers              regen hot.md

Footer (bold, bottom edge):
"First Visit: bootstrap → memory + CRG build → seed  |  Every Session: boot → graph-first → /wrap-up → repeat  |  /golden save · /replay · /budget"

━━━ ARROWS LEGEND (bottom corner) ━━━
—→  solid: every-session flow
- →  dashed: one-time or on-demand
..→  dotted: passive/auto hook
◇   diamond: conditional branch
```
