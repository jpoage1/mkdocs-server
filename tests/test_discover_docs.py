"""@brief Tests for the MkDocs virtual file discovery hook (`hooks/discover_docs.py`)."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from mkdocs.structure.files import Files, File

from docs_server.hooks.discover_docs import on_files
from docs_server.config import ScannerConfig


def _make_settings(source_dir: str = "/test/workspace") -> ScannerConfig:
    return ScannerConfig(
        search_paths=[],
        allowed_roots=[],
        source_dir=source_dir,
    )


@patch("docs_server.hooks.discover_docs.get_settings")
@patch("docs_server.hooks.discover_docs.scanner.get_documentation_files")
def test_on_files_injects_virtual_files(
    mock_get_files: MagicMock,
    mock_get_settings: MagicMock,
    tmp_path: Path,
) -> None:
    """@brief Verify that on_files discovers files via scanner and injects virtual File entries.
    @param mock_get_files Mocked get_documentation_files scanner function.
    @param mock_get_settings Mocked get_settings function.
    @param tmp_path Pytest temporary directory fixture.
    """
    mock_get_settings.return_value = _make_settings()
    mock_file_1 = Path("/test/workspace/project-a/docs/guide.md")
    mock_file_2 = Path("/test/workspace/project-b/README.md")
    mock_get_files.return_value = [mock_file_1, mock_file_2]

    config = {
        "site_dir": str(tmp_path / "site"),
        "use_directory_urls": True,
    }
    existing_files = Files([])

    updated_files = on_files(existing_files, config)

    assert len(updated_files) == 2
    src_paths = [f.src_path for f in updated_files]
    assert "project-a/docs/guide.md" in src_paths
    assert "project-b/README.md" in src_paths


@patch("docs_server.hooks.discover_docs.get_settings")
@patch("docs_server.hooks.discover_docs.scanner.get_documentation_files")
def test_on_files_avoids_duplicates(
    mock_get_files: MagicMock,
    mock_get_settings: MagicMock,
    tmp_path: Path,
) -> None:
    """@brief Verify that existing files are not duplicated by virtual injection.
    @param mock_get_files Mocked get_documentation_files scanner function.
    @param mock_get_settings Mocked get_settings function.
    @param tmp_path Pytest temporary directory fixture.
    """
    mock_get_settings.return_value = _make_settings()
    mock_file_1 = Path("/test/workspace/project-a/docs/guide.md")
    mock_get_files.return_value = [mock_file_1]

    config = {
        "site_dir": str(tmp_path / "site"),
        "use_directory_urls": True,
    }
    existing_file = File(
        path="project-a/docs/guide.md",
        src_dir="/test/workspace",
        dest_dir=config["site_dir"],
        use_directory_urls=True,
    )
    existing_files = Files([existing_file])

    updated_files = on_files(existing_files, config)

    assert len(updated_files) == 1
