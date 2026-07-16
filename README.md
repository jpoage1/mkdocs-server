# Workspace Documentation Portal (`/srv/projects/docs`)

## Status
Active development

## Quick Start
```bash
# Sync dependencies via uv
uv sync --extra dev

# Run discovery scanner (models ../docs.sh)
uv run python3 scanner.py

# Run FastMCP server (for AI agents over stdio)
uv run docs-mcp-server # or: uv run python3 mcp_server.py

# Run MkDocs development server
uv run mkdocs serve -a 127.0.0.1:8000
```

### Self-Aware Entrypoint (`entrypoint.sh`)
We also created and verified `entrypoint.sh`, which handles all three operational modes of your documentation portal from a single script:
- `./entrypoint.sh --mcp` → Launches the FastMCP server over `stdio` for AI agents.
- `./entrypoint.sh --serve` → Launches the MkDocs development portal (`http://127.0.0.1:8000`).
- `./entrypoint.sh` → Runs the discovery scanner CLI (`scanner.py`).

## Architecture
- **`entrypoint.sh`**: Self-aware bash launcher for unified execution across scanner, FastMCP, and MkDocs modes.
- **`scanner.py`**: Dynamic discovery scanner across `/srv/projects/` (`SEARCH_PATHS` and `EXCLUDE_DIRS`) matching `docs.sh` behavior while including `README.md`, `AGENTS.md`, and `CHANGELOG.md`.
- **`mcp_server.py`**: FastMCP server providing safe `list_documentation_files`, `search_documentation`, `read_document`, `create_document`, `edit_document`, and `replace_in_document` tools to AI agents.
- **`hooks/discover_docs.py`**: Native MkDocs hook (`on_files` and `on_nav`) that mounts discovered files directly into virtual memory during build/serve without symlinks.
- **`mkdocs.yml`**: Material theme configuration with dark/light toggle and search.

## Related Plane Projects
- **DOCS** (Documentation) — docs-portal, docs-server, and doc normalization.
