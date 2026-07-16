#!/usr/bin/env python3
"""Validate content pipeline records, approvals, hashes, and projections."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^run-\d{8}-\d{6}-[a-z0-9-]+$")
AUTHORIZATION_ID_RE = re.compile(r"^feishu-review-\d{8}-[a-z0-9-]+$")
DECISION_ID_RE = re.compile(r"^dec-[a-z0-9-]+$")
FEISHU_VERSION_RE = re.compile(r"^v\d{4}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
VAGUE_VERSION_RE = re.compile(r"^(?:current|latest)(?:\s+documentation)?$|^(?:linux\s+)?man-pages$", re.I)

APPROVAL_STATES = {"pending", "approved", "changes_requested", "rejected", "not_required"}
RUN_STATES = {"researching", "drafting", "review", "ready", "stopped", "published", "archived"}
CANDIDATE_STATES = {
    "pending",
    "selected",
    "parked",
    "rejected",
    "needs_authorization",
    "needs_confirmation",
}
FEISHU_STATES = {"disabled", "pending", "synced", "drift", "error", "revoked", "redacted"}
WORKSPACE_AUTH_STATES = {"pending", "active", "revoked", "expired"}
DRIFT_STATES = {"not_synced", "in_sync", "detected", "resolved"}
OUTBOX_STATES = {"pending", "in_progress", "completed", "failed", "blocked_drift", "cancelled"}
CHECKLIST_RESULTS = {"pending", "passed", "failed"}
MASTER_GATES = ("claims_verified", "disclosure_approved", "draft_approved")
ARTIFACT_TYPES = {"master_article", "platform_article"}
ARTIFACT_STATES = {"draft", "review", "ready", "published", "archived"}
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


class Validator:
    def __init__(self, content_hub: Path, private_root: Path, run_id: str | None) -> None:
        self.content_hub = content_hub.resolve()
        self.private_root = private_root.resolve()
        self.run_id = run_id
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checked_runs = 0
        self.checked_artifacts = 0

    def error(self, path: Path | str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: Path | str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")

    def load_yaml(self, path: Path) -> dict[str, Any] | None:
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            self.error(path, f"cannot parse YAML: {exc}")
            return None
        if not isinstance(value, dict):
            self.error(path, "top-level YAML value must be a mapping")
            return None
        return value

    def load_frontmatter(self, path: Path) -> dict[str, Any] | None:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as exc:
            self.error(path, f"cannot read Markdown: {exc}")
            return None
        if not lines or lines[0].strip() != "---":
            self.error(path, "Markdown must start with YAML frontmatter")
            return None
        try:
            end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
        except StopIteration:
            self.error(path, "frontmatter closing delimiter is missing")
            return None
        try:
            value = yaml.safe_load("\n".join(lines[1:end]))
        except yaml.YAMLError as exc:
            self.error(path, f"cannot parse frontmatter: {exc}")
            return None
        if not isinstance(value, dict):
            self.error(path, "frontmatter must be a mapping")
            return None
        return value

    @staticmethod
    def hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def validate_text_bytes(self, path: Path, field: str) -> None:
        try:
            raw = path.read_bytes()
        except OSError as exc:
            self.error(path, f"cannot read {field}: {exc}")
            return
        if raw.startswith(b"\xef\xbb\xbf"):
            self.error(path, f"{field} must use UTF-8 without a byte-order mark")
        if b"\r" in raw:
            self.error(path, f"{field} must use LF line endings")
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            self.error(path, f"{field} must be valid UTF-8")

    def resolve_hub_path(self, value: Any, record_path: Path, field: str) -> Path | None:
        if not isinstance(value, str) or not value:
            self.error(record_path, f"{field} must be a non-empty repository-relative path")
            return None
        relative = PurePosixPath(value)
        if relative.is_absolute() or "\\" in value or ".." in relative.parts or WINDOWS_ABSOLUTE_RE.search(value):
            self.error(record_path, f"{field} must be a safe repository-relative POSIX path")
            return None
        resolved = (self.content_hub / Path(*relative.parts)).resolve()
        if not resolved.is_relative_to(self.content_hub):
            self.error(record_path, f"{field} resolves outside Content Hub")
            return None
        return resolved

    def resolve_version_path(self, root: Path, value: Any, path: Path, field: str) -> Path | None:
        if not isinstance(value, str) or not value:
            self.error(path, f"{field} must be a non-empty relative path")
            return None
        relative = PurePosixPath(value)
        if relative.is_absolute() or "\\" in value or ".." in relative.parts or WINDOWS_ABSOLUTE_RE.search(value):
            self.error(path, f"{field} must be a safe relative POSIX path")
            return None
        resolved = (root / Path(*relative.parts)).resolve()
        if not resolved.is_relative_to(root.resolve()):
            self.error(path, f"{field} resolves outside the platform-version directory")
            return None
        return resolved

    def validate_schema_version(self, record: dict[str, Any], path: Path) -> None:
        if record.get("schema_version") != "1.0":
            self.error(path, "schema_version must be 1.0")

    def require_mapping(self, parent: dict[str, Any], key: str, path: Path) -> dict[str, Any] | None:
        value = parent.get(key)
        if not isinstance(value, dict):
            self.error(path, f"{key} must be a mapping")
            return None
        return value

    def require_list(self, parent: dict[str, Any], key: str, path: Path) -> list[Any] | None:
        value = parent.get(key)
        if not isinstance(value, list):
            self.error(path, f"{key} must be a list")
            return None
        return value

    def validate_timestamp(self, value: Any, path: Path, field: str, required: bool = True) -> None:
        if value in (None, ""):
            if required:
                self.error(path, f"{field} must be a timezone-aware timestamp")
            return
        if not isinstance(value, str):
            self.error(path, f"{field} must be a string timestamp")
            return
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            self.error(path, f"{field} is not ISO-8601: {value}")
            return
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            self.error(path, f"{field} must include a UTC offset")

    @staticmethod
    def parse_timestamp(value: Any) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed

    def validate_sha(self, value: Any, path: Path, field: str, required: bool = True) -> bool:
        if value in (None, "") and not required:
            return False
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            self.error(path, f"{field} must be a lowercase SHA-256")
            return False
        return True

    def validate_approval(self, gate: Any, gate_name: str, master_sha: str, path: Path) -> None:
        if not isinstance(gate, dict):
            self.error(path, f"approvals.{gate_name} must be a mapping")
            return
        status = gate.get("status")
        if status not in APPROVAL_STATES:
            self.error(path, f"approvals.{gate_name}.status is invalid: {status}")
            return
        decided = status in {"approved", "not_required", "changes_requested", "rejected"}
        if decided:
            decision_id = gate.get("decision_id")
            if not isinstance(decision_id, str) or not DECISION_ID_RE.fullmatch(decision_id):
                self.error(path, f"approvals.{gate_name}.decision_id is required for {status}")
            for field in ("by", "at", "scope", "notes"):
                if not gate.get(field):
                    self.error(path, f"approvals.{gate_name}.{field} is required for {status}")
            self.validate_timestamp(gate.get("at"), path, f"approvals.{gate_name}.at")
            self.validate_sha(gate.get("artifact_sha256"), path, f"approvals.{gate_name}.artifact_sha256")
        if decided and gate.get("artifact_sha256") != master_sha:
            self.error(path, f"approvals.{gate_name} decision does not match master.sha256")

    def validate_workspace_authorization(
        self, authorization_id: str, run_id: str, path: Path, required_status: str = "active"
    ) -> set[str]:
        authorized_actions: set[str] = set()
        if not AUTHORIZATION_ID_RE.fullmatch(authorization_id):
            self.error(path, f"invalid Feishu workspace authorization ID: {authorization_id}")
            return authorized_actions
        authorization_path = self.private_root / "authorizations" / f"{authorization_id}.yaml"
        if not authorization_path.is_file():
            self.error(path, f"Feishu workspace authorization is missing: {authorization_path}")
            return authorized_actions
        record = self.load_yaml(authorization_path)
        if record is None:
            return authorized_actions
        self.validate_schema_version(record, authorization_path)
        if record.get("authorization_id") != authorization_id:
            self.error(authorization_path, "authorization_id does not match the file name or run reference")
        status = record.get("status")
        if status not in WORKSPACE_AUTH_STATES:
            self.error(authorization_path, f"status is invalid: {status}")
        elif status != required_status:
            self.error(authorization_path, f"authorization must be {required_status}, not {status}")

        authorization = self.require_mapping(record, "authorization", authorization_path)
        if authorization is not None:
            for field in ("authorized_by", "authorized_at", "persistence"):
                if not authorization.get(field):
                    self.error(authorization_path, f"authorization.{field} is required")
            self.validate_timestamp(
                authorization.get("authorized_at"), authorization_path, "authorization.authorized_at"
            )
            scope = authorization.get("scope")
            if not isinstance(scope, list) or not any(isinstance(item, str) and item.strip() for item in scope):
                self.error(authorization_path, "authorization.scope must contain at least one operation")
            else:
                authorized_actions = {item.strip() for item in scope if isinstance(item, str) and item.strip()}
            persistence = authorization.get("persistence")
            if persistence not in {"one_run", "persistent"}:
                self.error(authorization_path, "authorization.persistence must be one_run or persistent")
            run_ids = authorization.get("authorized_run_ids")
            if persistence == "one_run" and (not isinstance(run_ids, list) or run_id not in run_ids):
                self.error(authorization_path, "one-run authorization must include the current run_id")
            expires_at = authorization.get("expires_at")
            if expires_at:
                self.validate_timestamp(expires_at, authorization_path, "authorization.expires_at")
                try:
                    expires = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
                    if required_status == "active" and expires <= datetime.now(expires.tzinfo):
                        self.error(authorization_path, "authorization has expired")
                except (TypeError, ValueError):
                    pass
            if required_status == "active" and authorization.get("revoked_at"):
                self.error(authorization_path, "active authorization cannot have revoked_at")
            if required_status == "revoked":
                self.validate_timestamp(
                    authorization.get("revoked_at"), authorization_path, "authorization.revoked_at"
                )

        binding = self.require_mapping(record, "binding", authorization_path)
        if binding is not None:
            for field in (
                "account_id",
                "app_token",
                "topic_table_id",
                "review_versions_table_id",
                "folder_token",
                "guide_doc_id",
            ):
                if not binding.get(field):
                    self.error(authorization_path, f"binding.{field} is required")
        security = self.require_mapping(record, "security", authorization_path)
        if security is not None:
            if security.get("document_acl") != "restricted_read_comment":
                self.error(authorization_path, "security.document_acl must be restricted_read_comment")
            if security.get("link_sharing") != "disabled":
                self.error(authorization_path, "security.link_sharing must be disabled")
            reviewers = security.get("allowed_reviewers")
            if not isinstance(reviewers, list) or not reviewers:
                self.error(authorization_path, "security.allowed_reviewers must name at least one reviewer")
        return authorized_actions

    def validate_feishu(self, run: dict[str, Any], path: Path, master_sha: str) -> None:
        review = self.require_mapping(run, "feishu_review", path)
        if review is None:
            return
        status = review.get("status")
        if status not in FEISHU_STATES:
            self.error(path, f"feishu_review.status is invalid: {status}")
            return
        mirror = self.require_mapping(review, "master_mirror", path)
        versions = self.require_list(review, "review_versions", path)
        outbox = self.require_list(review, "outbox", path)
        if run.get("storage_class") == "sanitized_public":
            if status not in {"disabled", "redacted"}:
                self.error(path, "sanitized records must not expose operational Feishu state")
            if review.get("workspace_authorization_id") or review.get("topic_record_id"):
                self.error(path, "sanitized records must clear Feishu authorization and resource IDs")
            if versions or outbox:
                self.error(path, "sanitized records must clear Feishu version details and outbox operations")
            if mirror and any(value for key, value in mirror.items() if key != "drift_status"):
                self.error(path, "sanitized records must clear Feishu mirror identifiers and revisions")
            return
        if status == "disabled":
            if review.get("workspace_authorization_id") or review.get("topic_record_id"):
                self.error(path, "disabled Feishu review cannot retain active workspace or topic IDs")
            if versions or outbox:
                self.error(path, "disabled Feishu review cannot contain versions or outbox operations")
            return

        if run.get("visibility") == "private":
            self.error(path, "private material cannot enable Feishu review")
        authorization_id = review.get("workspace_authorization_id")
        authorized_actions: set[str] = set()
        if not authorization_id:
            self.error(path, "enabled Feishu review requires workspace_authorization_id")
        elif isinstance(authorization_id, str):
            required_auth_status = "revoked" if status == "revoked" else "active"
            authorized_actions = self.validate_workspace_authorization(
                authorization_id, str(run.get("run_id", "")), path, required_auth_status
            )
        if status != "revoked":
            disclosure = run.get("approvals", {}).get("disclosure_approved", {})
            if disclosure.get("status") != "approved" or disclosure.get("artifact_sha256") != master_sha:
                self.error(path, "enabled Feishu review requires current disclosure approval")
        if mirror is not None:
            drift_status = mirror.get("drift_status")
            if drift_status not in DRIFT_STATES:
                self.error(path, f"Feishu mirror drift_status is invalid: {drift_status}")
            if mirror.get("source_sha256") not in ("", master_sha):
                self.error(path, "Feishu mirror source hash does not match master.sha256")
            if status == "synced":
                if not review.get("topic_record_id"):
                    self.error(path, "synced Feishu review requires topic_record_id")
                for field in ("artifact_id", "source_sha256", "doc_id", "remote_revision", "synced_at", "acl"):
                    if not mirror.get(field):
                        self.error(path, f"synced Feishu review requires master_mirror.{field}")
                if drift_status != "in_sync":
                    self.error(path, "synced Feishu review requires master_mirror.drift_status: in_sync")
                self.validate_timestamp(mirror.get("synced_at"), path, "feishu_review.master_mirror.synced_at")
            if status == "drift" and drift_status != "detected":
                self.error(path, "Feishu drift status requires master_mirror.drift_status: detected")

        if versions is not None:
            if versions:
                claims_gate = run.get("approvals", {}).get("claims_verified", {})
                if claims_gate.get("status") != "approved" or claims_gate.get("artifact_sha256") != master_sha:
                    self.error(path, "Feishu review snapshots require current claims verification")
            seen_versions: set[tuple[Any, Any]] = set()
            version_names: list[str] = []
            superseded_versions: list[tuple[str, str]] = []
            run_artifacts = {
                artifact.get("artifact_id"): artifact
                for artifact in run.get("artifacts", [])
                if isinstance(artifact, dict) and artifact.get("artifact_id")
            }
            for index, version in enumerate(versions):
                label = f"feishu_review.review_versions[{index}]"
                if not isinstance(version, dict):
                    self.error(path, f"{label} must be a mapping")
                    continue
                for field in (
                    "version",
                    "target_type",
                    "artifact_id",
                    "source_sha256",
                    "snapshot_sha256",
                    "doc_id",
                    "remote_revision",
                    "acl",
                    "created_at",
                ):
                    if not version.get(field):
                        self.error(path, f"{label}.{field} is required")
                version_name = version.get("version")
                if not isinstance(version_name, str) or not FEISHU_VERSION_RE.fullmatch(version_name):
                    self.error(path, f"{label}.version must use vNNNN")
                else:
                    version_names.append(version_name)
                target_type = version.get("target_type")
                if target_type not in {"master", "platform"}:
                    self.error(path, f"{label}.target_type must be master or platform")
                target_artifact = run_artifacts.get(version.get("artifact_id"))
                if not isinstance(target_artifact, dict):
                    self.error(path, f"{label}.artifact_id is unknown")
                else:
                    expected_type = "master_article" if target_type == "master" else "platform_article"
                    if target_artifact.get("type") != expected_type:
                        self.error(path, f"{label}.target_type does not match its artifact")
                    if version.get("source_sha256") != target_artifact.get("sha256"):
                        self.error(path, f"{label}.source_sha256 does not match its artifact")
                    if target_type == "platform" and version.get("platform") != target_artifact.get("platform"):
                        self.error(path, f"{label}.platform does not match its artifact")
                self.validate_sha(version.get("source_sha256"), path, f"{label}.source_sha256")
                self.validate_sha(version.get("snapshot_sha256"), path, f"{label}.snapshot_sha256")
                self.validate_timestamp(version.get("created_at"), path, f"{label}.created_at")
                key = (version.get("version"), version.get("snapshot_sha256"))
                if key in seen_versions:
                    self.error(path, f"duplicate Feishu review version: {key}")
                seen_versions.add(key)
                supersedes = version.get("supersedes_version")
                if supersedes:
                    superseded_versions.append((str(version_name), str(supersedes)))
                conclusion = version.get("conclusion")
                if conclusion:
                    for field in ("reviewer", "reviewed_at"):
                        if not version.get(field):
                            self.error(path, f"{label}.{field} is required with a conclusion")
                    self.validate_timestamp(version.get("reviewed_at"), path, f"{label}.reviewed_at")
            if version_names != sorted(version_names):
                self.error(path, "Feishu review versions must be ordered monotonically")
            known_versions = set(version_names)
            for version_name, supersedes in superseded_versions:
                if supersedes not in known_versions or supersedes >= version_name:
                    self.error(path, f"review version {version_name} has an invalid supersedes_version")

        if outbox is not None:
            operation_ids: set[str] = set()
            for index, operation in enumerate(outbox):
                label = f"feishu_review.outbox[{index}]"
                if not isinstance(operation, dict):
                    self.error(path, f"{label} must be a mapping")
                    continue
                operation_id = operation.get("operation_id")
                if not isinstance(operation_id, str) or not operation_id.startswith("feishu:"):
                    self.error(path, f"{label}.operation_id must use the feishu: prefix")
                elif operation_id in operation_ids:
                    self.error(path, f"duplicate outbox operation_id: {operation_id}")
                else:
                    operation_ids.add(operation_id)
                    parts = operation_id.split(":")
                    if len(parts) != 5:
                        self.error(path, f"{label}.operation_id must contain action, run, hash, and version")
                    else:
                        _, action, operation_run_id, operation_sha, operation_version = parts
                        if operation_run_id != run.get("run_id"):
                            self.error(path, f"{label}.operation_id references a different run")
                        if action not in authorized_actions:
                            self.error(path, f"{label} action is outside the workspace authorization scope")
                        if operation.get("action") != action:
                            self.error(path, f"{label}.action does not match operation_id")
                        if operation.get("artifact_sha256") != operation_sha:
                            self.error(path, f"{label}.artifact_sha256 does not match operation_id")
                        self.validate_sha(operation_sha, path, f"{label}.operation_id artifact hash")
                        if str(operation.get("version", "")) != operation_version:
                            self.error(path, f"{label}.version does not match operation_id")
                if operation.get("status") not in OUTBOX_STATES:
                    self.error(path, f"{label}.status is invalid")
                attempts = operation.get("attempts")
                if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
                    self.error(path, f"{label}.attempts must be a non-negative integer")
                elif attempts > 0:
                    self.validate_timestamp(operation.get("last_attempt_at"), path, f"{label}.last_attempt_at")
                writes_blocked = status in {"revoked", "drift"} or (
                    mirror is not None and mirror.get("drift_status") == "detected"
                )
                if writes_blocked and operation.get("status") in {"pending", "in_progress"}:
                    self.error(path, f"{label} cannot remain active while Feishu writes are blocked")

    def validate_candidate(self, path: Path, has_platform_artifact: bool) -> None:
        candidate = self.load_yaml(path)
        if candidate is None:
            return
        self.validate_schema_version(candidate, path)
        decision = self.require_mapping(candidate, "decision", path)
        scoring = self.require_mapping(candidate, "scoring", path)
        gates = self.require_mapping(candidate, "hard_gates", path)
        if decision is None or scoring is None or gates is None:
            return
        status = decision.get("status")
        if status not in CANDIDATE_STATES:
            self.error(path, f"decision.status is invalid: {status}")
        override = decision.get("override")
        if not isinstance(override, dict):
            self.error(path, "decision.override must be a structured mapping")
            override = {}
        values = scoring.get("values")
        if not isinstance(values, dict):
            self.error(path, "scoring.values must be a mapping")
            return
        dimensions = {
            "real_work_relevance",
            "reusable_value",
            "search_demand",
            "publishability",
            "timeliness",
        }
        weights = scoring.get("weights")
        if not isinstance(weights, dict) or set(weights) != dimensions:
            self.error(path, "scoring.weights must contain exactly the five scoring dimensions")
            return
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in weights.values()):
            self.error(path, "scoring.weights must be non-negative numbers")
            return
        if round(sum(weights.values()), 10) != 100:
            self.error(path, "scoring.weights must total 100")
        threshold = scoring.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 100:
            self.error(path, "scoring.threshold must be between 0 and 100")
            return
        reasons = scoring.get("reasons")
        if not isinstance(reasons, dict):
            self.error(path, "scoring.reasons must be a mapping")
            reasons = {}
        missing = [name for name in dimensions if values.get(name) is None]
        for name in dimensions - set(missing):
            if not reasons.get(name):
                self.error(path, f"scoring.reasons.{name} is required for a scored dimension")

        override_required = status == "selected" and bool(missing)
        expected_total: float | None = None
        if not missing:
            total = 0.0
            for name in dimensions:
                value = values.get(name)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
                    self.error(path, f"scoring.values.{name} must be between 0 and 5")
                    return
                total += value / 5 * weights[name]
            expected_total = round(total, 1)
            if scoring.get("total") != expected_total:
                self.error(path, f"scoring.total must be {expected_total}")
            if status == "selected" and expected_total < threshold:
                override_required = True
        elif scoring.get("total") is not None:
            self.error(path, "scoring.total must be null while any dimension is unknown")

        if override.get("applied") is True or override_required:
            if override.get("applied") is not True:
                self.error(path, "selected candidate below threshold or with incomplete scores requires an override")
            for field in ("by", "at", "reason"):
                if not override.get(field):
                    self.error(path, f"decision.override.{field} is required")
            self.validate_timestamp(override.get("at"), path, "decision.override.at")
        if status == "selected":
            if not decision.get("decided_by"):
                self.error(path, "selected candidate requires decision.decided_by")
            self.validate_timestamp(decision.get("decided_at"), path, "decision.decided_at")

        if has_platform_artifact:
            for gate_name in (
                "sources_authorized",
                "visibility_allows_adaptation",
                "redaction_feasible",
                "material_claims_verifiable",
            ):
                if gates.get(gate_name) is not True:
                    self.error(path, f"platform artifact exists while hard_gates.{gate_name} is not true")
            if status != "selected":
                self.error(path, f"platform artifact exists while decision.status is {status}")

    def validate_artifact_manifest(
        self, manifest_path: Path, artifact: dict[str, Any], article_path: Path, record_path: Path
    ) -> str:
        article_dir = article_path.parent.resolve()
        if manifest_path.parent.resolve() != article_dir or manifest_path.name != "artifact-manifest.yaml":
            self.error(record_path, "platform manifest must be artifact-manifest.yaml beside index.md")
        self.validate_text_bytes(manifest_path, "artifact manifest")
        manifest = self.load_yaml(manifest_path)
        manifest_sha = self.hash_file(manifest_path)
        if manifest is None:
            return manifest_sha
        self.validate_schema_version(manifest, manifest_path)
        if manifest.get("artifact_id") != artifact.get("artifact_id"):
            self.error(manifest_path, "artifact_id does not match the run record")
        files = self.require_list(manifest, "files", manifest_path)
        if files is None:
            return manifest_sha

        listed_paths: list[str] = []
        for index, item in enumerate(files):
            label = f"files[{index}]"
            if not isinstance(item, dict):
                self.error(manifest_path, f"{label} must be a mapping")
                continue
            relative_value = item.get("path")
            file_path = self.resolve_version_path(article_dir, relative_value, manifest_path, f"{label}.path")
            if not isinstance(relative_value, str) or file_path is None:
                continue
            listed_paths.append(relative_value)
            if not file_path.is_file():
                self.error(manifest_path, f"listed publishable file is missing: {relative_value}")
                continue
            expected_sha = item.get("sha256")
            self.validate_sha(expected_sha, manifest_path, f"{label}.sha256")
            if expected_sha != self.hash_file(file_path):
                self.error(manifest_path, f"{label}.sha256 does not match {relative_value}")
            if file_path.suffix.lower() in TEXT_SUFFIXES:
                self.validate_text_bytes(file_path, f"manifest file {relative_value}")

        if listed_paths != sorted(listed_paths):
            self.error(manifest_path, "manifest file paths must be sorted lexically")
        if len(listed_paths) != len(set(listed_paths)):
            self.error(manifest_path, "manifest file paths must be unique")
        if "index.md" not in listed_paths:
            self.error(manifest_path, "manifest must include index.md")

        excluded = {"meta.yaml", "publication-checklist.md", "artifact-manifest.yaml"}
        discovered = sorted(
            file.relative_to(article_dir).as_posix()
            for file in article_dir.rglob("*")
            if file.is_file()
            and file.relative_to(article_dir).as_posix() not in excluded
            and file.name != ".gitkeep"
        )
        if listed_paths != discovered:
            missing = sorted(set(discovered) - set(listed_paths))
            extra = sorted(set(listed_paths) - set(discovered))
            if missing:
                self.error(manifest_path, f"manifest omits publishable files: {', '.join(missing)}")
            if extra:
                self.error(manifest_path, f"manifest lists unexpected files: {', '.join(extra)}")
        return manifest_sha

    def validate_meta(
        self,
        meta_path: Path,
        artifact: dict[str, Any],
        master_sha: str,
        run_id: str,
        candidate_id: str,
        run_approvals: dict[str, Any],
        publications: list[dict[str, Any]],
    ) -> None:
        meta = self.load_yaml(meta_path)
        if meta is None:
            return
        self.validate_text_bytes(meta_path, "artifact metadata")
        pipeline = self.require_mapping(meta, "pipeline", meta_path)
        if pipeline is None:
            return
        artifact_sha = str(artifact.get("sha256", ""))
        if pipeline.get("run_id") != run_id:
            self.error(meta_path, "pipeline.run_id does not match the run record")
        if pipeline.get("candidate_id") != candidate_id:
            self.error(meta_path, "pipeline.candidate_id does not match the run record")
        if pipeline.get("artifact_id") != artifact.get("artifact_id"):
            self.error(meta_path, "pipeline.artifact_id does not match the artifact")
        if meta.get("platform") != artifact.get("platform"):
            self.error(meta_path, "platform does not match the artifact")
        if meta.get("status") != artifact.get("status"):
            self.error(meta_path, "status does not match the artifact")
        run_record_path = self.resolve_hub_path(
            pipeline.get("run_record_path"), meta_path, "pipeline.run_record_path"
        )
        expected_run_record = (self.content_hub / "registry" / "pipeline-runs" / f"{run_id}.yaml").resolve()
        if run_record_path is not None and run_record_path != expected_run_record:
            self.error(meta_path, "pipeline.run_record_path does not resolve to this run record")
        if pipeline.get("master_sha256") != master_sha:
            self.error(meta_path, "pipeline.master_sha256 does not match the run record")
        if pipeline.get("artifact_sha256") != artifact_sha:
            self.error(meta_path, "pipeline.artifact_sha256 does not match the artifact")
        source = self.require_mapping(meta, "source", meta_path)
        if source is not None and source.get("canonical_path") != artifact.get("path"):
            self.error(meta_path, "source.canonical_path does not match the artifact path")
        publishing = self.require_mapping(meta, "publishing", meta_path)
        matching_publications = [
            publication
            for publication in publications
            if isinstance(publication, dict)
            and publication.get("artifact_id") == artifact.get("artifact_id")
            and publication.get("platform") == artifact.get("platform")
        ]
        if len(matching_publications) > 1:
            self.error(meta_path, "metadata supports only one publication destination per platform artifact")
        artifact_path_value = str(artifact.get("path", ""))
        if matching_publications:
            if artifact.get("status") not in {"published", "archived"}:
                self.error(meta_path, "publication record requires published or archived metadata")
            if not any(segment in f"/{artifact_path_value}" for segment in ("/published/", "/archived/")):
                self.error(meta_path, "published or archived artifact is stored in the wrong directory")
            if publishing is not None:
                publication = matching_publications[0]
                if publishing.get("url") != publication.get("url"):
                    self.error(meta_path, "publishing.url does not match the publication record")
                if publishing.get("published_at") != publication.get("published_at"):
                    self.error(meta_path, "publishing.published_at does not match the publication record")
        else:
            if artifact.get("status") == "published":
                self.error(meta_path, "published metadata requires a publication record")
            if publishing is not None and (publishing.get("url") or publishing.get("published_at")):
                self.error(meta_path, "non-published metadata must clear URL and publication time")
        approvals = self.require_mapping(pipeline, "approvals", meta_path)
        if approvals is None:
            return
        for gate_name in MASTER_GATES:
            gate = approvals.get(gate_name)
            if not isinstance(gate, dict):
                self.error(meta_path, f"pipeline.approvals.{gate_name} must be a mapping")
                continue
            if gate.get("status") == "approved" and gate.get("artifact_sha256") != master_sha:
                self.error(meta_path, f"pipeline.approvals.{gate_name} must bind to the master hash")
            run_gate = run_approvals.get(gate_name, {})
            if gate.get("status") != run_gate.get("status"):
                self.error(meta_path, f"pipeline.approvals.{gate_name}.status differs from the run record")
        publish = approvals.get("publish_approved")
        if not isinstance(publish, dict):
            self.error(meta_path, "pipeline.approvals.publish_approved must be a mapping")
        else:
            matching_run_gate = any(
                isinstance(gate, dict)
                and gate.get("status") == "approved"
                and gate.get("artifact_id") == pipeline.get("artifact_id")
                and gate.get("platform") == meta.get("platform")
                and gate.get("destination") == publish.get("destination")
                and gate.get("artifact_sha256") == artifact_sha
                for gate in run_approvals.get("publish_approved", [])
            )
            if publish.get("status") == "approved":
                if publish.get("artifact_sha256") != artifact_sha:
                    self.error(meta_path, "publish approval must bind to the platform artifact hash")
                if not matching_run_gate:
                    self.error(meta_path, "approved publish snapshot has no matching run-record decision")
            elif matching_run_gate:
                self.error(meta_path, "publish snapshot is stale relative to the run record")

    def validate_checklist(
        self,
        path: Path,
        artifact: dict[str, Any],
        run_id: str,
        publish_approvals: list[dict[str, Any]],
    ) -> tuple[str, str, str, str] | None:
        frontmatter = self.load_frontmatter(path)
        if frontmatter is None:
            return None
        self.validate_text_bytes(path, "publication checklist")
        if frontmatter.get("run_id") != run_id:
            self.error(path, "run_id does not match the run record")
        if frontmatter.get("artifact_id") != artifact.get("artifact_id"):
            self.error(path, "artifact_id does not match the run record")
        if frontmatter.get("artifact_sha256") != artifact.get("sha256"):
            self.error(path, "artifact_sha256 does not match the run record")
        review = frontmatter.get("review")
        if not isinstance(review, dict) or review.get("result") not in CHECKLIST_RESULTS:
            self.error(path, "review.result must be pending, passed, or failed")
            return None
        if isinstance(review, dict) and review.get("result") == "passed":
            if not frontmatter.get("destination"):
                self.error(path, "passed checklist requires a destination")
            if not review.get("reviewed_by") or not review.get("reviewed_at"):
                self.error(path, "passed checklist requires reviewer and review time")
            self.validate_timestamp(review.get("reviewed_at"), path, "review.reviewed_at")
            matching_gate = any(
                gate.get("status") == "approved"
                and gate.get("artifact_id") == artifact.get("artifact_id")
                and gate.get("platform") == frontmatter.get("platform")
                and gate.get("destination") == frontmatter.get("destination")
                and gate.get("artifact_sha256") == artifact.get("sha256")
                for gate in publish_approvals
            )
            if not matching_gate:
                self.error(path, "passed checklist requires a matching publish_approved decision")
        return (
            str(review.get("result")),
            str(frontmatter.get("platform", "")),
            str(frontmatter.get("destination", "")),
            str(review.get("reviewed_at", "")),
        )

    def validate_private_run(self, run_id: str, public_run: dict[str, Any], has_platform_artifact: bool) -> None:
        run_dir = self.private_root / run_id
        run_path = run_dir / "run-record.yaml"
        candidate_path = run_dir / "candidate.yaml"
        if not run_path.is_file():
            self.error(run_path, "private authority record is missing")
            return
        private_run = self.load_yaml(run_path)
        if private_run is None:
            return
        self.validate_schema_version(private_run, run_path)
        if private_run.get("run_id") != run_id:
            self.error(run_path, "private run_id does not match its directory")
        if private_run.get("storage_class") != "private":
            self.error(run_path, "private authority record must use storage_class: private")
        for field in ("candidate_id", "visibility", "status", "updated_at"):
            if private_run.get(field) != public_run.get(field):
                self.error(run_path, f"private and sanitized {field} differ")
        master = self.require_mapping(private_run, "master", run_path)
        master_sha = ""
        if master is not None:
            master_sha = str(master.get("sha256", ""))
            master_path_value = master.get("path")
            if not isinstance(master_path_value, str) or not master_path_value:
                self.error(run_path, "private master.path is required")
            else:
                master_path = Path(master_path_value)
                if not master_path.is_file():
                    self.error(run_path, f"private master file is missing: {master_path}")
                else:
                    if not master_path.resolve().is_relative_to(run_dir.resolve()):
                        self.error(run_path, "private master.path must remain inside its run directory")
                    self.validate_text_bytes(master_path, "private master")
                    actual_sha = self.hash_file(master_path)
                    if master.get("sha256") != actual_sha:
                        self.error(run_path, "private master.sha256 does not match file bytes")
                    if public_run.get("master", {}).get("sha256") != actual_sha:
                        self.error(run_path, "sanitized and private master hashes differ")
        approvals = self.require_mapping(private_run, "approvals", run_path)
        public_approvals = public_run.get("approvals", {})
        if approvals is not None:
            for gate_name in MASTER_GATES:
                self.validate_approval(approvals.get(gate_name), gate_name, master_sha, run_path)
                private_gate = approvals.get(gate_name, {})
                public_gate = public_approvals.get(gate_name, {}) if isinstance(public_approvals, dict) else {}
                for field in ("decision_id", "status", "at", "artifact_sha256"):
                    if private_gate.get(field) != public_gate.get(field):
                        self.error(run_path, f"private and sanitized approvals.{gate_name}.{field} differ")
            private_publish = approvals.get("publish_approved", [])
            public_publish = public_approvals.get("publish_approved", [])
            for index, public_gate in enumerate(public_publish):
                if not isinstance(public_gate, dict):
                    continue
                if public_gate.get("status") == "pending":
                    matching = any(
                        isinstance(private_gate, dict)
                        and all(
                            private_gate.get(field) == public_gate.get(field)
                            for field in ("status", "artifact_id", "platform", "destination", "artifact_sha256")
                        )
                        for private_gate in private_publish
                    )
                else:
                    matching = any(
                        isinstance(private_gate, dict)
                        and all(
                            private_gate.get(field) == public_gate.get(field)
                            for field in (
                                "decision_id",
                                "status",
                                "at",
                                "artifact_id",
                                "platform",
                                "destination",
                                "artifact_sha256",
                            )
                        )
                        for private_gate in private_publish
                    )
                if not matching:
                    self.error(run_path, f"sanitized publish decision {index} has no private authority match")
        private_artifacts = self.require_list(private_run, "artifacts", run_path) or []
        public_artifacts = public_run.get("artifacts", [])
        private_by_id = {
            item.get("artifact_id"): item
            for item in private_artifacts
            if isinstance(item, dict) and item.get("artifact_id")
        }
        public_by_id = {
            item.get("artifact_id"): item
            for item in public_artifacts
            if isinstance(item, dict) and item.get("artifact_id")
        }
        if set(private_by_id) != set(public_by_id):
            self.error(run_path, "private and sanitized artifact ID sets differ")
        for artifact_id in set(private_by_id) & set(public_by_id):
            for field in ("type", "platform", "sha256", "status"):
                if private_by_id[artifact_id].get(field) != public_by_id[artifact_id].get(field):
                    self.error(run_path, f"private and sanitized artifact {artifact_id} {field} differ")
        if private_run.get("publications") != public_run.get("publications"):
            self.error(run_path, "private and sanitized publication records differ")
        self.validate_feishu(private_run, run_path, master_sha)
        signal_path = run_dir / "signal.yaml"
        if not signal_path.is_file():
            self.error(signal_path, "signal record is missing")
        else:
            signal = self.load_yaml(signal_path)
            if signal is not None:
                self.validate_schema_version(signal, signal_path)
                if signal.get("visibility") != private_run.get("visibility"):
                    self.error(signal_path, "signal and run visibility differ")
                source = self.require_mapping(signal, "source", signal_path)
                authorization = self.require_mapping(source, "authorization", signal_path) if source else None
                if authorization is not None:
                    for field in ("status", "authorized_by", "authorized_at", "scope", "persistence"):
                        if not authorization.get(field):
                            self.error(signal_path, f"source.authorization.{field} is required")
                    self.validate_timestamp(
                        authorization.get("authorized_at"), signal_path, "source.authorization.authorized_at"
                    )
        if not candidate_path.is_file():
            self.error(candidate_path, "candidate record is missing")
        else:
            self.validate_candidate(candidate_path, has_platform_artifact)

    def validate_public_run(self, path: Path) -> None:
        run = self.load_yaml(path)
        if run is None:
            return
        self.checked_runs += 1
        self.validate_schema_version(run, path)
        self.validate_text_bytes(path, "sanitized run record")
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
            self.error(path, f"run_id is invalid: {run_id}")
            return
        if path.stem != run_id:
            self.error(path, "file name must match run_id")
        if run.get("storage_class") != "sanitized_public":
            self.error(path, "registry record must use storage_class: sanitized_public")
        if run.get("visibility") not in {"public", "public_after_redaction"}:
            self.error(path, "sanitized record visibility must be public or public_after_redaction")
        if run.get("candidate_path"):
            self.error(path, "sanitized record must clear candidate_path")
        if run.get("status") not in RUN_STATES:
            self.error(path, f"status is invalid: {run.get('status')}")
        self.validate_timestamp(run.get("started_at"), path, "started_at")
        self.validate_timestamp(run.get("updated_at"), path, "updated_at")
        if WINDOWS_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig")):
            self.error(path, "sanitized record contains an absolute Windows path")
        if "claims" in run:
            self.error(path, "claims must be nested under research.claims")

        research = self.require_mapping(run, "research", path)
        source_ids: set[str] = set()
        if research is not None:
            for key in ("budget", "usage"):
                self.require_mapping(research, key, path)
            self.require_list(research, "tracks", path)
            sources = self.require_list(research, "sources", path)
            claims = self.require_list(research, "claims", path)
            if sources is not None:
                for index, source in enumerate(sources):
                    if not isinstance(source, dict):
                        self.error(path, f"research.sources[{index}] must be a mapping")
                        continue
                    source_id = source.get("source_id")
                    if not source_id:
                        self.error(path, f"research.sources[{index}].source_id is required")
                    elif source_id in source_ids:
                        self.error(path, f"duplicate source_id: {source_id}")
                    else:
                        source_ids.add(source_id)
                    version = source.get("version")
                    if not version:
                        self.error(path, f"research.sources[{index}].version is required")
                    elif not isinstance(version, str) or VAGUE_VERSION_RE.fullmatch(version.strip()):
                        self.error(path, f"research.sources[{index}].version must identify a reproducible version")
                    self.validate_timestamp(source.get("accessed_at"), path, f"research.sources[{index}].accessed_at")
            if claims is not None:
                for index, claim in enumerate(claims):
                    if not isinstance(claim, dict):
                        self.error(path, f"research.claims[{index}] must be a mapping")
                        continue
                    for source_id in claim.get("source_ids", []):
                        if source_id not in source_ids:
                            self.error(path, f"research.claims[{index}] references unknown source {source_id}")

        master = self.require_mapping(run, "master", path)
        if master is None:
            return
        if master.get("path"):
            self.error(path, "sanitized master.path must be empty")
        master_sha = master.get("sha256")
        self.validate_sha(master_sha, path, "master.sha256")
        approvals = self.require_mapping(run, "approvals", path)
        publish_approvals: list[dict[str, Any]] = []
        if approvals is not None:
            for gate_name in MASTER_GATES:
                self.validate_approval(approvals.get(gate_name), gate_name, master_sha, path)
            publish = self.require_list(approvals, "publish_approved", path)
            if publish is not None:
                for index, gate in enumerate(publish):
                    if not isinstance(gate, dict):
                        self.error(path, f"approvals.publish_approved[{index}] must be a mapping")
                        continue
                    status = gate.get("status")
                    if status not in APPROVAL_STATES:
                        self.error(path, f"approvals.publish_approved[{index}].status is invalid")
                    if status in {"approved", "not_required", "changes_requested", "rejected"}:
                        decision_id = gate.get("decision_id")
                        if not isinstance(decision_id, str) or not DECISION_ID_RE.fullmatch(decision_id):
                            self.error(path, f"approvals.publish_approved[{index}].decision_id is required")
                        for field in (
                            "platform",
                            "destination",
                            "artifact_id",
                            "by",
                            "at",
                            "scope",
                            "notes",
                        ):
                            if not gate.get(field):
                                self.error(path, f"approvals.publish_approved[{index}].{field} is required")
                        self.validate_sha(
                            gate.get("artifact_sha256"), path, f"approvals.publish_approved[{index}].artifact_sha256"
                        )
                        self.validate_timestamp(gate.get("at"), path, f"approvals.publish_approved[{index}].at")
                    publish_approvals.append(gate)

        disclosure = (approvals or {}).get("disclosure_approved", {})
        if disclosure.get("status") != "approved" or disclosure.get("artifact_sha256") != master_sha:
            self.error(path, "sanitized record requires current disclosure approval")
        self.validate_feishu(run, path, master_sha)

        publications = self.require_list(run, "publications", path) or []
        artifacts = self.require_list(run, "artifacts", path) or []
        artifacts_by_id = {
            artifact.get("artifact_id"): artifact
            for artifact in artifacts
            if isinstance(artifact, dict) and artifact.get("artifact_id")
        }
        if len(artifacts_by_id) != len([item for item in artifacts if isinstance(item, dict)]):
            self.error(path, "every artifact requires a unique artifact_id")
        has_platform_artifact = False
        checklist_results: dict[tuple[str, str, str], tuple[str, str]] = {}
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                self.error(path, f"artifacts[{index}] must be a mapping")
                continue
            artifact_type = artifact.get("type")
            if artifact_type not in ARTIFACT_TYPES:
                self.error(path, f"artifacts[{index}].type is invalid: {artifact_type}")
            if artifact.get("status") not in ARTIFACT_STATES:
                self.error(path, f"artifacts[{index}].status is invalid: {artifact.get('status')}")
            artifact_sha = artifact.get("sha256")
            self.validate_sha(artifact_sha, path, f"artifacts[{index}].sha256")
            relative_value = artifact.get("path")
            has_platform_artifact = artifact_type == "platform_article" or has_platform_artifact
            if artifact_type == "master_article":
                if relative_value:
                    self.error(path, "sanitized master artifact paths must be empty")
                continue
            artifact_path = self.resolve_hub_path(relative_value, path, f"artifacts[{index}].path")
            if artifact_path is None:
                continue
            if not artifact_path.is_file():
                self.error(path, f"artifact file is missing: {relative_value}")
                continue
            if artifact_path.name != "index.md":
                self.error(path, f"artifacts[{index}].path must point to index.md")
            self.validate_text_bytes(artifact_path, f"artifacts[{index}] article body")
            self.checked_artifacts += 1
            manifest_path = self.resolve_hub_path(
                artifact.get("manifest_path"), path, f"artifacts[{index}].manifest_path"
            )
            if manifest_path is None or not manifest_path.is_file():
                if manifest_path is not None:
                    self.error(path, f"artifact manifest is missing: {artifact.get('manifest_path')}")
                continue
            actual_sha = self.validate_artifact_manifest(manifest_path, artifact, artifact_path, path)
            if artifact_sha != actual_sha:
                self.error(path, f"artifacts[{index}].sha256 does not match the artifact manifest")
            meta_value = artifact.get("meta_path")
            meta_path = self.resolve_hub_path(meta_value, path, f"artifacts[{index}].meta_path")
            if meta_path is not None:
                if not meta_path.is_file():
                    self.error(path, f"artifact metadata is missing: {meta_value}")
                elif meta_path.parent.resolve() != artifact_path.parent.resolve():
                    self.error(path, f"artifacts[{index}].meta_path must be beside index.md")
                else:
                    self.validate_meta(
                        meta_path,
                        artifact,
                        master_sha,
                        run_id,
                        str(run.get("candidate_id", "")),
                        approvals or {},
                        publications,
                    )
            checklist_path = artifact_path.parent / "publication-checklist.md"
            if artifact_type == "platform_article":
                if checklist_path.is_file():
                    checklist_result = self.validate_checklist(
                        checklist_path, artifact, run_id, publish_approvals
                    )
                    if checklist_result is not None:
                        result, checklist_platform, checklist_destination, checklist_reviewed_at = checklist_result
                        checklist_results[
                            (str(artifact.get("artifact_id")), checklist_platform, checklist_destination)
                        ] = (result, checklist_reviewed_at)
                else:
                    self.error(checklist_path, "platform artifact publication checklist is missing")

        if has_platform_artifact:
            for gate_name in MASTER_GATES:
                gate = (approvals or {}).get(gate_name, {})
                if gate.get("status") != "approved" or gate.get("artifact_sha256") != master_sha:
                    self.error(path, f"platform artifact requires current approvals.{gate_name}")

        publish_keys: set[tuple[Any, Any, Any]] = set()
        for index, gate in enumerate(publish_approvals):
            if gate.get("status") == "pending":
                continue
            key = (gate.get("artifact_id"), gate.get("platform"), gate.get("destination"))
            if key in publish_keys:
                self.error(path, f"duplicate publish decision target: {key}")
            publish_keys.add(key)
            artifact = artifacts_by_id.get(gate.get("artifact_id"))
            if not isinstance(artifact, dict):
                self.error(path, f"approvals.publish_approved[{index}] references an unknown artifact")
                continue
            if gate.get("platform") != artifact.get("platform"):
                self.error(path, f"approvals.publish_approved[{index}].platform does not match the artifact")
            if gate.get("artifact_sha256") != artifact.get("sha256"):
                self.error(path, f"approvals.publish_approved[{index}].artifact_sha256 does not match the artifact")

        self.require_list(run, "source_authorizations", path)
        self.require_list(run, "metrics", path)
        self.require_list(run, "failures", path)
        self.require_list(run, "changes", path)
        for index, publication in enumerate(publications):
            label = f"publications[{index}]"
            if not isinstance(publication, dict):
                self.error(path, f"{label} must be a mapping")
                continue
            for field in ("artifact_id", "platform", "destination", "url", "published_at"):
                if not publication.get(field):
                    self.error(path, f"{label}.{field} is required")
            self.validate_timestamp(publication.get("published_at"), path, f"{label}.published_at")
            artifact = artifacts_by_id.get(publication.get("artifact_id"))
            if not isinstance(artifact, dict):
                self.error(path, f"{label} references an unknown artifact")
                continue
            if publication.get("platform") != artifact.get("platform"):
                self.error(path, f"{label}.platform does not match the artifact")
            if artifact.get("status") not in {"published", "archived"}:
                self.error(path, f"{label} requires artifact.status published or archived")
            publication_key = (
                str(publication.get("artifact_id", "")),
                str(publication.get("platform", "")),
                str(publication.get("destination", "")),
            )
            checklist_result, checklist_reviewed_at = checklist_results.get(publication_key, ("", ""))
            if checklist_result != "passed":
                self.error(path, f"{label} requires a passed publication checklist")
            matching_gates = [
                gate
                for gate in publish_approvals
                if (
                gate.get("status") == "approved"
                and gate.get("artifact_id") == publication.get("artifact_id")
                and gate.get("platform") == publication.get("platform")
                and gate.get("destination") == publication.get("destination")
                and gate.get("artifact_sha256") == artifact.get("sha256")
                )
            ]
            if not matching_gates:
                self.error(path, f"{label} requires a matching publish_approved decision")
            published_at = self.parse_timestamp(publication.get("published_at"))
            decision_at = self.parse_timestamp(matching_gates[0].get("at")) if matching_gates else None
            reviewed_at = self.parse_timestamp(checklist_reviewed_at)
            if published_at and decision_at and published_at < decision_at:
                self.error(path, f"{label}.published_at predates publish approval")
            if published_at and reviewed_at and published_at < reviewed_at:
                self.error(path, f"{label}.published_at predates checklist review")
        if run.get("status") == "published" and not publications:
            self.error(path, "published run requires at least one publication record")
        if publications and run.get("status") not in {"published", "archived"}:
            self.error(path, "run with publication records must use status published or archived")
        for artifact_id, artifact in artifacts_by_id.items():
            if artifact.get("status") == "published" and not any(
                publication.get("artifact_id") == artifact_id
                for publication in publications
                if isinstance(publication, dict)
            ):
                self.error(path, f"published artifact {artifact_id} requires a publication record")
        self.require_mapping(run, "privacy", path)
        self.require_mapping(run, "quality", path)
        self.validate_private_run(run_id, run, has_platform_artifact)

    def validate_templates(self) -> None:
        template_dir = self.content_hub / "templates" / "pipeline"
        for name in (
            "signal.yaml",
            "candidate.yaml",
            "run-record.yaml",
            "feishu-review-workspace.yaml",
            "artifact-manifest.yaml",
        ):
            path = template_dir / name
            if not path.is_file():
                self.error(path, "required pipeline template is missing")
            else:
                record = self.load_yaml(path)
                self.validate_text_bytes(path, f"template {name}")
                if record is not None:
                    self.validate_schema_version(record, path)
        meta_path = self.content_hub / "templates" / "meta.yaml"
        meta = self.load_yaml(meta_path) if meta_path.is_file() else None
        if meta is None:
            if not meta_path.is_file():
                self.error(meta_path, "metadata template is missing")
        else:
            self.validate_text_bytes(meta_path, "metadata template")
            pipeline = meta.get("pipeline", {})
            approvals = pipeline.get("approvals", {}) if isinstance(pipeline, dict) else {}
            for name in (*MASTER_GATES, "publish_approved"):
                gate = approvals.get(name)
                if not isinstance(gate, dict) or gate.get("status") != "pending":
                    self.error(meta_path, f"pipeline.approvals.{name} must default to pending")
        checklist_template = template_dir / "publication-checklist.md"
        checklist_frontmatter = (
            self.load_frontmatter(checklist_template) if checklist_template.is_file() else None
        )
        if checklist_frontmatter is None:
            if not checklist_template.is_file():
                self.error(checklist_template, "publication checklist template is missing")
        else:
            self.validate_text_bytes(checklist_template, "publication checklist template")
            self.validate_schema_version(checklist_frontmatter, checklist_template)
            review = checklist_frontmatter.get("review")
            if not isinstance(review, dict) or review.get("result") != "pending":
                self.error(checklist_template, "review.result must default to pending")
        attributes_path = self.content_hub / ".gitattributes"
        if not attributes_path.is_file():
            self.error(attributes_path, "LF enforcement is required for stable artifact hashes")
        else:
            self.validate_text_bytes(attributes_path, ".gitattributes")
            attributes = attributes_path.read_text(encoding="utf-8-sig")
            for rule in ("* text=auto eol=lf", "*.md text eol=lf", "*.yaml text eol=lf"):
                if rule not in attributes:
                    self.error(attributes_path, f"missing rule: {rule}")

    def run(self) -> int:
        self.validate_templates()
        registry = self.content_hub / "registry" / "pipeline-runs"
        if not registry.is_dir():
            self.error(registry, "pipeline run registry is missing")
        else:
            records = sorted(registry.glob("*.yaml"))
            if self.run_id:
                records = [path for path in records if path.stem == self.run_id]
                if not records:
                    self.error(registry / f"{self.run_id}.yaml", "requested run was not found")
            for path in records:
                self.validate_public_run(path)

        for warning in self.warnings:
            print(f"WARNING: {warning}")
        for error in self.errors:
            print(f"ERROR: {error}")
        print(
            f"Checked {self.checked_runs} run(s) and {self.checked_artifacts} artifact(s): "
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)."
        )
        return 1 if self.errors else 0


def parse_args() -> argparse.Namespace:
    script = Path(__file__).resolve()
    workspace = script.parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-hub", type=Path, default=workspace / "content-hub")
    parser.add_argument("--private-root", type=Path, default=workspace / "private" / "content-pipeline")
    parser.add_argument("--run-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validator = Validator(args.content_hub, args.private_root, args.run_id)
    return validator.run()


if __name__ == "__main__":
    sys.exit(main())
