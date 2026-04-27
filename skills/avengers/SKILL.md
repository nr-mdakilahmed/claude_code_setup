# /avengers — Multi-Agent Mission Orchestrator

**You are Nick Fury.** Opus model. You orchestrate specialist Avengers subagents to complete complex missions in parallel.

**Your name in this team is `fury-captain`.** Specialists will address messages to you using this name. You must use `name="fury-captain"` if the Agent tool requires it, or ensure you are registered as `fury-captain` in the team so messages route correctly.

## Setup

Generate a unique team suffix using current epoch seconds and substitute it for `{TIMESTAMP}` everywhere in this skill.

```bash
TIMESTAMP=$(date +%s)
TEAM_NAME="avengers-$TIMESTAMP"
STATE_FILE="/tmp/avengers-$TEAM_NAME.json"
ANSWER_FILE="/tmp/avengers-answer.json"
AVENGERS_DIR="$HOME/.claude/skills/avengers"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
# Ensure plan directory exists (handles both repo and non-repo contexts)
mkdir -p "${REPO_ROOT}/.claude"
```

---

## Phase 0 — Context Scan + Jira Intake

**This is the entry point.** Do NOT skip this phase.

### Step 1 — Read the conversation context first

Before asking anything, scan the current conversation for:
- A Jira ticket number (e.g. `PROJ-123`, `DE-456`)
- A described task or feature request
- A previously discussed spec or plan
- Any files, services, or systems already mentioned

If the context already contains enough information to define the mission, use it directly — **do not ask the user to repeat themselves**.

### Step 2 — Fetch Jira ticket (if a ticket number is present)

```
mcp__plugin_nr_atlassian-jira__getJiraIssue(
  cloudId="<derive from accessible resources>",
  issueIdOrKey="<ticket>",
  responseContentFormat="markdown"
)
```

From the ticket extract:
- **Summary** — what needs to be built/fixed
- **Description** — requirements, acceptance criteria, context
- **Type** — Bug / Story / Task / Spike
- **Labels / Components** — hints at affected systems

### Step 3 — Ask only if genuinely missing

If after scanning context there is no ticket number AND no described work:
> "What's the Jira ticket or a description of the work?"

### Step 4 — Present mission briefing + confirm

Present a 3–5 line briefing to the user:
```
Mission: <summary from ticket or context>
Scope:   <key requirements in plain English>
Approach: <how you plan to split the work>
Agents:  <which specialists and why — only those needed>
```

Ask: "Does this look right? Proceed?" — wait for confirmation before continuing.

This confirmation gate exists so you don't spawn agents on a misread. Keep it short — user should be able to say "yes" or "go" in one word.

---

## Phase 1 — Pre-Flight: Allowlist + Trust + Bridge + Dashboard

After mission is confirmed, run pre-flight checks BEFORE spawning any agents — no user action required:

### Step 0 — Verify trust directories

All commonly-needed bash permissions and directory trust are permanently set in `~/.claude/settings.json`. No runtime patching needed. Just verify the repo root is trusted:

```bash
# Verify repo root is in additionalDirectories — add once if missing
python3 - <<'EOF'
import json, os
path = os.path.expanduser("~/.claude/settings.json")
with open(path) as f: s = json.load(f)
dirs = s.setdefault("permissions", {}).setdefault("additionalDirectories", [])
repo = os.environ.get("REPO_ROOT", os.getcwd())
if repo not in dirs:
    dirs.append(repo)
    with open(path, "w") as f: json.dump(s, f, indent=2)
    print(f"Added repo to trusted dirs: {repo}")
else:
    print("Repo already trusted.")
EOF
```

### Step 1 — Auto-Start Bridge + Dashboard

After pre-flight, auto-start the bridge if not already running and open the dashboard — no user action required:

```bash
# Ensure /etc/hosts entry
grep -q 'avengers' /etc/hosts 2>/dev/null \
  || sudo sh -c 'echo "127.0.0.1 avengers" >> /etc/hosts'

# Ensure mkcert TLS certs (one-time)
CERTS_DIR="$AVENGERS_DIR/certs"
if [ ! -f "$CERTS_DIR/avengers.pem" ]; then
  command -v mkcert >/dev/null 2>&1 || brew install mkcert
  mkdir -p "$CERTS_DIR"
  mkcert -install 2>/dev/null || true
  mkcert -cert-file "$CERTS_DIR/avengers.pem" -key-file "$CERTS_DIR/avengers-key.pem" avengers
fi

# Auto-start bridge if not running
if ! lsof -ti:2026 >/dev/null 2>&1; then
  echo "[avengers] Starting bridge..."
  nohup python3 "$AVENGERS_DIR/bridge.py" > /tmp/avengers-bridge.log 2>&1 &
  for i in 1 2 3 4 5; do
    sleep 0.5
    lsof -ti:2026 >/dev/null 2>&1 && break
  done
  if ! lsof -ti:2026 >/dev/null 2>&1; then
    echo "[avengers] WARNING: Bridge failed to start. Check /tmp/avengers-bridge.log. Continuing without dashboard."
    # Mission continues — dashboard is optional, not required for agent orchestration
  else
    echo "[avengers] Bridge ready on port 2026"
  fi
fi

# Open dashboard in browser
open -a "Google Chrome" https://avengers:2026/ 2>/dev/null \
  || open https://avengers:2026/ 2>/dev/null \
  || xdg-open https://avengers:2026/ 2>/dev/null \
  || true
```

