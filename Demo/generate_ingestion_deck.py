#!/usr/bin/env python3
"""
generate_ingestion_deck.py  —  v2 (rich, content-dense)

Generates:
  Ingestion-Team-AI-Led-Demo.pptx  (18 slides, NR branding, real content)
  Ingestion-Team-AI-Led-Demo.pdf   (via soffice)

Usage:
    python3 generate_ingestion_deck.py
"""

import os, subprocess
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Brand palette ─────────────────────────────────────────────────────────────
G     = RGBColor(0x00, 0xAC, 0x69)   # NR green  #00AC69
GLT   = RGBColor(0xE8, 0xF8, 0xF1)   # light green
GDK   = RGBColor(0x00, 0x6B, 0x40)   # dark green
W     = RGBColor(0xFF, 0xFF, 0xFF)
BK    = RGBColor(0x14, 0x14, 0x1E)   # near-black
GR    = RGBColor(0x55, 0x55, 0x66)   # body grey
LGR   = RGBColor(0xF0, 0xF0, 0xF4)   # very light grey bg
LN    = RGBColor(0xDD, 0xDD, 0xE8)   # rule line
TERM  = RGBColor(0x0E, 0x0E, 0x16)   # terminal dark bg
TCMD  = RGBColor(0x4A, 0xFF, 0x91)   # terminal green text
TGRY  = RGBColor(0x88, 0x99, 0x88)   # terminal grey comment
ATL   = RGBColor(0x00, 0x52, 0xCC)   # Atlassian blue
PUR   = RGBColor(0x7C, 0x3A, 0xED)   # purple (CRG)
YEL   = RGBColor(0xFF, 0xC8, 0x00)   # yellow badge
ORG   = RGBColor(0xFF, 0x7A, 0x00)   # orange badge
RED   = RGBColor(0xE8, 0x30, 0x40)   # red badge
NVY   = RGBColor(0x1A, 0x1A, 0x40)   # dark navy box

# Footer
FTR = "© 2025 New Relic, Inc. All rights reserved.  Confidential and proprietary.  For internal use only, not for external distribution."

SW = Inches(13.33)
SH = Inches(7.5)


# ── Core helpers ──────────────────────────────────────────────────────────────

def new_prs():
    p = Presentation()
    p.slide_width, p.slide_height = SW, SH
    return p

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def R(slide, x, y, w, h, fill=None, line=None, lw=Pt(0.75)):
    s = slide.shapes.add_shape(1, x, y, w, h)
    if fill: s.fill.solid(); s.fill.fore_color.rgb = fill
    else:    s.fill.background()
    if line: s.line.color.rgb = line; s.line.width = lw
    else:    s.line.fill.background()
    return s

