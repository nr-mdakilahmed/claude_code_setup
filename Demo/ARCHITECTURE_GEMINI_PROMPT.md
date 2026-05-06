# Gemini Prompt — Architecture Diagram
# Style: original hand-drawn sketch (architecture.png)
# Wording: clean + minimal (like v4)
# Paste directly into Gemini

---

```
Draw an architecture diagram in a hand-drawn sketch style: large pastel-colored
rounded-rectangle zones on a warm cream background, Caveat-style font, wavy/zigzag
arrows for data flows every session, dashed curved arrows for one-time flows,
3D cylinder shapes for storage, simple sketch icons (gears, sparkles, stars,
folders, lightning bolt, database cylinders, traffic lights), italic labels on
arrows, nested sub-zones inside parent zones, no drop shadows, flat sketch look.

Title at top (large hand-drawn font): "Claude Code AI-Led Dev Environment"
Subtitle (smaller italic): "hot/cold memory · code-review-graph · golden/replay · budget dial"

CANVAS: very wide and tall — 2800×2000px. Dense but readable.

━━━ WORDING RULE — CRITICAL ━━━
Every single line of text must follow this rule:
  • MAX 4 WORDS per item — names and short labels only
  • NO descriptions, NO sub-text, NO explanations after the name
  • NO colons followed by long text
  • Write like a label on a diagram, not a sentence

GOOD examples (follow this style):
  ✓ "Token Optimization (RTK)"
  ✓ "Load hooks · MCPs · plugins"
  ✓ "Detect stack"
  ✓ "Build Code Review Graph"
  ✓ "1. Get ticket/requirement"
  ✓ "Coders ×N (Sonnet)"
  ✓ "Caps: daily · weekly · monthly"

BAD examples (avoid this):
  ✗ "Token Optimization (RTK) — 60-90% Bash output savings"
  ✗ "Load ~/.claude/CLAUDE.md  global rules + routing + skills"
  ✗ "Phase 1 → detect-stack.sh → {lang, framework, primary}"
  ✗ "Sub: PostToolUse Grep|Glob → telemetry"

════════════════════════════════════
LAYOUT: 4 columns top + 3 columns middle + 1 bottom strip
════════════════════════════════════

━━━ TOP-LEFT COLUMN (soft blue #cce4f7): "Session Boot"
  Star ☆ top-left corner.
  • Claude Code starts  ☁
  • Load CLAUDE.md files
  • Load hooks · MCPs · plugins

━━━ TOP-CENTER-LEFT ZONE (soft yellow #fdf3c0): "Hooks Layer"
  Sparkle ✨ top-right.
  • Token Optimization (RTK)
  • OAuth Token Refresh
  • Telemetry Logging
  • Self-Heal + Lesson Capture
  • Stop Record Cost
  • Daily Statusline  🟢🟡🔴

━━━ TOP-CENTER-RIGHT ZONE (soft purple #e8d5f5): "Per-Project Memory (hot/cold)"
  Star ☆ top-right.

  Hot (auto-loaded):
    hot.md · GRAPH_REPORT.md

  Cold (pull on demand):
    lessons.md · architecture.md
    history.md · todo.md · plans/

━━━ TOP-RIGHT ZONE (lavender #d4c4f0): "/golden + /replay"
  Star ☆ top-right.  "the compounding layer"

  /golden save <slug>
    distills session
    reusable template

  /replay <slug>
    validates · prior-art plan

  cylinder: ~/.claude/golden/

━━━ MIDDLE-LEFT ZONE (soft coral #ffd5c8): "First Visit Only — /bootstrap"
  Gear ⚙ corners.  once per repo · Opus + high effort

  Phase 1: Detect stack
  Phase 2: Seed memory
  Phase 3: Write project CLAUDE.md
  Phase 4: Build Code Review Graph
  Phase 5: Populate architecture.md

━━━ MIDDLE-CENTER ZONE (soft sky blue #daeeff, LARGE):
     "/avengers — Multi-Agent Orchestration"
  Lightning ⚡ top corners.
  Fury (Opus) orchestrates specialists (Sonnet)

  LEFT SUB-ZONE (amber #fde8a0): "Nick Fury — Captain (Opus)"
    1. Get ticket/requirement
    2. Research & plan
    3. User review plan
    4. Approve → spawn agents
    5. Validate & close

  CENTER SUB-ZONE (light orange #fce0b8): "Coders ×N (Sonnet)"
    parallel tasks

  CENTER-RIGHT SUB-ZONE (light green #d5f0d5): "Pipeline Specialists"
    Reviewer / Contact SME
    Validator
    Pre-Validation Agent

  RIGHT SUB-ZONE (light pink #f5d5e5): "Human Review"
    PR review
    Approve / request changes

  FAR-RIGHT SUB-ZONE (teal #d0f0e8): "/wrap-up"
    Update Jira
    Append history
    /golden save

  BOTTOM:
    Agent Dashboard  |  State File  |  Domain + Context

  Tiny row: Solution-Architect · DE-Specialist · DevOps · NR-Expert

━━━ MIDDLE-RIGHT ZONE (soft green #d4edda): "Processing Pipeline" ⚙

  Cylinder (amber): code-review-graph
    Tree-sitter AST + SQLite
    28 MCP tools

  Cylinder (violet): memory MCP server
    get_memory · search_memory
    list_lessons · get_todo

  Box (green): /wrap-up phases
    0: corrections audit
    1: append-history
    2: todo update
    3: lessons dedupe
    3.5: golden auto-prompt
    4: CRG refresh
    5: regen hot.md
    6: handoff

━━━ BOTTOM-LEFT ZONE (soft mint #c0eaca): "Domain Skills (20 total)"

  Auto-trigger:
    /airflow  /pyspark  /python  /sql
    /shell  /docker  /cicd  /nrql
    /nralert  /terraform  /openmetadata
    /mcp-builder  /profiling

  Explicit invoke:
    /bootstrap  /wrap-up  /avengers
    /golden  /replay  /budget  /demo

  ⚡brainstorming  ⚡systematic-debugging

━━━ BOTTOM-CENTER-LEFT ZONE (soft purple #d4c4f5): "Model × Effort Routing"
  default = sonnet+medium

  Haiku 4.5   → lookups · mechanical
  Sonnet 4.6  → coding · debugging  ★ DEFAULT
  Opus 4.7    → architecture · multi-agent
  Opus+max    → novel research

━━━ BOTTOM-CENTER-RIGHT ZONE (soft red #f5b8b8): "/budget — Spend Dial"
  🟢🟡🔴 top-right

  Caps: daily · weekly · monthly
  🟢 <80%  normal
  🟡 80–100% switch to Haiku
  🔴 >cap  override required

  status · set · override · report

━━━ BOTTOM-RIGHT ZONE (warm peach #ffe8d8): "Plugins"
  ● nr-mcp  ● nr-kafka  ● terraform
  ● code-review-graph  ● superpowers
  ● jira  ● confluence  ● bedrock-retrieval

━━━ BOTTOM TIMELINE STRIP (warm cream #f5f0e0)

  [🔵 First Visit]   [🟢 Session Boot]   [🟡 During Work]    [🔴 Session End]    [🔵 Next Session]
  /bootstrap         Load hooks +        graph-first ·       /wrap-up ·          smarter context ·
  build-graph        MCPs + plugins +    MCP tools ·         golden prompt ·     library grows ·
  seed memory        hot.md              /golden · /replay   mirror-plans        stay in budget

  Footer: "boot → graph-first → /wrap-up → repeat  |  /golden · /replay · /budget"

════════════════════════════════════
VISUAL STYLE
════════════════════════════════════

Background: warm cream #f0ece0

Arrows:
  Wavy zigzag: every-session flows
  Dashed curved: one-time flows
  Dotted: auto-passive
  Diamond ◇: conditional

Typography (Caveat-style hand-drawn):
  Title: 42px bold
  Zone labels: 24px bold
  Component labels: 15px bold
  Sub-labels: 12px italic
  Arrow labels: 11px italic

Decorations:
  ☆ Session Boot, Memory, Golden corners
  ✨ Hooks corner
  ⚡ Avengers corners ×2
  ⚙ Bootstrap + Processing corners ×2
  ☁ near "Claude Code starts"
  🟢🟡🔴 Budget zone only

NO drop shadows, gradients, sharp corners
YES wobbly borders, imperfect corners, hand-inked look
```
