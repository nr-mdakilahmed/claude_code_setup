# Plugins

Plugins are **auto-installed** when you restart Claude Code after running `install.sh`.
The installer merges all plugin entries into your `~/.claude/settings.json` — CC picks them up on next start.

## Prerequisites

**NR-internal plugins** (`nr`, `nr-kafka`) require SSH access to the internal git server:
```bash
ssh -T git@source.datanerd.us   # should return: Hi <user>! You've authenticated...
```
If this fails, set up your SSH key with IT before proceeding.

## Plugin List

| Plugin | Marketplace | What it does |
|--------|-------------|--------------|
| `nr` | NR internal | New Relic MCP — NRQL, dashboards, alerts, entities |
| `nr-kafka` | NR internal | Kafka-specific MCP tools — topic analysis, lag investigation |
| `superpowers` | Official | Auto-loads all skills at session start (brainstorming, systematic-debugging, etc.) |
| `data-engineering` | Official | Airflow, dbt, OpenLineage, warehouse patterns |
| `terraform` | Official | Terraform registry lookups, provider/module docs |
| `coderabbit` | Official | AI code review via CodeRabbit |
| `code-review` | Official | PR code review skill |
| `pr-review-toolkit` | Official | Full PR review — code, tests, types, silent failures |
| `github` | Official | GitHub PR/issue management |
| `skill-creator` | Official | Create and modify skills |
| `security-guidance` | Official | Security review and vulnerability guidance |

Disabled by default (uncomment in settings.json to enable):
- `claude-code-setup` — guided CC setup wizard
- `ralph-loop` — loop-based agent patterns

## Fallback: Manual Install

If auto-install fails, run these inside Claude Code:

```
# Step 1 — Add NR internal marketplace (one-time)
/plugin marketplace add git@source.datanerd.us:commune/claude-plugin-marketplace.git

# Step 2 — Install NR plugins
/plugin install nr@claude-plugin-marketplace
/plugin install nr-kafka@claude-plugin-marketplace

# Step 3 — Install official plugins
/plugin install superpowers@claude-plugins-official
/plugin install data-engineering@claude-plugins-official
/plugin install terraform@claude-plugins-official
/plugin install coderabbit@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install pr-review-toolkit@claude-plugins-official
/plugin install github@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
```

## NR API Key Helper (optional)

The `apiKeyHelper` in settings.json points to the NR nerd-completion binary.
Ask your team lead for the install path — it provides automatic API key injection.
Once installed, add to your `~/.claude/settings.json`:
```json
"apiKeyHelper": "/opt/homebrew/bin/claude-nerd-completion"
```
