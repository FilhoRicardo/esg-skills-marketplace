#!/usr/bin/env python3
"""Build or verify the static catalogue from validated skill metadata."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from site_intake import submission_config
from validate_skills import ROOT, PolicyError, expected_catalog, skill_directories


def rendered_catalog(root: Path) -> str:
    return json.dumps(expected_catalog(root), indent=2, ensure_ascii=False) + "\n"


def rendered_submission_config() -> str:
    return json.dumps(submission_config(), indent=2, ensure_ascii=False) + "\n"


_ZIP_FIXED_DATE = (2024, 1, 1, 0, 0, 0)


def build_download_bundles(root: Path) -> None:
    downloads_dir = root / "site" / "downloads"
    if downloads_dir.exists():
        shutil.rmtree(downloads_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    for skill_dir in skill_directories(root):
        archive_path = downloads_dir / f"{skill_dir.name}.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(skill_dir.rglob("*")):
                if not path.is_file():
                    continue
                arcname = f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}"
                info = zipfile.ZipInfo(arcname, date_time=_ZIP_FIXED_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail instead of rewriting stale data")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()
    root = args.root.resolve()
    catalog_path = root / "site" / "catalog.json"
    submission_config_path = root / "site" / "submission-config.json"
    try:
        rendered = rendered_catalog(root)
        rendered_config = rendered_submission_config()
    except (OSError, PolicyError) as exc:
        print(f"CATALOGUE FAILURE: {exc}", file=sys.stderr)
        return 1

    if args.check:
        current = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else ""
        if current != rendered:
            print("Catalogue is stale; run python3 scripts/build_catalog.py", file=sys.stderr)
            return 1
        current_config = (
            submission_config_path.read_text(encoding="utf-8")
            if submission_config_path.exists()
            else ""
        )
        if current_config != rendered_config:
            print("Submission config is stale; run python3 scripts/build_catalog.py", file=sys.stderr)
            return 1
        print("Catalogue is current.")
        return 0

    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(rendered, encoding="utf-8")
    submission_config_path.write_text(rendered_config, encoding="utf-8")
    build_download_bundles(root)
    print(f"Wrote {catalog_path.relative_to(root)}")
    print(f"Wrote {submission_config_path.relative_to(root)}")
    print("Wrote site/downloads/*.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
