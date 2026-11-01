"""Scenarios that break the pointer rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import unittest

from tests.scenario.project import ScenarioCase

_FEATURE = "docs/design/Feature.md"
_APP = "src/app.py"
_RUN_DOC = '    """Run.\n\n    @doc: docs/design/Feature.md#1-기능'
_INDEX_ROW = "| [기능 설계](design/Feature.md) | 기능 | M0-T1 |"


class PointerRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def add_document_b(self, body: str) -> None:
        self.write("docs/design/B.md", f"# B\n\n전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.\n\n## 1. 실행\n\n{body}")
        self.replace("docs/index.md", _INDEX_ROW, f"{_INDEX_ROW}\n| [B](design/B.md) | b | M0-T1 |")

    def test_missing_symbol(self) -> None:
        self.append(_FEATURE, "\n[x](../../src/app.py#nope)\n")
        self.assert_caught("check_pointers", "구문 트리에 심볼 없음: ../../src/app.py#nope")

    def test_missing_code_file(self) -> None:
        self.append(_FEATURE, "\n[x](../../src/gone.py#f)\n")
        self.assert_caught("check_pointers", "코드 포인터 대상 파일 없음: ../../src/gone.py#f")

    def test_line_number_pointer(self) -> None:
        self.append(_FEATURE, "\n[x](../../src/app.py#L10)\n")
        self.assert_caught("check_pointers", "줄 번호 포인터는 금지됨")

    def test_missing_document(self) -> None:
        self.replace(_APP, _RUN_DOC, _RUN_DOC + "\n    @doc: docs/design/Gone.md")
        self.assert_caught("check_pointers", "근거 문서 없음: docs/design/Gone.md")

    def test_missing_anchor(self) -> None:
        self.replace(_APP, _RUN_DOC, _RUN_DOC.replace("#1-기능", "#9-없음"))
        self.assert_caught("check_pointers", "앵커 없음: docs/design/Feature.md#9-없음")

    def test_public_function_without_pointer(self) -> None:
        self.append(_APP, "\n\ndef extra() -> None:\n    pass\n")
        self.assert_caught("check_pointers", "공개 심볼 extra에 @doc 포인터 없음")

    def test_module_without_pointer(self) -> None:
        self.write("src/other.py", 'def f() -> None:\n    """F.\n\n    @doc: docs/design/Feature.md#1-기능\n    """\n')
        self.assert_caught("check_pointers", "src/other.py:1: 파일에 @doc 포인터 없음")

    def test_typescript_function_without_pointer(self) -> None:
        self.append("src/util.ts", "\nexport function util2(): number {\n  return 2;\n}\n")
        self.assert_caught("check_pointers", "공개 심볼 util2에 @doc 포인터 없음")

    def test_document_pointer_without_reverse(self) -> None:
        self.add_document_b("[run](../../src/app.py#run)\n")
        self.assert_caught("check_pointers", "역방향 포인터 없음")
        self.assert_caught("check_pointers", "@doc: docs/design/B.md#1-실행를 단다")

    def test_code_pointer_without_receiving_document(self) -> None:
        self.add_document_b("내용.\n")
        self.replace(_APP, _RUN_DOC, _RUN_DOC + "\n    @doc: docs/design/B.md")
        self.assert_caught("check_pointers", "받아 주는 문서 포인터 없음: docs/design/B.md")

    def test_module_pointer_is_not_a_symbol_reverse(self) -> None:
        self.add_document_b("[run](../../src/app.py#run)\n")
        self.replace(_APP, '"""App.\n\n@doc: docs/design/Feature.md#1-기능', '"""App.\n\n@doc: docs/design/Feature.md#1-기능\n@doc: docs/design/B.md')
        self.assert_caught("check_pointers", "역방향 포인터 없음")

    def test_stub_of_unknown_task(self) -> None:
        self.replace(_APP, "@stub: I2", "@stub: I99")
        self.assert_caught("check_pointers", "목업의 작업 I99가 로드맵·이슈에 없음")

    def test_stub_of_finished_task(self) -> None:
        self.replace(_APP, "@stub: I2", "@stub: I1")
        self.assert_caught("check_pointers", "작업 I1가 진행 중([~])이 아닌데 목업이 남아 있음")

    def test_syntax_error(self) -> None:
        self.append(_APP, "\ndef broken(:\n")
        self.assert_caught("check_pointers", "src/app.py")

    def test_unattached_comment_pointer(self) -> None:
        self.append("src/util.ts", "\n// @doc: docs/design/Feature.md\n\nconst x = 1;\n")
        self.assert_caught("check_pointers", "@doc 주석 아래에 심볼 정의가 없음")

    def test_comment_pointer_on_a_code_line(self) -> None:
        self.append("src/util.ts", "\nconst y = 2; // @doc: docs/design/Feature.md\n")
        self.assert_caught("check_pointers", "코드와 같은 줄의 @doc 주석은 허용되지 않음")

    def test_document_pointer_that_followed_a_code_pointer(self) -> None:
        self.replace(_FEATURE, "[Parser](../../src/app.py#Parser)", "[Parser](../../src/app.py#Parser.parse)")
        self.assert_caught("check_pointers", "포인터 확인 필요: src/app.py#Parser.parse")

    def test_document_side_is_checked_first(self) -> None:
        self.append(_FEATURE, "\n[x](../../src/app.py#nope)\n")
        self.append(_APP, "\n\ndef extra() -> None:\n    pass\n")
        self.assert_caught("check_pointers", "문서→코드 포인터 문제 1건을 먼저 고친다")
        self.assertNotIn("extra", self.checks()["check_pointers"][1])

    def test_removed_symbol_pointer_when_the_module_is_not_linked(self) -> None:
        self.replace(_FEATURE, "- [app](../../src/app.py): 앱 모듈.\n", "")
        self.replace(_FEATURE, "- [run](../../src/app.py#run): 실행한다.\n", "")
        self.assert_caught("check_pointers", "받아 주는 문서 포인터 없음: docs/design/Feature.md가 src/app.py#run")

    def test_removed_class_pointer(self) -> None:
        self.replace(_APP, '    """Parse.\n\n    @doc: docs/design/Feature.md#1-기능\n    """', '    """Parse."""')
        self.assert_caught("check_pointers", "역방향 포인터 없음")

    def test_document_path_whose_case_differs(self) -> None:
        self.replace(_APP, _RUN_DOC, _RUN_DOC.replace("Feature.md", "feature.md"))
        case_insensitive = (self.root / "docs/design/feature.md").exists()
        self.assert_caught("check_pointers", "근거 문서의 대소문자가 다름" if case_insensitive else "근거 문서 없음")


if __name__ == "__main__":
    unittest.main()
