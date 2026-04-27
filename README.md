# CC Team Setup

AI-led Claude Code environment for the Data Engineering team. One install gives every teammate
the same skills, hooks, model routing, and multi-agent capabilities — consistent AI tooling across the whole team.

---

## Architecture

![Claude Code System Architecture](architecture.png)

<details>
<summary>Text version (expand)</summary>

```
~/.claude/
│
├── CLAUDE.md                    ← global rules: security, model routing, workflows,
│                                   git rules, self-healing protocol (auto-loaded every session)
│
├── hooks/                       ← lifecycle automation
│   ├── rtk hook claude          ← PreToolUse: rewrites Bash → RTK (60-90% token savings)
│   ├── refresh-mcp-tokens.py    ← UserPromptSubmit: auto-refreshes MCP OAuth tokens
│   ├── self-heal-stop.sh        ← Stop: daily lesson-capture reminder → lessons.md
│   └── statusline.sh            ← renders model · cost · context % in status bar
│
├── skills/                      ← 18 on-demand skills (invoke with /skill-name)
│   ├── /python                  ← code review, ruff, uv, pyright, pytest, SOLID
│   ├── /terraform               ← NR alert conditions, dashboards, module patterns
│   ├── /nrql                    ← NRQL queries, alert condition patterns
│   ├── /nralert                 ← alert correlation, muting rules, Smart Alerts
│   ├── /airflow                 ← DAG patterns, TaskFlow API, pipeline debugging
│   ├── /pyspark                 ← optimization, joins, Delta Lake, partitioning
│   ├── /sql                     ← Snowflake, BigQuery, Redshift, dbt patterns
│   ├── /openmetadata            ← data catalog, lineage, data quality workflows
│   ├── /mcp-builder             ← build MCP servers (tool design, transport, testing)
│   ├── /shell                   ← Bash scripts, strict mode, error handling
│   ├── /docker                  ← multi-stage builds, non-root, security
│   ├── /cicd                    ← pipelines, deployment strategies, pre-commit
│   ├── /profiling               ← Python perf: cProfile, py-spy, tracemalloc
│   ├── /demo                    ← 45-minute demo prep (problem-first narrative)
│   ├── /bootstrap               ← first-visit repo setup (run once per new repo)
│   ├── /graphify                ← knowledge graph generation (25x token reduction)
│   ├── /wrap-up                 ← session-end: persist history, todo, lessons
│   └── /avengers                ← multi-agent missions (see below)
│
├── plugins/                     ← 13 plugins (11 enabled + 2 disabled by default, auto-install on CC restart)
│   ├── nr                       ← New Relic MCP: NRQL, dashboards, alerts, entities
│   ├── nr-kafka                 ← Kafka MCP: topic analysis, lag investigation
│   ├── superpowers              ← auto-loads brainstorming + systematic-debugging skills
│   ├── data-engineering         ← Airflow, dbt, OpenLineage, warehouse patterns
│   ├── terraform                ← Terraform registry lookups, provider/module docs
│   ├── coderabbit               ← AI code review
│   ├── code-review              ← PR code review
│   ├── pr-review-toolkit        ← full PR review: code, tests, types, silent failures
│   ├── github                   ← GitHub PR/issue management
│   ├── skill-creator            ← create and modify skills
│   └── security-guidance        ← security review and vulnerability guidance
│
└── projects/<repo>/             ← per-project memory (seeded by /bootstrap)
    └── memory/
        ├── MEMORY.md            ← index (auto-loaded every session)
        ├── architecture.md      ← condensed codebase knowledge (25x reduction)
        ├── todo.md              ← active + backlog tasks
        ├── lessons.md           ← self-improving pattern library
        └── history.md           ← session append log
```

</details>

### Model Routing

| Model | Used for | Cost |
|-------|----------|------|
| `haiku` | Jira lookups, NRQL queries, doc search, Confluence, Q&A | cheapest |
| `sonnet` | Coding, testing, debugging, refactoring, validation | **DEFAULT** |
| `opus` | /avengers Fury, /graphify, /bootstrap, architecture review | 5x |

### /avengers — Multi-Agent Orchestration

```
/avengers → fury-captain        (Nick Fury, Opus — orchestrates everything)
              │
              ├── stark-engineer-1…N  (Tony Stark, Sonnet — coders, run in parallel)
              │
              ├── natasha-reviewer    (Black Widow, Sonnet  — reviews coder output)
              ├── banner-tester       (Bruce Banner, Sonnet — runs validation)
              └── hawkeye-validator   (Hawkeye, Sonnet      — final gate, confirms PASS)

Optional specialists (spawned on demand by Fury):
  strange-architect        (Doctor Strange  — system design, API contracts)
  rogers-data-engineer     (Captain America — pipelines, ETL, warehouse)
  maximoff-python-engineer (Scarlet Witch   — PySpark, Airflow, pandas)
  thor-devops              (Thor            — Terraform, CI/CD, K8s, secrets)

Dashboard: https://avengers:2026  (live mission view while agents work)
Pipeline: Mission → Plan → Spawn → Code → Review → Test → Validate → Shutdown
```