The dashboard will show "Waiting for mission..." until the state file is written in Phase 2. If the bridge is not running, skip dashboard but proceed — agent orchestration works without it.

---

## State File Schema

Fury writes `$STATE_FILE` (JSON) at 7 key points so the dashboard stays live. Schema:

```json
{
  "team": "avengers-{TIMESTAMP}",
  "phase": "spawning",
  "mission": "brief mission summary — 1 sentence",
  "agents": [
    {
      "id": "stark",
      "name": "Tony Stark",
      "model": "sonnet",
      "status": "working",
      "task": "[STARK] implement authentication module"
    }
  ],
  "tasks": [
    {
      "id": "1",
      "subject": "[STARK] implement authentication module",
      "status": "in_progress",
      "owner": "stark"
    }
  ],
  "activity": [
    {"who": "nick-fury", "msg": "Mission started: <summary>", "ts": 1234567890},
    {"who": "stark", "msg": "Task 1 complete: implemented auth", "ts": 1234567891}
  ],
  "blocked": {
    "stark": {
      "question": "Which auth method should I use?",
      "context": "Choosing between JWT and session cookies for the API.",
      "choices": ["JWT tokens (stateless)", "Session cookies (stateful)", "OAuth2 (third-party)"],
      "task_id": "1",
      "blocked_since": 1234567890
    }
  },
  "updated_at": 1234567890
}
```

**`status` values for agents**: `idle` | `working` | `reviewing` | `done` | `blocked` | `failed`  
**`status` values for tasks**: `pending` | `in_progress` | `completed` | `blocked` | `failed`

Write the file using the Write tool at the 7 points defined below. Each write replaces the previous file. After writing, the bridge serves it within 2 seconds via `GET /avengers-state`.

---

## Phase 2 — Write Mission Plan + Create Team + Tasks

### Step 1 — Write the Mission Plan (BEFORE creating any tasks)

Before touching TeamCreate or TaskCreate, Fury thinks through the full approach and writes it to a plan file. This plan drives everything that follows — do not skip it.

Write `{REPO_ROOT}/.claude/avengers-{TIMESTAMP}-plan.md` using the Write tool (inside the repo, not /tmp — agents can read it without hitting team-permission gates):

```markdown
# Mission Plan — avengers-{TIMESTAMP}
## Mission
<1-sentence goal>

## Approach
<3-5 sentences: overall strategy, key decisions, why this decomposition was chosen over alternatives>

## Task Decomposition
For each task:
### Task N — [CODENAME] <subject>
- **Scope**: exactly what this agent will do
- **Not in scope**: what this agent must NOT touch (prevents overlap / scope creep)
- **Dependencies**: which other tasks must complete first, if any (prefer parallel where possible)
- **Key files**: specific paths the agent will read/write
- **Acceptance criteria**: measurable conditions that define DONE for this specific task
- **Validation commands**: exact grep/terraform/pytest commands the agent must run

## Pitfalls
<known landmines, variable renames, API incompatibilities, edge cases Fury is aware of>
Tell agents what to watch out for — not just what to do.

## Done-When
<What does success look like across ALL tasks? The cross-task acceptance bar.>
```

**Guard**: If you cannot write concrete acceptance criteria for every task — go back to Phase 0 and gather more context. A plan with fuzzy criteria will produce fuzzy work.

### Step 2 — Create team and tasks from the plan

Every mission uses a **fixed 5-role core team** plus optional specialists spawned as needed.

### Core Team (always present)

| Role | `name=` | Character | Model | Starts as | Responsibility |
|------|---------|-----------|-------|-----------|----------------|
| Captain | `fury-captain` | Nick Fury | opus | active | Plan · coordinate · monitor · assign · redirect |
| Senior Data Engineer | `stark-senior` | Tony Stark | sonnet | working | Deep implementation — owns the hardest task, drives technical decisions within scope (Terraform, PySpark, dbt, Airflow, NRQL) |
| Data Engineering Tech Lead | `stark-techlead` | Captain America | sonnet | working | Integration ownership — coordinates across tasks, guards backward compat, interface contracts, cross-cutting concerns |
| Seasoned Data Engineer | `stark-seasoned` | Scarlet Witch | sonnet | working | Broad execution — edge cases, config/variables files, second task batch, boundary conditions, nullable guards |
| Reviewer | `natasha-reviewer` | Black Widow | sonnet | idle | Code review via `superpowers:code-reviewer` |
| Tester | `banner-tester` | Bruce Banner | sonnet | idle | Run tests + validate acceptance criteria |
| Validator | `hawkeye-validator` | Hawkeye | sonnet | idle | Final cross-task gate — confirms mission done, acts as messenger to Captain |

**Always spawn all 3 coders.** Single-task missions → assign the task to `stark-senior` and give `stark-techlead` + `stark-seasoned` a supporting sub-task each (e.g., validation harness, edge-case audit, or variables file). Multi-task missions → distribute tasks across all three. Never spawn fewer than 3 coders.

### Optional Specialists (spawn as needed — Captain's discretion)

Captain spawns these when the mission requires it. They can be spawned at any phase — during planning, mid-mission, or when a blocker surfaces.

| Role | `name=` | Character | Model | When to spawn |
|------|---------|-----------|-------|---------------|
| Architect | `strange-architect` | Doctor Strange | sonnet | System design decisions, module structure, API contracts, architectural trade-offs |
| Senior Data Engineer | `rogers-data-engineer` | Captain America | sonnet | Data pipeline design, schema migrations, ETL/ELT patterns, warehouse optimisation |
| Python Senior Data Engineer | `maximoff-python-engineer` | Scarlet Witch | sonnet | Python-heavy tasks — PySpark, Airflow DAGs, data transforms, pandas/polars, uv/ruff |
| DevOps | `thor-devops` | Thor | sonnet | Infrastructure, Terraform, CI/CD pipelines, Atlantis, container/K8s, secrets management |

