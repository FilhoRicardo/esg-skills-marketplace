#!/usr/bin/env python3
"""Validate and materialize site-native skill submissions."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import ALLOWED_CATEGORIES, PolicyError, ROOT, SLUG_RE, parse_frontmatter, validate_skill

SITE_INTAKE_SKILL_MD_MAX_BYTES = 40_000
SITE_INTAKE_MARKETPLACE_MAX_BYTES = 4_000
SITE_INTAKE_MAX_PUBLIC_NAME_CHARS = 80
SITE_INTAKE_MAX_PUBLIC_CONTACT_CHARS = 200


def submission_config() -> dict[str, object]:
    return {
        "dispatchPath": "/api/submit-skill",
        "allowedCategories": sorted(ALLOWED_CATEGORIES),
        "maxSkillFileBytes": SITE_INTAKE_SKILL_MD_MAX_BYTES,
        "maxMarketplaceFileBytes": SITE_INTAKE_MARKETPLACE_MAX_BYTES,
        "maxPublicNameChars": SITE_INTAKE_MAX_PUBLIC_NAME_CHARS,
        "maxPublicContactChars": SITE_INTAKE_MAX_PUBLIC_CONTACT_CHARS,
        "minDescriptionChars": 20,
        "maxDescriptionChars": 300,
        "minBodyChars": 80,
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

    with tempfile.TemporaryDirectory() as temporary_name:
        temporary_root = Path(temporary_name)
        seed_file = temporary_root / "seed-SKILL.md"
        seed_file.write_text(skill_md, encoding="utf-8")
        metadata, _body = parse_frontmatter(seed_file)
        proposed_slug = metadata.get("name", "")
        folder_slug = proposed_slug if SLUG_RE.fullmatch(proposed_slug) else "candidate-skill"

        skill_dir = temporary_root / folder_slug
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (skill_dir / "marketplace.json").write_text(marketplace_json, encoding="utf-8")
        entry = validate_skill(skill_dir)

    if (root / "skills" / entry["slug"]).exists():
        raise PolicyError(
            f"skills/{entry['slug']} already exists in the approved catalogue; use maintainer review for updates"
        )
    return entry


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
