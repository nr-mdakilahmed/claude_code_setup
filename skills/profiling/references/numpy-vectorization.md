# NumPy Vectorization

Rewrites for slow Python loops over arrays and DataFrames. Read this when a profile shows time concentrated in `iterrows`, `.apply`, or explicit `for` over NumPy arrays.

## Contents

- Core rule
- Common rewrites
- Broadcasting patterns
- `.apply` is not vectorization
- Memory layout pitfalls
- When vectorization isn't enough
- Cython vs Numba decision

## Core rule

**Any loop that touches one element at a time in Python is a bug if the array has >1000 elements.** NumPy ufuncs operate in C at ~100× the speed of a Python `for` loop. The rewrite is usually 1 line.

## Common rewrites

| Slow | Fast |
|---|---|
| `[x**2 for x in arr]` | `arr ** 2` |
| `np.array([f(x) for x in arr])` | `f(arr)` if `f` is a ufunc |
| `for i, row in df.iterrows(): df.loc[i, 'z'] = row.x + row.y` | `df['z'] = df['x'] + df['y']` |
| `df['z'] = df.apply(lambda r: r.x + r.y, axis=1)` | `df['z'] = df['x'] + df['y']` |
| `total = 0; for x in arr: total += x` | `arr.sum()` |
| `result = []; for x in arr: result.append(x if x > 0 else 0)` | `np.maximum(arr, 0)` |
| `mask = []; for x in arr: mask.append(x > threshold)` | `mask = arr > threshold` |
| `if condition: out = a else: out = b` (scalar per row) | `np.where(condition, a, b)` |
| `sum(a * b for a, b in zip(x, y))` | `np.dot(x, y)` or `x @ y` |
| Nested `for i, for j` over 2D array | `arr.reshape(-1)` then vectorize, or use broadcasting |

## Broadcasting patterns

Broadcasting lets you operate on arrays of different shapes without explicit loops:

```python
# Distance from each row to a centroid (shape: (n, 3) and (3,))
distances = np.linalg.norm(points - centroid, axis=1)

# Pairwise distance matrix (shape: (n, m))
diff = points[:, None, :] - queries[None, :, :]   # (n, m, 3)
dists = np.linalg.norm(diff, axis=-1)             # (n, m)

# Column-wise normalization
normalized = (arr - arr.mean(axis=0)) / arr.std(axis=0)
```

Rule of thumb: if you're writing two nested loops, look for a shape `(n, 1)` + `(1, m)` → `(n, m)` broadcast first.

## `.apply` is not vectorization

`df.apply(func, axis=1)` runs `func` once per row in Python — same speed as `iterrows`. It's a convenience, not an optimization.

- If `func` can be expressed with column operations: rewrite as `df['z'] = df['x'] * df['y']`.
- If `func` needs row context but is simple: use `np.where`, `np.select`, or `pd.Series.where`.
- If `func` genuinely needs Python per row: profile first — is it actually the bottleneck? If yes, see "when vectorization isn't enough" below.

## Memory layout pitfalls

- `arr.T` returns a view with reversed strides — operations on it may be 10× slower than on contiguous memory. Call `np.ascontiguousarray(arr.T)` if you'll read it repeatedly.
- `df.values` copies when dtypes are mixed; `df.to_numpy(copy=False)` is explicit.
- Chained operations like `(a + b + c + d)` create intermediate arrays. For large arrays, use `np.add(a, b, out=a)` or `numexpr` to fuse.
- Masked assignment: `arr[mask] = value` is fast; `arr[mask] = other_arr[mask]` with mismatched shapes silently broadcasts — benchmark it.

## When vectorization isn't enough

NumPy is C-fast but Python-slow at the edges: kernel launches, intermediate arrays, and operations that don't fit a ufunc (recurrence relations, complex branching).

Consider escalating when:

- The hot loop has data dependencies across iterations (can't be expressed as a ufunc).
- You've vectorized but profile still shows 80%+ in the hot path and the array is huge.
- Memory allocation for intermediates dominates — `%timeit` shows GC pauses.

## Cython vs Numba decision

| Factor | Cython | Numba |
|---|---|---|
| Compile time | AOT (separate build step) | JIT (first call slow, then cached) |
| Integration with NumPy | Typed memoryviews; verbose | `@njit` — drop-in, usually works |
| Supports Python objects | Yes | No (nopython mode) |
| GIL release | Manual `with nogil:` | Automatic with `@njit(parallel=True)` |
| Best for | Library code, full C interop, stable APIs | Numerical kernels, quick wins, research code |
| Deployment friction | Must ship compiled `.so`/`.pyd` | Runtime LLVM — larger install, no build step |

**Default to Numba** for a numerical inner loop in application code. **Reach for Cython** when you need Python object interop, a stable compiled module, or fine-grained GIL control.

Example Numba rewrite of a recurrence:

```python
from numba import njit

@njit(cache=True)
def ema(x, alpha):
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i-1]
    return out
```

First call pays compile cost (~1s); subsequent calls run at C speed.