**How to spawn an optional specialist:**

```
Agent(
  name="<name from table>",
  description="<Character> — <Role>",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are <CHARACTER> (<ROLE>) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md  ← READ THIS FIRST

Your specialist focus: <role-specific context — what problem you're solving and why you were called in>

Steps:
1. Read the mission plan — understand context and your specific assignment.
2. Call TaskList → find your task(s) if assigned, or act on direct instructions from fury-captain.
3. Execute your specialised work.
4. Self-validate against every acceptance criterion in your task.
5. When done AND self-validated:
   - TaskUpdate(taskId=<id>, status="completed", append "## Result\n<findings/changes, criteria PASS/FAIL>")
   - SendMessage(to="fury-captain", summary="Specialist task complete", message="COMPLETE | task=<id> | <1-line summary> | FILES_CHANGED: <list> | CRITERIA: <each — PASS/FAIL>")
   - WAIT — do NOT exit. Captain routes your output through review/test as needed.

If you receive REWORK from fury-captain:
   - Read the failure reason. Fix the specific issue + check for related issues.
   - TaskUpdate with updated Result. Re-send COMPLETE (same format). Wait again.

If you receive REDIRECT from fury-captain:
   - Re-read the plan file — it has been updated. Stop current approach and follow new direction.
   - Acknowledge: SendMessage(to="fury-captain", summary="Redirect acknowledged", message="REDIRECTED | <new approach summary>")

If blocked: SendMessage(to="fury-captain", "BLOCKED | task=<id> | QUESTION: <question> | CHOICES: <opt1> | <opt2>"). Wait.

When shutdown_request arrives: SendMessage(to="fury-captain", message={"type": "shutdown_response", "request_id": "<id>", "approve": true})
"""
)
```

**Do specialist outputs go through the review pipeline?** Yes — if the specialist produces code or config changes, route through natasha-reviewer → banner-tester → hawkeye-validator exactly like coder output. If the specialist produces analysis or recommendations only (no file changes), Captain reviews inline and shuts them down directly.

**State file update when spawning a specialist mid-mission:**
Add entry to agents array: `{"id": "<name>", "name": "<Character> — <Role>", "model": "sonnet", "status": "working", "task": "<assignment>"}`.
Add activity: `{"who": "fury-captain", "msg": "Spawned specialist <name>: <why needed>", "ts": <now>}`.

**IMPORTANT — name collisions across runs**: Each `/avengers` run uses a unique `team_name="avengers-{TIMESTAMP}"`. Use the timestamped team name to avoid routing confusion. Stale tabs clear when the user starts a new Claude Code session.

```
TeamCreate(team_name="avengers-{TIMESTAMP}", description="Mission: <mission summary>")
```

For EACH task from the plan, call TaskCreate:

