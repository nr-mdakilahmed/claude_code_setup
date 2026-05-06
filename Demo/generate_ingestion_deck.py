#!/usr/bin/env python3
"""
generate_ingestion_deck.py  —  v4
17 executive slides: Full lifecycle with timings · Architecture diagram
· ROI calculation · Hero numbers · NR branding

Usage:  python3 generate_ingestion_deck.py
Output: Ingestion-Team-AI-Led-Demo.pptx  +  .pdf
"""

import os, subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette ───────────────────────────────────────────────────────────────────
G      = RGBColor(0x00, 0xAC, 0x69)   # NR green
GB     = RGBColor(0x00, 0xD0, 0x84)   # NR bright
GD     = RGBColor(0x00, 0x6B, 0x40)   # dark green
NVY    = RGBColor(0x0D, 0x0D, 0x24)   # deep navy
CHR    = RGBColor(0x1F, 0x29, 0x37)   # charcoal
W      = RGBColor(0xFF, 0xFF, 0xFF)
LG     = RGBColor(0xF3, 0xF4, 0xF6)   # light grey bg
MG     = RGBColor(0xE5, 0xE7, 0xEB)   # mid grey border
GR     = RGBColor(0x6B, 0x72, 0x80)   # body grey
BK     = RGBColor(0x14, 0x14, 0x1E)
RED    = RGBColor(0xE5, 0x3E, 0x3E)
AMB    = RGBColor(0xFF, 0xC1, 0x07)   # amber
BLU    = RGBColor(0x00, 0x52, 0xCC)   # Atlassian
PUR    = RGBColor(0x7C, 0x3A, 0xED)
TEAL   = RGBColor(0x06, 0x82, 0xA0)   # teal for docs

FTR = "© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution."
DIR      = os.path.dirname(os.path.abspath(__file__))
ARCH_IMG = os.path.join(DIR, "architecture (1).png")
NR_LOGO  = os.path.join(DIR, "nr_logo_2.png")

SW, SH = Inches(13.33), Inches(7.5)


# ── Helpers ───────────────────────────────────────────────────────────────────
def prs():
    p = Presentation(); p.slide_width = SW; p.slide_height = SH; return p

def blank(p):
    return p.slides.add_slide(p.slide_layouts[6])

def R(s, x, y, w, h, fill=None, ln=None, lw=Pt(0.75)):
    sh = s.shapes.add_shape(1, x, y, w, h)
    sh.fill.solid() if fill else sh.fill.background()
    if fill: sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = ln if ln else (MG if ln is None else None)
    if ln:   sh.line.width = lw
    else:    sh.line.fill.background()
    return sh

def T(s, t, x, y, w, h, sz=12, bold=False, c=BK,
      a=PP_ALIGN.LEFT, it=False, f="Calibri", wrap=True):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = a
    r = p.add_run(); r.text = t
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = it
    r.font.color.rgb = c; r.font.name = f
    return tb

def HL(s, x, y, w, c=MG):
    R(s, x, y, w, Inches(0.018), fill=c)

def ftr(s):
    T(s, FTR, Inches(0.3), Inches(7.08), Inches(11.0), Inches(0.34), sz=7, c=GR)
    if os.path.exists(NR_LOGO):
        # Logo aspect ratio ~4.73:1  →  1.3" × 0.275"
        s.shapes.add_picture(NR_LOGO, Inches(11.75), Inches(7.07), width=Inches(1.3))

def hdr(s, title, h=Inches(0.68)):
    R(s, 0, 0, SW, h, fill=G)
    T(s, title, Inches(0.4), Inches(0.07), Inches(12.5), h - Inches(0.07),
      sz=23, bold=True, c=W, a=PP_ALIGN.CENTER)

def stripe(s, x, y, w, h, color):
    """Thin left accent stripe on a card."""
    R(s, x, y, Inches(0.07), h, fill=color)

def card(s, x, y, w, h, fill=W, border=MG):
    R(s, x, y, w, h, fill=fill, ln=border, lw=Pt(0.85))

def top_bar(s, x, y, w, h=Inches(0.06), color=G):
    R(s, x, y, w, h, fill=color)

# ══════════════════════════════════════════════════════════════════════════════
#  SLIDES
# ══════════════════════════════════════════════════════════════════════════════

def s01_title(p):
    s = blank(p)
    R(s, 0, 0, SW, SH, fill=NVY)
    R(s, 0, 0, SW, Inches(0.06), fill=G)
    R(s, 0, SH - Inches(0.06), SW, Inches(0.06), fill=G)
    R(s, Inches(8.6), 0, Inches(4.73), SH, fill=RGBColor(0x12, 0x12, 0x30))
    if os.path.exists(NR_LOGO):
        s.shapes.add_picture(NR_LOGO, Inches(0.6), Inches(0.28), width=Inches(2.0))
    T(s, "Ingestion Team",           Inches(0.6), Inches(1.52), Inches(7.6), Inches(0.72), sz=38, bold=True, c=W)
    T(s, "AI-Led Development",       Inches(0.6), Inches(2.26), Inches(7.6), Inches(0.65), sz=34, bold=True, c=G)
    T(s, "Environment",              Inches(0.6), Inches(2.93), Inches(7.6), Inches(0.62), sz=34, bold=True, c=W)
    HL(s, Inches(0.6), Inches(3.7), Inches(6.8), G)
    T(s, "Claude Code  +  GitHub Copilot  +  New Relic MCP",
      Inches(0.6), Inches(3.86), Inches(7.6), Inches(0.42), sz=15, c=GR, it=True)

    chips = [
        ("🚀", "Rapid Development"),
        ("🔍", "Instant Logs & RCA"),
        ("⚡", "Multi-Agent Orchestration"),
        ("🧠", "Compound Knowledge"),
        ("📈", "3×  Productivity"),
    ]
    for i, (ic, lb) in enumerate(chips):
        yy = Inches(1.2 + i * 1.05)
        R(s, Inches(8.9), yy, Inches(4.0), Inches(0.82),
          fill=RGBColor(0x1A, 0x1A, 0x3A), ln=RGBColor(0x2A, 0x2A, 0x5A))
        R(s, Inches(8.9), yy, Inches(0.06), Inches(0.82), fill=G)
        T(s, ic, Inches(9.06), yy + Inches(0.2), Inches(0.4), Inches(0.42), sz=18)
        T(s, lb, Inches(9.52), yy + Inches(0.2), Inches(3.25), Inches(0.42), sz=13, c=W)


