#!/bin/bash
# verify.sh — confirm install.sh succeeded and the CC environment is wired.
# Safe to re-run any time. Exits 0 on success, 1 if any check fails.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
fail=0

pass() { echo "  ✓ $1"; }
warn() { echo "  ⚠ $1"; }
fail() { echo "  ✗ $1"; fail=1; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     CC Team Setup — Verifying        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Prereqs ───────────────────────────────────────────────────────────────
echo "→ Prerequisites"
command -v claude   >/dev/null 2>&1 && pass "claude is installed"   || fail "claude not found (install Claude Code)"
command -v python3  >/dev/null 2>&1 && pass "python3 is installed"  || fail "python3 not found"
command -v git      >/dev/null 2>&1 && pass "git is installed"      || fail "git not found"
command -v jq       >/dev/null 2>&1 && pass "jq is installed"       || fail "jq not found (brew install jq)"
command -v pipx     >/dev/null 2>&1 && pass "pipx is installed"     || fail "pipx not found (brew install pipx)"
command -v uv       >/dev/null 2>&1 && pass "uv is installed"       || fail "uv not found (brew install uv)"
command -v rtk      >/dev/null 2>&1 && pass "rtk is installed (token savings on)" \
                                     || warn "rtk not installed (token-saving hook will skip filtering)"

# ── code-review-graph CLI ─────────────────────────────────────────────────
echo ""
echo "→ MCP servers"
if command -v code-review-graph >/dev/null 2>&1; then
  pass "code-review-graph installed ($(code-review-graph --version 2>&1 | head -1))"
else
  fail "code-review-graph not installed — run: pipx install code-review-graph"
fi

if [ -d "$REPO/mcp-servers/memory-server" ]; then
  if [ -f "$REPO/mcp-servers/memory-server/uv.lock" ]; then
    pass "memory-server ready (uv.lock present)"
  else
    warn "memory-server deps not synced — run: (cd $REPO/mcp-servers/memory-server && uv sync)"
  fi
else
  fail "memory-server source not found in repo"
fi

# ── Global config files ───────────────────────────────────────────────────
echo ""
echo "→ Global config"
for f in CLAUDE.md RTK.md settings.json budget.json; do
  [ -f "$CLAUDE/$f" ] && pass "$CLAUDE/$f" || fail "$CLAUDE/$f missing"
done

# ── State directories ─────────────────────────────────────────────────────
echo ""
echo "→ State directories"
for d in golden telemetry plans skills hooks; do
  [ -d "$CLAUDE/$d" ] && pass "$CLAUDE/$d/" || fail "$CLAUDE/$d/ missing"
done
[ -f "$CLAUDE/golden/index.json" ] && pass "golden/index.json" || warn "golden/index.json missing (auto-created on first /golden save)"

# ── Skills ────────────────────────────────────────────────────────────────
echo ""
echo "→ Skills"
expected_skills=0 found_skills=0 missing_skills=""
for dir in "$REPO/skills"/*/; do
  name=$(basename "$dir")
  [[ "$name" == "_template" ]] && continue
  expected_skills=$((expected_skills + 1))
  if [ -d "$CLAUDE/skills/$name" ]; then
    found_skills=$((found_skills + 1))
  else
    missing_skills="$missing_skills $name"
  fi
done
if [ "$found_skills" -eq "$expected_skills" ]; then
  pass "all $expected_skills skills installed"
else
  fail "$found_skills/$expected_skills skills installed — missing:$missing_skills"
fi

# ── Hooks ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Hooks"
for hook in "$REPO/hooks"/*; do
  name=$(basename "$hook")
  target="$CLAUDE/hooks/$name"
  if [ -f "$target" ]; then
    if [ -x "$target" ]; then pass "$name (executable)"
    else warn "$name exists but is not executable — run: chmod +x $target"
    fi
  else
    fail "$name missing at $target"
  fi
done

# ── settings.json contents ────────────────────────────────────────────────
echo ""
echo "→ settings.json"
if [ -f "$CLAUDE/settings.json" ]; then
  python3 - <<'EOF'
import json, os, sys
p = os.path.expanduser("~/.claude/settings.json")
d = json.load(open(p))
checks = [
    ("enabledPlugins",            lambda d: len(d.get("enabledPlugins", {})) >= 10),
    ("extraKnownMarketplaces",    lambda d: len(d.get("extraKnownMarketplaces", {})) >= 1),
    ("permissions.allow",         lambda d: len(d.get("permissions", {}).get("allow", [])) >= 30),
    ("hooks.PreToolUse",          lambda d: "PreToolUse" in d.get("hooks", {})),
    ("hooks.UserPromptSubmit",    lambda d: "UserPromptSubmit" in d.get("hooks", {})),
    ("hooks.PostToolUse",         lambda d: "PostToolUse" in d.get("hooks", {})),
    ("hooks.Stop",                lambda d: "Stop" in d.get("hooks", {})),
    ("Stop has ≥2 hooks",         lambda d: len(d.get("hooks", {}).get("Stop", [{}])[0].get("hooks", [])) >= 2),
]
failed = False
for label, test in checks:
    ok = False
    try: ok = test(d)
    except Exception: pass
    print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else "  ← missing or below threshold"))
    if not ok: failed = True
sys.exit(1 if failed else 0)
EOF
  if [ $? -eq 0 ]; then pass "all settings keys present"; else fail "settings.json keys missing — re-run ./install.sh"; fi
else
  fail "settings.json not found"
fi

# ── Memory MCP smoke test ─────────────────────────────────────────────────
echo ""
echo "→ Memory MCP server"
if [ -d "$REPO/mcp-servers/memory-server" ] && command -v uv >/dev/null 2>&1; then
  if (cd "$REPO/mcp-servers/memory-server" && uv run python -c "from memory_server.server import build_server, Config" >/dev/null 2>&1); then
    pass "memory-server imports clean"
  else
    warn "memory-server import failed — run: (cd $REPO/mcp-servers/memory-server && uv sync)"
  fi
fi

# ── Budget config ─────────────────────────────────────────────────────────
echo ""
echo "→ Budget"
if [ -f "$CLAUDE/budget.json" ]; then
  d=$(jq -r '.daily_cap_usd // 0' "$CLAUDE/budget.json" 2>/dev/null)
  w=$(jq -r '.weekly_cap_usd // 0' "$CLAUDE/budget.json" 2>/dev/null)
  m=$(jq -r '.monthly_cap_usd // 0' "$CLAUDE/budget.json" 2>/dev/null)
  if [ -n "$d" ] && [ "$d" != "null" ] && [ "$d" != "0" ]; then
    pass "caps: daily=\$$d, weekly=\$$w, monthly=\$$m"
  else
    warn "budget.json present but caps are 0 — run: /budget set --daily 75 --weekly 200 --monthly 700"
  fi
fi

# ── Plugins (only checkable after CC restart merges them) ─────────────────
echo ""
echo "→ Plugins (edit ~/.claude/settings.json to toggle)"
python3 - <<'PYEOF'
import json, os
p = os.path.expanduser("~/.claude/settings.json")
d = json.load(open(p))
plugins = d.get("enabledPlugins", {})
enabled  = sorted(k for k, v in plugins.items() if v)
disabled = sorted(k for k, v in plugins.items() if not v)
print(f"  ✓ Enabled  ({len(enabled)}): " + ", ".join(e.split('@')[0] for e in enabled))
if disabled:
    print(f"  ○ Disabled ({len(disabled)}): " + ", ".join(p.split('@')[0] for p in disabled))
PYEOF
warn "plugins install on CC restart — verify inside CC with: /plugin list"

# ── MCP servers (global + reminder about per-repo) ────────────────────────
echo ""
echo "→ MCP config"
if [ -f "$CLAUDE/.mcp.json" ]; then
  servers=$(/usr/bin/jq -r '.mcpServers | keys | join(", ")' "$CLAUDE/.mcp.json" 2>/dev/null)
  [ -n "$servers" ] && pass "global: $servers" || warn "global .mcp.json exists but has no servers"
else
  warn "no global ~/.claude/.mcp.json — CRG tools won't be available in non-repo sessions"
fi
warn "per-repo MCP (code-review-graph + memory) added by /bootstrap in each repo"

# ── SSH to NR internal (non-fatal) ────────────────────────────────────────
echo ""
echo "→ Optional — NR internal SSH"
if ssh -T -o BatchMode=yes -o ConnectTimeout=3 git@source.datanerd.us 2>&1 | grep -q "successfully authenticated"; then
  pass "SSH to source.datanerd.us works — NR plugins will install"
else
  warn "SSH to source.datanerd.us failed — NR-internal plugins (nr, nr-kafka) won't install"
  warn "  fix: set up your SSH key with IT, then run: ssh -T git@source.datanerd.us"
fi

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
if [ "$fail" -eq 0 ]; then
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ✓ All checks passed. Restart Claude Code to auto-install   ║"
  echo "║    plugins, then /bootstrap per-repo on first visit.         ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  exit 0
else
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ✗ Some checks failed. Review the output above and fix      ║"
  echo "║    before using CC. Re-run ./install.sh if needed.          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  exit 1
fi
