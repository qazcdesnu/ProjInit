"""Tests for the document link checker.

@doc: docs/design/Checkers.md#5-테스트
"""

import unittest

from tests.support import RepoTestCase
from projinit.check_docs import check_entry, check_entry_format, check_links, find_orphans
from projinit.config import load_project


class CheckDocsTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("CLAUDE.md", "# C\n\n[index](docs/index.md)\n")
        self.write("docs/index.md", "# Index\n\n[rule](Rule.md#1-intro)\n")
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[back](index.md)\n")

    def test_clean_repository_passes(self) -> None:
        self.assertEqual(check_links(load_project(self.root)) + check_entry(load_project(self.root)) + find_orphans(load_project(self.root)), [])

    def test_reports_missing_file_and_anchor(self) -> None:
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[gone](Gone.md) [bad](index.md#nope)\n")
        messages = [problem.message for problem in check_links(load_project(self.root))]
        self.assertEqual(messages, ["링크 대상 없음: Gone.md", "앵커 없음: index.md#nope"])

    def test_skips_external_and_code_links(self) -> None:
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[w](https://x.y) [c](../missing.py#f)\n")
        self.assertEqual(check_links(load_project(self.root)), [])

    def test_reports_orphan(self) -> None:
        orphan = self.write("docs/Orphan.md", "# Orphan\n\n[index](index.md)\n")
        self.assertEqual([problem.path for problem in find_orphans(load_project(self.root))], [orphan])

    def test_reports_entry_without_index_link(self) -> None:
        self.write("CLAUDE.md", "# C\n")
        self.assertEqual(len(check_entry(load_project(self.root))), 1)


class EntryFormatTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/index.md", "# Index\n")

    def problems(self, text: str) -> list[tuple[int, str]]:
        self.write("CLAUDE.md", text)
        return [(problem.line, problem.message) for problem in check_entry_format(load_project(self.root))]

    def test_title_purpose_and_link_lists_pass(self) -> None:
        text = "# C\n\n이 문서는 루트다.\n여러 줄 문단.\n\n## 읽는 순서\n\n- [인덱스](docs/index.md)를 읽는다.\n"
        self.assertEqual(self.problems(text), [])

    def test_reports_code_blocks_and_inline_code(self) -> None:
        text = "# C\n\n목적.\n\n- [인덱스](docs/index.md)와 `uv run`\n\n```sh\nuv run x\n```\n"
        self.assertEqual(
            self.problems(text),
            [
                (5, "진입 문서에 인라인 코드를 쓸 수 없음"),
                (7, "진입 문서에 코드 블록을 쓸 수 없음"),
                (8, "진입 문서에 코드 블록을 쓸 수 없음"),
                (9, "진입 문서에 코드 블록을 쓸 수 없음"),
            ],
        )

    def test_reports_items_without_doc_links_and_extra_paragraphs(self) -> None:
        text = "# C\n\n목적.\n\n- 링크 없음\n- [밖](https://x.y)\n1. [번호](docs/index.md)\n\n둘째 문단.\n"
        messages = self.problems(text)
        self.assertEqual([line for line, _ in messages], [5, 6, 7, 9])

    def test_reports_missing_title(self) -> None:
        self.assertIn((1, "진입 문서는 '# ' 제목으로 시작해야 함"), self.problems("C\n\n- [i](docs/index.md)\n"))


if __name__ == "__main__":
    unittest.main()