def s02_problem(p):
    s = blank(p)
    hdr(s, "The Challenge — Four Real Pains the DataOS Ingestion Team Was Living With")

    cards = [
        ("🕐", "Slow Development Tickets",  "2–3 DAYS",   "per ticket — regardless of complexity or volume",   RED),
        ("🔍", "Pipeline Debugging",        "30 MIN–3 HRS", "backtracking alert issues one by one manually",  AMB),
        ("💥", "Hidden Blast Radius",       "5-DAY",      "incident caused by a change no one knew would break", CHR),
        ("🗂", "No Historical Context",     "HOURS–DAYS", "re-discovering repo structure and past decisions\nevery time someone joined, left, or came back",     CHR),
    ]
    positions = [(Inches(0.4), Inches(0.82)), (Inches(6.88), Inches(0.82)),
                 (Inches(0.4), Inches(3.92)), (Inches(6.88), Inches(3.92))]

    for (ic, title, big, sub, accent), (x, y) in zip(cards, positions):
        w, h = Inches(6.05), Inches(2.88)
        card(s, x, y, w, h)
        top_bar(s, x, y, w, color=accent)
        T(s, ic + "  " + title, x + Inches(0.22), y + Inches(0.2), w - Inches(0.44), Inches(0.44), sz=15, bold=True)
        T(s, big,  x + Inches(0.22), y + Inches(0.72), w - Inches(0.44), Inches(0.9),
          sz=48, bold=True, c=accent, a=PP_ALIGN.CENTER)
        HL(s, x + Inches(0.22), y + Inches(1.72), w - Inches(0.44))
        T(s, sub,  x + Inches(0.22), y + Inches(1.82), w - Inches(0.44), Inches(0.42), sz=13, c=GR)

    # Total cost banner
    R(s, Inches(0.4), Inches(6.95), Inches(12.5), Inches(0.0))  # spacer
    ftr(s)


def s03_how_we_work(p):
    """DataOS Ingestion — how the team actually runs AI-led development."""
    s = blank(p)
    hdr(s, "DataOS Ingestion  —  How We Run AI-Led Development Today")

    # Left: 3-stage data pipeline flow
    card(s, Inches(0.4), Inches(0.82), Inches(4.1), Inches(5.75))
    R(s, Inches(0.4), Inches(0.82), Inches(4.1), Inches(0.48), fill=CHR)
    T(s, "What We Own", Inches(0.6), Inches(0.9), Inches(3.7), Inches(0.34), sz=14, bold=True, c=W)

    # Stage 1 — Data Sources
    T(s, "DATA SOURCES", Inches(0.6), Inches(1.44), Inches(3.7), Inches(0.26),
      sz=9, bold=True, c=GR)
    R(s, Inches(0.55), Inches(1.72), Inches(3.8), Inches(0.82), fill=LG, ln=MG, lw=Pt(0.75))
    T(s, "Billing Platform  ·  Kafka\nSFDC  ·  Zuora  ·  etc.",
      Inches(0.7), Inches(1.8), Inches(3.5), Inches(0.66), sz=11, c=BK)

    # Arrow
    T(s, "↓", Inches(0.55), Inches(2.6), Inches(3.8), Inches(0.38),
      sz=20, bold=True, c=G, a=PP_ALIGN.CENTER)

    # Stage 2 — Ingestion (what we own — highlighted)
    T(s, "INGESTION  —  WE OWN THIS", Inches(0.6), Inches(3.04), Inches(3.7), Inches(0.26),
      sz=9, bold=True, c=G)
    R(s, Inches(0.55), Inches(3.32), Inches(3.8), Inches(1.02), fill=G)
    T(s, "FiveTran  ·  Kafka  ·  NRDB\nSpark  ·  Custom Pipelines",
      Inches(0.7), Inches(3.46), Inches(3.5), Inches(0.74), sz=11, bold=True, c=W)

    # Arrow
    T(s, "↓", Inches(0.55), Inches(4.4), Inches(3.8), Inches(0.38),
      sz=20, bold=True, c=G, a=PP_ALIGN.CENTER)

    # Stage 3 — Downstream
    T(s, "DOWNSTREAM ZONE 2", Inches(0.6), Inches(4.84), Inches(3.7), Inches(0.26),
      sz=9, bold=True, c=GR)
    R(s, Inches(0.55), Inches(5.12), Inches(3.8), Inches(0.82), fill=LG, ln=MG, lw=Pt(0.75))
    T(s, "Consumer  ·  Data Lake\nDashboard",
      Inches(0.7), Inches(5.22), Inches(3.5), Inches(0.64), sz=11, c=BK)

    # Middle: daily workflow
    card(s, Inches(4.72), Inches(0.82), Inches(4.1), Inches(5.75))
    R(s, Inches(4.72), Inches(0.82), Inches(4.1), Inches(0.48), fill=G)
    T(s, "Daily Workflow", Inches(4.92), Inches(0.9), Inches(3.7), Inches(0.34), sz=14, bold=True, c=W)
    steps = [
        ("1", "Start with full context",       "Memory + codebase graph auto-load in seconds"),
        ("2", "Copilot: lines + blind spot check", "Autocomplete in IDE · cross-model review catches what Claude misses"),
        ("3", "Skills trigger automatically",  "/airflow · /pyspark · /nrql · /terraform · /sql"),
        ("4", "Incidents diagnosed via NR MCP","30 min–3 hrs → 0–20 min for alert issues"),
        ("5", "/avengers for big tasks",       "5 parallel agents — 2–3 days → 2–6 hours"),
        ("6", "/wrap-up closes the loop",      "Jira updated · knowledge captured · graph refreshed"),
    ]
    for i, (num, title, sub) in enumerate(steps):
        y = Inches(1.46 + i * 0.72)
        R(s, Inches(4.87), y, Inches(3.8), Inches(0.66),
          fill=(RGBColor(0xF0, 0xFB, 0xF5) if i % 2 == 0 else W), ln=MG, lw=Pt(0.5))
        R(s, Inches(4.87), y, Inches(0.36), Inches(0.66), fill=G)
        T(s, num,   Inches(4.87), y + Inches(0.17), Inches(0.36), Inches(0.34),
          sz=11, bold=True, c=W, a=PP_ALIGN.CENTER)
        T(s, title, Inches(5.32), y + Inches(0.04), Inches(3.2), Inches(0.32), sz=11, bold=True)
        T(s, sub,   Inches(5.32), y + Inches(0.36), Inches(3.2), Inches(0.28), sz=9.5, c=GR)

    # Right: tools stack
    card(s, Inches(9.05), Inches(0.82), Inches(3.85), Inches(5.75))
    R(s, Inches(9.05), Inches(0.82), Inches(3.85), Inches(0.48), fill=GD)
    T(s, "Tools in Use", Inches(9.25), Inches(0.9), Inches(3.45), Inches(0.34), sz=14, bold=True, c=W)
    tools = [
        ("Claude Code",        "20 skills · memory · /avengers\nTeam environment AI",      G),
        ("GitHub Copilot",     "Line completion · inline chat\nCross-model review (covers Claude blind spots)", CHR),
        ("NR MCP",             "Live logs · metrics · traces\nDiagnose without leaving chat", BLU),
        ("Jira + Confluence",  "Tickets + docs auto-updated\non every /wrap-up",            TEAL),
        ("Code Graph",         "28 tools · blast radius\nImpact analysis before coding",   PUR),
    ]
    for i, (name, desc, color) in enumerate(tools):
        y = Inches(1.46 + i * 0.98)
        R(s, Inches(9.2), y, Inches(3.52), Inches(0.88), fill=LG, ln=MG, lw=Pt(0.75))
        R(s, Inches(9.2), y, Inches(0.07), Inches(0.88), fill=color)
        T(s, name, Inches(9.36), y + Inches(0.06), Inches(2.0), Inches(0.38), sz=12, bold=True, c=color)
        T(s, desc, Inches(9.36), y + Inches(0.46), Inches(3.1), Inches(0.36), sz=10, c=GR)
    ftr(s)


