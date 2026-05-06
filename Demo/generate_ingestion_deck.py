#!/usr/bin/env python3
"""
generate_ingestion_deck.py  —  v3  (executive, lifecycle-first, stunning)

Story arc:  Problem → Answer → Full Lifecycle → Outcomes → Proof → Ask
Audience:   CEO, VPs, PMs  —  "What / How / How much"
Design:     NR green + dark navy + white space + hero numbers

Usage:
    python3 generate_ingestion_deck.py
Outputs:
    Ingestion-Team-AI-Led-Demo.pptx
    Ingestion-Team-AI-Led-Demo.pdf
"""

import os, subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette (matches NR brand from existing deck) ────────────────────────────
NR_GREEN   = RGBColor(0x00, 0xAC, 0x69)   # #00AC69  primary green
NR_BRIGHT  = RGBColor(0x00, 0xD0, 0x84)   # #00D084  bright accent
NR_DARK_G  = RGBColor(0x00, 0x6B, 0x40)   # #006B40  dark green
NR_NAVY    = RGBColor(0x0D, 0x0D, 0x24)   # #0D0D24  deep navy (hero slides)
NR_CHARCOAL= RGBColor(0x1F, 0x29, 0x37)   # #1F2937  dark charcoal
NR_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
NR_LGRAY   = RGBColor(0xF3, 0xF4, 0xF6)   # #F3F4F6  light gray bg
NR_MGRAY   = RGBColor(0xE5, 0xE7, 0xEB)   # #E5E7EB  border / rule
NR_GRAY    = RGBColor(0x6B, 0x72, 0x80)   # #6B7280  body / secondary text
NR_BLACK   = RGBColor(0x14, 0x14, 0x1E)   # near black

# Phase / accent palette
C_HUMAN    = NR_CHARCOAL
C_AI       = NR_GREEN
C_WARN     = RGBColor(0xFF, 0xC1, 0x07)   # amber
C_RED      = RGBColor(0xE5, 0x3E, 0x3E)
C_BLUE     = RGBColor(0x00, 0x52, 0xCC)   # Atlassian blue
C_PUR      = RGBColor(0x7C, 0x3A, 0xED)

FOOTER_TXT = "© 2025 New Relic, Inc.  All rights reserved.  Confidential and proprietary.  For internal use only."

SW = Inches(13.33)
SH = Inches(7.5)


# ── Primitives ────────────────────────────────────────────────────────────────

def new_prs():
    p = Presentation(); p.slide_width = SW; p.slide_height = SH; return p

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def box(s, x, y, w, h, fill=None, line=None, lw=Pt(0.75)):
    sh = s.shapes.add_shape(1, x, y, w, h)
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    else:    sh.fill.background()
    if line: sh.line.color.rgb = line; sh.line.width = lw
    else:    sh.line.fill.background()
    return sh

def txt(s, t, x, y, w, h, sz=13, bold=False, color=NR_BLACK,
        align=PP_ALIGN.LEFT, italic=False, font="Calibri"):
    tb = s.shapes.add_textbox(x, y, w, h); tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = t
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color; r.font.name = font
    return tb

def hero(s, number, label, x, y, w, number_sz=64, label_sz=16,
         num_color=NR_GREEN, label_color=NR_GRAY):
    """Big hero number + small label below."""
    txt(s, number, x, y,          w, Inches(1.2), sz=number_sz, bold=True, color=num_color, align=PP_ALIGN.CENTER)
    txt(s, label,  x, y+Inches(1.1), w, Inches(0.5), sz=label_sz, color=label_color, align=PP_ALIGN.CENTER)

def rule(s, x, y, w, color=NR_MGRAY):
    box(s, x, y, w, Inches(0.018), fill=color)

def ftr(s):
    txt(s, FOOTER_TXT, Inches(0.3), Inches(7.06), Inches(11.6), Inches(0.36), sz=7, color=NR_GRAY)
    txt(s, "⬢ new relic", Inches(11.8), Inches(7.01), Inches(1.4), Inches(0.42),
        sz=10, bold=True, color=NR_GREEN, align=PP_ALIGN.RIGHT)

def section_header(s, title, h=Inches(0.68)):
    box(s, 0, 0, SW, h, fill=NR_GREEN)
    txt(s, title, Inches(0.4), Inches(0.06), Inches(12.5), h-Inches(0.06),
        sz=24, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)

def pill(s, label, x, y, color=NR_GREEN, tc=NR_WHITE, sz=10):
    box(s, x, y, Inches(2.1), Inches(0.36), fill=color)
    txt(s, label, x+Inches(0.08), y+Inches(0.04), Inches(1.94), Inches(0.28),
        sz=sz, bold=True, color=tc, align=PP_ALIGN.CENTER)

def circle_num(s, n, x, y, r=Inches(0.38), fill=NR_GREEN):
    box(s, x-r/2, y-r/2, r, r, fill=fill)
    txt(s, str(n), x-r/2, y-r/2+Inches(0.03), r, r-Inches(0.04),
        sz=14, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)

def outcome_card(s, x, y, w, h, icon, headline, metric, sub,
                 fill=NR_WHITE, border=NR_MGRAY, accent=NR_GREEN):
    box(s, x, y, w, h, fill=fill, line=border, lw=Pt(1))
    box(s, x, y, Inches(0.07), h, fill=accent)           # left accent stripe
    txt(s, icon,     x+Inches(0.22), y+Inches(0.14), w-Inches(0.35), Inches(0.44), sz=22)
    txt(s, headline, x+Inches(0.22), y+Inches(0.62), w-Inches(0.35), Inches(0.42),
        sz=13, bold=True, color=NR_BLACK)
    txt(s, metric,   x+Inches(0.22), y+Inches(1.08), w-Inches(0.35), Inches(0.55),
        sz=26, bold=True, color=accent)
    txt(s, sub,      x+Inches(0.22), y+Inches(1.65), w-Inches(0.35), Inches(0.42),
        sz=10, color=NR_GRAY)

