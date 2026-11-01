"""Scenarios that break the doc rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import unittest

from tests.scenario.project import ScenarioCase

_FEATURE = "docs/design/Feature.md"


class DocRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def test_baseline_is_clean(self) -> None:
        self.assert_clean()

    def test_broken_link(self) -> None:
        self.append(_FEATURE, "\n[x](Nope.md)\n")
        self.assert_caught("check_docs", "링크 대상 없음: Nope.md")

    def test_missing_anchor(self) -> None:
        self.append(_FEATURE, "\n[x](../index.md#nope)\n")
        self.assert_caught("check_docs", "앵커 없음: ../index.md#nope")

    def test_orphan_document(self) -> None:
        self.write("docs/design/Orphan.md", "# O\n\n[i](../index.md)\n")
        self.assert_caught("check_docs", "고아 문서")

    def test_entry_without_index_link(self) -> None:
        self.replace("CLAUDE.md", "- 모든 작업 전에 [문서 인덱스](docs/index.md)를 읽고, 지금 작업에 해당하는 문서를 찾아 읽는다.\n", "")
        self.assert_caught("check_docs", "진입 문서에 docs/index.md 링크 없음")

    def test_entry_inline_code(self) -> None:
        self.append("CLAUDE.md", "- `x` [a](docs/index.md)\n")
        self.assert_caught("check_docs", "진입 문서에 인라인 코드를 쓸 수 없음")

    def test_entry_prose(self) -> None:
        self.append("CLAUDE.md", "그냥 문장이다.\n")
        self.assert_caught("check_docs", "하위 문서 링크 목록 줄만 쓸 수 있음")

    def test_entry_code_block(self) -> None:
        self.append("CLAUDE.md", "\n```sh\nls\n```\n")
        self.assert_caught("check_docs", "진입 문서에 코드 블록을 쓸 수 없음")

    def test_entry_missing(self) -> None:
        self.remove("CLAUDE.md")
        self.assert_caught("check_docs", "진입 문서 없음")

    def test_index_missing(self) -> None:
        self.remove("docs/index.md")
        self.assert_caught("check_docs", "인덱스 문서 없음")

    def test_link_into_private(self) -> None:
        self.append(_FEATURE, "\n[s](../../private/secret.txt)\n")
        self.assert_caught("check_docs", "로컬 자료로 링크할 수 없음: ../../private/secret.txt")

    def test_optional_link_into_private(self) -> None:
        self.append(_FEATURE, '\n[s](../../private/none.md "선택")\n')
        self.assert_caught("check_docs", "로컬 자료로 링크할 수 없음: ../../private/none.md")

    def test_existing_optional_link_with_missing_anchor(self) -> None:
        self.write("README.md", "# R\n")
        self.append(_FEATURE, '\n[R](../../README.md#nope "선택")\n')
        self.assert_caught("check_docs", "앵커 없음: ../../README.md#nope")

    def test_missing_legacy_file_link(self) -> None:
        self.append(_FEATURE, "\n[x](../../legacy/old/gone.py)\n")
        self.assert_caught("check_docs", "링크 대상 없음: ../../legacy/old/gone.py")

    def test_broken_link_in_readme(self) -> None:
        self.write("README.md", "# R\n\n[g](docs/Gone.md)\n")
        self.assert_caught("check_docs", "링크 대상 없음: docs/Gone.md")

    def test_link_whose_case_differs(self) -> None:
        self.append(_FEATURE, "\n[x](feature.md)\n")
        case_insensitive = (self.root / "docs/design/feature.md").exists()
        self.assert_caught("check_docs", "링크 대상의 대소문자가 다름" if case_insensitive else "링크 대상 없음: feature.md")

    def test_optional_link_without_target_passes(self) -> None:
        self.append(_FEATURE, '\n[x](Maybe.md "선택")\n')
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
