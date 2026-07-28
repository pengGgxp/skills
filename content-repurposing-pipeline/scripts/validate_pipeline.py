#!/usr/bin/env python3
"""Validate the lightweight content-workspace workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from pipeline_runtime import (
    DASHBOARD_DATA_REL,
    DASHBOARD_HTML,
    PLATFORM_PROFILES_DIR,
    PipelineError,
    load_yaml,
    resolve_workspace,
)


DASHBOARD_SCHEMA = "1.0"
ARTICLE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ARTICLE_STAGES = {
    "idea",
    "drafting_master",
    "awaiting_master_review",
    "adapting",
    "awaiting_publish_review",
    "ready_to_publish",
    "published",
    "paused",
    "archived",
}
MASTER_STATES = {
    "drafting",
    "awaiting_review",
    "changes_requested",
    "approved",
    "rejected",
}
PLATFORM_STATES = {
    "drafting",
    "awaiting_review",
    "changes_requested",
    "approved",
    "published",
    "skipped",
}
QA_STATES = {"not_run", "passed", "needs_changes", "not_recorded"}
RUNTIME_DEMO_STATES = {
    "not_required",
    "present",
    "needed",
    "not_assessed",
    "not_recorded",
}
META_STATES = {
    "drafting": {"draft"},
    "awaiting_review": {"ready", "review"},
    "changes_requested": {"draft", "review"},
    "approved": {"ready"},
    "published": {"published"},
    "skipped": {"archived", "deleted"},
}


class Validator:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.errors: list[str] = []
        self.article_count = 0
        self.platform_count = 0

    def display(self, path: Path) -> str:
        try:
            return path.relative_to(self.workspace).as_posix()
        except ValueError:
            return str(path)

    def error(self, context: str | Path, message: str) -> None:
        label = self.display(context) if isinstance(context, Path) else context
        self.errors.append(f"{label}: {message}")

    def workspace_path(self, value: Any, context: str, *, must_exist: bool = True) -> Path | None:
        if not isinstance(value, str) or not value.strip():
            self.error(context, "path must be a non-empty workspace-relative string")
            return None
        rel = PurePosixPath(value)
        if rel.is_absolute() or ".." in rel.parts:
            self.error(context, "path must stay inside the content workspace")
            return None
        path = (self.workspace / Path(*rel.parts)).resolve()
        try:
            path.relative_to(self.workspace)
        except ValueError:
            self.error(context, "resolved path escapes the content workspace")
            return None
        if must_exist and not path.exists():
            self.error(context, f"referenced path does not exist: {value}")
        return path

    def validate_workspace(self) -> None:
        if not self.workspace.is_dir():
            self.error(self.workspace, "current content workspace is not a directory")
        self.validate_platform_profiles()

    def validate_platform_profiles(self) -> None:
        common_profile = PLATFORM_PROFILES_DIR / "common.md"
        if not PLATFORM_PROFILES_DIR.is_dir():
            self.error(PLATFORM_PROFILES_DIR, "bundled platform profiles are missing")
            return
        if not common_profile.is_file():
            self.error(common_profile, "bundled common platform profile is missing")
        else:
            try:
                common_lines = common_profile.read_text(
                    encoding="utf-8-sig"
                ).splitlines()
            except (OSError, UnicodeError) as exc:
                self.error(common_profile, f"cannot read common platform profile: {exc}")
            else:
                for section in (
                    "## Load And Route",
                    "## Preserve Source Truth",
                    "## Visual Contract",
                    "## Volatile Platform Constraints",
                    "## Platform QA",
                ):
                    if section not in common_lines:
                        self.error(common_profile, f"missing required section {section!r}")

        profiles = sorted(
            path for path in PLATFORM_PROFILES_DIR.glob("*.md") if path != common_profile
        )
        if not profiles:
            self.error(PLATFORM_PROFILES_DIR, "no platform-specific profiles found")
        for profile_path in profiles:
            platform_name = profile_path.stem
            if not ARTICLE_ID_RE.fullmatch(platform_name):
                self.error(profile_path, "profile filename must be a lowercase ASCII ID")
            try:
                profile_lines = profile_path.read_text(
                    encoding="utf-8-sig"
                ).splitlines()
            except (OSError, UnicodeError) as exc:
                self.error(profile_path, f"cannot read platform profile: {exc}")
                continue
            marker = f"Platform ID: `{platform_name}`"
            if marker not in profile_lines:
                self.error(profile_path, f"must declare the exact marker {marker!r}")
            for section in ("## Position", "## Write", "## Avoid", "## Platform QA"):
                if section not in profile_lines:
                    self.error(profile_path, f"missing required section {section!r}")
            if not {"## Visuals", "## Visuals And Production"}.intersection(
                profile_lines
            ):
                self.error(profile_path, "missing required visuals section")

    def validate_timestamp(self, value: Any, context: str, *, allow_empty: bool = False) -> None:
        if allow_empty and value in ("", None):
            return
        if not isinstance(value, str) or not value:
            self.error(context, "timestamp must be a non-empty ISO-8601 string")
            return
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            self.error(context, f"invalid ISO-8601 timestamp: {value!r}")
            return
        if parsed.tzinfo is None:
            self.error(context, "timestamp must include an explicit timezone")

    def validate_revision(
        self,
        item: dict[str, Any],
        context: str,
        state: str,
        approved_states: set[str],
    ) -> None:
        revision = item.get("revision")
        approved = item.get("approved_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            self.error(context, "revision must be a positive integer")
            return
        if approved is not None and (
            not isinstance(approved, int)
            or isinstance(approved, bool)
            or approved < 1
            or approved > revision
        ):
            self.error(context, "approved_revision must be null or an integer up to revision")
            return
        if state in approved_states and approved != revision:
            self.error(context, "approved state requires approved_revision to equal revision")
        if state not in approved_states and approved is not None:
            self.error(context, "non-approved state must clear approved_revision")

    def validate_master(
        self, article: dict[str, Any], article_id: str, context: str
    ) -> None:
        master = article.get("master")
        if master is None:
            if article.get("stage") not in {"published", "archived"}:
                self.error(context, "master may be null only for imported published or archived work")
            return
        if not isinstance(master, dict):
            self.error(context, "master must be a mapping or null")
            return

        state = master.get("status")
        if state not in MASTER_STATES:
            self.error(
                f"{context}.master.status",
                f"must be one of {sorted(MASTER_STATES)}",
            )
            state = ""
        self.validate_revision(master, f"{context}.master", state, {"approved"})

        path = self.workspace_path(master.get("path"), f"{context}.master.path")
        expected = f"articles/{article_id}/master.md"
        if master.get("path") != expected:
            self.error(
                f"{context}.master.path",
                f"must be exactly {expected!r}",
            )
        if path is not None and path.exists() and not path.is_file():
            self.error(path, "master path must be a file")
        self.validate_timestamp(
            master.get("reviewed_at"),
            f"{context}.master.reviewed_at",
            allow_empty=True,
        )

    def validate_meta(
        self,
        path: Path,
        article_id: str,
        platform_name: str,
        platform: dict[str, Any],
    ) -> None:
        meta_path = path / "meta.yaml"
        index_path = path / "index.md"
        if not index_path.is_file():
            self.error(index_path, "platform version requires index.md")
        if not meta_path.is_file():
            self.error(meta_path, "platform version requires meta.yaml")
            return
        try:
            meta = load_yaml(meta_path)
        except PipelineError as exc:
            self.error(meta_path, str(exc))
            return
        if not isinstance(meta, dict):
            self.error(meta_path, "metadata must be a mapping")
            return
        if meta.get("article_id") != article_id:
            self.error(meta_path, "article_id does not match dashboard state")
        if meta.get("platform") != platform_name:
            self.error(meta_path, "platform does not match dashboard state")
        state = platform.get("status")
        allowed_meta = META_STATES.get(state, set())
        if meta.get("status") not in allowed_meta:
            self.error(
                meta_path,
                f"status {meta.get('status')!r} does not match dashboard platform state {state!r}",
            )
        if "pipeline" in meta:
            self.error(meta_path, "legacy pipeline hashes and approvals must not be stored in meta.yaml")
        if state == "published":
            publishing = meta.get("publishing")
            meta_url = publishing.get("url") if isinstance(publishing, dict) else None
            if meta_url != platform.get("url"):
                self.error(meta_path, "publishing.url does not match dashboard state")

    def validate_platforms(
        self, article: dict[str, Any], article_id: str, context: str
    ) -> None:
        selected = article.get("selected_platforms")
        platforms = article.get("platforms")
        if not isinstance(selected, list) or any(
            not isinstance(item, str) or not ARTICLE_ID_RE.fullmatch(item)
            for item in selected
        ):
            self.error(f"{context}.selected_platforms", "must be a list of lowercase ASCII names")
            selected = []
        if len(selected) != len(set(selected)):
            self.error(f"{context}.selected_platforms", "contains duplicate names")
        if not isinstance(platforms, dict):
            self.error(f"{context}.platforms", "must be a mapping")
            return
        if set(selected) != set(platforms):
            self.error(
                f"{context}.platforms",
                "keys must exactly match selected_platforms",
            )

        for platform_name, platform in platforms.items():
            platform_context = f"{context}.platforms.{platform_name}"
            self.platform_count += 1
            if not ARTICLE_ID_RE.fullmatch(platform_name):
                self.error(platform_context, "platform name must be lowercase ASCII")
            profile_path = PLATFORM_PROFILES_DIR / f"{platform_name}.md"
            if not profile_path.is_file():
                self.error(
                    platform_context,
                    f"missing bundled platform profile: {profile_path.name}",
                )
            if not isinstance(platform, dict):
                self.error(platform_context, "platform state must be a mapping")
                continue
            state = platform.get("status")
            if state not in PLATFORM_STATES:
                self.error(
                    f"{platform_context}.status",
                    f"must be one of {sorted(PLATFORM_STATES)}",
                )
                state = ""
            self.validate_revision(
                platform,
                platform_context,
                state,
                {"approved", "published"},
            )

            rel_value = platform.get("path")
            path = self.workspace_path(rel_value, f"{platform_context}.path")
            if isinstance(rel_value, str):
                parts = PurePosixPath(rel_value).parts
                valid_shape = (
                    len(parts) == 4
                    and parts[0] == "platforms"
                    and parts[1] == platform_name
                    and parts[2] in {"drafts", "published"}
                    and parts[3] == article_id
                )
                if not valid_shape:
                    self.error(
                        f"{platform_context}.path",
                        "must be platforms/<platform>/<drafts|published>/<article_id>",
                    )
                elif state == "published" and parts[2] != "published":
                    self.error(f"{platform_context}.path", "published state requires published/")
                elif state != "published" and state != "skipped" and parts[2] != "drafts":
                    self.error(f"{platform_context}.path", "unpublished state requires drafts/")
            if path is not None and path.is_dir():
                self.validate_meta(path, article_id, platform_name, platform)

            url = platform.get("url")
            if state == "published" and (not isinstance(url, str) or not url.startswith(("http://", "https://"))):
                self.error(f"{platform_context}.url", "published version requires an HTTP(S) URL")
            if state != "published" and url not in ("", None):
                self.error(f"{platform_context}.url", "unpublished version must not have a publication URL")
            self.validate_timestamp(
                platform.get("published_at"),
                f"{platform_context}.published_at",
                allow_empty=True,
            )

    def validate_qa(self, article: dict[str, Any], context: str) -> None:
        qa = article.get("qa")
        if not isinstance(qa, dict):
            self.error(f"{context}.qa", "must be a mapping")
            return
        for field in ("master", "visuals"):
            if qa.get(field) not in QA_STATES:
                self.error(f"{context}.qa.{field}", f"must be one of {sorted(QA_STATES)}")
        platform_qa = qa.get("platforms")
        if not isinstance(platform_qa, dict):
            self.error(f"{context}.qa.platforms", "must be a mapping")
        else:
            if set(platform_qa) != set(article.get("platforms", {})):
                self.error(
                    f"{context}.qa.platforms",
                    "keys must exactly match article.platforms",
                )
            for platform_name, state in platform_qa.items():
                if state not in QA_STATES:
                    self.error(
                        f"{context}.qa.platforms.{platform_name}",
                        f"must be one of {sorted(QA_STATES)}",
                    )

        visuals = article.get("visuals")
        if not isinstance(visuals, dict):
            self.error(f"{context}.visuals", "must be a mapping")
            return
        if visuals.get("status") not in QA_STATES:
            self.error(
                f"{context}.visuals.status",
                f"must be one of {sorted(QA_STATES)}",
            )
        if visuals.get("runtime_demo") not in RUNTIME_DEMO_STATES:
            self.error(
                f"{context}.visuals.runtime_demo",
                f"must be one of {sorted(RUNTIME_DEMO_STATES)}",
            )
        assets = visuals.get("assets", [])
        if not isinstance(assets, list):
            self.error(f"{context}.visuals.assets", "must be a list when present")
        else:
            for index, asset in enumerate(assets):
                asset_context = f"{context}.visuals.assets[{index}]"
                if not isinstance(asset, dict):
                    self.error(asset_context, "must be a mapping")
                    continue
                self.workspace_path(asset.get("path"), f"{asset_context}.path")
                for field in ("role", "origin", "rights", "inspection"):
                    if not isinstance(asset.get(field), str) or not asset.get(field):
                        self.error(asset_context, f"{field} must be a non-empty string")

    def validate_stage(self, article: dict[str, Any], context: str) -> None:
        stage = article.get("stage")
        master = article.get("master")
        master_state = master.get("status") if isinstance(master, dict) else None
        platforms = article.get("platforms") if isinstance(article.get("platforms"), dict) else {}
        platform_states = {
            item.get("status") for item in platforms.values() if isinstance(item, dict)
        }
        if stage == "awaiting_master_review" and master_state != "awaiting_review":
            self.error(context, "awaiting_master_review requires master.status awaiting_review")
        if stage == "adapting" and "drafting" not in platform_states:
            self.error(context, "adapting requires at least one drafting platform")
        if stage == "awaiting_publish_review" and "awaiting_review" not in platform_states:
            self.error(context, "awaiting_publish_review requires an awaiting_review platform")
        if stage == "ready_to_publish" and not platform_states.intersection({"approved", "published"}):
            self.error(context, "ready_to_publish requires an approved platform")
        if stage == "published" and "published" not in platform_states:
            self.error(context, "published requires at least one published platform")

    def validate_article(self, article: Any, index: int, seen: set[str]) -> None:
        context = f"dashboard.data.articles[{index}]"
        if not isinstance(article, dict):
            self.error(context, "article must be a mapping")
            return
        article_id = article.get("article_id")
        if not isinstance(article_id, str) or not ARTICLE_ID_RE.fullmatch(article_id):
            self.error(f"{context}.article_id", "must be a lowercase ASCII slug")
            return
        if article_id in seen:
            self.error(f"{context}.article_id", "must be unique")
        seen.add(article_id)
        context = f"article[{article_id}]"

        for field in ("title", "current_task"):
            if not isinstance(article.get(field), str) or not article.get(field).strip():
                self.error(f"{context}.{field}", "must be a non-empty string")
        if article.get("stage") not in ARTICLE_STAGES:
            self.error(
                f"{context}.stage",
                f"must be one of {sorted(ARTICLE_STAGES)}",
            )
        blockers = article.get("blockers")
        if not isinstance(blockers, list) or any(
            not isinstance(item, str) or not item.strip() for item in blockers
        ):
            self.error(f"{context}.blockers", "must be a list of non-empty strings")
        self.validate_timestamp(article.get("updated_at"), f"{context}.updated_at")
        self.validate_master(article, article_id, context)
        self.validate_platforms(article, article_id, context)
        self.validate_qa(article, context)
        self.validate_stage(article, context)

    def validate_dashboard(self) -> None:
        html_path = DASHBOARD_HTML
        data_path = self.workspace_path(
            DASHBOARD_DATA_REL.as_posix(), "dashboard.data"
        )
        if html_path.is_file():
            try:
                html = html_path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                self.error(html_path, f"cannot read dashboard HTML: {exc}")
            else:
                data_name = DASHBOARD_DATA_REL.name
                if data_name not in html:
                    self.error(html_path, f"dashboard must read {data_name}")
                if "<form" in html.lower():
                    self.error(html_path, "dashboard must remain read-only and contain no forms")
        else:
            self.error(html_path, "bundled dashboard HTML is missing")
        if data_path is None or not data_path.is_file():
            return
        try:
            data = json.loads(data_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            self.error(data_path, f"cannot parse dashboard JSON: {exc}")
            return
        if not isinstance(data, dict):
            self.error(data_path, "top-level JSON must be an object")
            return
        if str(data.get("schema_version")) != DASHBOARD_SCHEMA:
            self.error(data_path, f"schema_version must be {DASHBOARD_SCHEMA}")
        self.validate_timestamp(data.get("updated_at"), "dashboard.data.updated_at")
        articles = data.get("articles")
        if not isinstance(articles, list):
            self.error(data_path, "articles must be a list")
            return
        seen: set[str] = set()
        for index, article in enumerate(articles):
            self.article_count += 1
            self.validate_article(article, index, seen)

    def validate_removed_complexity(self) -> None:
        forbidden_files = [
            self.workspace / "registry" / "articles-index.md",
        ]
        for path in forbidden_files:
            if path.exists():
                self.error(path, "duplicate workflow index is not allowed; use dashboard/data.json")
        for pattern in ("artifact-manifest.yaml", "publication-checklist.md"):
            for path in self.workspace.rglob(pattern):
                self.error(path, "legacy pipeline control file must not be reintroduced")
        registry = self.workspace / "registry" / "pipeline-runs"
        if registry.is_dir():
            for path in registry.iterdir():
                if path.is_file():
                    self.error(path, "legacy sanitized run registry must remain retired")

    def run(self) -> int:
        self.validate_workspace()
        if not self.errors:
            self.validate_dashboard()
            self.validate_removed_complexity()
        if self.errors:
            for message in self.errors:
                print(f"ERROR: {message}", file=sys.stderr)
            print(f"Pipeline validation failed with {len(self.errors)} error(s).", file=sys.stderr)
            return 1
        print(
            "Content workspace validation passed: "
            f"{self.article_count} article(s), {self.platform_count} platform version(s)."
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    return parser.parse_args()


def main() -> int:
    parse_args()
    try:
        workspace = resolve_workspace()
    except (PipelineError, OSError) as exc:
        print(f"Workspace error: {exc}", file=sys.stderr)
        return 2
    return Validator(workspace).run()


if __name__ == "__main__":
    raise SystemExit(main())
