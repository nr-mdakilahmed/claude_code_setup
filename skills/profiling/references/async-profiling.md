# Async Profiling

Profiling coroutines, event loops, and thread/process pools. Read this only when the workload is async or mixes async with blocking I/O.

## Contents

- When sync profilers lie
- asyncio debug mode
- py-spy on async code
- Event-loop lag
- trio and anyio
- concurrent.futures gotchas
- Diagnosing GIL contention

## When sync profilers lie

`cProfile` attributes time to whatever function is on the stack when the event loop yields — which is often `selectors.select` or `asyncio.base_events._run_once`. Results: "50% of time in `select`" tells you nothing.

- Prefer `py-spy` (sampling) for async code — it captures the full stack at sample time, including the coroutine frame.
- If you must use cProfile, wrap a single coroutine call, not the full `asyncio.run`.
- Sort py-spy output by `--function` to collapse async frames.

## asyncio debug mode

Enable before profiling an asyncio app:

```python
import asyncio
asyncio.run(main(), debug=True)
```

Or: `PYTHONASYNCIODEBUG=1 python app.py`.

- Logs coroutines that take >100ms without yielding (tunable via `loop.slow_callback_duration`).
- Surfaces `Task was destroyed but it is pending!` and un-awaited coroutines.
- Overhead is real — leave it off in prod unless investigating a specific incident.

## py-spy on async code

```bash
# Record a flame graph with thread separation
py-spy record --nonblocking --threads -o async.svg --pid $PID --duration 30

# Dump live stacks (no file) — great for "why is it hanging?"
py-spy dump --pid $PID
```

- `--threads` separates the event-loop thread from worker threads (thread pool, executors).
- Coroutines appear as frames named after the `async def` function — not the event loop internals.
- For native C extensions (uvloop, aiohttp's C parser): add `--native`.

## Event-loop lag

The single best async health metric. Measure how long a no-op callback takes to fire:

```python
import asyncio, time

async def measure_lag(interval: float = 1.0) -> None:
    loop = asyncio.get_running_loop()
    while True:
        start = loop.time()
        await asyncio.sleep(interval)
        lag_ms = (loop.time() - start - interval) * 1000
        if lag_ms > 50:
            print(f"event-loop lag: {lag_ms:.1f}ms")
```

- Healthy lag: <5ms. Sustained >50ms means something is blocking the loop (CPU work, sync I/O, a C extension holding the GIL).
- Use `loop.slow_callback_duration = 0.1` to auto-log slow callbacks instead of rolling your own.

## trio and anyio

- `trio` ships with `trio.to_thread.run_sync` for offloading blocking calls — if profiler shows time in `trio.lowlevel.wait_*`, you're CPU-bound and should move the work.
- Use `py-spy` the same way; trio tasks show as `_run` frames with the task function one level up.
- `anyio` bridges asyncio/trio — profile the underlying loop, not the anyio wrapper.

## concurrent.futures gotchas

- `ThreadPoolExecutor` for I/O-bound work (releases the GIL on I/O syscalls). py-spy sees each worker thread; filter with `--threads`.
- `ProcessPoolExecutor` for CPU-bound. Profile each worker separately — attach py-spy to the worker PID (`ps --ppid $PARENT`), not the parent.
- Don't use `asyncio.run_in_executor` for long CPU work without `max_workers`; the default pool is `min(32, cpu + 4)` and will serialize silently.
- Cancellation is cooperative: a blocked worker cannot be cancelled. Profile shows threads stuck in `socket.recv`? Add timeouts, don't add more workers.

## Diagnosing GIL contention

When py-spy shows many threads but only one ever executing Python code:

```bash
py-spy dump --pid $PID | grep -c "Thread"   # count threads
py-spy top --pid $PID                        # watch which thread holds GIL
```

- If one thread dominates `%CPU` while others idle in `pthread_cond_wait`: GIL contention.
- Fix: move CPU work to `ProcessPoolExecutor`, release the GIL in C extensions (NumPy/pandas already do), or switch to async for I/O-bound paths.
- `perf` + `py-spy --native` together show whether time is in Python bytecode or C — GIL matters for the former.
