# Modern Python Tooling & Features (2024-2026)


## Contents

- Tooling Stack (2024-2026)
- Ruff Configuration
- uv — Package Manager
- pyproject.toml Template
- Project Layout (src layout — 2024 consensus)
- Python 3.12+ Features Worth Using
- CLI Tools Pattern (Typer)
- FastAPI Service Pattern

> **When to load:** When setting up a Python project, configuring tooling, or using Python 3.12+ features.

## Tooling Stack (2024-2026)

| Concern | Tool | Replaces |
|---------|------|----------|
| Linting + formatting | `ruff` | flake8 + black + isort + pyupgrade + bandit |
| Type checking | `pyright` (new) or `mypy --strict` (existing) | - |
| Package management | `uv` | pip + pip-tools + poetry + pyenv + virtualenv |
| Testing | `pytest` + `pytest-asyncio` | unittest |
| Property testing | `hypothesis` | manual edge cases |
| Security scanning | `pip-audit` + `bandit` | safety |
| Config management | `pydantic-settings` | dynaconf, manual env parsing |

---

## Ruff Configuration

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # bugbear
    "UP",   # pyupgrade (auto-modernize syntax)
    "SIM",  # simplify
    "S",    # bandit security
    "RUF",  # ruff-specific
]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

```bash
ruff check --fix .   # lint + auto-fix
ruff format .        # format
```

---

## uv — Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # install

uv init myproject                    # init project
uv add pydantic ruff                 # add deps (updates pyproject.toml + uv.lock)
uv add --dev pytest pytest-cov       # dev deps
uv run python main.py               # run in project env
uv run pytest                        # run tests
uv python install 3.13              # manage Python versions
uv python pin 3.13                  # pin version
```

---

## pyproject.toml Template

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.0", "sqlalchemy>=2.0"]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "hypothesis", "pip-audit", "ruff", "pyright"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=src --cov-branch --cov-report=term-missing"

[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
```

---

## Project Layout (src layout — 2024 consensus)

```
myproject/
  src/
    mypackage/
      __init__.py
      core.py
  tests/
    unit/
    integration/
    conftest.py
  pyproject.toml
```

---

## Python 3.12+ Features Worth Using

### Pattern Matching (3.10+)
```python
def process_event(event: dict) -> None:
    match event:
        case {"type": "click", "x": int(x), "y": int(y)}:
            handle_click(x, y)
        case {"type": "keypress", "key": str(key)}:
            handle_key(key)
        case _:
            raise ValueError(f"Unknown: {event}")
```

### Exception Groups (3.11+ — for concurrent code)
```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(task_a())
        tg.create_task(task_b())
except* ValueError as eg:
    for exc in eg.exceptions:
        handle_value_error(exc)
except* ConnectionError as eg:
    for exc in eg.exceptions:
        handle_conn_error(exc)
```

### f-String Improvements (3.12+)
```python
# Nest f-strings, reuse quotes, add comments in expressions
x = f"result: {f'{2 + 2}'}"
msg = f"""Total: {
    sum(prices)  # comments allowed now
}"""
```

### Deferred Annotations (3.14 — no more string quotes)
```python
# Python 3.14: forward references work without quotes
class Node:
    def next(self) -> Node: ...  # no NameError
# No need for: from __future__ import annotations
```

---

## CLI Tools Pattern (Typer)

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def run(source: str, dry_run: bool = False):
    if dry_run:
        console.print("[yellow]Dry run[/yellow]")
        return
    result = process(source)
    console.print(f"Processed {result['count']} records")
```

## FastAPI Service Pattern

```python
from fastapi import FastAPI, Query
import asyncpg

app = FastAPI()

@app.get("/api/data")
async def get_data(user_id: str = Query(None), page: int = 1):
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch(query, user_id, page)
    return {"data": [dict(r) for r in rows]}
```
