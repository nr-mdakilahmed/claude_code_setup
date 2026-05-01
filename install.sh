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

check_cmd_optional() {
  local cmd="$1" hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "  ⚠ $cmd not found — $hint"
  else
    echo "  ✓ $cmd ($(command -v "$cmd"))"
  fi
}

echo "→ Checking prerequisites..."
check_cmd claude  "install Claude Code first: https://docs.claude.com/claude-code"
check_cmd python3 "install with: brew install python3  (or system Python 3.10+)"
check_cmd git     "install with: brew install git"
check_cmd jq      "install with: brew install jq  (required for hooks + budget)"
check_cmd pipx    "install with: brew install pipx && pipx ensurepath"
check_cmd uv      "install with: brew install uv  (needed for memory-server)"
if [ "$missing" -eq 1 ]; then
  echo ""
  echo "  Install the missing prerequisites above, then re-run ./install.sh"
  exit 1
fi

# Optional (non-fatal)
check_cmd_optional rtk "token-saving hook will skip filtering without it"
check_cmd_optional code-review-graph "will install via pipx in a moment"

if ! ssh -T -o BatchMode=yes -o ConnectTimeout=3 git@source.datanerd.us 2>&1 | grep -q "successfully authenticated"; then
  echo "  ⚠ SSH access to source.datanerd.us not verified — NR-internal plugins may fail to install"
  echo "    (run: ssh -T git@source.datanerd.us  to test)"
fi
echo ""

# Ensure ~/.claude dirs exist
mkdir -p "$CLAUDE/skills" "$CLAUDE/hooks" "$CLAUDE/golden" "$CLAUDE/telemetry" "$CLAUDE/plans"

# ── code-review-graph MCP server (per-repo graph) ─────────────────────────────
echo "→ Installing code-review-graph (Tree-sitter + 28 MCP tools)..."
if command -v code-review-graph >/dev/null 2>&1; then
  echo "  ✓ already installed ($(code-review-graph --version 2>&1 | head -1))"
else
  pipx install code-review-graph 2>&1 | tail -3 | sed 's/^/  /'
fi

# ── Memory MCP server (per-project pull-on-demand memory) ────────────────────
echo ""
echo "→ Installing memory-server MCP..."
if [ -d "$REPO/mcp-servers/memory-server" ]; then
  (
    cd "$REPO/mcp-servers/memory-server" && uv sync 2>&1 | tail -3 | sed 's/^/  /'
  )
  echo "  ✓ memory-server ready for uvx invocation"
else
  echo "  ⚠ mcp-servers/memory-server/ not in repo — skipping"
fi

# ── Skills ────────────────────────────────────────────────────────────────────
echo ""
echo "→ Installing skills..."
for dir in "$REPO/skills"/*/; do
  name=$(basename "$dir")
  [[ "$name" == "_template" ]] && continue
  target="$CLAUDE/skills/$name"
  if [ -d "$target" ] && [ ! -L "$target" ]; then
    echo "  skip $name (local version exists — not overwriting)"
  else
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

# ── Budget config + golden index (seed if missing) ────────────────────────────
echo ""
echo "→ Seeding budget + golden index..."
if [ ! -f "$CLAUDE/budget.json" ]; then
  cat > "$CLAUDE/budget.json" <<'EOF'
{
  "daily_cap_usd": 75,
  "weekly_cap_usd": 200,
  "monthly_cap_usd": 700,
  "auto_downshift_pct": 80,
  "hard_warn_pct": 100,
  "note": "Run /budget set --daily <N> --weekly <N> --monthly <N> to adjust."
}
EOF
  echo "  ✓ budget.json (daily=\$75, weekly=\$200, monthly=\$700 — tune with /budget set)"
else
  echo "  skip budget.json (exists)"
fi

if [ ! -f "$CLAUDE/golden/index.json" ]; then
  echo '{"goldens": [], "version": "1.0"}' > "$CLAUDE/golden/index.json"
  echo "  ✓ golden/index.json"
fi

# ── Global MCP config (code-review-graph) ─────────────────────────────────────
echo ""
echo "→ Configuring global MCP (code-review-graph)..."
MCP_GLOBAL="$CLAUDE/.mcp.json"
if command -v code-review-graph >/dev/null 2>&1; then
  if [ -f "$MCP_GLOBAL" ] && /usr/bin/jq -e '.mcpServers["code-review-graph"]' "$MCP_GLOBAL" >/dev/null 2>&1; then
    echo "  skip (already configured)"
  else
    CRG_ENTRY='{"command":"uvx","args":["code-review-graph","serve"],"type":"stdio"}'
    if [ -f "$MCP_GLOBAL" ]; then
      TMP=$(mktemp)
      /usr/bin/jq --argjson e "$CRG_ENTRY" '.mcpServers["code-review-graph"] = $e' "$MCP_GLOBAL" > "$TMP"
      mv "$TMP" "$MCP_GLOBAL"
      echo "  ✓ merged code-review-graph into $MCP_GLOBAL"
    else
      echo "{\"mcpServers\":{\"code-review-graph\":$CRG_ENTRY}}" | /usr/bin/jq . > "$MCP_GLOBAL"
      echo "  ✓ created $MCP_GLOBAL with code-review-graph"
    fi
  fi
else
  echo "  ⚠ code-review-graph not available — skipping global MCP config"
fi

# ── Plugin status summary ─────────────────────────────────────────────────────
echo ""
echo "→ Plugin status (edit ~/.claude/settings.json to toggle):"
python3 - <<'PYEOF'
import json, os
p = os.path.expanduser("~/.claude/settings.json")
d = json.load(open(p))
plugins = d.get("enabledPlugins", {})
enabled  = sorted(k for k, v in plugins.items() if v)
disabled = sorted(k for k, v in plugins.items() if not v)
print(f"  ✓ Enabled  ({len(enabled)}):")
for p in enabled:
    print(f"      {p.split('@')[0]}  ({p.split('@')[1] if '@' in p else 'local'})")
if disabled:
    print(f"  ○ Disabled ({len(disabled)}):")
    for p in disabled:
        print(f"      {p.split('@')[0]}  ({p.split('@')[1] if '@' in p else 'local'})")
PYEOF

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Done! Restart Claude Code to apply all changes.            ║"
echo "║                                                              ║"
echo "║  On restart, Claude Code will auto-install all plugins.     ║"
echo "║  NR plugins require SSH access to source.datanerd.us        ║"
echo "║                                                              ║"
echo "║  Core workflow:                                              ║"
echo "║    First visit per repo:  /bootstrap                         ║"
echo "║    Every session end:     /wrap-up                           ║"
echo "║    Complex parallel work: /avengers                          ║"
echo "║    After validated win:   /golden save <slug>                ║"
echo "║    Hit familiar problem:  /replay <slug>                     ║"
echo "║    Spend awareness:       /budget status                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  To update later:"
echo "    cd $REPO && git pull && ./install.sh"
echo ""
