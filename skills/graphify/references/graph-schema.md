# graph.json Schema

The canonical structure that `scripts/scan-repo.sh` emits and `scripts/render-graph-html.sh`, `bootstrap`, and `wrap-up` consume. Breaking this schema breaks every downstream skill — treat it as a contract.

## Contents

- Top-level object
- `repo` block
- `stats` block
- `entry_points` array
- `nodes` array (file entries)
- `edges` array (import relationships)
- `external_deps` array
- `hotspots` array
- `languages` map
- Versioning and compatibility
- Minimal valid example
- Full example
- Required vs optional field summary

## Top-level object

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-05-01T12:00:00Z",
  "repo": { ... },
  "stats": { ... },
  "languages": { ... },
  "entry_points": [ ... ],
  "nodes": [ ... ],
  "edges": [ ... ],
  "external_deps": [ ... ],
  "hotspots": [ ... ]
}
```

**Required top-level keys**: `schema_version`, `generated_at`, `repo`, `stats`, `nodes`, `edges`.
**Optional**: `languages`, `entry_points`, `external_deps`, `hotspots` (emit empty array `[]` if not detected, do not omit the key).

`schema_version` is semver-compatible ("MAJOR.MINOR"). Bump MAJOR only for breaking changes. Consumers (bootstrap, wrap-up) must check MAJOR and refuse mismatches.

## `repo` block

Metadata about the scanned repository.

```json
"repo": {
  "name": "om-airflow-dags",
  "root": "/Users/x/Documents/GitHub/om-airflow-dags",
  "commit": "a1b2c3d",
  "branch": "main"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | `basename $REPO_ROOT` |
| `root` | string | yes | absolute path |
| `commit` | string | no | short SHA if a git repo, else `null` |
| `branch` | string | no | current branch if a git repo, else `null` |

## `stats` block

Aggregate counts — used by `wrap-up` to decide whether to refresh.

```json
"stats": {
  "file_count": 142,
  "line_count": 18743,
  "node_count": 142,
  "edge_count": 318,
  "language_count": 3
}
```

All fields integers, all required. `file_count` and `node_count` are typically equal; they diverge only when the scanner intentionally skips generated files.

## `entry_points` array

Files the scanner identified as runnable entry points (main modules, DAGs, server entrypoints, scripts).

```json
"entry_points": [
  { "path": "src/main.py", "kind": "cli", "reason": "has __main__ block" },
  { "path": "dags/etl_daily.py", "kind": "dag", "reason": "imports airflow.models.DAG" }
]
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | repo-relative path |
| `kind` | string | yes | one of `cli`, `server`, `dag`, `script`, `lambda`, `worker`, `other` |
| `reason` | string | no | short string explaining the classification |

## `nodes` array (file entries)

The core of the graph. One object per source file.

```json
{
  "id": "src/pipeline/extract.py",
  "path": "src/pipeline/extract.py",
  "language": "python",
  "kind": "module",
  "loc": 142,
  "imports_internal": 3,
  "imports_external": 5,
  "in_degree": 4,
  "out_degree": 8,
  "tags": ["pipeline", "extract"]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | stable identifier — **use the repo-relative path**; downstream consumers treat `id` as a primary key |
| `path` | string | yes | same as `id` today; kept distinct to allow future renames |
| `language` | string | yes | lowercase: `python`, `typescript`, `go`, `sql`, `yaml`, `hcl`, `shell`, `markdown`, `other` |
| `kind` | string | yes | `module`, `package`, `config`, `test`, `fixture`, `entrypoint`, `script`, `docs` |
| `loc` | integer | yes | non-comment, non-blank line count |
| `imports_internal` | integer | yes | count of imports that resolve to another node in this graph |
| `imports_external` | integer | yes | count of imports that resolve to `external_deps` |
| `in_degree` | integer | yes | number of edges pointing at this node (how many files import it) |
| `out_degree` | integer | yes | number of edges originating from this node |
| `tags` | array of strings | no | scanner-assigned tags (directory stems, framework names) |

**Rule**: `in_degree` and `out_degree` must match the `edges` array exactly. Validate with `jq`.

## `edges` array (import relationships)

```json
{
  "source": "src/pipeline/load.py",
  "target": "src/pipeline/extract.py",
  "kind": "import",
  "raw": "from src.pipeline.extract import fetch"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `source` | string | yes | node `id` (the file doing the importing) |
| `target` | string | yes | node `id` (the file being imported) |
| `kind` | string | yes | `import`, `require`, `use`, `include`, `call` |
| `raw` | string | no | the original import line; useful for debugging |

Both `source` and `target` must reference existing node IDs. Orphaned edges are a scanner bug.

## `external_deps` array

Third-party dependencies that nodes import but which are not in the repo.

```json
[
  { "name": "pandas", "language": "python", "used_by_count": 12 },
  { "name": "apache-airflow", "language": "python", "used_by_count": 34 }
]
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | package name as it would appear in `requirements.txt` / `package.json` |
| `language` | string | yes | same enum as `nodes[].language` |
| `used_by_count` | integer | yes | number of nodes that import this dep |

## `hotspots` array

Top-N most-imported nodes. Derived from `nodes[].in_degree`. Precomputed for bootstrap and reports.

```json
[
  { "id": "src/utils/config.py", "in_degree": 28 },
  { "id": "src/db/session.py", "in_degree": 19 }
]
```

Sorted descending by `in_degree`. Typically top 10. Required key, may be empty array.

## `languages` map

Per-language summary.

```json
"languages": {
  "python": { "file_count": 89, "loc": 12044 },
  "yaml":   { "file_count": 23, "loc": 1420 },
  "sql":    { "file_count": 30, "loc": 5279 }
}
```

Keys are the same enum as `nodes[].language`. Optional but strongly recommended — bootstrap uses this to populate the tech-stack table.

## Versioning and compatibility

- **MAJOR** bump: rename or remove a required field, change the meaning of an enum value, re-key an array.
- **MINOR** bump: add an optional field, extend an enum with a new value.
- Consumers MUST tolerate unknown optional fields (forward compatibility).
- Consumers MUST refuse JSON with a different MAJOR version and ask the user to re-run `/graphify`.

## Minimal valid example

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-05-01T12:00:00Z",
  "repo": { "name": "example", "root": "/tmp/example" },
  "stats": { "file_count": 1, "line_count": 10, "node_count": 1, "edge_count": 0, "language_count": 1 },
  "nodes": [
    {
      "id": "main.py",
      "path": "main.py",
      "language": "python",
      "kind": "entrypoint",
      "loc": 10,
      "imports_internal": 0,
      "imports_external": 0,
      "in_degree": 0,
      "out_degree": 0
    }
  ],
  "edges": [],
  "external_deps": [],
  "hotspots": []
}
```

## Full example

See `scripts/scan-repo.sh` output on any real repo — the script writes conformant JSON by construction.

## Required vs optional field summary

**Top-level required**: `schema_version`, `generated_at`, `repo`, `stats`, `nodes`, `edges`.
**Top-level optional**: `languages`, `entry_points`, `external_deps`, `hotspots` (emit empty array, don't omit).
**Node required**: `id`, `path`, `language`, `kind`, `loc`, `imports_internal`, `imports_external`, `in_degree`, `out_degree`.
**Node optional**: `tags`.
**Edge required**: `source`, `target`, `kind`.
**Edge optional**: `raw`.

Validation contract: `jq -e '.schema_version and .repo.name and (.nodes | length > 0 or .edges | length == 0) and ([.nodes[] | .id, .language, .kind, .loc] | length > 0)' graph.json` returns truthy.
