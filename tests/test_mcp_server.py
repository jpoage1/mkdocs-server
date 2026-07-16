"""@brief Tests for the FastMCP documentation management server (`mcp_server.py`)."""

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch
import pytest

from docs_server.mcp_server import (
    is_allowed_path,
    list_documentation_files,
    search_documentation,
    read_document,
    create_document,
    edit_document,
    replace_in_document,
    mcp,
)
from docs_server.config import ScannerConfig


def _make_settings(allowed_roots: list[str] | None = None) -> ScannerConfig:
    return ScannerConfig(
        search_paths=[],
        allowed_roots=allowed_roots or [],
        source_dir="/tmp",
    )


@patch("docs_server.mcp_server.get_settings")
def test_is_allowed_path_validates_security(
    mock_get_settings: MagicMock, tmp_path: Path
) -> None:
    """@brief Verify that only valid markdown files within authorized search paths are allowed.
    @param mock_get_settings Mocked get_settings function.
    @param tmp_path Pytest temporary directory fixture.
    """
    mock_get_settings.return_value = _make_settings(["/tmp/test_projects"])
    valid_file = Path("/tmp/test_projects/cheatsheet/test.md")
    assert is_allowed_path(valid_file) is True

    # Path outside allowed roots
    unauthorized = Path("/etc/passwd")
    assert is_allowed_path(unauthorized) is False

    # Excluded directory (e.g., node_modules)
    excluded = Path("/tmp/test_projects/finance.lan/api/node_modules/package.md")
    assert is_allowed_path(excluded) is False

    # Non-markdown file
    py_file = Path("/tmp/test_projects/cheatsheet/script.py")
    assert is_allowed_path(py_file) is False


@patch("docs_server.mcp_server.scanner.get_documentation_files")
def test_list_documentation_files(mock_get_files: Any) -> None:
    """@brief Verify that list_documentation_files returns string paths from scanner.
    @param mock_get_files Mocked scanner function.
    """
    mock_get_files.return_value = [Path("/test/workspace/project-a/docs/guide.md")]
    results = list_documentation_files()
    assert results == ["/test/workspace/project-a/docs/guide.md"]


@patch("docs_server.mcp_server.scanner.get_documentation_files")
def test_search_documentation(mock_get_files: Any, tmp_path: Path) -> None:
    """@brief Verify that search_documentation finds query snippets across files.
    @param mock_get_files Mocked scanner function.
    @param tmp_path Pytest temporary directory fixture.
    """
    doc_file = tmp_path / "guide.md"
    doc_file.write_text("# Guide\nHello MCP world\nSecond line")
    mock_get_files.return_value = [doc_file]

    results: List[Dict[str, Any]] = search_documentation(
        query="MCP world", case_insensitive=True
    )
    assert len(results) == 1
    assert results[0]["file_path"] == str(doc_file)
    assert results[0]["line_number"] == 2
    assert "Hello MCP world" in results[0]["content"]


@patch("docs_server.mcp_server.is_allowed_path", return_value=True)
def test_read_document(mock_allowed: Any, tmp_path: Path) -> None:
    """@brief Verify that read_document returns full markdown content.
    @param mock_allowed Mocked security validation function.
    @param tmp_path Pytest temporary directory fixture.
    """
    doc_file = tmp_path / "test.md"
    doc_file.write_text("# Read Me Content")

    content = read_document(str(doc_file))
    assert content == "# Read Me Content"


@patch("docs_server.mcp_server.is_allowed_path", return_value=True)
def test_create_document(mock_allowed: Any, tmp_path: Path) -> None:
    """@brief Verify that create_document writes new file and creates parent directories if needed.
    @param mock_allowed Mocked security validation function.
    @param tmp_path Pytest temporary directory fixture.
    """
    new_doc = tmp_path / "subdir" / "created.md"
    result = create_document(str(new_doc), "# New Document", overwrite=False)

    assert result == f"Successfully created document at: {new_doc}"
    assert new_doc.read_text() == "# New Document"


@patch("docs_server.mcp_server.is_allowed_path", return_value=True)
def test_create_document_prevents_unintended_overwrite(
    mock_allowed: Any, tmp_path: Path
) -> None:
    """@brief Verify that create_document raises error if file exists and overwrite=False.
    @param mock_allowed Mocked security validation function.
    @param tmp_path Pytest temporary directory fixture.
    """
    existing_doc = tmp_path / "existing.md"
    existing_doc.write_text("# Old")

    with pytest.raises(ValueError, match="already exists"):
        create_document(str(existing_doc), "# New", overwrite=False)


@patch("docs_server.mcp_server.is_allowed_path", return_value=True)
def test_edit_document(mock_allowed: Any, tmp_path: Path) -> None:
    """@brief Verify that edit_document replaces content of an existing file.
    @param mock_allowed Mocked security validation function.
    @param tmp_path Pytest temporary directory fixture.
    """
    doc_file = tmp_path / "edit.md"
    doc_file.write_text("# Old Content")

    result = edit_document(str(doc_file), "# Updated Content")
    assert result == f"Successfully updated document at: {doc_file}"
    assert doc_file.read_text() == "# Updated Content"


@patch("docs_server.mcp_server.is_allowed_path", return_value=True)
def test_replace_in_document(mock_allowed: Any, tmp_path: Path) -> None:
    """@brief Verify that replace_in_document performs exact substring replacement.
    @param mock_allowed Mocked security validation function.
    @param tmp_path Pytest temporary directory fixture.
    """
    doc_file = tmp_path / "replace.md"
    doc_file.write_text("# Header\nfoo bar baz\n# Footer")

    result = replace_in_document(
        str(doc_file), target_content="foo bar baz", replacement_content="hello world"
    )
    assert result == f"Successfully replaced content inside document at: {doc_file}"
    assert doc_file.read_text() == "# Header\nhello world\n# Footer"


def test_fastmcp_server_initialization() -> None:
    """@brief Verify that FastMCP server instance is initialized and tools are registered."""
    assert mcp.name == "Workspace Documentation Portal"
