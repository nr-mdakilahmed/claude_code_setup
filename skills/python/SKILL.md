---
name: python
description: Reviews, refactors, and writes Python at senior data-engineering standards. Triggers when Claude edits Python files, reviews pull requests, or designs pipelines, CLIs, APIs, or internal services.
when_to_use: Auto-trigger when the user asks to review, write, fix, or refactor Python. Invoke explicitly with /python for a full-review report.
paths:
  - "**/*.py"
  - "pyproject.toml"
  - "requirements*.txt"
---

# Python Code Quality

Turns Claude into a senior Python reviewer: enforces modern tooling (ruff, uv, pyright), SOLID design, specific exception handling, and data-pipeline idempotency before approving any change.

**Freedom level: High** — Python problems admit many valid approaches. The skill directs judgment with principles and tool choices, not step-by-step recipes.

## 1. Write Small, Pure, Typed

**Functions do one thing; signatures are typed; side effects live at edges.**

- Keep functions under 20 lines. If a function needs three internal comments to be legible, split it.
- Type every signature. `from __future__ import annotations` in libraries.
- Prefer pure transformations; push I/O and state mutation to module boundaries.
- "Raw dict of config" → "`pydantic.BaseModel` or `@dataclass(slots=True, frozen=True)`".

## 2. Fail Loud at Boundaries, Trust Internal Code

**Validate inputs at system edges; never guard against impossible internal states.**

- Catch specific exceptions only. `except Exception:` or `except:` fails the review.
- Log with `structlog` and re-raise; do not swallow.
- Retry only **transient** errors; set explicit `timeout` on every I/O call.
- "Hardcoded secret" → "`os.environ[\"KEY\"]` or `pydantic_settings` with `SecretStr`".
- "f-string SQL" → "parameterized: `cursor.execute(q, (val,))`".

## 3. Test Behavior, Not Implementation

**Tests verify outputs for inputs, including the sharp edges.**

- Cover empty, null, negative, oversized, and concurrent cases.
- Use `hypothesis` for property-based tests on data transformations.
- `pytest-asyncio` for async code; do not `asyncio.run()` inside tests.
- Data-pipeline tests assert row counts, schema, and idempotency — not just "it ran".

## 4. Review Like the Code Ships Today

**Severity drives scope. Match review depth to the change, not the calendar.**

- Read every file fully before flagging; never skim.
- Score on correctness → security → performance → maintainability → standards.
- "Critical" blocks merge. "Major" requires a plan. "Minor" is advisory.
- Auto-fix Critical first, one file at a time; verify with `ruff check` and `pytest` before moving on.

## Tool selection

The single lookup consulted on every invocation.

| Need | Tool |
|---|---|
| Config / API schemas | `pydantic.BaseModel` (v2) |
| Internal data containers | `@dataclass(slots=True, frozen=True)` |
| CLI | `typer` + `rich` |
| HTTP API | `FastAPI` |
| Retry | `tenacity` |
| Logging | `structlog` (JSON) |
| Lint + format | `ruff` |
| Package / env | `uv` |
| Type checking | `pyright --strict` |
| Testing | `pytest` + `pytest-asyncio` + `hypothesis` |
| Config with secrets | `pydantic-settings` + `SecretStr` |

## Review depth

| Change | Depth | Focus |
|---|---|---|
| Hotfix (1–5 lines) | Quick | Correctness only |
| Feature PR (<200 lines) | Standard | All five dimensions |
| Refactor (>200 lines) | Deep | Architecture, tests, regression risk |
| New module / service | Architectural | SOLID, interfaces, design patterns |
| Data pipeline | Data-focused | Idempotency, schema evolution, backfill safety |

## Feedback loop (review mode)

1. Produce the review report (Critical / Major / Minor, overall score `X/10`).
2. **Validate immediately**: `ruff check <path>` and `python -c "import <module>"`; run `pytest` if tests exist.
3. If Critical errors found: fix → rerun ruff/pytest. Loop until clean.
4. Proceed to Major fixes only when all Critical pass.

## Anti-patterns

| Pattern | Fix |
|---|---|
| God function (>30 lines) | Split into extract / validate / transform / load |
| Hardcoded secret | `os.environ[...]` or `SecretStr` |
| `except Exception: pass` / bare `except:` | Catch specific; log and re-raise |
| Mutable default argument | `None` sentinel: `def f(items: list \| None = None)` |
| f-string SQL | Parameterized: `cursor.execute(q, (val,))` |
| `iterrows()` in a loop | Vectorize: `df["total"] = df["price"] * df["qty"]` |
| Missing resource cleanup | Context manager: `with get_conn() as conn:` |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| Airflow `Variable.get()` at import | Move inside the task function |
| `print()` in service code | `structlog` with `.bind()` |
| Raw dict for structured data | `pydantic.BaseModel` or `@dataclass` |
| Boolean trap argument | Keyword-only with an `Enum` |

## Checklist

- [ ] Type hints on every function signature
- [ ] Imports sorted: stdlib → third-party → local (no wildcards)
- [ ] Context managers for all resources; `pathlib.Path` over `os.path`
- [ ] No hardcoded secrets
- [ ] Parameterized SQL
- [ ] Specific exception handling; log and re-raise
- [ ] Retry only transient errors; explicit timeouts on I/O
- [ ] Edge-case tests: empty, null, negative, oversized, concurrent
- [ ] Functions < 20 lines, single responsibility
- [ ] Pipelines: idempotent, with row-count assertions

## References

- `references/coding-patterns.md` — naming, error handling, logging, type hints, SOLID, security
- `references/testing-patterns.md` — fixtures, mocking, property-based testing, coverage
- `references/modern-python.md` — Python 3.12+ features, ruff/uv config, pyproject.toml, project layout

## Cross-references

| Skill | When |
|---|---|
| `profiling` | Code is slow — profile before optimizing |
| `pyspark` | Spark-specific patterns |
| `sql` | Query optimization, warehouse design |
| `airflow` | DAG patterns and debugging |
