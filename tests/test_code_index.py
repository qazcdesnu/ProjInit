"""Tests for the per-file analysis of symbols and pointers to documents.

@doc: docs/VerificationTools.md#5-테스트
"""

from tests.support import RepoTestCase
from tools.code_index import ModuleIndex, index_module


class IndexModuleTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def index(self, relative: str, text: str) -> ModuleIndex:
        return index_module(self.write(relative, text), self.root)

    def owners(self, index: ModuleIndex) -> list[tuple[str, int]]:
        return [(pointer.symbol.qualname, pointer.line) for pointer in index.doc_pointers]

    def test_comment_attaches_to_definition_right_below(self) -> None:
        index = self.index("a.rs", "fn main() {}\n\n/// @doc: docs/A.md\n/// more\n#[inline]\nfn run() {}\n")
        self.assertEqual(self.owners(index), [("run", 3)])
        self.assertEqual(index.problems, [])

    def test_file_header_comment_belongs_to_module(self) -> None:
        index = self.index("a.go", "// @doc: docs/A.md\n\npackage a\n\nfunc Run() {}\n")
        self.assertEqual(self.owners(index), [("", 1)])
        index = self.index("b.rs", "//! @doc: docs/A.md\nuse std::fmt;\n")
        self.assertEqual(self.owners(index), [("", 1)])

    def test_header_comment_right_above_definition_belongs_to_definition(self) -> None:
        index = self.index("a.ts", "// @doc: docs/A.md\nexport class A {}\n")
        self.assertEqual(self.owners(index), [("A", 1)])

    def test_blank_line_after_code_leaves_comment_unattached(self) -> None:
        index = self.index("a.c", "int x;\n\n/* @doc: docs/A.md */\n\nint f(void);\n")
        self.assertEqual(index.doc_pointers, [])
        self.assertIn("@doc 주석 아래에 심볼 정의가 없음", index.problems[0].message)

    def test_comment_sharing_a_line_with_code_is_rejected(self) -> None:
        index = self.index("a.cpp", "int x; // @doc: docs/A.md\n/* @doc: docs/A.md */ int y;\n")
        messages = [(problem.line, problem.message) for problem in index.problems]
        self.assertEqual(
            messages,
            [(1, "코드와 같은 줄의 @doc 주석은 허용되지 않음"), (2, "코드와 같은 줄의 @doc 주석은 허용되지 않음")],
        )

    def test_block_comment_with_several_tags(self) -> None:
        index = self.index("A.java", "class A {\n  /**\n   * @doc: docs/A.md\n   * @doc: docs/B.md\n   */\n  void m() {}\n}\n")
        self.assertEqual(self.owners(index), [("A.m", 3), ("A.m", 4)])

    def test_python_docstring_pointers(self) -> None:
        index = self.index("a.py", '"""@doc: docs/A.md"""\n\n\ndef f():\n    """Do.\n\n    @doc: docs/B.md#x\n    """\n')
        self.assertEqual(self.owners(index), [("", 1), ("f", 7)])
        self.assertEqual(index.doc_pointers[1].anchor, "x")

    def test_syntax_error_is_reported(self) -> None:
        index = self.index("a.py", "def f(:\n    pass\n")
        self.assertEqual([problem.message for problem in index.problems], ["파싱 실패: 구문 오류"])
        self.assertEqual(index.symbols, {})

    def test_comment_only_file_has_no_code(self) -> None:
        self.assertFalse(self.index("a.rs", "// nothing here\n").has_code)
        self.assertTrue(self.index("b.rs", "const X: i32 = 1;\n").has_code)
