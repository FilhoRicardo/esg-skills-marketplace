#!/usr/bin/env python3
"""Validate and materialize site-native skill submissions."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import PolicyError, ROOT, SLUG_RE

SITE_INTAKE_SKILL_MD_MAX_BYTES = 40_000
SITE_INTAKE_MARKETPLACE_MAX_BYTES = 4_000
SITE_INTAKE_MAX_PUBLIC_NAME_CHARS = 80
SITE_INTAKE_MAX_PUBLIC_CONTACT_CHARS = 200
SITE_INTAKE_MIN_SKILL_CHARS = 80


def submission_config() -> dict[str, object]:
    return {
        "stageUploadPath": "/api/intake/stage",
        "finalizeUploadPath": "/api/intake/finalize",
        "maxSkillFileBytes": SITE_INTAKE_SKILL_MD_MAX_BYTES,
        "maxMarketplaceFileBytes": SITE_INTAKE_MARKETPLACE_MAX_BYTES,
        "maxPublicNameChars": SITE_INTAKE_MAX_PUBLIC_NAME_CHARS,
        "maxPublicContactChars": SITE_INTAKE_MAX_PUBLIC_CONTACT_CHARS,
        "minTitleChars": 4,
        "maxTitleChars": 80,
        "minSkillChars": SITE_INTAKE_MIN_SKILL_CHARS,
    }


def _bounded_text(text: str, label: str, maximum_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) > maximum_bytes:
        raise PolicyError(f"{label} exceeds the site intake limit of {maximum_bytes} bytes")
    return text


def _normalize_public_field(value: str, label: str, maximum_chars: int) -> str:
    compact = " ".join(value.split()).strip()
    if len(compact) > maximum_chars:
        raise PolicyError(f"{label} must be {maximum_chars} characters or fewer")
    return compact


def _validate_skill_markdown(text: str) -> None:
    if len(text.strip()) < SITE_INTAKE_MIN_SKILL_CHARS:
        raise PolicyError(
            f"skill instructions must contain at least {SITE_INTAKE_MIN_SKILL_CHARS} characters"
        )
    if "\x00" in text:
        raise PolicyError("skill instructions must not contain NUL bytes")
    for character in text:
        if character not in "\n\r\t" and unicodedata.category(character) in {"Cc", "Cf"}:
            raise PolicyError(
                "skill instructions contain unsupported invisible Unicode control characters"
            )


def _parse_title(marketplace_json: str) -> str:
    try:
        marketplace = json.loads(marketplace_json)
    except json.JSONDecodeError as exc:
        raise PolicyError(f"submission metadata is invalid JSON: {exc.msg}") from exc
    if not isinstance(marketplace, dict) or set(marketplace) != {"title"}:
        raise PolicyError("site intake metadata may only contain title")
    title = marketplace.get("title")
    if not isinstance(title, str) or not 4 <= len(title.strip()) <= 80:
        raise PolicyError("public title must contain 4 to 80 characters")
    if any(character in title for character in "\r\n\t"):
        raise PolicyError("public title must be a single line of plain text")
    return title.strip()


def _slugify_title(title: str) -> str:
    ascii_title = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
    if not SLUG_RE.fullmatch(slug):
        raise PolicyError("public title must include letters or numbers that can form a URL slug")
    return slug


def validate_submission(
    skill_md: str,
    marketplace_json: str,
    *,
    root: Path = ROOT,
    rights_confirmed: bool,
    boundary_confirmed: bool,
) -> dict[str, str]:
    if not rights_confirmed:
        raise PolicyError("redistribution rights must be confirmed before submission")
    if not boundary_confirmed:
        raise PolicyError("the professional-advice boundary must be confirmed before submission")

    skill_md = _bounded_text(skill_md, "SKILL.md", SITE_INTAKE_SKILL_MD_MAX_BYTES)
    marketplace_json = _bounded_text(
        marketplace_json,
        "marketplace.json",
        SITE_INTAKE_MARKETPLACE_MAX_BYTES,
    )

    _validate_skill_markdown(skill_md)
    title = _parse_title(marketplace_json)
    slug = _slugify_title(title)
    if (root / "skills" / slug).exists():
        raise PolicyError(
            f"skills/{slug} already exists in the approved catalogue; use maintainer review for updates"
        )
    return {
        "slug": slug,
        "title": title,
        "description": "Pending maintainer normalization.",
        "category": "pending-review",
        "path": f"skills/{slug}",
    }


def write_submission(
    *,
    root: Path,
    skill_md: str,
    marketplace_json: str,
    public_name: str,
    public_contact: str,
    rights_confirmed: bool,
    boundary_confirmed: bool,
) -> dict[str, str]:
    entry = validate_submission(
        skill_md,
        marketplace_json,
        root=root,
        rights_confirmed=rights_confirmed,
        boundary_confirmed=boundary_confirmed,
    )
    skill_dir = root / "skills" / entry["slug"]
    skill_dir.mkdir(parents=True, exist_ok=False)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (skill_dir / "marketplace.json").write_text(marketplace_json, encoding="utf-8")
    entry["public_name"] = _normalize_public_field(
        public_name,
        "public submitter name",
        SITE_INTAKE_MAX_PUBLIC_NAME_CHARS,
    )
    entry["public_contact"] = _normalize_public_field(
        public_contact,
        "public contact field",
        SITE_INTAKE_MAX_PUBLIC_CONTACT_CHARS,
    )
    return entry


def _write_metadata(path: Path, payload: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("config", help="Print the public submission configuration as JSON")

    submit_parser = subparsers.add_parser(
        "write-submission",
        help="Read the site intake environment and write a new skill bundle into the repository",
    )
    submit_parser.add_argument("--root", type=Path, default=ROOT)
    submit_parser.add_argument("--metadata-out", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "config":
        print(json.dumps(submission_config(), indent=2, ensure_ascii=False))
        return 0

    if args.command != "write-submission":
        parser.error(f"unknown command: {args.command}")

    try:
        entry = write_submission(
            root=args.root.resolve(),
            skill_md=os.environ["SITE_INTAKE_SKILL_MD"],
            marketplace_json=os.environ["SITE_INTAKE_MARKETPLACE_JSON"],
            public_name=os.environ.get("SITE_INTAKE_PUBLIC_NAME", ""),
            public_contact=os.environ.get("SITE_INTAKE_PUBLIC_CONTACT", ""),
            rights_confirmed=os.environ.get("SITE_INTAKE_RIGHTS_CONFIRMED") == "true",
            boundary_confirmed=os.environ.get("SITE_INTAKE_BOUNDARY_CONFIRMED") == "true",
        )
    except KeyError as exc:
        print(f"INTAKE FAILURE: missing environment variable {exc.args[0]}", file=sys.stderr)
        return 2
    except PolicyError as exc:
        print(f"INTAKE FAILURE: {exc}", file=sys.stderr)
        return 1

    _write_metadata(args.metadata_out, entry)
    print(json.dumps(entry, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
