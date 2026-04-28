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
command -v rtk      >/dev/null 2>&1 && pass "rtk is installed (token savings on)" \
                                     || warn "rtk not installed (token-saving hook will skip filtering)"

# ── Global config files ───────────────────────────────────────────────────
echo ""
echo "→ Global config"
for f in CLAUDE.md RTK.md settings.json; do
  [ -f "$CLAUDE/$f" ] && pass "$CLAUDE/$f" || fail "$CLAUDE/$f missing"
done

# ── Skills ────────────────────────────────────────────────────────────────
echo ""
echo "→ Skills"
expected_skills=0 found_skills=0 missing_skills=""
for dir in "$REPO/skills"/*/; do
  expected_skills=$((expected_skills + 1))
  name=$(basename "$dir")
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
    ("enabledPlugins",      lambda d: len(d.get("enabledPlugins", {})) >= 10),
    ("extraKnownMarketplaces", lambda d: len(d.get("extraKnownMarketplaces", {})) >= 1),
    ("permissions.allow",   lambda d: len(d.get("permissions", {}).get("allow", [])) >= 30),
    ("hooks.PreToolUse",    lambda d: "PreToolUse" in d.get("hooks", {})),
    ("hooks.UserPromptSubmit", lambda d: "UserPromptSubmit" in d.get("hooks", {})),
    ("hooks.Stop",          lambda d: "Stop" in d.get("hooks", {})),
]
for label, test in checks:
    ok = False
    try: ok = test(d)
    except Exception: pass
    print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else "  ← missing or below threshold"))
    if not ok: sys.exit(1)
EOF
  if [ $? -eq 0 ]; then pass "all settings keys present"; else fail "settings.json keys missing — re-run ./install.sh"; fi
else
  fail "settings.json not found"
fi

# ── Plugins (only checkable after CC restart merges them) ─────────────────
echo ""
echo "→ Plugins"
plugin_count=$(python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.claude/settings.json'))); print(len(d.get('enabledPlugins',{})))" 2>/dev/null || echo 0)
if [ "$plugin_count" -ge 10 ]; then
  pass "$plugin_count plugins listed in settings.json (auto-install on CC restart)"
else
  fail "only $plugin_count plugins in settings.json — expected ≥10"
fi
warn "plugins install on CC restart — verify inside CC with: /plugin list"

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
  echo "║    plugins, then verify inside CC with: /plugin list        ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  exit 0
else
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ✗ Some checks failed. Review the output above and fix      ║"
  echo "║    before using CC. Re-run ./install.sh if needed.          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  exit 1
fi
