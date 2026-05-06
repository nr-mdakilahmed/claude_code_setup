# Gemini Prompt — Architecture Diagram (Full Generation)

Paste this entire prompt into Gemini to regenerate the architecture diagram with corrected content.
No reference image needed — this prompt is fully self-contained.

---

```
Draw an architecture diagram in a hand-drawn sketch style: large pastel-colored
rounded-rectangle zones on a warm cream background, Caveat-style font, wavy/zigzag
arrows for data flows every session, dashed curved arrows for one-time flows,
3D cylinder shapes for storage, simple sketch icons (gears, sparkles, stars,
folders, lightning bolt, database cylinders, traffic lights), italic labels on
arrows, nested sub-zones inside parent zones, no drop shadows, flat sketch look.

Title at top (large hand-drawn font): "Claude Code AI-Led Dev Environment — v2"
Subtitle (smaller italic): "hot/cold memory · code-review-graph · golden/replay · budget dial"

CANVAS: very wide and tall — 2800×2000px. Dense but readable.

════════════════════════════════════
LAYOUT: 4 columns top + 3 columns middle + 1 bottom strip
════════════════════════════════════

━━━ TOP-LEFT COLUMN (soft blue #cce4f7): "Session Boot"
  Star ☆ top-left corner.
  Vertical flow:
  → "Claude Code starts" (entry arrow, small cloud ☁ icon)
  ↓ wavy "loads"
  → Box: ~/.claude/CLAUDE.md  "global rules + routing + skills"
  ↓ wavy "loads"
  → Box: <repo>/.claude/CLAUDE.md  "only 2 @ refs"
     Small note under: "@ hot.md + @ GRAPH_REPORT.md"
  ↓ wavy "loads"
  → Box: "Load hooks · Load MCPs · Load plugins"

━━━ TOP-CENTER-LEFT ZONE (soft yellow #fdf3c0): "Hooks Layer"
  Sparkle ✨ top-right.
  Six rounded boxes stacked:

  Box 1 (warm orange #f5c9a0): rtk hook claude
    Sub: "PreToolUse → every Bash call"
    Badge: "60-90% token savings"

  Box 2 (teal #a0d4c8): refresh-mcp-tokens.py
    Sub: "UserPromptSubmit → MCP OAuth"

  Box 3 (sage #c0d4a0): log-grep-usage.sh
    Sub: "PostToolUse Grep|Glob → telemetry"
    Small arrow: "weekly review tunes graph coverage"

  Box 4 (rose #f5a0a8): self-heal-stop.sh
    Sub: "Stop → lesson-capture reminder"

  Box 5 (salmon #f5b8a8): stop-record-cost.sh
    Sub: "Stop → append session $ to cost.jsonl"
    Small arrow: "feeds /budget status"

  Box 6 (blue #a0c4f5): statusline.sh
    Sub: "model · context % · session $ · 🟢🟡🔴 daily"

━━━ TOP-CENTER-RIGHT ZONE (soft purple #e8d5f5): "Per-Project Memory (Hot/Cold)"
  Star ☆ top-right.
  Folder icon: ~/.claude/projects/<repo>/memory/

  TOP ROW (highlighted with bright border) — "AUTO-LOADED on boot":
    [hot.md] ← big bold, label "curated digest, wrap-up regenerates"
    [GRAPH_REPORT.md] ← label "code graph summary + MCP tool hints"

  BOTTOM ROW (dimmer, "pull on demand via memory MCP"):
    [MEMORY.md] [architecture.md] [todo.md] [lessons.md] [history.md]

  Small circular self-arrow on lessons.md:
    "mistakes → append → 3× = Pattern rule"
    Label: "self-improvement loop"

  Sibling folder below: ~/.claude/projects/<repo>/plans/
    Sub: "mirrored from ~/.claude/plans/ at /wrap-up"

  Arrows IN:
    • from Session Boot: "hot.md + GRAPH_REPORT auto-loaded only"
    • from /bootstrap: "seeds on first visit"
    • wavy from /wrap-up: "regenerates hot.md each session end"
    • dashed from self-heal-stop: "auto-captures corrections"
    • dashed from memory MCP: "deeper fetches pull-on-demand"

━━━ TOP-RIGHT ZONE (lavender #d4c4f0): "/golden + /replay"
  Star ☆ top-right.
  Tagline: "the compounding layer"

  Split into two halves:

  LEFT HALF: "/golden save <slug>"
    → distills validated session
    → writes ~/.claude/golden/<slug>.md
    Schema inset:
      pattern | scope | tags | trigger_hints
      Symptom → Root Cause → Steps That Worked →
      What NOT To Do → Files Touched

  RIGHT HALF: "/replay <slug>"
    → validates staleness (files exist, <30d)
    → loads golden as prior-art plan
    Small badge: "avoids re-deriving proven fixes"

  BOTTOM: cylinder ~/.claude/golden/ with index.json
    "N patterns · tagged · dated"

  Dashed arrow IN from /wrap-up Phase 3.5:
    "auto-prompts on save-worthy sessions [y/n/edit]"

━━━ MIDDLE-LEFT ZONE (soft coral #ffd5c8): "First Visit Only — /bootstrap"
  Gear ⚙ in corners. Sub-label: "(run once per new repo, Opus + high effort)"

  5-Phase vertical flow:
  Phase 1 → "detect-stack.sh → {lang, framework, primary}"
  Phase 2 → "seed-memory.sh → 6 files + plans/ dir"
  Phase 3 → "write-project-claude.sh → .claude/CLAUDE.md + .mcp.json + .gitignore"
  Phase 4 → "build-graph.sh"
           Sub-bullets:
             • code-review-graph install (wire MCP)
             • code-review-graph build (SQLite graph)
             • compose GRAPH_REPORT.md (from wiki + status)
  Phase 5 → "populate architecture.md ← from GRAPH_REPORT.md"

  Thick dashed arrows OUT:
    • to memory zone: "seeds hot.md + 5 cold files + plans/"
    • to CRG cylinder: "builds SQLite graph"
    • to MCP zone: "wires both servers in .mcp.json"
    • to repo CLAUDE.md: "@ hot.md + @ GRAPH_REPORT.md"

━━━ MIDDLE-CENTER ZONE (soft sky blue #daeeff, LARGE):
     "/avengers — Multi-Agent Orchestration"
  Lightning ⚡ top corners.
  Subtitle: "Fury (Opus) orchestrates specialists (Sonnet) in parallel"

  LEFT SUB-ZONE (amber #fde8a0): "Nick Fury — Captain (Opus)"
    Workflow:
    1. Get Jira ticket or requirement
    2. Research codebase → write implementation plan
    3. Ask user to review plan
    4. Once approved → spawn parallel subagents
    5. Validates gates · blocks bad code · shuts down on completion

  CENTER SUB-ZONE (light orange #fce0b8): "Coders ×N (Sonnet)"
    Label: "parallel, different task batches"
    Badge: "write code per plan · verify build"

  RIGHT SUB-ZONE (light green #d5f0d5): "Pipeline Specialists (Sonnet)"
    [Reviewer] → [Validator] → [Pre-Validation Agent]
    Labels: "code standards + security | tests + blast radius | final gate"

  BOTTOM — two small items:
    Left (amber): "Multi-Agent Orchestration Dashboard"
      "live mission view"
    Right (teal): State File /tmp/avengers-{TEAM}.json
      "phase · agents · tasks · blocked"

  Optional specialists row (tiny, on-demand):
    Solution-Architect | DE-Specialist | DevOps | NR-Expert
    Label: "spawned on-demand by Fury"

━━━ MIDDLE-RIGHT ZONE (soft green #d4edda): "Processing Pipeline" ⚙

  TOP — Cylinder (amber #fdc060): "code-review-graph"
    Sub: "Tree-sitter AST + SQLite + 28 MCP tools"
    Location: <repo>/.code-review-graph/ (gitignored)
    28-tools badge cluster:
      semantic_search_nodes · query_graph · get_impact_radius
      detect_changes · get_review_context · get_architecture_overview
      get_hub_nodes · refactor_tool · ...
    Small label: "auto-updates on every Edit via hook (<2s)"

  MIDDLE — Cylinder (violet #c4a8f0): "memory MCP server"
    Sub: "pull-on-demand access to cold memory"
    Location: ~/.claude-kit/mcp-servers/memory-server/
    5 tools badges:
      get_memory · search_memory · list_lessons
      get_todo · recall_plan
    Label: "no more 20k @-loads"

  BOTTOM — Box (green #a0e0b0): /wrap-up
    Sub: "session end ritual — 6 phases"
    Phase list (small):
      0: corrections audit
      1: append-history
      2: todo update
      3: lessons dedupe + CLAUDE.md promotion
      3.5: golden-worthiness auto-prompt
      4: refresh-graph-report (CRG update)
      5: mirror-plans + regenerate hot.md
      6: handoff summary

    Wavy arrows UP:
      "persists → history · todo · lessons · hot.md · plans · GRAPH_REPORT"

━━━ BOTTOM-LEFT ZONE (soft mint #c0eaca): "Domain Skills (20 total)"

  Auto-trigger on keyword or file path (compact grid):
    /airflow    /pyspark    /python     /sql
    /shell      /docker     /cicd       /nrql
    /nralert    /terraform  /openmetadata  /mcp-builder
    /profiling

  Explicit invoke using /skill_name (different color):
    /bootstrap  /wrap-up  /avengers
    /golden     /replay   /budget   /demo

  Superpowers badges:
    ⚡brainstorming  ⚡systematic-debugging

━━━ BOTTOM-CENTER-LEFT ZONE (soft purple #d4c4f5): "Model × Effort Routing"
  Tagline: "default = sonnet+medium, escalate per-turn not per-session"
  Four badges stacked:
    [haiku 4.5]  → lookups · NRQL · doc search · mechanical transforms   (cheapest)
    [sonnet 4.6] → coding · testing · debugging · refactoring             ★ DEFAULT
    [opus 4.7]   → architecture · code review · multi-agent orchestration · brainstorming
    [opus+max]   → novel research only (rare)
  Note: "Avengers: Fury=opus, specialists=sonnet"

━━━ BOTTOM-CENTER-RIGHT ZONE (soft red #f5b8b8): "/budget — Spend Dial"
  Traffic light 🟢🟡🔴 top-right.

  Caps: daily / weekly / monthly (budget.json)

  Statusline indicator (live):
    🟢 under 80% — normal work
    🟡 80-100% — switch to Haiku for mechanical tasks
    🔴 over cap — override required or stop

  Sources feeding /budget status:
    /tmp/claude_daily_YYYY-MM-DD.cost  (NR MCP cache)
    ~/.claude/projects/**/*.jsonl  (Claude transcripts)
    ~/.claude/telemetry/cost.jsonl  (stop-record-cost hook)

  Commands row:
    /budget status · /budget set · /budget override · /budget report

━━━ BOTTOM-RIGHT ZONE (warm peach #ffe8d8): "Plugins"
  Pill badges (green = on):
    ● nr-mcp          ● nr-kafka         ● terraform
    ● code-review-graph  ● superpowers   ● jira
    ● confluence      ● bedrock-retrieval

━━━ BOTTOM TIMELINE STRIP (warm cream #f5f0e0)
  Horizontal arrow timeline:

  [🔵 First Visit]         [🟢 Session Boot]         [🟡 During Work]              [🔴 Session End]            [🔵 Next Session]
  /bootstrap +             Load hooks + MCPs +        graph-first work ·            /wrap-up (6 phases +        smarter context ·
  build-graph +            plugins + context           MCP tools · /golden save ·    golden auto-prompt +        golden library grows ·
  seed memory +            (hot.md + GRAPH_REPORT      /replay · /avengers ·         mirror-plans +              stay in budget
  install MCPs             auto-loaded)                /budget statusline 🟢🟡🔴      regen hot.md)               (loop continues)

  Footer bold italic (large):
  "First Visit: bootstrap → memory MCP wire → CRG build → seed
   | Every Session: boot → graph-first work → /wrap-up → repeat
   | Capture wins: /golden save | Apply wins: /replay | Stay in budget: /budget"

════════════════════════════════════
EXACT VISUAL STYLE REQUIREMENTS
════════════════════════════════════

Background: warm cream #f0ece0

Arrow styles:
  Wavy zigzag:  every-session flows
  Solid thick:  internal zone flows
  Dashed curved: one-time flows
  Dotted:       auto-passive
  Diamond ◇:    conditional branches
  Traffic-light 🟢🟡🔴: ONLY on /budget zone + statusline

Typography (hand-drawn sketch, Caveat-style):
  Title: 42px bold
  Subtitle: 22px italic
  Zone labels: 24px bold
  Component labels: 15px bold
  Sub-labels: 12px italic
  Arrow labels: 11px italic along arrow path
  Badge text: 12px bold

Decorations:
  ☆ star: Session Boot, Memory, Golden corners
  ✨ sparkle: Hooks Layer corner
  ⚡ lightning x2: Avengers corners
  ⚙ gear x2: Bootstrap + Processing corners
  ☁ cloud: near "Claude Code starts"
  🟢🟡🔴 traffic lights: Budget zone top-right
  ◇ diamond: conditional-branch nodes

NO: drop shadows, gradients, sharp corners, corporate-flat look
YES: line wobble on borders, imperfect rounded corners, hand-inked look,
     slight zone overlaps, organic spacing
```