def s03b_two_tools(p):
    """Copilot + Claude Code — how they work together."""
    s = blank(p)
    R(s, 0, 0, SW, Inches(1.22), fill=G)
    T(s, "Two AI Tools.  Different Jobs.  Better Together.",
      Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.8),
      sz=26, bold=True, c=W, a=PP_ALIGN.CENTER)

    # Copilot panel
    card(s, Inches(0.4), Inches(1.38), Inches(5.75), Inches(4.82), fill=LG)
    R(s, Inches(0.4), Inches(1.38), Inches(5.75), Inches(0.5), fill=CHR)
    T(s, "GitHub Copilot  —  In the IDE",
      Inches(0.6), Inches(1.46), Inches(5.35), Inches(0.36), sz=16, bold=True, c=W)
    copilot_items = [
        "Autocomplete lines & functions as you type",
        "Inline chat: explain, refactor, or debug code",
        "Generate tests and boilerplate instantly",
        "Cross-model review: GPT catches Claude blind spots",
    ]
    for i, txt_ in enumerate(copilot_items):
        T(s, "✅  " + txt_, Inches(0.62), Inches(2.06 + i * 0.52),
          Inches(5.3), Inches(0.44), sz=12, c=BK)

    # "Claude Code fills the gap" label
    HL(s, Inches(0.62), Inches(4.2), Inches(5.3))
    T(s, "Together: deliberate cross-model coverage —",
      Inches(0.62), Inches(4.3), Inches(5.3), Inches(0.3),
      sz=10, bold=True, c=GD, it=True)
    gap_items = [
        "Different AI models catch different blind spots",
        "Claude leads · Copilot verifies · humans approve",
    ]
    for i, txt_ in enumerate(gap_items):
        T(s, txt_, Inches(0.62), Inches(4.66 + i * 0.36),
          Inches(5.3), Inches(0.32), sz=10.5, c=GR)

    # + bridge
    T(s, "+", Inches(6.2), Inches(3.1), Inches(0.9), Inches(0.9),
      sz=44, bold=True, c=G, a=PP_ALIGN.CENTER)

    # Claude Code panel
    card(s, Inches(7.15), Inches(1.38), Inches(5.75), Inches(4.82),
         fill=RGBColor(0xF0, 0xFB, 0xF5), border=G)
    R(s, Inches(7.15), Inches(1.38), Inches(5.75), Inches(0.5), fill=G)
    T(s, "Claude Code  —  Team Environment AI",
      Inches(7.35), Inches(1.46), Inches(5.35), Inches(0.36), sz=16, bold=True, c=W)
    cc_items = [
        ("Full codebase context at every session start",      ""),
        ("Queries NR, Jira, Confluence live in the chat",     ""),
        ("Blast radius visible before writing a single line", ""),
        ("/avengers: 5 parallel agents — 2–3 days → 2–6h",   "✅"),
        ("Incident diagnosis via NR MCP — 0–20 min",          "✅"),
        ("20 skills auto-trigger on file type or topic",      ""),
        ("Jira + Confluence auto-update on every session end",""),
        ("5-layer review: CC Opus → Copilot GPT (blind spots) → agents → human", ""),
    ]
    for i, (txt_, badge) in enumerate(cc_items):
        line = ("⚡  " if badge else "✅  ") + txt_
        c_ = GD if badge else BK
        T(s, line, Inches(7.35), Inches(2.06 + i * 0.46),
          Inches(5.35), Inches(0.42), sz=11.5, c=c_, bold=(badge == "✅"))

    # Full-width "Together" banner
    R(s, Inches(0.4), Inches(6.35), Inches(12.5), Inches(0.58), fill=G)
    T(s, "Together:  8–12×  overall productivity for DataOS Ingestion DE tasks  —  reported by the team",
      Inches(0.6), Inches(6.44), Inches(12.1), Inches(0.4),
      sz=15, bold=True, c=W, a=PP_ALIGN.CENTER)
    ftr(s)


def s04_architecture(p):
    """Full architecture diagram slide."""
    s = blank(p)
    hdr(s, "System Architecture  —  How It All Connects Under One Environment")

    if os.path.exists(ARCH_IMG):
        # Fill most of the slide with the architecture image
        s.shapes.add_picture(ARCH_IMG, Inches(0.3), Inches(0.78), width=Inches(12.73))
    else:
        T(s, f"[Architecture image not found at: {ARCH_IMG}]",
          Inches(0.4), Inches(3.5), Inches(12.5), Inches(0.5), sz=14, c=RED, a=PP_ALIGN.CENTER)

    ftr(s)


def s05_lifecycle(p):
    """THE CENTERPIECE — lifecycle with time savings at each phase."""
    s = blank(p)
    hdr(s, "Full AI-Led Development Lifecycle  —  Time Savings at Every Phase")

    # Before/After times: verified by engineer (marked) or omitted if not confirmed
    # "—" = scope-dependent or not confirmed; no invented numbers
    phases = [
        ("01", "Requirement",  "Manager\n/ PM",      CHR,  W,    "—",      "—"),
        ("02", "Spec & Plan",  "AI-assisted",         G,    W,    "4–6h",   "20m–1h"),
        ("03", "Architect",    "AI + Graph",          GD,   W,    "2–4d",   "1–2d"),
        ("04", "Build",        "Task &\nvolume dep.", G,    W,    "2–3d",   "2–6h"),
        ("05", "Review",       "5-layer\nAI+Human",  GD,   W,    "—",      "—"),
        ("06", "Test & Gate",  "AI auto-\nmated",     G,    W,    "—",      "—"),
        ("07", "Deploy",       "Human\ninitiates",    CHR,  W,    "—",      "—"),
        ("08", "Monitor",      "NR MCP\n(AI)",        BLU,  W,    "1–10h",  "0–20m"),
        ("09", "Document",     "AI auto-\nupdate",    TEAL, W,    "manual", "auto"),
        ("10", "Learn",        "Golden\npatterns",    PUR,  W,    "—",      "auto"),
    ]

    BW = Inches(1.24)
    BH = Inches(1.32)
    GAP = Inches(0.01)
    total_w = len(phases) * BW + (len(phases) - 1) * GAP
    sx = (SW - total_w) / 2

    for i, (num, title, who, fill, tc, before, after) in enumerate(phases):
        x = sx + i * (BW + GAP)
        y = Inches(0.82)

        # Phase box
        R(s, x, y, BW, BH, fill=fill)
        T(s, num,   x + Inches(0.08), y + Inches(0.06), BW - Inches(0.16), Inches(0.24),
          sz=9, bold=True, c=RGBColor(0xAA, 0xFF, 0xAA) if fill != CHR else W)
        T(s, title, x + Inches(0.06), y + Inches(0.28), BW - Inches(0.12), Inches(0.52),
          sz=11, bold=True, c=tc, a=PP_ALIGN.CENTER)
        T(s, who,   x + Inches(0.06), y + Inches(0.84), BW - Inches(0.12), Inches(0.38),
          sz=8, c=RGBColor(0xCC, 0xFF, 0xCC) if fill not in (W, LG) else GR,
          a=PP_ALIGN.CENTER)

        # Arrow
        if i < len(phases) - 1:
            T(s, "›", x + BW - Inches(0.08), y + Inches(0.42), Inches(0.22), Inches(0.48),
              sz=16, bold=True, c=RGBColor(0xBB, 0xBB, 0xCC), a=PP_ALIGN.CENTER)

        # Time savings row
        by = y + BH + Inches(0.08)
        th = Inches(0.44)
        R(s, x, by, BW, th, fill=RGBColor(0xFF, 0xEE, 0xEE) if before not in ("∞", "0m") else LG)
        T(s, before, x + Inches(0.04), by + Inches(0.06), BW - Inches(0.08), Inches(0.3),
          sz=9, bold=True, c=RED if before not in ("∞", "0m") else GR, a=PP_ALIGN.CENTER)

        by2 = by + th + Inches(0.04)
        R(s, x, by2, BW, th, fill=RGBColor(0xF0, 0xFB, 0xF5))
        T(s, after, x + Inches(0.04), by2 + Inches(0.06), BW - Inches(0.08), Inches(0.3),
          sz=9, bold=True, c=GD, a=PP_ALIGN.CENTER)

    # Column labels on left
    label_y = Inches(0.82) + BH + Inches(0.08)
    T(s, "Before:", Inches(0.05), label_y + Inches(0.08), Inches(0.55), Inches(0.3), sz=8, c=RED, bold=True)
    T(s, "After:",  Inches(0.05), label_y + Inches(0.56), Inches(0.55), Inches(0.3), sz=8, c=GD,  bold=True)

    # Bottom summary — only confirmed phases shown; "—" = not yet measured
    R(s, Inches(0.4), Inches(5.96), Inches(12.5), Inches(0.62), fill=G)
    T(s, "Confirmed by engineer  ·  Spec+Arch+Build: days → hours  ·  Alert issue diagnosis: hours → 0–20 min  ·  Overall: 8–12×",
      Inches(0.6), Inches(6.08), Inches(12.1), Inches(0.42),
      sz=15, bold=True, c=W, a=PP_ALIGN.CENTER)
    ftr(s)


