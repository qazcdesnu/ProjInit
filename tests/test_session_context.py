"""Tests for the session start context.

@doc: docs/design/Checkers.md#16-세션-시작-안내
"""

import contextlib
import io
import unittest
from unittest import mock

from tests.support import RepoTestCase
from projinit import session_context
from projinit.config import load_project
from projinit.session_context import reference_context


class ReferenceContextTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#16-세션-시작-안내"""

    def run_main(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = session_context.main(["--root", str(self.root)])
        return code, out.getvalue()

    def test_empty_without_materials(self) -> None:
        self.assertEqual(reference_context(load_project(self.root)), "")
        self.assertEqual(self.run_main(), (0, ""))

    def test_without_list_document(self) -> None:
        self.write("reference/notes.md", "# n\n")
        lines = reference_context(load_project(self.root)).splitlines()
        self.assertTrue(lines[0].startswith("참고 자료: reference/에 자료 1개가 있다."))
        self.assertEqual(lines[1:], ["목록 문서 docs/Reference.md 없음.", "목록에 없는 자료:", "- reference/notes.md"])

    def test_list_items_and_unlisted(self) -> None:
        self.write("reference/api.pdf", "x")
        self.write("reference/notes.md", "x")
        self.write(
            "docs/Reference.md",
            "# R\n\n- [API](../reference/api.pdf): 결제 API. 쓰는 곳: 결제.\n\n```markdown\n- 예시 줄\n```\n",
        )
        lines = reference_context(load_project(self.root)).splitlines()
        self.assertEqual(
            lines[1:],
            [
                "목록 문서 docs/Reference.md의 항목:",
                "- [API](../reference/api.pdf): 결제 API. 쓰는 곳: 결제.",
                "목록에 없는 자료:",
                "- reference/notes.md",
            ],
        )

    def test_caps_long_lists(self) -> None:
        for number in range(3):
            self.write(f"reference/{number}.txt", "x")
        with mock.patch.object(session_context, "MAX_ITEMS", 2):
            lines = reference_context(load_project(self.root)).splitlines()
        self.assertEqual(lines[-3:], ["- reference/0.txt", "- reference/1.txt", "- … 외 1개"])

    def test_config_error_still_exits_zero(self) -> None:
        self.write("projinit.toml", "not toml [")
        self.write("reference/notes.md", "x")
        self.assertEqual(self.run_main(), (0, ""))


if __name__ == "__main__":
    unittest.main()
