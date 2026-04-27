---
name: python
description: >
  Use when writing Python code, reviewing PRs, building data pipelines, CLI tools,
  internal services, or ensuring senior data engineering standards. Covers SOLID, type hints,
  error handling, testing, linting (ruff/uv/pyright), and security.
  Auto-triggers for Python files. Invoke explicitly with /python.
---

# Python Code Quality

## Usage

- `/python <path>` — Full review + report
- `/python <path> --fix` — Review + auto-fix
- `/python <path> --report-only` — Report without fixes

## Review Workflow

**Phase 1 — Discovery**: List files, read each fully, map architecture.
**Phase 2 — Analysis**: Score on correctness, security, performance, maintainability, standards.
**Phase 3 — Report**: Critical/Major/Minor severity, overall score X/10.
**Phase 4 — Fix**: Critical first, one file at a time, never change behavior unless bug.
**Phase 5 — Verify**: `ruff check`, `python -c "import <module>"`, `pytest` if tests exist.

## Writing Mode (auto-triggered)

When writing new Python code, read these references for detailed patterns:
- `references/coding-patterns.md` — naming, error handling, logging, type hints, SOLID, security
- `references/testing-patterns.md` — fixtures, mocking, property-based testing, coverage
- `references/modern-python.md` — Python 3.12+ features, ruff/uv config, pyproject.toml, project layout

## Review Depth

| Change Type | Depth | Focus |
|---|---|---|
| Hotfix (1-5 lines) | Quick scan | Correctness only |
| Feature PR (<200 lines) | Standard | All 5 dimensions |
| Refactor (>200 lines) | Deep | Architecture, tests, regression risk |
| New module/service | Architectural | Design patterns, interfaces, SOLID |
| Data pipeline | Data-focused | Idempotency, schema evolution, backfill safety |

## Tool Selection

| Need | Tool |
|---|---|
| Config/API schemas | Pydantic v2 `BaseModel` |
| Internal data containers | `@dataclass(slots=True, frozen=True)` |
| CLI | `typer` + `rich` |
| HTTP API | `FastAPI` |
| Retry | `tenacity` |
| Logging | `structlog` (JSON) |
| Lint + format | `ruff` |
| Package management | `uv` |
| Type checking | `pyright` strict |
| Testing | `pytest` + `pytest-asyncio` + `hypothesis` |
| Config with secrets | `pydantic-settings` + `SecretStr` |

## Anti-Patterns

| Pattern | Fix |
|---|---|
| God function (>30 lines) | Split: extract, validate, transform, load |
| Hardcoded secrets | `os.environ["KEY"]`, pydantic `SecretStr` |
| Bare `except:` or `except Exception: pass` | Catch specific; log and re-raise |
| Mutable default arguments | `None` sentinel: `def f(items: list | None = None)` |
| SQL injection via f-strings | Parameterized: `cursor.execute(q, (val,))` |
| `iterrows()` in loop | Vectorized: `df["total"] = df["price"] * df["qty"]` |
| Missing resource cleanup | Context managers: `with get_conn() as conn:` |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `Variable.get()` at import time | Move inside task function |
| `print()` instead of logger | `structlog` with `.bind()` |
| Raw dicts for structured data | Pydantic `BaseModel` or `@dataclass` |
| Boolean trap arguments | Keyword-only with enums |

## Checklist

- [ ] Type hints on all function signatures
- [ ] Imports sorted: stdlib, third-party, local (no wildcards)
- [ ] Context managers for resources, `pathlib.Path` over `os.path`
- [ ] No hardcoded secrets (use env vars, `SecretStr`)
- [ ] Parameterized SQL queries
- [ ] Specific exception handling; log and re-raise
- [ ] Retry only transient errors with explicit timeouts on I/O
- [ ] Edge case tests: empty, null, negative, large values
- [ ] Functions < 20 lines, single responsibility
- [ ] Idempotent operations for pipelines, row count assertions

## Cross-References

| Skill | When |
|---|---|
| `profiling` | Code is slow — profile before optimizing |
| `pyspark` | Spark optimization |
| `sql` | SQL query optimization, warehouse design |
| `airflow` | DAG patterns and debugging |
