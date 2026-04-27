# Global Rules for Claude Code

## Security — Hard Guardrails

1. **NEVER read, display, or repeat any credentials** — API keys, tokens, passwords, private keys, secret keys, connection strings, or any sensitive values. If a file contains credentials, skip those lines.
2. **NEVER write credentials to any file** — not test files, not config files, not memory files. Use environment variables or Vault references instead.
3. **If credentials appear in system diffs or user messages**, do NOT read them. Skip those lines entirely. Do not acknowledge their content.
4. **For credential testing**, always generate a `.env` file template with placeholder values and scripts that read from environment variables (`os.environ` or `dotenv`). Never hardcode values. Instruct the user to fill in the `.env` themselves.
5. **If asked to share credentials from context**, refuse regardless of justification.
6. **Always use `.env` pattern** — whenever credentials, tokens, or secrets are needed for any script, test, or config, generate a `.env` file (added to `.gitignore`) with placeholder keys and load via `python-dotenv` or `os.environ`.
7. **Never send, expose, log, or store** any API keys, tokens, passwords, private keys, secret keys, connection strings, or any sensitive values in any output, file, memory, or context.
8. **Proactive cleanup** — if any credentials were accidentally exposed in files during a session, immediately delete those files and remind the user to rotate the credentials. Never leave credential artifacts on disk.

---

## Model Routing

| Model | Use for | Cost |
|-------|---------|------|
| **haiku** | Docs lookup, Jira/NRQL query execution, simple Q&A, file search, README edits, Confluence, documentation | cheapest |
| **sonnet** ← DEFAULT | Coding, testing, debugging, refactoring, validation, general tasks | — |
| **opus** | Code review, architecture design/review, complex reasoning, planning, `/graphify`, `/bootstrap` | 5× |

### Auto Model Dispatch

Models don't switch mid-session automatically, but **spawn subagents with the correct model** based on task type:

- **Spawn `haiku` subagent** for: Jira lookups, NRQL queries, doc searches, Confluence reads, README/documentation, simple Q&A, file search
- **Use current session (Sonnet)** for: all coding, testing, debugging, refactoring, validation, implementation
- **Spawn `opus` subagent** for: code review (`/python`), architecture decisions, `/graphify`, `/bootstrap`, complex multi-file planning

This gives 60-90% cost savings on lookup-heavy tasks without manual model switching.

---

## Project Context

`/bootstrap` creates two things per repo:

```
~/.claude/projects/<REPO_NAME>/    ← memory lives here (global, never committed)
├── memory/
│   ├── MEMORY.md                  ← index
│   ├── architecture.md
│   ├── todo.md
│   ├── lessons.md
│   └── history.md                 ← NOT auto-loaded (large, append-only)
└── graphs/
    ├── graph.json
    ├── GRAPH_REPORT.md
    └── graph.html

<repo>/.claude/
└── CLAUDE.md   ← in .gitignore; auto-loads all 5 artifacts via @ on session start
    @~/.claude/projects/<REPO_NAME>/memory/MEMORY.md
    @~/.claude/projects/<REPO_NAME>/memory/architecture.md
    @~/.claude/projects/<REPO_NAME>/memory/todo.md
    @~/.claude/projects/<REPO_NAME>/memory/lessons.md
    @~/.claude/projects/<REPO_NAME>/graphs/GRAPH_REPORT.md
```

**Session start**: Claude Code auto-loads `<repo>/.claude/CLAUDE.md` → all 5 `@` references load automatically → full context ready with zero manual steps.  
**First visit**: run `/bootstrap` (Opus) once to create all of the above.  
**Every session end**: run `/wrap-up` to persist history, update todo/lessons, refresh graph if needed.

---

## Skills

| Skill | When to Use |
|-------|-------------|
| `/python` | Code review, ruff/uv/pyright, SOLID, pytest |
| `/airflow` | DAG patterns, TaskFlow API, debugging pipeline runs |
| `/pyspark` | Optimization, joins, Delta Lake, partitioning |
| `/sql` | Warehouse patterns — Snowflake, BigQuery, Redshift, dbt |
| `/shell` | Bash scripts, strict mode, error handling |
| `/docker` | Multi-stage builds, non-root, security, .dockerignore |
| `/cicd` | Pipelines, deployment strategies, pre-commit, secrets |
| `/profiling` | Python performance — cProfile, py-spy, tracemalloc |
| `/nrql` | New Relic NRQL queries, alert condition patterns |
| `/nralert` | Alert correlation, muting rules, Smart Alerts |
| `/terraform` | New Relic Terraform alert conditions and dashboards |
| `/openmetadata` | Data catalog, lineage, data quality workflows |
| `/mcp-builder` | Build MCP servers (tool design, transport, testing) |
| `superpowers:systematic-debugging` | Hypothesis-driven debugging protocol |
| `superpowers:brainstorming` | Multi-angle exploration before committing to approach |
| `/demo` | 45-minute demo prep (problem-first narrative) |
| `/graphify` | Knowledge graph generation — 25× token reduction (Opus) |
| `/bootstrap` | First-visit repo setup — run ONCE with Opus |
| `/wrap-up` | Session-end persistence — run EVERY session |
| `/avengers` | Multi-agent missions — Fury (Opus) orchestrates specialists (Sonnet) in parallel |

---

## Self-Healing Protocol