def s06_faster_dev(p):
    """Faster Development — matches Challenge 1: Slow Development Tickets."""
    s = blank(p)
    hdr(s, "Faster Development  —  Days Became Hours")

    # Before
    card(s, Inches(0.4), Inches(0.82), Inches(5.8), Inches(3.72))
    top_bar(s, Inches(0.4), Inches(0.82), Inches(5.8), color=RED)
    T(s, "BEFORE", Inches(0.6), Inches(0.98), Inches(5.4), Inches(0.34), sz=12, bold=True, c=GR)
    T(s, "2–3 DAYS", Inches(0.6), Inches(1.36), Inches(5.4), Inches(1.02),
      sz=58, bold=True, c=RED, a=PP_ALIGN.CENTER)
    T(s, "Per development ticket — regardless of complexity\nContext rebuilt from scratch every time",
      Inches(0.6), Inches(2.52), Inches(5.4), Inches(0.78), sz=12, c=GR, a=PP_ALIGN.CENTER)

    T(s, "→", Inches(6.38), Inches(2.0), Inches(0.55), Inches(0.7),
      sz=34, bold=True, c=G, a=PP_ALIGN.CENTER)

    # After
    card(s, Inches(7.1), Inches(0.82), Inches(5.8), Inches(3.72), border=G,
         fill=RGBColor(0xF0, 0xFB, 0xF5))
    top_bar(s, Inches(7.1), Inches(0.82), Inches(5.8), color=G)
    T(s, "AFTER", Inches(7.3), Inches(0.98), Inches(5.4), Inches(0.34), sz=12, bold=True, c=GD)
    T(s, "2–6 HOURS", Inches(7.3), Inches(1.36), Inches(5.4), Inches(1.02),
      sz=52, bold=True, c=G, a=PP_ALIGN.CENTER)
    T(s, "Task & volume dependent\nFull context auto-loaded · skills auto-trigger · graph aware",
      Inches(7.3), Inches(2.52), Inches(5.4), Inches(0.78), sz=12, c=GD, a=PP_ALIGN.CENTER)

    # Three outcome cards
    cs = [
        ("Spec & Plan\n4–6h → 20m–1h",  "AI assists planning from existing\ncodebase patterns — not from scratch"),
        ("Architecture\n2–4d → 1–2d",    "Code graph shows impact +\nCDD & Confluence auto-updated"),
        ("Context\nalways ready",         "Memory + graph auto-load\nNo archaeology every session"),
    ]
    for i, (title, desc) in enumerate(cs):
        x = Inches(0.4 + i * 4.3)
        card(s, x, Inches(4.72), Inches(4.06), Inches(1.92))
        top_bar(s, x, Inches(4.72), Inches(4.06), color=G)
        T(s, title, x + Inches(0.18), Inches(4.84), Inches(3.7), Inches(0.52), sz=13, bold=True, c=GD)
        T(s, desc,  x + Inches(0.18), Inches(5.42), Inches(3.7), Inches(1.0),  sz=11, c=GR)
    ftr(s)


def s07_parallel(p):
    s = blank(p)
    hdr(s, "/avengers — Five AI Engineers Working in Parallel on One Task")

    T(s, "Tasks that take one engineer one full day, completed in under 2 hours:",
      Inches(0.4), Inches(0.82), Inches(8.5), Inches(0.38), sz=13, c=GR)

    # Orchestrator
    R(s, Inches(0.4), Inches(1.28), Inches(8.2), Inches(0.74), fill=CHR)
    T(s, "Orchestrator  (Opus model — plans, routes, validates, shuts down)",
      Inches(0.6), Inches(1.36), Inches(7.6), Inches(0.4), sz=14, bold=True, c=W)

    agents = [
        ("Planner",       "Researches codebase\n→ implementation plan", GD),
        ("Coder ×N",      "Parallel code writing\nverifies build passes", G),
        ("Code Reviewer", "Code standards +\nsecurity checks",           G),
        ("Validator",     "Tests + impact analysis\nbefore any merge",    GD),
    ]
    for i, (name, desc, color) in enumerate(agents):
        x = Inches(0.4 + i * 2.06)
        R(s, x, Inches(2.2), Inches(1.88), Inches(1.62), fill=color)
        T(s, name, x + Inches(0.1), Inches(2.3),  Inches(1.68), Inches(0.4), sz=12, bold=True, c=W, a=PP_ALIGN.CENTER)
        T(s, desc, x + Inches(0.1), Inches(2.75), Inches(1.68), Inches(0.88), sz=10, c=RGBColor(0xCC, 0xFF, 0xCC), a=PP_ALIGN.CENTER)

    # Right: hero metric
    card(s, Inches(8.82), Inches(1.06), Inches(4.12), Inches(5.62), fill=LG)
    T(s, "1 DAY",   Inches(8.82), Inches(1.5),  Inches(4.12), Inches(0.9), sz=54, bold=True, c=RED, a=PP_ALIGN.CENTER)
    T(s, "↓",       Inches(8.82), Inches(2.48), Inches(4.12), Inches(0.5), sz=28, bold=True, c=G,   a=PP_ALIGN.CENTER)
    T(s, "2 HOURS", Inches(8.82), Inches(3.04), Inches(4.12), Inches(0.9), sz=54, bold=True, c=G,   a=PP_ALIGN.CENTER)
    T(s, "Airflow DAG + dbt model\n+ NR alert — all in parallel",
      Inches(8.92), Inches(4.02), Inches(3.92), Inches(0.84), sz=12, c=GR, a=PP_ALIGN.CENTER)
    T(s, "Engineer reviews\n1 PR instead of 5 files",
      Inches(8.92), Inches(4.94), Inches(3.92), Inches(0.62), sz=13, bold=True, c=GD, a=PP_ALIGN.CENTER)

    # Steps
    steps = [
        "Orchestrator reads spec → spawns Planner + Coders simultaneously",
        "Each agent works on an independent file — zero waiting",
        "Reviewer + Validator run in parallel on all output",
        "Human sees a single clean PR to approve",
    ]
    for i, step in enumerate(steps):
        fill_ = RGBColor(0xF0, 0xFB, 0xF5) if i % 2 == 0 else W
        R(s, Inches(0.4), Inches(4.06 + i * 0.52), Inches(8.2), Inches(0.48), fill=fill_, ln=MG, lw=Pt(0.5))
        T(s, f"{i+1}.", Inches(0.56), Inches(4.14 + i * 0.52), Inches(0.34), Inches(0.36), sz=12, bold=True, c=G)
        T(s, step, Inches(0.96), Inches(4.14 + i * 0.52), Inches(7.4), Inches(0.36), sz=11, c=BK)
    ftr(s)


