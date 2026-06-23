"""Tests for scripts/intake_server.py"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import intake_server


def _good_bundle(**overrides):
    b = {
        "skill_md": "# ESG Skill\n\nThis skill helps with ESG reporting workflows and materiality assessment tasks.",
        "title": "Test ESG Skill",
        "public_name": "Alice",
        "public_contact": "alice@example.com",
        "rights_confirmed": True,
        "boundary_confirmed": True,
        "submitted_at": "2026-06-23T00:00:00Z",
    }
    b.update(overrides)
    return b


class TestValidateBundle(unittest.TestCase):
    def test_valid_bundle_returns_skill_and_title(self):
        skill_md, title = intake_server._validate_bundle(_good_bundle())
        self.assertIn("ESG Skill", skill_md)
        self.assertEqual(title, "Test ESG Skill")

    def test_missing_skill_md_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(skill_md=""))
        self.assertIn("skill_md", str(ctx.exception))

    def test_skill_md_too_short_raises(self):
        with self.assertRaises(ValueError):
            intake_server._validate_bundle(_good_bundle(skill_md="short"))

    def test_nul_byte_in_skill_md_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(skill_md="# ESG\n\n" + "x" * 80 + "\x00"))
        self.assertIn("NUL", str(ctx.exception))

    def test_skill_md_too_large_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(skill_md="x" * 41_000))
        self.assertIn("bytes", str(ctx.exception))

    def test_title_too_short_raises(self):
        with self.assertRaises(ValueError):
            intake_server._validate_bundle(_good_bundle(title="hi"))

    def test_title_multiline_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(title="Title\nSecond line"))
        self.assertIn("single line", str(ctx.exception))

    def test_rights_not_confirmed_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(rights_confirmed=False))
        self.assertIn("rights_confirmed", str(ctx.exception))

    def test_boundary_not_confirmed_raises(self):
        with self.assertRaises(ValueError) as ctx:
            intake_server._validate_bundle(_good_bundle(boundary_confirmed=False))
        self.assertIn("boundary_confirmed", str(ctx.exception))


class TestWriteInbox(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        root = Path(self.tmpdir.name)
        self._orig_inbox = intake_server.INBOX_DIR
        self._orig_needs = intake_server.NEEDS_ATTENTION_DIR
        intake_server.INBOX_DIR = root / "inbox"
        intake_server.NEEDS_ATTENTION_DIR = root / "needs-attention"
        intake_server.INBOX_DIR.mkdir(parents=True)

    def tearDown(self):
        intake_server.INBOX_DIR = self._orig_inbox
        intake_server.NEEDS_ATTENTION_DIR = self._orig_needs
        self.tmpdir.cleanup()

    def test_writes_skill_md_and_submission_json(self):
        b = _good_bundle()
        skill_md = b["skill_md"]
        sid = intake_server._write_inbox(b, skill_md, b["title"])
        sub_dir = intake_server.INBOX_DIR / sid
        self.assertTrue((sub_dir / "SKILL.md").exists())
        self.assertTrue((sub_dir / "submission.json").exists())

    def test_submission_json_contains_sha256(self):
        b = _good_bundle()
        sid = intake_server._write_inbox(b, b["skill_md"], b["title"])
        meta = json.loads((intake_server.INBOX_DIR / sid / "submission.json").read_text())
        expected_sha = hashlib.sha256(b["skill_md"].encode("utf-8")).hexdigest()
        self.assertEqual(meta["sha256"], expected_sha)

    def test_submission_json_records_title(self):
        b = _good_bundle()
        sid = intake_server._write_inbox(b, b["skill_md"], b["title"])
        meta = json.loads((intake_server.INBOX_DIR / sid / "submission.json").read_text())
        self.assertEqual(meta["title"], "Test ESG Skill")

    def test_skill_md_preserved_byte_for_byte(self):
        b = _good_bundle()
        sid = intake_server._write_inbox(b, b["skill_md"], b["title"])
        self.assertEqual(
            (intake_server.INBOX_DIR / sid / "SKILL.md").read_text(encoding="utf-8"),
            b["skill_md"],
        )

    def test_public_name_truncated_to_max(self):
        b = _good_bundle(public_name="A" * 500)
        sid = intake_server._write_inbox(b, b["skill_md"], b["title"])
        meta = json.loads((intake_server.INBOX_DIR / sid / "submission.json").read_text())
        self.assertLessEqual(len(meta["public_name"]), intake_server.PUBLIC_FIELD_MAX)

    def test_each_call_generates_unique_id(self):
        b = _good_bundle()
        sid1 = intake_server._write_inbox(b, b["skill_md"], b["title"])
        sid2 = intake_server._write_inbox(b, b["skill_md"], b["title"])
        self.assertNotEqual(sid1, sid2)


if __name__ == "__main__":
    unittest.main()
