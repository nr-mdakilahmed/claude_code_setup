# Gemini Prompt — Architecture Diagram (Hand-Drawn Sketch)

Upload the reference image: `architecture.png`
Then paste the prompt below.

---

```
I am attaching a hand-drawn sketch architecture diagram as a STYLE REFERENCE.
Recreate a new version of this diagram in the EXACT SAME visual style — same font, same hand-drawn look, same pastel zone colours, same wavy arrows, same badge elements, same sketch icons, same dense layout on cream background.

DO NOT copy the content from the reference image. Use ONLY the new content listed below.
ONLY copy the visual style, colour palette, typography, and layout density.

━━━ MATCH THESE STYLE ELEMENTS FROM THE REFERENCE IMAGE EXACTLY ━━━
• Background: warm cream #F5EDD8 — same as reference
• Font: Caveat handwriting font — same bold titles, same lighter body text as reference
• Zone borders: same slightly wobbly hand-inked rounded rectangles as reference
• Arrows: same wavy/zigzag style as reference — zigzag for active flows, dashed curves for one-time
• Zone fills: same rich pastel wash colours per zone as reference
• Badge elements: same small coloured rounded-rectangle badges for labels (like [hot.md ~2k], model badges)
• Icons: same hand-drawn style — ☆ stars, ✨ sparkles, ⚡ lightning, ⚙ gears, ☁ cloud, 🟢🟡🔴 traffic lights
• Zone titles: same bold handwriting with coloured underline
• Arrow labels: same small italic annotations along arrow paths
• Nested sub-zones: same treatment as reference (brighter borders, slightly different fill)
• Same dense information layout — pack content tightly like the reference
• Paper texture: same slight ink grain as reference
• Canvas: 2800×2000px, same proportions as reference

━━━ OUTPUT REQUIREMENTS ━━━
• 2800×2000px PNG
• No watermarks, no AI labels
• Match the reference's hand-drawn quality exactly
• Style reference: like Excalidraw but more artistic and detailed

━━━ TITLE (top-centre, large bold handwriting) ━━━
"Claude Code AI-Led Dev Environment"
Smaller italic below: "hot/cold memory  ·  code-review-graph  ·  golden/replay  ·  budget dial"

━━━ CANVAS LAYOUT — 4 ROWS — DO NOT REORDER ━━━
ROW 1 (top):     4 equal columns → Session Boot | Hooks Layer | Per-Project Memory | /golden + /replay
ROW 2 (middle):  Left quarter = /bootstrap | Centre half = /avengers (LARGE) | Right quarter = Processing Pipeline
ROW 3 (lower):   3 equal columns → Domain Skills | Model × Effort Routing | /budget — Spend Dial + Plugins
ROW 4 (bottom):  Full-width session flow timeline strip

━━━ ZONE COLOURS (pastel, hand-wash style) ━━━
Session Boot:              sky blue wash #B8D4F0
Hooks Layer:               warm yellow wash #FAE8A0
Per-Project Memory:        soft lavender #D8C8F0
/golden + /replay:         mint green wash #B8E8D0
/bootstrap:                peach coral wash #F8C8B0
/avengers:                 light sky blue wash #C0DCF8 (LARGE zone)
Processing Pipeline:       sage green wash #C0D8B8
Domain Skills:             soft mint #C0EAD0
Model × Effort Routing:    lilac wash #D0C0F0
/budget — Spend Dial:      soft rose #F0C0C0
Plugins:                   warm sand #F0E0C0

━━━ ROW 1 — SESSION BOOT (sky blue, ☆ corner) ━━━
• Claude Code starts  ☁
• Load ~/.claude/CLAUDE.md — global rules + 20 skills
• Load repo/.claude/CLAUDE.md — project context
• Load hooks · Load MCPs · Load plugins

━━━ ROW 1 — HOOKS LAYER (warm yellow, ✨ corner) ━━━
Six stacked items (each a small rounded box):
• Token Optimization (RTK) — 60–90% Bash savings
• OAuth Token Refresh — auto-refreshes MCP tokens
• Telemetry Logging — grep fallback rate tracking
• Self-Heal + Lesson Capture — corrections → lessons.md
• Stop Record Cost — session $ → cost.jsonl
• Daily Statusline — model · context % · session $ · 🟢🟡🔴

━━━ ROW 1 — PER-PROJECT MEMORY (lavender, ☆ corner) ━━━
HOT sub-zone (brighter border, bold label "AUTO-LOADED on boot"):
  hot.md — todos + lessons + architecture summary
  GRAPH_REPORT.md — code graph summary + MCP hints

COLD sub-zone (dimmer, "pull on demand via memory MCP"):
  lessons.md · architecture.md · history.md · todo.md
  plans/ — session plans per repo

Tiny circular self-arrow on lessons.md:
  "corrections → 3× = Pattern rule"  (self-improvement loop)

━━━ ROW 1 — /GOLDEN + /REPLAY (mint green, ☆ corner) ━━━
Tagline: "the compounding layer"

Left half — /golden save <slug>:
  → distills validated session
  → Symptom · Root Cause · Steps That Worked · What NOT To Do
  → ~/.claude/golden/<slug>.md

Right half — /replay <slug>:
  → validates staleness · loads proven steps
  Badge: "avoids re-deriving proven fixes"

Bottom: cylinder icon — ~/.claude/golden/ + index.json
Dashed arrow from /wrap-up: "auto-prompts save-worthy sessions [y/n/edit]"

━━━ ROW 2 LEFT — /BOOTSTRAP (peach coral, ⚙ corners) ━━━
Sub-label: "runs once per repo · Opus + high effort"

Phase 1: Detect stack — language + framework
Phase 2: Seed memory — 6 files + plans/
Phase 3: Write project CLAUDE.md + .mcp.json + .gitignore
Phase 4: build-graph.sh
  · install code-review-graph (wire MCP)
  · build SQLite graph
  · compose GRAPH_REPORT.md
Phase 5: Populate architecture.md ← from GRAPH_REPORT.md

Dashed arrows out (with italic hand-written labels):
  → memory: "seeds hot.md + cold files"
  → CRG: "builds SQLite graph"
  → CLAUDE.md: "@ hot.md + @ GRAPH_REPORT.md"

━━━ ROW 2 CENTRE — /AVENGERS (sky blue, ⚡ corners, LARGE) ━━━
Zone title: "/avengers — Multi-Agent Orchestration"
Subtitle: "Fury (Opus) orchestrates specialists (Sonnet) in parallel"

FIVE SUB-PANELS inside this zone (left to right):

Panel 1 (amber wash): "Nick Fury — Captain (Opus)"
  Numbered steps (EXACT text — do not paraphrase):
  1. Get Jira ticket or requirement
  2. Research codebase → write implementation plan
  3. Ask user to review plan
  4. Once approved → spawn parallel subagents
  5. Validates gates · blocks bad code · shuts down on completion

Panel 2 (light orange wash): "Coders ×N (Sonnet)"
  Parallel code writing
  Different task batches
  Write code per plan · verify build

Panel 3 (light green wash): "Pipeline Specialists (Sonnet)"
  [Reviewer / Contact SME] → [Validator] → [Pre-Validation Agent]
  Code standards + security
  Tests + blast radius check
  Final gate before human review

Panel 4 (light pink wash): "Human Review"
  PR review required before merge
  Human approves or requests changes
  AI-assisted PR description
  Arrow in: "passes gate →"
  Arrow out: "approved → merge"

Panel 5 (teal wash): "/wrap-up on Completion"
  Update Jira tickets
  Append to session history
  Summarize session
  /golden save for future reference

BOTTOM ROW (inside zone, do NOT place outside):
  Left box (amber): "Agent Dashboard" — live mission view
  Centre box (teal): "State File" — /tmp/avengers-{TEAM}.json — phase · agents · tasks · blocked
  Right: "Domain + Context"

DEDICATED SUB-AGENTS (tiny row at very bottom of zone):
  Label: "Spawned on-demand by Fury:"
  [Solution-Architect]  [DE-Specialist]  [DevOps]  [NR-Expert]

━━━ ROW 2 RIGHT — PROCESSING PIPELINE (sage green, ⚙ corner) ━━━
TOP — cylinder: "code-review-graph"
  Tree-sitter AST + SQLite
  28 MCP tools
  auto-updates on every Edit (<2s)
  semantic_search · get_impact_radius · detect_changes · query_graph

MIDDLE — cylinder: "memory MCP server"
  pull-on-demand cold memory
  get_memory · search_memory · list_lessons · get_todo · recall_plan

BOTTOM — box: "/wrap-up"
  6 phases:
  0: corrections audit
  1: append-history
  2: todo update
  3: lessons dedupe
  3.5: golden auto-prompt
  4: CRG graph refresh
  5: mirror-plans + regen hot.md
  6: handoff summary

━━━ ROW 3 LEFT — DOMAIN SKILLS (mint, 20 total) ━━━
Auto-trigger on keyword or file path:
  /airflow · /pyspark · /python · /sql · /shell
  /docker · /cicd · /nrql · /nralert · /terraform
  /openmetadata · /mcp-builder · /profiling

Explicit invoke using /skill_name:
  /bootstrap · /wrap-up · /avengers
  /golden · /replay · /budget · /demo

Superpowers: ⚡brainstorming · ⚡systematic-debugging

━━━ ROW 3 CENTRE — MODEL × EFFORT ROUTING (lilac) ━━━
Sub-label: "default = sonnet+medium, escalate per-turn"

  Haiku 4.5    → lookups · NRQL · mechanical transforms        (cheapest)
  Sonnet 4.6   → coding · testing · debugging · refactoring     ★ DEFAULT
  Opus 4.7     → architecture · code review · multi-agent · brainstorming
  Opus + max   → novel research only (rare)

Note: "Fury = Opus · Specialists = Sonnet"

━━━ ROW 3 RIGHT — /BUDGET SPEND DIAL (rose) + PLUGINS (sand) ━━━
/BUDGET:
  Traffic lights 🟢🟡🔴 (hand-drawn icon)
  Caps: daily / weekly / monthly (budget.json)
  🟢 <80% — normal
  🟡 80–100% — switch to Haiku
  🔴 >cap — override required
  Commands: status · set · override · report

PLUGINS (small stacked pills):
  ● nr-mcp  ● nr-kafka  ● terraform
  ● code-review-graph  ● superpowers
  ● jira  ● confluence  ● bedrock-retrieval

━━━ ROW 4 — FULL WIDTH TIMELINE (cream strip) ━━━
Five connected boxes with arrows:

[First Visit]           [Session Boot]            [During Work]              [Session End]               [Next Session]
/bootstrap →            Load hooks +              graph-first work ·         /wrap-up (6 phases) ·       smarter context ·
memory + CRG build      MCPs + plugins +          MCP tools ·                golden auto-prompt ·        golden library grows ·
+ seed                  hot.md + GRAPH_REPORT     /golden save · /replay ·   mirror-plans +              stay in budget
                                                  /avengers                  regen hot.md

Footer (bold italic handwriting, bottom edge):
"First Visit: bootstrap → memory + CRG build → seed  |  Every Session: boot → graph-first → /wrap-up → repeat  |  /golden save · /replay · /budget"

━━━ DECORATIVE TOUCHES ━━━
• ☆ star: mark Session Boot, Memory, Golden zones (top corner)
• ✨ sparkle: Hooks Layer top-right
• ⚡ lightning: both corners of /avengers zone
• ⚙ gear: Bootstrap and Processing Pipeline corners
• ☁ cloud: next to "Claude Code starts"
• 🟢🟡🔴: Budget zone only
• Small ink blot or smudge at a few corners for authenticity
• Slightly different ink weight on different arrows for variety
• Zone borders should look like they were drawn with a fine-tip marker
```
