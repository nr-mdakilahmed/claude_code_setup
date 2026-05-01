---
name: docker
description: Writes Dockerfiles and docker-compose files that are small, secure, and reproducible. Triggers when Claude writes a Dockerfile, optimizes image size, designs multi-stage builds, containerizes an application, or configures docker-compose.
when_to_use: Auto-trigger on edits to Dockerfile, docker-compose.yml, and .dockerignore. Invoke explicitly when debugging image bloat, slow builds, or container runtime failures.
paths:
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/.dockerignore"
---

# Writing Dockerfiles

Turns Claude into a containerization reviewer: enforces multi-stage builds, non-root users, pinned base images, and real healthchecks before approving any image.

**Freedom level: Medium** — a preferred pattern exists per language/runtime; Claude selects from known base-image and build-stage options rather than improvising.

## 1. Multi-Stage Always

**Build artifacts in a fat stage; ship them in a lean stage.**

- Use `FROM ... AS builder` for compilation, wheel/jar building, or `npm install`.
- Final stage copies only binaries, wheels, or built assets with `COPY --from=builder`.
- Never install compilers (`build-essential`, `gcc`, `make`) in the final image.
- "Single-stage with `pip install`" → "builder stage produces `/wheels`; runtime stage installs from wheels and discards them".

## 2. Non-Root By Default

**Create a user in the Dockerfile; drop to it before `CMD`.**

- `RUN adduser --system --group --no-create-home app` then `USER app`.
- Own writable paths explicitly: `COPY --chown=app:app . /app`.
- Reject images that leave `USER root` (default) — Kubernetes `runAsNonRoot: true` will refuse to schedule them.
- Never embed secrets: use `--mount=type=secret` at build time, env vars or a secret manager at runtime.

## 3. Pin Base Images

**Tag plus digest. `:latest` is a bug report waiting to happen.**

- Use semver tags: `python:3.12-slim`, `node:20-slim`, `golang:1.23-alpine`.
- For production, pin by digest: `FROM python:3.12-slim@sha256:...`.
- Prefer `COPY` over `ADD` unless extracting a tarball from a URL.
- Keep one `RUN` per logical step; combine `apt-get update && apt-get install` with cleanup in the same layer.

## 4. Healthcheck Or It's Not Running

**`docker ps` shows "up" for broken containers. A healthcheck is the only source of truth.**

- Every production image declares `HEALTHCHECK` with realistic `--interval`, `--timeout`, `--start-period`, `--retries`.
- HTTP services: `CMD curl -fsS http://localhost:8080/healthz || exit 1`.
- Workers without HTTP: custom script that checks queue connectivity or a liveness file.
- Use exec form for `CMD` / `ENTRYPOINT` so PID 1 receives `SIGTERM` directly.

## Base image picker

| Need | Image | Why |
|---|---|---|
| Python/Node service (default) | `python:3.12-slim` / `node:20-slim` | Debian-based; glibc; compatible with most wheels |
| Alpine glibc issues (e.g. pandas, grpc) | `*-slim` | Avoid musl incompatibilities |
| Tiny Go/Rust binary | `gcr.io/distroless/static-debian12` | No shell, no pkg manager, minimal CVEs |
| Needs shell for debugging | `*-slim` or `distroless:debug` | Distroless non-debug has no `sh` |
| Simple static site | `nginx:1.27-alpine` | Purpose-built, tiny |

## Feedback loop

1. Write the Dockerfile and `.dockerignore`.
2. **Validate immediately**:
   - `docker build -t app:dev .` (check cache hits, note final image size).
   - `docker image inspect app:dev --format '{{.Size}} {{.Config.User}}'` (size sane? non-root?).
   - `docker run --rm app:dev <health command>` or `docker run -d app:dev && docker ps` after 30s to confirm healthy state.
3. If build slow / image bloated / container unhealthy: fix layer order, base image, or healthcheck → rebuild. Loop until clean.
4. Only ship after validation passes.

## Anti-patterns

| Pattern | Fix |
|---|---|
| `FROM python:latest` | Pin tag + digest: `FROM python:3.12-slim@sha256:...` |
| `COPY . .` before installing deps | Copy lockfile first, install, then copy source |
| Running as root | `RUN adduser --system app && USER app` |
| `CMD python app.py` (shell form) | Exec form: `CMD ["python", "app.py"]` |
| Secrets baked via `ENV API_KEY=...` | Runtime `-e` or `--mount=type=secret` |
| Missing `.dockerignore` | Add `.git`, `.venv`, `node_modules`, `.env`, `tests/` |
| No `HEALTHCHECK` | Add `HEALTHCHECK CMD curl -fsS /healthz \|\| exit 1` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Cache invalidates on every source change | Copy dependency files (`requirements.txt`, `package-lock.json`) before source; install; then copy source |
| Image size >1 GB for a Python service | Switch to multi-stage; verify no `build-essential` in final stage; run `docker history` to find the fat layer |
| `permission denied` writing to `/app` at runtime | `COPY --chown=app:app . /app` and ensure any mounted volume uses matching UID |
| Build hits "no space left" mid-build | `docker system prune -af --volumes`; check `/var/lib/docker` filesystem |
| `docker ps` shows "healthy" but app is broken | Healthcheck is superficial — hit a real endpoint, not `/`; check dependencies (DB, queue) |
| Container exits 0 immediately | Foreground process missing; exec form uses non-existent binary; check `docker logs` and `ENTRYPOINT`/`CMD` interaction |
| `SIGTERM` ignored, 10s shutdown | Shell form `CMD` wrapped in `sh -c`; switch to exec form so PID 1 is the app |
| `apt-get` slow / fails on rebuild | Same-layer: `apt-get update && apt-get install -y --no-install-recommends X && rm -rf /var/lib/apt/lists/*` |
| Distroless image "no such file: sh" when debugging | Use `:debug` tag (`gcr.io/distroless/static:debug`) or exec into a sidecar |
| Build stalls on `npm install` / `pip install` | Use BuildKit cache mount: `RUN --mount=type=cache,target=/root/.cache/pip pip install ...` |

## Checklist

- [ ] Multi-stage build (no compilers in final image)
- [ ] Non-root `USER` set before `CMD`
- [ ] Base image pinned (tag + digest in prod)
- [ ] `.dockerignore` present and excludes `.git`, `.env`, `node_modules`, `tests/`
- [ ] Dependency files copied before source (cache-friendly layer order)
- [ ] `apt-get` / `apk` installs in single `RUN` with cleanup in same layer
- [ ] `CMD` / `ENTRYPOINT` in exec form (JSON array)
- [ ] `HEALTHCHECK` declared with real check, not `exit 0`
- [ ] No secrets in `ENV`, `ARG`, or baked files
- [ ] Image builds reproducibly (`--no-cache` still succeeds)
- [ ] Final image size reviewed (`docker image ls`)

## References

- `references/dockerfile-python.md` — full Python Dockerfiles (pip and uv), multi-stage with wheels, healthcheck
- `references/dockerfile-go.md` — Go Dockerfiles (scratch, distroless, alpine) with build flags
- `references/healthcheck-patterns.md` — HTTP, TCP, custom-script healthchecks; liveness vs readiness vs startup

## Cross-references

| Skill | When |
|---|---|
| `cicd` | Building and pushing images in GitHub Actions / pipelines |
| `python` | App code standards inside the container |
| `shell` | Entrypoint scripts (`entrypoint.sh`) |
