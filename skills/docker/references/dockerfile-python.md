# Python Dockerfiles

Full copy-paste-ready Dockerfiles for Python services. Read when containerizing a Python app, debugging Python image bloat, or migrating to `uv`.

## Contents

- Multi-stage with `pip` and wheels
- Multi-stage with `uv` (faster, smaller)
- FastAPI with healthcheck
- Worker (no HTTP) with custom healthcheck
- Layer-order reference
- Common failures

## Multi-stage with pip and wheels

Use for legacy projects on `requirements.txt`. Builder compiles wheels; runtime installs from the wheel dir and throws it away.

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.12-slim@sha256:... AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim@sha256:...
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN adduser --system --group --no-create-home app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels
COPY --chown=app:app . .
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/healthz',timeout=3).status==200 else 1)"
CMD ["python", "-m", "app.main"]
```

## Multi-stage with uv

Use for new projects. `uv` is 10-100x faster than pip; copy a single static binary from the uv image, build a `.venv`, copy it to runtime.

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.12-slim@sha256:... AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim@sha256:...
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN adduser --system --group --no-create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/healthz',timeout=3).status==200 else 1)"
CMD ["python", "-m", "app.main"]
```

## FastAPI service

`CMD` invokes `uvicorn` with exec form so `SIGTERM` reaches the worker.

```dockerfile
# ... builder stage identical to "Multi-stage with uv" above ...

FROM python:3.12-slim@sha256:...
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
RUN adduser --system --group --no-create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8080/healthz || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

Note: install `curl` in the final stage only if the healthcheck needs it. The `python -c urllib` variant avoids that dependency.

## Worker without HTTP

Background workers (Celery, Kafka consumers, Airflow workers) need a non-HTTP healthcheck. Custom script checks broker connectivity and heartbeat file.

```dockerfile
# ... builder stage identical ...

FROM python:3.12-slim@sha256:...
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
RUN adduser --system --group --no-create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
COPY --chown=app:app scripts/healthcheck.py /usr/local/bin/healthcheck
USER app
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python /usr/local/bin/healthcheck || exit 1
CMD ["python", "-m", "app.worker"]
```

`scripts/healthcheck.py` pattern:

```python
import sys, time, pathlib
HEARTBEAT = pathlib.Path("/tmp/worker.heartbeat")
MAX_AGE_SECONDS = 60
if not HEARTBEAT.exists() or time.time() - HEARTBEAT.stat().st_mtime > MAX_AGE_SECONDS:
    sys.exit(1)
# Optional: also ping broker. Keep under timeout.
sys.exit(0)
```

Worker writes `HEARTBEAT.touch()` each loop iteration.

## Layer-order reference

Order from least to most frequently changed:

1. `FROM` (pinned)
2. `ENV` / system config
3. `RUN apt-get install` system deps (change rarely)
4. `COPY requirements.txt` / `pyproject.toml` + install (change weekly)
5. `COPY . .` app source (changes per commit)
6. `USER`, `EXPOSE`, `HEALTHCHECK`, `CMD`

Reversing 4 and 5 invalidates the dependency cache on every source change. This is the single most common bloat / slow-build cause.

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `pip install` recompiles every build | Source copied before requirements | Copy `requirements.txt` first |
| Image >800 MB for a small FastAPI app | `build-essential` in final stage | Move compilers to builder only |
| `ModuleNotFoundError` at runtime | Virtualenv path not on `PATH` | `ENV PATH="/app/.venv/bin:$PATH"` |
| `Permission denied: /app/.cache` | `.venv` or working dir owned by root | `COPY --chown=app:app` |
| Healthcheck perpetually "starting" | `--start-period` too short for cold start | Increase to 30–60s for slow imports |
