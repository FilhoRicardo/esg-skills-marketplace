from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class IdAndLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: set[str] = set()
        self.scripts: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.links.add(values["href"] or "")
        if tag == "script" and values.get("src"):
            self.scripts.add(values["src"] or "")


def parse_page(name: str) -> IdAndLinkParser:
    parser = IdAndLinkParser()
    parser.feed((SITE / name).read_text(encoding="utf-8"))
    return parser


class SitePageTests(unittest.TestCase):
    def test_catalogue_and_submission_are_separate_pages(self) -> None:
        catalogue = parse_page("index.html")
        submission = parse_page("submit.html")

        self.assertIn("skill-list", catalogue.ids)
        self.assertNotIn("submission-form", catalogue.ids)
        self.assertIn("submit.html", catalogue.links)

        self.assertIn("submission-form", submission.ids)
        self.assertIn("marketplace-title", submission.ids)
        self.assertNotIn("marketplace-category", submission.ids)
        self.assertNotIn("marketplace-file", submission.ids)
        self.assertNotIn("submission-preview", (SITE / "submit.html").read_text(encoding="utf-8"))
        self.assertIn("./#skills-title", submission.links)

    def test_both_pages_load_the_shared_assets(self) -> None:
        for name in ("index.html", "submit.html"):
            page = parse_page(name)
            self.assertTrue(any(source.split("?", 1)[0] == "app.js" for source in page.scripts))
            html = (SITE / name).read_text(encoding="utf-8")
            self.assertIn('href="aster-tokens.css"', html)
            self.assertIn('href="styles.css?', html)

    def test_browser_still_sends_generated_marketplace_metadata(self) -> None:
        app = (SITE / "app.js").read_text(encoding="utf-8")
        self.assertIn("JSON.stringify({ title })", app)
        self.assertIn("stageUploadPath", app)
        self.assertIn("finalizeUploadPath", app)
        self.assertIn("slugifyTitle", app)
        self.assertNotIn("parseFrontmatter", app)

    def test_public_page_does_not_lock_document_scrolling(self) -> None:
        styles = (SITE / "styles.css").read_text(encoding="utf-8")
        body_rule = re.search(r"body\s*\{(?P<body>.*?)\}", styles, re.DOTALL)
        self.assertIsNotNone(body_rule)
        self.assertNotIn("overflow: hidden", body_rule.group("body"))
        self.assertNotIn("height: 100dvh", body_rule.group("body"))

    def test_disabled_submit_button_has_a_visible_state(self) -> None:
        styles = (SITE / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".aster-btn:disabled", styles)
        self.assertIn(".aster-btn--primary:disabled", styles)


if __name__ == "__main__":
    unittest.main()
