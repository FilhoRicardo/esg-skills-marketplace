#!/usr/bin/env python3
"""Prevent external pull requests from changing the marketplace platform."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath

OWNER = "FilhoRicardo"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def changed_paths(base: str, repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", f"{base}...HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def scope_errors(actor: str, paths: list[str]) -> list[str]:
    if actor.casefold() == OWNER.casefold():
        return []

    errors: list[str] = []
    skill_slugs: set[str] = set()
    for raw_path in paths:
        path = PurePosixPath(raw_path)
        parts = path.parts
        if raw_path == "site/catalog.json":
            continue
        if len(parts) < 3 or parts[0] != "skills":
            errors.append(f"external contributors cannot change platform file: {raw_path}")
            continue
        slug = parts[1]
        if not SLUG_RE.fullmatch(slug):
            errors.append(f"invalid skill folder slug in path: {raw_path}")
            continue
        skill_slugs.add(slug)

    if not skill_slugs:
        errors.append("an external contribution must change one skill folder")
    elif len(skill_slugs) > 1:
        errors.append("submit one skill per pull request")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        errors = scope_errors(args.actor, changed_paths(args.base, args.repo.resolve()))
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"SCOPE FAILURE: {error}", file=sys.stderr)
        return 1
    print("Pull-request scope is allowed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
