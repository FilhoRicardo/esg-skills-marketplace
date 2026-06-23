#!/usr/bin/env python3
"""Accept a reviewed intake submission and publish it to the catalogue.

Usage:
  python3 scripts/accept_submission.py <uuid> \
      --slug <url-slug> \
      --description "<description>" \
      --category <category>

What it does:
  1. Reads SKILL.md from var/intake/inbox/<uuid>/
  2. Adds YAML frontmatter (name, description)
  3. Creates skills/<slug>/SKILL.md and marketplace.json
  4. Runs build_catalog.py to regenerate catalog.json and ZIPs
  5. Commits to main and pushes to GitHub
  6. Redeploys the here.now site

Required environment (or ~/.herenow/credentials for the site key):
  HERENOW_API_KEY  - here.now owner API key (for site redeploy)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(os.environ.get("ESG_INTAKE_ROOT", Path(__file__).resolve().parents[1]))
INBOX_DIR = ROOT / "var" / "intake" / "inbox"
PUBLISHED_DIR = ROOT / "var" / "intake" / "published"
SKILLS_DIR = ROOT / "skills"

ALLOWED_CATEGORIES = frozenset(
    ["data", "disclosure", "operations", "reporting", "risk", "strategy"]
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s accept-submission %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def _herenow_api_key() -> str:
    key = os.environ.get("HERENOW_API_KEY", "").strip()
    if not key:
        creds = Path.home() / ".herenow" / "credentials"
        if creds.is_file():
            key = creds.read_text(encoding="utf-8").strip()
    return key


def _add_frontmatter(skill_md: str, slug: str, description: str) -> str:
    """Prepend YAML frontmatter to the skill markdown if not already present."""
    if skill_md.startswith("---"):
        return skill_md
    frontmatter = f"---\nname: {slug}\ndescription: {description}\n---\n\n"
    return frontmatter + skill_md.lstrip("\n")


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    log.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {result.stderr[:400] or result.stdout[:400]}"
        )
    return result


def accept(uuid: str, slug: str, description: str, category: str) -> None:
    # Validate inputs
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"slug {slug!r} must be lowercase letters, numbers, and hyphens")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"category {category!r} must be one of {sorted(ALLOWED_CATEGORIES)}")
    description = unicodedata.normalize("NFC", description.strip())
    if not 20 <= len(description) <= 300:
        raise ValueError(f"description must be 20–300 characters (got {len(description)})")

    submission_dir = INBOX_DIR / uuid
    if not submission_dir.is_dir():
        raise FileNotFoundError(f"No submission found at {submission_dir}")

    skill_md_raw = (submission_dir / "SKILL.md").read_text(encoding="utf-8")
    submission_meta = json.loads((submission_dir / "submission.json").read_text(encoding="utf-8"))

    # Check slug is not already taken
    skill_dir = SKILLS_DIR / slug
    if skill_dir.exists():
        raise FileExistsError(
            f"skills/{slug} already exists — choose a different slug or use maintainer edit"
        )

    # Build skill files
    skill_md = _add_frontmatter(skill_md_raw, slug, description)
    marketplace = {"title": submission_meta.get("title", slug), "category": category}

    # Write to skills/
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (skill_dir / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    log.info("Wrote skills/%s/", slug)

    # Rebuild catalogue
    _run([sys.executable, str(ROOT / "scripts" / "build_catalog.py")])
    log.info("Catalogue rebuilt")

    # Commit and push
    _run(["git", "add", f"skills/{slug}", "site/catalog.json", "site/submission-config.json",
          f"site/downloads/{slug}.zip"])
    _run(["git", "commit", "-m", f"Add skill: {slug}\n\nAccepted from intake submission {uuid[:8]}"])
    _run(["git", "push", "origin", "main"])
    log.info("Pushed to GitHub")

    # Move submission to published
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(submission_dir), str(PUBLISHED_DIR / uuid))
    log.info("Moved submission to published/")

    # Redeploy site
    api_key = _herenow_api_key()
    if api_key:
        _run([
            sys.executable, str(ROOT / "scripts" / "publish_site.py"),
            str(ROOT / "site"), "--slug", "royal-bugle-xgg7",
        ], env={**os.environ, "HERENOW_API_KEY": api_key})
        log.info("Site redeployed")
    else:
        log.warning("HERENOW_API_KEY not set — skipping site redeploy")

    log.info("Done: skills/%s is now live", slug)


def main() -> int:
    parser = argparse.ArgumentParser(description="Accept a reviewed intake submission")
    parser.add_argument("uuid", help="Submission UUID from var/intake/inbox/")
    parser.add_argument("--slug", required=True, help="URL slug for the skill")
    parser.add_argument("--description", required=True, help="One-line public description")
    parser.add_argument("--category", required=True, choices=sorted(ALLOWED_CATEGORIES))
    args = parser.parse_args()

    try:
        accept(args.uuid, args.slug, args.description, args.category)
        return 0
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        log.error("%s", exc)
        return 1
    except RuntimeError as exc:
        log.error("Command failed: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
