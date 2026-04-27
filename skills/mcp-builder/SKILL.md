---
name: mcp-builder
description: >
  Use when building MCP (Model Context Protocol) servers that let LLMs interact
  with external services. Covers Python (FastMCP) and TypeScript (MCP SDK),
  tool design, naming, pagination, annotations, and transport selection.
  Auto-triggers when building or editing MCP servers.
---

# MCP Server Development Guide

## Phased Workflow

**Phase 1 — Research**: Study target API, choose language, plan tool coverage.
> Read `references/best-practices.md` for naming, response format, pagination, security, annotations.

**Phase 2 — Implement**: Set up project, build infrastructure, implement tools.
> Read `references/python-server.md` for Python/FastMCP patterns and examples.
> Read `references/typescript-server.md` for TypeScript/Zod patterns and examples.

**Phase 3 — Review & Test**: Verify quality, build, test with MCP Inspector.
- No duplicated code (DRY), consistent error handling, full type coverage
- `npm run build` (TS) or `python -m py_compile` (Python)
- Test with `npx @modelcontextprotocol/inspector`

**Phase 4 — Evaluations**: Build 10 complex questions to test LLM effectiveness.
> Read `references/evaluation.md` for format and guidelines.

## Tool Design Principles

| Principle | Guideline |
|---|---|
| Naming | snake_case with service prefix: `github_create_issue` |
| Descriptions | Concise, unambiguous, match actual functionality |
| Input validation | Zod (TS) or Pydantic (Python) with constraints |
| Output | Support JSON (machine) + Markdown (human) |
| Errors | Actionable messages with next steps |
| Pagination | Respect `limit`, return `has_more`, `next_offset` |
| Annotations | Set `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` |

## Transport Selection

| Criterion | stdio | Streamable HTTP |
|---|---|---|
| Deployment | Local | Remote |
| Clients | Single | Multiple |
| Real-time | No | Yes |

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Generic tool names (`send_message`) | Prefix: `slack_send_message` |
| No input validation | Zod/Pydantic with constraints |
| Exposing internal errors | Actionable error messages |
| Loading all results in memory | Pagination with limit/offset |
| Missing annotations | Always set all 4 hints |
| Sync I/O in handlers | Always async/await |
| Copy-paste between tools | Extract shared client/formatters |

## Checklist

- [ ] Tool names: snake_case with service prefix
- [ ] All 4 annotations on every tool
- [ ] JSON + Markdown response formats
- [ ] Pagination for list operations
- [ ] Async/await for all I/O
- [ ] API keys from environment variables
- [ ] Tested with MCP Inspector
- [ ] 10 evaluation questions created
