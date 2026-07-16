#!/usr/bin/env bash
# ===========================================================================
# workspace-docs-portal — Self-aware entrypoint for MkDocs and FastMCP Server
#
# Usage:
#   ./entrypoint.sh --mcp       # Launch FastMCP server over stdio for AI agents
#   ./entrypoint.sh --serve     # Launch local MkDocs documentation development server
#   ./entrypoint.sh [options]   # Run discovery scanner (default)
# ===========================================================================
set -euo pipefail

SCRIPT_SRC="${BASH_SOURCE[0]}"
while [ -h "$SCRIPT_SRC" ]; do
	SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SRC")" && pwd)"
	SCRIPT_SRC="$(readlink "$SCRIPT_SRC")"
	[[ "$SCRIPT_SRC" != /* ]] && SCRIPT_SRC="$SCRIPT_DIR/$SCRIPT_SRC"
done
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SRC")" && pwd)"

UV_CMD="$(command -v uv 2>/dev/null || true)"
if [[ -z "$UV_CMD" ]]; then
	echo "Error: 'uv' not found on PATH. Install it from https://docs.astral.sh/uv/" >&2
	exit 1
fi

if [[ "${1:-}" == "--mcp" ]]; then
	shift || true
	exec "$UV_CMD" run --project "$SCRIPT_DIR" python3 "$SCRIPT_DIR/src/docs_server/mcp_server.py" "$@"
elif [[ "${1:-}" == "--serve" ]]; then
	shift || true
	exec "$UV_CMD" run --project "$SCRIPT_DIR" mkdocs serve -a 127.0.0.1:8000 "$@"
else
	exec "$UV_CMD" run --project "$SCRIPT_DIR" python3 "$SCRIPT_DIR/src/docs_server/scanner.py" "$@"
fi
