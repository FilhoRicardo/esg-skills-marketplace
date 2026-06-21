from __future__ import annotations

import unittest

from scripts.validate_pr_scope import scope_errors


class PullRequestScopeTests(unittest.TestCase):
    def test_owner_can_change_platform_files(self) -> None:
        self.assertEqual(scope_errors("FilhoRicardo", ["scripts/validate_skills.py"]), [])

    def test_external_contributor_can_submit_one_skill(self) -> None:
        paths = [
            "skills/materiality-brief/SKILL.md",
            "skills/materiality-brief/marketplace.json",
            "site/catalog.json",
        ]
        self.assertEqual(scope_errors("contributor", paths), [])

    def test_external_platform_change_is_rejected(self) -> None:
        errors = scope_errors("contributor", [".github/workflows/skill-review.yml"])
        self.assertTrue(any("platform file" in error for error in errors))

    def test_one_skill_per_pull_request(self) -> None:
        errors = scope_errors(
            "contributor",
            ["skills/one-skill/SKILL.md", "skills/two-skill/SKILL.md"],
        )
        self.assertIn("submit one skill per pull request", errors)


if __name__ == "__main__":
    unittest.main()
