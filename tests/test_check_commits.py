"""Tests for the commit message, branch name and pull request title checker.

@doc: docs/design/Checkers.md#5-테스트
"""

import io
import subprocess
import unittest
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit.check_commits import check_branch, check_message, main

_STATUSES = {"M0-T6": "x", "M0-T8": "~", "I1": "x", "H2": "~", "I9": " "}


class CheckMessageTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def problems(self, message: str, require_started: bool = True, is_pr_title: bool = False) -> list[str]:
        return check_message(message, _STATUSES, require_started, is_pr_title)

    def test_valid_messages_pass(self) -> None:
        for message in (
            "M0-T6: 요약",
            "M0-T8, I1, H2: 여러 작업",
            "M0-T8(진행 중): 목업",
            "# git 주석\n\nM0-T6: 요약\n\n본문 M9-T9\n\nCo-Authored-By: A <a@b>\n# 주석\n",
        ):
            self.assertEqual(self.problems(message), [], message)

    def test_git_generated_subjects_pass(self) -> None:
        for subject in ("Merge branch 'x'", 'Revert "M0-T6: 요약"', "fixup! M0-T6: 요약", "squash! x"):
            self.assertEqual(self.problems(subject), [], subject)

    def test_reports_format_problems(self) -> None:
        self.assertEqual(self.problems("# 주석만\n\n"), ["빈 커밋 메시지"])
        for subject in ("요약만 있음", "M0-T6:요약", ", M0-T6: 요약", "M0-T6 (진행 중): 요약", "M0: 요약"):
            self.assertTrue(self.problems(subject)[0].startswith("제목 형식 오류"), subject)
        self.assertEqual(self.problems("M0-T6: 요약."), ["요약은 마침표로 끝내지 않음"])
        self.assertEqual(self.problems("M0-T6: 요약\n본문"), ["제목 다음 줄은 비어 있어야 함"])
        self.assertEqual(self.problems("M0-T6, M0-T6: 요약"), ["제목에 같은 작업 ID가 반복됨: M0-T6"])
        self.assertEqual(self.problems("M0-T6: " + "가" * 70), ["제목 줄이 72자를 넘음 (77자)"])

    def test_reports_unknown_and_unstarted_ids(self) -> None:
        self.assertEqual(self.problems("M0-T6, M9-T9: 요약"), ["로드맵·이슈에 없는 작업 ID: M9-T9"])
        self.assertEqual(self.problems("I9: 요약"), ["시작하지 않은 작업([ ])의 ID: I9"])
        self.assertEqual(self.problems("I9: 요약", require_started=False), [])

    def test_pull_request_title_cannot_be_in_progress(self) -> None:
        self.assertEqual(self.problems("M0-T8(진행 중): 요약", is_pr_title=True), ["PR 제목에는 (진행 중)를 붙이지 않음"])

    def test_branch_names(self) -> None:
        self.assertEqual(check_branch("m0-t6-commit-rule", _STATUSES), [])
        self.assertEqual(check_branch("i1-x2", _STATUSES), [])
        self.assertTrue(check_branch("feature/x", _STATUSES)[0].startswith("브랜치 이름 형식 오류"))
        self.assertTrue(check_branch("M0-T6-upper", _STATUSES)[0].startswith("브랜치 이름 형식 오류"))
        self.assertEqual(check_branch("i7-gone", _STATUSES), ["로드맵·이슈에 없는 작업 ID의 브랜치: I7"])


class CheckCommitsCommandTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/Roadmap.md", "# R\n\n## M0 a\n\n- [x] M0-T1 a\n- [ ] M0-T2 b\n")
        self.write("docs/Issue.md", "# I\n")
        self.git("init", "-q", "-b", "main")
        self.base = self.commit("M0-T1: 첫 커밋")

    def git(self, *args: str) -> str:
        command = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args]
        return subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, message: str) -> str:
        self.write("change.txt", message)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "--short", "HEAD")

    def run_main(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), *args])
        return code, output.getvalue()

    def test_history_after_baseline_skipping_merges(self) -> None:
        bad = self.commit("규칙 없는 커밋")
        self.write("projinit.toml", f'[check]\ncommit_baseline = "{bad}"\n')
        self.commit("M0-T2: 시작 전 작업도 이력 검사에서는 존재만 본다")
        self.git("switch", "-q", "-c", "m0-t1-side")
        self.commit("M0-T1: 옆 브랜치")
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "아무 병합 메시지", "m0-t1-side")
        code, output = self.run_main()
        self.assertEqual(code, 0, output)
        self.assertIn("커밋 2개", output)
        self.write("projinit.toml", "")
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn(f"commit {bad}:1: 제목 형식 오류", output)

    def test_message_file_and_pull_request_modes(self) -> None:
        message = self.write("msg.txt", "M0-T2: 시작하지 않은 작업\n")
        code, output = self.run_main("--message-file", str(message))
        self.assertEqual(code, 1)
        self.assertIn("시작하지 않은 작업([ ])의 ID: M0-T2", output)
        code, output = self.run_main("--subject", "M0-T1: 요약", "--branch", "m0-t1-x")
        self.assertEqual(code, 0, output)
        code, output = self.run_main("--subject", "M0-T1(진행 중): 요약", "--branch", "bad")
        self.assertIn("PR:1: PR 제목: PR 제목에는 (진행 중)를 붙이지 않음", output)
        self.assertIn("PR:1: 브랜치 이름 형식 오류", output)


if __name__ == "__main__":
    unittest.main()
