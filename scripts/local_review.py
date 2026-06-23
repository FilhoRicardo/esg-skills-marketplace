#!/usr/bin/env python3
"""Run an isolated Codex review of a skill submission from the local inbox.

Processes ONE submission directory at a time. Called by the launchd reviewer
watcher when inbox becomes non-empty.

Required environment variables:
  CODEX_API_KEY   - dedicated OpenAI API key with a low project spend limit

Optional:
  ESG_INTAKE_ROOT - repository root (defaults to script's parent)
  CODEX_PATH      - path to the codex binary (defaults to 'codex' on PATH)
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(os.environ.get("ESG_INTAKE_ROOT", Path(__file__).resolve().parents[1]))
INBOX_DIR = ROOT / "var" / "intake" / "inbox"
PROCESSED_DIR = ROOT / "var" / "intake" / "processed"
NEEDS_ATTENTION_DIR = ROOT / "var" / "intake" / "needs-attention"
SCHEMA_PATH = ROOT / "config" / "codex-review-schema.json"

ALLOWED_CATEGORIES = frozenset(
    ["data", "disclosure", "operations", "reporting", "risk", "strategy"]
)
ALLOWED_RISK_FLAGS = frozenset(
    [
        "contains-external-urls",
        "references-third-party-tools",
        "includes-financial-guidance",
        "includes-legal-guidance",
        "includes-credentials-placeholder",
    ]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s local-review %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

_REVIEW_PROMPT = """\
You are reviewing a submitted skill for the ESG Skills Marketplace.

Read the SKILL.md content below and output ONLY a single JSON object.

RULES:
- description: one line, 20-300 characters, plain ASCII or NFC Unicode, no control or format characters
- category: exactly one of: data, disclosure, operations, reporting, risk, strategy
- risk_flags: array of zero or more strings from this fixed set only:
    contains-external-urls
    references-third-party-tools
    includes-financial-guidance
    includes-legal-guidance
    includes-credentials-placeholder

OUTPUT FORMAT (output ONLY this JSON, nothing else, no markdown fences):
{"description":"...","category":"...","risk_flags":[...]}

SKILL.md content follows:
---
"""


def _find_next_submission() -> Path | None:
    if not INBOX_DIR.exists():
        return None
    for candidate in sorted(INBOX_DIR.iterdir()):
        if not candidate.is_dir():
            continue
        if (candidate / "review.json").exists():
            continue
        if (candidate / "SKILL.md").exists() and (candidate / "submission.json").exists():
            return candidate
    return None


def _validate_review_output(raw: str) -> dict:
    # Strip any accidental markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw, count=1)
        raw = re.sub(r"\n?```$", "", raw)
    raw = raw.strip()

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Codex output is not valid JSON: {exc}") from exc

    if not isinstance(obj, dict):
        raise ValueError("Codex output must be a JSON object")
    if set(obj.keys()) != {"description", "category", "risk_flags"}:
        raise ValueError(f"Codex output has unexpected keys: {sorted(obj.keys())}")

    description = obj.get("description", "")
    if not isinstance(description, str):
        raise ValueError("description must be a string")
    description = unicodedata.normalize("NFC", description)
    if not 20 <= len(description) <= 300:
        raise ValueError(f"description length {len(description)} is not in [20, 300]")
    for ch in description:
        if ch not in "\t" and unicodedata.category(ch) in {"Cc", "Cf"}:
            raise ValueError("description contains disallowed Unicode control/format characters")
    obj["description"] = description

    category = obj.get("category", "")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"category {category!r} is not in allowed set")

    risk_flags = obj.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        raise ValueError("risk_flags must be an array")
    for flag in risk_flags:
        if flag not in ALLOWED_RISK_FLAGS:
            raise ValueError(f"risk flag {flag!r} is not in allowed set")
    obj["risk_flags"] = list(dict.fromkeys(risk_flags))  # deduplicate, preserve order

    return obj


def _build_codex_config(config_dir: Path) -> None:
    # deny-all PreToolUse hook: Codex cannot execute tools
    config = {
        "model": "gpt-5.4-mini",
        "approvalMode": "full-auto",
        "disableWebSearch": True,
        "disableMcp": True,
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": ".*",
                    "hooks": [{"type": "command", "command": "exit 2"}],
                }
            ]
        },
    }
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")


def _run_codex(skill_md: str, api_key: str) -> str:
    codex_bin = os.environ.get("CODEX_PATH", "codex")

    with tempfile.TemporaryDirectory(prefix="esg-review-") as tmpdir:
        tmp_path = Path(tmpdir)
        codex_home = tmp_path / ".codex"
        codex_home.mkdir()
        _build_codex_config(codex_home)

        prompt = _REVIEW_PROMPT + skill_md

        env = {
            "HOME": tmpdir,
            "CODEX_HOME": str(codex_home),
            "OPENAI_API_KEY": api_key,
            # Exclude all Mac credential stores, plugins, and user config
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        }

        try:
            result = subprocess.run(
                [
                    codex_bin,
                    "exec",
                    "--approval-mode",
                    "full-auto",
                    "--sandbox-type",
                    "read-only",
                    "--no-web-search",
                    prompt,
                ],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
                timeout=120,
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"Codex binary not found at {codex_bin!r}. "
                "Set CODEX_PATH or install Codex CLI."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Codex review timed out after 120 seconds")

        if result.returncode != 0:
            stderr_snippet = result.stderr[:500] if result.stderr else "(no stderr)"
            raise RuntimeError(
                f"Codex exited with code {result.returncode}: {stderr_snippet}"
            )

        return result.stdout.strip()


def _move_to_needs_attention(submission_dir: Path, reason: str) -> None:
    dest = NEEDS_ATTENTION_DIR / submission_dir.name
    NEEDS_ATTENTION_DIR.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        import shutil
        shutil.rmtree(dest)
    submission_dir.rename(dest)
    (dest / "review-error.txt").write_text(reason + "\n", encoding="utf-8")
    log.error("Needs attention: %s — %s", submission_dir.name, reason)


def review_submission(submission_dir: Path) -> bool:
    api_key = os.environ.get("CODEX_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("CODEX_API_KEY environment variable is not set")

    submission_id = submission_dir.name
    skill_md_path = submission_dir / "SKILL.md"
    submission_json_path = submission_dir / "submission.json"

    skill_md = skill_md_path.read_text(encoding="utf-8")
    submission_meta = json.loads(submission_json_path.read_text(encoding="utf-8"))

    log.info("Reviewing: %s (title: %s)", submission_id, submission_meta.get("title", ""))

    try:
        raw_output = _run_codex(skill_md, api_key)
    except RuntimeError as exc:
        _move_to_needs_attention(submission_dir, f"Codex runner error: {exc}")
        return False

    try:
        review = _validate_review_output(raw_output)
    except ValueError as exc:
        _move_to_needs_attention(
            submission_dir,
            f"Codex output failed validation: {exc}\nRaw output:\n{raw_output[:500]}",
        )
        return False

    review["submission_id"] = submission_id
    review["source_sha256"] = submission_meta.get("sha256", "")
    (submission_dir / "review.json").write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    log.info(
        "Review complete: %s → category=%s risk_flags=%s",
        submission_id,
        review["category"],
        review["risk_flags"],
    )
    return True


def main() -> int:
    submission_dir = _find_next_submission()
    if submission_dir is None:
        log.debug("No pending submissions in inbox")
        return 0

    try:
        ok = review_submission(submission_dir)
        return 0 if ok else 1
    except RuntimeError as exc:
        log.error("Review failed: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
