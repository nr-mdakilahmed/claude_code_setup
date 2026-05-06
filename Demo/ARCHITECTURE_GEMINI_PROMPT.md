# Gemini Prompt — Simplified Architecture Diagram

Upload BOTH images:
1. `architecture.png` — the original (use as structural reference)
2. The sketch screenshot — use as layout guidance

Then paste the prompt below.

---

```
You are a world-class technical illustrator. Generate a single high-resolution PNG image (2752×1536px) that is a clean, simplified version of the attached architecture diagram. 

Use the original architecture diagram for structure and content accuracy.
Use the sketch as guidance for layout and simplicity level.

━━━ CRITICAL RULES ━━━
• Keep EVERY section from the original — do not remove any box or section
• Simplify text inside each box — keep only the key concept name and 1-2 sub-items max
• NO file paths, NO code snippets, NO verbose descriptions
• Every word must be spelled correctly — check carefully
• Use the EXACT names listed below — do not invent alternative names
• All text must be readable at presentation size — minimum 14pt equivalent
• Output: 2752×1536px PNG, crisp and sharp, no blur

━━━ EXACT NAMES TO USE — DO NOT CHANGE THESE ━━━

Title: "Claude Code AI-Led Dev Environment — v2"
Subtitle: "hot/cold memory  ·  code-review-graph  ·  golden/replay  ·  budget dial"

Section names (use exactly):
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
  Plugins (11 enabled, 2 off)

Agent names in /avengers (use EXACTLY these — the previous attempt used wrong names):
  Nick Fury (Captain, Opus) — Orchestrator
  Coders × N (Sonnet) — parallel
  Reviewer / Contact SME (Sonnet)
  Pre-Validation Agent
  Dedicated sub agents: Solution-Architect · openmetadata-sme · DevOps · NewRelic

━━━ CONTENT PER SECTION (simplified) ━━━

SESSION BOOT:
  • Claude Code Starts
  • Load global CLAUDE.md (rules + skills)
  • Load repo/.claude/CLAUDE.md
  Note: ~4k tokens at session start (3–7× cheaper)

HOOKS LAYER:
  • Token Optimization (RTK)
  • Refresh Tokens (OAuth)
  • Log Usage (Telemetry)
  • Auto-Heal + Stop (Lessons)
  • Statusline (daily)

PER-PROJECT MEMORY (HOT/COLD):
  Hot (auto-loaded on boot):
    • hot.md ~2k tokens — curated digest
    • GRAPH_REPORT.md — code graph summary
  Cold (pull on demand):
    • MEMORY.md · lessons.md · history.md
    • plans/

/GOLDEN + /REPLAY — The Compounding Layer:
  • /golden save <slug> — captures validated fix
  • /replay <slug> — loads proven steps
  • Validates staleness, applies previous patterns

/BOOTSTRAP — FIRST VISIT ONLY (runs once per repo, Opus + high effort):
  Phase 1: Detect stack
  Phase 2: Seed memory (.md + plans)
  Phase 3: Project CLAUDE.md
  Phase 4: Build Code Review Graph
  Phase 5: Populate Architecture

/AVENGERS — MULTI-AGENT ORCHESTRATION:
  Nick Fury (Captain, Opus) — Orchestrator
    routes work · validates gates · blocks bad code
  Coders × N (Sonnet) — parallel code writing
  Reviewer / Contact SME (Sonnet)
  Pre-Validation Agent
  Agent Dashboard: [avengers:2026] (real-time missions)
  Dedicated sub agents:
    Solution-Architect · openmetadata-sme · DevOps · NewRelic

DOMAIN SKILLS (20 total — auto + explicit):
  Auto-trigger: airflow · pyspark · sql · python · shell · docker · cicd
  Explicit only: bootstrap · wrap-up · golden · replay · budget · avengers

MODEL × EFFORT ROUTING:
  Haiku 4.5 — cheapest: lookups, docs, mechanical
  Sonnet 4.6 — default: coding, testing, debugging
  Opus 4.7 — max-effort: architecture, analysis, new research

/BUDGET — SPEND DIAL:
  • daily / weekly / monthly caps
  • 🟢 under 80%  🟡 80–100%  🔴 over cap
  • auto-downshift model when yellow

PROCESSING PIPELINE:
  Code Review Graph (Tree-sitter AST + SQLite)
  ↓
  MCP Server (Cold Memory · Tool Access)
  • semantic search · blast radius · community detection

PLUGINS (11 enabled, 2 off):
  NR MCP · Jira · Confluence · Terraform · Kafka · etc.

SESSION FLOW (bottom bar — show as connected steps):
  [First Visit: /bootstrap → memory + CRG build + seed]
  → [Session Boot: auto-load 4k tokens (hot.md + GRAPH_REPORT)]
  → [During Work: graph-first work → /wrap-up → repeat]
  → [Session End: capture wins · /golden save · /replay]
  → [Next Session: smarter context · stay in budget]

━━━ STYLE ━━━
• Same overall layout structure as the original diagram
• Clean white or very light grey background
• Colour-coded sections (use the same colour zones as the original)
• Each section is a clearly bounded box with a bold section title
• Connecting arrows between sections where the original has them
• The bottom session-flow bar spans the full width
• Professional technical diagram quality — not a slide, not a mind map
• No watermarks, no AI labels
```
