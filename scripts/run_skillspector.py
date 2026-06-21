#!/usr/bin/env python3
"""Run pinned SkillSpector against changed skills and enforce a SAFE result."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import ROOT, skill_directories


def changed_skill_directories(base: str, root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", f"{base}...HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    slugs = {
        parts[1]
        for line in result.stdout.splitlines()
        if len(parts := Path(line).parts) >= 3 and parts[0] == "skills"
    }
    return [root / "skills" / slug for slug in sorted(slugs) if (root / "skills" / slug).is_dir()]


def scan(skill_dir: Path, reports_dir: Path, root: Path = ROOT) -> tuple[bool, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{skill_dir.name}.json"
    command = [
        "skillspector",
        "scan",
        str(skill_dir),
        "--no-llm",
        "--format",
        "json",
        "--output",
        str(report_path),
    ]
    result = subprocess.run(command, cwd=root, text=True)
    if result.returncode not in {0, 1}:
        return False, f"{skill_dir.name}: scanner failed with exit code {result.returncode}"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assessment = report["risk_assessment"]
        recommendation = assessment["recommendation"]
        score = assessment["score"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return False, f"{skill_dir.name}: invalid SkillSpector report: {exc}"
    if recommendation != "SAFE":
        return False, f"{skill_dir.name}: blocked by SkillSpector ({recommendation}, score {score}/100)"
    return True, f"{skill_dir.name}: SAFE ({score}/100)"


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--base", help="Scan skill folders changed since this commit")
    selection.add_argument("--all", action="store_true", help="Scan every approved skill")
    parser.add_argument("--reports", default="artifacts/skillspector")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        targets = skill_directories(root) if args.all else changed_skill_directories(args.base, root)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr)
        return 2
    if not targets:
        print("No skill changes require a SkillSpector scan.")
        return 0

    reports_dir = root / args.reports
    reports_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for target in targets:
        passed, message = scan(target, reports_dir, root)
        print(message)
        failures += int(not passed)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
