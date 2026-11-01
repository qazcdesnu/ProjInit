"""Tests for markdown link extraction and heading anchors.

@doc: docs/design/Checkers.md#5-테스트
"""

import tempfile
import unittest
from pathlib import Path

from projinit.doclib import actual_case, extract_links, heading_anchors, slugify


class ExtractLinksTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_finds_prose_links_with_line_numbers(self) -> None:
        text = "# T\n\nsee [a](a.md) and [b](b.md#x)\n"
        links = extract_links(Path("doc.md"), text)
        self.assertEqual([(l.line, l.text, l.target) for l in links], [(3, "a", "a.md"), (3, "b", "b.md#x")])

    def test_ignores_code_blocks_inline_code_and_images(self) -> None:
        text = "```md\n[a](a.md)\n```\n`[b](b.md)` ![c](c.png)\n~~~\n[d](d.md)\n~~~\n"
        self.assertEqual(extract_links(Path("doc.md"), text), [])


class HeadingAnchorsTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_slugify_keeps_korean_and_drops_punctuation(self) -> None:
        self.assertEqual(slugify("3. 링크 규칙"), "3-링크-규칙")
        self.assertEqual(slugify("Use `uv` [here](x.md)!"), "use-uv-here")

    def test_duplicate_headings_get_suffixes(self) -> None:
        text = "# A\n## Same\n## Same\n```\n# Hidden\n```\n"
        self.assertEqual(heading_anchors(text), {"a", "same", "same-1"})


class ActualCaseTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#2-공통-모듈"""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        (self.root / "docs/Design").mkdir(parents=True)
        (self.root / "docs/Design/Rule.md").write_text("# R\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_exact_spelling_and_outside_paths_are_none(self) -> None:
        self.assertIsNone(actual_case(self.root / "docs/Design/Rule.md", self.root))
        self.assertIsNone(actual_case(self.root / "docs/Gone.md", self.root))
        self.assertIsNone(actual_case(self.root.parent, self.root))

    def test_reports_the_disk_spelling(self) -> None:
        wrong = self.root / "docs/design/rule.md"
        if not wrong.exists():
            self.skipTest("대소문자를 구분하는 파일 시스템에서는 틀린 이름이 없는 파일이다")
        self.assertEqual(actual_case(wrong, self.root), "docs/Design/Rule.md")
        self.assertEqual(actual_case(Path("docs/design/../Design/rule.md"), self.root), "docs/Design/Rule.md")


if __name__ == "__main__":
    unittest.main()
