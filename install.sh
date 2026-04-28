#!/bin/bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     CC Team Setup — Installing       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Pre-flight — fail fast with a clear message if prerequisites are missing ──
missing=0
check_cmd() {
  local cmd="$1" hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "  ✗ $cmd not found — $hint"
    missing=1
  else
    echo "  ✓ $cmd ($(command -v "$cmd"))"
  fi
}
echo "→ Checking prerequisites..."
check_cmd claude  "install Claude Code first: https://docs.claude.com/claude-code"
check_cmd python3 "install with: brew install python3  (or system Python 3.8+)"
check_cmd git     "install with: brew install git"
if [ "$missing" -eq 1 ]; then
  echo ""
  echo "  Install the missing prerequisites above, then re-run ./install.sh"
  exit 1
fi
# Non-fatal warnings
if ! command -v rtk >/dev/null 2>&1; then
  echo "  ⚠ rtk not found — token-saving hook will run but skip filtering"
  echo "    (ask your team lead for the RTK install link)"
fi
if ! ssh -T -o BatchMode=yes -o ConnectTimeout=3 git@source.datanerd.us 2>&1 | grep -q "successfully authenticated"; then
  echo "  ⚠ SSH access to source.datanerd.us not verified — NR-internal plugins may fail to install"
  echo "    (run: ssh -T git@source.datanerd.us  to test)"
fi
echo ""

# Ensure ~/.claude dirs exist
mkdir -p "$CLAUDE/skills" "$CLAUDE/hooks"

# ── Skills ────────────────────────────────────────────────────────────────────
echo "→ Installing skills..."
for dir in "$REPO/skills"/*/; do
  name=$(basename "$dir")
  target="$CLAUDE/skills/$name"
  if [ -d "$target" ] && [ ! -L "$target" ]; then
    echo "  skip $name (local version exists — not overwriting)"
  else
    # Remove stale symlink if present, then copy fresh
    [ -L "$target" ] && rm "$target"
    cp -r "$dir" "$target"
    echo "  ✓ $name"
  fi
done

# ── Hooks ─────────────────────────────────────────────────────────────────────
echo ""
echo "→ Installing hooks..."
for file in "$REPO/hooks"/*; do
  name=$(basename "$file")
  target="$CLAUDE/hooks/$name"
  if [ -f "$target" ] && [ ! -L "$target" ]; then
    cp "$target" "${target}.bak"
    echo "  backed up existing $name → ${name}.bak"
  fi
  [ -L "$target" ] && rm "$target"
  cp "$file" "$target"
  echo "  ✓ $name"
done
chmod +x "$CLAUDE/hooks"/*.py "$CLAUDE/hooks"/*.sh 2>/dev/null || true

# ── CLAUDE.md + RTK.md ────────────────────────────────────────────────────────
echo ""
echo "→ Installing config files..."
for fname in CLAUDE.md RTK.md; do
  target="$CLAUDE/$fname"
  if [ -f "$target" ] && [ ! -L "$target" ]; then
    cp "$target" "${target}.bak"
    echo "  backed up existing $fname"
  fi
  [ -L "$target" ] && rm "$target"
  cp "$REPO/$fname" "$target"
  echo "  ✓ $fname"
done

# ── settings.json ─────────────────────────────────────────────────────────────
echo ""
echo "→ Merging settings.json..."
if [ ! -f "$CLAUDE/settings.json" ]; then
  cp "$REPO/settings.template.json" "$CLAUDE/settings.json"
  echo "  ✓ created settings.json from template"
else
  python3 "$REPO/scripts/merge-settings.py" \
    "$REPO/settings.template.json" "$CLAUDE/settings.json"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Done! Restart Claude Code to apply all changes.            ║"
echo "║                                                              ║"
echo "║  On restart, Claude Code will auto-install all plugins.     ║"
echo "║  NR plugins require SSH access to source.datanerd.us        ║"
echo "║                                                              ║"
echo "║  First time on a repo? Run: /bootstrap                      ║"
echo "║  End of every session?   Run: /wrap-up                      ║"
echo "║  Complex task?           Run: /avengers                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  To update later:"
echo "    cd $REPO && git pull && ./install.sh"
echo ""
