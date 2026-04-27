---
name: profiling
description: >
  Use when debugging slow code, optimizing hot paths, or reducing memory usage.
  Covers cProfile, py-spy, tracemalloc, line_profiler, memory_profiler,
  caching, multiprocessing, async I/O, and NumPy vectorization.
  Auto-triggers when debugging performance issues or profiling code.
---

# Python Performance Optimization

## Profile First — Never Optimize Without Data

```python
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
main()
profiler.disable()
pstats.Stats(profiler).sort_stats('cumulative').print_stats(10)

# Or: python -m cProfile -o out.prof script.py
# Or: py-spy record -o profile.svg -- python script.py
```

## Tool Selection

```
Slow code?
  +-- Know which function? --> line_profiler (@profile)
  +-- Don't know where?
        +-- Can modify code? --> cProfile
        +-- Production/can't modify? --> py-spy (attach to PID)
        +-- Memory growing? --> tracemalloc snapshot diff
        +-- Async/await slow? --> asyncio debug mode + py-spy
```

| Scenario | Tool |
|---|---|
| CPU bottleneck (function) | `cProfile` |
| CPU bottleneck (flame graph) | `py-spy` |
| Memory leak | `tracemalloc` + `objgraph` |
| Line-level timing | `line_profiler` |
| Production | `py-spy` (no code changes) |
| Startup time | `python -X importtime` |

## Hot Path Optimizations

```python
# List comprehension > loop (2x faster)
result = [i**2 for i in range(n)]

# Generator for memory (constant memory)
data = (i**2 for i in range(1000000))

# String join > concatenation (O(n) vs O(n^2))
"".join(parts)

# Dict lookup > list search (O(1) vs O(n))
x in lookup_dict

# Local variables > globals (inside loops)
local = GLOBAL_VAL
```

## Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)  # ALWAYS set maxsize — unbounded = memory leak
def expensive(n):
    return compute(n)
```

## Large Data Strategy

| Size | Strategy |
|---|---|
| <10K rows | Load all in memory |
| 10K-1M | Batch (1000 chunks) |
| >1M | Streaming/generators |

## Memory Profiling

```python
import tracemalloc
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
# ... suspected leaky code ...
snap2 = tracemalloc.take_snapshot()
for stat in snap2.compare_to(snap1, "lineno")[:10]:
    print(stat)  # Shows size diff per line
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Premature optimization | `cProfile -s cumulative` first; top-10 functions only |
| Profiling wrong layer | Check cumulative time — optimize the I/O call, not the transform |
| Optimizing cold paths | Focus on per-request, per-row hot paths |
| Unbounded `lru_cache` | Always `maxsize=N` |
| `multiprocessing` for I/O | Use `asyncio` or `ThreadPoolExecutor` for I/O |
