"""Scenarios that break the commit rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import json
import unittest

from tests.scenario.project import ScenarioCase


class CommitRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def commit_msg(self, message: str) -> tuple[int, str]:
        self.write(".git/MSG", message)
        return self.projinit("commit-msg", ".git/MSG")

    def assert_message_refused(self, message: str, needle: str) -> None:
        code, output = self.commit_msg(message)
        self.assertNotEqual(code, 0, output)
        self.assertIn(needle, output)

    def assert_message_accepted(self, message: str) -> None:
        code, output = self.commit_msg(message)
        self.assertEqual(code, 0, output)

    def test_messages_that_are_refused(self) -> None:
        cases = [
            ("그냥 고침\n", "제목 형식 오류"),
            ("I99: 고침\n", "로드맵·이슈에 없는 작업 ID: I99"),
            ("I2: 고침.\n", "요약은 마침표로 끝내지 않음"),
            ("I2: " + "가" * 80 + "\n", "자를 넘음"),
            ("I2, I2: 고침\n", "제목에 같은 작업 ID가 반복됨: I2"),
            ("I2: 고침\n본문\n", "제목 다음 줄은 비어 있어야 함"),
            ("# 주석만\n", "빈 커밋 메시지"),
            ("I2:고침\n", "제목 형식 오류"),
            ("I1-I2: 고침\n", "제목 형식 오류"),
        ]
        for message, needle in cases:
            with self.subTest(message=message):
                self.assert_message_refused(message, needle)

    def test_messages_that_are_accepted(self) -> None:
        for message in ("I2(진행 중): 목업\n", "I1: 오타 고침\n", "Merge branch 'x'\n", "I2: 고침\n\n본문\n\nCo-Authored-By: t <t@t>\n"):
            with self.subTest(message=message):
                self.assert_message_accepted(message)

    def test_task_that_has_not_started(self) -> None:
        self.append("docs/Issue.md", "- [ ] I3 셋째\n  - 등록일: 2026-11-01\n")
        self.assert_message_refused("I3: 고침\n", "시작하지 않은 작업([ ])의 ID: I3")

    def test_history_catches_a_commit_that_skipped_the_hooks(self) -> None:
        self.write("docs/x.txt", "x")
        self.commit("아무 메시지", "--no-verify")
        self.assert_caught("check_commits", "제목 형식 오류")

    def test_pull_requests(self) -> None:
        cases = [
            ("I2(진행 중): x", "i2-later", "PR 제목에는 (진행 중)을 붙이지 않음"),
            ("I2: x", "feature/x", "브랜치 이름 형식 오류"),
            ("I2: x", "i99-x", "로드맵·이슈에 없는 작업 ID의 브랜치: I99"),
            ("나중 기능", "i2-later", "제목 형식 오류"),
        ]
        for subject, branch, needle in cases:
            with self.subTest(subject=subject, branch=branch):
                code, output = self.projinit("commits", "--subject", subject, "--branch", branch)
                self.assertNotEqual(code, 0, output)
                self.assertIn(needle, output)
        code, output = self.projinit("commits", "--subject", "I2: 나중 기능", "--branch", "i2-later")
        self.assertEqual(code, 0, output)

    def test_pull_request_of_a_task_that_has_not_started(self) -> None:
        self.append("docs/Issue.md", "- [ ] I3 셋째\n  - 등록일: 2026-11-01\n")
        code, output = self.projinit("commits", "--subject", "I3: x", "--branch", "i3-x")
        self.assertNotEqual(code, 0, output)
        self.assertIn("시작하지 않은 작업([ ])의 ID: I3", output)

    def open_pr_file(self, oid: str) -> None:
        self.write(".git/prs.json", json.dumps([{"number": 1, "headRefName": "i2-a", "headRefOid": oid}]))

    def first_pr(self) -> str:
        self.git("checkout", "-q", "-b", "i2-a")
        self.write("a.txt", "a")
        self.commit("I2(진행 중): a", "--no-verify")
        return self.git("rev-parse", "HEAD")[1].strip()

    def test_pull_request_that_skips_an_earlier_one(self) -> None:
        oid = self.first_pr()
        self.git("checkout", "-q", "main")
        self.git("checkout", "-q", "-b", "i2-b")
        self.open_pr_file(oid)
        code, output = self.projinit("pr-order", "--pr", "2", "--open-prs", ".git/prs.json")
        self.assertNotEqual(code, 0, output)
        self.assertIn("PR #1 (i2-a)를 포함하지 않음", output)

    def test_pull_request_stacked_on_an_earlier_one(self) -> None:
        oid = self.first_pr()
        self.git("checkout", "-q", "-b", "i2-b")
        self.open_pr_file(oid)
        code, output = self.projinit("pr-order", "--pr", "2", "--open-prs", ".git/prs.json")
        self.assertEqual(code, 0, output)

    def test_earlier_pull_request_missing_from_the_repository(self) -> None:
        self.open_pr_file("0" * 40)
        code, output = self.projinit("pr-order", "--pr", "2", "--open-prs", ".git/prs.json")
        self.assertNotEqual(code, 0, output)
        self.assertIn("PR #1 (i2-a)를 포함하지 않음", output)


if __name__ == "__main__":
    unittest.main()
