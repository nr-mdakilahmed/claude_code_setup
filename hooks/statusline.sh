#!/bin/bash

# Claude Code Status Line
# Reads rich JSON from native `statusLine` config (stdin), NOT a Stop hook.
#
# Wide (100+):  🧠 Sonnet 4.6 │ ●●○○○ 67% 103k/200k │ 💰 $11 │ 📅 $8 │ 📂 project │ 🌿 main
# Narrow (50+): 🧠 Sonnet 4.6 │ ● 67% 103k/200k │ 💰 $11 │ 📂 project │ 🌿 main
# Tiny (<50):   🧠 Sonnet 4.6 │ ● 67% │ 💰 $11

input=$(cat)

# Uncomment to debug: echo "$input" > /tmp/statusline-input.json

model_display=$(echo "$input" | jq -r '.model.display_name // "Claude"')
pct_int=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

# current_usage is an object — sum input + cache tokens (output doesn't consume context window)
used_tokens=$(echo "$input" | jq -r '
  (.context_window.current_usage.input_tokens // 0) +
  (.context_window.current_usage.cache_creation_input_tokens // 0) +
  (.context_window.current_usage.cache_read_input_tokens // 0)
')

# Actual context window size field (not "max_size")
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000' | cut -d. -f1)

cost_usd=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')

# Ensure integers
[[ "$used_tokens" =~ ^[0-9]+$ ]] || used_tokens=0
[[ "$ctx_size"    =~ ^[0-9]+$ ]] || ctx_size=200000
[[ "$pct_int"     =~ ^[0-9]+$ ]] || pct_int=0

# Strip "Claude " prefix for compact display (e.g. "Claude Sonnet 4.6" → "Sonnet 4.6")
model_display="${model_display#Claude }"

# Format token counts
if [ "$used_tokens" -ge 1000000 ]; then
    tokens_fmt="$((used_tokens / 1000000))M"
else
    tokens_fmt="$((used_tokens / 1000))k"
fi
if [ "$ctx_size" -ge 1000000 ]; then
    ctx_fmt="$((ctx_size / 1000000))M"
else
    ctx_fmt="$((ctx_size / 1000))k"
fi

# Daily cost — call NR MCP server directly (same OAuth token used by Claude Code),
# falls back to JSONL if token missing or request fails. Cached 5 min.
today=$(date +%Y-%m-%d)
daily_cache="/tmp/claude_daily_${today}.cost"
now_ts=$(date +%s)
recalc=1
if [ -f "$daily_cache" ]; then
    cache_ts=$(stat -f %m "$daily_cache" 2>/dev/null || echo 0)
    [ $((now_ts - cache_ts)) -lt 300 ] && recalc=0
fi
if [ "$recalc" -eq 1 ]; then
    daily_usd=$(python3 - <<'PYEOF' 2>/dev/null
import json, subprocess, os, datetime, urllib.request, urllib.error, glob

today = datetime.date.today().isoformat()
NR_ACCOUNT  = int(os.environ.get("NR_ACCOUNT_ID", "12700570"))
MCP_URL     = os.environ.get("NR_MCP_URL", "https://mcp-stg.staging-service.nr-ops.net/mcp/")

# ── NR via MCP HTTP (no NerdGraph key needed — reuses Claude Code OAuth) ───
def nr_daily_cost():
    try:
        raw = subprocess.check_output(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            stderr=subprocess.DEVNULL,
        )
        creds = json.loads(raw.decode())
    except Exception:
        return None

    access_token = None
    for entry in creds.get("mcpOAuth", {}).values():
        if "nr-mcp-server" in entry.get("serverName", ""):
            access_token = entry.get("accessToken")
            break
    if not access_token:
        return None

    # User email: env override → git config → $USER@newrelic.com
    user_email = os.environ.get("NR_USER_EMAIL", "")
    if not user_email:
        try:
            user_email = subprocess.check_output(
                ["git", "config", "--global", "user.email"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except Exception:
            pass
    if not user_email:
        user_email = f"{os.environ.get('USER', 'unknown')}@newrelic.com"

    nrql = (
        f"SELECT sum(claude_code.cost.usage) AS cost FROM Metric "
        f"WHERE metricName = 'claude_code.cost.usage' AND username = '{user_email}' "
        f"SINCE today"
    )
    payload = json.dumps({
        "jsonrpc": "2.0", "id": "1", "method": "tools/call",
        "params": {
            "name": "execute_nrql_query",
            "arguments": {"nrql_query": nrql, "account_id": NR_ACCOUNT}
        }
    }).encode()

    try:
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json, text/event-stream",
            },
        )
        resp = urllib.request.urlopen(req, timeout=5)
        body = json.loads(resp.read())
        rows = (
            body.get("result", {})
                .get("structuredContent", {})
                .get("result", {})
                .get("data", {})
                .get("actor", {})
                .get("account", {})
                .get("nrql", {})
                .get("results", [])
        )
        if rows:
            return float(rows[0].get("cost") or 0)
    except Exception:
        pass
    return None

# ── JSONL fallback ─────────────────────────────────────────────────────────
def jsonl_daily_cost():
    def cost(u, model):
        m = model.lower()
        if   'opus'  in m: p = (15.00, 75.00, 18.75, 1.50)
        elif 'haiku' in m: p = (0.80,   4.00,  1.00, 0.08)
        else:              p = (3.00,  15.00,  3.75, 0.30)
        return (
            (u.get('input_tokens', 0) or 0) * p[0] +
            (u.get('output_tokens', 0) or 0) * p[1] +
            (u.get('cache_creation_input_tokens', 0) or 0) * p[2] +
            (u.get('cache_read_input_tokens', 0) or 0) * p[3]
        ) / 1_000_000
    total = 0.0
    for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True):
        try:
            with open(f, errors='replace') as fh:
                for line in fh:
                    try:
                        d = json.loads(line.strip())
                        if d.get('timestamp', '')[:10] != today: continue
                        msg = d.get('message') or {}
                        u = msg.get('usage')
                        if not isinstance(u, dict): continue
                        total += cost(u, msg.get('model', ''))
                    except: pass
        except: pass
    return total

result = nr_daily_cost()
if result is None:
    result = jsonl_daily_cost()
print(f'{result:.4f}')
PYEOF
    )
    echo "${daily_usd:-0}" > "$daily_cache"
else
    daily_usd=$(cat "$daily_cache")
fi

# Terminal width
cols=${SL_COLS:-$(tput cols 2>/dev/null || echo 120)}

# Colors
GREEN="\033[38;2;90;120;80m"
YELLOW="\033[38;2;150;120;40m"
RED="\033[38;2;150;55;40m"
TEAL="\033[38;2;65;115;120m"
ORANGE="\033[38;2;140;110;70m"
BLUE="\033[38;2;90;110;130m"
FG="\033[38;2;140;135;120m"
DIM="\033[38;2;75;70;65m"
RESET="\033[0m"
S=" ${DIM}│${RESET} "

[[ "$pct_int" =~ ^[0-9]+$ ]] || pct_int=0

if   [ "$pct_int" -le 60 ]; then pct_color="$GREEN"
elif [ "$pct_int" -le 80 ]; then pct_color="$YELLOW"
else                              pct_color="$RED"
fi

status=""

# 1. Model (always)
status+=$(printf "🧠 ${TEAL}%s${RESET}" "$model_display")

# 2. Context bar
if [ "$cols" -ge 80 ]; then
    bar=""
    for i in {0..4}; do
        midpoint=$(( i * 20 + 10 ))
        if [ "$pct_int" -ge "$midpoint" ]; then bar+="${pct_color}●${RESET}"
        else                                     bar+="${DIM}○${RESET}"
        fi
    done
    status+=$(printf "%b%b ${pct_color}%s%%${RESET} ${DIM}%s/%s${RESET}" "$S" "$bar" "$pct_int" "$tokens_fmt" "$ctx_fmt")
elif [ "$cols" -ge 50 ]; then
    status+=$(printf "%b${pct_color}● %s%%${RESET} ${DIM}%s/%s${RESET}" "$S" "$pct_int" "$tokens_fmt" "$ctx_fmt")
else
    status+=$(printf "%b${pct_color}● %s%%${RESET}" "$S" "$pct_int")
fi

# 3. Session cost
if [ -n "$cost_usd" ] && [ "$cost_usd" != "0" ] && [ "$cost_usd" != "null" ]; then
    cost_int=$(printf "%.0f" "$cost_usd" 2>/dev/null || echo "0")
    if [ "${cost_int:-0}" -le 0 ] 2>/dev/null; then
        status+=$(printf "%b💰 ${ORANGE}<\$1${RESET}" "$S")
    else
        status+=$(printf "%b💰 ${ORANGE}\$%s${RESET}" "$S" "$cost_int")
    fi
fi

# 4. Daily total with budget-aware color (80+)
# Vivid tier palette distinct from muted session-cost orange so the signal pops
BUDGET_GREEN="\033[1;38;2;80;220;120m"
BUDGET_YELLOW="\033[1;38;2;255;200;40m"
BUDGET_RED="\033[1;38;2;255;70;70m"

if [ "$cols" -ge 80 ] && [ -n "$daily_usd" ] && [ "$daily_usd" != "0" ] && [ "$daily_usd" != "null" ]; then
    daily_int=$(printf "%.0f" "$daily_usd" 2>/dev/null || echo "0")

    # Read budget caps (fallback: unbounded → stays ORANGE)
    daily_color="$ORANGE"
    tier_icon=""
    budget_file="$HOME/.claude/budget.json"
    if [ -f "$budget_file" ]; then
        daily_cap=$(jq -r '.daily_cap_usd // 0' "$budget_file" 2>/dev/null)
        downshift_pct=$(jq -r '.auto_downshift_pct // 80' "$budget_file" 2>/dev/null)
        if [ -n "$daily_cap" ] && awk -v c="$daily_cap" 'BEGIN{exit !(c>0)}'; then
            daily_pct=$(awk -v u="$daily_usd" -v c="$daily_cap" 'BEGIN{if(c==0)print 0; else printf "%.0f", 100*u/c}')
            if   [ "$daily_pct" -ge 100 ]; then daily_color="$BUDGET_RED";    tier_icon="🔴"
            elif [ "$daily_pct" -ge "$downshift_pct" ]; then daily_color="$BUDGET_YELLOW"; tier_icon="🟡"
            else daily_color="$BUDGET_GREEN"; tier_icon="🟢"
            fi
        fi
    fi

    if [ "${daily_int:-0}" -le 0 ] 2>/dev/null; then
        status+=$(printf "%b%s %b<\$1${RESET}" "$S" "${tier_icon:-📅}" "$daily_color")
    else
        status+=$(printf "%b%s %b\$%s${RESET}" "$S" "${tier_icon:-📅}" "$daily_color" "$daily_int")
    fi
fi

# 5. Directory (50+)
if [ "$cols" -ge 50 ] && [ -n "$cwd" ]; then
    dir_name=$(basename "$cwd")
    status+=$(printf "%b📂 ${FG}%s${RESET}" "$S" "$dir_name")
fi

# 6. Git branch (50+)
if [ "$cols" -ge 50 ] && [ -n "$cwd" ] && [ -d "$cwd" ]; then
    branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
    [ -n "$branch" ] && status+=$(printf "%b🌿 ${BLUE}%s${RESET}" "$S" "$branch")
fi

echo -e "$status"
