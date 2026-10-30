"""Tests for the hook installation checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import json
import subprocess
import unittest

from tests.support import RepoTestCase
from projinit.check_hooks import (
    HOOKS_PATH,
    check_commit_msg_hook,
    check_hooks_path,
    check_pre_commit,
    check_stop_hook,
    hook_commands,
    projinit_command,
)
from projinit.config import Config, load_project

_COMMANDS = hook_commands(Config(command="uv run projinit"))


class HookCommandsTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_commands_come_from_the_settings(self) -> None:
        self.assertEqual(_COMMANDS.stop, 'cd "$CLAUDE_PROJECT_DIR" && uv run projinit check --hook stop')
        self.assertEqual(_COMMANDS.pre_commit, "uv run projinit check --hook pre-commit")
        self.assertEqual(_COMMANDS.commit_msg, 'uv run projinit commit-msg "$1"')

    def test_uvx_command_from_source_and_version(self) -> None:
        config = Config(source="git+https://example.com/ProjInit", version="0.1.0")
        self.assertEqual(projinit_command(config), "uvx --from git+https://example.com/ProjInit@v0.1.0 projinit")

    def test_no_command_without_settings(self) -> None:
        self.assertIsNone(hook_commands(Config()))
        self.assertIsNone(hook_commands(Config(source="git+https://example.com/ProjInit")))


class CheckHooksTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write_settings({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": _COMMANDS.stop}]}]}})
        hook = self.write(".githooks/pre-commit", f"#!/bin/sh\nexec {_COMMANDS.pre_commit}\n")
        hook.chmod(0o755)
        self.write(".githooks/commit-msg", f"#!/bin/sh\nexec {_COMMANDS.commit_msg}\n").chmod(0o755)
        self.git("init", "-q")
        self.git("config", "core.hooksPath", HOOKS_PATH)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def write_settings(self, settings: object) -> None:
        self.write(".claude/settings.json", json.dumps(settings))

    def messages(self) -> list[str]:
        project = load_project(self.root)
        problems = (
            check_stop_hook(project, _COMMANDS.stop)
            + check_pre_commit(project, _COMMANDS.pre_commit)
            + check_commit_msg_hook(project, _COMMANDS.commit_msg)
            + check_hooks_path(self.root)
        )
        return [problem.message for problem in problems]

    def test_installed_hooks_pass(self) -> None:
        self.assertEqual(self.messages(), [])

    def test_reports_stop_hook_problems(self) -> None:
        (self.root / ".claude/settings.json").unlink()
        self.assertIn("Claude Code 설정 없음: .claude/settings.json", self.messages())
        self.write(".claude/settings.json", "{not json")
        self.assertTrue(self.messages()[0].startswith("JSON 형식 오류"))
        self.write_settings({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "true"}]}]}})
        self.assertIn(f"Stop hook에 검사 명령 없음: {_COMMANDS.stop}", self.messages())

    def test_reports_pre_commit_problems(self) -> None:
        hook = self.root / ".githooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 0\n")
        hook.chmod(0o644)
        messages = self.messages()
        self.assertIn("pre-commit hook에 실행 권한 없음", messages)
        self.assertIn(f"pre-commit hook에 검사 명령 없음: {_COMMANDS.pre_commit}", messages)
        hook.unlink()
        self.assertIn("pre-commit hook 없음: .githooks/pre-commit", self.messages())

    def test_reports_missing_commit_msg_hook(self) -> None:
        (self.root / ".githooks/commit-msg").unlink()
        self.assertIn("commit-msg hook 없음: .githooks/commit-msg", self.messages())

    def test_reports_hooks_path_problems(self) -> None:
        self.git("config", "--unset", "core.hooksPath")
        self.assertTrue(any(message.startswith("git core.hooksPath가") for message in self.messages()))
        subprocess.run(["rm", "-rf", str(self.root / ".git")], check=True)
        self.assertIn("git 저장소가 아님", self.messages())
