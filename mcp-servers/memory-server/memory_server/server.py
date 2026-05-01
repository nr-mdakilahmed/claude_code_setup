"""Memory MCP server.

Exposes per-project memory (architecture.md, todo.md, lessons.md, history.md,
plans/) as pull-on-demand MCP tools, so Claude doesn't have to @-load the full
set at session start.

Config: server is pinned to one repo via --repo-name on startup. All queries
resolve against ~/.claude/projects/<repo-name>/.

Tools:
  - get_memory(topic: str) -> file contents
  - search_memory(query: str, k: int) -> ranked snippets across memory files
  - list_lessons(tag: str | None, recent: int | None) -> filtered lesson items
  - get_todo(status: str) -> active|backlog|done items
  - recall_plan(slug: str | None) -> plan file content (or list if slug omitted)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config (bound at startup via CLI args)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    project_root: Path
    memory_dir: Path
    plans_dir: Path
    graphs_dir: Path

    @classmethod
    def from_repo_name(cls, repo_name: str) -> "Config":
        base = Path.home() / ".claude" / "projects" / repo_name
        if not base.exists():
            raise SystemExit(
                f"memory-server: project dir not found for '{repo_name}' at {base}. "
                "Run /bootstrap in the repo first."
            )
        return cls(
            project_root=base,
            memory_dir=base / "memory",
            plans_dir=base / "plans",
            graphs_dir=base / "graphs",
        )


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


_VALID_TOPICS = {
    "architecture",
    "todo",
    "lessons",
    "history",
    "hot",
    "memory",  # MEMORY.md (the index)
    "graph_report",
}


def _read_topic(config: Config, topic: str) -> str:
    """Resolve a topic name to a memory file and read it."""
    topic_lower = topic.lower().strip()
    if topic_lower == "graph_report":
        path = config.graphs_dir / "GRAPH_REPORT.md"
    elif topic_lower == "memory":
        path = config.memory_dir / "MEMORY.md"
    elif topic_lower in _VALID_TOPICS:
        path = config.memory_dir / f"{topic_lower}.md"
    else:
        valid = ", ".join(sorted(_VALID_TOPICS))
        return f"Error: unknown topic '{topic}'. Valid topics: {valid}"

    if not path.exists():
        return f"Error: {path} does not exist. Memory may be empty."
    return path.read_text(encoding="utf-8")


def _grep_file(path: Path, query: str, context_lines: int = 2) -> list[str]:
    """Return matching lines from a file with surrounding context."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    hits: list[str] = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            snippet = "\n".join(lines[start:end])
            hits.append(f"[{path.name}:L{i+1}]\n{snippet}")
    return hits


def _search_across(
    config: Config,
    query: str,
    k: int,
    files: list[Path] | None = None,
) -> str:
    """Grep-based multi-file search. Ranks by hit count per file."""
    targets = files or [
        config.memory_dir / "hot.md",
        config.memory_dir / "architecture.md",
        config.memory_dir / "lessons.md",
        config.memory_dir / "todo.md",
        config.memory_dir / "history.md",
    ]
    all_hits: list[tuple[str, str]] = []
    for path in targets:
        for hit in _grep_file(path, query):
            all_hits.append((path.name, hit))
    if not all_hits:
        return f"No matches for '{query}' in memory."

    top = all_hits[:k]
    out = [f"Found {len(all_hits)} match(es) for '{query}' (showing top {len(top)}):", ""]
    out.extend(hit for _, hit in top)
    return "\n\n---\n\n".join(out) if len(top) > 1 else "\n".join(out)


def _extract_section(path: Path, section_header: str) -> list[str]:
    """Extract bullet items from a specific H2 section."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = line.strip() == f"## {section_header}"
            continue
        if in_section and line.startswith("- "):
            items.append(line.lstrip("- ").rstrip())
    return items


# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------


def build_server(config: Config) -> FastMCP:
    mcp = FastMCP(
        name=f"memory-server ({config.project_root.name})",
        instructions=(
            "Per-project memory retrieval. Prefer these tools over @-loading "
            "full memory files. Use get_memory for targeted topic reads, "
            "search_memory for cross-file keyword hunts, list_lessons for "
            "filtered patterns, get_todo for task status, recall_plan for "
            "past-session plans."
        ),
    )

    @mcp.tool
    def get_memory(topic: str) -> str:
        """Read a specific memory file.

        Args:
            topic: One of 'architecture', 'todo', 'lessons', 'history', 'hot',
                   'memory' (the index), 'graph_report'.

        Returns:
            Full contents of the file, or an error message.
        """
        return _read_topic(config, topic)

    @mcp.tool
    def search_memory(query: str, k: int = 5) -> str:
        """Keyword search across all memory files.

        Args:
            query: Text to search for (case-insensitive).
            k: Max number of snippets to return. Default 5.

        Returns:
            Ranked snippets with file + line number annotations.
        """
        return _search_across(config, query, k)

    @mcp.tool
    def list_lessons(tag: str | None = None, recent: int | None = None) -> str:
        """List lessons, optionally filtered by tag or recency.

        Args:
            tag: If given, only lessons whose body contains this tag (case-insensitive).
            recent: If given, return only the last N items.

        Returns:
            Newline-joined list of lesson entries from the Patterns section.
        """
        items = _extract_section(config.memory_dir / "lessons.md", "Patterns")
        if tag:
            t = tag.lower()
            items = [i for i in items if t in i.lower()]
        if recent is not None and recent > 0:
            items = items[-recent:]
        if not items:
            return "(no matching lessons)"
        return "\n".join(f"- {i}" for i in items)

    @mcp.tool
    def get_todo(status: str = "active") -> str:
        """Get todo items by status.

        Args:
            status: 'active', 'backlog', or 'done'.

        Returns:
            Newline-joined list of todo entries under that section.
        """
        section = status.capitalize()
        if section not in {"Active", "Backlog", "Done"}:
            return f"Error: status must be 'active', 'backlog', or 'done' (got '{status}')."
        items = _extract_section(config.memory_dir / "todo.md", section)
        if not items:
            return f"(no items in {section})"
        return "\n".join(f"- {i}" for i in items)

    @mcp.tool
    def recall_plan(slug: str | None = None) -> str:
        """Get a plan by slug, or list all plans if slug is None.

        Args:
            slug: Filename stem (without .md) of a plan in the plans/ dir.

        Returns:
            Plan contents, a list of available slugs, or an error.
        """
        if not config.plans_dir.exists():
            return "(no plans/ dir for this project; run /wrap-up to mirror from ~/.claude/plans/)"
        if slug is None:
            plans = sorted(config.plans_dir.glob("*.md"))
            if not plans:
                return "(no plans mirrored yet)"
            return "\n".join(p.stem for p in plans)
        path = config.plans_dir / f"{slug}.md"
        if not path.exists():
            return f"Error: plan '{slug}' not found at {path}"
        return path.read_text(encoding="utf-8")

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory MCP server")
    parser.add_argument(
        "--repo-name",
        required=True,
        help="Repo name under ~/.claude/projects/ (e.g., 'om-airflow-dags')",
    )
    args = parser.parse_args()

    config = Config.from_repo_name(args.repo_name)
    server = build_server(config)
    # FastMCP 2.x uses stdio by default
    server.run()


if __name__ == "__main__":
    main()
