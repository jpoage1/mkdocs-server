"""@brief Tests for the dynamic workspace documentation discovery scanner (`scanner.py`)."""

from pathlib import Path
import pytest

from docs_server.scanner import get_documentation_files, EXCLUDE_DIRS, SEARCH_PATHS


def test_get_documentation_files_skips_missing_dirs(tmp_path: Path) -> None:
    """@brief Verify that non-existent directories in search_paths are skipped cleanly without errors.
    @param tmp_path Pytest temporary directory fixture.
    """
    missing_dir = tmp_path / "non_existent_path"
    existing_dir = tmp_path / "existing_dir"
    existing_dir.mkdir()
    (existing_dir / "test.md").write_text("# Test")

    results = get_documentation_files(
        search_paths=[str(missing_dir), str(existing_dir)]
    )
    assert results == [existing_dir / "test.md"]


def test_get_documentation_files_prunes_excluded_dirs(tmp_path: Path) -> None:
    """@brief Verify that excluded directories like node_modules and .venv are pruned during traversal.
    @param tmp_path Pytest temporary directory fixture.
    """
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.md").write_text("# Package")

    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib.md").write_text("# Lib")

    valid_dir = tmp_path / "docs"
    valid_dir.mkdir()
    valid_file = valid_dir / "guide.markdown"
    valid_file.write_text("# Guide")

    results = get_documentation_files(search_paths=[str(tmp_path)])
    assert results == [valid_file]


def test_get_documentation_files_prunes_hidden_dirs(tmp_path: Path) -> None:
    """@brief Verify that any hidden directory starting with a dot is pruned during traversal.
    @param tmp_path Pytest temporary directory fixture.
    """
    hidden_dir = tmp_path / ".expo"
    hidden_dir.mkdir()
    (hidden_dir / "README.md").write_text("# Expo Readme")

    valid_file = tmp_path / "README.md"
    valid_file.write_text("# Root Readme")

    results = get_documentation_files(search_paths=[str(tmp_path)])
    assert results == [valid_file]


def test_get_documentation_files_includes_boilerplate(tmp_path: Path) -> None:
    """@brief Verify that README.md, AGENTS.md, and CHANGELOG.md are included in results.
    @param tmp_path Pytest temporary directory fixture.
    """
    readme = tmp_path / "README.md"
    readme.write_text("# Readme")

    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Agents")

    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog")

    # Excluded CLAUDE.md and README without extension should not be returned
    claude = tmp_path / "CLAUDE.md"
    claude.write_text("# Claude")

    readme_no_ext = tmp_path / "README"
    readme_no_ext.write_text("Readme without ext")

    results = get_documentation_files(search_paths=[str(tmp_path)])
    assert sorted(results) == sorted([readme, agents, changelog])


def test_exclude_dirs_matches_docs_sh_behavior() -> None:
    """@brief Verify that EXCLUDE_DIRS contains all directory exclusion rules modeled from docs.sh."""
    expected = {
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
    assert EXCLUDE_DIRS == expected
