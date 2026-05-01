# Go Dockerfiles

Three variants for Go services: scratch (smallest), distroless (recommended), alpine (when shell needed). Read when containerizing a Go binary or choosing between runtime options.

## Contents

- Variant picker
- Scratch (static binary)
- Distroless (recommended default)
- Alpine (with shell + debug tools)
- Build flags reference
- Common failures

## Variant picker

| Need | Base | Size | Shell |
|---|---|---|---|
| Smallest possible, purely static | `scratch` | ~5–20 MB | No |
| Minimal CVEs, production default | `gcr.io/distroless/static-debian12` | ~20 MB | No (`:debug` tag adds busybox) |
| Shell access for on-container debugging | `alpine:3.20` | ~30 MB | Yes (`sh`) |
| CGO-enabled (libc dependency) | `gcr.io/distroless/base-debian12` | ~30 MB | No |

## Scratch

Smallest, statically linked binary. No CA certs, no timezone data by default.

```dockerfile
# syntax=docker/dockerfile:1.7

FROM golang:1.23-alpine@sha256:... AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build \
        -trimpath -ldflags="-s -w" \
        -o /out/app ./cmd/app

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /out/app /app
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["/app", "healthcheck"]
ENTRYPOINT ["/app"]
```

Notes:
- `USER 65532:65532` is the `nonroot` UID/GID from distroless conventions. Scratch has no `/etc/passwd`, so numeric form is required.
- Healthcheck uses a subcommand of the binary itself, since `scratch` has no `curl` or `wget`.
- `-trimpath -ldflags="-s -w"` strips debug info and paths; shrinks ~30%.

## Distroless (recommended default)

Same build stage as scratch; runtime is Google's distroless image. Has CA certs and tzdata preinstalled, no shell by default.

```dockerfile
# ... builder stage identical ...

FROM gcr.io/distroless/static-debian12@sha256:...
COPY --from=builder /out/app /app
USER nonroot:nonroot
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["/app", "healthcheck"]
ENTRYPOINT ["/app"]
```

For debugging, swap to `gcr.io/distroless/static-debian12:debug` which includes busybox.

## Alpine (shell + debug tools)

Use when operators need to `docker exec` into the container for investigation.

```dockerfile
# ... builder stage identical ...

FROM alpine:3.20@sha256:...
RUN apk add --no-cache ca-certificates tzdata curl \
    && adduser -S -H app
COPY --from=builder /out/app /app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8080/healthz || exit 1
ENTRYPOINT ["/app"]
```

Beware: CGO-compiled binaries (those using `sqlite3`, `net/cgo`, etc.) need `GOOS=linux CGO_ENABLED=1` plus alpine-compatible musl, or use `distroless/base-debian12` with glibc.

## Build flags reference

| Flag | Effect |
|---|---|
| `CGO_ENABLED=0` | Static binary; required for `scratch` / `distroless/static` |
| `-trimpath` | Remove local paths from binary (reproducible builds) |
| `-ldflags="-s -w"` | Strip symbol table and DWARF debug info |
| `-ldflags="-X main.version=$(git rev-parse --short HEAD)"` | Inject version at build time |
| `GOOS=linux GOARCH=amd64` | Cross-compile target (explicit) |
| `-buildvcs=false` | Skip stamping VCS info (faster in CI with shallow clones) |

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| "no such file or directory" running binary on scratch | CGO enabled; dynamic lib missing | `CGO_ENABLED=0` or switch to `distroless/base-debian12` |
| TLS errors: "x509: certificate signed by unknown authority" | No CA bundle in final image | Copy `/etc/ssl/certs/ca-certificates.crt` from builder |
| Wrong timezone at runtime | No `tzdata` in final image | Copy `/usr/share/zoneinfo` or `RUN apk add tzdata` |
| Binary is 40 MB | Debug symbols + unstripped | `-ldflags="-s -w" -trimpath` |
| Cannot `docker exec sh` | Distroless has no shell by default | Use `:debug` tag or alpine base |
| `go mod download` runs every build | Source copied before `go.sum` | Copy `go.mod go.sum` first, download, then copy source |
