"""Tests for the projinit upgrade command.

@doc: docs/design/Templates.md#10-갱신-명령
"""

import io
import subprocess
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit.config import load_config
from projinit.init import init_project, package_version
from projinit.upgrade import NEXT_STEP, main, set_version


class UpgradeTest(RepoTestCase):
    """@doc: docs/design/Templates.md#10-갱신-명령"""

    def setUp(self) -> None:
        super().setUp()
        init_project(self.root, "git@github.com:me/demo.git")
        config = self.root / "projinit.toml"
        config.write_text(config.read_text().replace(f'version = "{package_version()}"', 'version = "0.0.9"'))
        self.write("docs/CodeRule.md", "이전 버전의 규칙\n")
        self.commit_all()

    def commit_all(self) -> None:
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null"]
        subprocess.run([*git, "add", "-A"], cwd=self.root, check=True)
        subprocess.run([*git, "commit", "-q", "-m", "M0-T1: 이전 버전"], cwd=self.root, check=True)

    def run_main(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def test_moves_an_older_project_to_the_running_version(self) -> None:
        code, output = self.run_main()
        self.assertEqual(code, 0, output)
        self.assertIn(f"upgrade: 0.0.9 → {package_version()}", output)
        self.assertIn("바뀜: docs/CodeRule.md", output)
        self.assertTrue(output.rstrip().endswith(NEXT_STEP))
        config = load_config(self.root)
        self.assertEqual((config.version, config.template_values), (package_version(), {"repository": "git@github.com:me/demo.git"}))
        self.assertNotEqual((self.root / "docs/CodeRule.md").read_text(), "이전 버전의 규칙\n")

    def test_refuses_with_uncommitted_changes(self) -> None:
        self.write("docs/Roadmap.md", "작업 중\n")
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("upgrade: 커밋하지 않은 변경이 있다", output)
        self.assertEqual(load_config(self.root).version, "0.0.9")

    def test_refuses_when_a_command_is_set(self) -> None:
        config = self.root / "projinit.toml"
        config.write_text(config.read_text().replace("[projinit]\n", '[projinit]\ncommand = "uv run projinit"\n'))
        self.commit_all()
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("실행 명령(projinit.command)이 있어", output)

    def test_set_version_keeps_other_lines(self) -> None:
        text = '# 설정\n[projinit]\nsource = "s"\nversion = "0.1.0"\n\n[check]\nversion = "x"\n'
        self.assertEqual(set_version(text, "0.2.0"), '# 설정\n[projinit]\nsource = "s"\nversion = "0.2.0"\n\n[check]\nversion = "x"\n')
        self.assertEqual(set_version('[projinit]\nsource = "s"\n', "0.2.0"), '[projinit]\nversion = "0.2.0"\nsource = "s"\n')
