#!/usr/bin/env python3
"""
iTerm2 API helper for Avengers bridge.
Replaces tmux list-panes / capture-pane / send-keys.

Usage:
  python3 iterm2_helper.py find
  python3 iterm2_helper.py capture <session_id>
  python3 iterm2_helper.py send <session_id> <message>
"""
import sys
import json
import iterm2


async def _find_session(app):
    """Return the iTerm2 session running Claude Code (node/claude process)."""
    for window in app.windows:
        for tab in window.tabs:
            for session in tab.sessions:
                try:
                    job = await session.async_get_variable("jobName")
                    if job and ('node' in job.lower() or 'claude' in job.lower()):
                        return session
                except Exception:
                    pass
    return None


async def _get_session(app, session_id):
    for window in app.windows:
        for tab in window.tabs:
            for session in tab.sessions:
                if session.session_id == session_id:
                    return session
    return None


async def main(connection):
    app = await iterm2.async_get_app(connection)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''

    if cmd == 'find':
        session = await _find_session(app)
        if session:
            print(session.session_id)
        else:
            sys.exit(1)

    elif cmd == 'capture':
        session = await _get_session(app, sys.argv[2])
        if not session:
            print(json.dumps([]))
            return
        contents = await session.async_get_screen_contents()
        lines = []
        for i in range(contents.number_of_lines):
            text = contents.line(i).string
            if text.strip():
                lines.append(text)
        print(json.dumps(lines))

    elif cmd == 'send':
        session = await _get_session(app, sys.argv[2])
        if not session:
            print('error: session not found', file=sys.stderr)
            sys.exit(1)
        text = sys.argv[3] if len(sys.argv) > 3 else ''
        await session.async_send_text(text + '\n')
        print('ok')

    elif cmd == 'list':
        sessions = []
        for window in app.windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    sessions.append(session.session_id)
        print(json.dumps(sessions))

    elif cmd == 'close':
        session_id = sys.argv[2] if len(sys.argv) > 2 else ''
        session = await _get_session(app, session_id)
        if not session:
            print('error: session not found', file=sys.stderr)
            sys.exit(1)
        await session.async_close(force=True)
        print('ok')

    else:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        sys.exit(1)


iterm2.run_until_complete(main)
