"""Tests for the hook installation checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import json
import subprocess

from tests.support import RepoTestCase
from tools.check_hooks import (
    COMMIT_MSG_COMMAND,
    HOOKS_PATH,
    PRE_COMMIT_COMMAND,
    STOP_HOOK_COMMAND,
    check_commit_msg_hook,
    check_hooks_path,
    check_pre_commit,
    check_stop_hook,
)


class CheckHooksTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write_settings({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": STOP_HOOK_COMMAND}]}]}})
        hook = self.write(".githooks/pre-commit", f"#!/bin/sh\nexec {PRE_COMMIT_COMMAND}\n")
        hook.chmod(0o755)
        self.write(".githooks/commit-msg", f"#!/bin/sh\nexec {COMMIT_MSG_COMMAND}\n").chmod(0o755)
        self.git("init", "-q")
        self.git("config", "core.hooksPath", HOOKS_PATH)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def write_settings(self, settings: object) -> None:
        self.write(".claude/settings.json", json.dumps(settings))

    def messages(self) -> list[str]:
        problems = (
            check_stop_hook(self.root)
            + check_pre_commit(self.root)
            + check_commit_msg_hook(self.root)
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
        self.assertIn(f"Stop hook에 검사 명령 없음: {STOP_HOOK_COMMAND}", self.messages())

    def test_reports_pre_commit_problems(self) -> None:
        hook = self.root / ".githooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 0\n")
        hook.chmod(0o644)
        messages = self.messages()
        self.assertIn("pre-commit hook에 실행 권한 없음", messages)
        self.assertIn(f"pre-commit hook에 검사 명령 없음: {PRE_COMMIT_COMMAND}", messages)
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
