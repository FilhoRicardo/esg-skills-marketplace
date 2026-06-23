from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_catalog import build_download_bundles, rendered_submission_config


class BuildCatalogueTests(unittest.TestCase):
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

    def test_submission_config_exposes_public_limits(self) -> None:
        rendered = json.loads(rendered_submission_config())
        self.assertEqual(rendered["submitPath"], "/api/intake/submit")
        self.assertNotIn("stageUploadPath", rendered)
        self.assertNotIn("finalizeUploadPath", rendered)
        self.assertNotIn("dispatchPath", rendered)
        self.assertNotIn("allowedCategories", rendered)
        self.assertEqual(rendered["minTitleChars"], 4)
        self.assertEqual(rendered["maxTitleChars"], 80)
        self.assertEqual(rendered["minSkillChars"], 80)
        self.assertNotIn("minBodyChars", rendered)
        self.assertGreater(rendered["maxSkillFileBytes"], rendered["maxMarketplaceFileBytes"])

    def test_download_bundle_contains_reviewed_bundle(self) -> None:
        root = self.make_root()
        self.add_skill(root)
        build_download_bundles(root)

        archive_path = root / "site" / "downloads" / "materiality-brief.zip"
        self.assertTrue(archive_path.is_file())
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(
                sorted(archive.namelist()),
                [
                    "materiality-brief/SKILL.md",
                    "materiality-brief/marketplace.json",
                ],
            )


if __name__ == "__main__":
    unittest.main()
