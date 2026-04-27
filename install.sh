#!/bin/bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     CC Team Setup — Installing       ║"
echo "╚══════════════════════════════════════╝"
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