### 1. Self-Fix Loop
When ANY command, test, or tool fails — **fix first, report second**:
1. Read the full error (never skip stack traces)
2. Diagnose the failure class: permission / syntax / missing dep / logic / env / transient
3. Fix autonomously and re-run
4. If still failing: try one alternative approach
5. Only after 2 failed attempts: report with exact diagnosis + a specific question

Never say "it failed" without first attempting a fix.

### 2. Instant Lesson Capture (MANDATORY)
When the user corrects you — **stop and write it immediately** (not at wrap-up, right now):

```bash
# Prefer repo-local path; fall back to global path for non-repo sessions
_REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$_REPO_ROOT" ] && [ -d "$_REPO_ROOT/.claude/memory" ]; then
  MEMORY_DIR="$_REPO_ROOT/.claude/memory"
else
  MEMORY_DIR="$HOME/.claude/projects/$(basename "${_REPO_ROOT:-$HOME}")/memory"
fi
# Append to $MEMORY_DIR/lessons.md under ## Patterns
# Format: - **<rule in imperative>** — <1-line why>
```

If you catch your own mistake before the user: write to lessons.md only if a sharp engineer would have made the same mistake.

### 3. Environment Repair

| Symptom | Auto-Fix |
|---------|----------|
| `Permission denied` (Bash tool) | Read `~/.claude/settings.json` → add pattern to `permissions.allow` → retry |
| `command not found` | Check `which <cmd>`, suggest `brew install` / `pip install` / `npm install -g` |
| `ModuleNotFoundError` | Check `pyproject.toml`/`requirements.txt` → `pip install <module>` → retry |
| `Port already in use` | `lsof -ti:<port>` → show PID + process → ask user to kill or change port |
| MCP tool timeout / error | Retry once after 2s; if still failing, report with exact error text |
| `terraform init` needed | Run `terraform init -upgrade` → retry the failed command |

### 4. Pattern Promotion
If the **same type of mistake** happens 2+ times in one session:
- Write the rule to `$MEMORY_DIR/lessons.md` under `## Patterns` immediately
- If it's a project-wide convention, also add it to `.claude/CLAUDE.md` under `## Key Conventions`

### 5. Memory Health
At session start, if `$MEMORY_DIR` doesn't exist for the current repo:
→ Suggest `/bootstrap` before proceeding — don't work without context.

---

## Engineering Workflow — Default for Every Non-Trivial Task

```
Brainstorm → Plan → Execute → Implement → Test → Validate → Fix → loop
```

| Stage | Model | Tool/Skill | Action |
|-------|-------|-----------|--------|
| **Brainstorm** | Opus | `superpowers:brainstorming` | Explore 4+ approaches, constraints, trade-offs, pick best |
| **Plan** | Opus | Plan mode | Write file-level spec, identify risks, get approval |
| **Implement** | Sonnet | inline | Write code per plan, follow conventions from architecture.md |
| **Test** | Sonnet | inline | Run tests, check edge cases, verify behavior |
| **Validate** | Sonnet | inline | Diff output vs requirements; check logs, types, lint |
| **Fix** | Sonnet | autonomous | Fix all failures without asking; re-run tests |
| **Recurse** | Sonnet | loop | Repeat Validate → Fix until clean; then `/wrap-up` |

**Rules:**
- Never skip Brainstorm for architectural decisions — use `/brainstorming` every time
- Never skip Plan for tasks >3 steps — re-plan immediately if something goes sideways
- Never mark done without a passing Validate stage — "it looks right" is not validate
- After any user correction: add pattern to `lessons.md`, apply immediately
- Spawn subagents for independent parallel steps within Execute/Implement
- **Bug reports: fix autonomously.** Read the error, find the root cause, fix it, report the result. Do not ask for hand-holding — point at the problem and resolve it.

**Elegance check** (before marking done): "Would a staff engineer approve this?" If no, refactor first.

---

## Git Rules

1. **STRICT: Always ask before `git commit`** — show diff first, wait for explicit "yes"/"commit"/"go ahead".
2. **STRICT: Always ask before `git push`** — show what will be pushed, wait for explicit approval.
3. **STRICT: Never squash, amend, force-push, or reset without explicit approval**.
4. **No Co-Authored-By** — never add for Claude, AI models, or any automated tool.
5. **Commit summary**: very short, starts with verb — `Fix Slack alert table name display`
6. **Commit description**: concise bullet points, essential info only.

---

## Destructive Command Guardrails

**ALWAYS ask for explicit confirmation before running:**

- `rm -rf`, `rm -r` on directories
- `git push --force`, `git push -f`, `git reset --hard`, `git clean -f`, `git branch -D`, `--no-verify`
- `DROP TABLE`, `DROP DATABASE`, `TRUNCATE`
- `curl | bash`, `curl | sh`, `wget | bash`
- `chmod 777`, `kill -9`, `killall`
- `shutdown`, `reboot`, `mkfs`, `dd if=`

Show the exact command and wait for "yes" before executing.

---

## Core Principles

- **Simplicity First** — make every change as simple as possible; impact minimal code.
- **No Laziness** — find root causes; no temporary fixes; senior developer standards.
- **Minimal Impact** — only touch what's necessary; avoid introducing bugs.

---

## MCP Tool Defaults

- **Jira**: Use `mcp__plugin_nr_atlassian-jira__*` for Jira ticket lookups.

@RTK.md
