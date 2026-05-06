#!/usr/bin/env python3
"""
generate_architecture_excalidraw.py
Generates architecture.excalidraw — open at excalidraw.com

Usage: python3 generate_architecture_excalidraw.py
Output: architecture.excalidraw (open in excalidraw.com, export as PNG/SVG)
"""

import json, os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.excalidraw")

# ── Excalidraw element builder ─────────────────────────────────────────────

_id = 0
def uid():
    global _id; _id += 1; return f"el-{_id:04d}"

FONT_HAND = 1   # Virgil — hand-drawn look

def rect(x, y, w, h, bg="#ffffff", stroke="#1e1e1e", roughness=1,
         fill="hachure", sw=2, opacity=100):
    return {
        "id": uid(), "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": fill, "strokeWidth": sw,
        "roughness": roughness, "opacity": opacity,
        "angle": 0, "seed": random.randint(1, 99999),
        "version": 1, "versionNonce": 1,
        "isDeleted": False, "groupIds": [],
        "frameId": None, "roundness": {"type": 3},
    }

def text(x, y, w, h, content, sz=14, bold=False, color="#1e1e1e", align="left"):
    return {
        "id": uid(), "type": "text",
        "x": x, "y": y, "width": w, "height": h,
        "text": content, "fontSize": sz,
        "fontFamily": FONT_HAND,
        "textAlign": align, "verticalAlign": "top",
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1,
        "roughness": 1, "opacity": 100,
        "angle": 0, "seed": random.randint(1, 99999),
        "version": 1, "versionNonce": 1,
        "isDeleted": False, "groupIds": [],
        "frameId": None, "roundness": None,
        "fontWeight": "bold" if bold else "normal",
    }

def arrow(x1, y1, x2, y2, label="", dashed=False, color="#555555"):
    el = {
        "id": uid(), "type": "arrow",
        "x": x1, "y": y1,
        "width": abs(x2-x1), "height": abs(y2-y1),
        "points": [[0, 0], [x2-x1, y2-y1]],
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2 if not dashed else 1,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 2, "opacity": 90,
        "angle": 0, "seed": random.randint(1, 99999),
        "version": 1, "versionNonce": 1,
        "isDeleted": False, "groupIds": [],
        "frameId": None, "roundness": {"type": 2},
        "startArrowhead": None, "endArrowhead": "arrow",
        "startBinding": None, "endBinding": None,
    }
    elements = [el]
    if label:
        mid_x = min(x1, x2) + abs(x2-x1)//2 - 40
        mid_y = min(y1, y2) + abs(y2-y1)//2 - 10
        elements.append(text(mid_x, mid_y, 100, 20, label, sz=11, color="#777777"))
    return elements

def zone(x, y, w, h, title, bg, content_lines, stroke=None,
         title_sz=16, content_sz=13, roughness=1):
    """Create a labelled zone with title and content lines."""
    if stroke is None:
        stroke = "#555555"
    els = []
    # Background rect
    els.append(rect(x, y, w, h, bg=bg, stroke=stroke, roughness=roughness, sw=2))
    # Title
    els.append(text(x+10, y+8, w-20, 28, title, sz=title_sz, bold=True, color="#222222"))
    # Divider under title
    els.append({**rect(x+10, y+36, w-20, 2, bg=stroke, stroke=stroke,
                       roughness=0, fill="solid", sw=1), "type": "line",
                "points": [[0,0],[w-20,0]]})
    # Content
    cy = y + 44
    for line in content_lines:
        if line == "---":  # separator
            els.append(rect(x+10, cy, w-20, 1, bg="#aaaaaa", stroke="#aaaaaa",
                            roughness=0, fill="solid", sw=1))
            cy += 8
            continue
        indent = 0
        display = line
        if line.startswith("  "):
            indent = 12
            display = line.strip()
        sz = content_sz - (2 if indent else 0)
        col = "#444444" if indent else "#1e1e1e"
        line_h = max(18, sz + 6)
        els.append(text(x+10+indent, cy, w-20-indent, line_h, display, sz=sz, color=col))
        cy += line_h + 2
    return els

