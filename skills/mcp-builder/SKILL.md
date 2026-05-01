---
name: mcp-builder
description: Builds Model Context Protocol servers that expose external APIs, data sources, or internal tooling to LLM clients. Triggers when the user asks about building MCP servers, adding tools to an existing MCP server, debugging MCP server issues, or choosing between stdio and HTTP transport. Covers Python (FastMCP) and TypeScript (@modelcontextprotocol/sdk), tool design, pagination, annotations, and Inspector-based testing.
when_to_use: Auto-trigger when editing files that register MCP tools (FastMCP `@server.tool`, `server.tool()` from the TS SDK) or when the user mentions MCP, FastMCP, or the MCP Inspector. Invoke explicitly with /mcp-builder for a scaffold or design review.
---

# MCP Server Development

Turns Claude into an MCP server designer: names tools for humans, paginates every list, annotates every mutation, and validates with the MCP Inspector before shipping.

**Freedom level: High** — MCP server design admits many valid approaches (transport, SDK flavor, resource shape). The skill directs judgment with principles and decision tables, not a fixed recipe.

## 1. Name Tools For Humans

**Tool names must read like intent, not implementation.**

- Use `snake_case` with a service prefix: `github_create_issue`, never `create_issue` or `createIssueV2`.
- One tool = one verb on one noun. Split `manage_issue` into `create_issue` / `update_issue` / `close_issue`.
- Descriptions state purpose and constraints in one sentence. "Creates a GitHub issue in the given repo. Requires `repo:write` scope."
- "Generic `search`" → "`jira_search_issues` with explicit JQL param".

## 2. Paginate Or Explode Context

**Any tool that returns a list must accept `limit` and `cursor`/`offset` and return `has_more`.**

- Default `limit` to 25; cap at 100. Reject unbounded queries at the boundary.
- Return `{items, next_cursor, has_more}` — never a bare array when results can grow.
- Truncate long string fields (logs, bodies) to ~2 KB; offer a `get_*_detail` tool for full payloads.
- "Return all rows" → "Return first page + `next_cursor`; Claude iterates only when needed".

## 3. Annotate For Safety

**Every tool sets all four hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`.**

- Read tools: `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`.
- Mutations: `readOnlyHint: false` and set `destructiveHint` honestly (delete → true, upsert → false).
- `openWorldHint: true` for anything hitting the public internet; `false` for local/sandboxed I/O.
- Missing annotations means the client cannot build safe UX around the tool — reject PRs that omit them.

## 4. Stdio For Local, HTTP For Shared

**Default to stdio; switch to Streamable HTTP only when the server is remote or multi-client.**

- Stdio: one process per client, zero auth, trivial to debug. Use for desktop agents and CI.
- Streamable HTTP: multi-tenant, auth required (OAuth or bearer), server lifecycle independent of client.
- Never expose a stdio server over the network via a shell wrapper — use the HTTP transport instead.
- "SSE for remote" → "Streamable HTTP (the SSE transport is deprecated in recent SDKs)".

## 5. Test With Inspector Before Shipping

**Run `npx @modelcontextprotocol/inspector` against every tool before calling the server done.**

- Verify each tool: description reads well, inputs validate, errors are actionable, pagination returns `has_more`.
- Write 10 evaluation questions (see `references/evaluation.md`) and run them through a real client.
- Reject any tool that fails Inspector load, returns raw stack traces, or hangs without a timeout.

## Quick reference

| When you need | Use | Why |
|---|---|---|
| New Python server | FastMCP (`pip install mcp[cli]`) | Decorator API, handles stdio/HTTP, Pydantic-validated |
| New TypeScript server | `@modelcontextprotocol/sdk` + Zod | First-class types, best tooling ecosystem |
| Local single-client | stdio transport | Zero auth, one process per client |
| Remote / multi-client | Streamable HTTP transport | Auth, independent lifecycle, multi-tenant |
| Manual smoke test | `npx @modelcontextprotocol/inspector` | Canonical client — matches real agent behavior |

## Tool teasers

Python (FastMCP) — paginated read with annotations:

```python
from mcp.server.fastmcp import FastMCP
server = FastMCP("github")

@server.tool(annotations={"readOnlyHint": True, "destructiveHint": False,
                          "idempotentHint": True, "openWorldHint": True})
