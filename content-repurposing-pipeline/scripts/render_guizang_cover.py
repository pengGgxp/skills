#!/usr/bin/env python3
"""Render a single-slide local HTML cover to an exact-size PNG with Chrome."""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
from pathlib import Path


WINDOWS_CHROME_PATHS = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)


def find_chrome(explicit: Path | None) -> Path:
    if explicit:
        chrome = explicit.expanduser().resolve()
        if chrome.is_file():
            return chrome
        raise ValueError("the supplied Chrome executable does not exist")
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    for candidate in WINDOWS_CHROME_PATHS:
        if candidate.is_file():
            return candidate.resolve()
    raise ValueError("Chrome or Chromium was not found; pass --chrome with its executable path")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Chrome did not produce a valid PNG")
    return struct.unpack(">II", data[16:24])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="private single-slide HTML file")
    parser.add_argument("--output", type=Path, required=True, help="destination PNG path")
    parser.add_argument("--width", type=int, required=True, help="verified platform width in pixels")
    parser.add_argument("--height", type=int, required=True, help="verified platform height in pixels")
    parser.add_argument("--chrome", type=Path, help="Chrome or Chromium executable")
    parser.add_argument("--virtual-time-budget", type=int, default=3000, help="render wait in milliseconds")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0:
        parser.error("--width and --height must be positive integers")
    if args.virtual_time_budget < 0:
        parser.error("--virtual-time-budget must be non-negative")
    return args


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in {".html", ".htm"}:
        print("ERROR: --source must be an existing local HTML file", file=sys.stderr)
        return 2
    if output.suffix.lower() != ".png":
        print("ERROR: --output must use the .png extension", file=sys.stderr)
        return 2
    if output.exists() and not args.force:
        print("ERROR: output already exists; choose another path or pass --force", file=sys.stderr)
        return 2
    try:
        chrome = find_chrome(args.chrome)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={args.width},{args.height}",
        f"--virtual-time-budget={args.virtual_time_budget}",
        f"--screenshot={output}",
        source.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    if result.returncode != 0 or not output.is_file():
        detail = (result.stderr or result.stdout or "Chrome render failed").strip().splitlines()[-1]
        print(f"ERROR: {detail}", file=sys.stderr)
        return 1
    try:
        actual = png_dimensions(output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    expected = (args.width, args.height)
    if actual != expected:
        print(
            f"ERROR: rendered PNG is {actual[0]}x{actual[1]}, expected {expected[0]}x{expected[1]}",
            file=sys.stderr,
        )
        return 1
    print(f"Rendered {output} at {actual[0]}x{actual[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
