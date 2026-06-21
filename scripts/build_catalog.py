#!/usr/bin/env python3
"""Build or verify the static catalogue from validated skill metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import ROOT, PolicyError, expected_catalog


def rendered_catalog(root: Path) -> str:
    return json.dumps(expected_catalog(root), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail instead of rewriting stale data")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()
    root = args.root.resolve()
    catalog_path = root / "site" / "catalog.json"
    try:
        rendered = rendered_catalog(root)
    except (OSError, PolicyError) as exc:
        print(f"CATALOGUE FAILURE: {exc}", file=sys.stderr)
        return 1

    if args.check:
        current = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else ""
        if current != rendered:
            print("Catalogue is stale; run python3 scripts/build_catalog.py", file=sys.stderr)
            return 1
        print("Catalogue is current.")
        return 0

    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {catalog_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
