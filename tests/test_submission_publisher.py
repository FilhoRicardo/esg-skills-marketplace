"""Tests for scripts/submission_publisher.py — deterministic helpers only.

The full publish pipeline requires git and SSH; those are tested via smoke test.
"""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import submission_publisher


class TestBuildSkillMd(unittest.TestCase):
    def test_adds_frontmatter(self):
        result = submission_publisher._build_skill_md(
            "test-skill",
            "Helps practitioners complete ESG materiality assessments.",
            "# Test Skill\n\nThis is the body.",
        )
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("name: test-skill", result)
        self.assertIn("# Test Skill", result)

    def test_body_preserved_byte_for_byte(self):
        body = "# My Skill\n\nBody with unicode: café résumé\n"
        result = submission_publisher._build_skill_md("my-skill", "A description.", body)
        self.assertIn(body.lstrip("\n"), result)

    def test_leading_newlines_stripped_from_body(self):
        body = "\n\n\n# Title\n\nContent."
        result = submission_publisher._build_skill_md("s", "A" * 20, body)
        # Body should start right after the closing ---
        self.assertNotIn("\n\n\n\n# Title", result)
        self.assertIn("# Title", result)


class TestBuildZipDeterministic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _make_skill_dir(self, slug: str) -> Path:
        skill_dir = self.root / slug
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: " + slug + '\ndescription: "A test."\n---\n# Test\n\nBody.', encoding="utf-8")
        (skill_dir / "marketplace.json").write_text('{"title": "Test", "category": "data"}', encoding="utf-8")
        return skill_dir

    def test_zip_is_created(self):
        skill_dir = self._make_skill_dir("test-skill")
        archive = self.root / "test-skill.zip"
        submission_publisher._build_zip_deterministic(skill_dir, archive)
        self.assertTrue(archive.exists())

    def test_zip_is_byte_stable(self):
        skill_dir = self._make_skill_dir("stable-skill")
        archive1 = self.root / "run1.zip"
        archive2 = self.root / "run2.zip"
        submission_publisher._build_zip_deterministic(skill_dir, archive1)
        submission_publisher._build_zip_deterministic(skill_dir, archive2)
        self.assertEqual(archive1.read_bytes(), archive2.read_bytes())

    def test_zip_contains_expected_files(self):
        skill_dir = self._make_skill_dir("check-skill")
        archive = self.root / "check-skill.zip"
        submission_publisher._build_zip_deterministic(skill_dir, archive)
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
        self.assertIn("check-skill/SKILL.md", names)
        self.assertIn("check-skill/marketplace.json", names)

    def test_zip_fixed_timestamps(self):
        skill_dir = self._make_skill_dir("ts-skill")
        archive = self.root / "ts-skill.zip"
        submission_publisher._build_zip_deterministic(skill_dir, archive)
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                self.assertEqual(info.date_time, (2024, 1, 1, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
