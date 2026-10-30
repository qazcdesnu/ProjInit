"""Tests for the projinit init command.

@doc: docs/design/Templates.md#9-초기화-명령
"""

import io
import subprocess
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit import check_docs, check_tasks
from projinit.config import load_config, load_project
from projinit.init import NO_REPOSITORY, init_project, main, package_version, refresh_common, repository_url
from projinit.template import COMMON_FILES, INITIAL_FILES


class InitTest(RepoTestCase):
    """@doc: docs/design/Templates.md#9-초기화-명령"""

    def run_main(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), *args])
        return code, output.getvalue()

    def test_initializes_an_empty_folder(self) -> None:
        target = self.root / "new"
        created = init_project(target, "git@github.com:me/demo.git")
        self.assertEqual(created, list(COMMON_FILES + INITIAL_FILES))
        self.assertTrue((target / ".git").is_dir())
        config = load_config(target)
        self.assertEqual((config.version, config.template_values), (package_version(), {"repository": "git@github.com:me/demo.git"}))
        # The pull request template is an enforcement file that M2-T3 installs.
        (target / ".github").mkdir()
        (target / ".github/pull_request_template.md").write_text("")
        for checker in (check_docs, check_tasks):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(checker.main(["--root", str(target)]), 0, output.getvalue())

    def test_repository_comes_from_argument_then_origin(self) -> None:
        self.assertEqual(repository_url(self.root, None), NO_REPOSITORY)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "git@example.com:o.git"], cwd=self.root, check=True)
        self.assertEqual(repository_url(self.root, None), "git@example.com:o.git")
        self.assertEqual(repository_url(self.root, "given"), "given")

    def test_refuses_when_a_file_exists_and_writes_nothing(self) -> None:
        self.write("docs/index.md", "# 내 인덱스\n")
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("init: 이미 있는 파일이 있어 초기화하지 않음: docs/index.md", output)
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.assertEqual((self.root / "docs/index.md").read_text(), "# 내 인덱스\n")

    def test_refresh_common_restores_common_files_only(self) -> None:
        self.assertEqual(self.run_main()[0], 0)
        self.write("docs/CodeRule.md", "손으로 고침\n")
        self.write("docs/Roadmap.md", self.root.joinpath("docs/Roadmap.md").read_text() + "- [ ] M0-T2 더함\n")
        self.assertEqual(refresh_common(load_project(self.root)), ["docs/CodeRule.md"])
        self.assertNotEqual((self.root / "docs/CodeRule.md").read_text(), "손으로 고침\n")
        self.assertIn("M0-T2 더함", (self.root / "docs/Roadmap.md").read_text())
        code, output = self.run_main("--refresh-common")
        self.assertEqual((code, output.splitlines()[-1]), (0, "init: 공통 문서 0개를 다시 씀"))
