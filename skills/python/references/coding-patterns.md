# Python Coding Patterns — Senior Engineer Standards


## Contents

- Philosophy
- Delete Aggressively
- Naming Conventions
- Security: No Hardcoded Secrets
- Type Hints (Modern — 3.12+)
- Import Order & Lazy Loading
- Error Handling
- Logging (not print)
- SOLID in Practice
- Data Structures Decision
- Timeouts
- Path Handling

> **When to load:** When writing new Python code or reviewing existing code for quality, naming, error handling, logging, security, and architecture.

## Philosophy

- Simplicity over cleverness
- Delete before adding complexity
- Trust frameworks (Airflow, Spark, Snowflake)
- Maintainability over robustness
- NO emojis in code, comments, or output

## Delete Aggressively

- Unused imports, dead functions, orphaned classes — delete immediately
- Redundant validation the framework already does — delete
- Dead exception handlers, unreachable catch blocks — delete
- If not called, it doesn't exist

---

## Naming Conventions

```python
# Variables: short, descriptive, snake_case
user_id, db_conn, row_count, staleness_min

# Functions: verb-based, action-oriented
fetch_baseline, validate_config, send_to_kafka

# Classes: PascalCase, noun-based
NRQLClient, DataProcessor, SnowflakeConnector

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300
```

**Senior rule**: If you need a comment to explain a variable name, rename the variable.

---

## Security: No Hardcoded Secrets

```python
# NEVER
PASSWORD = "secret123"
KEY = os.getenv("KEY", "default")  # BAD: default fallback

# CORRECT
PASSWORD = os.environ["PASSWORD"]  # Fails if missing
KEY = Variable.get("KEY")          # Airflow Variable
```

Use `pydantic-settings` with `SecretStr` for config:
```python
from pydantic_settings import BaseSettings, SecretStr

class Settings(BaseSettings):
    database_url: SecretStr  # masked in repr/logs
    api_key: SecretStr

    model_config = {"env_file": ".env"}

settings = Settings()
url = settings.database_url.get_secret_value()  # explicit unwrap
```

---

## Type Hints (Modern — 3.12+)

```python
# Union syntax (3.10+)
def process(value: str | None = None) -> str | int: ...

# PEP 695 generics (3.12+) — replaces TypeVar
class Cache[T]:
    def get(self, key: str) -> T | None: ...

type ListOrSet[T] = list[T] | set[T]  # type alias

# Self type for fluent APIs (3.11+)
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self

# @override (3.12+) — catch subclass drift
from typing import override

class Child(Base):
    @override
    def fetch(self) -> list[str]: ...
```

**Keyword-only args** for 3+ optional parameters:
```python
def create_pipeline(*, source: str, sink: str, batch_size: int = 100) -> Pipeline: ...
```

---

## Import Order & Lazy Loading

```python
# PEP 8 order
import os                          # 1. Standard library
import sys

import pandas as pd                # 2. Third-party
from airflow.models import Variable

from utils.client import Client    # 3. Local
```

**Lazy loading** (critical for Airflow — heavy imports slow DAG parsing):
```python
# DON'T: top-level heavy imports
import pandas as pd

# DO: import inside functions
def process_data():
    import pandas as pd
    return pd.DataFrame(data)

# TYPE_CHECKING guard for type-only imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from heavy_module import HeavyClass
```

---

## Error Handling

```python
# DO: catch specific, log, re-raise
try:
    result = operation()
except (ConnectionError, TimeoutError) as e:
    logger.error("Failed", error=str(e))
    raise

# DON'T: bare except, except Exception with pass
try:
    result = api_call()
except:
    pass  # NEVER — swallows KeyboardInterrupt too
```

**Context-aware retries** — only retry transient errors:
```python
def is_transient(e: Exception) -> bool:
    msg = str(e).lower()
    return any(x in msg for x in [
        "lock wait timeout", "connection reset",
        "temporarily unavailable", "deadlock"
    ])
# DON'T retry: 401/403, 400, schema errors, null PK
```

