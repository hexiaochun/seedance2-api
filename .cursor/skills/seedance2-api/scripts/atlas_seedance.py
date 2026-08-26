#!/usr/bin/env python3
"""Submit and poll Seedance 2.0 video tasks through Atlas Cloud."""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


TEXT_MODEL = "bytedance/seedance-2.0/text-to-video"
IMAGE_MODEL = "bytedance/seedance-2.0/image-to-video"
DEFAULT_BASE_URL = "https://api.atlascloud.ai/api/v1"
SUCCESS_STATES = {"completed", "succeeded"}
FAILURE_STATES = {"failed", "timeout", "canceled", "cancelled"}


class AtlasHTTPError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"Atlas API returned HTTP {status}: {body}")
        self.status = status


def _api_key() -> str:
    key = os.environ.get("ATLASCLOUD_API_KEY")
    if not key:
        raise RuntimeError("ATLASCLOUD_API_KEY is required")
    return key


def _base_url() -> str:
    return os.environ.get("ATLASCLOUD_MEDIA_API_BASE", DEFAULT_BASE_URL).rstrip("/")


def _request_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 60,
) -> dict[str, Any]:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "User-Agent": "seedance2-api/atlas-provider",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:500]
        raise AtlasHTTPError(error.code, body) from error


def _get_with_backoff(url: str, *, attempts: int = 4) -> dict[str, Any]:
    for attempt in range(attempts):
        try:
            return _request_json("GET", url, timeout=30)
        except AtlasHTTPError as error:
            if error.status < 500 and error.status != 429:
                raise
            last_error: Exception = error
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
        if attempt == attempts - 1:
            raise RuntimeError("Atlas prediction polling failed") from last_error
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def _image_value(value: str) -> str:
    if value.startswith(("http://", "https://", "data:", "asset://")):
        return value
    path = Path(value).expanduser()
    if path.is_file():
        return base64.b64encode(path.read_bytes()).decode("ascii")
    return value


def submit(
    prompt: str,
    *,
    image: str | None = None,
    last_image: str | None = None,
    duration: int = 5,
    resolution: str = "720p",
    ratio: str = "adaptive",
    generate_audio: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": IMAGE_MODEL if image else TEXT_MODEL,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "ratio": ratio,
        "generate_audio": generate_audio,
        "watermark": False,
    }
    if image:
        payload["image"] = _image_value(image)
    if last_image:
        if not image:
            raise ValueError("--last-image requires --image")
        payload["last_image"] = _image_value(last_image)

    # Submission is intentionally attempted once because it creates a paid task.
    response = _request_json(
        "POST",
        f"{_base_url()}/model/generateVideo",
        payload=payload,
    )
    prediction = response.get("data", {})
    if not prediction.get("id"):
        raise RuntimeError("Atlas response did not include a prediction id")
    return prediction


def query(prediction_id: str) -> dict[str, Any]:
    response = _get_with_backoff(
        f"{_base_url()}/model/prediction/{prediction_id}"
    )
    return response.get("data", {})


def poll(
    prediction_id: str,
    *,
    interval: float = 5,
    timeout: float = 900,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        prediction = query(prediction_id)
        status = str(prediction.get("status", "unknown")).lower()
        if status in SUCCESS_STATES:
            if not prediction.get("outputs"):
                raise RuntimeError("Atlas prediction completed without output URLs")
            return prediction
        if status in FAILURE_STATES:
            message = prediction.get("error") or prediction.get("message") or status
            raise RuntimeError(f"Atlas video generation failed: {message}")
        time.sleep(interval)
    raise TimeoutError("Atlas video generation timed out")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit_parser = subparsers.add_parser("submit", help="submit one video task")
    submit_parser.add_argument("--prompt", required=True)
    submit_parser.add_argument("--image")
    submit_parser.add_argument("--last-image")
    submit_parser.add_argument("--duration", type=int, choices=range(4, 16), default=5)
    submit_parser.add_argument(
        "--resolution",
        choices=("480p", "720p", "720p-SR", "1080p", "1080p-SR", "1440p-SR", "4k"),
        default="720p",
    )
    submit_parser.add_argument(
        "--ratio",
        choices=("16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"),
        default="adaptive",
    )
    submit_parser.add_argument("--no-audio", action="store_true")

    query_parser = subparsers.add_parser("query", help="query one prediction")
    query_parser.add_argument("--prediction-id", required=True)

    poll_parser = subparsers.add_parser("poll", help="poll until terminal state")
    poll_parser.add_argument("--prediction-id", required=True)
    poll_parser.add_argument("--interval", type=float, default=5)
    poll_parser.add_argument("--timeout", type=float, default=900)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "submit":
        result = submit(
            args.prompt,
            image=args.image,
            last_image=args.last_image,
            duration=args.duration,
            resolution=args.resolution,
            ratio=args.ratio,
            generate_audio=not args.no_audio,
        )
    elif args.command == "query":
        result = query(args.prediction_id)
    else:
        result = poll(
            args.prediction_id,
            interval=args.interval,
            timeout=args.timeout,
        )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