def sub_zone(x, y, w, h, title, bg, lines, stroke=None, title_sz=13, content_sz=11):
    """Smaller nested sub-zone."""
    if stroke is None: stroke = "#888888"
    els = []
    els.append(rect(x, y, w, h, bg=bg, stroke=stroke, roughness=1, sw=1))
    els.append(text(x+8, y+5, w-16, 22, title, sz=title_sz, bold=True, color="#333333"))
    cy = y + 28
    for line in lines:
        display = line.strip()
        col = "#555555" if line.startswith("  ") else "#222222"
        els.append(text(x+8, cy, w-16, 17, display, sz=content_sz, color=col))
        cy += 18
    return els

# ── Build all elements ─────────────────────────────────────────────────────

elements = []

# Zone colours
C_BOOT    = "#C8DEFA"   # sky blue
C_HOOKS   = "#FBE99E"   # warm yellow
C_MEM     = "#DDD0F5"   # lavender
C_GOLDEN  = "#B6E8CE"   # mint green
C_BOOT2   = "#F8C8A8"   # peach (bootstrap)
C_AVG     = "#C4DDF8"   # sky blue (avengers)
C_PIPE    = "#C2D9B4"   # sage green
C_SKILLS  = "#BEE8CC"   # mint
C_MODEL   = "#D4C4F5"   # lilac
C_BUDGET  = "#F0BEBE"   # rose
C_PLUGINS = "#F0E0C0"   # sand
C_TIME    = "#F0EAD8"   # cream

# ── TITLE ──────────────────────────────────────────────────────────────────
elements.append(text(40, 10, 2900, 44,
    "Claude Code AI-Led Dev Environment",
    sz=36, bold=True, color="#1a1a2e", align="center"))
elements.append(text(40, 52, 2900, 24,
    "hot/cold memory  ·  code-review-graph  ·  golden/replay  ·  budget dial",
    sz=15, color="#666666", align="center"))

# ──────────────────────────────────────────────────────────────────────────
# ROW 1  (y=90)
# ──────────────────────────────────────────────────────────────────────────

# SESSION BOOT
elements += zone(40, 90, 670, 330, "☆ Session Boot", C_BOOT, [
    "• Claude Code starts  ☁",
    "• Load ~/.claude/CLAUDE.md",
    "   global rules + 20 skills",
    "• Load repo/.claude/CLAUDE.md",
    "   project context",
    "• Load hooks · Load MCPs",
    "• Load plugins",
])

# HOOKS LAYER
elements += zone(730, 90, 660, 330, "✨ Hooks Layer", C_HOOKS, [
    "• Token Optimization (RTK)",
    "   60–90% Bash output savings",
    "• OAuth Token Refresh",
    "   auto-refreshes MCP tokens",
    "• Telemetry Logging",
    "   grep fallback rate tracking",
    "• Self-Heal + Lesson Capture",
    "   corrections → lessons.md",
    "• Stop Record Cost",
    "   session $ → cost.jsonl",
    "• Daily Statusline",
    "   model · context % · 🟢🟡🔴",
])

# PER-PROJECT MEMORY
elements += zone(1410, 90, 680, 330, "☆ Per-Project Memory (Hot/Cold)", C_MEM, [])
# HOT sub-zone
elements += sub_zone(1425, 170, 648, 95, "🔥 HOT — auto-loaded on boot", "#EAD8FF", [
    "  hot.md — todos + lessons + arch summary",
    "  GRAPH_REPORT.md — code graph + MCP hints",
], stroke="#9B59B6")
# COLD sub-zone
elements += sub_zone(1425, 272, 648, 138, "❄ COLD — pull on demand (memory MCP)", "#E8E8FF", [
    "  lessons.md · architecture.md",
    "  history.md · todo.md",
    "  plans/ — session plans per repo",
    "  ↺ corrections → 3× = Pattern rule",
], stroke="#7777AA")

