#!/usr/bin/env bash
# start.sh — one command to start everything:
#   1. Install tmux if missing
#   2. bridge.py (background, port 2026)
#   3. Claude Code in tmux session 'cc'
#   4. Opens dashboard in browser

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE_PY="$SCRIPT_DIR/bridge.py"
CERTS_DIR="$SCRIPT_DIR/certs"
BRIDGE_PORT=2026
DASHBOARD_URL="https://avengers:2026/"
TMUX_SESSION="cc"

# Ensure Homebrew is on PATH (needed when script runs outside login shell)
eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true

# ── 0. Install tmux if missing ────────────────────────────────────────────────
if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found — installing via Homebrew..."
  brew install tmux
fi

# ── 0b. Ensure /etc/hosts entry for avengers ─────────────────────────────────
if ! grep -q 'avengers' /etc/hosts 2>/dev/null; then
  echo "Adding 127.0.0.1 avengers to /etc/hosts (requires sudo once)..."
  sudo sh -c 'echo "127.0.0.1 avengers" >> /etc/hosts'
  echo "Done."
fi

# ── 0c. Set up TLS certs via mkcert (one-time) ───────────────────────────────
if ! command -v mkcert >/dev/null 2>&1; then
  echo "Installing mkcert..."
  brew install mkcert
fi
mkdir -p "$CERTS_DIR"
if [ ! -f "$CERTS_DIR/avengers.pem" ]; then
  echo "Generating TLS cert for avengers (one-time)..."
  mkcert -install 2>/dev/null || true
  mkcert -cert-file "$CERTS_DIR/avengers.pem" -key-file "$CERTS_DIR/avengers-key.pem" avengers
  echo "Cert generated → $CERTS_DIR/"
fi

# ── 1. Start bridge if not already running ───────────────────────────────────
if lsof -ti:"$BRIDGE_PORT" >/dev/null 2>&1; then
  echo "Bridge already running on port $BRIDGE_PORT"
else
  echo "Starting bridge..."
  nohup python3 "$BRIDGE_PY" > /tmp/avengers-bridge.log 2>&1 &
  for i in 1 2 3 4 5; do
    sleep 0.5
    lsof -ti:"$BRIDGE_PORT" >/dev/null 2>&1 && break
  done
  echo "Bridge started → http://avengers:${BRIDGE_PORT}/"
fi

# ── 2. Start Claude Code in tmux ─────────────────────────────────────────────
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  echo "tmux session '$TMUX_SESSION' already exists"
else
  echo "Starting Claude Code in tmux session '$TMUX_SESSION'..."
  tmux new-session -d -s "$TMUX_SESSION"
  tmux send-keys -t "$TMUX_SESSION" "command claude" Enter
  sleep 1
fi

# ── 3. Open dashboard ─────────────────────────────────────────────────────────
echo "Opening dashboard..."
if command -v open >/dev/null 2>&1; then
  open "$DASHBOARD_URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$DASHBOARD_URL"
fi

echo ""
echo "Done!"
echo "  Dashboard: $DASHBOARD_URL"
echo "  Claude:    tmux attach -t $TMUX_SESSION"
echo "  Bridge log: tail -f /tmp/avengers-bridge.log"
