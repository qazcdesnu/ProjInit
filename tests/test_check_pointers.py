"""Tests for the document-code pointer checker.

@doc: docs/design/Checkers.md#5-테스트
"""

import io
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.support import RepoTestCase
from projinit.check_pointers import main
from projinit.code_index import SymbolRef, index_module

_DOC = "# A\n\n## 1. Spec\n\n[run](../src/mod.py#Thing.run) [d](../src/mod.py#_decorated)\n"
_MODULE = """'''Module.

@doc: docs/A.md#1-spec
'''

# @doc: docs/A.md
@staticmethod
def _decorated():
    pass


class Thing:
    '''@doc: docs/A.md'''

    def run(self):
        return 1
"""


class CheckPointersTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/A.md", _DOC)
        self.module = self.write("src/mod.py", _MODULE)

    def run_checker(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def test_valid_bidirectional_pointers_pass(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_comment_pointer_attaches_to_decorated_symbol_below(self) -> None:
        index = index_module(self.module, self.root)
        owners = {pointer.symbol.qualname for pointer in index.doc_pointers}
        self.assertEqual(owners, {"", "_decorated", "Thing"})
        self.assertEqual(index.problems, [])

    def test_reports_missing_symbol(self) -> None:
        self.write("docs/A.md", _DOC.replace("Thing.run", "Thing.gone"))
        code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn("구문 트리에 심볼 없음: ../src/mod.py#Thing.gone", output)

    def test_reports_line_number_pointer(self) -> None:
        self.write("docs/A.md", _DOC.replace("#Thing.run", "#L3"))
        self.assertIn("줄 번호 포인터는 금지됨", self.run_checker()[1])

    def test_reports_unattached_comment_pointers(self) -> None:
        self.write("src/mod.py", _MODULE + "\nLIMIT = 3  # @doc: docs/A.md\n# @doc: docs/A.md\n")
        output = self.run_checker()[1]
        self.assertIn("코드와 같은 줄의 @doc 주석은 허용되지 않음", output)
        self.assertIn("@doc 주석 아래에 심볼 정의가 없음", output)

    def test_reports_missing_document_and_anchor(self) -> None:
        self.write("src/mod.py", _MODULE.replace("docs/A.md#1-spec", "docs/A.md#nope\n@doc: docs/Gone.md"))
        output = self.run_checker()[1]
        self.assertIn("앵커 없음: docs/A.md#nope", output)
        self.assertIn("근거 문서 없음: docs/Gone.md", output)

    def test_reports_missing_coverage(self) -> None:
        self.write("src/bare.py", "def helper():\n    pass\n")
        output = self.run_checker()[1]
        self.assertIn("src/bare.py:1: 파일에 @doc 포인터 없음", output)
        self.assertIn("공개 심볼 helper에 @doc 포인터 없음", output)

    def test_reports_missing_back_pointers(self) -> None:
        self.write("docs/B.md", "# B\n\n[thing](../src/mod.py#Thing)\n")
        self.write("src/other.py", "'''@doc: docs/A.md'''\n")
        output = self.run_checker()[1]
        self.assertIn("src/mod.py:12: 역방향 포인터 없음: docs/B.md:3이 src/mod.py#Thing을 가리킴. Thing에 @doc: docs/B.md#b를 단다", output)
        self.assertIn("src/other.py:1: 받아 주는 문서 포인터 없음: docs/A.md가 src/other.py 또는 관련 심볼을", output)

    def test_suggested_back_pointer_uses_the_section_of_the_link(self) -> None:
        self.write("docs/B.md", "# B\n\n## 1. Intro\n\n## 2. Files\n\n[mod](../src/mod.py)\n")
        output = self.run_checker()[1]
        self.assertIn("src/mod.py:1: 역방향 포인터 없음: docs/B.md:7이 src/mod.py을 가리킴. 파일 머리에 @doc: docs/B.md#2-files를 단다", output)

    def test_document_pointer_problems_hold_back_code_side_checks(self) -> None:
        self.write("docs/B.md", "# B\n\n[gone](../src/mod.py#Gone) [thing](../src/mod.py#Thing)\n")
        self.write("src/bare.py", "def helper():\n    pass\n")
        code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn("구문 트리에 심볼 없음: ../src/mod.py#Gone", output)
        self.assertIn("문서→코드 포인터 문제 1건을 먼저 고친다", output)
        self.assertNotIn("역방향", output)
        self.assertNotIn("@doc 포인터 없음", output)

    def test_module_pointer_alone_does_not_back_a_symbol_pointer(self) -> None:
        self.write("docs/B.md", "# B\n\n[run](../src/mod.py#Thing.run) [file](../src/mod.py)\n")
        self.write("src/mod.py", _MODULE.replace("@doc: docs/A.md#1-spec", "@doc: docs/A.md#1-spec\n@doc: docs/B.md"))
        output = self.run_checker()[1]
        self.assertIn("src/mod.py:16: 역방향 포인터 없음: docs/B.md:3이 src/mod.py#Thing.run을 가리킴", output)
        self.assertNotIn("src/mod.py 또는", output)
        self.write("src/mod.py", _MODULE.replace("\'\'\'@doc: docs/A.md\'\'\'", "\'\'\'@doc: docs/A.md\n    @doc: docs/B.md\'\'\'"))
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_code_links_into_material_folders_are_not_pointers(self) -> None:
        self.write("legacy/old/app.py", "def run():\n    pass\n")
        self.write("reference/sample.rs", "fn main() {}\n")
        self.write("docs/A.md", _DOC + "[예전](../legacy/old/app.py#run) [예시](../reference/sample.rs#gone)\n")
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_non_python_repository_passes_and_reports(self) -> None:
        self.write("docs/A.md", "# A\n\n[parse](../src/lib.rs#Parser.parse) [mod](../src/lib.rs)\n")
        self.module.unlink()
        self.write(
            "src/lib.rs",
            "//! @doc: docs/A.md\n\n/// @doc: docs/A.md\npub struct Parser;\n\nimpl Parser {\n    fn parse() {}\n}\n",
        )
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)
        self.write("src/util.ts", "// @doc: docs/A.md\n\nexport function helper() {}\nfunction hidden() {}\n")
        output = self.run_checker()[1]
        self.assertIn("src/util.ts:3: 공개 심볼 helper에 @doc 포인터 없음", output)
        self.assertNotIn("hidden", output)


class ConfirmationTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#4-포인터-검사기"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/A.md", _DOC)
        self.write("docs/B.md", "# B\n\n## 1. Run\n\n[thing](../src/mod.py#Thing)\n")
        self.write("src/mod.py", _MODULE.replace("'''@doc: docs/A.md'''", "'''@doc: docs/A.md\n    @doc: docs/B.md'''"))
        self.write("docs/Ongoing.md", "# 진행 중\n\n없음\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def run_checker(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def test_committed_pointers_need_no_confirmation(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_document_pointer_that_followed_an_older_code_pointer_needs_confirmation(self) -> None:
        # The link to Thing.run is retargeted to Thing, which already named docs/A.md in HEAD.
        self.write("docs/A.md", _DOC.replace("#Thing.run", "#Thing"))
        code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn("docs/A.md:5: 포인터 확인 필요: src/mod.py#Thing의 @doc이 이 문서 포인터보다 먼저 있었음", output)
        self.assertIn("`- 포인터 확인: docs/A.md → src/mod.py#Thing: <이유>`", output)
        self.write("docs/Ongoing.md", "# 진행 중\n\n- 포인터 확인: docs/A.md → src/mod.py#Thing:\n")
        self.assertEqual(self.run_checker()[0], 1)
        self.write("docs/Ongoing.md", "# 진행 중\n\n- 포인터 확인: docs/A.md → src/mod.py#Thing: 1절은 클래스 전체를 말한다\n")
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_pointers_added_with_their_code_pointer_need_no_confirmation(self) -> None:
        self.write("docs/B.md", "# B\n\n## 1. Run\n\n[thing](../src/mod.py#Thing) [extra](../src/mod.py#extra)\n")
        self.write("src/mod.py", _MODULE.replace("'''@doc: docs/A.md'''", "'''@doc: docs/A.md\n    @doc: docs/B.md'''") + "\n\ndef extra():\n    '''@doc: docs/B.md'''\n")
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_module_pointer_does_not_count_for_a_symbol(self) -> None:
        # Only the file header pointed to docs/C.md in HEAD, so the new pointer to Thing.run followed no code pointer.
        module = (self.root / "src/mod.py").read_text(encoding="utf-8").replace("@doc: docs/A.md#1-spec", "@doc: docs/A.md#1-spec\n@doc: docs/C.md")
        self.write("docs/C.md", "# C\n\n[mod](../src/mod.py)\n")
        self.write("src/mod.py", module)
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
        self.write("docs/C.md", "# C\n\n[mod](../src/mod.py) [run](../src/mod.py#Thing.run)\n")
        self.write("src/mod.py", module.replace("    def run(self):", "    def run(self):\n        '''@doc: docs/C.md'''"))
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_skips_outside_git(self) -> None:
        self.git("update-ref", "-d", "HEAD")
        self.write("docs/A.md", _DOC.replace("#Thing.run", "#Thing"))
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)


class StubTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/A.md", "# A\n\n[run](../src/mod.rs#run)\n")
        self.write("docs/Roadmap.md", "# R\n\n## M0 a\n\n- [~] M0-T1 a\n- [x] M0-T2 b\n- [ ] M0-T3 c\n")
        self.write("docs/Issue.md", "# I\n\n- [~] I1 linked\n  - 연결 작업: M0-T2\n")

    def stub(self, task: str) -> str:
        self.write("src/mod.rs", f"//! @doc: docs/A.md\n\n/// @doc: docs/A.md\n/// @stub: {task}\npub fn run() {{ todo!() }}\n")
        output = io.StringIO()
        with redirect_stdout(output):
            main(["--root", str(self.root)])
        return output.getvalue()

    def test_stub_of_task_in_progress_passes(self) -> None:
        self.assertIn("목업 1개", self.stub("M0-T1"))

    def test_reports_stub_of_finished_unstarted_or_unknown_task(self) -> None:
        self.assertIn("src/mod.rs:4: 작업 M0-T2가 진행 중([~])이 아닌데 목업이 남아 있음", self.stub("M0-T2"))
        self.assertIn("작업 M0-T3가 진행 중([~])이 아닌데 목업이 남아 있음", self.stub("M0-T3"))
        self.assertIn("목업의 작업 M9-T9가 로드맵·이슈에 없음", self.stub("M9-T9"))

    def test_linked_issue_follows_its_linked_task(self) -> None:
        self.assertIn("작업 I1가 진행 중([~])이 아닌데 목업이 남아 있음", self.stub("I1"))


class SymbolRefTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_related_means_same_ancestor_or_descendant(self) -> None:
        def ref(name: str, file: str = "a.py") -> SymbolRef:
            return SymbolRef(Path(file), name)

        self.assertTrue(ref("A").is_related(ref("A.b")))
        self.assertTrue(ref("A.b").is_related(ref("")))
        self.assertFalse(ref("A").is_related(ref("AB")))
        self.assertFalse(ref("A").is_related(ref("A", "b.py")))


if __name__ == "__main__":
    unittest.main()
