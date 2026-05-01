# memory-server

MCP server exposing per-project memory as pull-on-demand tools. Companion to
the hot.md / cold-memory split described in `~/.claude-kit/designs/07-memory-mcp-server.md`.

## Tools

| Tool | Purpose |
|---|---|
| `get_memory(topic)` | Read a specific memory file (architecture, todo, lessons, history, hot, memory, graph_report) |
| `search_memory(query, k)` | Keyword search across all memory files |
| `list_lessons(tag?, recent?)` | Filter lessons.md Patterns section |
| `get_todo(status)` | Active / Backlog / Done items |
| `recall_plan(slug?)` | Get a plan by slug, or list available plans |

## Install

Installed via uvx from a local path (no PyPI publish needed):

```bash
uvx --from ~/.claude-kit/mcp-servers/memory-server memory-server --repo-name <repo>
```

`/bootstrap` wires this into each repo's `.mcp.json` automatically.

## Per-repo config

Added to `<repo>/.mcp.json` by `write-project-claude.sh`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "uvx",
      "args": [
        "--from", "/Users/<you>/.claude-kit/mcp-servers/memory-server",
        "memory-server",
        "--repo-name", "<repo-name>"
      ],
      "type": "stdio"
    }
  }
}
```

## Development

```bash
cd ~/.claude-kit/mcp-servers/memory-server
uv sync                    # install deps
uv run memory-server --repo-name om-airflow-dags  # smoke test
```

Test tools interactively with `fastmcp dev memory_server/server.py`.

## Why grep-based search (not BM25)

v1 scope. Memory files are small (<500 KB typically). Grep is <50ms and
has zero index-maintenance cost. If per-query latency becomes a problem
or ranking quality matters more, upgrade to FTS5 or BM25 via `whoosh`.
