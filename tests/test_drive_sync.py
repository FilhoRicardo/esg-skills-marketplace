"""Tests for scripts/drive_sync.py"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import drive_sync


def _make_bundle(skill_md="# ESG Skill\n\nThis skill helps with ESG reporting workflows.",
                 title="Test ESG Skill"):
    bundle = {
        "skill_md": skill_md,
        "title": title,
        "public_name": "",
        "public_contact": "",
        "rights_confirmed": True,
        "boundary_confirmed": True,
        "submitted_at": "2026-06-23T00:00:00Z",
    }
    return json.dumps(bundle, ensure_ascii=False).encode("utf-8")


class TestWriteInboxAtomic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self._orig_inbox = drive_sync.INBOX_DIR
        self._orig_needs = drive_sync.NEEDS_ATTENTION_DIR
        drive_sync.INBOX_DIR = self.root / "inbox"
        drive_sync.NEEDS_ATTENTION_DIR = self.root / "needs-attention"
        drive_sync.INBOX_DIR.mkdir(parents=True)

    def tearDown(self):
        drive_sync.INBOX_DIR = self._orig_inbox
        drive_sync.NEEDS_ATTENTION_DIR = self._orig_needs
        self.tmpdir.cleanup()

    def test_writes_skill_md_and_submission_json(self):
        bundle_bytes = _make_bundle()
        sha = hashlib.sha256(bundle_bytes).hexdigest()
        sub_dir = drive_sync._write_inbox_atomic("test-uuid-001", bundle_bytes, sha)
        self.assertTrue((sub_dir / "SKILL.md").exists())
        self.assertTrue((sub_dir / "submission.json").exists())
        meta = json.loads((sub_dir / "submission.json").read_text())
        self.assertEqual(meta["sha256"], sha)
        self.assertEqual(meta["title"], "Test ESG Skill")

    def test_skill_md_preserved_byte_for_byte(self):
        skill_text = "# ESG Skill\n\nThis skill helps with ESG reporting workflows."
        bundle_bytes = _make_bundle(skill_md=skill_text)
        sha = hashlib.sha256(bundle_bytes).hexdigest()
        sub_dir = drive_sync._write_inbox_atomic("test-uuid-002", bundle_bytes, sha)
        self.assertEqual((sub_dir / "SKILL.md").read_text(encoding="utf-8"), skill_text)

    def test_sha256_mismatch_raises(self):
        bundle_bytes = _make_bundle()
        wrong_sha = "a" * 64
        with self.assertRaises(ValueError) as ctx:
            drive_sync._write_inbox_atomic("test-uuid-003", bundle_bytes, wrong_sha)
        self.assertIn("SHA-256 mismatch", str(ctx.exception))

    def test_sha256_with_prefix_accepted(self):
        bundle_bytes = _make_bundle()
        sha = "sha256:" + hashlib.sha256(bundle_bytes).hexdigest()
        sub_dir = drive_sync._write_inbox_atomic("test-uuid-004", bundle_bytes, sha)
        self.assertTrue(sub_dir.exists())

    def test_already_in_inbox_skips_without_error(self):
        bundle_bytes = _make_bundle()
        sha = hashlib.sha256(bundle_bytes).hexdigest()
        drive_sync._write_inbox_atomic("test-uuid-005", bundle_bytes, sha)
        # Second call should not raise
        result = drive_sync._write_inbox_atomic("test-uuid-005", bundle_bytes, sha)
        self.assertTrue(result.exists())

    def test_missing_skill_md_raises(self):
        bundle = {"title": "Test", "rights_confirmed": True, "boundary_confirmed": True}
        bundle_bytes = json.dumps(bundle).encode("utf-8")
        sha = hashlib.sha256(bundle_bytes).hexdigest()
        with self.assertRaises(ValueError) as ctx:
            drive_sync._write_inbox_atomic("test-uuid-006", bundle_bytes, sha)
        self.assertIn("skill_md", str(ctx.exception))

    def test_invalid_json_raises(self):
        bundle_bytes = b"not valid json"
        sha = hashlib.sha256(bundle_bytes).hexdigest()
        with self.assertRaises(Exception):
            drive_sync._write_inbox_atomic("test-uuid-007", bundle_bytes, sha)


class TestSubmissionIdFromPath(unittest.TestCase):
    def test_extracts_stem(self):
        self.assertEqual(
            drive_sync._submission_id_from_path("incoming/abc-123.json"), "abc-123"
        )

    def test_uuid_format(self):
        sid = drive_sync._submission_id_from_path(
            "incoming/550e8400-e29b-41d4-a716-446655440000.json"
        )
        self.assertEqual(sid, "550e8400-e29b-41d4-a716-446655440000")


class TestApiKeyLookup(unittest.TestCase):
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(Path, "is_file", return_value=False):
                with self.assertRaises(RuntimeError) as ctx:
                    drive_sync._api_key()
        self.assertIn("HERENOW_API_KEY", str(ctx.exception))

    def test_env_var_used(self):
        with patch.dict("os.environ", {"HERENOW_API_KEY": "test-key"}):
            self.assertEqual(drive_sync._api_key(), "test-key")


if __name__ == "__main__":
    unittest.main()
