#!/usr/bin/env python3
"""Lightweight HTTP intake server — receives skill submissions from the here.now proxy.

Runs as a persistent daemon on the Mac mini. The here.now proxy forwards
POST /intake from the public site; Cloudflare Tunnel exposes this server at
a stable URL without opening a public port.

Required environment variables:
  MAC_MINI_INTAKE_SECRET   - shared secret; here.now injects this as Bearer token

Optional:
  INTAKE_PORT              - port to listen on (default: 8765)
  ESG_INTAKE_ROOT          - repository root (default: script parent directory)
"""

from __future__ import annotations

import hashlib
import http.server
import json
import logging
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(os.environ.get("ESG_INTAKE_ROOT", Path(__file__).resolve().parents[1]))
INBOX_DIR = ROOT / "var" / "intake" / "inbox"
NEEDS_ATTENTION_DIR = ROOT / "var" / "intake" / "needs-attention"
PORT = int(os.environ.get("INTAKE_PORT", "8765"))

SKILL_MD_MAX_BYTES = 40_000
TITLE_MIN = 4
TITLE_MAX = 80
SKILL_MIN_CHARS = 80
PUBLIC_FIELD_MAX = 200

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s intake-server %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def _secret() -> str:
    s = os.environ.get("MAC_MINI_INTAKE_SECRET", "").strip()
    if not s:
        raise RuntimeError("MAC_MINI_INTAKE_SECRET environment variable is not set")
    return s


def _validate_bundle(bundle: dict) -> tuple[str, str]:
    """Return (skill_md, title) or raise ValueError."""
    skill_md = bundle.get("skill_md", "")
    if not isinstance(skill_md, str):
        raise ValueError("skill_md must be a string")
    skill_md_bytes = skill_md.encode("utf-8")
    if len(skill_md_bytes) > SKILL_MD_MAX_BYTES:
        raise ValueError(f"skill_md exceeds {SKILL_MD_MAX_BYTES} bytes")
    if len(skill_md.strip()) < SKILL_MIN_CHARS:
        raise ValueError(f"skill_md must contain at least {SKILL_MIN_CHARS} characters")
    if "\x00" in skill_md:
        raise ValueError("skill_md must not contain NUL bytes")

    title = bundle.get("title", "")
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    title = title.strip()
    if not TITLE_MIN <= len(title) <= TITLE_MAX:
        raise ValueError(f"title must be {TITLE_MIN}–{TITLE_MAX} characters")
    if any(c in title for c in "\r\n\t"):
        raise ValueError("title must be a single line")

    if not bundle.get("rights_confirmed"):
        raise ValueError("rights_confirmed must be true")
    if not bundle.get("boundary_confirmed"):
        raise ValueError("boundary_confirmed must be true")

    return skill_md, title


def _write_inbox(bundle: dict, skill_md: str, title: str) -> str:
    submission_id = str(uuid.uuid4())
    submission_dir = INBOX_DIR / submission_id
    tmp_dir = INBOX_DIR.parent / f".tmp-{submission_id}"

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        (tmp_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        sha256 = hashlib.sha256(skill_md.encode("utf-8")).hexdigest()
        meta = {
            "submission_id": submission_id,
            "sha256": sha256,
            "title": title,
            "public_name": str(bundle.get("public_name", ""))[:PUBLIC_FIELD_MAX],
            "public_contact": str(bundle.get("public_contact", ""))[:PUBLIC_FIELD_MAX],
            "rights_confirmed": bool(bundle.get("rights_confirmed")),
            "boundary_confirmed": bool(bundle.get("boundary_confirmed")),
            "submitted_at": str(bundle.get("submitted_at", "")),
        }
        (tmp_dir / "submission.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        tmp_dir.rename(submission_dir)
    except Exception:
        if tmp_dir.exists():
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    log.info("Queued: %s (title: %s)", submission_id, title)
    return submission_id


class IntakeHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        log.info(fmt, *args)

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/intake":
            self._send_json(404, {"error": "not found"})
            return

        # Authenticate
        auth = self.headers.get("Authorization", "")
        try:
            secret = _secret()
        except RuntimeError as exc:
            log.error("Server misconfiguration: %s", exc)
            self._send_json(503, {"error": "server misconfiguration"})
            return
        if auth != f"Bearer {secret}":
            log.warning("Rejected request: bad Authorization header from %s", self.client_address[0])
            self._send_json(401, {"error": "unauthorized"})
            return

        # Read body
        length = int(self.headers.get("Content-Length", "0"))
        if length > SKILL_MD_MAX_BYTES + 4096:
            self._send_json(413, {"error": "request body too large"})
            return
        raw = self.rfile.read(length)

        # Parse
        try:
            bundle = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"invalid JSON: {exc}"})
            return

        # Validate
        try:
            skill_md, title = _validate_bundle(bundle)
        except ValueError as exc:
            self._send_json(422, {"error": str(exc)})
            return

        # Write
        try:
            submission_id = _write_inbox(bundle, skill_md, title)
        except Exception as exc:
            log.error("Failed to write inbox: %s", exc)
            self._send_json(500, {"error": "intake write failed"})
            return

        self._send_json(200, {"submission_id": submission_id})


def main() -> int:
    try:
        _secret()
    except RuntimeError as exc:
        log.error("%s", exc)
        return 2

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_ATTENTION_DIR.mkdir(parents=True, exist_ok=True)

    server = http.server.HTTPServer(("127.0.0.1", PORT), IntakeHandler)
    log.info("Intake server listening on 127.0.0.1:%d", PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
