# Workspace Documentation Portal

Welcome to the centralized documentation hub. This portal dynamically mounts markdown documentation (`README.md`, `AGENTS.md`, `CHANGELOG.md`, guides, and specifications) across your configured project directories in real-time.

## Quick Navigation

Use the left navigation sidebar or top search bar to browse documentation. The sidebar is populated automatically from your configured `search_paths` in `docs_server.toml`.

## Discovery Architecture

This portal is powered by a dynamic Python discovery scanner (`src/docs_server/scanner.py`) and MkDocs lifecycle hook (`src/docs_server/hooks/discover_docs.py`), which mount files directly into virtual memory during build without creating symlinks or copying files across disks.
