---
name: profiling
description: Diagnoses slow Python code and high memory usage by selecting the right profiler for the observed symptom before proposing any fix. Triggers on "slow Python code", "profiling", "optimizing hot path", "reducing memory usage", "py-spy", "cProfile", "tracemalloc", flame graphs, and requests to make Python faster or leaner.
when_to_use: Auto-trigger when the user reports slow Python, memory growth, or asks to optimize a hot path. Use before any performance change — measurement precedes edits.
---

# Profiling Python

Turns Claude into a performance engineer: picks the profiler that matches the symptom, reads the data before proposing fixes, and refuses to guess at bottlenecks.

**Freedom level: Medium** — a preferred tool exists for each symptom (CPU vs memory, dev vs prod, function vs line), and Claude selects between them from a decision table rather than inventing an approach.

## 1. Measure Before Guessing

**No optimization without a profile. Read the numbers first; pattern-match second.**

- Require a profile artifact (cProfile stats, py-spy SVG, tracemalloc diff) before proposing changes.
- Sort by `cumulative` time for end-to-end bottlenecks; by `tottime` for self-time hotspots.
- "Looks slow" → "cProfile says `json.loads` is 38% cumulative — optimize there".
- Optimize the top offender only; re-profile after each change to confirm the win.

## 2. Pick Tool For Symptom

**Match the profiler to what hurts. CPU, memory, line-level, and production use different tools.**

- Unknown CPU bottleneck in dev → `cProfile` (stdlib, function-granular).
- Known hot function → `line_profiler` with `@profile` decorator.
- Production process (can't modify code) → `py-spy` attach to PID.
- Memory growth → `tracemalloc` snapshot diff; add `objgraph` for reference cycles.
- Slow startup → `python -X importtime script.py 2>import.log`.

## 3. Vectorize Hot Loops

**Python loops are slow; NumPy/pandas broadcast in C.**

- "`for i, row in df.iterrows(): df.loc[i, 'x'] = row.a * row.b`" → "`df['x'] = df.a * df.b`".
- Replace Python-level arithmetic on arrays with NumPy ufuncs; avoid `.apply` with Python callables.
- Batch I/O; never call `cursor.execute` per row — use `executemany` or bulk insert.
- Cache pure functions with `@lru_cache(maxsize=N)` — never leave `maxsize=None` in long-lived processes.
- When vectorization isn't enough: reach for Cython or Numba (see `references/numpy-vectorization.md`).

## 4. py-spy In Prod, cProfile In Dev

**Sampling profilers run in production; deterministic profilers run locally.**

- Dev: `cProfile` (deterministic, exact call counts, ~2× overhead — fine locally).
- Prod: `py-spy record` or `py-spy top` — sampling, no code change, attaches via PID.
- **Production safety**: always pass `--nonblocking` or cap with `--rate 50` on live traffic. Without it, py-spy pauses the target on each sample and can stall latency-sensitive services.
- Containers: py-spy needs `SYS_PTRACE` capability or `--cap-add=SYS_PTRACE`; PID-namespaced containers require running py-spy inside the same namespace (or use `kubectl debug` ephemeral container).
- Never run `memory_profiler`'s `@profile` decorator in prod — it slows the target 10–100×.

## Quick reference

| Symptom | Tool | One-liner |
|---|---|---|
| Unknown CPU hotspot (dev) | `cProfile` | `python -m cProfile -o out.prof -s cumulative script.py` |
| Known slow function | `line_profiler` | `kernprof -l -v script.py` (with `@profile`) |
| Live production process | `py-spy` | `py-spy record --nonblocking -o flame.svg --pid $PID` |
| Memory growth / leak | `tracemalloc` | snapshot diff — see principle 2 |
| Slow `import` / cold start | `-X importtime` | `python -X importtime app.py 2> import.log` |

## Anti-patterns

| Pattern | Fix |
|---|---|
| Guessing at bottleneck before profiling | Produce a profile artifact; then read, then edit |
| `cProfile` attached to a live prod service | Use `py-spy --nonblocking` instead |
| `@lru_cache` with no `maxsize` on long-lived process | `@lru_cache(maxsize=1024)`; verify with memory diff |
| `multiprocessing` for I/O-bound work | `asyncio` or `ThreadPoolExecutor` — I/O releases the GIL |
| `iterrows()` in a pandas hot loop | Vectorize: `df['x'] = df.a * df.b` |
| Optimizing cold paths (startup, rare branch) | Sort cProfile by `cumulative`; focus on per-request path |
| `memory_profiler` `@profile` left in production | Remove; use `tracemalloc` sampling or `py-spy dump --native` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `py-spy` "Permission denied" on Linux | `sudo py-spy record ...` or grant `CAP_SYS_PTRACE`; in k8s set `securityContext.capabilities.add: ["SYS_PTRACE"]` |
| `py-spy` "Permission denied" on macOS | Disable SIP selectively or run under sudo; py-spy cannot attach to system-signed Python |
| `py-spy` attaches but shows no samples | PID namespace mismatch — run py-spy inside the container, not the host |
| cProfile misses time spent in C extensions | Switch to `py-spy --native` to see C frames |
| cProfile distorts results under heavy async | Use `py-spy` or `asyncio` debug mode; cProfile overcounts event-loop ticks |
| `memory_profiler` slows target 10–100× | Expected — it instruments every line; move to `tracemalloc` snapshot diffs |
| `tracemalloc` itself uses significant RAM | Lower frame count: `tracemalloc.start(nframe=5)`; diff two snapshots, not ten |
| Flame graph unreadable — one giant bar | Filter by thread: `py-spy record --threads`; exclude idle with `--idle` off |
| Flame graph shows only `_bootstrap` / `select` | You're sampling an idle loop — ensure the workload is active during capture |
| Profile changes results on every run | Stabilize input data; profile `n=100` iterations, not a single request |

## References

- `references/async-profiling.md` — profiling asyncio/trio, async-aware py-spy patterns, `concurrent.futures` gotchas, event-loop lag measurement.
- `references/numpy-vectorization.md` — vectorization patterns, `iterrows`/`apply` rewrites, memory-layout pitfalls, and when Cython/Numba beat pure NumPy.

## Cross-references

- `/python` — once the hotspot is identified, code quality rules for the rewrite.
- `/pyspark` — Spark-specific performance (skew, AQE, broadcast joins) uses a different toolkit.
