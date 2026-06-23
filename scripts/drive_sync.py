#!/usr/bin/env python3
"""Poll the here.now ESG Skills Intake Drive and write incoming bundles to the local inbox.

Called by launchd at most once per minute.

Required environment variables:
  HERENOW_API_KEY           - owner API key (read/write/move access)
  HERENOW_INTAKE_DRIVE_ID   - Drive identifier, e.g. drv_01abc...

Optional:
  ESG_INTAKE_ROOT           - repository root (defaults to script's parent)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("ESG_INTAKE_ROOT", Path(__file__).resolve().parents[1]))
INBOX_DIR = ROOT / "var" / "intake" / "inbox"
NEEDS_ATTENTION_DIR = ROOT / "var" / "intake" / "needs-attention"
DRIVE_API = "https://here.now/api/v1/drives"
INCOMING_PREFIX = "incoming/"
CLAIMED_PREFIX = "claimed/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s drive-sync %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def _api_key() -> str:
    key = os.environ.get("HERENOW_API_KEY", "").strip()
    if not key:
        creds = Path.home() / ".herenow" / "credentials"
        if creds.is_file():
            key = creds.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("HERENOW_API_KEY not set and ~/.herenow/credentials is missing")
    return key


def _drive_id() -> str:
    drive_id = os.environ.get("HERENOW_INTAKE_DRIVE_ID", "").strip()
    if not drive_id:
        raise RuntimeError("HERENOW_INTAKE_DRIVE_ID environment variable is not set")
    return drive_id


def _request(method: str, url: str, *, api_key: str, body: bytes | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body_text}") from exc


def _list_incoming(drive_id: str, api_key: str) -> list[dict]:
    url = f"{DRIVE_API}/{drive_id}/files?prefix={INCOMING_PREFIX}"
    data = _request("GET", url, api_key=api_key)
    files = data.get("files", [])
    cursor = data.get("nextCursor")
    while cursor:
        next_data = _request(
            "GET", f"{url}&cursor={cursor}", api_key=api_key
        )
        files.extend(next_data.get("files", []))
        cursor = next_data.get("nextCursor")
    return [f for f in files if f["path"].endswith(".json")]


def _download_file(drive_id: str, path: str, api_key: str) -> bytes:
    encoded_path = urllib.parse.quote(path, safe="")
    url = f"{DRIVE_API}/{drive_id}/files/{encoded_path}"
    headers = {"Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} downloading {path}: {body_text}") from exc


def _move_file(drive_id: str, from_path: str, to_path: str, etag: str, api_key: str) -> None:
    url = f"{DRIVE_API}/{drive_id}/files/move"
    body = json.dumps({"from": from_path, "to": to_path, "ifMatch": etag}).encode()
    _request("POST", url, api_key=api_key, body=body)


def _submission_id_from_path(path: str) -> str:
    # path is like incoming/<uuid>.json
    return Path(path).stem


def _write_inbox_atomic(
    submission_id: str, bundle_bytes: bytes, remote_sha256: str
) -> Path:
    actual_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    if actual_sha256 != remote_sha256.removeprefix("sha256:"):
        raise ValueError(
            f"SHA-256 mismatch for {submission_id}: "
            f"expected {remote_sha256}, got {actual_sha256}"
        )

    bundle = json.loads(bundle_bytes.decode("utf-8"))
    skill_md = bundle.get("skill_md", "")
    if not isinstance(skill_md, str) or not skill_md.strip():
        raise ValueError(f"Bundle {submission_id} is missing skill_md")

    submission_dir = INBOX_DIR / submission_id
    if submission_dir.exists():
        log.info("Already in inbox: %s — skipping", submission_id)
        return submission_dir

    # Write atomically via a temp dir in the same filesystem
    tmp_dir = INBOX_DIR.parent / f".tmp-{submission_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        (tmp_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        submission_meta = {
            "submission_id": submission_id,
            "sha256": actual_sha256,
            "title": bundle.get("title", ""),
            "public_name": bundle.get("public_name", ""),
            "public_contact": bundle.get("public_contact", ""),
            "rights_confirmed": bundle.get("rights_confirmed", False),
            "boundary_confirmed": bundle.get("boundary_confirmed", False),
            "submitted_at": bundle.get("submitted_at", ""),
        }
        (tmp_dir / "submission.json").write_text(
            json.dumps(submission_meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        tmp_dir.rename(submission_dir)
    except Exception:
        if tmp_dir.exists():
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    log.info("Wrote inbox: %s", submission_id)
    return submission_dir


def _move_to_needs_attention(submission_id: str, reason: str) -> None:
    attention_dir = NEEDS_ATTENTION_DIR / submission_id
    attention_dir.mkdir(parents=True, exist_ok=True)
    (attention_dir / "error.txt").write_text(reason + "\n", encoding="utf-8")
    log.error("Needs attention: %s — %s", submission_id, reason)


def sync_once() -> int:
    api_key = _api_key()
    drive_id = _drive_id()

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_ATTENTION_DIR.mkdir(parents=True, exist_ok=True)

    try:
        files = _list_incoming(drive_id, api_key)
    except Exception as exc:
        log.error("Failed to list Drive incoming/: %s", exc)
        return 1

    if not files:
        log.debug("No incoming files")
        return 0

    log.info("Found %d incoming file(s)", len(files))
    errors = 0

    for file_meta in files:
        path = file_meta["path"]
        etag = file_meta["etag"]
        remote_sha256 = file_meta.get("sha256", "")
        submission_id = _submission_id_from_path(path)

        # Already claimed?
        if (INBOX_DIR / submission_id).exists():
            log.info("Already claimed locally: %s", submission_id)
            try:
                claimed_path = CLAIMED_PREFIX + Path(path).name
                _move_file(drive_id, path, claimed_path, etag, api_key)
            except Exception as exc:
                log.warning("Could not move already-claimed %s: %s", submission_id, exc)
            continue

        try:
            bundle_bytes = _download_file(drive_id, path, api_key)
        except Exception as exc:
            _move_to_needs_attention(submission_id, f"download failed: {exc}")
            errors += 1
            continue

        try:
            _write_inbox_atomic(submission_id, bundle_bytes, remote_sha256)
        except ValueError as exc:
            _move_to_needs_attention(submission_id, str(exc))
            errors += 1
            continue
        except Exception as exc:
            _move_to_needs_attention(submission_id, f"write failed: {exc}")
            errors += 1
            continue

        try:
            claimed_path = CLAIMED_PREFIX + Path(path).name
            _move_file(drive_id, path, claimed_path, etag, api_key)
            log.info("Claimed: %s → %s", path, claimed_path)
        except Exception as exc:
            log.warning(
                "Wrote inbox for %s but failed to mark claimed on Drive: %s. "
                "Next run will skip (already in inbox).",
                submission_id, exc,
            )

    return 1 if errors else 0


def main() -> int:
    try:
        return sync_once()
    except RuntimeError as exc:
        log.error("%s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
