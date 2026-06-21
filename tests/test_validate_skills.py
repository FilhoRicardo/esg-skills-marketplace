from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_skills import PolicyError, expected_catalog, validate_catalog, validate_skill


class SkillPolicyTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "skills").mkdir()
        (root / "site").mkdir()
        return root

    def add_skill(self, root: Path, slug: str = "materiality-brief") -> Path:
        skill = root / "skills" / slug
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\n"
            f"name: {slug}\n"
            "description: Prepare a concise ESG materiality briefing from user-provided evidence.\n"
            "---\n\n"
            "# Materiality brief\n\n"
            "Review the supplied evidence, separate facts from assumptions, and produce a bounded briefing with sources and explicit uncertainties.\n",
            encoding="utf-8",
        )
        (skill / "marketplace.json").write_text(
            json.dumps({"title": "Materiality brief", "category": "strategy"}),
            encoding="utf-8",
        )
        return skill

    def test_valid_text_only_skill(self) -> None:
        root = self.make_root()
        skill = self.add_skill(root)
        entry = validate_skill(skill)
        self.assertEqual(entry["slug"], "materiality-brief")
        self.assertEqual(entry["category"], "strategy")

    def test_executable_file_is_rejected(self) -> None:
        root = self.make_root()
        skill = self.add_skill(root)
        extra = skill / "notes.txt"
        extra.write_text("review notes", encoding="utf-8")
        extra.chmod(extra.stat().st_mode | 0o111)
        with self.assertRaisesRegex(PolicyError, "executable"):
            validate_skill(skill)

    def test_dependency_manifest_is_rejected(self) -> None:
        root = self.make_root()
        skill = self.add_skill(root)
        (skill / "requirements.txt").write_text("requests\n", encoding="utf-8")
        with self.assertRaisesRegex(PolicyError, "dependency"):
            validate_skill(skill)

    def test_binary_extension_is_rejected(self) -> None:
        root = self.make_root()
        skill = self.add_skill(root)
        (skill / "payload.py").write_text("print('no')\n", encoding="utf-8")
        with self.assertRaisesRegex(PolicyError, "file type"):
            validate_skill(skill)

    def test_invisible_unicode_control_is_rejected(self) -> None:
        root = self.make_root()
        skill = self.add_skill(root)
        with (skill / "notes.txt").open("w", encoding="utf-8") as handle:
            handle.write("visible\u202etext")
        with self.assertRaisesRegex(PolicyError, "Unicode control"):
            validate_skill(skill)

    def test_catalogue_must_match_validated_skills(self) -> None:
        root = self.make_root()
        self.add_skill(root)
        (root / "site" / "catalog.json").write_text(
            json.dumps(expected_catalog(root)), encoding="utf-8"
        )
        validate_catalog(root)
        (root / "site" / "catalog.json").write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(PolicyError, "stale"):
            validate_catalog(root)


if __name__ == "__main__":
    unittest.main()