def s08_investigate(p):
    s = blank(p)
    hdr(s, "Incident Investigation  —  AI Queries New Relic Directly, Instantly")

    # Before
    card(s, Inches(0.4), Inches(0.82), Inches(5.8), Inches(5.55))
    top_bar(s, Inches(0.4), Inches(0.82), Inches(5.8), color=RED)
    T(s, "BEFORE  —  Manual hunt",
      Inches(0.6), Inches(0.98), Inches(5.4), Inches(0.38), sz=14, bold=True)
    T(s, "2–3\nHOURS", Inches(0.6), Inches(1.4), Inches(5.4), Inches(1.22),
      sz=56, bold=True, c=RED, a=PP_ALIGN.CENTER)
    T(s, "Log in to NR UI  ·  navigate to entity  ·  scroll logs\nswitch tabs  ·  compare charts  ·  Slack teammates",
      Inches(0.6), Inches(2.76), Inches(5.4), Inches(0.72), sz=11, c=GR, a=PP_ALIGN.CENTER)
    HL(s, Inches(0.6), Inches(3.58), Inches(5.4))
    T(s, "Form hypothesis → test → repeat →  still uncertain\nCustomer impact growing every minute",
      Inches(0.6), Inches(3.68), Inches(5.4), Inches(0.62), sz=12, c=RED, a=PP_ALIGN.CENTER)

    T(s, "→", Inches(6.38), Inches(2.9), Inches(0.55), Inches(0.6), sz=32, bold=True, c=G, a=PP_ALIGN.CENTER)

    # After
    card(s, Inches(7.1), Inches(0.82), Inches(5.8), Inches(5.55), border=G,
         fill=RGBColor(0xF0, 0xFB, 0xF5))
    top_bar(s, Inches(7.1), Inches(0.82), Inches(5.8), color=G)
    T(s, "AFTER  —  AI-powered diagnosis",
      Inches(7.3), Inches(0.98), Inches(5.4), Inches(0.38), sz=14, bold=True, c=GD)
    T(s, "30\nMINS", Inches(7.3), Inches(1.4), Inches(5.4), Inches(1.22),
      sz=56, bold=True, c=G, a=PP_ALIGN.CENTER)
    T(s, "\"analyze kafka consumer lag last 4 hours\"\nClaude queries NR, returns structured analysis",
      Inches(7.3), Inches(2.76), Inches(5.4), Inches(0.72), sz=11, c=GD, a=PP_ALIGN.CENTER)
    HL(s, Inches(7.3), Inches(3.58), Inches(5.4), G)
    T(s, "Consumer lag  ·  partition skew  ·  throughput drop\nAffected services identified — fix scoped immediately",
      Inches(7.3), Inches(3.68), Inches(5.4), Inches(0.62), sz=12, c=GD, a=PP_ALIGN.CENTER)
    T(s, "12 New Relic tools  ·  Jira auto-updated  ·  root cause in minutes",
      Inches(7.3), Inches(4.48), Inches(5.4), Inches(0.38), sz=11, bold=True, c=GD, a=PP_ALIGN.CENTER)
    ftr(s)


def s09_ship(p):
    s = blank(p)
    hdr(s, "Impact Analysis  —  Know What Breaks Before Writing a Single Line")

    R(s, Inches(0.4), Inches(0.82), Inches(12.5), Inches(0.84), fill=G)
    T(s, "We see the full impact of every change  BEFORE  it touches production.",
      Inches(0.6), Inches(0.94), Inches(12.1), Inches(0.62),
      sz=23, bold=True, c=W, a=PP_ALIGN.CENTER)

    card(s, Inches(0.4), Inches(1.84), Inches(5.9), Inches(2.44))
    top_bar(s, Inches(0.4), Inches(1.84), Inches(5.9), color=RED)
    T(s, "⚠  Before: Invisible blast radius",
      Inches(0.6), Inches(1.96), Inches(5.5), Inches(0.4), sz=14, bold=True, c=RED)
    T(s, "Engineer changes a pipeline file.\nDeploys. A downstream consumer breaks silently.\n5-day incident — all from one undetected dependency.",
      Inches(0.6), Inches(2.44), Inches(5.5), Inches(1.6), sz=12, c=GR)

    card(s, Inches(7.0), Inches(1.84), Inches(5.9), Inches(2.44), border=G,
         fill=RGBColor(0xF0, 0xFB, 0xF5))
    top_bar(s, Inches(7.0), Inches(1.84), Inches(5.9), color=G)
    T(s, "✅  After: Instant clarity",
      Inches(7.2), Inches(1.96), Inches(5.5), Inches(0.4), sz=14, bold=True, c=GD)
    T(s, "Impact analysis runs before coding.\nSees 3 callers, 1 downstream consumer.\nFix scoped. Ships confidently. Zero incident.",
      Inches(7.2), Inches(2.44), Inches(5.5), Inches(1.6), sz=12, c=BK)

    T(s, "→", Inches(6.27), Inches(2.66), Inches(0.55), Inches(0.5), sz=28, bold=True, c=G, a=PP_ALIGN.CENTER)

    metrics = [
        ("~1 sprint/qtr",   "absorbed in surprise\nrework — before",     RED),
        ("< 1 day",         "rework after impact-\naware development",    G),
        ("0 blind deploys",  "every change impact-\nchecked first",       GD),
        ("Auto-updates",    "dependency map rebuilt\non every file save",  GD),
    ]
    for i, (val, label, c_) in enumerate(metrics):
        x = Inches(0.4 + i * 3.22)
        card(s, x, Inches(4.52), Inches(3.06), Inches(1.76))
        top_bar(s, x, Inches(4.52), Inches(3.06), color=c_)
        T(s, val,   x + Inches(0.15), Inches(4.64), Inches(2.76), Inches(0.6), sz=22, bold=True, c=c_)
        T(s, label, x + Inches(0.15), Inches(5.28), Inches(2.76), Inches(0.86), sz=11, c=GR)
    ftr(s)


