# Agents

## Commands
```bash
# Run tests
uv run pytest

# Run scanner directly
uv run python3 scanner.py

# Run FastMCP server via stdio
uv run docs-mcp-server

# Serve docs locally
uv run mkdocs serve -a 127.0.0.1:8000
```

## Test
We follow strict Test-Driven Development (TDD). Behavior-based tests in `tests/` must be confirmed failing before new functionality is implemented.

## Architecture
- `scanner.py` defines `get_documentation_files()` which scans `SEARCH_PATHS` across `/srv/projects/`.
- `mcp_server.py` defines `mcp` (`FastMCP`) exposing search, read, create, and edit tools for workspace documentation.
- `hooks/discover_docs.py` binds to `mkdocs` events (`on_files` and `on_nav`).

## Plane
- Workspace: jason-poage
- Project: DOCS
- Base URL: https://issues-lan.jasonpoage.com
