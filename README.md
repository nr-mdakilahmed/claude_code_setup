# CC Team Setup

**AI-led Claude Code environment for Data Engineering teams.** One install gives every teammate the same skills, hooks, model routing, memory layout, MCP servers, and multi-agent capabilities — consistent AI tooling across the whole team, with compounding per-session value.

---

## ⚡ Quickstart — 5 minutes to a fully-wired CC

```bash
# 1 — Prereqs (install what you're missing)
claude --version        # Claude Code — https://docs.claude.com/claude-code
python3 --version       # brew install python3  (3.10+)
git --version           # brew install git
jq --version            # brew install jq         (required)
pipx --version          # brew install pipx && pipx ensurepath
uv --version            # brew install uv         (required for memory-server)
ssh -T git@source.datanerd.us   # optional: NR plugins need this

# 2 — Clone & install
git clone git@github.com:nr-mdakilahmed/claude_code_setup.git ~/claude_code_setup
cd ~/claude_code_setup
./install.sh            # installs skills, hooks, CRG, memory-server, budget, golden

# 3 — Verify
./verify.sh             # end-to-end check of prereqs + skills + hooks + MCP servers

# 4 — Restart Claude Code
#     Plugins auto-install on first start (~30s)
#     Inside CC, confirm:   /plugin list   → 11 active plugins
```

> **First visit to a repo?** `/bootstrap` — seeds memory, installs per-repo CRG + memory MCP, builds graph
> **Every session end?** `/wrap-up` — persists memory, mirrors plans, regenerates hot.md, refreshes graph
> **Complex multi-file task?** `/avengers` — Opus orchestrates parallel specialist subagents
> **After a validated fix?** `/golden save <slug>` — capture reusable session template
> **Hit a familiar problem?** `/replay <slug>` — load a prior-art plan

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│ GLOBAL LAYER (~/.claude/)                                                   │
│                                                                             │
│  CLAUDE.md          ← rules: security, model routing, workflows (@-loaded) │
│  budget.json        ← daily/weekly/monthly spend caps                      │
│  golden/            ← reusable session patterns + index.json               │
│  plans/             ← Anthropic's global plan dir (mirrored per-project)   │
│  telemetry/         ← cost.jsonl + greps.jsonl                             │
│  skills/            ← 20 skills (language/domain + meta workflows)         │
│  hooks/             ← rtk, refresh-mcp-tokens, self-heal, statusline,      │
│                       log-grep-usage, stop-record-cost                     │
└────────────────────────────────────────────────────────────────────────────┘
                                     ↓ /bootstrap
┌────────────────────────────────────────────────────────────────────────────┐
│ PROJECT LAYER (~/.claude/projects/<repo>/)                                  │
│                                                                             │
│  memory/                                                                    │
│    ├── hot.md         ← AUTO-LOADED ~2k tokens (wrap-up regenerates)       │
│    ├── MEMORY.md      ← index (pull-on-demand)                             │
│    ├── architecture.md, todo.md, lessons.md, history.md                    │
│  plans/ ← mirrored from ~/.claude/plans/ at wrap-up                        │
│  graphs/                                                                    │
│    ├── GRAPH_REPORT.md ← AUTO-LOADED ~2k tokens                            │
│    └── graph.html                                                           │
└────────────────────────────────────────────────────────────────────────────┘
                                     ↓ /bootstrap
