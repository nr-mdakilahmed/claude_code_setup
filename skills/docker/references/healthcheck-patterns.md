# Healthcheck Patterns

Read when designing a `HEALTHCHECK`, wiring Kubernetes probes, or chasing a false-positive "healthy" container.

## Contents

- Timing parameters
- HTTP healthcheck
- TCP healthcheck
- Custom script healthcheck
- Liveness vs readiness vs startup
- Dockerfile vs orchestrator
- Common failures

## Timing parameters

```
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ...
```

| Param | What it controls | Default | Tune when |
|---|---|---|---|
| `--interval` | Gap between checks | 30s | Expensive checks → increase; latency-sensitive → decrease |
| `--timeout` | Fail if check exceeds this | 30s | Set below `--interval`; typical 3–5s |
| `--start-period` | Grace window before failures count | 0s | Cold-start apps need 10–60s |
| `--retries` | Consecutive fails before "unhealthy" | 3 | Flaky deps → 5; fast-fail → 2 |

Exit code contract: `0` = healthy, `1` = unhealthy. Any other code = unhealthy (treated as failure).

## HTTP healthcheck

Prefer a dedicated endpoint (`/healthz`, `/readyz`) that returns 200 with a small JSON payload. Never hit `/` — it often does work.

```dockerfile
# With curl (add to image if not present)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/healthz || exit 1
```

Flags: `-f` fails on HTTP >= 400, `-s` silent, `-S` show errors.

```dockerfile
# Without curl — Python has urllib in stdlib
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/healthz',timeout=3).status==200 else 1)"
```

```dockerfile
# Go binary: subcommand of the app itself
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["/app", "healthcheck"]
```

Endpoint handler should:
- Return 200 quickly (<100ms).
- Check in-process state (DB pool open, config loaded).
- Avoid downstream dependency calls (those belong in readiness, not liveness).

## TCP healthcheck

For services without HTTP. Tests only that the port is accepting connections.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD nc -z localhost 5432 || exit 1
```

```dockerfile
# No netcat? Use bash /dev/tcp (bash only, not dash/sh)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD bash -c 'cat < /dev/null > /dev/tcp/localhost/5432' || exit 1
```

Weak signal: the port being open doesn't mean the app works. Prefer a protocol-level check where possible (e.g. `pg_isready` for Postgres, `redis-cli ping`).

## Custom script healthcheck

For workers, batch jobs, or apps where HTTP/TCP is insufficient.

```dockerfile
COPY --chown=app:app scripts/healthcheck.sh /usr/local/bin/healthcheck
RUN chmod +x /usr/local/bin/healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /usr/local/bin/healthcheck
```

Script checklist:
- Exits `0` on healthy, `1` on unhealthy. No other codes.
- Completes well under `--timeout`.
- Checks actual liveness signal: heartbeat file age, queue consumer lag, last-processed timestamp.
- Writes nothing to stdout unless debugging (stdout is ignored; stderr appears in `docker inspect`).

Worker heartbeat pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail
HEARTBEAT=/tmp/worker.heartbeat
MAX_AGE=60
[[ -f "$HEARTBEAT" ]] || exit 1
age=$(( $(date +%s) - $(stat -c %Y "$HEARTBEAT") ))
(( age < MAX_AGE )) || exit 1
exit 0
```

Worker loop must `touch "$HEARTBEAT"` each iteration.

## Liveness vs readiness vs startup

Docker's single `HEALTHCHECK` conflates concerns that Kubernetes splits into three probes. On Kubernetes, prefer probe definitions in the pod spec over Dockerfile `HEALTHCHECK`.

| Probe | Answers | Action on fail | Use case |
|---|---|---|---|
| **Startup** | "Has the app finished booting?" | None (until it passes once) | Slow-starting apps (JVM, ML model load) — gates the other probes |
| **Liveness** | "Is the process alive and responsive?" | Restart the container | Deadlock detection, memory leak kills |
| **Readiness** | "Can the app accept traffic right now?" | Remove from load-balancer rotation | Draining, dependency outage, warming up |

Endpoint design:

- `/healthz` (liveness): in-process sanity — `return 200` unconditionally once the server is up.
- `/readyz` (readiness): dependency check — DB reachable, cache warm, config loaded; returns 503 otherwise.
- `/startupz` (startup): same as `/readyz` during boot; graduates to always-200 once started.

Common mistake: making liveness also check the database. The DB has a blip, the pod restarts, the restart doesn't help, the pod restart-loops. Keep liveness local.

## Dockerfile vs orchestrator

| Environment | Source of truth |
|---|---|
| Local `docker run` / `docker-compose` | `HEALTHCHECK` in Dockerfile |
| Kubernetes | `livenessProbe` / `readinessProbe` / `startupProbe` in pod spec; Dockerfile `HEALTHCHECK` is ignored |
| ECS | Task definition `healthCheck`; falls back to Dockerfile if omitted |
| Nomad | `check` block in job file |

Keep `HEALTHCHECK` in the Dockerfile as a baseline — it documents intent and works in local dev even when the orchestrator overrides it.

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| Container "starting" forever | `--start-period` shorter than actual cold start | Increase to observed cold-start + 50% |
| Container "healthy" but app broken | Healthcheck hits `/` which returns 200 on a static page | Dedicated `/healthz` that inspects real state |
| Healthcheck passes locally, fails in orchestrator | Orchestrator overrides Dockerfile healthcheck | Update the orchestrator probe, not the Dockerfile |
| Restart loop when DB blips | Liveness depends on DB | Move DB check to readiness; liveness stays local |
| `nc: command not found` in alpine | `netcat-openbsd` not installed | `RUN apk add --no-cache netcat-openbsd` or use `/dev/tcp` |
| Curl in distroless: "no such file" | Distroless has no curl | Use `python -c urllib` or binary subcommand |
| Healthcheck takes 30s, interval is 10s | `--timeout` missing; Docker queues checks | Set `--timeout` below `--interval` |