async def github_list_issues(repo: str, limit: int = 25, cursor: str | None = None):
    """Lists open issues for a repo. Paginated; returns has_more + next_cursor."""
    page = await gh.issues(repo, per_page=min(limit, 100), after=cursor)
    return {"items": page.items, "next_cursor": page.next, "has_more": page.has_more}
```

TypeScript (SDK + Zod) — destructive mutation, honest annotations:

```ts
server.tool("github_close_issue",
  { repo: z.string(), number: z.number().int().positive(), reason: z.string().optional() },
  { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: true },
  async ({ repo, number, reason }) => {
    const res = await gh.closeIssue(repo, number, reason);
    return { content: [{ type: "text", text: `Closed ${repo}#${number}` }], structuredContent: res };
  });
```

Stdio entrypoint (both SDKs auto-wire stdio when run as a module):

```bash
python -m my_server                     # FastMCP stdio
node dist/server.js                     # TS SDK stdio
npx @modelcontextprotocol/inspector -- python -m my_server   # smoke test
```

## Anti-patterns

| Pattern | Fix |
|---|---|
| Generic tool name (`send_message`) | Prefix with service: `slack_send_message` |
| Unbounded list endpoint | Accept `limit` + `cursor`; return `has_more` |
| Missing annotations | Set all 4 hints; be honest about `destructiveHint` |
| Raw internal error surfaced to client | Catch, log, return structured `{error: "..."}` with next step |
| Synchronous I/O in handler | `async def` + `httpx.AsyncClient` / `fetch` |
| Hardcoded API key | `os.environ["X"]` / `process.env.X`; document in `.env.example` |
| SSE transport on new server | Streamable HTTP (SSE is deprecated in current SDKs) |

## Troubleshooting

| Symptom | Fix |
|---|---|
| Server won't start (Python) | `python -m py_compile server.py`; check `mcp[cli]` is installed in the active venv |
| Server won't start (TS) | `npm run build`; verify `dist/` exists and `"type": "module"` is set in `package.json` |
| Inspector can't connect | Confirm entrypoint writes nothing to stdout before the MCP handshake (no stray `print()`) |
| Tool missing from Inspector | Decorator/handler not registered before `server.run()`; check import order |
| "Method not found" from client | Tool name has uppercase or hyphens — rename to `snake_case` |
| Tool runs once then hangs | Missing `return` in async handler or unawaited coroutine |
| Pagination returns all rows | `limit`/`cursor` declared but ignored — wire them into the underlying API call |
| Auth fails on HTTP transport | Bearer header not forwarded; check middleware order and CORS for browser clients |
| Timeout on long operations | Return a job id + `get_status` tool rather than holding the request open |
| Stdio works, HTTP doesn't | Wrong transport registered — use `Streamable HTTP`, not deprecated SSE |

## Checklist

- [ ] Tool names: `snake_case` with service prefix
- [ ] One verb per tool; no `manage_*` catch-alls
- [ ] All 4 annotations set on every tool
- [ ] Every list tool accepts `limit` + `cursor` and returns `has_more`
- [ ] Inputs validated with Zod (TS) or Pydantic (Python)
- [ ] Errors return structured messages with a next step
- [ ] Async I/O throughout; no blocking calls in handlers
- [ ] Secrets loaded from env; `.env.example` committed
- [ ] Transport matches deployment (stdio local, HTTP remote)
- [ ] Smoke-tested with `@modelcontextprotocol/inspector`
- [ ] 10 evaluation questions written and passing

## References

- `references/best-practices.md` — naming, response format, pagination, security, annotations (read for every new server)
- `references/python-server.md` — FastMCP patterns, Pydantic models, async clients, worked examples
- `references/typescript-server.md` — MCP SDK patterns, Zod schemas, build config, worked examples
- `references/evaluation.md` — format and guidelines for the 10-question eval suite
- `scripts/scaffold-server.sh` — scaffold a Python or TypeScript server skeleton: `scaffold-server.sh --lang python --name github-mcp`

## Cross-references

| Skill | When |
|---|---|
| `python` | Server is Python — run `/python` review on tool implementations |
| `shell` | Wrapping the server in a launcher script |
| `cicd` | Publishing the server to a registry or running eval suite in CI |
