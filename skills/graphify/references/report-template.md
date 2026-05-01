# GRAPH_REPORT.md Template


## Contents

- Required sections (in this order)
- Template
- Overview
- Tech Stack
- Entry Points
- Key Modules
- Dependency Hotspots
- Data Flow
- Critical Paths
- Test Coverage Estimate
- External Dependencies
- Conventions Observed
- Potential Issues
- Example outputs (what "good" looks like)
- Rules for the narrative

The canonical layout for the Markdown narrative that accompanies `graph.json`. `bootstrap` extracts sections from this report into `architecture.md`, so section names and ordering must stay stable.

## Required sections (in this order)

1. Title + timestamp
2. Overview
3. Tech Stack
4. Entry Points
5. Key Modules
6. Dependency Hotspots
7. Data Flow
8. Critical Paths
9. Test Coverage Estimate
10. External Dependencies
11. Conventions Observed
12. Potential Issues

Each section heading uses `## <Name>` exactly as above — bootstrap greps for these headings by name.

## Template

```markdown
# <REPO_NAME> — Codebase Knowledge Graph

Generated: <ISO-8601 UTC>
Source: ~/.claude/projects/<REPO_NAME>/graphs/graph.json

## Overview

<2–4 sentences. What kind of system is this? Primary language(s)? Rough size (files, LOC)? What does it do?>

## Tech Stack

| Layer | Tech | Source of truth |
|---|---|---|
| Language | Python 3.12 | pyproject.toml |
| Orchestration | Apache Airflow 2.8 | requirements.txt |
| Warehouse | Snowflake | dbt_project.yml |
| IaC | Terraform 1.6 | .tf files |

## Entry Points

| Path | Kind | Purpose |
|---|---|---|
| src/main.py | cli | Service entrypoint |
| dags/etl_daily.py | dag | Daily ETL DAG |

## Key Modules

<4–8 modules. For each: path, responsibility (1 line), key functions/classes.>

- **`src/pipeline/`** — extract/transform/load; primary business logic
- **`src/db/`** — database session management; uses SQLAlchemy
- **`src/config/`** — Pydantic settings; reads from env
- **`tests/`** — pytest suite; fixtures in `conftest.py`

## Dependency Hotspots

Top 10 most-imported files. Derived from `graph.json` → `hotspots`.

| Rank | Path | Imported by N files |
|---|---|---|
| 1 | src/utils/config.py | 28 |
| 2 | src/db/session.py | 19 |
| 3 | src/models/base.py | 17 |

## Data Flow

<Narrative prose, 1–3 short paragraphs. How does data move through the system end-to-end? Where does it enter (API, file, queue)? Where does it land (DB, warehouse, file)?>

## Critical Paths

<3–6 bullets. The code paths that matter — typically the ones on a hot request/run path, or the ones that touch external systems.>

- Request → `src/api/handler.py` → `src/pipeline/transform.py` → Snowflake
- DAG trigger → `dags/etl_daily.py` → `src/pipeline/load.py` → S3

## Test Coverage Estimate

Rough estimate based on test file count and module coverage. Do not claim line coverage — state the method.

- Test files: 42 / 89 source modules (47%)
- Tested modules: `pipeline/`, `db/`, `utils/`
- Untested: `cli/`, `admin/`

## External Dependencies

From `graph.json` → `external_deps`. Top 10 by `used_by_count`.

| Package | Used by |
|---|---|
| pandas | 12 |
| apache-airflow | 34 |
| sqlalchemy | 18 |

## Conventions Observed

- **Naming**: snake_case modules, PascalCase classes
- **Config**: `pydantic.BaseSettings` reading from env; no hardcoded secrets
- **Errors**: specific exceptions; structured logging via `structlog`
- **Tests**: `pytest`, fixtures in `conftest.py`, factories in `tests/factories/`

## Potential Issues

<Derived from graph analysis. List only real issues, not speculation.>

- **Circular dependency candidate**: `src/a.py` ↔ `src/b.py` (both import each other)
- **Orphaned files**: `src/legacy/old_helper.py` has 0 in-edges and 0 out-edges
- **Large files**: `src/pipeline/monolith.py` has 1,240 LOC — candidate for split
```

## Example outputs (what "good" looks like)

### Overview — good

> A Python 3.12 data-engineering repo built on Apache Airflow 2.8 and Snowflake. 89 Python files across `dags/`, `src/`, and `tests/` (~12k LOC). Daily DAGs extract from Postgres, transform in Python, and load to Snowflake via dbt.

### Overview — bad (too vague)

> This is a Python project with some files and folders.

### Data Flow — good

> Ingestion begins when the `etl_daily` DAG triggers at 02:00 UTC. `dags/etl_daily.py` calls `src/pipeline/extract.py::fetch_orders`, which reads from Postgres via SQLAlchemy. Raw rows are staged to S3 as Parquet. A second task invokes `dbt run` against Snowflake. Failures route to a Slack alert callback.

### Potential Issues — good

> `src/db/session.py` ↔ `src/db/models.py` — both files import each other. Extract shared types into `src/db/types.py` to break the cycle.

### Potential Issues — bad (speculation)

> The code could probably be more modular and might benefit from refactoring.

## Rules for the narrative

- Write from the graph, not from guessing. If `graph.json` doesn't support a claim, leave it out.
- Use tables for structured data (stacks, hotspots, deps), prose for flow and conventions.
- Keep each section short — the full report should be readable in 2 minutes.
- No emojis. No marketing language. No "exciting", "powerful", "robust".
- Absolute repo paths only where they appear in `graph.json`; otherwise repo-relative.
