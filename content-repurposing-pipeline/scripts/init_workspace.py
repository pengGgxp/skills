#!/usr/bin/env python3
"""Initialize a content workspace without creating or requiring a Git repository."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from pipeline_runtime import ConfigError, resolve_runtime


WORKSPACE_DIRS = (
    Path("articles"),
    Path("platforms"),
    Path("shared"),
    Path("dashboard"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, help="explicit content workspace")
    parser.add_argument("--config", type=Path, help="explicit configuration path")
    return parser.parse_args()


def initialize(workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    for relative in WORKSPACE_DIRS:
        path = workspace / relative
        if path.exists() and not path.is_dir():
            raise ConfigError(f"workspace path must be a directory: {path}")
        path.mkdir(parents=True, exist_ok=True)

    data_path = workspace / "dashboard" / "data.json"
    if data_path.exists() and not data_path.is_file():
        raise ConfigError(f"dashboard state path must be a file: {data_path}")
    if not data_path.exists():
        now = datetime.now().astimezone().replace(microsecond=0).isoformat()
        payload = {
            "schema_version": "1.0",
            "updated_at": now,
            "articles": [],
        }
        data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    args = parse_args()
    try:
        settings = resolve_runtime(args.workspace, args.config)
        initialize(settings.workspace)
    except (ConfigError, OSError) as exc:
        print(f"Workspace initialization failed: {exc}", file=sys.stderr)
        return 2
    print(f"Content workspace ready: {settings.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
