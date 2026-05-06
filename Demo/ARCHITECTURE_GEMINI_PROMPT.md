# Gemini Prompt — Simplified Architecture Diagram

Upload BOTH images:
1. `architecture.png` — the original (use as structural reference)
2. The sketch screenshot — use as layout/simplicity guidance

Then paste the prompt below.

---

```
You are a world-class technical illustrator. Generate a single high-resolution PNG image (2752×1536px) that is a clean, simplified version of the attached architecture diagram.

Use the original architecture diagram for structure and content accuracy.
Use the sketch as guidance for layout and simplicity level.

━━━ CRITICAL RULES ━━━
• Keep EVERY section from the original — do not remove any box or section
• Simplify text inside each box — keep only the key concept and 1–2 sub-items max
• NO file paths, NO code snippets, NO verbose descriptions
• Every word must be spelled correctly — check carefully before outputting
• Use the EXACT names listed below — do not invent or abbreviate any names
• All text must be readable at presentation size — minimum 14pt equivalent
• Output: 2752×1536px PNG, crisp and sharp, no blur
• No watermarks, no AI-generated labels

━━━ EXACT NAMES — DO NOT CHANGE THESE ━━━

Title: "Claude Code AI-Led Dev Environment — v2"
Subtitle: "hot/cold memory  ·  code-review-graph  ·  golden/replay  ·  budget dial"

Section names (spell exactly):
  Session Boot
  Hooks Layer
  Per-Project Memory (Hot/Cold)
  /golden + /replay
  /bootstrap — First Visit Only
  /avengers — Multi-Agent Orchestration
  Domain Skills (20 total)
  Model × Effort Routing
  /budget — Spend Dial
  Processing Pipeline
  Plugins

Agent names in /avengers (use EXACTLY — previous attempts used wrong names):
  Nick Fury (Opus — Orchestrator)
  Coders ×N (Sonnet)
  Reviewer (Sonnet)
  Validator (Sonnet)
  Pre-Validation Agent
  Dedicated sub agents: Solution-Architect · DE-Specialist · DevOps · NR-Expert

━━━ CONTENT PER SECTION ━━━

SESSION BOOT:
  • Claude Code starts
  • Load ~/.claude/CLAUDE.md — global rules + 20 skills
  • Load repo/.claude/CLAUDE.md — project context
  • Load hooks · Load MCPs · Load plugins

HOOKS LAYER:
  • Token Optimization (RTK) — 60–90% Bash output savings
  • OAuth Token Refresh — auto-refreshes MCP tokens silently
  • Telemetry Logging — tracks grep fallback rate
  • Self-Heal + Lesson Capture — corrections → lessons.md
  • Daily Statusline — model · context % · session $ · daily $ 🟢🟡🔴

PER-PROJECT MEMORY (HOT/COLD):
  Hot — auto-loaded on boot:
    • hot.md — active todos + recent lessons + architecture summary
    • GRAPH_REPORT.md — code graph summary + MCP tool hints
  Cold — pull on demand via memory MCP:
    • lessons.md · architecture.md · history.md · todo.md
    • plans/ — session plans mirrored per repo

/GOLDEN + /REPLAY — The Compounding Layer:
  • /golden save <slug> — distills session into reusable template
  • /golden list/validate — browse library, check staleness
  • /replay <slug> — loads proven steps as prior-art plan
  • Auto-prompt at wrap-up if 3 signals present

/BOOTSTRAP — FIRST VISIT ONLY (runs once per repo · Opus + high effort):
  Phase 1: Detect stack — language + framework
  Phase 2: Seed memory — 6 files + plans/
  Phase 3: Write project CLAUDE.md + .mcp.json + .gitignore
  Phase 4: Build Code Review Graph — Tree-sitter AST + SQLite
  Phase 5: Populate architecture.md from GRAPH_REPORT.md

/AVENGERS — MULTI-AGENT ORCHESTRATION:
  Nick Fury (Opus — Orchestrator):
    1. Get Jira ticket or requirement
    2. Research codebase → write implementation plan
    3. Ask user to review plan
    4. Once approved → spawn parallel subagents
    5. Validates gates · blocks bad code · shuts down on completion

  Parallel agents (Sonnet):
    Coders ×N — write code per plan, verify build
    Reviewer — code standards + security checks
    Validator — tests + blast radius before merge
    Pre-Validation Agent — final gate

  Multi-Agent Orchestration Dashboard

  Dedicated sub agents (on demand):
    Solution-Architect · DE-Specialist · DevOps · NR-Expert

DOMAIN SKILLS (20 total):
  Auto-trigger on keyword or file path:
    /airflow · /pyspark · /python · /sql · /shell · /docker · /cicd
    /nrql · /nralert · /terraform · /openmetadata · /mcp-builder · /profiling

  Explicit invoke using /skill_name:
    /bootstrap · /wrap-up · /avengers · /golden · /replay · /budget · /demo

MODEL × EFFORT ROUTING:
  Haiku 4.5 — lookups · NRQL · doc search · mechanical transforms
  Sonnet 4.6 — DEFAULT: coding · testing · debugging · refactoring
  Opus 4.7 — max effort: architecture · code review · multi-agent orchestration · brainstorming

/BUDGET — SPEND DIAL:
  • Caps: daily / weekly / monthly (budget.json)
  • 🟢 <80% — normal  🟡 80–100% — switch to Haiku  🔴 >cap — override required
  • Commands: /budget status · set · override · report

PROCESSING PIPELINE:
  Tree-sitter AST parsing → SQLite knowledge graph
  ↓
  28 MCP tools: semantic_search · get_impact_radius · detect_changes · query_graph
  ↓
  GRAPH_REPORT.md (auto-loaded) + graph.html (optional viz)

PLUGINS:
  nr-mcp · nr-kafka · terraform · code-review-graph · superpowers
  jira · confluence · bedrock-retrieval

SESSION FLOW (bottom bar — full width, connected steps):
  [First Visit]
  /bootstrap → memory + CRG build + seed

  → [Session Boot]
  Load hooks + MCPs + plugins + context

  → [During Work]
  graph-first work → /wrap-up → repeat
  /golden save | /replay

  → [Session End]
  corrections → lessons.md
  /wrap-up: history + graph + budget check

  → [Next Session]
  smarter context · golden library grows · stay in budget

━━━ STYLE ━━━
• Same overall layout structure as the original diagram
• Clean white or very light background
• Colour-coded sections matching the original colour zones
• Each section is a clearly bounded box with a bold section title
• Connecting arrows between sections where the original has them
• The bottom session-flow bar spans the full width
• Professional technical diagram quality — not a slide, not a mind map
• No watermarks, no AI labels, no platform branding
```
