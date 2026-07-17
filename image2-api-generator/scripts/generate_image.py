#!/usr/bin/env python3
"""Generate one image through an OpenAI-compatible Image2 API."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


MODEL = "gpt-image-2"
SKILL_ROOT = Path(__file__).resolve().parents[1]
KNOWN_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class ImageGenerationError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an image using the fixed model 'gpt-image-2'."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Image generation prompt")
    prompt_group.add_argument(
        "--prompt-file", type=Path, help="UTF-8 text file containing the prompt"
    )
    parser.add_argument("--out", type=Path, help="Output image path")
    parser.add_argument("--env-file", type=Path, help="Explicit .env file")
    parser.add_argument("--size", default="1024x1024", help="Requested image size")
    parser.add_argument("--quality", help="Optional provider-specific quality value")
    parser.add_argument(
        "--output-format",
        choices=("png", "jpeg", "webp"),
        help="Optional provider-specific output format",
    )
    parser.add_argument("--timeout", type=float, default=300, help="Timeout in seconds")
    parser.add_argument(
        "--overwrite", action="store_true", help="Allow replacing an existing output"
    )
    return parser.parse_args()


def read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ImageGenerationError(
                f"Invalid .env entry at {path}:{line_number}; expected KEY=VALUE"
            )
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def load_config(explicit_env: Path | None) -> tuple[str, str]:
    if explicit_env:
        paths = [explicit_env.expanduser().resolve()]
        if not paths[0].is_file():
            raise ImageGenerationError(f"Environment file not found: {paths[0]}")
    else:
        candidates = [SKILL_ROOT / ".env", Path.cwd() / ".env"]
        paths = []
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved.is_file() and resolved not in paths:
                paths.append(resolved)

    values: dict[str, str] = {}
    for path in paths:
        values.update(read_dotenv(path))

    api_key = os.environ.get("IMAGE_API_KEY") or values.get("IMAGE_API_KEY", "")
    base_url = os.environ.get("IMAGE_BASE_URL") or values.get("IMAGE_BASE_URL", "")
    missing = [
        name
        for name, value in (
            ("IMAGE_API_KEY", api_key),
            ("IMAGE_BASE_URL", base_url),
        )
        if not value.strip()
    ]
    if missing:
        raise ImageGenerationError(
            f"Missing configuration: {', '.join(missing)}. Set it in a .env file."
        )

    base_url = base_url.strip().rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ImageGenerationError("IMAGE_BASE_URL must be an absolute HTTP(S) URL")
    return api_key.strip(), base_url


def generation_endpoint(base_url: str) -> str:
    if base_url.endswith("/images/generations"):
        return base_url
    if base_url.endswith("/images"):
        return f"{base_url}/generations"
    return f"{base_url}/images/generations"


def api_error_message(exc: HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8", errors="replace"))
        error = payload.get("error", payload)
        if isinstance(error, dict):
            message = error.get("message") or error.get("code")
        else:
            message = str(error)
        if message:
            return str(message)[:1000]
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        pass
    return exc.reason or "request failed"


def post_generation(
    endpoint: str, api_key: str, payload: dict[str, object], timeout: float
) -> dict[str, object]:
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "codex-image2-api-generator/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        raise ImageGenerationError(
            f"Image API returned HTTP {exc.code}: {api_error_message(exc)}"
        ) from None
    except URLError as exc:
        raise ImageGenerationError(f"Image API request failed: {exc.reason}") from None

    try:
        result = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ImageGenerationError("Image API returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise ImageGenerationError("Image API returned an unexpected JSON value")
    return result


def decode_result(result: dict[str, object], timeout: float) -> bytes:
    data = result.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ImageGenerationError("Image API response does not contain data[0]")
    item = data[0]

    encoded = item.get("b64_json") or item.get("b64")
    if isinstance(encoded, str) and encoded:
        try:
            return base64.b64decode("".join(encoded.split()), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ImageGenerationError("Image API returned invalid base64 image data") from exc

    image_url = item.get("url")
    if isinstance(image_url, str) and image_url:
        parsed = urlparse(image_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ImageGenerationError("Image API returned an invalid image URL")
        download = Request(
            image_url,
            headers={"User-Agent": "codex-image2-api-generator/1.0"},
            method="GET",
        )
        try:
            with urlopen(download, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            raise ImageGenerationError(
                f"Image download returned HTTP {exc.code}: {exc.reason}"
            ) from None
        except URLError as exc:
            raise ImageGenerationError(f"Image download failed: {exc.reason}") from None

    raise ImageGenerationError("Image API response has neither b64_json nor url")


def detect_extension(image: bytes) -> str | None:
    if image.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if image.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if len(image) >= 12 and image.startswith(b"RIFF") and image[8:12] == b"WEBP":
        return ".webp"
    return None


def output_path(requested: Path | None, image: bytes, output_format: str | None) -> Path:
    detected = detect_extension(image)
    fallback = ".jpg" if output_format == "jpeg" else f".{output_format or 'png'}"
    extension = detected or fallback
    if requested is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return Path.cwd() / "output" / "imagegen" / f"image2-{stamp}{extension}"

    path = requested.expanduser().resolve()
    if not path.suffix:
        path = path.with_suffix(extension)
    elif detected and path.suffix.lower() in KNOWN_EXTENSIONS and path.suffix.lower() != detected:
        path = path.with_suffix(detected)
    return path


def main() -> int:
    args = parse_args()
    try:
        prompt = (
            args.prompt_file.read_text(encoding="utf-8-sig").strip()
            if args.prompt_file
            else args.prompt.strip()
        )
        if not prompt:
            raise ImageGenerationError("Prompt must not be empty")

        api_key, base_url = load_config(args.env_file)
        payload: dict[str, object] = {
            "model": MODEL,
            "prompt": prompt,
            "size": args.size,
            "n": 1,
        }
        if args.quality:
            payload["quality"] = args.quality
        if args.output_format:
            payload["output_format"] = args.output_format

        result = post_generation(
            generation_endpoint(base_url), api_key, payload, args.timeout
        )
        image = decode_result(result, args.timeout)
        if not image:
            raise ImageGenerationError("Image API returned an empty image")

        destination = output_path(args.out, image, args.output_format)
        if destination.exists() and not args.overwrite:
            raise ImageGenerationError(
                f"Output already exists: {destination}. Use --overwrite to replace it."
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(image)
        print(destination)
        return 0
    except (ImageGenerationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
