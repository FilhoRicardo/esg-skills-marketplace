from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.site_intake import SITE_INTAKE_MARKETPLACE_MAX_BYTES, PolicyError, validate_submission


VALID_SKILL = """---
name: climate-action-brief
description: Prepare a bounded ESG briefing from user-provided operating evidence and source notes.
---

# Climate action brief

Use the supplied evidence only. Separate facts from assumptions, preserve source links, and call out uncertainty where the source pack is incomplete.
"""

VALID_MARKETPLACE = json.dumps({"title": "Climate action brief", "category": "strategy"})


class SiteIntakeTests(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "skills").mkdir()
        (root / "site").mkdir()
        return root

    def test_valid_site_submission_passes(self) -> None:
        entry = validate_submission(
            VALID_SKILL,
            VALID_MARKETPLACE,
            root=self.make_root(),
            rights_confirmed=True,
            boundary_confirmed=True,
        )
        self.assertEqual(entry["slug"], "climate-action-brief")
        self.assertEqual(entry["category"], "strategy")

    def test_existing_slug_is_rejected(self) -> None:
        root = self.make_root()
        skill = root / "skills" / "climate-action-brief"
        skill.mkdir()
        (skill / "SKILL.md").write_text(VALID_SKILL, encoding="utf-8")
        (skill / "marketplace.json").write_text(VALID_MARKETPLACE, encoding="utf-8")

        with self.assertRaisesRegex(PolicyError, "already exists"):
            validate_submission(
                VALID_SKILL,
                VALID_MARKETPLACE,
                root=root,
                rights_confirmed=True,
                boundary_confirmed=True,
            )

    def test_site_specific_size_limit_is_enforced(self) -> None:
        oversize_json = "{" + '"title":"' + ("A" * SITE_INTAKE_MARKETPLACE_MAX_BYTES) + '","category":"strategy"}'
        with self.assertRaisesRegex(PolicyError, "site intake limit"):
            validate_submission(
                VALID_SKILL,
                oversize_json,
                root=self.make_root(),
                rights_confirmed=True,
                boundary_confirmed=True,
            )

    def test_missing_attestation_is_rejected(self) -> None:
        with self.assertRaisesRegex(PolicyError, "redistribution rights"):
            validate_submission(
                VALID_SKILL,
                VALID_MARKETPLACE,
                root=self.make_root(),
                rights_confirmed=False,
                boundary_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
