# Workspace Documentation Server Implementation Plan (`mkdocs`)

## Goal Description

The current `/srv/projects/docs.sh` bash script runs `find` across an **explicit list of 38 starting directory paths** under `/srv/projects/` (`helm_charts`, `hexascript/src/...`, `finance.lan/...`, `python_packages`, `cheatsheet`, etc.) while pruning build directories (`node_modules`, `.git`, `dist`, `.venv`) and excluding standard project boilerplate (`README.md`, `AGENTS.md`, `CLAUDE.md`). However:
1. **Brittle Execution**: When executed (`../docs.sh`), `find` exits with error code `1` because hardcoded target paths like `/srv/projects/finance.lan/react` no longer exist on disk.
2. **Scattered Output**: It outputs a raw flat list of file paths, with no search, navigation hierarchy, or rendered HTML preview.
3. **Server Need**: We want to create a unified documentation server using **Python MkDocs** (`mkdocs-material` + native virtual file hooks) that models `docs.sh`'s behavior almost identically (`SEARCH_PATHS` and directory pruning rules), **with the exception that `README.md`, `AGENTS.md`, and `CHANGELOG.md` are included.**

---

## Architectural Alignment with `docs.sh` Behavior

Instead of scanning the entire `/srv/projects/**` tree (which contains massive archives, node_modules, and unrelated files), our Python scanner (`scanner.py`) and MkDocs virtual hook (`hooks/discover_docs.py`) will **model `docs.sh`'s behavior almost identically**:

1. **Exact Target Search Paths (`SEARCH_PATHS`)**:
   We define the exact 38 target search roots from `docs.sh` in Python:
   ```python
   SEARCH_PATHS: list[str] = [
       "/srv/projects/helm_charts",
       "/srv/projects/jasonpoage.com/expressjs-blog",
       "/srv/projects/hexascript/src/core",
       "/srv/projects/hexascript/src/miner",
       "/srv/projects/hexascript/src/ide",
       "/srv/projects/hexascript/src/api_server",
       "/srv/projects/finance.lan/svelte",
       "/srv/projects/finance.lan/api",
       "/srv/projects/finance.lan/infrastructure",
       "/srv/projects/finance.lan/react",  # Gracefully skipped if missing!
       "/srv/projects/node_packages",
       "/srv/projects/python_packages",
       "/srv/projects/go",
       "/srv/projects/access_manager",
       "/srv/projects/auth_redirect",
       "/srv/projects/auth_server",
       "/srv/projects/bin-selector",
       "/srv/projects/budget-analyzer",
       "/srv/projects/cheatsheet",
       "/srv/projects/clip",
       "/srv/projects/config_loader",
       "/srv/projects/deployment_pipeline",
       "/srv/projects/docker",
       "/srv/projects/dwl",
       "/srv/projects/dwl-patches",
       "/srv/projects/home-manager",
       "/srv/projects/i3-workspace-switcher",
       "/srv/projects/logs",
       "/srv/projects/mail",
       "/srv/projects/nixpkgs",
       "/srv/projects/ollama",
       "/srv/projects/pipeline_runner",
       "/srv/projects/resume",
       "/srv/projects/rootwars",
       "/srv/projects/Rummy",
       "/srv/projects/server_healthcheck",
       "/srv/projects/telemetry",
       "/srv/projects/workspaces",
   ]
   ```
   If any path in `SEARCH_PATHS` does not exist on disk, `scanner.py` gracefully skips it without logging an error or exiting with code `1`.

2. **Identical Directory Pruning (`EXCLUDE_DIRS`)**:
   We prune the exact same build and cache directories that `docs.sh` prunes (`-prune`):
   ```python
   EXCLUDE_DIRS: set[str] = {
       "node_modules", ".git", "dist", "build", "target", "vendor",
       "coverage", ".next", ".svelte-kit", ".cache", ".venv",
       ".pytest_cache", "content", ".terragrunt-cache", ".terraform",
       "www", "test-results", "data"
   }
   ```

3. **Updated File Inclusion Rules**:
   Unlike `docs.sh`, which excluded `README.md`, `AGENTS.md`, and `CLAUDE.md`, our scanner will match `*.md` and `*.markdown` across all valid target directories while **explicitly including `README.md`, `AGENTS.md`, and `CHANGELOG.md`**. (We will continue excluding `CLAUDE.md` and `README` without extension).