# /GOLDEN + /REPLAY
elements += zone(2110, 90, 680, 330, "☆ /golden + /replay", C_GOLDEN, [])
elements.append(text(2120, 100, 660, 20, "the compounding layer", sz=11, color="#888888"))
elements += sub_zone(2125, 150, 310, 175, "/golden save <slug>", "#D5F5E5", [
    "  distills validated session",
    "  Symptom · Root Cause",
    "  Steps That Worked",
    "  What NOT To Do",
    "  → ~/.claude/golden/<slug>.md",
], stroke="#2ECC71")
elements += sub_zone(2443, 150, 330, 175, "/replay <slug>", "#D5F5E5", [
    "  validates staleness",
    "  loads proven steps",
    "  as prior-art plan",
    "",
    "  'avoids re-deriving fixes'",
], stroke="#2ECC71")
elements += sub_zone(2125, 332, 648, 74, "💾 ~/.claude/golden/ + index.json", "#C8EFDC", [
    "  N patterns · tagged · dated",
    "  ← dashed: auto-prompts at wrap-up [y/n/edit]",
], stroke="#27AE60")

# ──────────────────────────────────────────────────────────────────────────
# ROW 2  (y=440)
# ──────────────────────────────────────────────────────────────────────────

# /BOOTSTRAP
elements += zone(40, 440, 670, 520, "⚙ /bootstrap — First Visit Only", C_BOOT2, [
    "runs once per repo · Opus + high effort",
    "---",
    "Phase 1: Detect stack",
    "  language + framework",
    "Phase 2: Seed memory",
    "  6 files + plans/",
    "Phase 3: Write project CLAUDE.md",
    "  + .mcp.json + .gitignore",
    "Phase 4: build-graph.sh",
    "  · install code-review-graph",
    "  · build SQLite graph",
    "  · compose GRAPH_REPORT.md",
    "Phase 5: Populate architecture.md",
    "  ← from GRAPH_REPORT.md",
])

# /AVENGERS — large zone
AVG_X, AVG_Y, AVG_W, AVG_H = 730, 440, 1370, 520
elements += zone(AVG_X, AVG_Y, AVG_W, AVG_H,
    "⚡ /avengers — Multi-Agent Orchestration", C_AVG, [])
elements.append(text(AVG_X+10, AVG_Y+38, AVG_W-20, 18,
    "Fury (Opus) orchestrates specialists (Sonnet) in parallel",
    sz=12, color="#555555"))

# Nick Fury sub-panel
elements += sub_zone(AVG_X+10, AVG_Y+62, 340, 240,
    "🎖 Nick Fury — Captain (Opus)", "#FDE68A", [
    "1. Get Jira ticket / requirement",
    "2. Research codebase",
    "   → write implementation plan",
    "3. Ask user to review plan",
    "4. Once approved →",
    "   spawn parallel subagents",
    "5. Validates gates",
    "   blocks bad code",
    "   shuts down on completion",
], stroke="#F59E0B", title_sz=12)

# Coders sub-panel
elements += sub_zone(AVG_X+360, AVG_Y+62, 220, 120,
    "💻 Coders ×N (Sonnet)", "#FED7AA", [
    "Parallel code writing",
    "Different task batches",
    "Write code per plan",
    "Verify build passes",
], stroke="#F97316", title_sz=11)

# Pipeline Specialists
elements += sub_zone(AVG_X+360, AVG_Y+192, 220, 110,
    "🔧 Pipeline Specialists", "#BBF7D0", [
    "Reviewer / Contact SME",
    "Validator",
    "Pre-Validation Agent",
    "code · tests · final gate",
], stroke="#10B981", title_sz=11)

# Human Review
elements += sub_zone(AVG_X+590, AVG_Y+62, 220, 150,
    "👤 Human Review", "#FECDD3", [
    "PR review before merge",
    "Approves or requests changes",
    "AI-assisted PR description",
    "",
    "← passes gate",
    "approved → merge",
], stroke="#EF4444", title_sz=11)

# /wrap-up on completion
elements += sub_zone(AVG_X+590, AVG_Y+222, 220, 132,
    "🔄 /wrap-up on Completion", "#99F6E4", [
    "Update Jira tickets",
    "Append to history",
    "Summarize session",
    "/golden save",
    "for future reference",
], stroke="#0EA5E9", title_sz=11)

