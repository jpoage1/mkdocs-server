# Workspace Documentation Portal

A Python-based documentation server that dynamically discovers and serves markdown files across multiple project directories. Includes an MkDocs site with Material theme and a FastMCP server for AI agent access.

## Status
Active development

## Quick Start
```bash
# Sync dependencies via uv
uv sync --extra dev

# Configure search paths in docs_server.toml, then:
uv run python3 src/docs_server/scanner.py

# Run FastMCP server (for AI agents over stdio)
uv run docs-mcp-server

# Run MkDocs development server
uv run mkdocs serve -a 127.0.0.1:8000
```

### Self-Aware Entrypoint (`entrypoint.sh`)
```bash
./entrypoint.sh --mcp       # Launch FastMCP server over stdio
./entrypoint.sh --serve     # Launch MkDocs dev server
./entrypoint.sh             # Run discovery scanner
```

## Configuration

Create `docs_server.toml` in the project root:
```toml
[scanner]
search_paths = [
    "/path/to/project-a/docs",
    "/path/to/project-b/docs",
]
allowed_roots = [
    "/path/to/project-a",
    "/path/to/project-b",
]
```

Or set the `DOCS_SERVER_SEARCH_PATHS` environment variable (colon-separated paths) to override the TOML file.

## Architecture
- **`entrypoint.sh`**: Bash launcher for scanner, FastMCP, and MkDocs modes.
- **`src/docs_server/scanner.py`**: Discovery scanner with configurable `search_paths` and `allowed_roots`.
- **`src/docs_server/mcp_server.py`**: FastMCP server exposing `list_documentation_files`, `search_documentation`, `read_document`, `create_document`, `edit_document`, and `replace_in_document` tools.
- **`src/docs_server/hooks/discover_docs.py`**: MkDocs hook (`on_files` and `on_nav`) for virtual file mounting.
- **`mkdocs.yml`**: Material theme with dark/light toggle and search.

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. Use at your own risk. The authors and contributors are not responsible for any damage, data loss, or security issues arising from the use of this software. Always review and audit the code before deploying in any environment.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
