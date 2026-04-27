---
name: docker
description: >
  Use when writing Dockerfiles, optimizing images, containerizing applications,
  or configuring docker-compose. Covers multi-stage builds, layer optimization,
  security, base image selection, and health checks.
  Auto-triggers for Dockerfile and docker-compose files.
---

# Dockerfile Patterns

## Minimal Template

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
EXPOSE 8080
CMD ["python", "app.py"]
```

## Base Image Selection

| Use Case | Image | Why |
|---|---|---|
| Python app | `python:3.12-slim` | Good balance of size + compat |
| Go binary | `gcr.io/distroless/static` | Minimal attack surface |
| Node.js | `node:20-slim` | Official, well-maintained |
| Static site | `nginx:1.25-alpine` | Tiny, purpose-built |
| Max security | Distroless | No shell, no package manager |

**Always pin versions** — never use `:latest`.

## Layer Optimization

Order from least to most frequently changed:

```dockerfile
# 1. System deps (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# 2. App dependencies (change occasionally)
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 3. App code (changes frequently)
COPY . .
```

## Multi-Stage Build (Python)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY . .
USER nobody
CMD ["python", "app.py"]
```

## Security

- **Non-root user**: Always `USER nobody` or create dedicated user
- **No secrets in image**: Pass at runtime via `-e` or `--mount=type=secret`
- **Pin with digest** for critical apps: `FROM python:3.12-slim@sha256:abc...`
- **Scan images**: `docker scout cves`, `trivy image`
- **.dockerignore**: Exclude `.git`, `node_modules`, `.env`, `*.pem`, `tests/`

## Key Rules

- `CMD ["exec", "form"]` — never shell form (proper signal handling)
- `COPY` over `ADD` (unless tar extraction needed)
- Single `RUN` for apt — chain with `&&`, clean in same layer
- `HEALTHCHECK` on every production image
- `ARG` for build-time, `ENV` for runtime

## Anti-Patterns

| Pattern | Fix |
|---|---|
| `FROM :latest` | Pin version: `FROM python:3.12-slim` |
| Running as root | Add `USER nobody` or dedicated user |
| Secrets in image | Pass at runtime: `docker run -e API_KEY` |
| No .dockerignore | Add with `.git`, `.env`, `node_modules` |
| `COPY . .` before deps | Copy dependency files first, install, then copy code |
| Shell form CMD | Exec form: `CMD ["python", "app.py"]` |
| Multiple RUN for apt | Single RUN with `&&` and cleanup |
| No HEALTHCHECK | Add with appropriate interval |
