#!/usr/bin/env python3
"""Resolve the configured content workspace and bundled Skill assets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


CONFIG_SCHEMA = "3.0"
LEGACY_CONFIG_SCHEMA = "2.0"
SKILL_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_HTML = SKILL_DIR / "assets" / "dashboard" / "index.html"
DASHBOARD_DATA_REL = Path("dashboard") / "data.json"
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeSettings:
    workspace: Path
    config_path: Path | None
    legacy_config: bool = False

    @property
    def dashboard_data(self) -> Path:
        return self.workspace / DASHBOARD_DATA_REL


def resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"cannot parse YAML {path}: {exc}") from exc


def select_config(explicit: Path | None) -> Path:
    if explicit is not None:
        return resolve_path(explicit, Path.cwd())

    local = SKILL_DIR / ".content-pipeline.yaml"
    if local.is_file():
        return local.resolve()

    environment = os.environ.get("CONTENT_PIPELINE_CONFIG")
    if environment:
        return resolve_path(environment, Path.cwd())

    raise ConfigError(
        "content pipeline is not configured; provide an explicit workspace or create "
        f"{local} from {SKILL_DIR / '.content-pipeline.example.yaml'}"
    )


def require_workspace_value(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{context}.{key} must be a non-empty string")
    normalized = value.strip()
    if "<" in normalized or normalized.startswith("D:/path/"):
        raise ConfigError(f"{context}.{key} still contains a placeholder")
    return normalized


def validate_workspace_location(workspace: Path) -> Path:
    workspace = workspace.resolve()
    if workspace == Path(workspace.anchor):
        raise ConfigError("content workspace must not be a filesystem root")
    try:
        workspace.relative_to(SKILL_DIR)
    except ValueError:
        pass
    else:
        raise ConfigError("content workspace must stay outside the Skill directory")
    return workspace


def load_config(path: Path) -> RuntimeSettings:
    if not path.is_file():
        raise ConfigError(f"configuration file does not exist: {path}")

    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ConfigError(f"configuration must be a mapping: {path}")

    schema = str(data.get("schema_version"))
    if schema == CONFIG_SCHEMA:
        value = require_workspace_value(data, "content_workspace", "config")
        legacy = False
    elif schema == LEGACY_CONFIG_SCHEMA:
        value = require_workspace_value(data, "content_repository", "config")
        legacy = True
    else:
        raise ConfigError(
            f"configuration schema_version must be {CONFIG_SCHEMA} "
            f"(legacy {LEGACY_CONFIG_SCHEMA} is temporarily accepted): {path}"
        )

    workspace = validate_workspace_location(resolve_path(value, path.parent))
    return RuntimeSettings(workspace, path.resolve(), legacy)


def resolve_runtime(
    explicit_workspace: Path | None = None,
    explicit_config: Path | None = None,
) -> RuntimeSettings:
    if explicit_workspace is not None:
        workspace = validate_workspace_location(
            resolve_path(explicit_workspace, Path.cwd())
        )
        return RuntimeSettings(workspace, None, False)
    return load_config(select_config(explicit_config))
