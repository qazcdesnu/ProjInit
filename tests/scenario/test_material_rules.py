"""Scenarios that break the material rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import unittest

from tests.scenario.project import ScenarioCase

_LEGACY_ITEM = "- [예전 앱](../legacy/old/): 예전 구현.\n"


class MaterialRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def test_unlisted_legacy_project(self) -> None:
        self.write("legacy/other/x.py", "x\n")
        self.assert_caught("check_materials", "목록 문서에 없는 자료: docs/Legacy.md에 링크 필요")

    def test_legacy_without_list(self) -> None:
        self.remove("docs/Legacy.md")
        self.assert_caught("check_materials", "목록 문서 없음: docs/Legacy.md")

    def test_changed_legacy_file(self) -> None:
        self.append("legacy/old/main.py", "print('new')\n")
        self.assert_caught("check_materials", "legacy/old/main.py:1: 커밋된 기존 프로젝트를 바꿈")

    def test_removed_legacy_file(self) -> None:
        self.remove("legacy/old/main.py")
        self.assert_caught("check_materials", "커밋된 기존 프로젝트를 바꿈")

    def test_new_file_in_committed_legacy_project(self) -> None:
        self.write("legacy/old/new.py", "x\n")
        self.assert_caught("check_materials", "legacy/old/new.py:1: 커밋된 기존 프로젝트를 바꿈")

    def test_staged_legacy_change(self) -> None:
        self.append("legacy/old/main.py", "print('new')\n")
        self.git("add", "legacy/old/main.py")
        self.assert_caught("check_materials", "커밋된 기존 프로젝트를 바꿈")

    def test_nested_git_in_legacy(self) -> None:
        self.write("legacy/new/a.py", "x\n")
        (self.root / "legacy/new/.git").mkdir()
        self.replace("docs/Legacy.md", _LEGACY_ITEM, _LEGACY_ITEM + "- [새](../legacy/new/): 새.\n")
        self.assert_caught("check_materials", "기존 프로젝트 안의 .git: 빼고 넣는다")

    def test_private_without_ignore_line(self) -> None:
        self.write(".gitignore", "node_modules/\n")
        self.assert_caught("check_materials", "로컬 자료가 git에서 빠지지 않음: .gitignore에 /private/를 더한다")

    def test_force_staged_private_file(self) -> None:
        self.git("add", "-f", "private/secret.txt")
        self.assert_caught("check_materials", "로컬 자료가 git에 추적됨")

    def test_private_file_with_space_in_name(self) -> None:
        self.write(".gitignore", "")
        self.write("private/my secret.txt", "x")
        self.assert_caught("check_materials", "로컬 자료가 git에서 빠지지 않음")

    def test_reference_without_list_passes(self) -> None:
        self.write("reference/new.pdf", "x")
        self.assert_clean()

    def test_new_listed_legacy_project_passes(self) -> None:
        self.write("legacy/new/a.py", "x\n")
        self.replace("docs/Legacy.md", _LEGACY_ITEM, _LEGACY_ITEM + "- [새](../legacy/new/): 새.\n")
        self.assert_clean()

    def test_session_context_names_reference_and_private(self) -> None:
        code, output = self.projinit("context")
        self.assertEqual(code, 0, output)
        self.assertIn("- reference/notes.md", output)
        self.assertIn("로컬 자료: private/에 자료 1개가 있다.", output)
        self.assertIn("- private/secret.txt", output)


if __name__ == "__main__":
    unittest.main()
