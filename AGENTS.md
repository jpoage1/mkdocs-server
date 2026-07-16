# Agents

## Commands
```bash
# Run tests
uv run pytest

# Run scanner directly
uv run python3 src/docs_server/scanner.py

# Run FastMCP server via stdio
uv run docs-mcp-server

# Serve docs locally
uv run mkdocs serve -a 127.0.0.1:8000
```

## Test
We follow strict Test-Driven Development (TDD). Behavior-based tests in `tests/` must be confirmed failing before new functionality is implemented.

## Architecture
- `src/docs_server/scanner.py` defines `get_documentation_files()` which scans `SEARCH_PATHS` from `docs_server.toml`.
- `src/docs_server/mcp_server.py` defines `mcp` (`FastMCP`) exposing search, read, create, and edit tools for workspace documentation.
- `src/docs_server/hooks/discover_docs.py` binds to `mkdocs` events (`on_files` and `on_nav`).

## Configuration
- `docs_server.toml` holds `search_paths` and `allowed_roots`.
- Env var `DOCS_SERVER_SEARCH_PATHS` (colon-separated) overrides TOML `search_paths`.