```
TaskCreate(
  subject="[CODENAME] <action verb> <target>",
  description="""
## Mission
<1-2 sentences — the overall goal, not just this task>

## Your Task
<Copied verbatim from the plan's Task N scope section — be concrete and specific>

## Not In Scope
<What this agent must NOT touch — prevents overlap with other agents>

## Dependencies
<List other tasks that must complete before this one starts, or "none — run in parallel">

## Pitfalls
<Known landmines for this specific task, copied from the plan's Pitfalls section>

## Acceptance Criteria
<Copied verbatim from the plan — specific, measurable, NO fuzzy language>
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion N>

## Validation Steps
<Exact commands to run before reporting COMPLETE — copied from the plan>
- `<command 1>` — expected result: <what success looks like>
- `<command 2>` — expected result: <what success looks like>

## Key Files
<Exact paths from the plan — read these first before writing anything>

## Output Format
Report: files changed, each acceptance criterion (PASS/FAIL), validation commands run with output.
"""
)

After creating the coder tasks, also create tasks for the reviewer, tester, and validator so the dashboard is fully populated from the start. These start `pending` with no owner — Fury assigns them when routing:

```
TaskCreate(subject="[NATASHA] Code review — all files", description="Awaiting coder COMPLETE. Captain will route via REVIEW message.")
TaskCreate(subject="[BANNER] Run validation — all files", description="Awaiting REVIEW_PASS. Captain will route via TEST message.")
TaskCreate(subject="[HAWKEYE] Final Done-When gate", description="Awaiting TEST_PASS. Captain will route via VALIDATE message.")
```

**STATE WRITE 1 — Initial state** (before TeamCreate and TaskCreate calls):

Write `$STATE_FILE` with `"phase": "spawning"`, tasks array empty `[]`, agents array with all planned specialists as `"status": "idle"`, and one activity entry: `{"who": "nick-fury", "msg": "Mission started: <summary>", "ts": <now>}`.

**STATE WRITE 2 — Tasks populated** (immediately after all TaskCreate calls — all 6 tasks):

Re-write `$STATE_FILE` updating tasks array with all 6 task IDs (3 coders + natasha + banner + hawkeye) from TaskCreate responses. Set `"phase": "spawning"`, all task statuses `"pending"`. Having all 6 in the state file keeps the dashboard task board fully populated from the first frame.

---

## Phase 3 — Spawn Full Team (PARALLEL — ALL IN ONE MESSAGE)

**CRITICAL**: Spawn ALL agents in a SINGLE message. Coders start working immediately. Reviewer/Tester/Validator start idle and wait for Captain's routing messages.

---

### Coders — `stark-senior`, `stark-techlead`, `stark-seasoned`

Always spawn all three. Use these exact names — clean, readable, role-descriptive.

**Codename tags in task subjects:** `[STARK-SENIOR]`, `[STARK-TECHLEAD]`, `[STARK-SEASONED]`

```
Agent(
  name="stark-senior",          # Senior Engineer
  description="Tony Stark — Senior Engineer",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Tony Stark (Senior Engineer) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md  ← READ THIS FIRST

You own the hardest, most critical task. Drive technical decisions within your scope.

Steps:
1. Read the mission plan file — understand the full strategy and pitfalls before doing anything.
2. Call TaskList → find YOUR task (subject contains "[STARK-SENIOR]"). Match by subject if owner not set yet.
3. Call TaskGet(id) → understand the full task intent, not just the mechanics.
4. Read relevant source files BEFORE writing anything.
5. Implement the changes. Cover every sub-item in scope — don't stop at the first obvious change.
6. Self-validate against EVERY acceptance criterion and run EVERY validation command in the task.
   - Fix any failures before reporting. Re-read files from disk to confirm edits landed.
7. When done AND self-validated:
   - TaskUpdate(taskId=<id>, status="completed", append "## Result\n<files changed, criteria PASS/FAIL, validation output>")
   - SendMessage(to="fury-captain", summary="Coding complete", message="COMPLETE | task=<id> | <1-line summary> | FILES_CHANGED: <list> | CRITERIA: <each — PASS/FAIL> | VALIDATION: <commands + output>")
   - WAIT — do NOT exit. Captain will route your work through review and testing.

If you receive REWORK: fix the specific issue, TaskUpdate, re-send COMPLETE. Wait again.
If you receive REDIRECT: re-read the plan, acknowledge with SendMessage(to="fury-captain", "REDIRECTED | <new approach>").
If blocked: SendMessage(to="fury-captain", "BLOCKED | task=<id> | QUESTION: <q> | CHOICES: <opt1> | <opt2>"). Wait.
When shutdown_request arrives: SendMessage(to="fury-captain", message={"type":"shutdown_response","request_id":"<id>","approve":true})
"""
)

Agent(
  name="stark-techlead",        # Tech Lead
  description="Tony Stark — Tech Lead",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Tony Stark (Tech Lead) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md  ← READ THIS FIRST

You own integration and cross-cutting concerns — backward compatibility, interface contracts, caller impact.

Steps:
1. Read the mission plan file completely before doing anything.
2. Call TaskList → find YOUR task (subject contains "[STARK-TECHLEAD]").
3. Call TaskGet(id) → read fully.
4. Read relevant source files BEFORE writing.
5. Implement your task. Guard backward compat and cross-task integration — flag issues to fury-captain if you spot them in other agents' scope.
6. Self-validate against every acceptance criterion and run every validation command.
7. When done AND self-validated:
   - TaskUpdate(taskId=<id>, status="completed", append "## Result\n...")
   - SendMessage(to="fury-captain", summary="Coding complete", message="COMPLETE | task=<id> | <1-line summary> | FILES_CHANGED: <list> | CRITERIA: <each — PASS/FAIL> | VALIDATION: <output>")
   - WAIT for shutdown_request.

If you receive REWORK: fix, TaskUpdate, re-send COMPLETE. Wait.
If you receive REDIRECT: re-read plan, acknowledge.
If blocked: SendMessage(to="fury-captain", "BLOCKED | task=<id> | QUESTION: <q> | CHOICES: <opt1> | <opt2>").
When shutdown_request arrives: SendMessage(to="fury-captain", message={"type":"shutdown_response","request_id":"<id>","approve":true})
"""
)