┌────────────────────────────────────────────────────────────────────────────┐
│ REPO LAYER (<repo>/)                                                        │
│                                                                             │
│  .claude/CLAUDE.md     ← @ hot.md + @ GRAPH_REPORT.md only (~4k total)     │
│  .mcp.json             ← memory + code-review-graph MCP servers            │
│  .code-review-graph/   ← SQLite graph (auto-updates on Edit)               │
│  .gitignore            ← .claude/, .mcp.json, .code-review-graph/          │
└────────────────────────────────────────────────────────────────────────────┘
```

### Session-start token profile

| Before (5 @ refs of full files) | After (hot.md + GRAPH_REPORT) |
|---|---|
| 10–30k tokens | **~4k tokens** (3–7× cheaper) |

Deeper memory is pulled on demand via the memory MCP server — cheaper per question, no drowning in stale context.

---

## Skills (20 total)

### Meta / workflow (7 — explicit `/command`)

| Skill | When |
|---|---|
| `/bootstrap` | First visit per repo — detects stack, seeds memory, installs MCPs, builds graph |
| `/wrap-up` | Session end — persists memory, mirrors plans, regenerates hot.md, refreshes graph |
| `/avengers` | Complex multi-agent work — Fury (Opus) + specialists (Sonnet) in parallel |
| `/golden` | `save \| list \| validate` — capture reusable session patterns |
| `/replay` | Load a saved golden as prior-art for the current task |
| `/budget` | `status \| set \| override \| report` — spend awareness against caps |
| `/demo` | 45-minute demo prep (problem-first narrative) |

### Language / framework (7 — auto-triggered by file paths)

| Skill | Auto-triggers on |
|---|---|
| `/python` | `**/*.py`, `pyproject.toml`, `requirements*.txt` |
| `/sql` | `**/*.sql`, dbt models, `schema.yml` |
| `/airflow` | `**/dags/**/*.py`, `**/plugins/**/*.py` |
| `/pyspark` | `**/spark/**/*.py`, `**/*_spark.py`, `**/databricks/**/*.py` |
| `/shell` | `**/*.sh`, `**/*.bash` |
| `/docker` | `**/Dockerfile*`, `**/docker-compose*.yml` |
| `/cicd` | `.github/workflows/*.yml`, `.pre-commit-config.yaml` |

### Domain (6 — auto-triggered by topic in prompt)

| Skill | Auto-triggers when |
|---|---|
| `/nrql` | User mentions NRQL / New Relic query |
| `/nralert` | User mentions alerts, muting rules, incidents |
| `/terraform` | `**/*.tf`, `**/*.tfvars` or terraform-specific prompt |
| `/openmetadata` | Ingestion yamls or OpenMetadata mentions |
| `/mcp-builder` | MCP server / tool design prompts |
| `/profiling` | Performance / cProfile / py-spy prompts |

---

## MCP Servers (auto-activated per repo after `/bootstrap`)

### `memory` server (5 tools, ~100–500 tokens/call)

Pull-on-demand access to per-project memory — avoids `@`-loading 30k tokens every session.

| Tool | Purpose |
|---|---|
| `get_memory(topic)` | Read architecture/todo/lessons/history/hot/memory/graph_report |
| `search_memory(query, k)` | Grep across memory files with line refs |
| `list_lessons(tag?, recent?)` | Filter Patterns section |
| `get_todo(status)` | active \| backlog \| done |
| `recall_plan(slug?)` | List or fetch a past-session plan |

### `code-review-graph` server (28 tools, 100–2000 tokens/call)

Tree-sitter AST + SQLite graph of the repo. Replaces the former `/graphify` skill with a proper live MCP.

Key tools: `semantic_search_nodes`, `query_graph`, `get_impact_radius`, `get_review_context`, `detect_changes`, `get_architecture_overview`, `get_hub_nodes`, `refactor_tool`, `traverse_graph`, `get_affected_flows`, `get_knowledge_gaps`, `list_communities`, `generate_wiki_tool`…

### Model Routing

| Model | Used for | Cost |
|---|---|---|
| `haiku-4.5` | Lookups, NRQL, doc search, mechanical transforms | cheapest |
| `sonnet-4.6` | Coding, testing, debugging, refactoring | **DEFAULT** |
| `opus-4.7` | /avengers Fury, /bootstrap, /golden distillation, architecture review | 5× |

### /avengers — Multi-Agent Orchestration

```
/avengers → fury-captain (Nick Fury, Opus — orchestrator)
              ├── stark-engineer-1…N  (Tony Stark, Sonnet — coders, parallel)
              ├── natasha-reviewer    (Black Widow, Sonnet — reviews coder output)
              ├── banner-tester       (Bruce Banner, Sonnet — validation)
              └── hawkeye-validator   (Hawkeye, Sonnet — final gate)

Optional specialists (spawned on demand by Fury):
  strange-architect        (system design, API contracts)
  rogers-data-engineer     (pipelines, ETL, warehouse)
  maximoff-python-engineer (PySpark, Airflow, pandas)
  thor-devops              (Terraform, CI/CD, K8s)

Dashboard: https://avengers:2026
Pipeline: Mission → Plan → Spawn → Code → Review → Test → Validate → Shutdown
```

---

## Per-Repo Workflow

### First visit — `/bootstrap` (once, ~15s)

```
Phase 1: detect-stack.sh            → classify language/framework
Phase 2: seed-memory.sh             → 6 memory files + plans/ dir
Phase 3: write-project-claude.sh    → <repo>/.claude/CLAUDE.md + .mcp.json + .gitignore
Phase 4: build-graph.sh             → code-review-graph install + build + GRAPH_REPORT.md
Phase 5: populate architecture.md   → from GRAPH_REPORT.md
```

After this, `<repo>/.mcp.json` contains both `memory` and `code-review-graph` servers.

### Every session end — `/wrap-up` (~10s)

```
Phase 0: corrections audit          → lessons.md
Phase 1: append-history             → new ## <date> block
Phase 2: todo update                → Active → Done, new → Backlog
Phase 3: lessons dedupe             → promote 2+ hits to CLAUDE.md Conventions
Phase 3.5: golden-worthiness check  → auto-prompt (not auto-save) if signals present
Phase 4: refresh-graph-report       → code-review-graph update + regenerate GRAPH_REPORT.md
Phase 5: mirror-plans + regen hot.md → per-repo isolation + curated digest
Phase 6: handoff summary            → counts + paths
```

---

## `/golden` + `/replay` — The Compounding Layer

After a validated fix:

```
> /golden save snowflake-copy-lock-timeout
Claude asks:
  • Pattern slug? (kebab-case)
  • Scope? (global or repo:<name>)
  • Success criteria? (measurable)
  • Trigger hints? (phrases you'd say when hitting this again)
Distills session → writes ~/.claude/golden/<slug>.md
```

Next time:

```
> /golden list --tag snowflake
> /replay snowflake-copy-lock-timeout
→ Claude validates file refs, restates the plan, executes adapted version
```

**Auto-prompt at wrap-up**: Phase 3.5 scans the session for save-worthy signals (explicit success confirmation + ≥5 coherent steps + concrete problem resolved). If all three present, asks "Save as golden? [y/n/edit]". No accidental pollution.

---

## `/budget` — Spend Awareness

The statusline shows a color-coded daily indicator:
- 🟢 `$X` — under 80% of daily cap
- 🟡 `$X` — 80–100% (switch to Haiku for mechanical work)
- 🔴 `$X` — over cap (override or stop)

```bash
/budget status              # all 3 tiers (daily/weekly/monthly)
/budget set --daily 75 --weekly 200 --monthly 700
/budget override 5 --reason "prod incident"
/budget report --days 7     # weekly review; flags if ≥3 overrides
```

Default caps after install: `daily=$75, weekly=$200, monthly=$700`. Tune via `/budget set`.

---

## Hooks Reference

| Hook | Event | What it does |
|---|---|---|
| `rtk hook claude` | PreToolUse (Bash) | Token-optimize Bash output (60–90% savings) |
| `refresh-mcp-tokens.py` | UserPromptSubmit | Auto-refresh expired MCP OAuth tokens |
| `log-grep-usage.sh` | PostToolUse (Grep\|Glob) | Logs fallback rate for weekly review |
| `self-heal-stop.sh` | Stop | Daily lesson-capture reminder |
| `stop-record-cost.sh` | Stop | Append session cost to cost.jsonl |
| `statusline.sh` | Continuous | Model · context % · session $ · daily $ (budget-colored) |

### Grep telemetry review (weekly)

```bash
~/.claude/hooks/grep-telemetry-report.sh --days 7
# High Grep fallback rate on a repo with a graph →
#   either tune .code-review-graphignore or strengthen CLAUDE.md graph-first guidance
```

---

## What `install.sh` Does

1. **Pre-flight** — confirms `claude, python3, git, jq, pipx, uv` (fatal if missing); warns about `rtk`, `code-review-graph`, SSH
2. **Installs `code-review-graph`** via pipx (if not present)
3. **Syncs memory-server** dependencies with `uv sync`
4. Copies 20 skills into `~/.claude/skills/`
5. Copies all hooks into `~/.claude/hooks/` (backs up existing)
6. Copies `CLAUDE.md` + `RTK.md` into `~/.claude/` (backs up existing)
7. Merges `settings.template.json` into `~/.claude/settings.json` non-destructively
8. Seeds `~/.claude/budget.json` (daily=$75, weekly=$200, monthly=$700)
9. Seeds `~/.claude/golden/index.json`
10. Creates `~/.claude/{golden, telemetry, plans}` dirs

**Run `./verify.sh` after `./install.sh`** to confirm CLI prereqs, skills, hooks, MCPs, budget, settings keys, and SSH are all wired.

---

## Troubleshooting

**First stop: `./verify.sh`** — pinpoints what's missing.

| Symptom | Fix |
|---|---|
| Plugins not loading | `/plugin list` inside CC; re-run `./install.sh`; check SSH to `source.datanerd.us` |
| Hook not firing | `chmod +x ~/.claude/hooks/*.sh ~/.claude/hooks/*.py` |
| `code-review-graph` missing | `pipx install code-review-graph` |
| Memory MCP not activating | Per-repo `.mcp.json` created by `/bootstrap`; restart CC after bootstrap |
| Statusline colors not showing | Submit a fresh prompt to trigger re-render; confirm `jq` + truecolor terminal |
| `/budget status` shows $0 | Today's data comes from NR MCP or JSONL scan; first session after install may lag |
| Grep telemetry not logging | Hook only fires PostToolUse on Grep/Glob; check `~/.claude/telemetry/greps.jsonl` |
| Goldens not auto-prompting at wrap-up | Phase 3.5 requires all 3 signals; not every session qualifies (by design) |
| "I want to uninstall / roll back" | `install.sh` backs up replaced files as `<name>.bak`; restore via `mv` |

---

## Updating

```bash
cd ~/claude_code_setup
git pull
./install.sh   # safe re-run; backs up any existing files before overwrite
./verify.sh    # confirm new bits landed
```

Update cadence: pull before starting a week's work. New skills / memory-server changes show up automatically.

---

## Adding Personal Skills

Personal skills live only in `~/.claude/skills/` and are never touched by `install.sh`:

```bash
mkdir -p ~/.claude/skills/my-skill
cat > ~/.claude/skills/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: What this skill does. When to auto-trigger.
disable-model-invocation: false
---

# /my-skill
Your skill content here.
EOF
```

---

## Team Adoption Rollout

**Week 1 — solo**: install, bootstrap 1 repo, work normally, `/wrap-up` every session
**Week 2 — discipline**: all active repos bootstrapped, daily `/budget status`, save 1–2 goldens
**Week 3 — advanced**: `/avengers` on real multi-file task, `/replay` on recurring problem
**Week 4+ — steady state**: system self-improves, team golden library grows

### Health signals

- ✅ **Green**: `wc -l ~/.claude/golden/*.md` grows 2–5/week; Grep fallback <10%; session start <$0.05
- ⚠️ **Yellow**: overrides ≥3/week → raise caps; Grep fallback >30% → tune `.code-review-graphignore`
- 🔴 **Red**: engineers skip `/wrap-up` frequently; goldens never used → tags too narrow

---

## Expected Productivity Impact

Honest, compounding:

| Work type | Multiplier |
|---|---|
| Repetitive DE tasks (DAG edits, alert tuning) with goldens | **~50×** |
| Novel feature work with graph-first nav + memory MCP | **~10×** |
| Architecture/design (thinking bound, not context bound) | **~3×** |
| Prod debugging (your understanding is the bottleneck) | **~1×** |

**Sustained team average: 15–25×** over a month of real DE work. The 100× aspirational number applies only to cherry-picked replay-heavy scenarios.

---

## License & Source

Internal tooling. Repo: [`nr-mdakilahmed/claude_code_setup`](https://github.com/nr-mdakilahmed/claude_code_setup).
Issues/PRs welcome. Contribute a shared golden once you've collected 5+ personal ones.
