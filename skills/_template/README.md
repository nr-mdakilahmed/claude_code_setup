# Skill Authoring Template — Usage Notes

This directory holds the canonical template every skill in `~/.claude/skills/` follows. The leading underscore in `_template` keeps Claude Code from discovering it as a real skill.

## What grounds this template

- Anthropic overview — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic best-practices — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Claude Code skills docs — https://code.claude.com/docs/en/skills
- Karpathy style — https://github.com/forrestchang/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines/SKILL.md

## The three disclosure levels (why the template is shaped this way)

1. **Level 1 — Metadata** (always in system prompt): `name` + `description` + `when_to_use`. Combined listing cap is 1,536 chars. This is the entire trigger surface — Claude never sees the body at discovery time.
2. **Level 2 — Body** (loaded on trigger): SKILL.md body, ≤500 lines per Anthropic, target under 5k tokens. Every line competes with conversation history once loaded.
3. **Level 3 — Depth** (lazy): `references/*.md` and `scripts/*.sh` read or executed only when needed. Zero per-invocation cost.

## Frontmatter rules

| Field | Required | Rule |
|---|---|---|
| `name` | yes | Lowercase letters, numbers, hyphens. ≤64 chars. No "anthropic"/"claude". Prefer gerund form (`writing-python`, `configuring-cicd`). Noun phrases OK. |
| `description` | yes | ≤1024 chars. Third person only ("Processes Excel files", not "I can help"). Include WHAT + WHEN. Front-load the key use case — descriptions get truncated in listings. |
| `when_to_use` | no | Extra trigger phrases. Counts toward 1,536-char listing cap. |
| `paths` | no | Glob list. Auto-triggers the skill when Claude edits matching files. Use for domain skills with clear file patterns. |
| `allowed-tools` | no | Space-separated or YAML list. Pre-approves tools while skill is active. |
| `disable-model-invocation` | no | `true` for skills that should only fire on explicit `/name` — side-effectful workflows, Opus-routed skills, anything the user alone should start. |
| `model` | no | `inherit`, `haiku`, `sonnet`, `opus`. Route cost per skill. |
| `effort` | no | `low`, `medium`, `high`, `xhigh`, `max`. |

## The three-cut rubric (apply to every line in the body)

1. **Behavior test**: Does this line change Claude's output? If Claude already behaves this way by default, cut. ("Python uses type hints for readability" → cut. "Prefer `pathlib` over `os.path`; reject PRs using the old style" → keep.)
2. **Frequency test**: Consulted on most invocations, or only sometimes? "Sometimes" → move to `references/`.
3. **Freedom test**: Content style matches declared freedom level?

## Degrees of freedom (central authoring concept from Anthropic)

Match specificity to task fragility:

| Tier | Use when | Content character |
|---|---|---|
| **High** | Multiple approaches are valid. Decisions depend on context. Heuristics guide. | Behavioral principles. Claude chooses tactics. |
| **Medium** | A preferred pattern exists. Some variation is acceptable. Configuration affects behavior. | Templates with decision tables. Claude picks between known options. |
| **Low** | Operations are fragile. Consistency is critical. A specific sequence must run. | Exact commands or script invocations. Claude follows steps. |

Anthropic's analogy: narrow bridge with cliffs (low freedom — specific guardrails) vs open field (high freedom — general direction).

## When to create references/ vs keep inline

Create a `references/` file only when **one** of these holds:

- The topic earns more than ~80 lines after the 3-cut rule is applied.
- The content is domain- or scenario-specific (Pattern 2: BigQuery's `finance.md` + `sales.md` + `product.md` — only one is needed at a time).
- Content is a full worked example (a complete Dockerfile, DAG, Terraform module) that is copy-paste ready.

Do not create a reference file because "this skill should have one." Create it because specific content passed the frequency test and moved out.

**Rules for reference files**:
- Named in kebab-case: `salting-patterns.md`, `k8s-log-protocol.md`.
- Linked **one level deep only** from SKILL.md. Never chain ref → ref → ref. Claude may preview nested files with `head -100` and miss content.
- If >100 lines, the file **must** start with a table of contents. Example:

```markdown
# Advanced NRQL Functions

## Contents
- Funnel queries
- Histogram bucketing
- Eventstream replay
- Worked examples

## Funnel queries
...
```

## When to create scripts/ vs keep bash inline

Create a script only when **one** of these holds:

- The existing inline bash block is more than ~15 lines.
- The same sequence is invoked from multiple places in the skill.
- Regenerating the logic each turn is more expensive than a single parameterized run.

Skills that currently meet the bar: bootstrap, wrap-up, graphify, airflow, mcp-builder, shell, openmetadata.

**Rules for scripts**:
- Shebang `#!/usr/bin/env bash` + `set -euo pipefail`.
- Accept arguments. No hidden state. Idempotent.
- `--help` returns 0.
- `bash -n script.sh` passes syntax check.
- Claude invokes the script via one SKILL.md line; the script body never enters context.

## Body structure (required vs optional sections)

| Section | Required when |
|---|---|
| Purpose (2 lines under title) | Always |
| Freedom level statement | Always |
| Numbered principles (3–5) | Always |
| Quick reference (≤5-row table or short flowchart) | Always — this is the single lookup Claude consults each invocation |
| Workflow checklist | Multi-step skills only (bootstrap, wrap-up, graphify, demo) |
| Feedback loop | Skills with validation (cicd, docker, terraform, bootstrap) |
| Anti-patterns (≤7 rows) | Coding and infra skills |
| Troubleshooting (≤10 rows) | Coding and infra skills where real failure modes change behavior |
| References | Any skill with depth content |
| Cross-references | When the skill overlaps another |

## Authoring voice

- **Third person always** in frontmatter descriptions.
- **Imperative in the body** ("Prefer pathlib", "Reject PRs that …").
- **Bold one-liner under each principle header** captures the rule in Karpathy style.
- **A → B transforms** when a rule needs an example ("Add validation" → "Write tests for invalid inputs, then make them pass").
- **No prose paragraphs**. If it can't be a bullet or bold line, it's probably explanatory — cut or move to references.

## Verification checklist (run before committing any rewrite)

- [ ] `wc -l SKILL.md` ≤ 500 (Anthropic cap).
- [ ] Description length: `python3 -c "import yaml,sys; d=yaml.safe_load(open('SKILL.md').read().split('---')[1]); print(len(d['description']))"` ≤ 1024.
- [ ] Description + when_to_use combined ≤ 1,536.
- [ ] Description is third person (no "I", "you", "we").
- [ ] Name uses lowercase + hyphens, no "anthropic"/"claude", ≤64 chars.
- [ ] Freedom level declared and matches content style.
- [ ] Every principle is an action-directing bullet, not a topic heading.
- [ ] `head -20 references/*.md` shows TOC for any file >100 lines.
- [ ] References are not cross-linked — grep `\]\(.*\.md\)` inside references, should not hit other references.
- [ ] All scripts: `bash -n *.sh` passes, `--help` returns 0.
- [ ] Trigger test: one realistic prompt fires the skill; one adjacent prompt does not.
- [ ] Smoke task: one real invocation on a realistic target produces the expected behavior.

## What this template does not enforce

- Line or character targets below the 500-line cap. Length is the output of the 3-cut discipline, not an input.
- Specific number of references or scripts. Zero is fine if the content doesn't earn them.
- A fixed set of section headers. The required ones are listed above; skills may omit optional ones.
