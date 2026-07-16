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

if [[ "${1:-}" == "--mcp" ]]; then
  shift || true
  exec /etc/profiles/per-user/me/bin/uv run --project "$SCRIPT_DIR" python3 "$SCRIPT_DIR/mcp_server.py" "$@"
elif [[ "${1:-}" == "--serve" ]]; then
  shift || true
  exec /etc/profiles/per-user/me/bin/uv run --project "$SCRIPT_DIR" mkdocs serve -a 127.0.0.1:8000 "$@"
else
  exec /etc/profiles/per-user/me/bin/uv run --project "$SCRIPT_DIR" python3 "$SCRIPT_DIR/scanner.py" "$@"
fi
