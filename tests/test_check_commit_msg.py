"""Tests for the commit message checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import unittest

from projinit.check_commit_msg import check_message

_KNOWN = {"M0-T6", "M0-T8", "I1", "H2"}


class CheckMessageTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_valid_subjects_pass(self) -> None:
        for subject in ("M0-T6: 요약", "M0-T8, I1, H2: 여러 작업", "I1(진행 중): 목업", "M0-T6: 요약\n\n본문 M9-T9"):
            self.assertEqual(check_message(subject, _KNOWN), [], subject)

    def test_git_generated_subjects_pass(self) -> None:
        for subject in ("Merge branch 'x'", 'Revert "M0-T6: 요약"', "fixup! M0-T6: 요약", "squash! x"):
            self.assertEqual(check_message(subject, _KNOWN), [], subject)

    def test_skips_comment_lines(self) -> None:
        self.assertEqual(check_message("# git 주석\n\nM0-T6: 요약\n# 주석\n", _KNOWN), [])

    def test_reports_malformed_subjects(self) -> None:
        for subject in ("요약만 있음", "M0-T6:요약", "M0-T6: ", ", M0-T6: 요약", "M0-T6 (진행 중): 요약"):
            problems = check_message(subject, _KNOWN)
            self.assertEqual(len(problems), 1, subject)
        self.assertTrue(check_message("요약만 있음", _KNOWN)[0].startswith("제목은"))

    def test_reports_unknown_ids(self) -> None:
        self.assertEqual(check_message("M0-T6, M9-T9: 요약", _KNOWN), ["로드맵·이슈에 없는 작업 ID: M9-T9"])

    def test_reports_empty_message(self) -> None:
        self.assertEqual(check_message("# 주석만\n\n", _KNOWN), ["제목이 없음"])


if __name__ == "__main__":
    unittest.main()
