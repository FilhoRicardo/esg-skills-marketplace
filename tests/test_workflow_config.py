from __future__ import annotations

import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/skill-review.yml")


class SkillReviewWorkflowTests(unittest.TestCase):
    def test_ready_for_review_is_not_a_trigger(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("types: [opened, synchronize, reopened]", workflow)
        self.assertNotIn("ready_for_review", workflow)


if __name__ == "__main__":
    unittest.main()
