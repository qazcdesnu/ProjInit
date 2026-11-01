"""Scenarios that break the device rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import json
import unittest

from tests.scenario.project import ScenarioCase

_FEATURE = "docs/design/Feature.md"


class DeviceRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def drop_hook(self, event: str) -> None:
        settings = json.loads(self.read(".claude/settings.json"))
        del settings["hooks"][event]
        self.write(".claude/settings.json", json.dumps(settings))

    def test_stop_hook_removed(self) -> None:
        self.drop_hook("Stop")
        self.assert_caught("check_hooks", "Stop hook에 검사 명령 없음")

    def test_session_start_hook_removed(self) -> None:
        self.drop_hook("SessionStart")
        self.assert_caught("check_hooks", "SessionStart hook에 안내 명령 없음")

    def test_pre_commit_not_executable(self) -> None:
        (self.root / ".githooks/pre-commit").chmod(0o644)
        self.assert_caught("check_hooks", "pre-commit hook에 실행 권한 없음")

    def test_pre_commit_without_the_check(self) -> None:
        self.write(".githooks/pre-commit", "#!/bin/sh\nexit 0\n")
        (self.root / ".githooks/pre-commit").chmod(0o755)
        self.assert_caught("check_hooks", "pre-commit hook에 검사 명령 없음")

    def test_commit_msg_hook_removed(self) -> None:
        self.remove(".githooks/commit-msg")
        self.assert_caught("check_hooks", "commit-msg hook 없음")

    def test_hooks_path_unset(self) -> None:
        self.git("config", "--unset", "core.hooksPath")
        self.assert_caught("check_hooks", "git core.hooksPath가 .githooks가 아님")

    def test_settings_not_json(self) -> None:
        self.write(".claude/settings.json", "{oops")
        self.assert_caught("check_hooks", "JSON 형식 오류")

    def test_common_rule_edited_by_hand(self) -> None:
        self.append("docs/TaskRule.md", "\n손으로 더한 줄.\n")
        self.assert_caught("check_template", "docs/TaskRule.md:1: 템플릿과 다름")

    def test_device_file_edited_by_hand(self) -> None:
        self.append(".github/workflows/verify.yml", "\n# 손으로\n")
        self.assert_caught("check_template", ".github/workflows/verify.yml:1: 템플릿과 다름")

    def test_common_rule_removed(self) -> None:
        self.remove("docs/CommitRule.md")
        self.assert_caught("check_template", "docs/CommitRule.md:1: 공통 파일 없음")

    def test_failing_project_command(self) -> None:
        self.replace("projinit.toml", "commands = []", 'commands = ["false"]')
        code, output = self.projinit("check")
        self.assertEqual(code, 1, output)
        self.assertIn("[false] 실패 (종료 코드 1)", output)

    def test_pre_commit_blocks_a_real_commit(self) -> None:
        self.append(_FEATURE, "\n[x](Nope.md)\n")
        code, output = self.commit("I2(진행 중): 깨짐")
        self.assertNotEqual(code, 0, output)
        self.assertIn("링크 대상 없음: Nope.md", output)

    def test_commit_msg_blocks_a_real_commit(self) -> None:
        self.write("docs/x.txt", "x")
        code, output = self.commit("메시지 형식 틀림")
        self.assertNotEqual(code, 0, output)
        self.assertIn("제목 형식 오류", output)

    def test_clean_commit_passes(self) -> None:
        self.write("docs/x.txt", "x")
        code, output = self.commit("I2(진행 중): 정상")
        self.assertEqual(code, 0, output)

    def test_stop_hook_blocks_first(self) -> None:
        self.append(_FEATURE, "\n[x](Nope.md)\n")
        code, output = self.projinit("check", "--hook", "stop", stdin="{}")
        self.assertEqual(code, 2, output)
        self.assertIn("링크 대상 없음: Nope.md", output)

    def test_stop_hook_allows_after_blocking_once(self) -> None:
        self.append(_FEATURE, "\n[x](Nope.md)\n")
        code, output = self.projinit("check", "--hook", "stop", stdin='{"stop_hook_active": true}')
        self.assertEqual(code, 0, output)
        self.assertIn("systemMessage", output)

    def test_stop_hook_passes_when_clean(self) -> None:
        code, output = self.projinit("check", "--hook", "stop", stdin="{}")
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
