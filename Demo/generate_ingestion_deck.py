#!/usr/bin/env python3
"""
generate_ingestion_deck.py

Creates: Ingestion-Team-AI-Led-Demo.pptx (16 slides, NR green/white branding)

Usage:
    python3 generate_ingestion_deck.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# ── NR Brand Colors ──────────────────────────────────────────────────────────
NR_GREEN     = RGBColor(0x00, 0xAC, 0x69)   # header green
NR_GREEN_LT  = RGBColor(0xE8, 0xF8, 0xF1)   # light green box
NR_GREEN_DARK= RGBColor(0x00, 0x8A, 0x52)   # darker accent
NR_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
NR_BLACK     = RGBColor(0x1A, 0x1A, 0x2E)
NR_GRAY      = RGBColor(0x66, 0x66, 0x66)
NR_LIGHT_GRAY= RGBColor(0xF5, 0xF5, 0xF5)
NR_LINE      = RGBColor(0xDD, 0xDD, 0xDD)
NR_DARK_BOX  = RGBColor(0x1A, 0x1A, 0x2E)
NR_RED       = RGBColor(0xCC, 0x00, 0x00)
ATLASSIAN    = RGBColor(0x00, 0x52, 0xCC)
PURPLE       = RGBColor(0x8B, 0x5C, 0xF6)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)
FOOTER  = "© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution."


# ── Primitives ───────────────────────────────────────────────────────────────

def prs_new():
    p = Presentation()
    p.slide_width  = SLIDE_W
    p.slide_height = SLIDE_H
    return p


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, x, y, w, h, fill=None, line=None, lw=Pt(1)):
    s = slide.shapes.add_shape(1, x, y, w, h)
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = line; s.line.width = lw
    else:
        s.line.fill.background()
    return s


def txt(slide, text, x, y, w, h, size=14, bold=False, color=NR_BLACK,
        align=PP_ALIGN.LEFT, wrap=True, italic=False):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name   = "Calibri"
    return tb


def footer(slide):
    txt(slide, FOOTER,
        Inches(0.3), Inches(7.05), Inches(11.8), Inches(0.38),
        size=7, color=NR_GRAY)
    txt(slide, "⬢ new relic",
        Inches(11.5), Inches(7.0), Inches(1.6), Inches(0.42),
        size=10, bold=True, color=NR_GREEN, align=PP_ALIGN.RIGHT)


def green_header(slide, title, h=Inches(0.72)):
    rect(slide, Inches(0), Inches(0), SLIDE_W, h, fill=NR_GREEN)
    txt(slide, title,
        Inches(0.4), Inches(0.08), Inches(12.5), h - Inches(0.1),
        size=26, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)


def light_box(slide, x, y, w, h, title=None, bullets=None, title_color=NR_BLACK):
    rect(slide, x, y, w, h, fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    cy = y + Inches(0.14)
    if title:
        txt(slide, title, x+Inches(0.14), cy, w-Inches(0.28), Inches(0.38),
            size=13, bold=True, color=title_color)
        cy += Inches(0.38)
    if bullets:
        for b in bullets:
            txt(slide, f"• {b}", x+Inches(0.14), cy, w-Inches(0.28), Inches(0.3),
                size=11, color=NR_BLACK)
            cy += Inches(0.3)


def dark_box(slide, x, y, w, h, title, subtitle=None):
    rect(slide, x, y, w, h, fill=NR_DARK_BOX)
    cy = y + Inches(0.15)
    txt(slide, title, x+Inches(0.15), cy, w-Inches(0.3), Inches(0.4),
        size=14, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
    if subtitle:
        txt(slide, subtitle, x+Inches(0.15), cy+Inches(0.4), w-Inches(0.3), Inches(0.32),
            size=11, color=NR_GREEN, align=PP_ALIGN.CENTER)


def hline(slide, x, y, w):
    rect(slide, x, y, w, Inches(0.018), fill=NR_LINE)


# ── Slide 01 — Title ─────────────────────────────────────────────────────────

def s01_title(prs):
    slide = blank(prs)
    rect(slide, Inches(8.4), Inches(0), Inches(4.93), Inches(3.6), fill=NR_GREEN_LT)
    txt(slide, "⬢ new relic",
        Inches(0.4), Inches(0.3), Inches(3.0), Inches(0.5),
        size=22, bold=True, color=NR_GREEN)
    txt(slide, "Ingestion Team\nAI-Led Development\nEnvironment",
        Inches(0.4), Inches(1.6), Inches(7.6), Inches(2.6),
        size=38, bold=True, color=NR_BLACK)
    txt(slide, "Shipping more · Debugging faster · Onboarding in hours",
        Inches(0.4), Inches(4.4), Inches(7.6), Inches(0.55),
        size=16, italic=True, color=NR_GRAY)
    footer(slide)


# ── Slide 02 — Agenda ────────────────────────────────────────────────────────

def s02_agenda(prs):
    slide = blank(prs)
    txt(slide, "Agenda",
        Inches(0.5), Inches(0.25), Inches(10), Inches(0.6),
        size=34, color=NR_BLACK)
    hline(slide, Inches(0.5), Inches(0.9), Inches(12.3))
    items = [
        ("01", "The Problem We Were Solving"),
        ("02", "Our AI-Led Development Environment"),
        ("03", "Capabilities in Action — NR MCP · Graph · /avengers · Memory"),
        ("04", "Before & After Metrics"),
        ("05", "Known Risks & How We Mitigate"),
        ("06", "What's Next"),
    ]
    y = Inches(1.05)
    for num, label in items:
        txt(slide, num, Inches(0.5), y, Inches(0.7), Inches(0.48), size=22, color=NR_GREEN)
        txt(slide, label, Inches(1.35), y+Inches(0.06), Inches(11.0), Inches(0.44), size=17, color=NR_BLACK)
        hline(slide, Inches(0.5), y+Inches(0.5), Inches(12.3))
        y += Inches(0.83)
    footer(slide)


# ── Slide 03 — SDLC vs AI-DLC ────────────────────────────────────────────────

def s03_sdlc(prs):
    slide = blank(prs)
    green_header(slide, "SDLC vs. AI-DLC")
    txt(slide, "Standard SDLC (Manual)",
        Inches(0.5), Inches(0.85), Inches(5.7), Inches(0.42),
        size=16, bold=True, align=PP_ALIGN.CENTER)
    txt(slide, "AI-DLC (Ingestion Team)",
        Inches(7.1), Inches(0.85), Inches(5.8), Inches(0.42),
        size=16, bold=True, align=PP_ALIGN.CENTER)
    rows = [
        ("Requirements & Analysis",    "Manual stakeholder docs, Jira spelunking",
         "Intake & Spec Agent",         "Reads existing patterns, writes spec in minutes"),
        ("Architecture & Design",       "Manual planning & diagrams",
         "Planner & Architect Agent",   "Codebase research → implementation plan via CRG"),
        ("Code Development",            "Human engineers writing line-by-line",
         "Implementation Agent",        "AI writes production code against specs"),
        ("QA & Security Review",        "Manual testing & periodic audits",
         "Verification & Security",     "Continuous automated tests + OWASP on every PR"),
        ("Deployment & Release Notes",  "Manual deployment & docs",
         "Deploy & Release Agent",      "Auto-generates release notes → Confluence"),
    ]
    y = Inches(1.38)
    for lt, ls, rt, rs in rows:
        rect(slide, Inches(0.4), y, Inches(5.9), Inches(0.9), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
        txt(slide, lt, Inches(0.55), y+Inches(0.06), Inches(5.5), Inches(0.32), size=12, bold=True)
        txt(slide, ls, Inches(0.55), y+Inches(0.4),  Inches(5.5), Inches(0.42), size=10, color=NR_GRAY)
        rect(slide, Inches(7.0), y, Inches(5.9), Inches(0.9), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
        txt(slide, rt, Inches(7.15), y+Inches(0.06), Inches(5.5), Inches(0.32), size=12, bold=True)
        txt(slide, rs, Inches(7.15), y+Inches(0.4),  Inches(5.5), Inches(0.42), size=10, color=NR_BLACK)
        y += Inches(1.04)
    footer(slide)


# ── Slide 04 — Four Pains ────────────────────────────────────────────────────

def s04_pains(prs):
    slide = blank(prs)
    green_header(slide, "The Four Pains We Were Living With")
    pains = [
        ("🕐  Onboarding: 2+ Weeks",
         "New engineers spent weeks reading docs, asking Slack, and re-deriving patterns from git history. Context lived in people's heads, not the codebase."),
        ("🔍  Prod Incident: Hours to Diagnose",
         "Something broke — the team hunted through NR logs manually. No structured entry point, no context about which components were affected, no blast radius."),
        ("💥  Blast Radius Unknown",
         "'1-day fix' became a 5-day incident because no one knew what else would break. Changes were made blind — we found out in prod."),
        ("🗂  Architecture Lives in Heads",
         "Knowledge lived in Slack threads and in the senior engineer's memory. Every time someone switched teams or took PTO, context was lost."),
    ]
    positions = [
        (Inches(0.4),  Inches(0.9)),
        (Inches(6.95), Inches(0.9)),
        (Inches(0.4),  Inches(3.85)),
        (Inches(6.95), Inches(3.85)),
    ]
    for (title, desc), (x, y) in zip(pains, positions):
        rect(slide, x, y, Inches(6.15), Inches(2.65), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
        txt(slide, title, x+Inches(0.2), y+Inches(0.15), Inches(5.75), Inches(0.42), size=14, bold=True)
        txt(slide, desc,  x+Inches(0.2), y+Inches(0.65), Inches(5.75), Inches(1.8),  size=12, color=NR_GRAY)
    footer(slide)


# ── Slide 05 — Environment Architecture ─────────────────────────────────────

def s05_arch(prs):
    slide = blank(prs)
    green_header(slide, "Ingestion Team: AI-Led Environment Architecture")
    dark_box(slide, Inches(4.3), Inches(0.85), Inches(4.7), Inches(0.9),
             "Claude Code + /avengers (Opus Orchestrator)",
             "Routes work · validates gates · runs investigations")
    # Top row: integrations
    top = [
        ("Memory & Context\n(hot.md + lessons.md)", "Compounds every session"),
        ("NR MCP\n(12 tools)", "Logs · metrics · alerts · traces"),
        ("Code Graph\n(CRG, 28 tools)", "Tree-sitter AST · blast radius"),
        ("Jira + Confluence\nMCP", "Auto-updates tickets & docs"),
    ]
    xs = [Inches(0.3), Inches(3.6), Inches(6.9), Inches(10.2)]
    for i, (t, s) in enumerate(top):
        rect(slide, xs[i], Inches(2.1), Inches(3.0), Inches(1.3), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
        txt(slide, t, xs[i]+Inches(0.1), Inches(2.2),  Inches(2.8), Inches(0.55), size=12, bold=True)
        txt(slide, s, xs[i]+Inches(0.1), Inches(2.78), Inches(2.8), Inches(0.5),  size=10, color=NR_GRAY)
    # Bottom row: /avengers specialists
    bots = [
        ("Planner\n(Architecture)", "Codebase research → plan"),
        ("Coder × N\n(Sonnet, parallel)", "Writes code · verifies build"),
        ("Reviewer\n(Black Widow)", "Code + security standards"),
        ("Validator\n(Hawkeye)", "Tests + blast radius gate"),
    ]
    for i, (t, s) in enumerate(bots):
        rect(slide, xs[i], Inches(3.75), Inches(3.0), Inches(1.3), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
        txt(slide, t, xs[i]+Inches(0.1), Inches(3.85), Inches(2.8), Inches(0.55), size=12, bold=True)
        txt(slide, s, xs[i]+Inches(0.1), Inches(4.43), Inches(2.8), Inches(0.5),  size=10, color=NR_GRAY)
    # Skills bar
    rect(slide, Inches(0.3), Inches(5.35), Inches(12.7), Inches(0.45), fill=NR_LIGHT_GRAY)
    txt(slide, "Skills (auto-trigger):  /airflow  /pyspark  /sql  /nrql  /nralert  /terraform  |  Explicit:  /bootstrap  /wrap-up  /golden  /replay  /avengers  /budget",
        Inches(0.5), Inches(5.42), Inches(12.3), Inches(0.35),
        size=10, color=NR_GRAY, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 06 — MCP Layer ─────────────────────────────────────────────────────

def s06_mcp(prs):
    slide = blank(prs)
    green_header(slide, "The MCP Integration Layer — Real Data, In Real Time")
    pillars = [
        ("NR Observability",    NR_GREEN,    "30-second incident diagnosis",
         ["analyze_kafka_metrics", "analyze_entity_logs", "analyze_golden_metrics",
          "list_recent_issues", "get_distributed_trace_details", "execute_nrql_query",
          "analyze_transactions"]),
        ("Jira + Confluence",   ATLASSIAN,   "Zero copy-paste ticket updates",
         ["getJiraIssue / editJiraIssue", "addCommentToJiraIssue", "transitionJiraIssue",
          "createConfluencePage", "updateConfluencePage", "searchConfluenceUsingCql"]),
        ("Code Graph (CRG)",    PURPLE,      "Blast radius before you code",
         ["semantic_search_nodes", "get_impact_radius", "detect_changes",
          "query_graph (callers / callees)", "get_affected_flows", "refactor_tool",
          "get_architecture_overview"]),
    ]
    for i, (title, color, tagline, tools) in enumerate(pillars):
        x = Inches(0.4 + i * 4.3)
        rect(slide, x, Inches(0.82), Inches(4.0), Inches(0.58), fill=color)
        txt(slide, title, x+Inches(0.1), Inches(0.88), Inches(3.8), Inches(0.46),
            size=15, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        y_t = Inches(1.55)
        for tool in tools:
            txt(slide, f"• {tool}", x+Inches(0.1), y_t, Inches(3.8), Inches(0.32), size=11)
            y_t += Inches(0.33)
        rect(slide, x, Inches(5.65), Inches(4.0), Inches(0.55), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
        txt(slide, tagline, x+Inches(0.1), Inches(5.72), Inches(3.8), Inches(0.42),
            size=12, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 07 — NR MCP: 3h → 30min ───────────────────────────────────────────

def s07_nr_demo(prs):
    slide = blank(prs)
    green_header(slide, "NR MCP: From 3 Hours to 30 Minutes")
    rect(slide, Inches(0.4), Inches(0.9), Inches(5.85), Inches(5.3), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "BEFORE", Inches(0.6), Inches(0.98), Inches(2), Inches(0.32), size=11, bold=True, color=NR_GRAY)
    txt(slide, "Manual NR UI Hunting", Inches(0.6), Inches(1.32), Inches(5.5), Inches(0.4), size=17, bold=True)
    before = [
        "1. Alert fires at 2am",
        "2. Log in to NR → navigate to entity",
        "3. Scroll through logs manually",
        "4. Switch to metrics tab → compare charts",
        "5. Check traces → click through spans",
        "6. Slack teammates for codebase context",
        "7. Form hypothesis → test → iterate",
        "",
        "⏱  Average: 2–3 hours to root cause",
    ]
    y = Inches(1.82)
    for s in before:
        c = NR_RED if s.startswith("⏱") else NR_BLACK
        b = s.startswith("⏱")
        txt(slide, s, Inches(0.6), y, Inches(5.5), Inches(0.3), size=11, color=c, bold=b)
        y += Inches(0.33)
    txt(slide, "→", Inches(6.35), Inches(3.3), Inches(0.6), Inches(0.5),
        size=34, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    rect(slide, Inches(7.05), Inches(0.9), Inches(5.85), Inches(5.3), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1.5))
    txt(slide, "AFTER", Inches(7.25), Inches(0.98), Inches(2), Inches(0.32), size=11, bold=True, color=NR_GREEN)
    txt(slide, "Claude Code + NR MCP", Inches(7.25), Inches(1.32), Inches(5.5), Inches(0.4), size=17, bold=True)
    after = [
        "1. Alert fires at 2am",
        '2. "analyze kafka consumer lag last 4h"',
        "   → analyze_kafka_metrics → structured output",
        "   → consumer lag, partitions, throughput in 30s",
        "3. get_impact_radius → affected DAGs shown",
        "4. Hypothesis formed. Fix scoped instantly.",
        "5. Jira ticket updated via MCP.",
        "",
        "⏱  Average: 20–30 minutes to root cause",
    ]
    y = Inches(1.82)
    for s in after:
        c = NR_GREEN if s.startswith("⏱") else NR_BLACK
        b = s.startswith("⏱")
        txt(slide, s, Inches(7.25), y, Inches(5.5), Inches(0.3), size=11, color=c, bold=b)
        y += Inches(0.33)
    footer(slide)


# ── Slide 08 — Blast Radius ──────────────────────────────────────────────────

def s08_blast(prs):
    slide = blank(prs)
    green_header(slide, "Know the Blast Radius Before Writing a Line")
    steps = [
        ("You make a\nchange",           NR_WHITE,    NR_LINE),
        ("get_impact_\nradius()",        NR_GREEN,    NR_GREEN),
        ("Callers · Callees\nFlows",     NR_GREEN_LT, NR_GREEN),
        ("Safe to\ncommit ✓",            NR_GREEN_LT, NR_GREEN),
    ]
    for i, (label, fill, line) in enumerate(steps):
        x = Inches(0.9 + i * 3.1)
        rect(slide, x, Inches(1.7), Inches(2.6), Inches(1.7), fill=fill, line=line, lw=Pt(1.5))
        txt(slide, label, x+Inches(0.1), Inches(2.2), Inches(2.4), Inches(1.1),
            size=14, bold=(fill != NR_WHITE),
            color=(NR_WHITE if fill == NR_GREEN else NR_BLACK), align=PP_ALIGN.CENTER)
        if i < 3:
            txt(slide, "→", Inches(3.55 + i * 3.1), Inches(2.4), Inches(0.5), Inches(0.5),
                size=26, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    rect(slide, Inches(0.4), Inches(3.75), Inches(5.9), Inches(1.8), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "Before: No visibility", Inches(0.6), Inches(3.85), Inches(5.5), Inches(0.35), size=13, bold=True)
    txt(slide, "Engineer changes a DAG file. Deploys to staging.\nDownstream Kafka consumer breaks silently.\n5-day incident to trace back to root cause.",
        Inches(0.6), Inches(4.25), Inches(5.5), Inches(1.2), size=11, color=NR_GRAY)
    rect(slide, Inches(7.0), Inches(3.75), Inches(5.9), Inches(1.8), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    txt(slide, "After: Instant clarity", Inches(7.2), Inches(3.85), Inches(5.5), Inches(0.35), size=13, bold=True)
    txt(slide, "Engineer runs get_impact_radius before touching code.\nSees 3 callers, 1 downstream Kafka consumer.\nFixes scope. Ships confidently. No incident.",
        Inches(7.2), Inches(4.25), Inches(5.5), Inches(1.2), size=11, color=NR_BLACK)
    footer(slide)


# ── Slide 09 — /avengers ─────────────────────────────────────────────────────

def s09_avengers(prs):
    slide = blank(prs)
    green_header(slide, "/avengers — Multi-Agent Orchestration for Complex Work")
    dark_box(slide, Inches(4.3), Inches(0.85), Inches(4.7), Inches(0.9),
             "Nick Fury — Opus (Orchestrator)",
             "Routes work · validates gates · blocks bad code")
    specs = [
        ("Planner\n(Architecture)", "Codebase research\n→ impl. plan"),
        ("Coder × N\n(Sonnet, parallel)", "Writes code per plan\nverifies build"),
        ("Reviewer\n(Black Widow)", "Code + security\nstandards"),
        ("Validator\n(Hawkeye)", "Tests + blast radius\nbefore merge"),
    ]
    xs = [Inches(0.3), Inches(3.6), Inches(6.9), Inches(10.2)]
    for i, (t, s) in enumerate(specs):
        rect(slide, xs[i], Inches(2.1), Inches(3.0), Inches(1.6), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
        txt(slide, t, xs[i]+Inches(0.1), Inches(2.2),  Inches(2.8), Inches(0.65), size=12, bold=True)
        txt(slide, s, xs[i]+Inches(0.1), Inches(2.88), Inches(2.8), Inches(0.72), size=10, color=NR_GRAY)
    rect(slide, Inches(0.4), Inches(4.05), Inches(12.5), Inches(2.0), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    txt(slide, "Real example: Multi-file Airflow DAG + dbt model + NR alert — what used to take 1 day",
        Inches(0.6), Inches(4.15), Inches(12.1), Inches(0.38), size=13, bold=True)
    txt(slide, "Fury reads the spec → spawns Planner (researches existing DAGs + graph) + Coder (writes DAG skeleton) in parallel → "
               "Reviewer checks patterns → Validator runs blast radius + tests → Fury merges output → Engineer reviews 1 PR instead of writing 5 files.",
        Inches(0.6), Inches(4.6), Inches(12.1), Inches(1.3), size=11, color=NR_BLACK)
    footer(slide)


# ── Slide 10 — Memory Compounds ──────────────────────────────────────────────

def s10_memory(prs):
    slide = blank(prs)
    green_header(slide, "Memory That Compounds — Every Session Makes the Next One Smarter")
    layers = [
        ("ALWAYS LOADED",  "hot.md  (~2k tokens, auto-loads at session start)",
         "Active todos + recent lessons + architecture summary. /wrap-up regenerates it every session.",
         NR_GREEN, NR_WHITE),
        ("PULL ON DEMAND",
         "lessons.md  ·  architecture.md  ·  history.md  ·  plans/",
         "Patterns, anti-patterns, wins. Architecture from graph. Session history. Retrieved via memory MCP when relevant.",
         NR_GREEN_LT, NR_BLACK),
        ("REPLAYABLE WINS",
         "~/.claude/golden/<slug>.md",
         "/golden save after a validated prod fix.  /replay <slug> next time the same problem recurs — avoids re-deriving the fix.",
         NR_WHITE, NR_BLACK),
    ]
    y = Inches(0.88)
    for tier, title, desc, fill, tc in layers:
        h = Inches(1.6)
        rect(slide, Inches(0.4), y, Inches(12.5), h,
             fill=fill, line=(NR_GREEN if fill != NR_WHITE else NR_LINE), lw=Pt(1))
        txt(slide, tier, Inches(0.6), y+Inches(0.12), Inches(1.8), Inches(0.3),
            size=9, bold=True, color=(NR_WHITE if fill == NR_GREEN else NR_GREEN))
        txt(slide, title, Inches(0.6), y+Inches(0.42), Inches(4.5), Inches(0.4),
            size=14, bold=True, color=tc)
        txt(slide, desc, Inches(5.3), y+Inches(0.22), Inches(7.4), Inches(1.1),
            size=11, color=(NR_WHITE if fill == NR_GREEN else NR_BLACK))
        y += h + Inches(0.12)
    rect(slide, Inches(0.4), Inches(5.7), Inches(12.5), Inches(0.46), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    txt(slide, "Result: Month 1 = 8 blocking issues/task.  Month 3 = 1–2.  The system gets smarter with every session.",
        Inches(0.6), Inches(5.78), Inches(12.1), Inches(0.36),
        size=13, bold=True, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 11 — Metrics ───────────────────────────────────────────────────────

def s11_metrics(prs):
    slide = blank(prs)
    green_header(slide, "Ingestion Team — Before & After")
    cols = ["Metric", "Before (Manual)", "After (AI-Led)"]
    cxs  = [Inches(0.5),  Inches(4.15), Inches(8.1)]
    cws  = [Inches(3.55), Inches(3.75), Inches(4.8)]
    for j, (h, x, w) in enumerate(zip(cols, cxs, cws)):
        txt(slide, h, x, Inches(0.88), w, Inches(0.38),
            size=13, bold=True, color=(NR_GRAY if j == 0 else NR_BLACK), align=PP_ALIGN.CENTER)
    hline(slide, Inches(0.5), Inches(1.24), Inches(12.3))
    rows = [
        ("Engineer onboarding time",   "2+ weeks (Slack + tribal knowledge)",    "Hours — /bootstrap seeds context day 1"),
        ("Incident diagnosis (MTTR)",  "2–3 hours (manual NR UI hunting)",        "20–30 min (NR MCP + structured output)"),
        ("Feature cycle time",         "14–20 days",                              "3–5 days"),
        ("Blast radius visibility",    "Unknown until something breaks",           "Instant — before a line is written"),
        ("Onboarding to new codebase", "Days of grep + git archaeology",           "Minutes — /bootstrap + graph loaded"),
        ("Sprint slippage from rework","~1 sprint/quarter",                        "< 1 day (hidden deps caught pre-commit)"),
        ("Deployment confidence",      "Medium (manual review)",                   "High (automated + blast radius verified)"),
    ]
    y = Inches(1.32)
    for i, (metric, before, after) in enumerate(rows):
        fill = NR_GREEN_LT if i % 2 else NR_WHITE
        rect(slide, Inches(0.5), y, Inches(12.3), Inches(0.54), fill=fill)
        txt(slide, metric, cxs[0], y+Inches(0.07), cws[0], Inches(0.42), size=11, bold=True)
        txt(slide, before, cxs[1], y+Inches(0.07), cws[1], Inches(0.42), size=11, color=NR_GRAY)
        txt(slide, after,  cxs[2], y+Inches(0.07), cws[2], Inches(0.42), size=11, bold=True, color=NR_GREEN)
        y += Inches(0.54)
    rect(slide, Inches(0.5), y+Inches(0.08), Inches(12.3), Inches(0.46), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "Measured across 3 active repos (om-airflow-dags · spark-kafka-apps · tf-dataos-new-relic)  ·  ~3 months of daily use",
        Inches(0.7), y+Inches(0.15), Inches(11.9), Inches(0.32), size=10, bold=True, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 12 — Jira + Confluence ─────────────────────────────────────────────

def s12_jira(prs):
    slide = blank(prs)
    green_header(slide, "Auto-Updated Jira & Confluence — Zero Copy-Paste")
    flow = [
        ("Developer\nmerges PR",     NR_WHITE),
        ("/wrap-up\nfires",          NR_GREEN_LT),
        ("Claude drafts\nsummary",   NR_GREEN_LT),
        ("Jira ticket\nupdated",     NR_GREEN),
        ("Confluence\npublished",    NR_GREEN),
    ]
    for i, (label, fill) in enumerate(flow):
        x = Inches(0.5 + i * 2.56)
        rect(slide, x, Inches(0.9), Inches(2.3), Inches(1.4),
             fill=fill, line=(NR_GREEN if fill != NR_WHITE else NR_LINE), lw=Pt(1.5))
        txt(slide, label, x+Inches(0.1), Inches(1.25), Inches(2.1), Inches(0.85),
            size=12, bold=(fill == NR_GREEN),
            color=(NR_WHITE if fill == NR_GREEN else NR_BLACK), align=PP_ALIGN.CENTER)
        if i < 4:
            txt(slide, "→", Inches(2.9 + i * 2.56), Inches(1.45), Inches(0.4), Inches(0.4),
                size=24, bold=True, color=NR_GREEN, align=PP_ALIGN.CENTER)
    rect(slide, Inches(0.5), Inches(2.65), Inches(5.9), Inches(2.7), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "Jira — Auto-populated", Inches(0.7), Inches(2.75), Inches(5.5), Inches(0.38), size=14, bold=True)
    y = Inches(3.24)
    for b in ["Status → In Review / Done", "Comment: what was done, decisions made",
              "Time logged from session duration", "Linked to commits via branch name"]:
        txt(slide, f"• {b}", Inches(0.7), y, Inches(5.5), Inches(0.3), size=11)
        y += Inches(0.38)
    rect(slide, Inches(7.0), Inches(2.65), Inches(5.9), Inches(2.7), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    txt(slide, "Confluence — Auto-published", Inches(7.2), Inches(2.75), Inches(5.5), Inches(0.38), size=14, bold=True)
    y = Inches(3.24)
    for b in ["Architecture decisions logged automatically",
              "Incident postmortems → page auto-created",
              "Release notes from git history (v2.2 → v2.3)",
              "Categorized by area · files changed listed"]:
        txt(slide, f"• {b}", Inches(7.2), y, Inches(5.5), Inches(0.3), size=11)
        y += Inches(0.38)
    txt(slide, "Zero manual effort.  Every session documented.  Every time.",
        Inches(0.5), Inches(5.55), Inches(12.3), Inches(0.42),
        size=14, bold=True, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 13 — Humans in Control ─────────────────────────────────────────────

def s13_humans(prs):
    slide = blank(prs)
    green_header(slide, "AI Does the Work.  Humans Stay in Control.")
    gates = [
        ("1", "Requirements approval",       "Before planning begins"),
        ("2", "Architecture plan approval",   "Before any code is written"),
        ("3", "Security review sign-off",     "Any critical finding blocks the pipeline"),
        ("4", "Final PR merge",               "Human reviews and approves"),
        ("5", "Production deployments",       "Human initiates · agent creates release notes"),
    ]
    y = Inches(1.0)
    for num, title, detail in gates:
        is3 = (num == "3")
        fill  = NR_GREEN_LT if is3 else NR_WHITE
        border= NR_GREEN    if is3 else NR_LINE
        rect(slide, Inches(0.5), y, Inches(12.3), Inches(0.82),
             fill=fill, line=border, lw=Pt(1.5 if is3 else 1))
        rect(slide, Inches(0.55), y+Inches(0.17), Inches(0.46), Inches(0.46), fill=NR_BLACK)
        txt(slide, num,   Inches(0.55), y+Inches(0.17), Inches(0.46), Inches(0.46),
            size=14, bold=True, color=NR_WHITE, align=PP_ALIGN.CENTER)
        txt(slide, title, Inches(1.15), y+Inches(0.18), Inches(4.6),  Inches(0.4),
            size=14, bold=True)
        txt(slide, "— " + detail, Inches(5.5), y+Inches(0.22), Inches(7.1), Inches(0.38),
            size=13, color=NR_GRAY)
        y += Inches(0.95)
    footer(slide)


# ── Slide 14 — Risks ─────────────────────────────────────────────────────────

def s14_risks(prs):
    slide = blank(prs)
    green_header(slide, "Known Risks & How We Mitigate")
    risks = [
        ("Hallucinations",
         "Validation loops required: blast radius, bash -n, tests. Garbage in = garbage out — same discipline as code review."),
        ("Context Drift",
         "hot.md + lessons.md read at every session start. Context gets sharper every session, not staler."),
        ("Runaway Actions",
         "No auto-push, no auto-merge. 4 human approval gates before production touches."),
        ("Security Blind Spots",
         "Pre-commit hook scans API keys. Security agent runs OWASP Top 10 on every PR."),
        ("Over-Engineering",
         "Skills enforce patterns, not creativity. Reviewer agent blocks unnecessary abstractions."),
        ("Test Coverage Gaps",
         "Negative tests + edge cases required. Build gate: tests must pass. No bypass."),
    ]
    positions = [
        (Inches(0.4), Inches(0.9)),  (Inches(4.65), Inches(0.9)),  (Inches(8.9), Inches(0.9)),
        (Inches(0.4), Inches(3.5)),  (Inches(4.65), Inches(3.5)),  (Inches(8.9), Inches(3.5)),
    ]
    for (title, detail), (x, y) in zip(risks, positions):
        rect(slide, x, y, Inches(3.95), Inches(2.2), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
        txt(slide, title,  x+Inches(0.15), y+Inches(0.12), Inches(3.65), Inches(0.36), size=13, bold=True)
        txt(slide, detail, x+Inches(0.15), y+Inches(0.52), Inches(3.65), Inches(1.5),  size=11, color=NR_GRAY)
    rect(slide, Inches(0.4), Inches(5.86), Inches(12.5), Inches(0.44), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1))
    txt(slide, "Review Burden Shifts: Reviewing agent output still requires engineering expertise — and now engineers have more time to do it.",
        Inches(0.6), Inches(5.93), Inches(12.1), Inches(0.34), size=11, bold=True, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Slide 15 — Where Next ─────────────────────────────────────────────────────

def s15_next(prs):
    slide = blank(prs)
    green_header(slide, "Where We Go From Here")
    rect(slide, Inches(0.4), Inches(0.88), Inches(5.9), Inches(2.55), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "Current Status & Expansion", Inches(0.6), Inches(0.98), Inches(5.5), Inches(0.38), size=15, bold=True)
    y = Inches(1.45)
    for b in ["• Environment live for Ingestion Team",
              "• All 3 active repos bootstrapped",
              "• NR MCP, Jira MCP, CRG fully wired",
              "• Ready to scale to other DE teams"]:
        txt(slide, b, Inches(0.6), y, Inches(5.5), Inches(0.3), size=12)
        y += Inches(0.3)
    rect(slide, Inches(7.0), Inches(0.88), Inches(5.9), Inches(2.55), fill=NR_WHITE, line=NR_LINE, lw=Pt(1))
    txt(slide, "Optimization & Learning", Inches(7.2), Inches(0.98), Inches(5.5), Inches(0.38), size=15, bold=True)
    y = Inches(1.45)
    for b in ["• Weekly grep-fallback telemetry review",
              "• Golden library grows 2–5/week",
              "• Session cost tracked daily in statusline",
              "• lessons.md compounding across all repos"]:
        txt(slide, b, Inches(7.2), y, Inches(5.5), Inches(0.3), size=12)
        y += Inches(0.3)
    rect(slide, Inches(0.4), Inches(3.7), Inches(12.5), Inches(2.9), fill=NR_GREEN_LT, line=NR_GREEN, lw=Pt(1.5))
    txt(slide, "Strategic Ask of Leadership", Inches(0.6), Inches(3.82), Inches(12.1), Inches(0.42), size=16, bold=True)
    asks = [
        ("Support adoption:",   "Drive AI-led workflows across Data Engineering & Management in DTM"),
        ("Allocate time:",       "Empower engineers to improve agent quality — /wrap-up daily, goldens weekly"),
        ("Endorse the model:",   "Establish this pipeline as the template for other DE teams to adopt"),
    ]
    y = Inches(4.38)
    for label, detail in asks:
        txt(slide, f"• {label}", Inches(0.6), y, Inches(2.3), Inches(0.38), size=13, bold=True)
        txt(slide, detail,        Inches(3.0), y, Inches(9.7), Inches(0.38), size=13)
        y += Inches(0.55)
    footer(slide)


# ── Slide 16 — Thank You ──────────────────────────────────────────────────────

def s16_thanks(prs):
    slide = blank(prs)
    txt(slide, "Thank You", Inches(1.5), Inches(2.5), Inches(10.33), Inches(1.5),
        size=60, color=NR_BLACK, align=PP_ALIGN.CENTER)
    txt(slide, "Questions?", Inches(4.0), Inches(4.3), Inches(5.33), Inches(0.7),
        size=26, color=NR_GRAY, align=PP_ALIGN.CENTER)
    footer(slide)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    prs = prs_new()
    s01_title(prs)
    s02_agenda(prs)
    s03_sdlc(prs)
    s04_pains(prs)
    s05_arch(prs)
    s06_mcp(prs)
    s07_nr_demo(prs)
    s08_blast(prs)
    s09_avengers(prs)
    s10_memory(prs)
    s11_metrics(prs)
    s12_jira(prs)
    s13_humans(prs)
    s14_risks(prs)
    s15_next(prs)
    s16_thanks(prs)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "Ingestion-Team-AI-Led-Demo.pptx")
    prs.save(out)
    print(f"✓  {len(prs.slides)} slides saved → {out}")


if __name__ == "__main__":
    main()
