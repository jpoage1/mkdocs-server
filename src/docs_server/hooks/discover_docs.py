"""@brief Native MkDocs lifecycle hook for virtual documentation discovery and mounting.

Dynamically scans configured search roots during `mkdocs serve` or `mkdocs build` and mounts
discovered files as virtual File entries without creating symlinks or copying files.
"""

from pathlib import Path
from typing import Any, Dict
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation

from docs_server import scanner
from docs_server.config import get_settings


def is_already_in_files(file_path: Path, files: Files) -> bool:
    """@brief Check if a candidate file path is already present in MkDocs files.
    @param file_path Absolute path of the candidate file.
    @param files Current MkDocs Files collection.
    @return True if already present, False otherwise.
    """
    source_dir = get_settings().source_dir or ""
    try:
        rel_str = str(file_path.relative_to(source_dir))
    except ValueError:
        rel_str = file_path.name

    for existing_file in files:
        if existing_file.src_path == rel_str or existing_file.abs_src_path == str(
            file_path
        ):
            return True
    return False


def inject_virtual_file(file_path: Path, files: Files, config: Dict[str, Any]) -> None:
    """@brief Create and append a virtual File instance for an external documentation path.
    @param file_path Absolute path of the documentation file to mount.
    @param files Current MkDocs Files collection to append to.
    @param config MkDocs configuration dictionary containing site_dir and URL settings.
    """
    source_dir = get_settings().source_dir or ""
    try:
        rel_path = file_path.relative_to(source_dir)
    except ValueError:
        rel_path = Path(file_path.name)

    virtual_file = File(
        path=str(rel_path),
        src_dir=source_dir,
        dest_dir=config.get("site_dir", ""),
        use_directory_urls=config.get("use_directory_urls", True),
    )
    files.append(virtual_file)


def on_files(files: Files, config: Dict[str, Any]) -> Files:
    """@brief MkDocs event hook executed after initial files discovery.
    @param files Initial Files collection discovered from docs_dir.
    @param config MkDocs configuration dictionary.
    @return Updated Files collection including all dynamically discovered virtual documentation files.
    """
    discovered_files = scanner.get_documentation_files()
    for file_path in discovered_files:
        if not is_already_in_files(file_path, files):
            inject_virtual_file(file_path, files, config)
    return files


def on_nav(nav: Navigation, config: Dict[str, Any], files: Files) -> Navigation:
    """@brief MkDocs event hook executed after navigation structure is constructed.
    @param nav Initial Navigation structure.
    @param config MkDocs configuration dictionary.
    @param files Complete collection of discovered files.
    @return Finalized Navigation structure.
    """
    return nav
