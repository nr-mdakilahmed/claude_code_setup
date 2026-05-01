#!/usr/bin/env bash
# log-grep-usage.sh — PostToolUse hook that logs every Grep/Glob call to
# ~/.claude/telemetry/greps.jsonl so we can audit "graph-first discipline".
#
# When Claude falls back to Grep/Glob, we want to know: which repo, what
# pattern, when. Weekly review answers "which of these could have been a
# graph query?" and informs CRG .code-review-graphignore tuning.
#
# Hook input (stdin, JSON): { tool_name, tool_input, session_id, ... }
# Hook output: non-blocking; errors are silent (telemetry is best-effort).

set -euo pipefail

LOG_DIR="$HOME/.claude/telemetry"
LOG_FILE="$LOG_DIR/greps.jsonl"
MAX_BYTES=10485760  # 10 MB — rotate at this threshold

mkdir -p "$LOG_DIR"

# Read hook payload
PAYLOAD=$(cat)

# Extract tool name; bail unless Grep or Glob
TOOL_NAME=$(echo "$PAYLOAD" | /usr/bin/jq -r '.tool_name // empty' 2>/dev/null || echo "")
[[ "$TOOL_NAME" != "Grep" && "$TOOL_NAME" != "Glob" ]] && exit 0

# Extract pattern + path (best-effort)
PATTERN=$(echo "$PAYLOAD" | /usr/bin/jq -r '.tool_input.pattern // .tool_input.query // empty' 2>/dev/null || echo "")
SEARCH_PATH=$(echo "$PAYLOAD" | /usr/bin/jq -r '.tool_input.path // empty' 2>/dev/null || echo "")
SESSION_ID=$(echo "$PAYLOAD" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null || echo "")

# Detect current repo
REPO_ROOT=$(cd "$(pwd)" 2>/dev/null && /usr/bin/git rev-parse --show-toplevel 2>/dev/null || echo "")
REPO_NAME=$(basename "${REPO_ROOT:-$(pwd)}")

# Detect whether a CRG graph exists for this repo — if yes, this Grep is a
# "fallback" (graph should have answered first). If no, it's expected.
CRG_EXISTS="false"
[[ -n "$REPO_ROOT" && -d "$REPO_ROOT/.code-review-graph" ]] && CRG_EXISTS="true"

# Emit one JSONL line
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
/usr/bin/jq -n -c \
  --arg ts "$TIMESTAMP" \
  --arg tool "$TOOL_NAME" \
  --arg pattern "$PATTERN" \
  --arg path "$SEARCH_PATH" \
  --arg session "$SESSION_ID" \
  --arg repo "$REPO_NAME" \
  --argjson crg "$CRG_EXISTS" \
  '{ts: $ts, tool: $tool, pattern: $pattern, path: $path, session: $session, repo: $repo, crg_available: $crg, fallback: $crg}' \
  >> "$LOG_FILE" 2>/dev/null || true

# Rotate if oversized (keep previous as .1)
if [[ -f "$LOG_FILE" ]]; then
  SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
  if (( SIZE > MAX_BYTES )); then
    mv "$LOG_FILE" "${LOG_FILE}.1" 2>/dev/null || true
    : > "$LOG_FILE"
  fi
fi

exit 0
