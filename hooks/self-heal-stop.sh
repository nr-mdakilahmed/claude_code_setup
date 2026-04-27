#!/usr/bin/env bash
# self-heal-stop.sh — fires on Claude Code Stop event
#
# Injects a one-time lesson-capture reminder per day if no lessons.md
# was updated this session. Keeps the environment self-improving without
# requiring the user to remember /wrap-up every time.
#
# Output format: JSON block decision — Claude reads the "reason" as a
# continuation prompt and captures any pending lessons before stopping.

TODAY=$(date +%Y-%m-%d)
SESSION_MARKER="/tmp/claude-self-heal-reminded-${TODAY}"

# Only remind once per day — prevents spamming on every Stop event
[ -f "$SESSION_MARKER" ] && exit 0

# Check if any lessons.md was updated in the last hour (active capture = skip)
NOW=$(date +%s)
for lessons in "$HOME/.claude/projects/"*/memory/lessons.md; do
    [ -f "$lessons" ] || continue
    MTIME=$(stat -f %m "$lessons" 2>/dev/null || stat -c %Y "$lessons" 2>/dev/null || echo 0)
    if [ $((NOW - MTIME)) -lt 3600 ]; then
        exit 0  # Lessons already captured this session
    fi
done

# Mark as reminded so this doesn't fire again today
touch "$SESSION_MARKER"

# Block stop once — Claude sees the reason and acts on it
printf '{"decision":"block","reason":"SELF-HEAL CHECK: No lessons.md was updated this session. Before finishing: (1) If any user corrections occurred → write them to lessons.md ## Patterns right now. (2) If you hit any anti-patterns → write to ## Anti-patterns. (3) If anything worked especially well → write to ## Wins. If genuinely nothing new this session, say so in one line and continue."}'
