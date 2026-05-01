# Python Testing Patterns — Senior Engineer Standards


## Contents

- Test Organization
- Database Fixtures with Temp Tables
- Mock External APIs
- Factory Fixture for Test Data
- Parameterized Tests for Edge Cases
- Freezing Time in Tests
- Property-Based Testing (Hypothesis)
- Async Testing
- What to Mock vs What NOT to Mock
- Coverage Strategy

> **When to load:** When writing tests, reviewing test quality, or setting up test infrastructure for data pipelines.

## Test Organization

```
tests/
  unit/           # Pure functions, transforms, validators (no I/O, sub-ms)
  integration/    # DB, S3, Kafka (use testcontainers, real infra)
  e2e/            # Full pipeline runs against staging
  fixtures/       # Shared test data (CSV, JSON, Parquet)
  conftest.py     # Session-scoped connections, shared factories
```

---

## Database Fixtures with Temp Tables

```python
import pytest, sqlalchemy

@pytest.fixture
def db_engine():
    engine = sqlalchemy.create_engine(os.environ["TEST_DB_URL"])
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS test_temp"))
    yield engine
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("DROP SCHEMA IF EXISTS test_temp CASCADE"))
    engine.dispose()

@pytest.fixture
def sample_table(db_engine):
    with db_engine.connect() as conn:
        conn.execute(sqlalchemy.text(
            "CREATE TABLE test_temp.orders (id INT, amount DECIMAL(10,2), created_at TIMESTAMP)"
        ))
        conn.execute(sqlalchemy.text(
            "INSERT INTO test_temp.orders VALUES (1,100.00,'2025-01-01'),(2,0.00,'2025-01-02')"
        ))
        conn.commit()
    yield "test_temp.orders"
```

---

## Mock External APIs

```python
from unittest.mock import patch, MagicMock

def test_fetch_and_transform():
    mock_resp = {"status": "success", "data": [{"id": 1, "value": 100}]}
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: mock_resp, raise_for_status=lambda: None
        )
        result = fetch_and_transform(endpoint="/api/data")
        assert len(result) == 1
```

**Prefer DI over patch** — inject dependencies, mock at construction:
```python
# Better: inject the client
def fetch_data(client: httpx.Client) -> dict: ...

# Test with a mock client — no string-based patching
mock_client = MagicMock()
mock_client.get.return_value = Response(200, json={"key": "val"})
result = fetch_data(mock_client)
```

---

## Factory Fixture for Test Data

```python
@pytest.fixture
def generate_records():
    def _generate(count: int = 100, null_pct: float = 0.0) -> list[dict]:
        return [
            {"id": i, "amount": round(random.uniform(-100, 10000), 2),
             "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(0, 365)),
             "category": random.choice(["A", "B", "C", None] if null_pct > 0 else ["A", "B", "C"])}
            for i in range(count)
        ]
    return _generate
```

---

## Parameterized Tests for Edge Cases

```python
@pytest.mark.parametrize("input_val,expected", [
    pytest.param([], 0, id="empty"),
    pytest.param([{"amount": 0}], 0, id="zero"),
    pytest.param([{"amount": -100}], -100, id="negative"),
    pytest.param([{"amount": 1e15}], 1e15, id="large"),
    pytest.param([{"amount": None}], 0, id="null"),
], ids=str)
def test_sum_amounts(input_val, expected):
    assert sum_amounts(input_val) == pytest.approx(expected, abs=1e-9)
```

---

## Freezing Time in Tests

```python
from freezegun import freeze_time

@freeze_time("2025-06-15 12:00:00")
def test_staleness_check():
    last_run = datetime(2025, 6, 14, 12, 0, 0, tzinfo=timezone.utc)
    assert is_stale(last_run, max_age_hours=12)
```

---

## Property-Based Testing (Hypothesis)

Use for: parsing, transforms with invariants, serialization round-trips, deduplication.

```python
from hypothesis import given, settings, strategies as st

@given(st.lists(st.integers(), min_size=1))
@settings(max_examples=500)
def test_dedup_preserves_elements(items):
    result = deduplicate(items)
    assert set(result) == set(items)
    assert len(result) == len(set(items))
```

---

## Async Testing

```python
# pyproject.toml: asyncio_mode = "auto"
import pytest

async def test_async_pipeline():
    result = await run_async_transform(data)
    assert result == expected

# Mock async functions
from unittest.mock import AsyncMock

async def test_with_async_mock():
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"status": "ok"}
    result = await my_service(mock_client)
    assert result["status"] == "ok"
```

---

## What to Mock vs What NOT to Mock

**Mock:** External HTTP APIs, time (`freezegun`), random/UUID, file system for unit tests, notification senders.

**Do NOT mock:** Your own business logic, database for integration tests (use testcontainers), Pandas/NumPy operations, the function under test.

**Rule of thumb:** If mocking > 2 things in a single test, the function has too many dependencies — refactor first.

---

## Coverage Strategy

- **80%** line coverage = useful floor
- **90%+** for core business logic / transforms
- **Branch coverage** (`--cov-branch`) is more useful than line coverage
- **Mutation testing** (`mutmut`) = real quality check — if mutants survive, assertions are weak

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:", "def __repr__"]
```
