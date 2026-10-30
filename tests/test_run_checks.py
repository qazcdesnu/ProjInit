"""Tests for running every check at once and the Stop hook response.

@doc: docs/design/Checkers.md#5-테스트
"""

import json
import unittest

from tests.support import RepoTestCase
from projinit.config import load_project

from projinit.run_checks import CHECKS, CheckResult, run_all, stop_hook_response, summarize

_PASS = CheckResult("check_docs", 0, "check_docs: 통과\n")
_FAIL = CheckResult("check_pointers", 1, "".join(f"line {n}\n" for n in range(100)))


class RunChecksTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_runs_every_checker_and_the_tests(self) -> None:
        self.assertEqual(
            [name for name, _ in CHECKS],
            ["check_docs", "check_pointers", "check_tasks", "check_hooks", "check_commits", "check_template"],
        )

    def test_passing_checks_let_claude_stop(self) -> None:
        self.assertEqual(stop_hook_response([_PASS], stop_hook_active=False).exit_code, 0)

    def test_first_failure_blocks_with_summary(self) -> None:
        response = stop_hook_response([_PASS, _FAIL], stop_hook_active=False)
        self.assertEqual(response.exit_code, 2)
        self.assertIn("[check_pointers] 실패", response.stderr)
        self.assertIn("사용자에게 보고", response.stderr)
        self.assertNotIn("check_docs", response.stderr)

    def test_repeated_stop_is_allowed_with_a_warning(self) -> None:
        response = stop_hook_response([_FAIL], stop_hook_active=True)
        self.assertEqual(response.exit_code, 0)
        self.assertIn("check_pointers", json.loads(response.stdout)["systemMessage"])

    def test_summary_keeps_only_the_tail(self) -> None:
        summary = summarize([_FAIL])
        self.assertIn("line 99", summary)
        self.assertNotIn("line 59\n", summary)
        self.assertIn("line 60", summary)



class ProjectCommandsTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_runs_the_configured_commands_after_the_checkers(self) -> None:
        self.write("projinit.toml", '[check]\ncommands = ["echo hi", "exit 3"]\n')
        results = run_all(load_project(self.root))
        self.assertEqual([result.name for result in results][len(CHECKS) :], ["echo hi", "exit 3"])
        self.assertEqual((results[-2].returncode, results[-2].output), (0, "hi\n"))
        self.assertEqual(results[-1].returncode, 3)


if __name__ == "__main__":
    unittest.main()
