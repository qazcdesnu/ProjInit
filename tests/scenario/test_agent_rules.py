"""Scenarios that break the agent rules in a project that also uses Codex.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import json
import subprocess
import unittest

from projinit.config import load_project
from projinit.init import refresh_common
from tests.scenario.project import ScenarioCase, baseline

_FEATURE = "docs/design/Feature.md"


class CodexRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.replace("projinit.toml", 'agents = ["claude"]', 'agents = ["claude", "codex"]')
        refresh_common(load_project(self.root))

    def codex_hook(self, event: str, stdin: str) -> tuple[int, str, str]:
        """Run a hook command from .codex/hooks.json the way Codex does: from the session folder, here src/."""
        command = json.loads(self.read(".codex/hooks.json"))["hooks"][event][0]["hooks"][0]["command"]
        done = subprocess.run(command, shell=True, cwd=self.root / "src", capture_output=True, text=True, input=stdin)
        return done.returncode, done.stdout, done.stderr

    def test_codex_project_is_clean(self) -> None:
        self.assert_clean()
        for relative in ("AGENTS.md", ".codex/hooks.json", ".agents/skills/start/SKILL.md", ".claude/settings.json"):
            self.assertTrue((self.root / relative).is_file(), relative)
        self.assertIn("AGENTS.md에서 문서를 읽는 순서를 확인", self.read(".agents/skills/start/SKILL.md"))

    def test_codex_stop_hook_removed(self) -> None:
        hooks = json.loads(self.read(".codex/hooks.json"))
        del hooks["hooks"]["Stop"]
        self.write(".codex/hooks.json", json.dumps(hooks))
        self.assert_caught("check_hooks", "Codex Stop hook에 명령 없음")

    def test_codex_hooks_file_removed(self) -> None:
        self.remove(".codex/hooks.json")
        self.assert_caught("check_hooks", "Codex hook 설정 없음: .codex/hooks.json")
        self.assert_caught("check_template", ".codex/hooks.json:1: 공통 파일 없음")

    def test_codex_entry_edited_by_hand(self) -> None:
        self.append("AGENTS.md", "- 손으로 더한 규칙 [인덱스](docs/index.md)\n")
        self.assert_caught("check_template", "AGENTS.md:1: 템플릿과 다름")

    def test_codex_entry_with_inline_code(self) -> None:
        self.append("AGENTS.md", "- `x` [a](docs/index.md)\n")
        self.assert_caught("check_docs", "AGENTS.md:15: 진입 문서에 인라인 코드를 쓸 수 없음")

    def test_codex_stop_hook_lets_a_clean_turn_end_with_json(self) -> None:
        code, stdout, stderr = self.codex_hook("Stop", '{"stop_hook_active": false}')
        self.assertEqual(code, 0, stderr)
        self.assertEqual(json.loads(stdout), {})

    def test_codex_stop_hook_blocks_then_allows(self) -> None:
        self.append(_FEATURE, "\n[x](Nope.md)\n")
        code, _, stderr = self.codex_hook("Stop", '{"stop_hook_active": false}')
        self.assertEqual(code, 2)
        self.assertIn("링크 대상 없음: Nope.md", stderr)
        code, stdout, stderr = self.codex_hook("Stop", '{"stop_hook_active": true}')
        self.assertEqual(code, 0, stderr)
        self.assertIn("check_docs", json.loads(stdout)["systemMessage"])

    def test_codex_session_start_hook_names_the_materials(self) -> None:
        code, stdout, stderr = self.codex_hook("SessionStart", '{"source": "startup"}')
        self.assertEqual(code, 0, stderr)
        self.assertIn("- reference/notes.md", stdout)

    def test_claude_files_stay_the_same_when_codex_is_on(self) -> None:
        for relative in ("CLAUDE.md", ".claude/settings.json", ".claude/commands/start.md"):
            self.assertEqual(self.read(relative), (baseline() / relative).read_text(encoding="utf-8"), relative)


if __name__ == "__main__":
    unittest.main()