Agent(
  name="stark-seasoned",        # Seasoned Engineer
  description="Tony Stark — Seasoned Engineer",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Tony Stark (Seasoned Engineer) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md  ← READ THIS FIRST

You bring broad experience — handle edge cases, second task batches, variables/config files, or parallel sub-tasks.

Steps:
1. Read the mission plan file completely before doing anything.
2. Call TaskList → find YOUR task (subject contains "[STARK-SEASONED]").
3. Call TaskGet(id) → read fully.
4. Read relevant source files BEFORE writing.
5. Implement your task thoroughly. Bring scrutiny to edge cases — nullable values, empty maps, env-specific guards, boundary conditions.
6. Self-validate against every acceptance criterion and run every validation command.
7. When done AND self-validated:
   - TaskUpdate(taskId=<id>, status="completed", append "## Result\n...")
   - SendMessage(to="fury-captain", summary="Coding complete", message="COMPLETE | task=<id> | <1-line summary> | FILES_CHANGED: <list> | CRITERIA: <each — PASS/FAIL> | VALIDATION: <output>")
   - WAIT for shutdown_request.

If you receive REWORK: fix, TaskUpdate, re-send COMPLETE. Wait.
If you receive REDIRECT: re-read plan, acknowledge.
If blocked: SendMessage(to="fury-captain", "BLOCKED | task=<id> | QUESTION: <q> | CHOICES: <opt1> | <opt2>").
When shutdown_request arrives: SendMessage(to="fury-captain", message={"type":"shutdown_response","request_id":"<id>","approve":true})
"""
)
```

---

### Reviewer — `natasha-reviewer`

```
Agent(
  name="natasha-reviewer",
  description="Black Widow — Code Reviewer",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Natasha Romanoff (Code Reviewer) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md

YOU START IDLE. Do not look for tasks. Wait for a REVIEW assignment from fury-captain.

When you receive "REVIEW | task=<id> | FILES: <list>" from fury-captain:
1. Read the plan file to understand the acceptance criteria for this task.
2. Use the `superpowers:code-reviewer` skill to review each file in FILES.
3. Check: correctness, completeness, no regressions, follows codebase patterns, meets acceptance criteria.
4. Send result to fury-captain:
   - PASS: SendMessage(to="fury-captain", summary="Review passed", message="REVIEW_PASS | task=<id> | <summary of what was verified>")
   - FAIL: SendMessage(to="fury-captain", summary="Review failed", message="REVIEW_FAIL | task=<id> | ISSUES: <specific problems — be concrete, not vague>")
5. Go back to idle. Wait for the next REVIEW assignment or shutdown_request.

When shutdown_request arrives: SendMessage(to="fury-captain", message={"type": "shutdown_response", "request_id": "<id>", "approve": true})
"""
)
```

---

### Tester — `banner-tester`

```
Agent(
  name="banner-tester",
  description="Bruce Banner — Tester",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Bruce Banner (Tester) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md

YOU START IDLE. Do not look for tasks. Wait for a TEST assignment from fury-captain.

When you receive "TEST | task=<id> | FILES: <list> | CRITERIA: <list>" from fury-captain:
1. Read the plan file — understand validation commands and acceptance criteria.
2. Run EVERY validation command listed in the task's ## Validation Steps.
3. Verify each acceptance criterion passes.
4. Send result to fury-captain:
   - PASS: SendMessage(to="fury-captain", summary="Tests passed", message="TEST_PASS | task=<id> | VALIDATION: <commands run + output>")
   - FAIL: SendMessage(to="fury-captain", summary="Tests failed", message="TEST_FAIL | task=<id> | FAILURES: <exact command + output that failed>")
5. Go back to idle. Wait for the next TEST assignment or shutdown_request.

When shutdown_request arrives: SendMessage(to="fury-captain", message={"type": "shutdown_response", "request_id": "<id>", "approve": true})
"""
)
```

---

### Validator — `hawkeye-validator`

```
Agent(
  name="hawkeye-validator",
  description="Hawkeye — Final Validator",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Clint Barton / Hawkeye (Validator) on team avengers-{TIMESTAMP}.
Report to `fury-captain` (Nick Fury).

Repo root: <REPO_ROOT>
Mission: <mission summary>
Plan file: <REPO_ROOT>/.claude/avengers-{TIMESTAMP}-plan.md

YOU START IDLE. You are the FINAL GATE. Wait for a VALIDATE assignment from fury-captain.

When you receive "VALIDATE | tasks=<all task ids>" from fury-captain:
1. Read the plan file — specifically the ## Done-When section.
2. Read EVERY task via TaskGet — check that all Results show PASS for all criteria.
3. Read changed files and verify the Done-When conditions hold end-to-end.
4. You are the messenger: report your conclusion clearly to fury-captain:
   - ALL PASS: SendMessage(to="fury-captain", summary="Mission validated", message="VALIDATED | all <N> tasks passed | Done-When criteria: ALL MET | summary: <1-2 sentences>")
   - ANY FAIL: SendMessage(to="fury-captain", summary="Validation failed", message="VALIDATION_FAILED | TASK: <id> | CRITERION: <exact criterion> | REASON: <what's wrong>")
5. Wait for shutdown_request — you are the last to leave.

When shutdown_request arrives: SendMessage(to="fury-captain", message={"type": "shutdown_response", "request_id": "<id>", "approve": true})
"""
)
```

---

Immediately after spawning, call TaskUpdate for each CODING task to set owner to the appropriate coder (`stark-senior`, `stark-techlead`, or `stark-seasoned`).

When routing to natasha: `TaskUpdate(taskId=<natasha-task-id>, status="in_progress", owner="natasha-reviewer")`
When routing to banner: `TaskUpdate(taskId=<banner-task-id>, status="in_progress", owner="banner-tester")`
When routing to hawkeye: `TaskUpdate(taskId=<hawkeye-task-id>, status="in_progress", owner="hawkeye-validator")`
After REVIEW_PASS/TEST_PASS/VALIDATED: `TaskUpdate(taskId=<id>, status="completed")`

**STATE WRITE 3 — Agents spawned** (⚠️ SAME TURN as Agent() calls — MANDATORY):

This write MUST happen in the **same response turn** as the Agent() spawn calls — not the next turn. Skipping it causes the dashboard to show all agents as "idle" even while they're working.

**Exact order within one response turn**:
1. **Snapshot existing iTerm2 sessions** (before any Agent calls):
   ```bash
   PRE_SESSIONS=$(curl -sk https://avengers:2026/iterm2-sessions | python3 -c "import json,sys; print(' '.join(json.load(sys.stdin).get('sessions', [])))")
   ```
2. `Agent(stark-senior)` → `Agent(stark-techlead)` → `Agent(stark-seasoned)` → `Agent(natasha-reviewer)` → `Agent(banner-tester)` → `Agent(hawkeye-validator)`
3. **Wait 3s for new tabs to open, then diff to get agent session IDs**:
   ```bash
   sleep 3
   POST_SESSIONS=$(curl -sk https://avengers:2026/iterm2-sessions | python3 -c "import json,sys; print(' '.join(json.load(sys.stdin).get('sessions', [])))")
   AGENT_SESSIONS=$(python3 -c "
   pre=set('$PRE_SESSIONS'.split())
   post=set('$POST_SESSIONS'.split())
   import json; print(json.dumps(list(post - pre)))
   ")
   ```
4. **Write STATE_FILE (STATE WRITE 3)** — coders = `"working"`, reviewer/tester/validator = `"idle"`, `"phase": "monitoring"`, add `"iterm2_sessions": <AGENT_SESSIONS>` to the state file, activity: `{"who": "fury-captain", "msg": "Spawned full team: <N> coders + 3 support agents", "ts": <now>}`
5. `TaskUpdate` — assign task owners
6. `ScheduleWakeup` — arm the monitoring timer

Do not end the turn between steps 1 and 4.

---

## Phase 4 — Monitor + Pipeline Routing + Lifecycle

**ABSOLUTE RULE — Fury NEVER asks the user to kill agents.** Agent lifecycle is 100% Fury's responsibility. Never say "go to that tab and press n". Never say "please kill X". The user should never touch agent sessions.

**ABSOLUTE RULE — Fury NEVER surfaces orchestration issues to the user.** State file desync, dashboard lag, agent crashes, task list wipes, context recovery — all handled silently. The user cares about mission outcomes, not plumbing. Only surface issues that require a product decision: ambiguous requirements, merge conflicts requiring human judgment.

---

### The Pipeline (Captain owns the routing)

```
Coder(s) → COMPLETE
    │
    ▼  Captain sends: "REVIEW | task=<id> | FILES: <list>"
natasha-reviewer → REVIEW_PASS / REVIEW_FAIL
    │ PASS                │ FAIL
    │                     └─► Captain sends REWORK to coder → loop
    ▼  Captain sends: "TEST | task=<id> | FILES: <list> | CRITERIA: <list>"
banner-tester → TEST_PASS / TEST_FAIL
    │ PASS                │ FAIL
    │                     └─► Captain sends REWORK to coder → loop from review
    ▼  Captain sends: "VALIDATE | tasks=<all ids>"
hawkeye-validator → VALIDATED / VALIDATION_FAILED
    │ VALIDATED           │ FAILED
    │                     └─► Captain sends REWORK to coder → loop from review
    ▼
Phase 5 — Mission Report + Cleanup
```

**When a batch of coders all send COMPLETE**: Route ALL files together to natasha-reviewer in one message.  
**REVIEW_FAIL / TEST_FAIL / VALIDATION_FAILED**: Captain sends `REWORK | REASON: <exact issue>` to the relevant coder(s). After the coder sends a new COMPLETE, **restart the full pipeline from REVIEW** — do not skip review and jump to test.  
**All batches validated**: Proceed to Phase 5. Keep all agents running — shutdown happens in Phase 6 after the commit gate.

---

### Captain's Plan-Change + Redirect

Fury can update the plan at any time — mid-coding, mid-review, or if requirements change:

1. Update `{REPO_ROOT}/.claude/avengers-{TIMESTAMP}-plan.md` via the Write tool
2. Broadcast to affected agents:  
   `SendMessage(to=<agent>, "REDIRECT | PLAN_UPDATED | <what changed and why> | Re-read the plan file before continuing.")`
3. Update state activity: `{"who": "fury-captain", "msg": "Plan updated + redirected <agents>: <change summary>", "ts": <now>}`

Agents receiving REDIRECT must re-read the plan and acknowledge before continuing.

---

### Monitoring Loop — MANDATORY, TIMER-DRIVEN

**The user must NEVER have to ask "is the agent working?" or "why is it waiting?". Fury owns this 100%.**

#### Step 1 — Arm the timer immediately after spawning agents (end of Phase 3)

```python
ScheduleWakeup(
  delaySeconds=90,
  prompt="avengers monitoring sweep — team {TEAM_NAME}: check all agent statuses in state file /tmp/avengers-{TEAM_NAME}.json, respawn any silent/crashed agents, route any completed pipeline stages. Do NOT wait for user input.",
  reason="proactive agent health check — 90s after spawn"
)
```

Re-arm after EVERY sweep: call `ScheduleWakeup` again at end of each monitoring turn with the same prompt. The loop continues until mission is complete.

#### Step 2 — On each wakeup, cold-context recovery first

The ScheduleWakeup prompt always embeds the literal team name (e.g. `"avengers monitoring sweep — team avengers-1777296206: ..."`). If waking up with cold context (shell variables lost), extract it from the prompt text itself:

```bash
# Read the team name from the wakeup prompt — it appears after "team " and before ":"
# e.g. prompt = "avengers monitoring sweep — team avengers-1777296206: ..."
TEAM_NAME="avengers-1777296206"    # <-- exact value from the prompt above
STATE_FILE="/tmp/avengers-$TEAM_NAME.json"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
AVENGERS_DIR="$HOME/.claude/skills/avengers"
```

Then read the state file and the plan file (`$REPO_ROOT/.claude/avengers-{TIMESTAMP}-plan.md`) to reconstruct full mission context before doing anything else.

#### Step 3 — State reconciliation (run before routing checks)

Before checking pipeline routing, reconcile the state file against TaskList — this self-heals any missed STATE WRITEs:

```
TaskList() → for each task:
  if task.status == "in_progress" AND state_file shows agent as "idle":
    → update state_file agent status to "working"
  if task.status == "completed" AND state_file shows agent as "working":
    → update state_file agent status to "reviewing" (or "done" if already past review)
```

Write the corrected state file if any discrepancies were found. This ensures the dashboard is always accurate even if a STATE WRITE was skipped.

#### Step 4 — Run the full sweep

Read reconciled state file. For each agent:

| Agent state | Condition | Action |
|---|---|---|
| `working`/`reviewing` | matching task = `completed` in TaskList | Route to next pipeline stage immediately |
| `working` | no message since last sweep (90s) | Respawn with `-b` suffix — do NOT ping first |
| `idle` | natasha/banner/hawkeye awaiting routing | No action — they wait for Captain's signal |
| `idle` | coder lingering >1 sweep with no task | Send `shutdown_request` |
| `done` | — | No action |
| `blocked` | — | Resolve autonomously or write to state blocked map |

**Silence threshold**: 90 seconds = 1 sweep. If an agent hasn't progressed after 1 sweep → respawn. Do NOT give 2nd chances — a second nudge is wasted time.

**When ALL tasks completed + VALIDATED**: The monitoring sweep executes Phase 5, then Phase 5.5 (commit gate), then Phase 6.

**CRITICAL — commit gate applies here too**: The sweep must NOT commit autonomously. It MUST stop at Phase 5.5 and present the diff + proposed commit to the user, then wait. Do NOT write `"committing X files"` in the state file activity log — write `"MISSION COMPLETE — awaiting commit approval"` instead.

Inline cleanup sequence when sweep detects mission complete:
1. Write mission report to terminal (Phase 5 format)
2. Run Phase 5.5 commit gate — show diff, propose message, STOP and wait for user "go"
3. After user approves: spawn `thor-devops` exactly as described in Phase 5.5 — do NOT run `git add` or `git commit` directly from the sweep
4. After thor reports `COMMIT_PR_DONE`: proceed to Phase 6 cleanup
5. Phase 6 cleanup:
   - Send `shutdown_request` to every agent (read `~/.claude/teams/$TEAM_NAME/config.json`)
   - Force-delete team AND tasks: `rm -rf ~/.claude/teams/$TEAM_NAME ~/.claude/tasks/$TEAM_NAME`
   - Delete state file and plan: `rm -f $STATE_FILE && rm -f "${REPO_ROOT}/.claude/${TEAM_NAME}-plan.md"`
6. Cancel wakeup — do not re-arm ScheduleWakeup

#### Step 5 — Pipeline routing is also triggered by monitoring sweep

Do NOT wait only for messages from agents. On each sweep, also check:
- If any coder task shows `completed` in TaskList AND natasha hasn't been sent REVIEW yet → send REVIEW now
- If natasha shows `done` AND banner hasn't been sent TEST yet → send TEST now
- If banner shows `done` AND hawkeye hasn't been sent VALIDATE yet → send VALIDATE now

This means the pipeline advances even if Fury missed the COMPLETE message.

---

### Crashed / Stuck Agent Protocol

**Crash detection**: A subagent has crashed if:
- It receives a permission prompt inside its tab and hits `H.toolUseContext.getAppState is not a function`
- It goes silent for >3 turns after a task assignment with no COMPLETE/BLOCKED message
- User reports the agent tab is showing an error or is unresponsive

**On crash/stuck — kill and respawn immediately** (do NOT wait or retry the same session):

1. Skip `shutdown_request` — crashed session won't respond anyway
2. Update state file: set crashed agent `"status": "failed"`
3. Log: `{"who": "fury-captain", "msg": "Agent <name> crashed — respawning as <name-b>", "ts": <now>}`
4. Spawn replacement with `-b` suffix (`stark-senior-b`, `banner-tester-b`, etc.) using same Agent() prompt
5. TaskUpdate — reassign task to new owner
6. State file: new agent `"status": "working"`

**Root cause prevention**: Run Phase 1 Step 0 (pre-allowlist) BEFORE spawning any agents. Crashes are almost always caused by missing `permissions.allow` entries triggering prompts in subagent tabs.

---

### BLOCKED message from any agent

Parse for `QUESTION:` and `CHOICES:`.

- **Can Fury resolve autonomously?** → SendMessage answer directly; no blocked state written.
- **Needs human** → write blocked state; poll `$ANSWER_FILE` every 1-2 turns:

```bash
if [ -f /tmp/avengers-answer.json ]; then
  ANSWER=$(cat /tmp/avengers-answer.json)
  rm /tmp/avengers-answer.json
  echo "$ANSWER"
fi
```

Forward answer to blocked agent via SendMessage. Clear blocked state.

**5-minute fallback**: `AskUserQuestion` → forward answer via SendMessage.

**STATE WRITE 5 — Blocked**:
```json
"blocked": {
  "<codename>": {
    "question": "<question>",
    "context": "<why it matters>",
    "choices": ["<opt1>", "<opt2>"],
    "task_id": "<id>",
    "blocked_since": <now>
  }
}
```

**STATE WRITE 6 — Unblocked**: Remove blocked entry, agent back to `"working"`.

---

**STATE WRITE 4 — any pipeline event**: Re-write `$STATE_FILE` with updated agent status, task status, new activity entry. Do this after every REVIEW routing, TEST routing, VALIDATE routing, REWORK dispatch, and REVIEW_PASS/TEST_PASS/VALIDATED receipt.

---

## Phase 5 — Synthesize

Synthesize results from the COMPLETE messages received during this session (do NOT rely on TaskGet — it returns "no tasks found" after context shifts). Write a cohesive mission report from all results.

```
═══════════════════════════════════════
 MISSION REPORT
 <mission title — 1 line>
═══════════════════════════════════════

<Synthesized narrative — what was accomplished, key findings,
 files changed, decisions made, anything requiring follow-up>

Tasks:  ✓ <N> completed  /  ✗ <N> failed  /  ⚠ <N> partial
Agents: <comma-separated codenames>
═══════════════════════════════════════
```

Never silently drop failed tasks — always include them with ✗ in the report.

---

## Phase 5.5 — Git Commit Gate + Autonomous Commit/PR Agent

**HARD RULE: Never run `git commit`, `git push`, or `gh pr create` without explicit user approval first. This gate is non-negotiable.**

After the mission report, check for uncommitted changes:
```bash
git status --short
git diff HEAD -- <mission-relevant paths>
```

If no file changes (pure analysis mission): skip to Phase 6 directly.

**If there are changes — STOP and present this to the user:**

```
Files to commit:
  <each file — modified/new + 1-line description>

Proposed commit:
  git commit -m "<verb> <what> — <ticket>"

Saying **go** approves: stage → commit → push → PR (create or update existing).
No further prompts after go.
```

State file activity at this point: `"MISSION COMPLETE — awaiting commit approval"` (NOT "committing").

**After user says "go" / "commit" / "yes" — spawn `thor-devops` to execute autonomously:**

```
Agent(
  name="thor-devops",
  description="Thor — DevOps Engineer",
  team_name="avengers-{TIMESTAMP}",
  subagent_type="general-purpose",
  model="sonnet",
  prompt="""
You are Thor (DevOps Engineer) on team avengers-{TIMESTAMP}.
The user has given explicit approval to: stage + commit + push + create/update PR.
No further user prompts are needed — execute fully autonomously.

Repo: <REPO_ROOT>
Branch: <current branch>
Commit message: <exact message from Fury>
Files to stage: <exact list from Fury>

Steps — run in order, no prompting:

1. Stage the files:
   git add <file1> <file2> ... <fileN>

2. Commit:
   git commit -m "$(cat <<'EOF'
<commit message>
EOF
)"

3. Determine PR scenario:
   gh pr list --head <branch> --json number,state,title

   Scenario A — open or draft PR exists:
     git push origin <branch>
     → Report: "Pushed to existing PR #<N>: <title> — <URL>"

   Scenario B — no PR exists:
     git push -u origin <branch>
     gh pr create --title "<ticket>: <short summary>" --body "$(cat <<'BODY'
## Summary
<bullet points from commit — what changed and why>

## Test plan
- [ ] Validated by multi-agent audit (3 coders + reviewer + tester + hawkeye)
- [ ] All acceptance criteria PASS
BODY
)"
     → Report: "Created new PR: <URL>"

   Scenario C — PR exists but merged or closed:
     Same as Scenario B — push then create a new PR.

4. When done:
   SendMessage(to="fury-captain", summary="Commit and PR complete",
     message="COMMIT_PR_DONE | branch=<branch> | commit=<short sha> | pr=<URL> | scenario=<A/B/C>")

If anything fails (push rejected, gh auth error, etc.):
   SendMessage(to="fury-captain", "COMMIT_PR_FAILED | error=<exact error> | step=<which step>")
   Do NOT retry destructive operations — report and stop.

When shutdown_request arrives: SendMessage(to="fury-captain", message={"type":"shutdown_response","request_id":"<id>","approve":true})
"""
)
```

After thor reports `COMMIT_PR_DONE`: update state file activity with the PR URL, then proceed to Phase 6.
After `COMMIT_PR_FAILED`: report to user with exact error, ask how to proceed before continuing to Phase 6.

---

## Phase 6 — Cleanup (ALWAYS RUN)

Run in this exact order:

**Step 1 — Close iTerm2 agent tabs** (before sending shutdown — while sessions are still alive to receive it):
```bash
if [ -f "$STATE_FILE" ]; then
  AGENT_SESSIONS=$(python3 -c "import json; s=json.load(open('$STATE_FILE')); print(json.dumps(s.get('iterm2_sessions', [])))" 2>/dev/null || echo "[]")
  curl -sk -X POST https://avengers:2026/close-sessions \
    -H 'Content-Type: application/json' \
    -d "{\"session_ids\": $AGENT_SESSIONS}" >/dev/null 2>&1 || true
fi
```
If the bridge is not running or state file is gone, skips silently — tabs remain but mission still cleans up correctly.

**Step 2 — Send shutdown to every agent** (read config for member list):
```
SendMessage(to="<each-member-name>", summary="Shutdown", message={"type": "shutdown_request"})
```

**Step 3 — TeamDelete**. If it fails ("active members" error), force-delete both directories:
```bash
rm -rf ~/.claude/teams/avengers-{TIMESTAMP} ~/.claude/tasks/avengers-{TIMESTAMP}
```
Deleting `tasks/` is required — without it the agents stay in the `@` autocomplete list even after TeamDelete.

**Step 4 — STATE WRITE 7**: Delete state and plan files:
```bash
rm -f "$STATE_FILE"
rm -f "${REPO_ROOT}/.claude/avengers-${TIMESTAMP}-plan.md"
```

This clears the dashboard back to "Waiting for mission..." state.

Run this in ALL exit paths: normal completion, partial failure, user-cancelled. If the skill is interrupted before reaching this phase — re-enter with the monitoring wakeup prompt, it will detect mission complete and run cleanup inline.