---

## Can MkDocs Be Customized Cleanly Without Symlinks?

**Yes.** MkDocs eliminates single-directory restrictions and symlinks through its native **Python Hooks API** (`hooks/discover_docs.py` using `on_files` and `on_nav` lifecycle events):
* **Virtual File Discovery (`on_files`)**: When MkDocs starts (`mkdocs serve` / `mkdocs build`), our Python hook calls `scanner.py` to get all valid markdown files across our `SEARCH_PATHS`. For each file, we create a native `mkdocs.structure.files.File` object in memory pointing directly to its absolute path on disk (`src_path`) and assign it a virtual destination inside the navigation tree (`dest_path`).
* **Zero Symlinks & Zero Copies**: MkDocs mounts and processes these virtual file objects directly in memory, compiling them into rendered HTML without creating symlinks on disk.

---

## Proposed Changes

All changes will be scoped inside `/srv/projects/docs/` and `/srv/projects/docs.sh`.

### 1. Dynamic Discovery Scanner (`scanner.py`)
#### [NEW] `/srv/projects/docs/scanner.py`
A pure Python module (`scanner.py`) with strict type hints and Doxygen-compatible docstrings implementing:
* `get_documentation_files(search_paths: list[str] | None = None) -> list[Path]`: Iterates over `SEARCH_PATHS`, skips non-existent directories, prunes `EXCLUDE_DIRS`, and returns all matching `*.md` / `*.markdown` files (including `README.md`, `AGENTS.md`, `CHANGELOG.md`).
* `main()`: CLI entry point that outputs discovered absolute file paths line by line (matching `docs.sh` output format).

### 2. Bash Script Rewrite (`docs.sh`)
#### [MODIFY] `/srv/projects/docs.sh`
Replace the brittle hardcoded `find` command with a clean wrapper around our Python scanner:
```bash
#!/usr/bin/env bash
# REFACTOR: Dynamic workspace documentation discovery modeling docs.sh behavior via Python scanner.
python3 /srv/projects/docs/scanner.py "$@"
```
This preserves exact backward compatibility with `fdoc.sh` and terminal piping while eliminating missing-directory errors.

### 3. MkDocs Server & Virtual Hook Architecture
#### [NEW] `/srv/projects/docs/mkdocs.yml`
```yaml
site_name: Workspace Documentation Portal
theme:
  name: material
  palette:
    - scheme: slate
      primary: indigo
      accent: cyan
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
    - scheme: default
      primary: indigo
      accent: cyan
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
plugins:
  - search
hooks:
  - hooks/discover_docs.py
```

#### [NEW] `/srv/projects/docs/hooks/discover_docs.py`
The native MkDocs lifecycle hook implementing:
1. `on_files(files, config)`: Calls `scanner.get_documentation_files()` across our exact 38 `SEARCH_PATHS`. Constructs virtual `File(path, src_dir='/srv/projects', dest_dir=config['site_dir'], use_directory_urls=True)` entries and appends them to `files`.
2. `on_nav(nav, config, files)`: Builds a clean, hierarchical navigation structure grouped by Domain/Project (`Finance -> API -> README.md`, `Hexascript -> Core -> AGENTS.md`, `Cheatsheet -> ripgrep.md`, etc.).

---

## Verification Plan

### Automated Tests
* **Unit Testing (`pytest`)**: Create `/srv/projects/docs/tests/test_scanner.py` to verify:
  1. `get_documentation_files()` iterates only `SEARCH_PATHS` without scanning entire `/srv/projects/**`.
  2. Missing paths (`/srv/projects/finance.lan/react`) are skipped cleanly without errors.
  3. Pruned directories (`node_modules`, `.venv`, `dist`, etc.) are excluded.
  4. `README.md`, `AGENTS.md`, and `CHANGELOG.md` are included.
* **Script & CLI Verification**: Execute `/srv/projects/docs.sh` and verify return code `0`, checking output compatibility with `fdoc.sh`.

### Manual Verification
* Run `mkdocs serve -a 127.0.0.1:8000` inside `/srv/projects/docs/`.
* Verify via browser/curl that virtual files across all 38 target paths (`/srv/projects/finance.lan/api/README.md`, `/srv/projects/helm_charts/docs/CHANGELOG.md`, etc.) are mounted and rendered cleanly without any symlinks on disk.
