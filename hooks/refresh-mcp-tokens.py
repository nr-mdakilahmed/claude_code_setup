#!/usr/bin/env python3
"""
Auto-refreshes expired Claude Code MCP OAuth tokens from macOS keychain.
Runs as a UserPromptSubmit hook. Outputs a warning only if a token
cannot be refreshed (requires manual /plugin re-auth).
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# NR MCP tokens expire every ~5 minutes. Refresh before expiry.
TOKEN_ENDPOINTS = {
    "plugin:nr:nr-mcp-server": "https://mcp-stg.staging-service.nr-ops.net/oauth2/token",
}

BUFFER_SECONDS = 30
DEFAULT_EXPIRES_IN = 300


def get_creds():
    raw = subprocess.check_output(
        ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
        stderr=subprocess.DEVNULL,
    )
    return json.loads(raw.decode())


def save_creds(creds):
    result = subprocess.run(
        ["security", "find-generic-password", "-s", "Claude Code-credentials"],
        capture_output=True, text=True,
    )
    acct = None
    for line in result.stdout.splitlines():
        if '"acct"' in line and '<blob>=' in line:
            acct = line.split('<blob>=')[1].strip().strip('"')
            break
    if not acct:
        print("⚠️  Could not detect keychain account name. Run /plugin to re-authenticate.", file=sys.stderr)
        return
    raw = json.dumps(creds)
    subprocess.run(
        ["security", "add-generic-password", "-s", "Claude Code-credentials",
         "-a", acct, "-w", raw, "-U"],
        check=True, capture_output=True,
    )


def refresh_token(entry, token_endpoint):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": entry["refreshToken"],
        "client_id": entry["clientId"],
    }).encode()
    req = urllib.request.Request(
        token_endpoint, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def main():
    now_ms = time.time() * 1000
    try:
        creds = get_creds()
    except subprocess.CalledProcessError:
        return  # keychain entry not found — first-time setup
    except json.JSONDecodeError as e:
        print(f"⚠️  Could not parse MCP credentials from keychain: {e}", file=sys.stderr)
        return

    oauth = creds.get("mcpOAuth", {})
    needs_manual = []
    changed = False

    for key, entry in oauth.items():
        server_name = entry.get("serverName", key.split("|")[0])
        endpoint = TOKEN_ENDPOINTS.get(server_name)
        expires_ms = entry.get("expiresAt", 0)

        if expires_ms > now_ms + BUFFER_SECONDS * 1000:
            continue  # still valid
        if endpoint is None:
            # Atlassian tokens can't be auto-refreshed — skip silently
            continue

        if not entry.get("refreshToken"):
            continue  # no refresh token stored — skip silently

        try:
            result = refresh_token(entry, endpoint)
            if "access_token" not in result:
                needs_manual.append(server_name)
                continue
            entry["accessToken"] = result["access_token"]
            if "refresh_token" in result:
                entry["refreshToken"] = result["refresh_token"]
            entry["expiresAt"] = int(time.time() * 1000) + result.get("expires_in", DEFAULT_EXPIRES_IN) * 1000
            changed = True
        except urllib.error.HTTPError as e:
            if e.code in (400, 401):
                needs_manual.append(server_name)
            else:
                print(f"⚠️  Token refresh failed for {server_name}: HTTP {e.code}", file=sys.stderr)
        except urllib.error.URLError as e:
            print(f"⚠️  Could not reach token endpoint for {server_name}: {e.reason}", file=sys.stderr)

    if changed:
        try:
            save_creds(creds)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not save refreshed tokens to keychain: {e}", file=sys.stderr)

    if needs_manual:
        names = ", ".join(needs_manual)
        print(f"⚠️  MCP auth expired and could not auto-refresh: {names}. Run /plugin to re-authenticate.")


if __name__ == "__main__":
    main()
