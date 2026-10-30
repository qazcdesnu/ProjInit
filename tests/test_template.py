"""Tests for the initialization templates.

@doc: docs/design/Templates.md#8-구현
"""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.support import RepoTestCase
from projinit import check_docs, check_tasks
from projinit.config import load_config
from projinit.doclib import extract_links, is_external, resolve_link
from projinit.template import COMMON_FILES, INITIAL_FILES, TemplateError, render

_REPO = Path(__file__).resolve().parent.parent
_VALUES = {"repository": "git@github.com:me/demo.git", "version": "0.1.0", "source": "git+https://example.com/ProjInit"}
# Installed by the enforcement step (M2-T3), not by the document templates.
_DEVICE_FILES = (".github/pull_request_template.md",)


class RenderTest(unittest.TestCase):
    """@doc: docs/design/Templates.md#8-구현"""

    def test_every_template_renders_and_needs_its_values(self) -> None:
        for relative in COMMON_FILES + INITIAL_FILES:
            self.assertNotIn("{{repository}}", render(relative, _VALUES), relative)
        self.assertIn("git@github.com:me/demo.git", render("docs/PullRequestRule.md", _VALUES))
        with self.assertRaises(TemplateError) as raised:
            render("docs/PullRequestRule.md", {})
        self.assertEqual(str(raised.exception), "docs/PullRequestRule.md: 값이 없는 빈 자리: repository")

    def test_this_repository_matches_its_templates(self) -> None:
        values = load_config(_REPO).template_values
        for relative in COMMON_FILES:
            self.assertEqual((_REPO / relative).read_text(encoding="utf-8"), render(relative, values), relative)


class RenderedProjectTest(RepoTestCase):
    """@doc: docs/design/Templates.md#8-구현"""

    def setUp(self) -> None:
        super().setUp()
        for relative in COMMON_FILES + INITIAL_FILES:
            self.write(relative, render(relative, _VALUES))
        for relative in _DEVICE_FILES:
            self.write(relative, "")

    def test_common_documents_link_only_to_generated_files(self) -> None:
        generated = {(self.root / relative).resolve() for relative in COMMON_FILES + INITIAL_FILES + _DEVICE_FILES}
        for relative in COMMON_FILES:
            path = self.root / relative
            for link in extract_links(path, path.read_text(encoding="utf-8")):
                if is_external(link.target):
                    continue
                self.assertIn(resolve_link(link)[0], generated, f"{relative}:{link.line} {link.target}")

    def test_generated_documents_pass_the_document_and_task_checks(self) -> None:
        for checker in (check_docs, check_tasks):
            output = io.StringIO()
            with redirect_stdout(output):
                code = checker.main(["--root", str(self.root)])
            self.assertEqual(code, 0, output.getvalue())


if __name__ == "__main__":
    unittest.main()