# Bottom row inside avengers
elements += sub_zone(AVG_X+820, AVG_Y+62, 260, 100,
    "📊 Agent Dashboard", "#FEF3C7", [
    "live mission view",
    "real-time agent status",
], stroke="#D97706", title_sz=11)

elements += sub_zone(AVG_X+820, AVG_Y+172, 260, 100,
    "📄 State File", "#E0F2FE", [
    "/tmp/avengers-{TEAM}.json",
    "phase · agents · tasks · blocked",
], stroke="#0EA5E9", title_sz=11)

elements.append(text(AVG_X+820, AVG_Y+282, 260, 18,
    "Domain + Context", sz=12, bold=True, color="#555555"))

# Dedicated sub-agents
elements += sub_zone(AVG_X+10, AVG_Y+312, 1340, 60,
    "Dedicated sub agents — spawned on-demand by Fury:", "#E0F2FE", [
    "  [Solution-Architect]    [DE-Specialist]    [DevOps]    [NR-Expert]",
], stroke="#7DD3FC", title_sz=11)

# PROCESSING PIPELINE
elements += zone(2120, 440, 668, 520, "⚙ Processing Pipeline", C_PIPE, [])
elements += sub_zone(2135, 500, 638, 145, "🔷 code-review-graph", "#D4EDDA", [
    "Tree-sitter AST + SQLite",
    "28 MCP tools, auto-updates on Edit (<2s)",
    "semantic_search · get_impact_radius",
    "detect_changes · query_graph",
    "get_architecture_overview",
], stroke="#27AE60", title_sz=12)

elements += sub_zone(2135, 654, 638, 105, "🧠 memory MCP server", "#D8D0F8", [
    "pull-on-demand cold memory",
    "get_memory · search_memory",
    "list_lessons · get_todo · recall_plan",
], stroke="#8B5CF6", title_sz=12)

elements += sub_zone(2135, 768, 638, 178, "📋 /wrap-up  (6 phases)", "#C8F0D8", [
    "0: corrections audit",
    "1: append-history",
    "2: todo update",
    "3: lessons dedupe + CLAUDE.md promote",
    "3.5: golden auto-prompt",
    "4: CRG graph refresh",
    "5: mirror-plans + regen hot.md",
    "6: handoff summary",
], stroke="#059669", title_sz=12)

# ──────────────────────────────────────────────────────────────────────────
# ROW 3  (y=980)
# ──────────────────────────────────────────────────────────────────────────

# DOMAIN SKILLS
elements += zone(40, 980, 860, 360, "🎯 Domain Skills (20 total)", C_SKILLS, [
    "Auto-trigger on keyword or file path:",
    "  /airflow · /pyspark · /python · /sql · /shell",
    "  /docker · /cicd · /nrql · /nralert",
    "  /terraform · /openmetadata",
    "  /mcp-builder · /profiling",
    "---",
    "Explicit invoke using /skill_name:",
    "  /bootstrap · /wrap-up · /avengers",
    "  /golden · /replay · /budget · /demo",
    "---",
    "Superpowers:",
    "  ⚡ brainstorming · ⚡ systematic-debugging",
])

# MODEL × EFFORT
elements += zone(920, 980, 860, 360, "🧩 Model × Effort Routing", C_MODEL, [
    "default = sonnet+medium",
    "escalate per-turn, not per-session",
    "---",
    "Haiku 4.5  → lookups · NRQL · mechanical",
    "  (cheapest)",
    "Sonnet 4.6 → coding · testing · debugging",
    "  ★ DEFAULT",
    "Opus 4.7   → architecture · code review",
    "  multi-agent orchestration · brainstorming",
    "Opus+max   → novel research only (rare)",
    "---",
    "Avengers: Fury = Opus · Specialists = Sonnet",
])

# /BUDGET + PLUGINS
elements += zone(1800, 980, 600, 360, "🚦 /budget — Spend Dial", C_BUDGET, [
    "Caps: daily / weekly / monthly",
    "(budget.json)",
    "---",
    "🟢 <80%  — normal work",
    "🟡 80–100% — switch to Haiku",
    "🔴 >cap  — override required",
    "---",
    "Commands:",
    "  status · set · override · report",
])

