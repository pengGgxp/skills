#!/usr/bin/env python3
"""Resolve the current content workspace and bundled Skill assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


SKILL_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_HTML = SKILL_DIR / "assets" / "dashboard" / "index.html"
DASHBOARD_DATA_REL = Path("dashboard") / "data.json"
PLATFORM_PROFILES_DIR = SKILL_DIR / "references" / "platforms"


class PipelineError(RuntimeError):
    pass


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise PipelineError(f"cannot parse YAML {path}: {exc}") from exc


def validate_workspace_location(workspace: Path) -> Path:
    workspace = workspace.resolve()
    if workspace == Path(workspace.anchor):
        raise PipelineError("content workspace must not be a filesystem root")
    try:
        workspace.relative_to(SKILL_DIR)
    except ValueError:
        pass
    else:
        raise PipelineError("content workspace must stay outside the Skill directory")
    if not workspace.is_dir():
        raise PipelineError(f"content workspace is not a directory: {workspace}")
    return workspace


def resolve_workspace() -> Path:
    """Treat the process working directory as the content workspace root."""
    return validate_workspace_location(Path.cwd())