def T(slide, text, x, y, w, h, sz=12, bold=False, color=BK,
      align=PP_ALIGN.LEFT, italic=False, font="Calibri", wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = wrap
    p  = tf.paragraphs[0]; p.alignment = align
    r  = p.add_run()
    r.text = text; r.font.size = Pt(sz); r.font.bold = bold
    r.font.italic = italic; r.font.color.rgb = color; r.font.name = font
    return tb

def Tmono(slide, text, x, y, w, h, sz=10, color=TCMD):
    return T(slide, text, x, y, w, h, sz=sz, color=color, font="Courier New")

def ftr(slide):
    T(slide, FTR,         Inches(0.3),  Inches(7.06), Inches(11.9), Inches(0.38), sz=7,  color=GR)
    T(slide, "⬢ new relic", Inches(11.8), Inches(7.01), Inches(1.4), Inches(0.42), sz=10, bold=True, color=G, align=PP_ALIGN.RIGHT)

def hdr(slide, title, h=Inches(0.70)):
    R(slide, 0, 0, SW, h, fill=G)
    T(slide, title, Inches(0.4), Inches(0.07), Inches(12.5), h-Inches(0.07),
      sz=24, bold=True, color=W, align=PP_ALIGN.CENTER)

def HL(slide, x, y, w, c=LN):
    R(slide, x, y, w, Inches(0.016), fill=c)

def badge(slide, label, x, y, color=G, sz=9):
    R(slide, x, y, Inches(1.5), Inches(0.3), fill=color)
    T(slide, label, x+Inches(0.05), y+Inches(0.02), Inches(1.4), Inches(0.28),
      sz=sz, bold=True, color=W, align=PP_ALIGN.CENTER)

def term_box(slide, lines, x, y, w, h):
    """Dark terminal box with green monospace text."""
    R(slide, x, y, w, h, fill=TERM)
    R(slide, x, y, w, Inches(0.28), fill=RGBColor(0x22,0x22,0x2E))  # title bar
    for i, (dot_color, _) in enumerate([(RED, ""), (YEL, ""), (G, "")]):
        R(slide, x+Inches(0.12+i*0.22), y+Inches(0.07), Inches(0.14), Inches(0.14), fill=dot_color)
    cy = y + Inches(0.36)
    for line in lines:
        col = TGRY if line.startswith("#") else (G if line.startswith("$") or line.startswith("→") else TCMD)
        Tmono(slide, line, x+Inches(0.15), cy, w-Inches(0.3), Inches(0.26), sz=9.5, color=col)
        cy += Inches(0.27)

def col_box(slide, x, y, w, h, title, bullets, fill=LGR, title_color=BK, bullet_color=GR,
            border=None, title_sz=12, bullet_sz=10.5):
    R(slide, x, y, w, h, fill=fill, line=border, lw=Pt(1))
    T(slide, title, x+Inches(0.15), y+Inches(0.12), w-Inches(0.3), Inches(0.38),
      sz=title_sz, bold=True, color=title_color)
    cy = y + Inches(0.56)
    for b in bullets:
        T(slide, b, x+Inches(0.15), cy, w-Inches(0.3), Inches(0.3), sz=bullet_sz, color=bullet_color)
        cy += Inches(0.31)

def dark_box(slide, x, y, w, h, title, sub=None):
    R(slide, x, y, w, h, fill=NVY)
    T(slide, title, x+Inches(0.15), y+Inches(0.13), w-Inches(0.3), Inches(0.4),
      sz=13, bold=True, color=W, align=PP_ALIGN.CENTER)
    if sub:
        T(slide, sub, x+Inches(0.15), y+Inches(0.52), w-Inches(0.3), Inches(0.3),
          sz=10, color=G, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDES
# ══════════════════════════════════════════════════════════════════════════════

def s01_title(prs):
    slide = blank(prs)
    # Green gradient bar left
    R(slide, 0, 0, Inches(0.5), SH, fill=G)
    R(slide, Inches(0.5), 0, Inches(0.08), SH, fill=GLT)
    # Top accent
    R(slide, 0, 0, SW, Inches(0.04), fill=G)
    # Right panel
    R(slide, Inches(8.8), Inches(0.04), Inches(4.53), SH-Inches(0.04), fill=GLT)

    T(slide, "⬢ new relic", Inches(0.75), Inches(0.3), Inches(3), Inches(0.5), sz=20, bold=True, color=G)

    T(slide, "Ingestion Team",
      Inches(0.75), Inches(1.4), Inches(7.8), Inches(0.7), sz=32, bold=True, color=BK)
    T(slide, "AI-Led Development Environment",
      Inches(0.75), Inches(2.1), Inches(7.8), Inches(0.65), sz=28, bold=True, color=G)
    T(slide, "Claude Code  +  GitHub Copilot",
      Inches(0.75), Inches(2.82), Inches(7.8), Inches(0.48), sz=20, color=GR)

    HL(slide, Inches(0.75), Inches(3.38), Inches(6.5), G)

    items = [
        ("🚀", "5× faster feature delivery"),
        ("🧠", "Day-1 onboarding via /bootstrap"),
        ("🔍", "30-second NR incident diagnosis"),
        ("⚡", "Multi-agent parallel work with /avengers"),
        ("📦", "Replayable golden patterns — knowledge that compounds"),
    ]
    y = Inches(3.55)
    for icon, txt_s in items:
        T(slide, icon, Inches(0.75), y, Inches(0.45), Inches(0.34), sz=14)
        T(slide, txt_s, Inches(1.28), y+Inches(0.02), Inches(6.2), Inches(0.34), sz=13, color=BK)
        y += Inches(0.4)

    # Right panel content
    boxes = [
        ("20 Skills",         "auto-trigger on file type",    G),
        ("28 CRG tools",      "code-review-graph MCP",        PUR),
        ("12+ NR MCP tools",  "live observability",           ATL),
        ("Memory + Goldens",  "knowledge that compounds",     GDK),
        ("Budget dial",       "🟢 🟡 🔴 daily spend cap",     ORG),
    ]
    y = Inches(1.2)
    for title, sub, color in boxes:
        R(slide, Inches(9.1), y, Inches(3.9), Inches(0.9), fill=W, line=LN, lw=Pt(0.75))
        R(slide, Inches(9.1), y, Inches(0.1), Inches(0.9), fill=color)
        T(slide, title, Inches(9.3), y+Inches(0.08), Inches(3.55), Inches(0.35), sz=14, bold=True)
        T(slide, sub,   Inches(9.3), y+Inches(0.44), Inches(3.55), Inches(0.32), sz=10, color=GR)
        y += Inches(1.05)

    ftr(slide)


def s02_problem(prs):
    slide = blank(prs)
    hdr(slide, "The Problem — Four Pains We Were Living With Every Week")

    pains = [
        ("🕐", "Onboarding: 2+ Weeks",
         "New engineers spent 2 weeks asking Slack, grepping git history,\nand re-deriving patterns that lived in people's heads.",
         "Cost: ~4 eng-weeks/year per team"),
        ("🔍", "Incident Diagnosis: 2–3 Hours",
         "Alert fires at 2am → manual NR UI hunt → log grep →\nSlack teammates → hypothesis → repeat.",
         "Cost: ~12h/year MTTR overhead (before fix time)"),
        ("💥", "Blast Radius: Invisible",
         "'1-day fix' became a 5-day incident because nobody knew\nwhat else would break before a line was written.",
         "Cost: ~1 sprint/quarter absorbed in rework"),
        ("🗂", "Architecture: In People's Heads",
         "Knowledge in Slack threads and the senior engineer's memory.\nEvery off-boarding = weeks of lost context.",
         "Cost: exponential as team grows"),
    ]

    y = Inches(0.85)
    cols = [(Inches(0.4), Inches(0.95)), (Inches(6.9), Inches(0.95)),
            (Inches(0.4), Inches(3.8)),  (Inches(6.9), Inches(3.8))]

    for (emoji, title, desc, cost), (x, y) in zip(pains, cols):
        R(slide, x, y, Inches(6.1), Inches(2.7), fill=W, line=LN, lw=Pt(1))
        R(slide, x, y, Inches(6.1), Inches(0.08), fill=G)           # top accent bar
        T(slide, emoji+" "+title, x+Inches(0.2), y+Inches(0.18), Inches(5.7), Inches(0.42),
          sz=15, bold=True)
        T(slide, desc, x+Inches(0.2), y+Inches(0.65), Inches(5.7), Inches(1.1), sz=11, color=GR)
        R(slide, x, y+Inches(1.85), Inches(6.1), Inches(0.7), fill=GLT)
        T(slide, cost, x+Inches(0.2), y+Inches(1.9), Inches(5.7), Inches(0.5),
          sz=11, bold=True, color=GDK)
    ftr(slide)


def s03_two_tools(prs):
    slide = blank(prs)
    hdr(slide, "Our Answer: Two AI Tools, One Team — Each Does What It Does Best")

    # Copilot column
    R(slide, Inches(0.4), Inches(0.85), Inches(5.9), Inches(5.6), fill=LGR, line=LN, lw=Pt(1))
    R(slide, Inches(0.4), Inches(0.85), Inches(5.9), Inches(0.52), fill=RGBColor(0x24,0x29,0x38))
    T(slide, "GitHub Copilot", Inches(0.6), Inches(0.9), Inches(5.5), Inches(0.4),
      sz=18, bold=True, color=W)
    cpitems = [
        ("✓", "Line & function autocomplete in IDE"),
        ("✓", "Inline chat: explain this function"),
        ("✓", "Generate boilerplate fast"),
        ("✓", "Test skeleton generation"),
        ("✓", "Rename / refactor suggestions"),
        ("", ""),
        ("×", "No codebase memory across sessions"),
        ("×", "Can't query NR, Jira, Confluence"),
        ("×", "No blast-radius analysis"),
        ("×", "No multi-agent parallelism"),
    ]
    y = Inches(1.5)
    for icon, item in cpitems:
        if not item:
            HL(slide, Inches(0.6), y, Inches(5.5))
            y += Inches(0.18)
            continue
        color = G if icon == "✓" else RED
        T(slide, icon, Inches(0.6), y, Inches(0.35), Inches(0.3), sz=12, bold=True, color=color)
        T(slide, item, Inches(1.0), y, Inches(5.0), Inches(0.3), sz=11, color=BK)
        y += Inches(0.36)

    # Claude Code column
    R(slide, Inches(7.0), Inches(0.85), Inches(5.9), Inches(5.6), fill=GLT, line=G, lw=Pt(1.5))
    R(slide, Inches(7.0), Inches(0.85), Inches(5.9), Inches(0.52), fill=G)
    T(slide, "Claude Code (our environment)", Inches(7.2), Inches(0.9), Inches(5.5), Inches(0.4),
      sz=18, bold=True, color=W)
    ccitems = [
        ("✓", "Investigation: queries NR, Jira, Confluence live"),
        ("✓", "Memory: hot.md loads full context at session start"),
        ("✓", "Blast radius: get_impact_radius before writing code"),
        ("✓", "/avengers: 5 parallel agents on one task"),
        ("✓", "/golden + /replay: compounding pattern library"),
        ("", ""),
        ("✓", "20 skills auto-trigger on file path / topic"),
        ("✓", "Model routing: Haiku → Sonnet → Opus by task"),
        ("✓", "Budget dial: 🟢🟡🔴 daily spend awareness"),
        ("✓", "Hooks: self-heal, cost record, MCP token refresh"),
    ]
    y = Inches(1.5)
    for icon, item in ccitems:
        if not item:
            HL(slide, Inches(7.2), y, Inches(5.5), G)
            y += Inches(0.18)
            continue
        T(slide, icon, Inches(7.2), y, Inches(0.35), Inches(0.3), sz=12, bold=True, color=G)
        T(slide, item, Inches(7.6), y, Inches(5.0), Inches(0.3), sz=11, color=BK)
        y += Inches(0.36)

    # Bridge
    T(slide, "→", Inches(6.15), Inches(3.4), Inches(0.7), Inches(0.6),
      sz=28, bold=True, color=G, align=PP_ALIGN.CENTER)
    T(slide, "Together", Inches(6.0), Inches(4.0), Inches(1.0), Inches(0.35),
      sz=10, bold=True, color=G, align=PP_ALIGN.CENTER)

    ftr(slide)


def s04_architecture(prs):
    slide = blank(prs)
    hdr(slide, "Three-Layer Architecture — Global → Project → Repo")

    layers = [
        ("GLOBAL  ~/.claude/",
         [" CLAUDE.md      ← rules: security, model routing, workflows",
          " budget.json    ← daily=$50  weekly=$120  monthly=$300",
          " golden/        ← reusable session patterns + index.json",
          " skills/        ← 20 skills (lang + domain + meta workflow)",
          " hooks/         ← rtk, statusline, self-heal, cost-record",
          " telemetry/     ← cost.jsonl  greps.jsonl"],
         G, W),
        ("PROJECT  ~/.claude/projects/<REPO_NAME>/",
         [" memory/hot.md           ← AUTO-LOADED ~2k tokens (session start)",
          " memory/lessons.md       ← patterns, wins, anti-patterns",
          " memory/architecture.md  ← derived from GRAPH_REPORT.md",
          " memory/history.md       ← append-only session log",
          " graphs/GRAPH_REPORT.md  ← AUTO-LOADED CRG summary + MCP hints",
          " plans/                  ← mirrored from ~/.claude/plans/ at /wrap-up"],
         GDK, W),
        ("REPO  <repo>/",
         [" .claude/CLAUDE.md  ← only 2 @ refs → hot.md + GRAPH_REPORT.md (~4k total)",
          " .mcp.json          ← memory-server + code-review-graph MCP",
          " .code-review-graph/ ← SQLite AST graph (auto-updates on Edit)",
          " .gitignore         ← .claude/, .mcp.json, .code-review-graph/"],
         PUR, W),
    ]

    y = Inches(0.82)
    for heading, lines, bg, fg in layers:
        h = Inches(0.3 + len(lines) * 0.3)
        R(slide, Inches(0.4), y, SW - Inches(0.8), h, fill=TERM)
        R(slide, Inches(0.4), y, SW - Inches(0.8), Inches(0.32), fill=bg)
        T(slide, heading, Inches(0.6), y+Inches(0.03), Inches(11.5), Inches(0.28),
          sz=12, bold=True, color=fg, font="Courier New")
        for i, line in enumerate(lines):
            Tmono(slide, line, Inches(0.6), y+Inches(0.38+i*0.30), Inches(11.5), Inches(0.26),
                  sz=9.5, color=TCMD)
        y += h + Inches(0.22)

    R(slide, Inches(0.4), y, SW-Inches(0.8), Inches(0.42), fill=GLT, line=G, lw=Pt(1))
    T(slide, "Session-start token cost:  Before = 10–30k tokens (5 @-loaded files)  →  After = ~4k tokens (hot.md + GRAPH_REPORT.md)  —  3–7× cheaper",
      Inches(0.6), y+Inches(0.06), Inches(12.1), Inches(0.34),
      sz=11, bold=True, color=GDK, align=PP_ALIGN.CENTER)
    ftr(slide)


def s05_install(prs):
    slide = blank(prs)
    hdr(slide, "5 Minutes to a Fully-Wired Team Environment")

    term_box(slide, [
        "# ── Install (one-time, per engineer) ────────────────────────────",
        "$ git clone git@github.com:nr-mdakilahmed/claude_code_setup.git ~/claude_code_setup",
        "$ cd ~/claude_code_setup && ./install.sh",
        "",
        "→ Checks: claude  python3  git  jq  pipx  uv  (fatal if missing)",
        "→ Installs code-review-graph via pipx  (Tree-sitter AST + 28 MCP tools)",
        "→ Syncs memory-server  (pull-on-demand project memory via uvx)",
        "→ Copies 20 skills to ~/.claude/skills/",
        "→ Copies hooks: rtk, statusline, self-heal, cost-record, MCP refresh",
        "→ Merges settings.template.json into ~/.claude/settings.json",
        "→ Seeds ~/.claude/budget.json  +  golden/index.json",
        "",
        "$ ./verify.sh          # end-to-end check: prereqs + skills + hooks + MCPs",
        "",
        "# ── First visit to a repo ────────────────────────────────────────",
        "$ cd ~/Documents/GitHub/om-airflow-dags",
        "$ claude                # opens Claude Code",
        "> /bootstrap            # Opus: detect stack → seed memory → build graph → wire MCPs",
        "",
        "# ── Every session end ────────────────────────────────────────────",
        "> /wrap-up              # persist history, lessons, refresh graph, regen hot.md",
    ], Inches(0.4), Inches(0.82), Inches(12.5), Inches(6.0))

    ftr(slide)


def s06_skills(prs):
    slide = blank(prs)
    hdr(slide, "20 Skills — Context-Aware by Default, Explicit When You Need Them")

    # Meta / workflow
    T(slide, "META / WORKFLOW  (7 — explicit /command only)",
      Inches(0.4), Inches(0.82), Inches(6.0), Inches(0.35), sz=11, bold=True, color=GDK)
    meta = [
        ("/bootstrap",  "First visit: detect stack, seed memory, build graph, wire MCPs"),
        ("/wrap-up",    "Session end: history + todos + lessons + graph refresh + hot.md"),
        ("/avengers",   "Opus orchestrates Sonnet specialists in parallel — for complex tasks"),
        ("/golden",     "save | list | validate — capture reusable session templates"),
        ("/replay",     "Load saved golden as prior-art for a matching task"),
        ("/budget",     "status | set | override | report — daily/weekly/monthly spend"),
        ("/demo",       "45-minute demo prep: problem-first, 5 acts, objection scripts"),
    ]
    y = Inches(1.18)
    for cmd, desc in meta:
        R(slide, Inches(0.4), y, Inches(5.9), Inches(0.34), fill=LGR, line=LN, lw=Pt(0.5))
        T(slide, cmd,  Inches(0.55), y+Inches(0.04), Inches(1.4), Inches(0.28), sz=11, bold=True, color=G, font="Courier New")
        T(slide, desc, Inches(1.85), y+Inches(0.04), Inches(4.3), Inches(0.28), sz=10, color=BK)
        y += Inches(0.35)

    # Language
    T(slide, "LANGUAGE / FRAMEWORK  (7 — auto-trigger on file paths)",
      Inches(6.75), Inches(0.82), Inches(6.2), Inches(0.35), sz=11, bold=True, color=PUR)
    lang = [
        ("/airflow",   "**/ dags/**/*.py,  **/plugins/**/*.py"),
        ("/pyspark",   "**/spark/**/*.py,  **/*_spark.py"),
        ("/python",    "**/*.py,  pyproject.toml,  requirements*.txt"),
        ("/sql",       "**/*.sql,  dbt models,  schema.yml"),
        ("/shell",     "**/*.sh,  **/*.bash"),
        ("/docker",    "**/Dockerfile*,  **/docker-compose*.yml"),
        ("/cicd",      ".github/workflows/*.yml,  .pre-commit-config.yaml"),
    ]
    y = Inches(1.18)
    for cmd, paths in lang:
        R(slide, Inches(6.75), y, Inches(6.2), Inches(0.34), fill=RGBColor(0xF5,0xF0,0xFF), line=LN, lw=Pt(0.5))
        T(slide, cmd,   Inches(6.9),  y+Inches(0.04), Inches(1.35), Inches(0.28), sz=11, bold=True, color=PUR, font="Courier New")
        T(slide, paths, Inches(8.25), y+Inches(0.04), Inches(4.5),  Inches(0.28), sz=9.5, color=GR, font="Courier New")
        y += Inches(0.35)

    # Domain
    HL(slide, Inches(0.4), Inches(3.7), Inches(12.5))
    T(slide, "DOMAIN  (6 — auto-trigger on topic keyword in prompt)",
      Inches(0.4), Inches(3.76), Inches(12.5), Inches(0.32), sz=11, bold=True, color=ATL)
    domain = [
        ("/nrql",         "NRQL / New Relic query"),
        ("/nralert",      "alerts, muting rules, incidents"),
        ("/terraform",    "**/*.tf  or terraform mention"),
        ("/openmetadata", "ingestion yamls or OpenMetadata"),
        ("/mcp-builder",  "MCP server / tool design"),
        ("/profiling",    "cProfile / py-spy / slow Python"),
    ]
    cols = [(Inches(0.4), Inches(4.1)), (Inches(4.5), Inches(4.1)), (Inches(8.6), Inches(4.1))]
    for i, (cmd, trigger) in enumerate(domain):
        x, y = cols[i % 3]
        if i >= 3:
            y += Inches(0.56)
        R(slide, x, y, Inches(3.75), Inches(0.46), fill=RGBColor(0xEE,0xF4,0xFF), line=LN, lw=Pt(0.5))
        T(slide, cmd,     x+Inches(0.1), y+Inches(0.06), Inches(1.4), Inches(0.34), sz=11, bold=True, color=ATL, font="Courier New")
        T(slide, trigger, x+Inches(1.6), y+Inches(0.08), Inches(2.0), Inches(0.30), sz=10, color=GR)

    ftr(slide)


def s07_session_loop(prs):
    slide = blank(prs)
    hdr(slide, "The Daily Habit — /bootstrap Once, /wrap-up Every Session")

    # Big loop diagram
    loop_steps = [
        ("1  /bootstrap\n(once per repo)", G),
        ("2  Open Claude Code\n in repo", GDK),
        ("3  Work\n(skills auto-trigger)", PUR),
        ("4  /wrap-up\n(session end)", ATL),
    ]
    xs = [Inches(1.2), Inches(4.5), Inches(7.8), Inches(11.1)]
    for i, ((title, color), x) in enumerate(zip(loop_steps, xs)):
        R(slide, x, Inches(1.0), Inches(2.8), Inches(1.6), fill=color)
        T(slide, title, x+Inches(0.1), Inches(1.2), Inches(2.6), Inches(1.2),
          sz=13, bold=True, color=W, align=PP_ALIGN.CENTER)
        if i < 3:
            T(slide, "→", Inches(x.inches+2.9), Inches(1.55), Inches(0.5), Inches(0.5),
              sz=22, bold=True, color=G, align=PP_ALIGN.CENTER)

    # /bootstrap detail
    T(slide, "/bootstrap phases (~15s):", Inches(0.4), Inches(2.85), Inches(5.9), Inches(0.35), sz=12, bold=True)
    for i, phase in enumerate([
        "Phase 1  detect-stack.sh → classify language + framework",
        "Phase 2  seed-memory.sh  → 6 memory files + plans/ dir",
        "Phase 3  write-project-claude.sh → .claude/CLAUDE.md + .mcp.json",
        "Phase 4  build-graph.sh  → CRG install + build + GRAPH_REPORT.md",
        "Phase 5  populate architecture.md from GRAPH_REPORT.md",
    ]):
        Tmono(slide, phase, Inches(0.4), Inches(3.22+i*0.32), Inches(5.9), Inches(0.28), sz=9.5)

    # /wrap-up detail
    T(slide, "/wrap-up phases (~10s):", Inches(6.9), Inches(2.85), Inches(6.0), Inches(0.35), sz=12, bold=True)
    for i, phase in enumerate([
        "Phase 0   corrections audit → lessons.md",
        "Phase 1   append-history → new ## <date> block",
        "Phase 2   todo update → Active/Backlog/Done",
        "Phase 3   lessons dedupe → promote to CLAUDE.md",
        "Phase 3.5 golden check (auto-prompt if 3 signals present)",
        "Phase 4   code-review-graph update + regen GRAPH_REPORT.md",
        "Phase 5   mirror-plans + regenerate hot.md",
        "Phase 6   handoff summary with counts",
    ]):
        Tmono(slide, phase, Inches(6.9), Inches(3.22+i*0.32), Inches(6.0), Inches(0.28), sz=9.5)

    HL(slide, Inches(0.4), Inches(6.52), Inches(12.5))
    T(slide, "hot.md is ~2k tokens (session start) · history.md, lessons.md, architecture.md are pull-on-demand via memory MCP · knowledge compounds across sessions",
      Inches(0.4), Inches(6.58), Inches(12.5), Inches(0.34), sz=10, color=GR, align=PP_ALIGN.CENTER)
    ftr(slide)


def s08_memory(prs):
    slide = blank(prs)
    hdr(slide, "Memory That Doesn't Decay — Knowledge Compounds Across Every Session")

    layers = [
        ("ALWAYS LOADED AT SESSION START",
         "hot.md  (~2k tokens)",
         "Active todos (top 10) + recent lessons (last 10) + architecture summary.\n"
         "/wrap-up regenerates it every session from the live memory files.",
         G, W, True),
        ("PULL ON DEMAND  (via memory MCP server)",
         "lessons.md  ·  architecture.md  ·  history.md  ·  todo.md  ·  plans/",
         "get_memory(topic) · search_memory(query) · list_lessons(tag) · get_todo(status) · recall_plan(slug)\n"
         "Retrieved only when relevant — avoids drowning in stale context, 100–500 tokens/call.",
         GDK, W, False),
        ("REPLAYABLE GOLDEN PATTERNS",
         "~/.claude/golden/<slug>.md  (indexed in golden/index.json)",
         "/golden save kafka-consumer-lag-fix  →  distills session into schema: Symptom · Root Cause · Steps That Worked · What NOT To Do\n"
         "/replay kafka-consumer-lag-fix  →  validates file refs, loads as prior-art plan",
         PUR, W, False),
    ]

    y = Inches(0.82)
    for tier, title, desc, fill, fg, auto in layers:
        h = Inches(1.62)
        R(slide, Inches(0.4), y, Inches(12.5), h, fill=fill, line=(None if auto else LN), lw=Pt(1))
        badge(slide, "AUTO-LOADED" if auto else "PULL ON DEMAND" if "DEMAND" in tier else "REPLAYABLE",
              Inches(0.55), y+Inches(0.12),
              color=(RGBColor(0xFF,0xC8,0x00) if auto else GDK if "DEMAND" in tier else PUR), sz=8)
        T(slide, title, Inches(2.3), y+Inches(0.12), Inches(10.4), Inches(0.38),
          sz=15, bold=True, color=fg)
        T(slide, desc, Inches(0.55), y+Inches(0.6), Inches(12.1), Inches(0.9),
          sz=11, color=(W if fill in (G,GDK,PUR) else BK))
        y += h + Inches(0.1)

    R(slide, Inches(0.4), y+Inches(0.05), Inches(12.5), Inches(0.44), fill=GLT, line=G, lw=Pt(1))
    T(slide, "Month 1: 8 blocking issues/task  →  Month 3: 1–2.  Every session the system gets sharper, not staler.",
      Inches(0.6), y+Inches(0.12), Inches(12.1), Inches(0.34), sz=12, bold=True, color=GDK, align=PP_ALIGN.CENTER)
    ftr(slide)


def s09_nr_mcp(prs):
    slide = blank(prs)
    hdr(slide, "NR MCP: 2-Hour Incident Hunt → 30-Minute Root Cause")

    # Before
    R(slide, Inches(0.4), Inches(0.85), Inches(5.85), Inches(5.45), fill=W, line=LN, lw=Pt(1))
    R(slide, Inches(0.4), Inches(0.85), Inches(5.85), Inches(0.04), fill=RED)
    T(slide, "BEFORE  —  Manual NR UI", Inches(0.6), Inches(0.95), Inches(5.5), Inches(0.38), sz=15, bold=True)
    term_box(slide, [
        "# Alert fires 2am  →  you open NR UI",
        "",
        "1. Navigate to entity manually",
        "2. Logs tab → scroll → ctrl+F 'error'",
        "3. Metrics tab → compare time ranges",
        "4. Traces → click through spans",
        "5. Slack teammates for context",
        "6. Form hypothesis → test → repeat",
        "",
        "⏱  avg: 2–3 hours to root cause",
    ], Inches(0.45), Inches(1.42), Inches(5.75), Inches(3.95))
    R(slide, Inches(0.4), Inches(5.5), Inches(5.85), Inches(0.65), fill=RGBColor(0xFF,0xEE,0xEE))
    T(slide, "Lost: sleep, momentum, time to fix", Inches(0.6), Inches(5.6), Inches(5.5), Inches(0.42),
      sz=12, bold=True, color=RED)

    T(slide, "→", Inches(6.35), Inches(3.3), Inches(0.6), Inches(0.5),
      sz=32, bold=True, color=G, align=PP_ALIGN.CENTER)

    # After
    R(slide, Inches(7.05), Inches(0.85), Inches(5.85), Inches(5.45), fill=GLT, line=G, lw=Pt(1.5))
    R(slide, Inches(7.05), Inches(0.85), Inches(5.85), Inches(0.04), fill=G)
    T(slide, "AFTER  —  Claude Code + NR MCP", Inches(7.25), Inches(0.95), Inches(5.5), Inches(0.38),
      sz=15, bold=True, color=GDK)
    term_box(slide, [
        "# Same alert, same 2am",
        "",
        '> "analyze kafka consumer lag last 4h"',
        "",
        "→ analyze_kafka_metrics(entity_guid)",
        "  consumer_lag: 847,293  (↑ 12×)",
        "  partition_balance: 3 of 8 skewed",
        "  throughput: dropped 89% at 01:47",
        "",
        "→ get_impact_radius('spark_ingest.py')",
        "  callers: 2,  affected_flows: 4",
        "  downstream: om_airflow_daily_dag",
        "",
        "⏱  30 minutes to root cause + scoped fix",
    ], Inches(7.1), Inches(1.42), Inches(5.75), Inches(3.95))
    R(slide, Inches(7.05), Inches(5.5), Inches(5.85), Inches(0.65), fill=GLT)
    T(slide, "NR MCP tools: analyze_kafka_metrics · analyze_entity_logs · analyze_golden_metrics\nlist_recent_issues · get_distributed_trace_details · execute_nrql_query · list_entity_error_groups",
      Inches(7.25), Inches(5.52), Inches(5.5), Inches(0.6), sz=9, color=GDK)
    ftr(slide)


def s10_graph(prs):
    slide = blank(prs)
    hdr(slide, "Code-Review-Graph: Blast Radius Before You Write a Line")

    # What it is
    T(slide, "code-review-graph  —  Tree-sitter AST + SQLite + 28 MCP tools per repo  (auto-builds on /bootstrap, auto-updates on every Edit)",
      Inches(0.4), Inches(0.82), Inches(12.5), Inches(0.36), sz=11, bold=True, color=PUR)

    # Flow
    steps = [
        ("You edit\nspark_ingest.py", W, BK, LN),
        ("get_impact_\nradius()", PUR, W, PUR),
        ("Callers: 2\nFlows: 4\nConsumers: 1", GLT, GDK, G),
        ("Fix scoped.\nShip safely.", G, W, G),
    ]
    for i, (label, fill, tc, border) in enumerate(steps):
        x = Inches(0.4 + i * 3.2)
        R(slide, x, Inches(1.3), Inches(2.9), Inches(1.7), fill=fill, line=border, lw=Pt(1.5))
        T(slide, label, x+Inches(0.1), Inches(1.6), Inches(2.7), Inches(1.1),
          sz=13, bold=True, color=tc, align=PP_ALIGN.CENTER, font="Courier New" if i in (1,) else "Calibri")
        if i < 3:
            T(slide, "→", Inches(3.35+i*3.2), Inches(1.95), Inches(0.5), Inches(0.5),
              sz=24, bold=True, color=G, align=PP_ALIGN.CENTER)

    # Key tools grid
    T(slide, "28 MCP tools — key ones:", Inches(0.4), Inches(3.22), Inches(12.5), Inches(0.35), sz=12, bold=True)
    tools = [
        ("get_impact_radius",      "Blast radius of a change — callers, callees, affected flows"),
        ("detect_changes",         "Risk-scored review: what changed and what it touches"),
        ("query_graph",            "callers_of / callees_of / imports_of / tests_for / file_summary"),
        ("semantic_search_nodes",  "Find functions/classes by name or semantic similarity"),
        ("get_affected_flows",     "Which execution paths pass through changed files"),
        ("get_architecture_overview", "High-level community structure + coupling analysis"),
        ("get_review_context",     "Token-efficient review: source + impact in one call"),
        ("refactor_tool",          "rename preview / dead_code scan / suggest misplaced functions"),
    ]
    y = Inches(3.62)
    for i, (name, desc) in enumerate(tools):
        x = Inches(0.4) if i % 2 == 0 else Inches(6.8)
        if i % 2 == 0 and i > 0:
            y += Inches(0.42)
        R(slide, x, y, Inches(6.0), Inches(0.38), fill=RGBColor(0xF5,0xF0,0xFF), line=LN, lw=Pt(0.5))
        T(slide, name, x+Inches(0.1), y+Inches(0.04), Inches(2.4), Inches(0.3),
          sz=10, bold=True, color=PUR, font="Courier New")
        T(slide, desc, x+Inches(2.6), y+Inches(0.05), Inches(3.25), Inches(0.28), sz=10, color=BK)

    ftr(slide)


def s11_avengers(prs):
    slide = blank(prs)
    hdr(slide, "/avengers — Multi-Agent Orchestration for Tasks Too Big for One Pass")

    # Fury
    dark_box(slide, Inches(4.3), Inches(0.85), Inches(4.7), Inches(0.9),
             "Nick Fury  (Opus — Orchestrator)",
             "Routes work · validates gates · blocks bad code · shuts down on completion")

    # Specialists
    specs = [
        ("strange-architect\n(design + API contracts)", PUR),
        ("stark-engineer-1…N\n(Sonnet, parallel coders)", G),
        ("natasha-reviewer\n(code + security review)", ATL),
        ("hawkeye-validator\n(tests + blast radius)", GDK),
    ]
    xs = [Inches(0.3), Inches(3.6), Inches(6.9), Inches(10.2)]
    for (title, color), x in zip(specs, xs):
        R(slide, x, Inches(2.1), Inches(3.0), Inches(1.5), fill=color)
        T(slide, title, x+Inches(0.1), Inches(2.3), Inches(2.8), Inches(1.1),
          sz=11, bold=True, color=W, align=PP_ALIGN.CENTER)

    # Optional specialists
    T(slide, "Optional domain specialists (spawned on demand by Fury):",
      Inches(0.3), Inches(3.78), Inches(12.7), Inches(0.32), sz=11, bold=True, color=GR)
    opt = ["rogers-data-engineer (pipelines, ETL, warehouse)",
           "maximoff-python-engineer (PySpark, Airflow, pandas)",
           "thor-devops (Terraform, CI/CD, K8s)"]
    for i, s in enumerate(opt):
        T(slide, "· "+s, Inches(0.3+i*4.3), Inches(4.1), Inches(4.1), Inches(0.28), sz=10, color=BK)

    # Real example
    R(slide, Inches(0.3), Inches(4.48), Inches(12.7), Inches(2.1), fill=TERM)
    Tmono(slide, "# Real example: Airflow DAG + dbt model + NR alert condition — what used to take 1 day",
          Inches(0.5), Inches(4.56), Inches(12.3), Inches(0.26), sz=9.5, color=TGRY)
    Tmono(slide, "> /avengers 'add daily_reconciliation_dag with NR alert on SLA breach'",
          Inches(0.5), Inches(4.83), Inches(12.3), Inches(0.26), sz=9.5, color=G)
    lines = [
        "→ Fury reads spec + graph context",
        "→ Spawns strange-architect (designs DAG topology) + stark-engineer-1 (writes DAG) in PARALLEL",
        "→ stark-engineer-2 writes NR alert HCL while stark-engineer-1 finishes DAG",
        "→ natasha-reviewer: code standards + OWASP + blast radius check",
        "→ hawkeye-validator: runs tests, confirms 0 regressions",
        "→ Fury: merges output, generates PR description, shuts down team",
    ]
    for i, line in enumerate(lines):
        Tmono(slide, line, Inches(0.5), Inches(5.12+i*0.24), Inches(12.3), Inches(0.22), sz=9)

    ftr(slide)


def s12_jira_confluence(prs):
    slide = blank(prs)
    hdr(slide, "Jira + Confluence MCP — Zero Copy-Paste, Every Session Documented")

    # Flow
    flow = [("Dev merges PR", W, BK), ("/wrap-up fires", GLT, GDK),
            ("Claude drafts", GLT, GDK), ("Jira updated", ATL, W), ("Confluence\npublished", ATL, W)]
    for i, (label, fill, tc) in enumerate(flow):
        x = Inches(0.4 + i * 2.56)
        R(slide, x, Inches(0.9), Inches(2.3), Inches(1.1),
          fill=fill, line=(ATL if fill == ATL else G if fill == GLT else LN), lw=Pt(1.5))
        T(slide, label, x+Inches(0.1), Inches(1.1), Inches(2.1), Inches(0.72),
          sz=12, bold=(fill==ATL), color=tc, align=PP_ALIGN.CENTER)
        if i < 4:
            T(slide, "→", Inches(2.82+i*2.56), Inches(1.28), Inches(0.38), Inches(0.38),
              sz=22, bold=True, color=G, align=PP_ALIGN.CENTER)

    # Two columns
    jira_items = [
        "Status:    In Review → Done",
        "Comment:   what was done, decisions made",
        "Time:      logged from session duration",
        "Linked:    to commits via branch name",
        "",
        "Jira MCP tools used:",
        "  editJiraIssue · addCommentToJiraIssue",
        "  transitionJiraIssue · addWorklogToJiraIssue",
    ]
    conf_items = [
        "Architecture decisions: auto-logged",
        "Incident postmortem:    page auto-created",
        "Release notes:          from git history",
        "Categorized by area, files changed listed",
        "",
        "Confluence MCP tools used:",
        "  createConfluencePage · updateConfluencePage",
        "  searchConfluenceUsingCql · createFooterComment",
    ]
    for label, items, x, color in [
        ("Jira — Auto-populated", jira_items, Inches(0.4), ATL),
        ("Confluence — Auto-published", conf_items, Inches(6.85), ATL),
    ]:
        R(slide, x, Inches(2.18), Inches(6.0), Inches(4.05), fill=W, line=LN, lw=Pt(1))
        R(slide, x, Inches(2.18), Inches(6.0), Inches(0.42), fill=color)
        T(slide, label, x+Inches(0.15), Inches(2.23), Inches(5.7), Inches(0.35), sz=14, bold=True, color=W)
        for i, line in enumerate(items):
            col = G if line.startswith("  ") else (BK if line else BK)
            T(slide, line, x+Inches(0.15), Inches(2.7+i*0.36), Inches(5.7), Inches(0.32),
              sz=10.5, color=col, font="Courier New" if line.startswith("  ") else "Calibri")

    HL(slide, Inches(0.4), Inches(6.33), Inches(12.5))
    T(slide, "Zero manual effort.  Every session documented.  Every time.",
      Inches(0.4), Inches(6.4), Inches(12.5), Inches(0.38), sz=14, bold=True, color=BK, align=PP_ALIGN.CENTER)
    ftr(slide)


def s13_model_routing(prs):
    slide = blank(prs)
    hdr(slide, "Model Routing — Right Tool, Right Cost, No Waste")

    T(slide, "Output cost dominates: Opus $75/M · Sonnet $15/M · Haiku $5/M.  Default = Sonnet.  Escalate per-turn, not per-session.",
      Inches(0.4), Inches(0.82), Inches(12.5), Inches(0.34), sz=11, color=GR)

    rows = [
        ("HAIKU 4.5  (cheapest)", RGBColor(0x00,0x70,0xBB), [
            "Jira / Confluence fetch + summarize",
            "NRQL query execution + format",
            "File search / grep / glob / cat",
            "Lint fix from explicit error",
            "Rename / format / simple transform",
            "Commit message from diff",
        ]),
        ("SONNET 4.6  (DEFAULT)", G, [
            "Bug fix with clear hypothesis",
            "Feature implementation (follows patterns)",
            "Unit tests on known function",
            "Cross-file refactor",
            "Code review on PR <500 lines",
            "Template-driven rewrite (skill rewrites)",
        ]),
        ("OPUS 4.7  (5× cost — earn it)", PUR, [
            "/bootstrap  (deep codebase analysis)",
            "/avengers Fury (orchestrator)",
            "Architecture design + security review",
            "Production incident, unclear cause",
            "Complex PR review >500 lines critical path",
            "Multi-phase initiative planning",
        ]),
    ]

    y = Inches(1.25)
    for i, (label, color, items) in enumerate(rows):
        x = Inches(0.4 + i * 4.3)
        R(slide, x, y, Inches(4.0), Inches(5.05), fill=W, line=color, lw=Pt(1.5))
        R(slide, x, y, Inches(4.0), Inches(0.44), fill=color)
        T(slide, label, x+Inches(0.12), y+Inches(0.06), Inches(3.76), Inches(0.34), sz=12, bold=True, color=W)
        for j, item in enumerate(items):
            T(slide, "• "+item, x+Inches(0.12), y+Inches(0.55+j*0.54), Inches(3.76), Inches(0.44),
              sz=11, color=BK)

    ftr(slide)


def s14_productivity(prs):
    slide = blank(prs)
    hdr(slide, "Productivity Multipliers — Honest Numbers, Real DE Work")

    rows_mult = [
        ("Repetitive DE tasks with /replay goldens",
         "DAG edits, alert tuning, connector YAML, routine fixes",
         "~50×", G),
        ("Novel feature work  —  graph-first nav + memory MCP",
         "New pipeline, new data source, new alert policy",
         "~10×", ATL),
        ("Architecture / design  —  thinking-bound, not context-bound",
         "New service, schema design, cross-team dependencies",
         "~3×", PUR),
        ("Prod debugging  —  your understanding is the bottleneck",
         "Novel failure mode, unfamiliar system, on-call",
         "~1×", GR),
    ]

    y = Inches(0.88)
    for task, example, mult, color in rows_mult:
        h = Inches(1.1)
        R(slide, Inches(0.4), y, Inches(12.5), h, fill=W, line=LN, lw=Pt(0.75))
        R(slide, Inches(0.4), y, Inches(0.08), h, fill=color)
        T(slide, task,    Inches(0.6), y+Inches(0.1),  Inches(9.5), Inches(0.38), sz=14, bold=True)
        T(slide, example, Inches(0.6), y+Inches(0.5),  Inches(9.5), Inches(0.34), sz=11, color=GR)
        T(slide, mult,    Inches(10.3), y+Inches(0.25), Inches(2.4), Inches(0.5),
          sz=28, bold=True, color=color, align=PP_ALIGN.CENTER)
        y += h + Inches(0.12)

    R(slide, Inches(0.4), y+Inches(0.06), Inches(12.5), Inches(0.7), fill=GLT, line=G, lw=Pt(1.5))
    T(slide, "Sustained team average:  15–25×  over a month of real DE work",
      Inches(0.6), y+Inches(0.15), Inches(8.5), Inches(0.45), sz=20, bold=True, color=GDK)
    T(slide, "(100× aspirational — cherry-picked replay-heavy scenarios only)",
      Inches(9.2), y+Inches(0.22), Inches(3.5), Inches(0.36), sz=10, italic=True, color=GR)
    ftr(slide)


def s15_metrics(prs):
    slide = blank(prs)
    hdr(slide, "Before & After — Ingestion Team Metrics (3 Repos, ~3 Months)")

    cols = ["Metric", "Before  (manual)", "After  (AI-led)"]
    cxs  = [Inches(0.4),  Inches(4.2),  Inches(8.15)]
    cws  = [Inches(3.65), Inches(3.7),  Inches(4.9)]
    for j, (h, x, w) in enumerate(zip(cols, cxs, cws)):
        T(slide, h, x, Inches(0.85), w, Inches(0.38), sz=13, bold=True,
          color=(GR if j == 0 else BK), align=PP_ALIGN.CENTER)
    HL(slide, Inches(0.4), Inches(1.2), Inches(12.6), G)

    data = [
        ("Engineer onboarding time",     "2+ weeks (Slack + git history)",         "Hours  — /bootstrap loads context day 1"),
        ("Incident MTTR (diagnosis)",     "2–3 hours (manual NR UI hunting)",        "20–30 min  (NR MCP structured output)"),
        ("Feature cycle time",           "14–20 days",                               "3–5 days"),
        ("Blast radius visibility",      "Unknown until prod breaks",                "Instant  —  get_impact_radius pre-commit"),
        ("Rework from hidden deps",      "~1 sprint/quarter absorbed",               "< 1 day  (caught pre-commit)"),
        ("Context on new codebase",      "Days of grep + git archaeology",           "Minutes  —  graph + hot.md loaded"),
        ("Security bugs caught",         "~40% (periodic manual review)",            "80–100%  (natasha-reviewer every PR)"),
        ("Test coverage",                "60–70%",                                   "90%  (hawkeye-validator gate)"),
    ]

    y = Inches(1.28)
    for i, (metric, before, after) in enumerate(data):
        fill = GLT if i % 2 else W
        R(slide, Inches(0.4), y, Inches(12.6), Inches(0.54), fill=fill)
        T(slide, metric, cxs[0], y+Inches(0.08), cws[0], Inches(0.4), sz=11, bold=True)
        T(slide, before, cxs[1], y+Inches(0.08), cws[1], Inches(0.4), sz=11, color=GR)
        T(slide, after,  cxs[2], y+Inches(0.08), cws[2], Inches(0.4), sz=11, bold=True, color=GDK)
        y += Inches(0.54)

    R(slide, Inches(0.4), y+Inches(0.06), Inches(12.6), Inches(0.38), fill=W, line=LN, lw=Pt(1))
    T(slide, "Repos: om-airflow-dags  ·  spark-kafka-apps  ·  tf-dataos-new-relic",
      Inches(0.6), y+Inches(0.12), Inches(12.2), Inches(0.28), sz=10, color=GR, align=PP_ALIGN.CENTER)
    ftr(slide)


def s16_controls(prs):
    slide = blank(prs)
    hdr(slide, "AI Does the Work.  Humans Stay in Control.")

    gates = [
        ("1", "Requirements approval",        "Before planning begins — human writes the spec, Claude reads it"),
        ("2", "Architecture plan approval",    "Before any code is written — /bootstrap plan mode, human approves"),
        ("3", "Security review sign-off",      "natasha-reviewer flags OWASP findings — any critical BLOCKS pipeline"),
        ("4", "Final PR merge",                "Human reviews every PR — agent PRs treated identically to human PRs"),
        ("5", "Production deployments",        "Human initiates + monitors — agent creates release notes, human deploys"),
    ]

    y = Inches(0.9)
    for num, title, detail in gates:
        is3 = num == "3"
        R(slide, Inches(0.4), y, Inches(12.5), Inches(0.94),
          fill=(GLT if is3 else W), line=(G if is3 else LN), lw=Pt(1.5 if is3 else 0.75))
        R(slide, Inches(0.4), y, Inches(0.5), Inches(0.94), fill=(G if is3 else LGR))
        T(slide, num, Inches(0.4), y+Inches(0.22), Inches(0.5), Inches(0.5),
          sz=18, bold=True, color=(W if is3 else G), align=PP_ALIGN.CENTER)
        T(slide, title,  Inches(1.1), y+Inches(0.1),  Inches(4.5), Inches(0.4), sz=15, bold=True)
        T(slide, detail, Inches(5.8), y+Inches(0.15), Inches(7.0), Inches(0.62), sz=12, color=GR)
        y += Inches(1.06)

    ftr(slide)


def s17_getting_started(prs):
    slide = blank(prs)
    hdr(slide, "Getting Started — Week-by-Week Adoption Plan")

    weeks = [
        ("Week 1  —  Solo",
         ["Install: ./install.sh + ./verify.sh  (15 min)",
          "/bootstrap on your most-used repo",
          "Work normally — skills auto-trigger",
          "/wrap-up at every session end",
          "Check /budget status daily"],
         G),
        ("Week 2  —  Discipline",
         ["All active repos bootstrapped",
          "Save first golden after a prod fix",
          "Try /replay on a recurring task",
          "Review grep-telemetry-report.sh weekly"],
         ATL),
        ("Week 3  —  Advanced",
         ["/avengers on first real multi-file task",
          "Golden library: 3–5 patterns saved",
          "Tune model routing (Haiku for mechanical)",
          "Check: session start cost < $0.05"],
         PUR),
        ("Week 4+  —  Steady State",
         ["2–5 new goldens/week automatically",
          "Grep fallback rate < 10%",
          "lessons.md promoting to CLAUDE.md",
          "Team sharing golden library"],
         GDK),
    ]

    for i, (title, items, color) in enumerate(weeks):
        x = Inches(0.4 + i * 3.2)
        R(slide, x, Inches(0.85), Inches(3.0), Inches(4.8), fill=W, line=LN, lw=Pt(1))
        R(slide, x, Inches(0.85), Inches(3.0), Inches(0.44), fill=color)
        T(slide, title, x+Inches(0.1), Inches(0.9), Inches(2.8), Inches(0.36), sz=11, bold=True, color=W)
        for j, item in enumerate(items):
            T(slide, "• "+item, x+Inches(0.1), Inches(1.4+j*0.56), Inches(2.8), Inches(0.48), sz=10.5, color=BK)

    # Health signals
    R(slide, Inches(0.4), Inches(5.85), Inches(12.5), Inches(0.78), fill=LGR, line=LN, lw=Pt(0.75))
    signals = [
        ("🟢  Green", "golden/*.md grows 2–5/wk · grep fallback <10% · session start <$0.05"),
        ("🟡  Yellow","overrides ≥3/wk → raise caps · grep fallback >30% → tune graphignore"),
        ("🔴  Red",   "engineers skip /wrap-up frequently · goldens never used → tags too narrow"),
    ]
    for i, (lbl, detail) in enumerate(signals):
        T(slide, lbl,    Inches(0.6+i*4.2),  Inches(5.93), Inches(1.3),  Inches(0.32), sz=11, bold=True)
        T(slide, detail, Inches(1.95+i*4.2), Inches(5.93), Inches(2.85), Inches(0.32), sz=10, color=GR)

    ftr(slide)


def s18_thanks(prs):
    slide = blank(prs)
    R(slide, 0, 0, SW, SH, fill=NVY)
    R(slide, 0, 0, SW, Inches(0.06), fill=G)
    R(slide, 0, SH-Inches(0.06), SW, Inches(0.06), fill=G)
    T(slide, "⬢ new relic", Inches(0.5), Inches(0.35), Inches(3), Inches(0.55), sz=22, bold=True, color=G)
    T(slide, "Thank You", Inches(1.5), Inches(2.3), Inches(10.33), Inches(1.4),
      sz=60, bold=False, color=W, align=PP_ALIGN.CENTER)
    T(slide, "Questions?", Inches(4.0), Inches(3.85), Inches(5.33), Inches(0.7),
      sz=26, italic=True, color=G, align=PP_ALIGN.CENTER)
    HL(slide, Inches(3.0), Inches(4.65), Inches(7.33), G)
    links = [
        ("Repo:", "github.com/nr-mdakilahmed/claude_code_setup"),
        ("Install:", "git clone → ./install.sh → ./verify.sh"),
        ("First visit:", "/bootstrap  |  Every session end: /wrap-up"),
    ]
    for i, (label, val) in enumerate(links):
        T(slide, label, Inches(3.5), Inches(4.9+i*0.52), Inches(1.5), Inches(0.42), sz=13, bold=True, color=G)
        T(slide, val,   Inches(5.1), Inches(4.9+i*0.52), Inches(5.5), Inches(0.42), sz=13, color=W)


# ── Main ──────────────────────────────────────────────────────────────────────

SLIDES = [
    s01_title, s02_problem, s03_two_tools, s04_architecture, s05_install,
    s06_skills, s07_session_loop, s08_memory, s09_nr_mcp, s10_graph,
    s11_avengers, s12_jira_confluence, s13_model_routing, s14_productivity,
    s15_metrics, s16_controls, s17_getting_started, s18_thanks,
]

OUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUT_PPTX = os.path.join(OUT_DIR, "Ingestion-Team-AI-Led-Demo.pptx")
OUT_PDF  = os.path.join(OUT_DIR, "Ingestion-Team-AI-Led-Demo.pdf")

def main():
    prs = new_prs()
    for fn in SLIDES:
        fn(prs)
    prs.save(OUT_PPTX)
    print(f"✓  {len(prs.slides)} slides  →  {OUT_PPTX}")

    # PDF via soffice (LibreOffice)
    soffice = "/opt/homebrew/bin/soffice"
    if os.path.exists(soffice):
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", OUT_DIR, OUT_PPTX],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✓  PDF         →  {OUT_PDF}")
        else:
            print(f"⚠  PDF conversion failed: {result.stderr.strip()}")
    else:
        print("⚠  soffice not found — open PPTX in PowerPoint and export PDF manually")

if __name__ == "__main__":
    main()