elements += zone(2420, 980, 368, 360, "🔌 Plugins", C_PLUGINS, [
    "● nr-mcp",
    "● nr-kafka",
    "● terraform",
    "● code-review-graph",
    "● superpowers",
    "● jira",
    "● confluence",
    "● bedrock-retrieval",
])

# ──────────────────────────────────────────────────────────────────────────
# ROW 4 — TIMELINE  (y=1360)
# ──────────────────────────────────────────────────────────────────────────

elements += zone(40, 1360, 2748, 200, "Session Flow", C_TIME, [])

timeline_steps = [
    ("🔵 First Visit",
     "/bootstrap →\nmemory + CRG build\n+ seed"),
    ("🟢 Session Boot",
     "Load hooks +\nMCPs + plugins +\nhot.md + GRAPH_REPORT"),
    ("🟡 During Work",
     "graph-first work ·\nMCP tools ·\n/golden save · /replay\n· /avengers"),
    ("🔴 Session End",
     "/wrap-up (6 phases) ·\ngolden auto-prompt ·\nmirror-plans +\nregen hot.md"),
    ("🔵 Next Session",
     "smarter context ·\ngolden library grows ·\nstay in budget"),
]

step_w = 500
for i, (title, content) in enumerate(timeline_steps):
    sx = 80 + i * 540
    elements.append(rect(sx, 1390, step_w, 140,
                         bg=["#C8DEFA","#B8F0C8","#FBE99E","#F0BEBE","#C8DEFA"][i],
                         stroke="#888888", roughness=1, sw=1))
    elements.append(text(sx+10, 1395, step_w-20, 22, title, sz=13, bold=True))
    elements.append(text(sx+10, 1418, step_w-20, 100, content, sz=11, color="#555555"))
    if i < 4:
        elements += arrow(sx+step_w+2, 1460, sx+step_w+38, 1460,
                          color="#999999")

# Footer
elements.append(text(40, 1520, 2748, 30,
    "First Visit: bootstrap → memory + CRG build → seed  |  Every Session: boot → graph-first → /wrap-up → repeat  |  /golden save · /replay · /budget",
    sz=12, color="#888888", align="center"))

# ──────────────────────────────────────────────────────────────────────────
# KEY ARROWS (inter-zone connections)
# ──────────────────────────────────────────────────────────────────────────

# Session Boot → Memory (hot.md loads)
elements += arrow(375, 418, 1450, 200, "hot.md auto-loaded")

# /bootstrap → Memory (seeds)
elements += arrow(375, 680, 1450, 380, "seeds files", dashed=True)

# /bootstrap → Processing Pipeline (CRG)
elements += arrow(710, 600, 2120, 560, "builds graph", dashed=True)

# /wrap-up → Memory
elements += arrow(2455, 768, 2040, 380, "regen hot.md")

# Nick Fury → Coders
elements += arrow(AVG_X+350, AVG_Y+150, AVG_X+360, AVG_Y+120, color="#F97316")

# Pre-Validation → Human Review
elements += arrow(AVG_X+580, AVG_Y+246, AVG_X+590, AVG_Y+120, "passes gate →")

# Human Review → /wrap-up
elements += arrow(AVG_X+700, AVG_Y+212, AVG_X+700, AVG_Y+225, "approved →")

# ── Serialize ───────────────────────────────────────────────────────────────

excalidraw = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "viewBackgroundColor": "#F5EDD8",
        "gridSize": None,
        "currentItemFontFamily": FONT_HAND,
        "currentItemStrokeColor": "#1e1e1e",
        "currentItemBackgroundColor": "transparent",
        "currentItemFillStyle": "hachure",
        "currentItemStrokeWidth": 2,
        "currentItemRoughness": 1,
        "currentItemOpacity": 100,
    },
    "files": {}
}

with open(OUT, "w") as f:
    json.dump(excalidraw, f, indent=2)

print(f"✓  {len(elements)} elements → {OUT}")
print(f"\nOpen at: https://excalidraw.com")
print(f"  1. Go to excalidraw.com")
print(f"  2. Hamburger menu → Open → select architecture.excalidraw")
print(f"  3. Export → PNG or SVG (high resolution)")