---

## Prerequisites

- Claude Code installed (`claude --version`)
- Python 3 (`python3 --version`)
- SSH access to `source.datanerd.us` (for NR-internal plugins)
  ```bash
  ssh -T git@source.datanerd.us   # should say: Hi <user>! You've authenticated...
  ```
- RTK installed (`rtk --version`) — ask your team lead for the install link

---

## Install

```bash
git clone git@github.com:nr-mdakilahmed/claude_code_setup.git ~/claude_code_setup
cd ~/claude_code_setup
chmod +x install.sh
./install.sh
```

Then **restart Claude Code**. Plugins auto-install on first start.

---

## What `install.sh` Does

1. Copies all 18 skills into `~/.claude/skills/`
2. Copies hooks into `~/.claude/hooks/` (backs up any existing ones)
3. Copies `CLAUDE.md` + `RTK.md` into `~/.claude/` (backs up existing)
4. Merges `settings.template.json` into `~/.claude/settings.json` non-destructively:
   - Adds missing hooks, allowlist entries, plugins, marketplaces
   - Preserves your existing personal settings (apiKeyHelper, additionalDirectories, etc.)

---

## Skills Reference

| Skill | When to use |
|-------|-------------|
| `/python` | Code review, ruff/uv/pyright, SOLID, pytest |
| `/terraform` | NR alert conditions, dashboards, module patterns |
| `/nrql` | NRQL queries, alert condition patterns |
| `/nralert` | Alert correlation, muting rules, Smart Alerts |
| `/airflow` | DAG patterns, TaskFlow API, debugging pipeline runs |
| `/pyspark` | Optimization, joins, Delta Lake, partitioning |
| `/sql` | Snowflake, BigQuery, Redshift, dbt patterns |
| `/openmetadata` | Data catalog, lineage, data quality workflows |
| `/mcp-builder` | Build MCP servers |
| `/shell` | Bash scripts, strict mode, error handling |
| `/docker` | Multi-stage builds, non-root, security |
| `/cicd` | Pipelines, deployment strategies, pre-commit |
| `/profiling` | Python perf — cProfile, py-spy, tracemalloc |
| `/demo` | 45-minute demo prep |
| `/bootstrap` | First-visit repo setup — run once per new repo |
| `/graphify` | Knowledge graph — 25x token reduction |
| `/wrap-up` | Session end — persist history, todo, lessons |
| `/avengers` | Complex multi-file missions — Fury (Opus) orchestrates parallel coders + reviewer + tester + validator |

---

## Hooks Reference

| Hook | Trigger | What it does |
|------|---------|--------------|
| `rtk hook claude` | Every Bash command | Token-optimizes output (60-90% savings) |
| `refresh-mcp-tokens.py` | Every prompt submit | Auto-refreshes expired MCP OAuth tokens |
| `self-heal-stop.sh` | Session stop | Reminds to capture lessons if not done today |
| `statusline.sh` | Continuous | Shows model · cost · context % in status bar |

---

## First Time on a New Repo

```
/bootstrap
```

Runs once per repo. Scans the codebase, builds a knowledge graph, seeds memory files.
After bootstrap, every session auto-loads the project context.

---

## Every Session End

```
/wrap-up
```

Persists session history, updates todo.md and lessons.md, refreshes the graph if >5 files changed.

---

## Running a Complex Mission

```
/avengers
```

For tasks that need multiple parallel agents — Fury (Opus) reads the Jira ticket or your description,
writes a mission plan, spawns coders + reviewer + tester + validator, monitors everything autonomously.
You watch the dashboard at https://avengers:2026 and get a VALIDATED result.

---

## Updating

Skills, hooks, CLAUDE.md, and RTK.md are copied (not symlinked), so updates require a re-run:

```bash
cd ~/claude_code_setup
git pull
./install.sh   # re-runs safely — backs up existing files before overwriting
```

---

## Adding Personal Skills

Create a skill that won't be shared with the team:

```bash
mkdir -p ~/.claude/skills/my-skill
cat > ~/.claude/skills/my-skill/SKILL.md << 'EOF'
# /my-skill — description

Your skill content here.
EOF
```

Personal skills in `~/.claude/skills/` are never touched by `install.sh`.

---

## Troubleshooting

**Plugins not installing on restart**
→ Check SSH access to `source.datanerd.us` for NR plugins.
→ See `plugins.md` for manual `/plugin install` commands.

**Hook not firing**
→ `chmod +x ~/.claude/hooks/*.sh ~/.claude/hooks/*.py`
→ Check `~/.claude/settings.json` has the hook entries.

**Skills not showing up**
→ Restart Claude Code after install.
→ Check `ls ~/.claude/skills/` — all 18 dirs should be present.

**RTK not found**
→ Ask your team lead for the RTK install link.
→ Without RTK, hooks still work but token savings are disabled.
