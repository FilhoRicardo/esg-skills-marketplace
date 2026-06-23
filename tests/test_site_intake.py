from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.site_intake import (
    SITE_INTAKE_MARKETPLACE_MAX_BYTES,
    PolicyError,
    validate_submission,
    write_submission,
)


VALID_SKILL = """# Climate action brief

Use the supplied evidence only. Separate facts from assumptions, preserve source links, and call out uncertainty where the source pack is incomplete.
"""

VALID_MARKETPLACE = json.dumps({"title": "Climate action brief"})


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
        self.assertEqual(entry["category"], "pending-review")

    def test_write_submission_preserves_raw_markdown(self) -> None:
        root = self.make_root()
        entry = write_submission(
            root=root,
            skill_md=VALID_SKILL,
            marketplace_json=VALID_MARKETPLACE,
            public_name="",
            public_contact="",
            rights_confirmed=True,
            boundary_confirmed=True,
        )
        self.assertEqual(
            (root / entry["path"] / "SKILL.md").read_text(encoding="utf-8"),
            VALID_SKILL,
        )

    def test_slug_is_derived_from_public_title(self) -> None:
        entry = validate_submission(
            VALID_SKILL,
            json.dumps({"title": "Café climate brief"}),
            root=self.make_root(),
            rights_confirmed=True,
            boundary_confirmed=True,
        )
        self.assertEqual(entry["slug"], "cafe-climate-brief")

    def test_site_submitter_cannot_assign_category(self) -> None:
        with self.assertRaisesRegex(PolicyError, "may only contain title"):
            validate_submission(
                VALID_SKILL,
                json.dumps({"title": "Climate action brief", "category": "strategy"}),
                root=self.make_root(),
                rights_confirmed=True,
                boundary_confirmed=True,
            )

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
        oversize_json = "{" + '"title":"' + ("A" * SITE_INTAKE_MARKETPLACE_MAX_BYTES) + '"}'
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

    def test_short_skill_instructions_are_rejected(self) -> None:
        with self.assertRaisesRegex(PolicyError, "at least 80 characters"):
            validate_submission(
                "# Too short",
                VALID_MARKETPLACE,
                root=self.make_root(),
                rights_confirmed=True,
                boundary_confirmed=True,
            )

    def test_invisible_control_character_is_rejected(self) -> None:
        with self.assertRaisesRegex(PolicyError, "invisible Unicode control"):
            validate_submission(
                VALID_SKILL + "\u202e",
                VALID_MARKETPLACE,
                root=self.make_root(),
                rights_confirmed=True,
                boundary_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
