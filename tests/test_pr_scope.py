from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.validate_pr_scope import changed_paths, scope_errors


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

    def test_deleted_platform_file_is_rejected(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)

        def git(*arguments: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["git", *arguments],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )

        git("init")
        git("config", "user.name", "Policy test")
        git("config", "user.email", "policy@example.test")
        workflow = root / ".github" / "workflows" / "skill-review.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: review\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-m", "base")
        base = git("rev-parse", "HEAD").stdout.strip()

        workflow.unlink()
        git("add", "-u")
        git("commit", "-m", "delete platform workflow")

        paths = changed_paths(base, root)
        self.assertIn(".github/workflows/skill-review.yml", paths)
        errors = scope_errors("external-contributor", paths)
        self.assertTrue(any("platform file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