def s10_document(p):
    s = blank(p)
    hdr(s, "Documentation That Writes Itself  —  Jira & Confluence Always Up to Date")

    flow = [
        ("Work session\ncompletes",    W,    BK),
        ("/wrap-up\nfires (~30s)",     G,    W),
        ("Claude drafts\nsummary",     G,    W),
        ("Jira ticket\nauto-updated",  BLU,  W),
        ("Confluence\npublished",      TEAL, W),
    ]
    for i, (label, fill, tc) in enumerate(flow):
        x = Inches(0.4 + i * 2.58)
        R(s, x, Inches(0.82), Inches(2.35), Inches(1.22),
          fill=fill, ln=(G if fill == G else BLU if fill == BLU else TEAL if fill == TEAL else MG), lw=Pt(1.2))
        T(s, label, x + Inches(0.1), Inches(1.02), Inches(2.15), Inches(0.82),
          sz=12, bold=(fill != W), c=tc, a=PP_ALIGN.CENTER)
        if i < 4:
            T(s, "→", Inches(2.8 + i * 2.58), Inches(1.3), Inches(0.36), Inches(0.38),
              sz=22, bold=True, c=G, a=PP_ALIGN.CENTER)

    jira = [("Status",    "In Review → Done  ·  automatically"),
            ("Comment",   "What was done + decisions made"),
            ("Worklog",   "Time logged from session duration"),
            ("Links",     "Commits linked via branch name")]
    conf  = [("Architecture","Decisions logged after every session"),
             ("Postmortem", "Incident page auto-created on wrap-up"),
             ("Release",    "Notes from git history — auto-versioned"),
             ("Runbooks",   "Updated as team learns new patterns")]

    for col_data, label, x, acc in [
        (jira, "Jira  —  What gets auto-updated",    Inches(0.4),  BLU),
        (conf, "Confluence  —  What gets published", Inches(6.85), TEAL),
    ]:
        card(s, x, Inches(2.22), Inches(6.0), Inches(4.02))
        R(s, x, Inches(2.22), Inches(6.0), Inches(0.44), fill=acc)
        T(s, label, x + Inches(0.15), Inches(2.3), Inches(5.7), Inches(0.32), sz=14, bold=True, c=W)
        for i, (field, detail) in enumerate(col_data):
            y = Inches(2.82 + i * 0.68)
            R(s, x + Inches(0.15), y, Inches(5.7), Inches(0.62),
              fill=LG if i % 2 == 0 else W)
            T(s, field,  x + Inches(0.28), y + Inches(0.12), Inches(1.5),  Inches(0.38), sz=12, bold=True, c=acc)
            T(s, detail, x + Inches(1.9),  y + Inches(0.12), Inches(3.85), Inches(0.38), sz=11, c=BK)

    HL(s, Inches(0.4), Inches(6.4), Inches(12.5))
    T(s, "Zero manual effort.  Every session documented.  Every time.",
      Inches(0.4), Inches(6.48), Inches(12.5), Inches(0.38),
      sz=15, bold=True, c=BK, a=PP_ALIGN.CENTER)
    ftr(s)


def s11_compounds(p):
    s = blank(p)
    R(s, 0, 0, SW, SH, fill=NVY)
    R(s, 0, 0, SW, Inches(0.06), fill=G)

    T(s, "Knowledge That Compounds",
      Inches(0.5), Inches(0.55), Inches(12.3), Inches(0.7),
      sz=36, bold=True, c=W, a=PP_ALIGN.CENTER)
    T(s, "Every session makes every future session smarter — knowledge never leaves the team",
      Inches(0.5), Inches(1.3), Inches(12.3), Inches(0.44),
      sz=16, it=True, c=G, a=PP_ALIGN.CENTER)

    layers = [
        ("ALWAYS LOADED",   "Session memory — auto-loads at every session start",
         "Active priorities + recent lessons + architecture summary loaded automatically. No manual setup. Zero tokens wasted.",
         G),
        ("PULL ON DEMAND",  "Team knowledge — retrieved only when relevant",
         "Patterns · architecture decisions · session history · past plans. Fetched on demand — only what's needed, when it's needed.",
         GD),
        ("REPLAYABLE WINS", "Validated fixes — saved as reusable templates",
         "After a confirmed fix: the steps are captured and indexed. Next time the same problem appears, the proven solution loads instantly.",
         PUR),
    ]

    for i, (tier, title, desc, color) in enumerate(layers):
        y = Inches(2.1 + i * 1.46)
        R(s, Inches(0.4), y, Inches(12.5), Inches(1.36), fill=RGBColor(0x14, 0x14, 0x30), ln=color, lw=Pt(1.2))
        R(s, Inches(0.4), y, Inches(0.07), Inches(1.36), fill=color)
        R(s, Inches(0.56), y + Inches(0.1), Inches(1.65), Inches(0.28), fill=color)
        T(s, tier,  Inches(0.58), y + Inches(0.1),  Inches(1.61), Inches(0.26), sz=8,  bold=True, c=W, a=PP_ALIGN.CENTER)
        T(s, title, Inches(2.4),  y + Inches(0.1),  Inches(10.28), Inches(0.4), sz=15, bold=True, c=W)
        T(s, desc,  Inches(2.4),  y + Inches(0.58), Inches(10.28), Inches(0.7), sz=11, c=GR)

    R(s, Inches(0.4), Inches(6.48), Inches(12.5), Inches(0.56), fill=RGBColor(0x0A, 0x2A, 0x18))
    T(s, "Every session: team knowledge grows.  Every fix: the next one is faster.  The system gets smarter, not staler.",
      Inches(0.6), Inches(6.58), Inches(12.1), Inches(0.38),
      sz=14, bold=True, c=G, a=PP_ALIGN.CENTER)




def s13_numbers(p):
    s = blank(p)
    hdr(s, "The Results  —  Numbers the Team Has Measured")

    # All numbers confirmed directly by engineer
    big4 = [
        ("8–12×",  "overall productivity\nfor DE tasks",          G),
        ("2–6h",   "dev ticket\nvs 2–3 days before",              GB),
        ("0–20m",  "Alert issue diagnosis\nvs 1–10 hours before",    BLU),
        ("25+ SP", "sprint capacity\n+ adhoc on top",             GD),
    ]
    for i, (num, label, c_) in enumerate(big4):
        x = Inches(0.4 + i * 3.22)
        card(s, x, Inches(0.82), Inches(3.06), Inches(3.52))
        top_bar(s, x, Inches(0.82), Inches(3.06), color=c_)
        T(s, num,   x, Inches(1.04), Inches(3.06), Inches(1.42), sz=76, bold=True, c=c_, a=PP_ALIGN.CENTER)
        T(s, label, x + Inches(0.15), Inches(2.52), Inches(2.76), Inches(0.78), sz=13, c=GR, a=PP_ALIGN.CENTER)

    # Secondary stats
    R(s, Inches(0.4), Inches(4.52), Inches(12.5), Inches(1.32), fill=LG, ln=MG, lw=Pt(0.75))
    T(s, "More measurements", Inches(0.6), Inches(4.62), Inches(12.1), Inches(0.32), sz=11, bold=True, c=GR)
    # Secondary stats — all engineer-confirmed
    secondary = [
        ("5–15 min",           "context reset after absence\n(vs hours/days before)"),
        ("3–5h",               "new pipeline (full cycle)\nvs 2–4 days before"),
        ("4–6h → 20m–1h",     "spec & plan phase"),
        ("2–4d → 1–2d",       "architecture + CDD\n+ Confluence"),
    ]
    for i, (val, label) in enumerate(secondary):
        x = Inches(0.6 + i * 3.15)
        T(s, val,   x, Inches(5.02), Inches(3.0), Inches(0.44), sz=16, bold=True, c=G)
        T(s, label, x, Inches(5.48), Inches(3.0), Inches(0.28), sz=10, c=GR)

    R(s, Inches(0.4), Inches(6.0), Inches(12.5), Inches(0.6), fill=G)
    T(s, "8–12× overall for DE tasks  ·  All metrics reported directly by Ingestion Team engineers",
      Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.42),
      sz=15, bold=True, c=W, a=PP_ALIGN.CENTER)
    ftr(s)


