# Workspace Documentation Portal

Welcome to the centralized documentation hub for `/srv/projects/`. This portal dynamically mounts markdown documentation (`README.md`, `AGENTS.md`, `CHANGELOG.md`, guides, and specifications) across 38+ workspace domains and repositories in real-time.

## Quick Navigation

Use the left navigation sidebar or top search bar to browse documentation grouped by domain and repository:
* **`finance.lan`**: Svelte, API, Infrastructure specifications and drift findings.
* **`hexascript`**: Core, Miner, IDE, and API server architecture.
* **`cheatsheet`**: Quick reference guides (Ollama, Ripgrep, etc.).
* **`budget-analyzer`**: Backend, frontend, and Expo documentation.
* **`helm_charts` / `docker` / `nixpkgs`**: Infrastructure and containerization guides.

## Discovery Architecture

This portal is powered by our dynamic Python discovery scanner (`scanner.py`) and MkDocs lifecycle hook (`hooks/discover_docs.py`), which mount files directly into virtual memory during build without creating symlinks or copying files across disks.
