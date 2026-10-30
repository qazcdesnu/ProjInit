"""Tests for the projinit init command.

@doc: docs/design/Templates.md#9-초기화-명령
"""

import io
import os
import subprocess
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit.run_checks import run_all
from projinit.config import load_config, load_project
from projinit.init import NO_REPOSITORY, START_HINT, init_project, main, package_version, refresh_common, repository_url
from projinit.template import COMMON_FILES, EXECUTABLE_FILES, INITIAL_FILES


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
        hooks_path = subprocess.run(["git", "config", "core.hooksPath"], cwd=target, capture_output=True, text=True)
        self.assertEqual(hooks_path.stdout.strip(), ".githooks")
        for relative in EXECUTABLE_FILES:
            self.assertTrue(os.access(target / relative, os.X_OK), relative)
        results = run_all(load_project(target))
        self.assertEqual([(r.name, r.returncode) for r in results if r.returncode], [], [r.output for r in results])

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
        code, output = self.run_main()
        self.assertEqual((code, output.splitlines()[-1]), (0, START_HINT))
        self.write("docs/CodeRule.md", "손으로 고침\n")
        self.write("docs/Roadmap.md", self.root.joinpath("docs/Roadmap.md").read_text() + "- [ ] M0-T2 더함\n")
        self.assertEqual(refresh_common(load_project(self.root)), ["docs/CodeRule.md"])
        self.assertNotEqual((self.root / "docs/CodeRule.md").read_text(), "손으로 고침\n")
        self.assertIn("M0-T2 더함", (self.root / "docs/Roadmap.md").read_text())
        self.assertTrue((self.root / ".claude/commands/start.md").is_file())
        code, output = self.run_main("--refresh-common")
        self.assertEqual((code, output.splitlines()[-1]), (0, "init: 공통 문서 0개를 다시 씀"))
