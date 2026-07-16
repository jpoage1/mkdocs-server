"""@brief FastMCP server for discovering, reading, creating, and editing workspace markdown documentation."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

import scanner

mcp = FastMCP("Workspace Documentation Portal")


def has_excluded_directory(path_obj: Path) -> bool:
    """@brief Check if any directory part of a path matches an excluded or hidden pattern.
    @param path_obj Path object to check.
    @return True if any parent directory is excluded or hidden dot-dir, False otherwise.
    """
    for part in path_obj.parts[:-1]:
        if scanner.is_excluded_directory(part):
            return True
    return False


def is_allowed_path(path_obj: Path) -> bool:
    """@brief Validate if a path is an authorized markdown documentation file location.
    @param path_obj Candidate Path to check.
    @return True if path is secure and within authorized search roots, False otherwise.
    """
    if not scanner.is_valid_doc_file(path_obj):
        return False
    if has_excluded_directory(path_obj):
        return False

    abs_str = str(path_obj.resolve() if path_obj.exists() else path_obj)
    if abs_str.startswith("/srv/projects/docs"):
        return True

    for root in scanner.SEARCH_PATHS:
        if abs_str.startswith(root):
            return True
    return False


def validate_path_security(file_path_str: str, require_exists: bool = False) -> Path:
    """@brief Validate path authorization and optionally verify file existence.
    @param file_path_str String path to validate.
    @param require_exists If True, verify that the file actually exists on disk.
    @return Validated Path object.
    """
    path_obj = Path(file_path_str)
    if not is_allowed_path(path_obj):
        raise PermissionError(f"Unauthorized path or invalid markdown documentation file: {file_path_str}")
    if require_exists and not path_obj.exists():
        raise FileNotFoundError(f"Documentation file not found: {file_path_str}")
    return path_obj


def search_single_file(file_path: Path, query: str, case_insensitive: bool) -> List[Dict[str, Any]]:
    """@brief Search for a text query inside a single markdown documentation file.
    @param file_path Path object of the file to search.
    @param query Text string to search for.
    @param case_insensitive Whether matching should ignore case.
    @return List of matching line dictionaries containing file_path, line_number, and content.
    """
    matches: List[Dict[str, Any]] = []
    try:
        lines = file_path.read_text(errors="ignore").splitlines()
    except Exception:
        return matches

    target_query = query.lower() if case_insensitive else query
    for line_num, line in enumerate(lines, start=1):
        target_line = line.lower() if case_insensitive else line
        if target_query in target_line:
            matches.append({
                "file_path": str(file_path),
                "line_number": line_num,
                "content": line.strip(),
            })
    return matches


@mcp.tool()
def list_documentation_files() -> List[str]:
    """@brief Discover and return all workspace markdown documentation file paths.
    @return List of absolute file path strings.
    """
    return [str(p) for p in scanner.get_documentation_files()]


@mcp.tool()
def search_documentation(query: str, case_insensitive: bool = True) -> List[Dict[str, Any]]:
    """@brief Search inside all discovered markdown documentation files for keywords.
    @param query Keyword or phrase to search for.
    @param case_insensitive Whether to perform case-insensitive matching (default True).
    @return List of match dictionaries containing file_path, line_number, and content snippet.
    """
    discovered = scanner.get_documentation_files()
    results: List[Dict[str, Any]] = []
    for doc_path in discovered:
        results.extend(search_single_file(doc_path, query, case_insensitive))
    return results


@mcp.tool()
def read_document(file_path: str) -> str:
    """@brief Read the full text content of an authorized markdown document.
    @param file_path Absolute path to the markdown file to read.
    @return Full text content of the markdown file.
    """
    path_obj = validate_path_security(file_path, require_exists=True)
    return path_obj.read_text()


@mcp.tool()
def create_document(file_path: str, content: str, overwrite: bool = False) -> str:
    """@brief Create a new markdown document at the specified path.
    @param file_path Absolute path where the markdown file should be created.
    @param content Markdown text content to write.
    @param overwrite If True, overwrite existing file without error (default False).
    @return Confirmation status message string.
    """
    path_obj = validate_path_security(file_path, require_exists=False)
    if path_obj.exists() and not overwrite:
        raise ValueError(f"Document already exists at {file_path}. Set overwrite=True to overwrite.")

    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(content)
    return f"Successfully created document at: {path_obj}"


@mcp.tool()
def edit_document(file_path: str, content: str) -> str:
    """@brief Replace the entire text content of an existing markdown document.
    @param file_path Absolute path of the markdown file to edit.
    @param content New markdown text content.
    @return Confirmation status message string.
    """
    path_obj = validate_path_security(file_path, require_exists=True)
    path_obj.write_text(content)
    return f"Successfully updated document at: {path_obj}"


@mcp.tool()
def replace_in_document(file_path: str, target_content: str, replacement_content: str) -> str:
    """@brief Perform precise substring replacement inside an existing markdown document.
    @param file_path Absolute path of the markdown file to edit.
    @param target_content Exact text string or block to find and replace.
    @param replacement_content New text string to substitute in place of target_content.
    @return Confirmation status message string.
    """
    path_obj = validate_path_security(file_path, require_exists=True)
    current_text = path_obj.read_text()
    if target_content not in current_text:
        raise ValueError(f"Target content not found in document: {file_path}")

    updated_text = current_text.replace(target_content, replacement_content)
    path_obj.write_text(updated_text)
    return f"Successfully replaced content inside document at: {path_obj}"


def main() -> None:
    """@brief CLI entry point for running the FastMCP documentation server via stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