**False success pattern:**
```python
response = requests.post(url, json=payload)
response.raise_for_status()  # only catches 4xx/5xx
data = response.json()
if "error" in data or data.get("status") == "failed":
    raise ValueError(f"API error: {data.get('error_message')}")
```

**Finally blocks — cleanup only:**
```python
try:
    result = process()
except Exception as e:
    logger.error(f"Failed: {e}")
    raise
finally:
    conn.close()  # Only cleanup here — no business logic
```

---

## Logging (not print)

```python
import structlog

logger = structlog.get_logger()

def process(batch_id: str, records: list):
    log = logger.bind(batch_id=batch_id)
    log.info("started", count=len(records))
    try:
        result = do_work(records)
        log.info("done", output=result["count"])
    except Exception as e:
        log.error("failed", error=str(e))
        raise
```

**Log boundaries and aggregates, not inside tight loops:**
```python
# BAD: logging inside loop
for record in million_records:
    logger.debug(f"Processing {record}")

# GOOD: log boundaries
logger.info(f"Processing {len(records)} records")
results = process_batch(records)
logger.info(f"Done: {results.success_count} ok, {results.error_count} failed")
```

---

## SOLID in Practice

**Single Responsibility** — functions under 20 lines, one reason to change:
```python
# Bad: one function does fetch + parse + persist
def process_user_data(user_id: int) -> None: ...

# Good: each testable independently
def fetch_user(user_id: int) -> dict: ...
def parse_user(raw: dict) -> User: ...
def save_user(user: User) -> None: ...
```

**Open/Closed — Protocol, not inheritance:**
```python
from typing import Protocol

class DataSource(Protocol):
    def read(self) -> list[dict]: ...

class PostgresSource:
    def read(self) -> list[dict]: ...   # no inheritance needed

class S3Source:
    def read(self) -> list[dict]: ...   # add new sources without modifying Pipeline
```

**Dependency Inversion — inject, never instantiate inside:**
```python
# Bad: hardcoded, untestable
class ReportService:
    def __init__(self):
        self.db = PostgresDB()

# Good: injectable, testable
class ReportService:
    def __init__(self, db: DatabaseProtocol) -> None:
        self.db = db
```

**When to use classes vs functions vs modules:**

| Scenario | Use |
|----------|-----|
| Stateless transformation | Function |
| Related functions sharing state | Class |
| Config/settings grouping | `@dataclass` or Pydantic |
| Namespace of related utilities | Module |
| Behavior varying by type | Protocol + implementations |

**Senior rule**: Avoid classes as namespaces. If no `__init__` and no state, use a module with functions.

---

## Data Structures Decision

| Use Case | Tool | Why |
|----------|------|-----|
| Internal containers, no validation | `@dataclass(slots=True, frozen=True)` | Zero deps, fast |
| Config, API schemas, JSON I/O | Pydantic v2 `BaseModel` | Validation, JSON schema |
| Complex domain objects | `attrs` | More power than dataclass |
| Simple immutable records | `NamedTuple` | Fastest, pattern-matchable |
| Raw dicts | **Never for structured data** | No type safety, KeyError risk |

```python
@dataclass(slots=True, frozen=True)  # slots: 30-40% less memory
class Config:
    host: str
    port: int = 8080
    tags: list[str] = field(default_factory=list)
```

---

## Timeouts

| Operation | Timeout |
|-----------|---------|
| DB queries | 5-10 min |
| HTTP APIs | 30-60 sec |
| Health checks | 5 sec |
| External services | 10-30 sec |

---

## Path Handling

```python
# DON'T: hardcoded paths
CONFIG = "/opt/airflow/dags/billing/config.yaml"

# DO: relative paths
CONFIG = os.path.join(os.path.dirname(__file__), "config.yaml")
# Or: pathlib.Path(__file__).parent / "config.yaml"
```