def s14_comparison(p):
    s = blank(p)
    hdr(s, "Before & After  —  Ingestion Team  ·  3 Repos  ·  3 Months")

    cols = ["What We Measured",       "Before",                                "After (AI-Led)"]
    cxs  = [Inches(0.4),              Inches(4.2),                             Inches(8.15)]
    cws  = [Inches(3.65),             Inches(3.7),                             Inches(4.9)]

    for j, (h, x, w) in enumerate(zip(cols, cxs, cws)):
        R(s, x, Inches(0.82), w, Inches(0.42),
          fill=(G if j == 2 else CHR if j == 1 else LG))
        T(s, h, x + Inches(0.12), Inches(0.9), w - Inches(0.24), Inches(0.3),
          sz=12, bold=True, c=W if j < 2 else W, a=PP_ALIGN.CENTER)

    # ✅ = confirmed directly by engineer   est. = reasonable estimate, not measured
    data = [
        ("Spec & Plan",               "4–6 hours",                "20 min – 1 hour  ✅"),
        ("Architecture + CDD",        "2–4 days",                 "1–2 days  ✅"),
        ("Development ticket",        "2–3 days",                 "2–6 hours (task-dependent)  ✅"),
        ("New pipeline (full cycle)", "2–4 days",                 "3–5 hours  ✅"),
        ("Alert issue diagnosis",      "30 min – 3 hours",         "0–20 minutes (NR MCP)  ✅"),
        ("Context after absence",     "Hours / days",             "5–15 min via /bootstrap  ✅"),
        ("Sprint throughput",         "25 SP (at capacity)",      "25 SP + additional + adhoc  ✅"),
        ("Documentation effort",      "Manual, often skipped",    "Automatic via /wrap-up  ✅"),
        ("Code review layers",        "Manual review only",       "CC Opus + Copilot + Natasha + Human  ✅"),
    ]

    y = Inches(1.32)
    for i, (metric, before, after) in enumerate(data):
        fill = LG if i % 2 == 0 else W
        for j, (val, x, w) in enumerate(zip([metric, before, after], cxs, cws)):
            R(s, x, y, w, Inches(0.5), fill=fill)
            c_ = BK if j == 0 else (GR if j == 1 else GD)
            T(s, val, x + Inches(0.12), y + Inches(0.07), w - Inches(0.24), Inches(0.38),
              sz=10.5, bold=(j == 0 or j == 2), c=c_)
        y += Inches(0.5)

    R(s, Inches(0.4), y + Inches(0.06), Inches(12.6), Inches(0.36), fill=W, ln=MG, lw=Pt(0.75))
    T(s, "✅ = confirmed by Ingestion Team engineers  ·  Repos: om-airflow-dags  ·  spark-kafka-apps  ·  tf-dataos-new-relic",
      Inches(0.6), y + Inches(0.12), Inches(12.2), Inches(0.28), sz=10, c=GR, a=PP_ALIGN.CENTER)
    ftr(s)


def s15_control(p):
    s = blank(p)
    hdr(s, "AI Does the Work.  Humans Stay in Control.  Always.")

    gates = [
        ("1", "Requirements",     "Human writes the spec — AI reads it, asks clarifying questions"),
        ("2", "Architecture",     "Human approves the implementation plan — before a line is written"),
        ("3", "Security Review",  "AI flags every security vulnerability — any critical issue blocks the pipeline"),
        ("4", "PR Merge",         "Human reviews every PR — agent output treated like any other code"),
        ("5", "Deploy",           "Human initiates the deploy — AI writes release notes + monitors"),
    ]
    y = Inches(0.82)
    for num, title, detail in gates:
        is3 = num == "3"
        h = Inches(1.0)
        R(s, Inches(0.4), y, Inches(12.5), h,
          fill=(RGBColor(0xF0, 0xFB, 0xF5) if is3 else W),
          ln=(G if is3 else MG), lw=Pt(1.5 if is3 else 0.75))
        R(s, Inches(0.4), y, Inches(0.54), h, fill=G if is3 else CHR)
        T(s, num,    Inches(0.4),   y + Inches(0.27), Inches(0.54), Inches(0.46),
          sz=18, bold=True, c=W, a=PP_ALIGN.CENTER)
        T(s, title,  Inches(1.1),   y + Inches(0.12), Inches(3.8), Inches(0.42), sz=15, bold=True)
        T(s, detail, Inches(5.06),  y + Inches(0.2),  Inches(7.7), Inches(0.6),  sz=13, c=GR)
        y += h + Inches(0.1)

    R(s, Inches(0.4), y + Inches(0.06), Inches(12.5), Inches(0.38), fill=LG, ln=MG)
    T(s, "Agent PRs treated identically to human PRs — same review, same standards, same gates.",
      Inches(0.6), y + Inches(0.12), Inches(12.1), Inches(0.28), sz=11, it=True, c=GR, a=PP_ALIGN.CENTER)
    ftr(s)


def s16_start(p):
    s = blank(p)
    hdr(s, "Getting Started  —  From Zero to Productive in 4 Steps")

    steps = [
        ("15 MIN",  "Install & Setup",       "One-time per engineer",
         "Claude Code + MCP servers + Budget dial\nMulti-orchestration + hooks + 20 skills\nFully automated — one script.", G),
        ("5 MIN",   "Bootstrap New Repo",    "First visit to any repo",
         "Detects your stack, seeds team memory,\nbuilds codebase graph, wires all MCPs.\nRuns once — context ready forever.", GD),
        ("ALWAYS",  "AI-Led Development",    "Single agent or multi agent",
         "Single task: Claude Code works alongside you.\nComplex task: /avengers spawns parallel agents.\nCopilot handles lines. Claude handles investigations.", G),
        ("30 SEC",  "Wrap-Up",              "Every session end",
         "Jira auto-updated · lessons captured\nKnowledge persisted · graph refreshed.\nThe habit that makes everything compound.", GD),
    ]
    for i, (time, cmd, when, desc, color) in enumerate(steps):
        x = Inches(0.4 + i * 3.22)
        card(s, x, Inches(0.82), Inches(3.06), Inches(4.7))
        R(s, x, Inches(0.82), Inches(3.06), Inches(0.72), fill=color)
        T(s, time, x + Inches(0.1), Inches(0.9),  Inches(2.86), Inches(0.54), sz=18, bold=True, c=W, a=PP_ALIGN.CENTER)
        T(s, f"Step {i+1}  —  {cmd}", x + Inches(0.14), Inches(1.68), Inches(2.78), Inches(0.44), sz=13, bold=True, c=color)
        T(s, when,  x + Inches(0.14), Inches(2.18), Inches(2.78), Inches(0.32), sz=10, it=True, c=GR)
        T(s, desc,  x + Inches(0.14), Inches(2.56), Inches(2.78), Inches(1.82), sz=10.5, c=BK)

    # The Compounding Effect
    HL(s, Inches(0.4), Inches(5.7), Inches(12.5), G)
    T(s, "The Compounding Effect", Inches(0.4), Inches(5.8), Inches(3.5), Inches(0.3),
      sz=11, bold=True, c=G)
    stages = [
        ("Day 1",    "Full codebase context ready.\nDevelopment tickets: days → hours."),
        ("Month 1",  "Lessons accumulate. Patterns reused.\nAlert diagnosis: hours → 0–20 min."),
        ("Month 3+", "Knowledge never leaves the team.\n8–12× productivity — sustained."),
    ]
    for i, (stage, desc) in enumerate(stages):
        x = Inches(0.4 + i * 4.3)
        R(s, x, Inches(6.16), Inches(4.06), Inches(1.0),
          fill=(G if i == 2 else RGBColor(0xD0,0xF0,0xE2) if i == 1 else LG),
          ln=(G if i > 0 else MG), lw=Pt(1))
        T(s, stage, x + Inches(0.18), Inches(6.24), Inches(3.7), Inches(0.3),
          sz=12, bold=True, c=(W if i == 2 else GD))
        T(s, desc,  x + Inches(0.18), Inches(6.58), Inches(3.7), Inches(0.5),
          sz=10.5, c=(W if i == 2 else BK))
    ftr(s)


