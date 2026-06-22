#!/usr/bin/env python3
"""Validate text-only skill bundles and the generated catalogue."""

from __future__ import annotations

import argparse
import json
import re
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG_PATH = ROOT / "site" / "catalog.json"

ALLOWED_EXTENSIONS = {".csv", ".json", ".md", ".txt", ".yaml", ".yml"}
ALLOWED_CATEGORIES = {"data", "disclosure", "operations", "reporting", "risk", "strategy"}
FORBIDDEN_FILENAMES = {
    "dockerfile",
    "makefile",
    "package-lock.json",
    "package.json",
    "pipfile",
    "poetry.lock",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "yarn.lock",
}
MAX_FILE_BYTES = 100_000
MAX_SKILL_BYTES = 500_000
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PolicyError(ValueError):
    """A skill violates the marketplace intake policy."""


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise PolicyError(f"{path}: SKILL.md must start with YAML frontmatter")

    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise PolicyError(f"{path}: frontmatter is missing its closing ---") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            raise PolicyError(f"{path}: frontmatter must use simple top-level key: value pairs")
        key, value = line.split(":", 1)
        key = key.strip()
        value = _unquote(value.strip())
        if not key or not value:
            raise PolicyError(f"{path}: frontmatter keys and values cannot be empty")
        if key in metadata:
            raise PolicyError(f"{path}: duplicate frontmatter key {key!r}")
        metadata[key] = value

    body = "\n".join(lines[closing + 1 :]).strip()
    return metadata, body


def skill_directories(root: Path = ROOT) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    return sorted(path for path in skills_dir.iterdir() if path.is_dir())


def validate_git_modes(root: Path = ROOT) -> None:
    if not (root / ".git").exists():
        return
    result = subprocess.run(
        ["git", "ls-files", "-s", "--", "skills"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        mode, _object_id, _stage_and_path = line.split(maxsplit=2)
        if mode != "100644":
            raise PolicyError(
                f"skills/: tracked mode {mode} is not allowed; use regular non-executable files only"
            )


def validate_skill(
    skill_dir: Path,
    *,
    allow_pending_category: bool = False,
) -> dict[str, str]:
    slug = skill_dir.name
    if not SLUG_RE.fullmatch(slug):
        raise PolicyError(f"{skill_dir}: folder name must be a lowercase hyphenated slug")
    if skill_dir.is_symlink():
        raise PolicyError(f"{skill_dir}: symlinked skill folders are not allowed")

    skill_file = skill_dir / "SKILL.md"
    marketplace_file = skill_dir / "marketplace.json"
    if not skill_file.is_file():
        raise PolicyError(f"{skill_dir}: missing SKILL.md")
    if not marketplace_file.is_file():
        raise PolicyError(f"{skill_dir}: missing marketplace.json")

    total_size = 0
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if any(part.startswith(".") for part in relative.parts):
            raise PolicyError(f"{path}: hidden paths are not allowed")
        if path.is_symlink():
            raise PolicyError(f"{path}: symlinks are not allowed")
        if path.is_dir():
            continue
        if not path.is_file():
            raise PolicyError(f"{path}: only regular text files are allowed")
        if path.name.lower() in FORBIDDEN_FILENAMES:
            raise PolicyError(f"{path}: dependency and build manifests are not allowed in v1")
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise PolicyError(f"{path}: file type {path.suffix or '(none)'} is not allowed")
        if path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            raise PolicyError(f"{path}: executable file mode is not allowed")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise PolicyError(f"{path}: file exceeds {MAX_FILE_BYTES} bytes")
        total_size += size
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise PolicyError(f"{path}: files must be valid UTF-8 text") from exc
        if "\x00" in content:
            raise PolicyError(f"{path}: NUL bytes are not allowed")
        for character in content:
            if character not in "\n\r\t" and unicodedata.category(character) in {"Cc", "Cf"}:
                raise PolicyError(f"{path}: invisible Unicode control characters are not allowed")

    if total_size > MAX_SKILL_BYTES:
        raise PolicyError(f"{skill_dir}: bundle exceeds {MAX_SKILL_BYTES} bytes")

    metadata, body = parse_frontmatter(skill_file)
    if metadata.get("name") != slug:
        raise PolicyError(f"{skill_file}: frontmatter name must equal folder slug {slug!r}")
    description = metadata.get("description", "")
    if not 20 <= len(description) <= 300:
        raise PolicyError(f"{skill_file}: description must contain 20 to 300 characters")
    if len(body) < 80:
        raise PolicyError(f"{skill_file}: skill body is too short for a meaningful review")

    try:
        marketplace = json.loads(marketplace_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyError(f"{marketplace_file}: invalid JSON: {exc.msg}") from exc
    if not isinstance(marketplace, dict):
        raise PolicyError(f"{marketplace_file}: expected a JSON object")
    marketplace_keys = set(marketplace)
    if allow_pending_category:
        if marketplace_keys != {"title"}:
            raise PolicyError(
                f"{marketplace_file}: site intake metadata may only contain title"
            )
        pending_category = True
    else:
        pending_category = False
    if not allow_pending_category and marketplace_keys != {"title", "category"}:
        raise PolicyError(f"{marketplace_file}: only title and category are allowed")
    title = marketplace.get("title")
    category = marketplace.get("category")
    if not isinstance(title, str) or not 4 <= len(title.strip()) <= 80:
        raise PolicyError(f"{marketplace_file}: title must contain 4 to 80 characters")
    if any(character in title for character in "\r\n\t"):
        raise PolicyError(f"{marketplace_file}: title must be a single line of plain text")
    if not pending_category and category not in ALLOWED_CATEGORIES:
        raise PolicyError(f"{marketplace_file}: category must be one of {sorted(ALLOWED_CATEGORIES)}")

    return {
        "slug": slug,
        "title": title.strip(),
        "description": description,
        "category": "pending-review" if pending_category else category,
        "path": f"skills/{slug}",
    }


def expected_catalog(root: Path = ROOT) -> list[dict[str, str]]:
    return [validate_skill(path) for path in skill_directories(root)]


def validate_catalog(root: Path = ROOT) -> None:
    catalog_path = root / "site" / "catalog.json"
    if not catalog_path.is_file():
        raise PolicyError(f"{catalog_path}: generated catalogue is missing")
    try:
        actual = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyError(f"{catalog_path}: invalid JSON: {exc.msg}") from exc
    expected = expected_catalog(root)
    if actual != expected:
        raise PolicyError(
            f"{catalog_path}: catalogue is stale; run python3 scripts/build_catalog.py"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Validate every approved skill")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()
    if not args.all:
        parser.error("--all is required")
    root = args.root.resolve()
    try:
        validate_git_modes(root)
        validate_catalog(root)
    except (OSError, PolicyError, subprocess.CalledProcessError) as exc:
        print(f"POLICY FAILURE: {exc}", file=sys.stderr)
        return 1
    print(f"Policy validation passed for {len(skill_directories(root))} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
