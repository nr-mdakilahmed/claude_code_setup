#!/usr/bin/env bash
# scaffold-server.sh — create a minimal MCP server skeleton (Python or TypeScript).
# Usage: scaffold-server.sh --lang python|typescript --name <server-name>
set -euo pipefail

LANG=""
NAME=""

usage() {
  cat <<'EOF'
scaffold-server.sh — scaffold a minimal MCP server skeleton.

Usage:
  scaffold-server.sh --lang python|typescript --name <server-name>
  scaffold-server.sh --help

Options:
  --lang   Language flavor: "python" (FastMCP) or "typescript" (@modelcontextprotocol/sdk).
  --name   Server name in kebab-case (e.g. github-mcp). Used as the directory name.
  --help   Show this help and exit 0.

The script creates a directory <name>/ in the current working directory, writes
a language-appropriate manifest (pyproject.toml or package.json) with the MCP
SDK dependency, and drops a minimal server file exposing one example tool.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)
      [[ $# -ge 2 ]] || { echo "error: --lang requires a value" >&2; exit 2; }
      LANG="$2"; shift 2 ;;
    --name)
      [[ $# -ge 2 ]] || { echo "error: --name requires a value" >&2; exit 2; }
      NAME="$2"; shift 2 ;;
    --help|-h)
      usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2 ;;
  esac
done

if [[ -z "$LANG" || -z "$NAME" ]]; then
  echo "error: --lang and --name are required" >&2
  usage >&2
  exit 2
fi

case "$LANG" in
  python|typescript) ;;
  *) echo "error: --lang must be 'python' or 'typescript', got '$LANG'" >&2; exit 2 ;;
esac

if [[ ! "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "error: --name must be kebab-case (lowercase, digits, hyphens): got '$NAME'" >&2
  exit 2
fi

if [[ -e "$NAME" ]]; then
  echo "error: '$NAME' already exists in $(pwd)" >&2
  exit 1
fi

mkdir -p "$NAME"

if [[ "$LANG" == "python" ]]; then
  # Underscored module name for Python import.
  MODULE="${NAME//-/_}"
  mkdir -p "$NAME/src/$MODULE"

  cat > "$NAME/pyproject.toml" <<EOF
[project]
name = "$NAME"
version = "0.1.0"
description = "MCP server: $NAME"
requires-python = ">=3.10"
dependencies = [
  "mcp[cli]>=1.0.0",
  "httpx>=0.27",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
$NAME = "$MODULE.server:main"

[tool.hatch.build.targets.wheel]
packages = ["src/$MODULE"]
EOF

  cat > "$NAME/src/$MODULE/__init__.py" <<EOF
"""MCP server package: $NAME."""
EOF

  cat > "$NAME/src/$MODULE/server.py" <<EOF
"""Minimal FastMCP server scaffold for $NAME.

Run locally:
  python -m $MODULE.server

Smoke test with Inspector:
  npx @modelcontextprotocol/inspector -- python -m $MODULE.server
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

server = FastMCP("$NAME")


@server.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def ${MODULE}_ping(message: str = "hello") -> dict:
    """Echoes the input message. Replace with a real tool."""
    return {"echo": message}


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
EOF

  cat > "$NAME/.env.example" <<'EOF'
# API credentials go here; never commit the real .env file.
API_KEY=
EOF

  cat > "$NAME/.gitignore" <<'EOF'
.env
.venv/
__pycache__/
*.egg-info/
dist/
build/
EOF

  echo "Scaffolded Python MCP server at $(pwd)/$NAME"
  echo "Next steps:"
  echo "  cd $NAME && uv sync   # or: pip install -e ."
  echo "  python -m $MODULE.server"
  echo "  npx @modelcontextprotocol/inspector -- python -m $MODULE.server"

else
  # typescript
  mkdir -p "$NAME/src"

  cat > "$NAME/package.json" <<EOF
{
  "name": "$NAME",
  "version": "0.1.0",
  "description": "MCP server: $NAME",
  "type": "module",
  "bin": {
    "$NAME": "dist/server.js"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "inspector": "npx @modelcontextprotocol/inspector -- node dist/server.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/node": "^20.0.0"
  }
}
EOF

  cat > "$NAME/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts"]
}
EOF

  cat > "$NAME/src/server.ts" <<EOF
/**
 * Minimal MCP server scaffold for $NAME.
 *
 * Build:   npm run build
 * Run:     node dist/server.js
 * Inspect: npm run inspector
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new Server(
  { name: "$NAME", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.tool(
  "${NAME//-/_}_ping",
  { message: z.string().default("hello") },
  {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false,
  },
  async ({ message }) => ({
    content: [{ type: "text", text: JSON.stringify({ echo: message }) }],
  }),
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

  cat > "$NAME/.env.example" <<'EOF'
# API credentials go here; never commit the real .env file.
API_KEY=
EOF

  cat > "$NAME/.gitignore" <<'EOF'
.env
node_modules/
dist/
*.log
EOF

  echo "Scaffolded TypeScript MCP server at $(pwd)/$NAME"
  echo "Next steps:"
  echo "  cd $NAME && npm install && npm run build"
  echo "  node dist/server.js"
  echo "  npm run inspector"
fi
