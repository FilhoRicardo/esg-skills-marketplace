#!/usr/bin/env python3
"""Normalize a reviewed inbox submission and push a review branch to GitHub.

Reads a reviewed submission from var/intake/inbox/<id>/ (must have review.json),
adds canonical frontmatter and marketplace metadata, rebuilds the catalogue,
verifies the diff is exactly the four allowed paths, commits, and pushes a
submission-reviewed/<slug>-<id> branch using an SSH deploy key.

Required environment variables:
  ESG_DEPLOY_KEY_PATH   - path to the repository SSH deploy key (ed25519 preferred)
                           e.g. /Users/ricardofilho/.ssh/esg-marketplace-deploy

Optional:
  ESG_INTAKE_ROOT       - repository root (defaults to script's parent)
  ESG_GITHUB_REPO       - full repo name, e.g. FilhoRicardo/esg-skills-marketplace
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(os.environ.get("ESG_INTAKE_ROOT", Path(__file__).resolve().parents[1]))
INBOX_DIR = ROOT / "var" / "intake" / "inbox"
PROCESSED_DIR = ROOT / "var" / "intake" / "processed"
NEEDS_ATTENTION_DIR = ROOT / "var" / "intake" / "needs-attention"
SKILLS_DIR = ROOT / "skills"
DOWNLOADS_DIR = ROOT / "site" / "downloads"
CATALOG_PATH = ROOT / "site" / "catalog.json"
SUBMISSION_CONFIG_PATH = ROOT / "site" / "submission-config.json"

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import ALLOWED_CATEGORIES, PolicyError, SLUG_RE

GITHUB_REPO = os.environ.get(
    "ESG_GITHUB_REPO", "FilhoRicardo/esg-skills-marketplace"
)

# Exactly these four paths (relative to repo root) may differ from main.
ALLOWED_DIFF_PATHS: set[str] = set()  # populated per-submission

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s submission-publisher %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def _find_next_reviewed() -> Path | None:
    if not INBOX_DIR.exists():
        return None
    for candidate in sorted(INBOX_DIR.iterdir()):
        if not candidate.is_dir():
            continue
        if (
            (candidate / "SKILL.md").exists()
            and (candidate / "submission.json").exists()
            and (candidate / "review.json").exists()
            and not (candidate / "published").exists()
        ):
            return candidate
    return None


def _assert_sha256(path: Path, expected_hex: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_hex:
        raise ValueError(
            f"SHA-256 mismatch on {path.name}: expected {expected_hex}, got {actual}"
        )


def _build_skill_md(slug: str, description: str, body: str) -> str:
    description_escaped = description.replace('"', '\\"')
    frontmatter = f'---\nname: {slug}\ndescription: "{description_escaped}"\n---\n'
    return frontmatter + body.lstrip("\n") + "\n"


def _build_zip_deterministic(skill_dir: Path, archive_path: Path) -> None:
    # Fixed mtime: 2024-01-01 00:00:00 UTC — ensures byte-stable archives
    FIXED_DATE = (2024, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            arcname = f"{skill_dir.name}/{file_path.relative_to(skill_dir).as_posix()}"
            info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, file_path.read_bytes())


def _run_git(args: list[str], *, cwd: Path, env: dict | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args[:3])} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _changed_paths_vs_main(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "main"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    return [p for p in result.stdout.splitlines() if p]


def _push_branch(branch: str, deploy_key_path: str, repo: Path) -> None:
    ssh_command = (
        f"ssh -i {deploy_key_path} "
        "-o StrictHostKeyChecking=accept-new "
        "-o BatchMode=yes"
    )
    env = {"GIT_SSH_COMMAND": ssh_command}
    remote_url = f"git@github.com:{GITHUB_REPO}.git"
    _run_git(
        ["push", remote_url, f"{branch}:{branch}", "--force-with-lease"],
        cwd=repo,
        env=env,
    )


def _move_to_needs_attention(submission_dir: Path, reason: str) -> None:
    dest = NEEDS_ATTENTION_DIR / submission_dir.name
    NEEDS_ATTENTION_DIR.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    submission_dir.rename(dest)
    (dest / "publish-error.txt").write_text(reason + "\n", encoding="utf-8")
    log.error("Needs attention: %s — %s", submission_dir.name, reason)


def publish_submission(submission_dir: Path) -> bool:
    deploy_key_path = os.environ.get("ESG_DEPLOY_KEY_PATH", "").strip()
    if not deploy_key_path or not Path(deploy_key_path).is_file():
        raise RuntimeError(
            f"ESG_DEPLOY_KEY_PATH is not set or file not found: {deploy_key_path!r}"
        )

    submission_id = submission_dir.name
    submission_meta = json.loads((submission_dir / "submission.json").read_text(encoding="utf-8"))
    review = json.loads((submission_dir / "review.json").read_text(encoding="utf-8"))

    # Re-validate the source SHA-256 against the local SKILL.md bytes
    skill_md_bytes = (submission_dir / "SKILL.md").read_bytes()
    original_sha256 = hashlib.sha256(skill_md_bytes).hexdigest()
    recorded_sha256 = review.get("source_sha256", "")
    if recorded_sha256 and original_sha256 != recorded_sha256.removeprefix("sha256:"):
        _move_to_needs_attention(
            submission_dir,
            f"SHA-256 mismatch after review: recorded={recorded_sha256} actual={original_sha256}",
        )
        return False

    # Re-validate review output (double-check before writing)
    description = review.get("description", "")
    category = review.get("category", "")
    if not (20 <= len(description) <= 300):
        _move_to_needs_attention(
            submission_dir, f"Review description length invalid: {len(description)}"
        )
        return False
    for ch in description:
        if ch not in "\t" and unicodedata.category(ch) in {"Cc", "Cf"}:
            _move_to_needs_attention(
                submission_dir, "Review description contains control characters"
            )
            return False
    if category not in ALLOWED_CATEGORIES:
        _move_to_needs_attention(
            submission_dir, f"Review category {category!r} not in allowed set"
        )
        return False

    # Derive slug from title
    title = submission_meta.get("title", "")
    if not title:
        _move_to_needs_attention(submission_dir, "submission.json missing title")
        return False
    ascii_title = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
    if not SLUG_RE.fullmatch(slug):
        _move_to_needs_attention(
            submission_dir, f"Title {title!r} cannot be slugified to a valid slug"
        )
        return False

    if (SKILLS_DIR / slug).exists():
        _move_to_needs_attention(
            submission_dir, f"skills/{slug} already exists in repository"
        )
        return False

    branch_name = f"submission-reviewed/{slug}-{submission_id[:8]}"
    log.info("Publishing: %s → branch %s", submission_id, branch_name)

    # Ensure we start from a clean main
    try:
        _run_git(["fetch", "origin", "main"], cwd=ROOT)
        _run_git(["checkout", "main"], cwd=ROOT)
        _run_git(["reset", "--hard", "origin/main"], cwd=ROOT)
        _run_git(["checkout", "-b", branch_name], cwd=ROOT)
    except RuntimeError as exc:
        _move_to_needs_attention(submission_dir, f"git setup failed: {exc}")
        return False

    skill_dir = SKILLS_DIR / slug
    try:
        # 1. Create skill directory with normalized SKILL.md
        skill_dir.mkdir(parents=True, exist_ok=False)
        skill_md_body = skill_md_bytes.decode("utf-8")
        # Remove any existing frontmatter from submitted text (strip before adding ours)
        if skill_md_body.startswith("---\n"):
            try:
                closing = skill_md_body.index("\n---\n", 4)
                skill_md_body = skill_md_body[closing + 5:]
            except ValueError:
                pass
        normalized_md = _build_skill_md(slug, description, skill_md_body)
        (skill_dir / "SKILL.md").write_text(normalized_md, encoding="utf-8")

        # 2. Write marketplace.json
        marketplace = {"title": title, "category": category}
        (skill_dir / "marketplace.json").write_text(
            json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # 3. Rebuild catalogue and submission config
        build_result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "build_catalog.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if build_result.returncode != 0:
            raise RuntimeError(f"build_catalog.py failed: {build_result.stderr.strip()}")

        # 4. Verify exactly the expected 4 paths changed vs main
        expected_paths = {
            f"skills/{slug}/SKILL.md",
            f"skills/{slug}/marketplace.json",
            "site/catalog.json",
            f"site/downloads/{slug}.zip",
        }
        changed = set(_changed_paths_vs_main(ROOT))
        # Also include untracked new files
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT, capture_output=True, text=True,
        )
        for line in status_result.stdout.splitlines():
            if line[:2].strip() in ("?", "A", "M"):
                path = line[3:].strip()
                if path:
                    changed.add(path)

        unexpected = changed - expected_paths
        if unexpected:
            raise RuntimeError(
                f"Unexpected changed paths: {sorted(unexpected)}. "
                "Expected exactly: " + str(sorted(expected_paths))
            )
        missing = expected_paths - changed
        if missing:
            raise RuntimeError(f"Expected changed paths not found: {sorted(missing)}")

        # 5. Commit
        sha256_line = f"source-sha256: {original_sha256}"
        commit_message = (
            f"Add reviewed skill: {slug}\n\n"
            f"title: {title}\n"
            f"category: {category}\n"
            f"submission-id: {submission_id}\n"
            f"{sha256_line}\n"
            f"linear: https://linear.app/rf-ai-workspace/issue/RF-100"
        )
        _run_git(["add", f"skills/{slug}", "site/catalog.json", "site/submission-config.json",
                  "site/downloads/"], cwd=ROOT)
        _run_git(
            [
                "commit",
                "-m", commit_message,
                "--author", "ESG Marketplace Intake <actions@users.noreply.github.com>",
            ],
            cwd=ROOT,
        )

        # 6. Push via deploy key
        _push_branch(branch_name, deploy_key_path, ROOT)
        log.info("Pushed branch: %s", branch_name)

    except Exception as exc:
        # Restore main on failure
        try:
            _run_git(["checkout", "main"], cwd=ROOT)
            _run_git(["branch", "-D", branch_name], cwd=ROOT)
        except Exception:
            pass
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        _move_to_needs_attention(submission_dir, f"publish failed: {exc}")
        return False

    # Mark locally processed
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed_dest = PROCESSED_DIR / submission_id
    submission_dir.rename(processed_dest)
    (processed_dest / "published").write_text(branch_name + "\n", encoding="utf-8")
    log.info("Processed: %s", submission_id)

    # Return to main
    try:
        _run_git(["checkout", "main"], cwd=ROOT)
    except Exception as exc:
        log.warning("Could not return to main after publish: %s", exc)

    return True


def main() -> int:
    submission_dir = _find_next_reviewed()
    if submission_dir is None:
        log.debug("No reviewed submissions ready to publish")
        return 0

    try:
        ok = publish_submission(submission_dir)
        return 0 if ok else 1
    except RuntimeError as exc:
        log.error("Publisher error: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
