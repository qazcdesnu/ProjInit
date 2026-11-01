"""Tests for the material folder checker.

@doc: docs/design/Checkers.md#15-자료-폴더-검사기
"""

import subprocess
import unittest

from tests.support import RepoTestCase
from projinit.check_materials import check_legacy_frozen, check_listed, check_nested_git, unlisted_files
from projinit.config import load_project


class ListedTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#15-자료-폴더-검사기"""

    def test_passes_without_material_folders(self) -> None:
        self.assertEqual(check_listed(load_project(self.root)), [])

    def test_reference_needs_no_list(self) -> None:
        self.write("reference/paper.pdf", "x")
        self.write("reference/spec.txt", "x")
        self.assertEqual(check_listed(load_project(self.root)), [])
        self.write("docs/Reference.md", "# R\n\n[논문](../reference/paper.pdf)\n")
        self.assertEqual(check_listed(load_project(self.root)), [])

    def test_reports_missing_legacy_list_document(self) -> None:
        main = self.write("legacy/old-app/main.py", "x")
        problems = check_listed(load_project(self.root))
        self.assertEqual([(problem.path, problem.message) for problem in problems], [(main, "목록 문서 없음: docs/Legacy.md")])

    def test_reports_unlisted_legacy_file(self) -> None:
        self.write("legacy/a/main.py", "x")
        other = self.write("legacy/b/main.py", "x")
        self.write("docs/Legacy.md", "# L\n\n[a](../legacy/a/)\n")
        self.assertEqual([problem.path for problem in check_listed(load_project(self.root))], [other])

    def test_unlisted_files(self) -> None:
        paper = self.write("reference/paper.pdf", "x")
        spec = self.write("reference/api/spec.txt", "x")
        list_doc = self.root / "docs/Reference.md"
        self.assertEqual(unlisted_files(self.root / "reference", list_doc), [spec, paper])
        self.write("docs/Reference.md", "# R\n\n[API](../reference/api/)\n")
        self.assertEqual(unlisted_files(self.root / "reference", list_doc), [paper])

    def test_folder_link_covers_its_files(self) -> None:
        self.write("legacy/old-app/src/main.py", "print(1)\n")
        self.write("legacy/old-app/README.md", "# old\n")
        self.write("docs/Legacy.md", "# L\n\n[예전 앱](../legacy/old-app/)\n")
        self.assertEqual(check_listed(load_project(self.root)), [])

    def test_honours_configured_folders(self) -> None:
        self.write("projinit.toml", '[paths]\nlegacy = "old"\n')
        notes = self.write("old/app/notes.txt", "x")
        self.write("legacy/ignored.txt", "x")
        self.assertEqual([problem.path for problem in check_listed(load_project(self.root))], [notes])


class LegacyFrozenTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#15-자료-폴더-검사기"""

    def setUp(self) -> None:
        super().setUp()
        self.main = self.write("legacy/old-app/main.py", "print(1)\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def paths(self) -> list[str]:
        return [problem.path.relative_to(self.root).as_posix() for problem in check_legacy_frozen(load_project(self.root))]

    def test_passes_when_unchanged(self) -> None:
        self.assertEqual(self.paths(), [])

    def test_reports_edit_delete_and_new_file(self) -> None:
        self.main.write_text("print(2)\n", encoding="utf-8")
        self.write("legacy/old-app/extra.py", "x\n")
        self.assertEqual(sorted(self.paths()), ["legacy/old-app/extra.py", "legacy/old-app/main.py"])
        self.main.unlink()
        self.git("add", "-A")
        self.assertEqual(sorted(self.paths()), ["legacy/old-app/extra.py", "legacy/old-app/main.py"])

    def test_allows_a_new_legacy_project(self) -> None:
        self.write("legacy/other-app/main.py", "x\n")
        self.assertEqual(self.paths(), [])

    def test_skips_a_folder_without_git(self) -> None:
        self.git("update-ref", "-d", "HEAD")
        self.main.write_text("print(2)\n", encoding="utf-8")
        self.assertEqual(self.paths(), [])


class NestedGitTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#15-자료-폴더-검사기"""

    def test_reports_nested_git(self) -> None:
        nested = self.write("legacy/old-app/.git/HEAD", "ref: refs/heads/main\n").parent
        self.assertEqual([problem.path for problem in check_nested_git(load_project(self.root))], [nested])

    def test_ignores_git_files_in_list_check(self) -> None:
        self.write("legacy/old-app/.git/HEAD", "x\n")
        self.write("legacy/old-app/main.py", "x\n")
        self.write("docs/Legacy.md", "# L\n\n[앱](../legacy/old-app/main.py)\n")
        self.assertEqual(check_listed(load_project(self.root)), [])


if __name__ == "__main__":
    unittest.main()
