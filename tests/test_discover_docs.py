"""@brief Tests for the MkDocs virtual file discovery hook (`hooks/discover_docs.py`)."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from mkdocs.structure.files import Files, File

# Attempt to import hook; if not yet implemented, this will fail cleanly (Red phase of TDD)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from hooks.discover_docs import on_files
except ImportError:
    pass


@patch("hooks.discover_docs.scanner.get_documentation_files")
def test_on_files_injects_virtual_files(mock_get_files: MagicMock, tmp_path: Path) -> None:
    """@brief Verify that on_files discovers files via scanner and injects virtual File entries.
    @param mock_get_files Mocked get_documentation_files scanner function.
    @param tmp_path Pytest temporary directory fixture.
    """
    # Create fake files inside /srv/projects structure
    mock_file_1 = Path("/srv/projects/cheatsheet/ripgrep.md")
    mock_file_2 = Path("/srv/projects/finance.lan/api/README.md")
    mock_get_files.return_value = [mock_file_1, mock_file_2]

    # Create dummy mkdocs config
    config = {
        "site_dir": str(tmp_path / "site"),
        "use_directory_urls": True,
    }
    existing_files = Files([])

    updated_files = on_files(existing_files, config)

    assert len(updated_files) == 2
    src_paths = [f.src_path for f in updated_files]
    assert "cheatsheet/ripgrep.md" in src_paths
    assert "finance.lan/api/README.md" in src_paths


@patch("hooks.discover_docs.scanner.get_documentation_files")
def test_on_files_avoids_duplicates(mock_get_files: MagicMock, tmp_path: Path) -> None:
    """@brief Verify that existing files are not duplicated by virtual injection.
    @param mock_get_files Mocked get_documentation_files scanner function.
    @param tmp_path Pytest temporary directory fixture.
    """
    mock_file_1 = Path("/srv/projects/cheatsheet/ripgrep.md")
    mock_get_files.return_value = [mock_file_1]

    config = {
        "site_dir": str(tmp_path / "site"),
        "use_directory_urls": True,
    }
    existing_file = File(
        path="cheatsheet/ripgrep.md",
        src_dir="/srv/projects",
        dest_dir=config["site_dir"],
        use_directory_urls=True,
    )
    existing_files = Files([existing_file])

    updated_files = on_files(existing_files, config)

    assert len(updated_files) == 1