def s17_ask(p):
    s = blank(p)
    R(s, 0, 0, SW, SH, fill=NVY)
    R(s, 0, 0, SW, Inches(0.06), fill=G)
    R(s, Inches(10.2), 0, Inches(3.13), SH, fill=RGBColor(0x12, 0x12, 0x30))

    if os.path.exists(NR_LOGO):
        # On dark background use the same logo — white bg is transparent enough
        s.shapes.add_picture(NR_LOGO, Inches(0.6), Inches(0.26), width=Inches(2.0))
    T(s, "What We're Asking",
      Inches(0.6), Inches(0.98), Inches(9.3), Inches(0.66), sz=34, bold=True, c=W)
    HL(s, Inches(0.6), Inches(1.7), Inches(8.0), G)

    asks = [
        ("Support adoption",  "Drive AI-led workflows across all Data Engineering & Management in DTM."),
        ("Allocate time",     "Support the daily wrap-up habit — 30 seconds per session. Knowledge compounds automatically."),
        ("Endorse the model", "Establish this as the standard template for all DE teams at New Relic."),
    ]
    for i, (label, detail) in enumerate(asks):
        y = Inches(2.0 + i * 1.18)
        R(s, Inches(0.6), y, Inches(9.38), Inches(1.02), fill=RGBColor(0x14, 0x14, 0x38), ln=G, lw=Pt(0.75))
        R(s, Inches(0.6), y, Inches(0.07), Inches(1.02), fill=G)
        T(s, label,  Inches(0.84), y + Inches(0.08), Inches(2.5),  Inches(0.4), sz=16, bold=True, c=G)
        T(s, detail, Inches(3.45), y + Inches(0.14), Inches(6.38), Inches(0.72), sz=14, c=W)

    # Right panel — 4 distinct verified metrics only
    for i, (val, lbl) in enumerate([
        ("8–12×",  "Productivity"),
        ("2–6h",   "Dev ticket"),
        ("0–20m",  "Alert diagnosis"),
        ("25+ SP", "Sprint capacity"),
    ]):
        T(s, val, Inches(10.2), Inches(1.5 + i * 1.3), Inches(3.13), Inches(0.72), sz=28, bold=True, c=G, a=PP_ALIGN.CENTER)
        T(s, lbl, Inches(10.2), Inches(2.18 + i * 1.3), Inches(3.13), Inches(0.3), sz=10, it=True, c=GR, a=PP_ALIGN.CENTER)

    T(s, "Thank You  ·  Questions?",
      Inches(0.6), Inches(5.78), Inches(9.3), Inches(0.65), sz=28, c=GR)
    T(s, "Repo: github.com/nr-mdakilahmed/claude_code_setup",
      Inches(0.6), Inches(6.5), Inches(9.3), Inches(0.38), sz=12, it=True, c=RGBColor(0x44, 0x44, 0x66))


# ══════════════════════════════════════════════════════════════════════════════

SLIDES = [
    # Act 1 — Story: Challenge
    s01_title,
    s02_problem,
    # Act 2 — Our approach
    s03_how_we_work,       # DataOS Ingestion: how we work now
    s03b_two_tools,        # Copilot + Claude Code: two tools, different jobs
    s04_architecture,      # System architecture diagram
    # Act 3 — The lifecycle
    s05_lifecycle,         # Full lifecycle with verified timings
    # Act 4 — Benefits (capabilities in action)
    s06_faster_dev,        # Faster development — 2-3 days → 2-6 hours
    s07_parallel,          # /avengers parallel build
    s08_investigate,       # NR MCP diagnosis
    s09_ship,              # Impact analysis
    s10_document,          # Auto-documentation
    s11_compounds,         # Knowledge compounds
    # Act 5 — Proof
    s13_numbers,           # Real metrics
    s14_comparison,        # Before & after
    # Act 6 — Governance + Getting started + Ask
    s15_control,           # AI works, humans in control
    s16_start,             # Getting started
    s17_ask,               # What we're asking
]

OUT_PPTX = os.path.join(DIR, "Ingestion-Team-AI-Led-Demo.pptx")
OUT_PDF  = os.path.join(DIR, "Ingestion-Team-AI-Led-Demo.pdf")

def make_pdf_from_pngs():
    """Build PDF from slide PNGs — correct landscape orientation (soffice rotates)."""
    from PIL import Image as PILImage
    png_dir = os.path.join(DIR, "ingestion_ai")
    slides = sorted([
        os.path.join(png_dir, f)
        for f in os.listdir(png_dir)
        if f.startswith("slide_") and f.endswith(".png")
    ]) if os.path.isdir(png_dir) else []

    if not slides:
        return False
    imgs = [PILImage.open(p).convert("RGB") for p in slides]
    imgs[0].save(OUT_PDF, save_all=True, append_images=imgs[1:], format="PDF", resolution=150)
    return True


def main():
    pr = prs()
    for fn in SLIDES:
        fn(pr)
    pr.save(OUT_PPTX)
    print(f"✓  {len(pr.slides)} slides  →  {OUT_PPTX}")

    # Export PNG slides first, then build PDF from them (correct landscape orientation)
    from pdf2image import convert_from_path
    import tempfile
    soffice = "/opt/homebrew/bin/soffice"
    if os.path.exists(soffice):
        # Convert PPTX → PDF via soffice just to get intermediate, then re-export via PIL
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                                "--outdir", tmp, OUT_PPTX], capture_output=True, text=True)
            if r.returncode == 0:
                tmp_pdf = os.path.join(tmp, "Ingestion-Team-AI-Led-Demo.pdf")
                pages = convert_from_path(tmp_pdf, dpi=150)
                pages[0].save(OUT_PDF, save_all=True, append_images=pages[1:],
                              format="PDF", resolution=150)
                print(f"✓  PDF  →  {OUT_PDF}")
            else:
                print(f"⚠  PDF: {r.stderr.strip()}")
    elif make_pdf_from_pngs():
        print(f"✓  PDF  →  {OUT_PDF}")

if __name__ == "__main__":
    main()
