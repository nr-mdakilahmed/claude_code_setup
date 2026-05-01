# Design: Memory MCP Server — Output-First Retrieval

## Problem

`@`-loaded memory is all-or-nothing push: every session starts with
~5-20k tokens of memory in context, regardless of task. For "fix a lint
error" the cost is absurd; for "refactor auth" it may be insufficient.

CRG solved this for code (pull via MCP). Memory should work the same way.

## Proposed approach

### Server shape

```
~/.claude-kit/mcp-servers/memory-server/
├── pyproject.toml
├── server.py                  # FastMCP entry
├── tools/
│   ├── get_memory.py          # get_memory(topic: str) → file contents
│   ├── search_history.py      # search_history(query: str, k: int = 5) → snippets
│   ├── list_lessons.py        # list_lessons(tag: str?, recent: int?) → list
│   ├── get_todo.py            # get_todo(status: active|backlog|done) → list
│   └── recall_plan.py         # recall_plan(slug: str) → plan file
└── indexes/                   # cached BM25/FTS indexes per repo
```

### MCP tools

| Tool | Purpose |
|---|---|
| `get_memory(topic)` | fetch architecture.md / lessons.md / hot.md section by name |
| `search_history(query, k)` | BM25 across history.md entries; return top-k with context |
| `list_lessons(tag?, recent?)` | filter lessons.md by tag or recency |
| `get_todo(status)` | pull active/backlog/done lists |
| `recall_plan(slug)` | load a prior plan by filename slug |
| `search_memory(query)` | cross-file fuzzy search if unsure which tool |

### New CLAUDE.md `@` loading

Instead of loading all 5 files:
```
@~/.claude/projects/<repo>/memory/hot.md
```

Only hot.md (curated top-20, <2k tokens). Everything else lives behind the
MCP server. Claude pulls when needed.

### Config

Per-repo `.mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "uvx",
      "args": ["--from", "~/.claude-kit/mcp-servers/memory-server", "memory-server", "--repo-name", "om-airflow-dags"],
      "type": "stdio"
    }
  }
}
```

## Open questions

1. **Cold-start cost**: first `search_memory` call has to build/load BM25
   index. Acceptable (<500ms)?
2. **Hot memory curation**: who writes hot.md? Proposed: wrap-up regenerates
   it as a distillation of the other files. What distillation algorithm?
   - Option A: top-5 most-recent lessons + active todo + 1-paragraph arch summary
   - Option B: tag-weighted: only items tagged `pinned: true` survive
   - Option C: Claude one-shot summary at wrap-up (cost: ~500 tokens/wrap-up)
3. **Consistency with @ refs**: `@`-loading is Anthropic-native; MCP is
   plugin-level. Risk: architecture.md gets edited manually, MCP server
   serves stale cache. Needs invalidation hook on Edit.
4. **Backward compat**: all existing bootstrap/wrap-up scripts assume the
   5-file layout. Memory MCP must coexist with that — don't break
   architecture.md, just don't load it by default.

## Rollout

1. Write memory-server skeleton (FastMCP, 3 tools: get_memory,
   search_history, list_lessons). ~200 lines.
2. Test on one repo (om-airflow-dags). Measure token savings on 10 real
   questions (with full @ load vs with hot.md + pull).
3. If ≥3× savings on average, roll out to other repos.
4. Update bootstrap to install per-repo .mcp.json pointing at memory server.
5. Update wrap-up to regenerate hot.md.

## Risk

- **Fragmented memory**: @-refs and MCP mixing can confuse Claude on where to
  look. Mitigation: hot.md includes pointers like "deep history: use
  search_history tool; architecture deep dive: use get_memory('architecture')".
- **Tool-call cost > context cost** for small memory files. Don't use MCP
  for anything < 1k tokens when the alternative is a direct @ ref.
- **Divergence from Anthropic's direction**: if Anthropic ships native
  memory search, this becomes redundant. Monitor changelog.
