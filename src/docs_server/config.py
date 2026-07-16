"""@brief Configuration management for docs-server.

Loads settings from `docs_server.toml` with environment variable overrides.
Uses pydantic-settings for validation and env var support.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from pydantic import BaseModel, Field


class ScannerConfig(BaseModel):
    """@brief Configuration for the documentation scanner."""

    search_paths: list[str] = Field(default_factory=list)
    allowed_roots: list[str] = Field(default_factory=list)
    source_dir: Optional[str] = None


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


def load_toml_raw() -> dict:
    """@brief Load raw TOML config file as a dictionary.
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


def parse_env_list(raw: Optional[str]) -> list[str]:
    """@brief Parse a colon-separated environment variable into a list of strings.
    @param raw Raw environment variable value.
    @return List of stripped, non-empty strings.
    """
    if not raw:
        return []
    return [p.strip() for p in raw.split(":") if p.strip()]


def _resolve_search_paths(toml_data: dict) -> list[str]:
    """@brief Resolve search paths: env var overrides TOML.
    @param raw Parsed TOML dictionary.
    @return List of search path strings.
    """
    env_override = parse_env_list(os.environ.get("DOCS_SERVER_SEARCH_PATHS", ""))
    if env_override:
        return env_override
    return toml_data.get("scanner", {}).get("search_paths", [])


def _resolve_allowed_roots(toml_data: dict, search_paths: list[str]) -> list[str]:
    """@brief Resolve allowed roots: TOML > search_paths fallback.
    @param toml_data Parsed TOML dictionary.
    @param search_paths Resolved search paths for fallback.
    @return List of allowed root strings.
    """
    roots = toml_data.get("scanner", {}).get("allowed_roots", [])
    if roots:
        return roots
    return search_paths


def _resolve_source_dir(toml_data: dict, search_paths: list[str]) -> str:
    """@brief Resolve source directory: TOML > first search_path parent > cwd.
    @param toml_data Parsed TOML dictionary.
    @param search_paths Resolved search paths for fallback.
    @return Absolute source directory path string.
    """
    explicit = toml_data.get("scanner", {}).get("source_dir")
    if explicit:
        return explicit
    if search_paths:
        return str(Path(search_paths[0]).parent)
    return str(Path.cwd())


def load_settings() -> ScannerConfig:
    """@brief Load ScannerConfig from TOML with env var overrides.
    @return Validated ScannerConfig instance.
    """
    toml_data = load_toml_raw()
    search_paths = _resolve_search_paths(toml_data)
    allowed_roots = _resolve_allowed_roots(toml_data, search_paths)
    source_dir = _resolve_source_dir(toml_data, search_paths)

    return ScannerConfig(
        search_paths=search_paths,
        allowed_roots=allowed_roots,
        source_dir=source_dir,
    )


_settings_cache: Optional[ScannerConfig] = None


def get_settings() -> ScannerConfig:
    """@brief Get cached ScannerConfig, loading on first access.
    @return Cached ScannerConfig instance.
    """
    global _settings_cache  # noqa: PLW0603
    if _settings_cache is None:
        _settings_cache = load_settings()
    return _settings_cache
