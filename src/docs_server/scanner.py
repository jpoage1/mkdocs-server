"""@brief Dynamic documentation discovery scanner.

Scans configured search roots for markdown documentation files (`README.md`,
`AGENTS.md`, `CHANGELOG.md`, guides, etc.), using exclusion rules modeled
from `docs.sh` behavior. Search paths are loaded from `docs_server.toml`
or the `DOCS_SERVER_SEARCH_PATHS` environment variable.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

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

ENV_VAR_NAME = "DOCS_SERVER_SEARCH_PATHS"


def find_config_file() -> Optional[Path]:
    """@brief Locate `docs_server.toml` by walking up from this file's directory.
    @return Path to config file, or None if not found.
    """
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "docs_server.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_toml_config() -> dict:
    """@brief Load the full TOML config file.
    @return Parsed config dictionary, or empty dict if file missing or invalid.
    """
    config_path = find_config_file()
    if config_path is None:
        return {}
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


_config_cache: Optional[dict] = None


def get_config() -> dict:
    """@brief Get cached TOML config, loading it on first access.
    @return Parsed config dictionary.
    """
    global _config_cache  # noqa: PLW0603
    if _config_cache is None:
        _config_cache = load_toml_config()
    return _config_cache


def load_search_paths() -> List[str]:
    """@brief Load search paths with priority: env var > TOML file > empty default.
    @return List of directory path strings to scan for documentation.
    """
    raw = os.environ.get(ENV_VAR_NAME, "").strip()
    if raw:
        return [p.strip() for p in raw.split(":") if p.strip()]
    return get_config().get("scanner", {}).get("search_paths", [])


def load_allowed_roots() -> List[str]:
    """@brief Load allowed roots from config, falling back to search_paths.
    @return List of root directory path strings the server may read/write.
    """
    roots = get_config().get("scanner", {}).get("allowed_roots", [])
    if roots:
        return roots
    return load_search_paths()


SEARCH_PATHS: List[str] = load_search_paths()
ALLOWED_ROOTS: List[str] = load_allowed_roots()


def load_source_dir() -> str:
    """@brief Load the MkDocs source directory from config, falling back to first search_path parent.
    @return Absolute directory path string for MkDocs virtual file mounting.
    """
    explicit = get_config().get("scanner", {}).get("source_dir")
    if explicit:
        return explicit
    if SEARCH_PATHS:
        return str(Path(SEARCH_PATHS[0]).parent)
    return str(Path.cwd())


SOURCE_DIR: str = load_source_dir()


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
