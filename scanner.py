"""@brief Dynamic documentation discovery scanner across `/srv/projects/`.

Models `/srv/projects/docs.sh` search roots and directory exclusion rules while explicitly
including `README.md`, `AGENTS.md`, and `CHANGELOG.md`.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

EXCLUDE_DIRS: set[str] = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "target",
    "vendor",
    "coverage",
    ".next",
    ".svelte-kit",
    ".cache",
    ".venv",
    ".pytest_cache",
    "content",
    ".terragrunt-cache",
    ".terraform",
    "www",
    "test-results",
    "data",
}

EXCLUDE_FILES: set[str] = {
    "CLAUDE.md",
    "README",
}

SEARCH_PATHS: List[str] = [
    "/srv/projects/helm_charts",
    "/srv/projects/jasonpoage.com/expressjs-blog",
    "/srv/projects/hexascript/src/core",
    "/srv/projects/hexascript/src/miner",
    "/srv/projects/hexascript/src/ide",
    "/srv/projects/hexascript/src/api_server",
    "/srv/projects/finance.lan/svelte",
    "/srv/projects/finance.lan/api",
    "/srv/projects/finance.lan/infrastructure",
    "/srv/projects/finance.lan/react",
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


def is_excluded_directory(dir_name: str) -> bool:
    """@brief Determine if a directory name matches an excluded pattern.
    @param dir_name Name of the directory to check.
    @return True if directory must be pruned, False otherwise.
    """
    return dir_name.startswith(".") or dir_name in EXCLUDE_DIRS


def is_valid_doc_file(file_path: Path) -> bool:
    """@brief Check if a file path is a valid documentation markdown file.
    @param file_path Path object to inspect.
    @return True if file is valid markdown documentation, False otherwise.
    """
    if file_path.name in EXCLUDE_FILES:
        return False
    return file_path.suffix.lower() in (".md", ".markdown")


def filter_directories(dirs: List[str]) -> None:
    """@brief Prune excluded directories in-place during directory traversal.
    @param dirs Mutable list of subdirectory names from os.walk.
    """
    dirs[:] = [d for d in dirs if not is_excluded_directory(d)]


def extract_valid_files(root: str, files: List[str]) -> List[Path]:
    """@brief Extract valid markdown documentation files from a directory listing.
    @param root Absolute directory path currently being traversed.
    @param files List of filenames inside the root directory.
    @return List of matching Path objects.
    """
    return [
        Path(root) / filename
        for filename in files
        if is_valid_doc_file(Path(root) / filename)
    ]


def scan_single_directory(root_path: Path) -> List[Path]:
    """@brief Recursively traverse and discover documentation files in one root directory.
    @param root_path Absolute directory Path to traverse.
    @return List of discovered documentation Path objects.
    """
    discovered: List[Path] = []
    for root, dirs, files in os.walk(root_path):
        filter_directories(dirs)
        discovered.extend(extract_valid_files(root, files))
    return discovered


def process_search_path(search_path_str: str) -> List[Path]:
    """@brief Inspect and scan a single candidate search path if valid and existing.
    @param search_path_str Absolute directory path string to inspect.
    @return List of discovered documentation Path objects from this root.
    """
    path_obj = Path(search_path_str)
    if not path_obj.exists() or not path_obj.is_dir():
        return []
    return scan_single_directory(path_obj)


def get_documentation_files(search_paths: Optional[List[str]] = None) -> List[Path]:
    """@brief Discover all documentation files across configured or provided roots.
    @param search_paths Optional custom list of directory path strings; defaults to SEARCH_PATHS.
    @return Sorted list of unique discovered documentation Path objects.
    """
    target_paths = search_paths if search_paths is not None else SEARCH_PATHS
    results: List[Path] = []
    for path_str in target_paths:
        results.extend(process_search_path(path_str))
    return sorted(list(set(results)))


def print_file_path(path_obj: Path) -> None:
    """@brief Print a single file path to standard output.
    @param path_obj Path object to output.
    """
    print(str(path_obj))


def main() -> int:
    """@brief CLI entry point for the documentation discovery scanner.
    @return Exit status code (0 for success).
    """
    custom_paths = sys.argv[1:] if len(sys.argv) > 1 else None
    files = get_documentation_files(custom_paths)
    for file_path in files:
        print_file_path(file_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