def phase_box(s, x, y, w, h, num, title, who, fill=NR_WHITE, tc=NR_BLACK, accent=NR_GREEN):
    box(s, x, y, w, h, fill=fill, line=NR_MGRAY, lw=Pt(0.75))
    box(s, x, y, w, Inches(0.05), fill=accent)           # top accent stripe
    txt(s, str(num), x+Inches(0.12), y+Inches(0.1), Inches(0.3), Inches(0.3),
        sz=10, bold=True, color=accent, font="Calibri")
    txt(s, title, x+Inches(0.12), y+Inches(0.38), w-Inches(0.25), Inches(0.5),
        sz=12, bold=True, color=tc)
    txt(s, who,   x+Inches(0.12), y+Inches(0.9),  w-Inches(0.25), Inches(0.28),
        sz=9, color=NR_GRAY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDES
# ══════════════════════════════════════════════════════════════════════════════

def s01_title(prs):
    """Dark hero title — immediate impact."""
    s = blank(prs)
    box(s, 0, 0, SW, SH, fill=NR_NAVY)
    box(s, 0, 0, SW, Inches(0.06), fill=NR_GREEN)        # top green line
    box(s, 0, SH-Inches(0.06), SW, Inches(0.06), fill=NR_GREEN)  # bottom green line
    box(s, Inches(8.6), 0, Inches(4.73), SH, fill=RGBColor(0x12,0x12,0x30))  # right panel

    # NR logo
    txt(s, "⬢ new relic", Inches(0.6), Inches(0.35), Inches(3), Inches(0.55),
        sz=22, bold=True, color=NR_GREEN)

    # Main headline
    txt(s, "Ingestion Team", Inches(0.6), Inches(1.55), Inches(7.6), Inches(0.72),
        sz=38, bold=True, color=NR_WHITE)
    txt(s, "AI-Led Development", Inches(0.6), Inches(2.28), Inches(7.6), Inches(0.65),
        sz=34, bold=True, color=NR_GREEN)
    txt(s, "Environment", Inches(0.6), Inches(2.95), Inches(7.6), Inches(0.62),
        sz=34, bold=True, color=NR_WHITE)

    rule(s, Inches(0.6), Inches(3.72), Inches(6.8), NR_GREEN)

    txt(s, "Claude Code  +  GitHub Copilot  +  New Relic MCP",
        Inches(0.6), Inches(3.88), Inches(7.6), Inches(0.42), sz=15, color=NR_GRAY, italic=True)

    # Right panel — 5 outcome chips
    outcomes = [
        ("🚀", "10×  faster feature delivery"),
        ("🧠", "Onboard in hours, not weeks"),
        ("🔍", "30-min incident diagnosis"),
        ("⚡", "5 agents working in parallel"),
        ("📦", "Knowledge that compounds"),
    ]
    for i, (ic, lbl) in enumerate(outcomes):
        yy = Inches(1.2 + i * 1.05)
        box(s, Inches(8.9), yy, Inches(4.0), Inches(0.82),
            fill=RGBColor(0x1A, 0x1A, 0x3A), line=RGBColor(0x2A,0x2A,0x5A), lw=Pt(0.75))
        box(s, Inches(8.9), yy, Inches(0.06), Inches(0.82), fill=NR_GREEN)
        txt(s, ic,  Inches(9.05), yy+Inches(0.2), Inches(0.4),  Inches(0.42), sz=18)
        txt(s, lbl, Inches(9.52), yy+Inches(0.2), Inches(3.25), Inches(0.42), sz=13, color=NR_WHITE)


def s02_problem(prs):
    """The challenge — big pain numbers."""
    s = blank(prs)
    section_header(s, "The Challenge — Four Pains That Slow Every Team Down")

    cards = [
        ("🕐", "New Engineer Onboarding",   "2+ WEEKS",  "to reach full productivity", C_RED),
        ("🔍", "Incident Root Cause",        "2–3 HOURS", "hunting logs manually at 2am", C_WARN),
        ("💥", "Blast Radius Unknown",       "5-DAY",     "incident from a '1-day fix'", NR_CHARCOAL),
        ("🗂", "Architecture in Heads",      "KNOWLEDGE", "lost every time someone leaves", NR_CHARCOAL),
    ]

    xs = [Inches(0.4),  Inches(6.85)]
    ys = [Inches(0.82), Inches(3.95)]

    for i, (icon, title, bignum, sub, accent) in enumerate(cards):
        x, y = xs[i % 2], ys[i // 2]
        w, h = Inches(6.05), Inches(2.85)
        box(s, x, y, w, h, fill=NR_WHITE, line=NR_MGRAY, lw=Pt(1))
        box(s, x, y, w, Inches(0.06), fill=accent)
        txt(s, icon+" "+title, x+Inches(0.25), y+Inches(0.2), w-Inches(0.5), Inches(0.44),
            sz=15, bold=True)
        txt(s, bignum, x+Inches(0.25), y+Inches(0.75), w-Inches(0.5), Inches(0.88),
            sz=46, bold=True, color=accent)
        rule(s, x+Inches(0.25), y+Inches(1.72), w-Inches(0.5), NR_MGRAY)
        txt(s, sub, x+Inches(0.25), y+Inches(1.84), w-Inches(0.5), Inches(0.42),
            sz=13, color=NR_GRAY)
    ftr(s)


def s03_answer(prs):
    """The answer — one clear statement + Copilot vs CC."""
    s = blank(prs)
    # Top statement band
    box(s, 0, 0, SW, Inches(1.55), fill=NR_GREEN)
    txt(s, "Two AI tools.  One team environment.  Knowledge that compounds every session.",
        Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.95),
        sz=26, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)

    # Copilot panel
    box(s, Inches(0.4), Inches(1.72), Inches(5.75), Inches(4.85), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(1))
    box(s, Inches(0.4), Inches(1.72), Inches(5.75), Inches(0.52), fill=NR_CHARCOAL)
    txt(s, "GitHub Copilot — Line-level AI",
        Inches(0.6), Inches(1.8), Inches(5.35), Inches(0.38), sz=16, bold=True, color=NR_WHITE)
    for i, (icon, item) in enumerate([
        ("✅", "Autocomplete lines & functions in IDE"),
        ("✅", "Inline chat: explain / refactor this"),
        ("✅", "Generate tests & boilerplate fast"),
        ("✅", "Works where engineers already work"),
        ("❌", "No memory across sessions"),
        ("❌", "Can't query NR, Jira, Confluence"),
        ("❌", "No blast-radius or impact analysis"),
        ("❌", "No multi-agent parallel execution"),
    ]):
        c = NR_GRAY if icon == "❌" else NR_BLACK
        txt(s, icon+" "+item, Inches(0.65), Inches(2.42+i*0.48), Inches(5.35), Inches(0.42), sz=12, color=c)

    # Bridge
    txt(s, "+", Inches(6.28), Inches(3.65), Inches(0.75), Inches(0.75),
        sz=42, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    txt(s, "together", Inches(6.15), Inches(4.45), Inches(1.0), Inches(0.32),
        sz=10, color=NR_GRAY, align=PP_ALIGN.CENTER)

    # Claude Code panel
    box(s, Inches(7.15), Inches(1.72), Inches(5.75), Inches(4.85), fill=RGBColor(0xF0,0xFB,0xF5), line=NR_GREEN, lw=Pt(1.5))
    box(s, Inches(7.15), Inches(1.72), Inches(5.75), Inches(0.52), fill=NR_GREEN)
    txt(s, "Claude Code — Team environment AI",
        Inches(7.35), Inches(1.8), Inches(5.35), Inches(0.38), sz=16, bold=True, color=NR_WHITE)
    for i, item in enumerate([
        "✅  Memory: full context loads at session start",
        "✅  NR MCP: queries logs, metrics, alerts live",
        "✅  Blast radius: impact analysis before coding",
        "✅  /avengers: 5 parallel AI agents on one task",
        "✅  /golden + /replay: patterns that compound",
        "✅  20 skills auto-trigger on file type / topic",
        "✅  Jira + Confluence: auto-updated every session",
        "✅  Budget dial: daily spend awareness built-in",
    ]):
        txt(s, item, Inches(7.35), Inches(2.42+i*0.48), Inches(5.35), Inches(0.42),
            sz=12, color=NR_BLACK)
    ftr(s)


def s04_lifecycle(prs):
    """THE CENTERPIECE — Full AI-led development lifecycle."""
    s = blank(prs)
    section_header(s, "The Full AI-Led Development Lifecycle  —  From Idea to Knowledge")

    phases = [
        ("01", "Requirement",  "Product / PM",   NR_CHARCOAL, NR_WHITE),
        ("02", "Spec & Plan",  "AI + Human",     NR_GREEN,    NR_WHITE),
        ("03", "Architect",    "AI (/avengers)",  NR_DARK_G,   NR_WHITE),
        ("04", "Build",        "AI + parallel",  NR_GREEN,    NR_WHITE),
        ("05", "Review",       "AI + Human",     NR_DARK_G,   NR_WHITE),
        ("06", "Test & Gate",  "AI-automated",   NR_GREEN,    NR_WHITE),
        ("07", "Deploy",       "Human initiates", NR_CHARCOAL, NR_WHITE),
        ("08", "Monitor",      "NR MCP (AI)",    C_BLUE,      NR_WHITE),
        ("09", "Document",     "AI auto-update", C_PUR,       NR_WHITE),
        ("10", "Learn",        "Golden patterns", NR_GREEN,    NR_WHITE),
    ]

    bw = Inches(1.25)
    bh = Inches(1.45)
    gap = Inches(0.005)
    total_w = len(phases) * bw + (len(phases)-1) * gap
    start_x = (SW - total_w) / 2

    for i, (num, title, who, fill, tc) in enumerate(phases):
        x = start_x + i * (bw + gap)
        y = Inches(0.82)
        box(s, x, y, bw, bh, fill=fill)
        txt(s, num,   x+Inches(0.1), y+Inches(0.07), bw-Inches(0.2), Inches(0.25),
            sz=9, bold=True, color=RGBColor(0xFF,0xFF,0xFF) if fill != NR_WHITE else NR_GRAY)
        txt(s, title, x+Inches(0.07), y+Inches(0.33), bw-Inches(0.14), Inches(0.58),
            sz=11, bold=True, color=tc, align=PP_ALIGN.CENTER)
        txt(s, who,   x+Inches(0.07), y+Inches(0.95), bw-Inches(0.14), Inches(0.38),
            sz=8,  color=RGBColor(0xCC,0xFF,0xCC) if fill in (NR_GREEN,NR_DARK_G,C_BLUE,C_PUR) else NR_GRAY,
            align=PP_ALIGN.CENTER)
        if i < len(phases)-1:
            txt(s, "›", x+bw-Inches(0.1), y+Inches(0.48), Inches(0.26), Inches(0.5),
                sz=18, bold=True, color=NR_MGRAY, align=PP_ALIGN.CENTER)

    # Loop arrow back
    box(s, start_x, Inches(2.42), total_w, Inches(0.04), fill=NR_GREEN)
    txt(s, "↺  repeats every sprint — knowledge compounds",
        start_x, Inches(2.5), total_w, Inches(0.32),
        sz=10, italic=True, color=NR_GRAY, align=PP_ALIGN.CENTER)

    # Role legend
    legend = [
        (NR_CHARCOAL, "Human-led"),
        (NR_GREEN,    "AI-led (Claude Code)"),
        (C_BLUE,      "NR MCP observability"),
        (C_PUR,       "Auto-documentation"),
    ]
    y = Inches(3.05)
    txt(s, "What AI handles vs. human:", Inches(0.4), y, Inches(3.2), Inches(0.32), sz=11, bold=True)
    for i, (color, label) in enumerate(legend):
        x = Inches(0.4 + i * 3.2)
        box(s, x, y+Inches(0.38), Inches(0.28), Inches(0.28), fill=color)
        txt(s, label, x+Inches(0.36), y+Inches(0.38), Inches(2.7), Inches(0.28), sz=11, color=NR_BLACK)

    # Key insight boxes
    insights = [
        ("AI writes code, runs tests, reviews security,\nupdates Jira — autonomously, in parallel.",
         NR_GREEN),
        ("Humans approve at 5 gates:\nRequirements · Architecture · Security · PR · Deploy.",
         NR_CHARCOAL),
        ("Each session makes the next one smarter.\nKnowledge never leaves the team.",
         C_PUR),
    ]
    y = Inches(3.95)
    for i, (text, color) in enumerate(insights):
        x = Inches(0.4 + i * 4.3)
        box(s, x, y, Inches(4.05), Inches(2.7), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(0.75))
        box(s, x, y, Inches(0.06), Inches(2.7), fill=color)
        txt(s, text, x+Inches(0.22), y+Inches(0.3), Inches(3.7), Inches(2.1),
            sz=12, color=NR_BLACK)
    ftr(s)


def s05_onboard(prs):
    """Onboarding — hero: 2 weeks → 2 hours."""
    s = blank(prs)
    section_header(s, "Onboard in Hours, Not Weeks  —  Full Context on Day One")

    # Hero comparison
    box(s, Inches(0.4), Inches(0.85), Inches(5.8), Inches(3.6), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(1))
    box(s, Inches(0.4), Inches(0.85), Inches(5.8), Inches(0.06), fill=C_RED)
    txt(s, "BEFORE", Inches(0.6), Inches(1.0), Inches(5.4), Inches(0.36), sz=12, bold=True, color=NR_GRAY)
    txt(s, "2 WEEKS", Inches(0.6), Inches(1.4), Inches(5.4), Inches(1.0),
        sz=62, bold=True, color=C_RED, align=PP_ALIGN.CENTER)
    txt(s, "Slack DMs · git archaeology · tribal knowledge\n→ still not fully productive by end of week 2",
        Inches(0.6), Inches(2.55), Inches(5.4), Inches(0.7), sz=12, color=NR_GRAY, align=PP_ALIGN.CENTER)

    txt(s, "→", Inches(6.4), Inches(2.0), Inches(0.55), Inches(0.7),
        sz=34, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)

    box(s, Inches(7.1), Inches(0.85), Inches(5.8), Inches(3.6), fill=RGBColor(0xF0,0xFB,0xF5), line=NR_GREEN, lw=Pt(1.5))
    box(s, Inches(7.1), Inches(0.85), Inches(5.8), Inches(0.06), fill=NR_GREEN)
    txt(s, "AFTER", Inches(7.3), Inches(1.0), Inches(5.4), Inches(0.36), sz=12, bold=True, color=NR_DARK_G)
    txt(s, "2 HOURS", Inches(7.3), Inches(1.4), Inches(5.4), Inches(1.0),
        sz=62, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    txt(s, "/bootstrap: detects stack, seeds memory,\nbuilds code graph, wires MCPs — in 15 seconds",
        Inches(7.3), Inches(2.55), Inches(5.4), Inches(0.7), sz=12, color=NR_DARK_G, align=PP_ALIGN.CENTER)

    # Three outcome cards
    cards = [
        ("Full codebase context", "Auto-loaded at session start.\nNo manual exploration needed."),
        ("Architecture diagram", "Built from code graph.\nUpdates automatically."),
        ("Team's lessons ready", "patterns + anti-patterns +\nwins — from day 1."),
    ]
    for i, (title, desc) in enumerate(cards):
        x = Inches(0.4 + i * 4.3)
        box(s, x, Inches(4.68), Inches(4.05), Inches(1.92), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(0.75))
        box(s, x, Inches(4.68), Inches(0.06), Inches(1.92), fill=NR_GREEN)
        txt(s, title, x+Inches(0.2), Inches(4.82), Inches(3.7), Inches(0.4), sz=13, bold=True)
        txt(s, desc,  x+Inches(0.2), Inches(5.28), Inches(3.7), Inches(1.0), sz=11, color=NR_GRAY)
    ftr(s)


def s06_parallel(prs):
    """/avengers — 5 parallel agents hero."""
    s = blank(prs)
    section_header(s, "/avengers — Multi-Agent Orchestration  ·  5 Engineers in One Session")

    # Left: What it does
    txt(s, "Complex tasks that used to take one engineer one full day:",
        Inches(0.4), Inches(0.88), Inches(8.0), Inches(0.38), sz=13, color=NR_GRAY)

    # Agent diagram
    dark_y = Inches(1.38)
    box(s, Inches(0.4), dark_y, Inches(8.0), Inches(0.72), fill=NR_CHARCOAL)
    txt(s, "Nick Fury  (Opus — Orchestrator)",
        Inches(0.6), dark_y+Inches(0.08), Inches(4.5), Inches(0.38), sz=14, bold=True, color=NR_WHITE)
    txt(s, "routes work · validates gates · blocks bad code",
        Inches(5.1), dark_y+Inches(0.14), Inches(3.1), Inches(0.36), sz=11, italic=True, color=NR_GREEN)

    agents = [
        ("Planner",     "codebase research\n→ implementation plan", NR_DARK_G),
        ("Coder ×N",    "parallel code writing\nverifies build passes",  NR_GREEN),
        ("Reviewer",    "code standards +\nOWASP security",         NR_GREEN),
        ("Validator",   "tests + blast radius\nbefore any merge",    NR_DARK_G),
    ]
    for i, (name, desc, color) in enumerate(agents):
        x = Inches(0.4 + i * 2.0)
        box(s, x, Inches(2.28), Inches(1.85), Inches(1.65), fill=color)
        txt(s, name, x+Inches(0.1), Inches(2.38), Inches(1.65), Inches(0.4),
            sz=12, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        txt(s, desc, x+Inches(0.1), Inches(2.8),  Inches(1.65), Inches(0.92),
            sz=10, color=RGBColor(0xCC,0xFF,0xCC), align=PP_ALIGN.CENTER)

    # Right: hero metric
    box(s, Inches(8.7), Inches(1.1), Inches(4.25), Inches(5.5), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(1))
    txt(s, "1 DAY", Inches(8.7), Inches(1.55), Inches(4.25), Inches(0.9),
        sz=52, bold=True, color=C_RED, align=PP_ALIGN.CENTER)
    txt(s, "→", Inches(8.7), Inches(2.55), Inches(4.25), Inches(0.55),
        sz=28, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    txt(s, "2 HOURS", Inches(8.7), Inches(3.15), Inches(4.25), Inches(0.9),
        sz=52, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    txt(s, "Multi-file Airflow DAG +\ndbt model + NR alert\nworking in parallel",
        Inches(8.9), Inches(4.12), Inches(3.85), Inches(0.9), sz=12, color=NR_GRAY, align=PP_ALIGN.CENTER)

    # Result steps
    steps = [
        "Fury reads spec → spawns Planner + Coders simultaneously",
        "Each coder works on an independent file — zero waiting",
        "Reviewer checks all output → Validator runs tests + blast radius",
        "Engineer reviews 1 PR instead of writing 5 files",
    ]
    for i, step in enumerate(steps):
        box(s, Inches(0.4), Inches(4.12+i*0.52), Inches(8.0), Inches(0.46),
            fill=(RGBColor(0xF0,0xFB,0xF5) if i%2==0 else NR_WHITE), line=NR_MGRAY, lw=Pt(0.5))
        txt(s, f"{i+1}.", Inches(0.55), Inches(4.18+i*0.52), Inches(0.35), Inches(0.36),
            sz=12, bold=True, color=NR_GREEN)
        txt(s, step,    Inches(0.95), Inches(4.18+i*0.52), Inches(7.2), Inches(0.36),
            sz=11, color=NR_BLACK)
    ftr(s)


def s07_investigate(prs):
    """NR MCP investigation — 30-min hero."""
    s = blank(prs)
    section_header(s, "Incident Investigation  —  AI Queries New Relic Directly")

    # Left: before
    box(s, Inches(0.4), Inches(0.88), Inches(5.8), Inches(5.5), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(1))
    box(s, Inches(0.4), Inches(0.88), Inches(5.8), Inches(0.05), fill=C_RED)
    txt(s, "MANUAL", Inches(0.6), Inches(1.0), Inches(2.5), Inches(0.3), sz=11, bold=True, color=NR_GRAY)
    txt(s, "2–3\nHOURS", Inches(0.6), Inches(1.35), Inches(5.4), Inches(1.25),
        sz=54, bold=True, color=C_RED, align=PP_ALIGN.CENTER)
    txt(s, "Log in to NR UI  ·  navigate entity  ·  grep logs\nswitch tabs  ·  compare time ranges  ·  Slack team",
        Inches(0.6), Inches(2.72), Inches(5.4), Inches(0.7), sz=11, color=NR_GRAY, align=PP_ALIGN.CENTER)
    rule(s, Inches(0.6), Inches(3.55), Inches(5.4))
    txt(s, "Form hypothesis → test → repeat → still not sure",
        Inches(0.6), Inches(3.65), Inches(5.4), Inches(0.36), sz=11, italic=True, color=NR_GRAY, align=PP_ALIGN.CENTER)
    txt(s, "Meanwhile: customer impact growing every minute",
        Inches(0.6), Inches(4.15), Inches(5.4), Inches(0.36), sz=12, bold=True, color=C_RED, align=PP_ALIGN.CENTER)

    txt(s, "→", Inches(6.35), Inches(2.8), Inches(0.6), Inches(0.6),
        sz=32, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)

    # Right: after
    box(s, Inches(7.1), Inches(0.88), Inches(5.8), Inches(5.5), fill=RGBColor(0xF0,0xFB,0xF5), line=NR_GREEN, lw=Pt(1.5))
    box(s, Inches(7.1), Inches(0.88), Inches(5.8), Inches(0.05), fill=NR_GREEN)
    txt(s, "NR MCP", Inches(7.3), Inches(1.0), Inches(2.5), Inches(0.3), sz=11, bold=True, color=NR_DARK_G)
    txt(s, "30\nMINS", Inches(7.3), Inches(1.35), Inches(5.4), Inches(1.25),
        sz=54, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    txt(s, "Claude queries NR via MCP  ·  structured analysis\nconsumer lag, throughput, traces — all in one call",
        Inches(7.3), Inches(2.72), Inches(5.4), Inches(0.7), sz=11, color=NR_DARK_G, align=PP_ALIGN.CENTER)
    rule(s, Inches(7.3), Inches(3.55), Inches(5.4), NR_GREEN)
    txt(s, "\"analyze kafka consumer lag last 4h\"  →  root cause",
        Inches(7.3), Inches(3.65), Inches(5.4), Inches(0.36), sz=11, italic=True, color=NR_DARK_G, align=PP_ALIGN.CENTER)
    nrtools = ["analyze_kafka_metrics", "analyze_entity_logs", "list_recent_issues", "get_distributed_trace_details"]
    for i, t in enumerate(nrtools):
        box(s, Inches(7.3+i*1.35), Inches(4.2), Inches(1.25), Inches(0.32), fill=NR_DARK_G)
        txt(s, t, Inches(7.3+i*1.35+Inches(0.05)), Inches(4.22), Inches(1.15), Inches(0.28),
            sz=7.5, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER, font="Courier New")
    txt(s, "12 NR MCP tools available. AI knows what to call and when.",
        Inches(7.3), Inches(4.72), Inches(5.4), Inches(0.36), sz=11, bold=True, color=NR_DARK_G, align=PP_ALIGN.CENTER)
    ftr(s)


def s08_ship_safe(prs):
    """Blast radius — ship without surprises."""
    s = blank(prs)
    section_header(s, "Ship Without Surprises  —  Impact Analysis Before You Write a Line")

    # Hero statement
    box(s, Inches(0.4), Inches(0.88), Inches(12.5), Inches(0.88), fill=NR_GREEN)
    txt(s, "We know what breaks BEFORE touching it.  Not after deploying.",
        Inches(0.6), Inches(0.98), Inches(12.1), Inches(0.68),
        sz=22, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)

    # Before / After scenario
    box(s, Inches(0.4), Inches(1.94), Inches(5.9), Inches(2.4), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(1))
    txt(s, "⚠  Before", Inches(0.6), Inches(2.02), Inches(5.5), Inches(0.38), sz=14, bold=True, color=C_RED)
    txt(s, "Engineer changes spark_ingest.py.\nDeploys to staging.\nDownstream Kafka consumer breaks silently.\n5-day incident to trace back the cause.",
        Inches(0.6), Inches(2.46), Inches(5.5), Inches(1.7), sz=12, color=NR_GRAY)

    box(s, Inches(7.0), Inches(1.94), Inches(5.9), Inches(2.4), fill=RGBColor(0xF0,0xFB,0xF5), line=NR_GREEN, lw=Pt(1.5))
    txt(s, "✅  After", Inches(7.2), Inches(2.02), Inches(5.5), Inches(0.38), sz=14, bold=True, color=NR_DARK_G)
    txt(s, "Before writing code: get_impact_radius().\nSees 3 callers, 1 downstream Kafka consumer.\nFixes scope — ships confidently.\nZero prod incident.",
        Inches(7.2), Inches(2.46), Inches(5.5), Inches(1.7), sz=12, color=NR_BLACK)

    txt(s, "→", Inches(6.28), Inches(2.85), Inches(0.55), Inches(0.5),
        sz=28, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)

    # Metric cards at bottom
    metrics = [
        ("~1 sprint/qtr", "absorbed in unexpected rework"),
        ("< 1 day",        "rework after impact-aware development"),
        ("28 tools",       "in code-review-graph MCP — all graph-aware"),
        ("Auto-updates",   "graph rebuilds on every file save"),
    ]
    for i, (num, label) in enumerate(metrics):
        x = Inches(0.4 + i * 3.22)
        box(s, x, Inches(4.52), Inches(3.04), Inches(1.72), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(0.75))
        box(s, x, Inches(4.52), Inches(0.06), Inches(1.72), fill=(NR_GREEN if i % 2 == 0 else NR_DARK_G))
        txt(s, num,   x+Inches(0.15), Inches(4.66), Inches(2.7), Inches(0.6),
            sz=22, bold=True, color=(C_RED if i == 0 else NR_GREEN))
        txt(s, label, x+Inches(0.15), Inches(5.32), Inches(2.7), Inches(0.7),
            sz=11, color=NR_GRAY)
    ftr(s)


def s09_document(prs):
    """Jira + Confluence — zero copy-paste."""
    s = blank(prs)
    section_header(s, "Documentation That Writes Itself  —  Jira & Confluence Auto-Updated")

    # Flow across top
    flow = [
        ("Work session\ncompletes",     NR_LGRAY,  NR_BLACK),
        ("/wrap-up\nfires",             NR_GREEN,  NR_WHITE),
        ("Claude drafts\nsummary",      NR_GREEN,  NR_WHITE),
        ("Jira ticket\nupdated via MCP", C_BLUE,    NR_WHITE),
        ("Confluence page\npublished",   C_BLUE,    NR_WHITE),
    ]
    for i, (label, fill, tc) in enumerate(flow):
        x = Inches(0.4 + i * 2.58)
        box(s, x, Inches(0.88), Inches(2.35), Inches(1.2),
            fill=fill, line=(NR_GREEN if fill == NR_GREEN else C_BLUE if fill == C_BLUE else NR_MGRAY), lw=Pt(1))
        txt(s, label, x+Inches(0.1), Inches(1.07), Inches(2.15), Inches(0.82),
            sz=12, bold=(fill != NR_LGRAY), color=tc, align=PP_ALIGN.CENTER)
        if i < 4:
            txt(s, "→", Inches(2.78+i*2.58), Inches(1.27), Inches(0.36), Inches(0.38),
                sz=22, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)

    # Two columns
    jira = [
        ("Status",    "In Review → Done — automatically"),
        ("Comment",   "What was done, decisions made"),
        ("Worklog",   "Time logged from session duration"),
        ("Links",     "Commits linked via branch name"),
    ]
    confluence = [
        ("Architecture", "Decisions logged after every session"),
        ("Postmortems",  "Incident page auto-created from wrap-up"),
        ("Release Notes","From git history — v2.2 → v2.3 auto"),
        ("Runbooks",     "Updated as team learns new patterns"),
    ]
    for col_data, label, x, color in [
        (jira,       "Jira — What gets auto-updated",       Inches(0.4),  C_BLUE),
        (confluence, "Confluence — What gets published",    Inches(6.85), C_BLUE),
    ]:
        box(s, x, Inches(2.3), Inches(6.0), Inches(3.9), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(1))
        box(s, x, Inches(2.3), Inches(6.0), Inches(0.44), fill=color)
        txt(s, label, x+Inches(0.15), Inches(2.38), Inches(5.7), Inches(0.32), sz=14, bold=True, color=NR_WHITE)
        for i, (field, detail) in enumerate(col_data):
            y = Inches(2.9 + i * 0.66)
            box(s, x+Inches(0.15), y, Inches(5.7), Inches(0.6), fill=NR_LGRAY if i%2==0 else NR_WHITE)
            txt(s, field,  x+Inches(0.28), y+Inches(0.12), Inches(1.5),  Inches(0.36), sz=12, bold=True, color=color)
            txt(s, detail, x+Inches(1.9),  y+Inches(0.12), Inches(3.85), Inches(0.36), sz=11, color=NR_BLACK)

    rule(s, Inches(0.4), Inches(6.35), Inches(12.5))
    txt(s, "Zero manual effort.  Every session documented.  Every time.",
        Inches(0.4), Inches(6.42), Inches(12.5), Inches(0.38),
        sz=14, bold=True, color=NR_BLACK, align=PP_ALIGN.CENTER)
    ftr(s)


def s10_compounds(prs):
    """Knowledge compounds — golden patterns."""
    s = blank(prs)
    # Dark hero background
    box(s, 0, 0, SW, SH, fill=NR_NAVY)
    box(s, 0, 0, SW, Inches(0.06), fill=NR_GREEN)

    txt(s, "Knowledge That Compounds",
        Inches(0.5), Inches(0.55), Inches(12.3), Inches(0.7),
        sz=36, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
    txt(s, "Every session makes every future session smarter",
        Inches(0.5), Inches(1.28), Inches(12.3), Inches(0.42),
        sz=18, italic=True, color=NR_GREEN, align=PP_ALIGN.CENTER)

    layers = [
        ("ALWAYS LOADED",    "hot.md  (~2k tokens at session start)",
         "Active priorities + recent lessons + architecture summary.\n/wrap-up regenerates after every session.",
         NR_GREEN),
        ("PULL ON DEMAND",   "lessons.md  ·  architecture.md  ·  history.md",
         "Team knowledge retrieved only when relevant — not loaded upfront.\nget_memory() · search_memory() · list_lessons()",
         NR_DARK_G),
        ("REPLAYABLE WINS",  "/golden save  →  /replay  →  50× on repeat problems",
         "Validated fixes distilled into reusable templates.\n/replay loads proven steps — team stops re-deriving the same root cause.",
         C_PUR),
    ]

    for i, (tier, title, desc, color) in enumerate(layers):
        y = Inches(2.05 + i * 1.48)
        box(s, Inches(0.4), y, Inches(12.5), Inches(1.38), fill=RGBColor(0x14,0x14,0x30), line=color, lw=Pt(1.5))
        box(s, Inches(0.4), y, Inches(0.06), Inches(1.38), fill=color)
        box(s, Inches(0.55), y+Inches(0.08), Inches(1.6), Inches(0.28), fill=color)
        txt(s, tier, Inches(0.58), y+Inches(0.08), Inches(1.56), Inches(0.26),
            sz=8, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        txt(s, title, Inches(2.35), y+Inches(0.08), Inches(10.35), Inches(0.4),
            sz=15, bold=True, color=NR_WHITE)
        txt(s, desc,  Inches(2.35), y+Inches(0.55), Inches(10.35), Inches(0.72),
            sz=11, color=NR_GRAY)

    box(s, Inches(0.4), Inches(6.52), Inches(12.5), Inches(0.5), fill=RGBColor(0x0A,0x2A,0x18))
    txt(s, "Month 1: 8 issues/task  →  Month 3: 1–2 issues/task  ·  The system gets sharper, not staler.",
        Inches(0.6), Inches(6.6), Inches(12.1), Inches(0.36),
        sz=13, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)


def s11_big_numbers(prs):
    """Hero metrics slide — the one execs remember."""
    s = blank(prs)
    section_header(s, "The Results  —  Numbers the Team Has Measured")

    stats = [
        ("10×",       "faster on novel feature work\nwith graph + memory context",   NR_GREEN),
        ("50×",       "faster on repeat problems\nusing /golden + /replay",           NR_BRIGHT),
        ("6×",        "reduction in MTTR\n3 hours → 30 minutes",                     C_BLUE),
        ("90%",       "test coverage achieved\nvs 60–70% before",                    NR_DARK_G),
    ]

    for i, (num, label, color) in enumerate(stats):
        x = Inches(0.4 + i * 3.22)
        box(s, x, Inches(0.88), Inches(3.05), Inches(3.6), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(1))
        box(s, x, Inches(0.88), Inches(3.05), Inches(0.06), fill=color)
        txt(s, num,   x, Inches(1.1), Inches(3.05), Inches(1.45),
            sz=76, bold=True, color=color, align=PP_ALIGN.CENTER)
        txt(s, label, x+Inches(0.15), Inches(2.62), Inches(2.75), Inches(0.85),
            sz=13, color=NR_GRAY, align=PP_ALIGN.CENTER)

    # Secondary stats bar
    box(s, Inches(0.4), Inches(4.68), Inches(12.5), Inches(1.28), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(0.75))
    txt(s, "Additional measurements", Inches(0.6), Inches(4.78), Inches(12.1), Inches(0.32),
        sz=11, bold=True, color=NR_GRAY)
    secondary = [
        ("2 weeks  →  2 hours", "engineer onboarding"),
        ("14–20 days  →  3–5 days", "feature cycle time"),
        ("<1 day", "rework from hidden deps"),
        ("0 manual updates", "Jira + Confluence"),
    ]
    for i, (val, label) in enumerate(secondary):
        x = Inches(0.6 + i * 3.15)
        txt(s, val,   x, Inches(5.18), Inches(3.0), Inches(0.42), sz=15, bold=True, color=NR_GREEN)
        txt(s, label, x, Inches(5.6),  Inches(3.0), Inches(0.28), sz=10, color=NR_GRAY)

    # Sustained average
    box(s, Inches(0.4), Inches(6.12), Inches(12.5), Inches(0.58), fill=NR_GREEN)
    txt(s, "Sustained team average:  15–25×  productivity improvement  ·  over one month of real data engineering work",
        Inches(0.6), Inches(6.22), Inches(12.1), Inches(0.4),
        sz=15, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
    ftr(s)


def s12_before_after(prs):
    """Before / After table — clean and scannable."""
    s = blank(prs)
    section_header(s, "Before & After — Ingestion Team  ·  3 Repos  ·  ~3 Months")

    cols  = ["What We Measured",     "Before",                               "After (AI-Led)"]
    cxs   = [Inches(0.4),            Inches(4.2),                            Inches(8.15)]
    cws   = [Inches(3.65),           Inches(3.7),                            Inches(4.9)]

    for j, (h, x, w) in enumerate(zip(cols, cxs, cws)):
        box(s, x, Inches(0.82), w, Inches(0.4), fill=(NR_GREEN if j == 2 else NR_CHARCOAL if j == 1 else NR_LGRAY))
        txt(s, h, x+Inches(0.12), Inches(0.88), w-Inches(0.24), Inches(0.3),
            sz=12, bold=True, color=(NR_WHITE if j < 2 else NR_WHITE), align=PP_ALIGN.CENTER)

    data = [
        ("Engineer onboarding",       "2+ weeks",              "2 hours — context loads on day 1"),
        ("Incident MTTR",             "2–3 hours",             "20–30 minutes"),
        ("Feature cycle time",        "14–20 days",            "3–5 days"),
        ("Blast radius visibility",   "Unknown until prod breaks", "Instant — before coding starts"),
        ("Rework from hidden deps",   "~1 sprint / quarter",   "< 1 day"),
        ("Security bugs caught",      "~40%",                  "80–100%  (every PR automated)"),
        ("Test coverage",             "60–70%",                "90%  (gate enforced)"),
        ("Jira / Docs update time",   "Manual, often skipped", "Zero  — auto-updated on /wrap-up"),
    ]

    y = Inches(1.3)
    for i, (metric, before, after) in enumerate(data):
        fill = NR_LGRAY if i % 2 == 0 else NR_WHITE
        for j, (val, x, w) in enumerate(zip([metric, before, after], cxs, cws)):
            box(s, x, y, w, Inches(0.52), fill=fill)
            c = NR_BLACK if j == 0 else (NR_GRAY if j == 1 else NR_DARK_G)
            b = j == 0 or j == 2
            txt(s, val, x+Inches(0.12), y+Inches(0.08), w-Inches(0.24), Inches(0.38),
                sz=11, bold=b, color=c)
        y += Inches(0.52)

    box(s, Inches(0.4), y+Inches(0.06), Inches(12.6), Inches(0.38), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(0.75))
    txt(s, "Repos:  om-airflow-dags  ·  spark-kafka-apps  ·  tf-dataos-new-relic",
        Inches(0.6), y+Inches(0.12), Inches(12.2), Inches(0.28), sz=10, color=NR_GRAY, align=PP_ALIGN.CENTER)
    ftr(s)


def s13_control(prs):
    """Humans always in control — brief, reassuring."""
    s = blank(prs)
    section_header(s, "AI Does the Work.  Humans Stay in Control.  Always.")

    gates = [
        ("1", "Requirements",     "Human writes the spec. AI reads it.",                     NR_CHARCOAL),
        ("2", "Architecture",     "Human approves the plan before any code is written.",     NR_CHARCOAL),
        ("3", "Security Review",  "AI flags every OWASP issue. Any critical finding blocks.", NR_GREEN),
        ("4", "PR Merge",         "Human reviews every PR — agent output treated like human code.", NR_CHARCOAL),
        ("5", "Deploy",           "Human initiates. Human monitors. AI writes release notes.", NR_CHARCOAL),
    ]
    y = Inches(0.88)
    for num, title, detail, color in gates:
        is_highlight = (num == "3")
        h = Inches(0.98)
        box(s, Inches(0.4), y, Inches(12.5), h,
            fill=(RGBColor(0xF0,0xFB,0xF5) if is_highlight else NR_WHITE),
            line=(NR_GREEN if is_highlight else NR_MGRAY), lw=Pt(1.5 if is_highlight else 0.75))
        box(s, Inches(0.4), y, Inches(0.52), h, fill=color)
        txt(s, num,    Inches(0.4),   y+Inches(0.26), Inches(0.52), Inches(0.46),
            sz=18, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        txt(s, title,  Inches(1.08),  y+Inches(0.12), Inches(3.8),  Inches(0.42), sz=15, bold=True)
        txt(s, detail, Inches(5.05),  y+Inches(0.18), Inches(7.7),  Inches(0.62), sz=13, color=NR_GRAY)
        y += h + Inches(0.12)

    box(s, Inches(0.4), y+Inches(0.06), Inches(12.5), Inches(0.42), fill=NR_LGRAY, line=NR_MGRAY, lw=Pt(0.75))
    txt(s, "Agent PRs are treated identically to human PRs — same review process, same standards, same gates.",
        Inches(0.6), y+Inches(0.12), Inches(12.1), Inches(0.32), sz=11, italic=True, color=NR_GRAY, align=PP_ALIGN.CENTER)
    ftr(s)


def s14_start(prs):
    """Getting started — simple 4-step ladder + 4-week rollout."""
    s = blank(prs)
    section_header(s, "Getting Started — From Zero to Productive in 4 Steps")

    steps = [
        ("15 MIN",    "Install",      "./install.sh  +  ./verify.sh",              "One-time setup per engineer. Prereqs auto-checked.", NR_GREEN),
        ("15 SEC",    "/bootstrap",   "First visit to any repo",                   "Detects stack, seeds memory, builds code graph, wires MCPs.", NR_DARK_G),
        ("ONGOING",   "Work",         "Skills auto-trigger as you type",           "20 skills activate on file type or topic. No manual setup.", NR_GREEN),
        ("30 SEC",    "/wrap-up",     "Every session end",                         "Persists history, refreshes graph, updates Jira, rebuilds hot.md.", NR_DARK_G),
    ]

    for i, (time, cmd, trigger, desc, color) in enumerate(steps):
        x = Inches(0.4 + i * 3.22)
        box(s, x, Inches(0.88), Inches(3.06), Inches(4.6), fill=NR_WHITE, line=NR_MGRAY, lw=Pt(1))
        box(s, x, Inches(0.88), Inches(3.06), Inches(0.06), fill=color)
        box(s, x, Inches(0.88), Inches(3.06), Inches(0.68), fill=color)
        txt(s, time, x+Inches(0.1), Inches(0.96), Inches(2.86), Inches(0.5),
            sz=16, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        txt(s, f"Step {i+1}:  {cmd}", x+Inches(0.14), Inches(1.7), Inches(2.78), Inches(0.45),
            sz=14, bold=True, color=color)
        txt(s, trigger, x+Inches(0.14), Inches(2.2), Inches(2.78), Inches(0.36),
            sz=11, italic=True, color=NR_GRAY)
        txt(s, desc, x+Inches(0.14), Inches(2.65), Inches(2.78), Inches(1.5),
            sz=11, color=NR_BLACK)

    # Week rollout
    rule(s, Inches(0.4), Inches(5.65), Inches(12.5))
    weeks = [
        ("Week 1", "Install + bootstrap 1 repo + /wrap-up every session"),
        ("Week 2", "All active repos. First /golden save after a win."),
        ("Week 3", "/avengers on a real multi-file task. Golden library: 3–5 patterns."),
        ("Week 4+", "Team shares goldens. Lessons compound. 15–25× productivity."),
    ]
    for i, (w, desc) in enumerate(weeks):
        x = Inches(0.4 + i * 3.22)
        txt(s, w,    x, Inches(5.76), Inches(3.0), Inches(0.3), sz=11, bold=True, color=NR_GREEN)
        txt(s, desc, x, Inches(6.1),  Inches(3.0), Inches(0.6), sz=10, color=NR_GRAY)
    ftr(s)


def s15_ask(prs):
    """Strategic ask — closing, dark hero."""
    s = blank(prs)
    box(s, 0, 0, SW, SH, fill=NR_NAVY)
    box(s, 0, 0, SW, Inches(0.06), fill=NR_GREEN)

    txt(s, "⬢ new relic", Inches(0.6), Inches(0.3), Inches(3), Inches(0.5),
        sz=20, bold=True, color=NR_GREEN)

    txt(s, "What We're Asking",
        Inches(0.6), Inches(1.0), Inches(10.5), Inches(0.66),
        sz=34, bold=True, color=NR_WHITE)
    rule(s, Inches(0.6), Inches(1.72), Inches(8.0), NR_GREEN)

    asks = [
        ("Support adoption",   "Drive AI-led workflows across all Data Engineering in DTM"),
        ("Allocate time",      "Engineers need 30 min/day: /wrap-up + goldens. It compounds."),
        ("Endorse the model",  "Establish this as the template for all DE teams to adopt"),
    ]
    for i, (label, detail) in enumerate(asks):
        y = Inches(2.05 + i * 1.18)
        box(s, Inches(0.6), y, Inches(11.5), Inches(1.02), fill=RGBColor(0x14,0x14,0x38), line=NR_GREEN, lw=Pt(0.75))
        box(s, Inches(0.6), y, Inches(0.06), Inches(1.02), fill=NR_GREEN)
        txt(s, label,  Inches(0.85), y+Inches(0.08), Inches(2.8),  Inches(0.4), sz=16, bold=True, color=NR_GREEN)
        txt(s, detail, Inches(3.75), y+Inches(0.12), Inches(8.1),  Inches(0.75), sz=14, color=NR_WHITE)

    # Right side — summary numbers
    box(s, Inches(10.3), Inches(1.1), Inches(2.65), Inches(5.5), fill=RGBColor(0x12,0x12,0x30))
    for i, (val, lbl) in enumerate([("15–25×","sustained avg"),("10×","novel work"),("50×","repeat tasks"),("30 min","to root cause")]):
        txt(s, val, Inches(10.3), Inches(1.4+i*1.3), Inches(2.65), Inches(0.7),
            sz=28, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
        txt(s, lbl, Inches(10.3), Inches(2.08+i*1.3), Inches(2.65), Inches(0.32),
            sz=10, italic=True, color=NR_GRAY, align=PP_ALIGN.CENTER)

    txt(s, "Thank You  ·  Questions?",
        Inches(0.6), Inches(5.8), Inches(9.5), Inches(0.65),
        sz=26, color=NR_GRAY, align=PP_ALIGN.LEFT)
    txt(s, "Repo:  github.com/nr-mdakilahmed/claude_code_setup",
        Inches(0.6), Inches(6.52), Inches(9.5), Inches(0.38),
        sz=12, italic=True, color=RGBColor(0x44,0x44,0x66))


# ══════════════════════════════════════════════════════════════════════════════

SLIDES = [
    s01_title, s02_problem, s03_answer, s04_lifecycle,
    s05_onboard, s06_parallel, s07_investigate, s08_ship_safe,
    s09_document, s10_compounds, s11_big_numbers, s12_before_after,
    s13_control, s14_start, s15_ask,
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

    soffice = "/opt/homebrew/bin/soffice"
    if os.path.exists(soffice):
        r = subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                            "--outdir", OUT_DIR, OUT_PPTX],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f"✓  PDF         →  {OUT_PDF}")
        else:
            print(f"⚠  PDF failed: {r.stderr.strip()}")

if __name__ == "__main__":
    main()
