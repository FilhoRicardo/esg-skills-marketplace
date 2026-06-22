#!/usr/bin/env python3
"""Publish the static site directory to here.now."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _content_type(path: Path) -> str:
    guessed, _encoding = mimetypes.guess_type(path.name)
    if guessed is None:
        return "application/octet-stream"
    if guessed.startswith("text/") or guessed in {
        "application/javascript",
        "application/json",
        "application/xml",
        "image/svg+xml",
    }:
        return f"{guessed}; charset=utf-8"
    return guessed


def _file_manifest(root: Path) -> tuple[list[dict[str, object]], dict[str, bytes]]:
    manifest: list[dict[str, object]] = []
    payloads: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        payloads[relative] = data
        manifest.append(
            {
                "path": relative,
                "size": len(data),
                "contentType": _content_type(path),
                "hash": hashlib.sha256(data).hexdigest(),
            }
        )
    return manifest, payloads


def _request_json(url: str, *, method: str, headers: dict[str, str], data: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        method=method,
        headers=headers,
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _upload(url: str, *, headers: dict[str, str], payload: bytes) -> None:
    request = urllib.request.Request(url, data=payload, method="PUT", headers=headers)
    with urllib.request.urlopen(request):
        return


def publish_directory(directory: Path, *, slug: str, api_key: str, client: str) -> dict[str, object]:
    manifest, payloads = _file_manifest(directory)
    if not manifest:
        raise ValueError(f"{directory} does not contain any files to publish")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-HereNow-Client": client,
    }
    create_payload = {"files": manifest}
    response = _request_json(
        f"https://here.now/api/v1/publish/{slug}",
        method="PUT",
        headers=headers,
        data=create_payload,
    )
    upload = response["upload"]
    for item in upload.get("uploads", []):
        payload = payloads[item["path"]]
        _upload(item["url"], headers=item.get("headers", {}), payload=payload)

    finalized = _request_json(
        upload["finalizeUrl"],
        method="POST",
        headers=headers,
        data={"versionId": upload["versionId"]},
    )
    return finalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--api-key-env", default="HERENOW_API_KEY")
    parser.add_argument("--client", default="codex/publish-site")
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env, "").strip()
    if not api_key:
        print(f"PUBLISH FAILURE: environment variable {args.api_key_env} is empty", file=sys.stderr)
        return 2

    try:
        result = publish_directory(
            args.directory.resolve(),
            slug=args.slug,
            api_key=api_key,
            client=args.client,
        )
    except (OSError, ValueError, KeyError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"PUBLISH FAILURE: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
