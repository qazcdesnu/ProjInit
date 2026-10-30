"""Tests for running every check at once and the Stop hook response.

@doc: docs/VerificationTools.md#5-테스트
"""

import json
import unittest

from projinit.run_checks import CHECKS, CheckResult, stop_hook_response, summarize

_PASS = CheckResult("check_docs", 0, "check_docs: 통과\n")
_FAIL = CheckResult("check_pointers", 1, "".join(f"line {n}\n" for n in range(100)))


class RunChecksTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_runs_every_checker_and_the_tests(self) -> None:
        self.assertEqual(
            [name for name, _ in CHECKS],
            ["check_docs", "check_pointers", "check_tasks", "check_hooks", "unittest"],
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


if __name__ == "__main__":
    unittest.main()
