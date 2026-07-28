#!/usr/bin/env python3
"""Serve the bundled read-only dashboard over the current content workspace."""

from __future__ import annotations

import argparse
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote_to_bytes, urlsplit

from pipeline_runtime import DASHBOARD_HTML, PipelineError, resolve_workspace


LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
EXPOSED_ROOTS = {"articles", "platforms", "shared"}
CSP = (
    "default-src 'self'; "
    "base-uri 'none'; "
    "connect-src 'self'; "
    "font-src 'self'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data: http: https:; "
    "object-src 'none'; "
    "script-src 'unsafe-inline'; "
    "style-src 'unsafe-inline'"
)


class DashboardServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], workspace: Path) -> None:
        self.workspace = workspace.resolve()
        super().__init__(address, DashboardHandler)


class DashboardHandler(BaseHTTPRequestHandler):
    server: DashboardServer
    server_version = "ContentPipelineDashboard/1.0"
    sys_version = ""

    def do_GET(self) -> None:
        self._serve(head_only=False)

    def do_HEAD(self) -> None:
        self._serve(head_only=True)

    def do_POST(self) -> None:
        self._method_not_allowed()

    def do_PUT(self) -> None:
        self._method_not_allowed()

    def do_PATCH(self) -> None:
        self._method_not_allowed()

    def do_DELETE(self) -> None:
        self._method_not_allowed()

    def _method_not_allowed(self) -> None:
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve(self, *, head_only: bool) -> None:
        try:
            path = self._decoded_path()
        except (UnicodeDecodeError, ValueError):
            self.send_error(HTTPStatus.BAD_REQUEST, "invalid request path")
            return

        if path in {"/", "/dashboard"}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/dashboard/")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path in {"/dashboard/", "/dashboard/index.html"}:
            self._send_file(DASHBOARD_HTML, head_only=head_only, html=True)
            return
        if path == "/dashboard/data.json":
            self._send_file(
                self.server.workspace / "dashboard" / "data.json",
                head_only=head_only,
            )
            return

        parts = path.removeprefix("/").split("/")
        if len(parts) < 2 or parts[0] not in EXPOSED_ROOTS:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        candidate = self._safe_workspace_file(parts[0], parts[1:])
        if candidate is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._send_file(candidate, head_only=head_only)

    def _decoded_path(self) -> str:
        raw = urlsplit(self.path).path
        decoded = unquote_to_bytes(raw).decode("utf-8", errors="strict")
        if not decoded.startswith("/") or "\x00" in decoded or "\\" in decoded:
            raise ValueError("unsafe path")
        return decoded

    def _safe_workspace_file(self, root_name: str, parts: list[str]) -> Path | None:
        if any(
            not part or part in {".", ".."} or ":" in part or "\x00" in part
            for part in parts
        ):
            return None
        root = (self.server.workspace / root_name).resolve()
        candidate = root.joinpath(*parts).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return None
        return candidate if candidate.is_file() else None

    def _send_file(self, path: Path, *, head_only: bool, html: bool = False) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            payload = path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        content_type = self._content_type(path)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        if html:
            self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        if not head_only:
            self.wfile.write(payload)

    @staticmethod
    def _content_type(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".html":
            return "text/html; charset=utf-8"
        if suffix == ".json":
            return "application/json; charset=utf-8"
        if suffix in {".md", ".markdown"}:
            return "text/markdown; charset=utf-8"
        guessed, _ = mimetypes.guess_type(path.name)
        return guessed or "application/octet-stream"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", choices=sorted(LOOPBACK_HOSTS))
    parser.add_argument("--port", type=int, default=4174)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.port <= 65535:
        print("Dashboard server failed: port must be between 1 and 65535", file=sys.stderr)
        return 2
    try:
        workspace = resolve_workspace()
        if not DASHBOARD_HTML.is_file():
            raise PipelineError(f"bundled dashboard is missing: {DASHBOARD_HTML}")
        server = DashboardServer((args.host, args.port), workspace)
    except (PipelineError, OSError) as exc:
        print(f"Dashboard server failed: {exc}", file=sys.stderr)
        return 2

    url = f"http://{args.host}:{args.port}/dashboard/"
    print(f"Serving content dashboard at {url}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
