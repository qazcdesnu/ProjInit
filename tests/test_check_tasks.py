"""Tests for the task document consistency checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import subprocess
import unittest
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from tools.check_tasks import main

_ROADMAP = """# 로드맵

## M0 기반

- [x] M0-T1 첫 작업
- [~] M0-T2 둘째 작업

## M1 다음

- [ ] M1-T1 할 일
"""
_ISSUE = """# 이슈

- [x] I1 사용자 지시
  - 연결 작업: M0-T1
- [ ] I2 미정 문제
- [~] H1 급한 결함
"""
_ONGOING = """# 진행 중

## M0-T2 둘째 작업

- 시작일: 2026-10-31
- 관련 이슈: I2

### 계획
- 둘째 일을 한다.

### 진행 기록
- 2026-10-31: 시작했다.

### 결정 사항
- 방식 A로 한다.

## H1 급한 결함

- 시작일: 2026-10-31

### 계획
- 결함을 고친다.
"""
_DONE = """# 완료

## M0-T1 첫 작업

- 시작일: 2026-10-30
- 완료일: 2026-10-30

### 계획
- 첫 일을 한다.

### 진행 기록
- 2026-10-30: 했다.

### 결정 사항
- 없음

### 변경 파일
- `a.py`

### 결과
- 됨. I1을 함께 처리했다.

### 검증
- 통과
"""


_M0_T2_RECORD = _ONGOING[_ONGOING.index("## M0-T2") : _ONGOING.index("## H1")]


class _TaskDocsTestCase(RepoTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.write("docs/Roadmap.md", _ROADMAP)
        self.write("docs/Issue.md", _ISSUE)
        self.write("docs/Ongoing.md", _ONGOING)
        self.write("docs/Done.md", _DONE)

    def run_checker(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def assert_reports(self, *messages: str) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 1, output)
        for message in messages:
            self.assertIn(message, output)


class CheckTasksTest(_TaskDocsTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_consistent_documents_pass(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_malformed_lines(self) -> None:
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [ ] M1-T1", "- [?] M1-T1").replace("## M1 다음", "## 다음"))
        self.assert_reports("태스크 줄 형식 오류", "마일스톤 제목 형식 오류")

    def test_reports_numbering_gaps_and_wrong_milestone(self) -> None:
        roadmap = _ROADMAP.replace("M0-T2 둘째", "M0-T3 둘째").replace("M1-T1 할 일", "M0-T9 할 일")
        self.write("docs/Roadmap.md", roadmap)
        self.write("docs/Ongoing.md", _ONGOING.replace("M0-T2", "M0-T3"))
        self.write("docs/Issue.md", _ISSUE.replace("I2 미정", "I3 미정"))
        self.assert_reports(
            "태스크 번호 차례 오류: M0-T2이어야 함", "M0-T9가 M0 마일스톤 아래에 있지 않음", "이슈 번호 차례 오류: I2이어야 함"
        )

    def test_reports_status_without_matching_record(self) -> None:
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [ ] M1-T1", "- [x] M1-T1"))
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1", "- [ ] H1"))
        self.assert_reports("M1-T1: 상태 [x]인데 완료 기록 없음", "H1: 상태 [ ]인데 진행 중 기록 있음")

    def test_reports_record_for_unknown_id(self) -> None:
        self.write("docs/Done.md", _DONE + "\n## M5-T1 유령\n\n- 시작일: 2026-10-29\n- 완료일: 2026-10-29\n\n### 결과\n### 검증\n")
        self.assert_reports("로드맵·이슈에 없는 작업의 기록: M5-T1")

    def test_reports_linked_issue_problems(self) -> None:
        self.write("docs/Issue.md", _ISSUE.replace("- [x] I1", "- [~] I1").replace("- [ ] I2 미정 문제", "- [ ] I2 미정 문제\n  - 연결 작업: M9-T1"))
        self.assert_reports("I1: 상태 [~]가 연결 작업 M0-T1의 [x]와 다름", "I2: 연결 작업 M9-T1가 없음")

    def test_reports_missing_fields_sections_and_order(self) -> None:
        older = "## M0-T9 x\n\n- 시작일: 2026-10-01\n- 완료일: 2026-10-01\n\n### 결과\n### 검증\n\n"
        done = _DONE.replace("## M0-T1", older + "## M0-T1").replace("### 검증\n- 통과\n", "")
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2", "- [x] M0-T9 x\n- [~] M0-T2"))
        self.write("docs/Done.md", done)
        self.write("docs/Ongoing.md", _ONGOING.replace("- 시작일: 2026-10-31\n- 관련", "- 관련"))
        self.assert_reports("M0-T1: '검증' 절 없음", "M0-T1: 완료 기록은 완료일이 늦은 것부터", "M0-T2: '시작일' 필드 없음")

    def test_ongoing_placeholder_rule(self) -> None:
        self.write("docs/Ongoing.md", _ONGOING + "\n없음\n")
        self.assert_reports("진행 중 기록이 있는데 '없음'이 남아 있음")
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2", "- [ ] M0-T2"))
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1", "- [ ] H1"))
        self.write("docs/Ongoing.md", "# 진행 중\n")
        self.assert_reports("진행 중 기록이 없으면 '없음'을 적어야 함")

    def test_reports_unknown_references_even_with_korean_particles(self) -> None:
        self.write("docs/Done.md", _DONE.replace("I1을 함께", "M7-T2으로 옮긴 I9을 `M8-T1`과 함께"))
        code, output = self.run_checker()
        self.assertIn("알 수 없는 작업 ID 참조: M7-T2", output)
        self.assertIn("알 수 없는 작업 ID 참조: I9", output)
        self.assertNotIn("M8-T1", output)


_M0_T2_DONE = _M0_T2_RECORD.replace("- 시작일: 2026-10-31\n", "- 시작일: 2026-10-31\n- 완료일: 2026-10-31\n").rstrip(
    "\n"
) + "\n\n### 변경 파일\n- `b.py`\n\n### 결과\n- 됨.\n\n### 검증\n- 통과\n"
_DONE_HEAD = "# 완료\n\n보관: [M0](Done-M0.md)\n\n"
_DONE_RECORDS = _DONE[_DONE.index("## M0-T1") :]


class ArchiveTest(_TaskDocsTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def close_m0(self, done: str, archive: str, name: str = "Done-M0.md") -> None:
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2", "- [x] M0-T2"))
        self.write("docs/Ongoing.md", _ONGOING.replace(_M0_T2_RECORD, ""))
        self.write("docs/Done.md", done)
        self.write(f"docs/{name}", "# 완료 보관 M0 기반\n\n[완료](Done.md)\n\n" + archive)

    def test_closed_milestone_archived_passes(self) -> None:
        self.close_m0(_DONE_HEAD, _M0_T2_DONE + "\n" + _DONE_RECORDS)
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_closed_milestone_left_in_done(self) -> None:
        self.close_m0(_DONE_HEAD + _M0_T2_DONE, _DONE_RECORDS)
        self.assert_reports("M0-T2: 닫힌 마일스톤의 기록은 docs/Done-M0.md로 옮겨야 함")

    def test_reports_archive_problems(self) -> None:
        self.close_m0(_DONE_HEAD + _DONE_RECORDS, _M0_T2_DONE + "\n" + _DONE_RECORDS, name="Done-Mold.md")
        self.write("docs/Done-M1.md", "# 완료 보관 M1 다음\n\n" + _M0_T2_DONE.replace("M0-T2", "M1-T1"))
        self.assert_reports(
            "보관 문서 이름은 'Done-M<n>.md'여야 함",
            "M0-T1: 완료 기록이 두 곳 이상에 있음",
            "닫히지 않은 마일스톤 M1의 보관 문서",
        )

    def test_reports_other_milestone_task_in_archive(self) -> None:
        self.close_m0(_DONE_HEAD, _M0_T2_DONE + "\n" + _DONE_RECORDS + "\n" + _M0_T2_DONE.replace("M0-T2", "M1-T1"))
        self.assert_reports("M1-T1: M0 보관 문서에 다른 마일스톤의 태스크 기록")


class LightIssueTest(_TaskDocsTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def add_issue(self, text: str) -> None:
        self.write("docs/Issue.md", _ISSUE + text)

    def test_light_issue_without_records_passes(self) -> None:
        self.add_issue(
            "- [x] I3 오타\n  - 등록일: 2026-10-31\n  - 경량: 오타를 고쳤다.\n  - 완료일: 2026-10-31\n"
            "- [ ] I4 다음 오타\n  - 경량: 고칠 것\n"
        )
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_light_issue_misuse(self) -> None:
        self.add_issue("- [~] I3 진행 중\n  - 경량: 고치는 중\n- [x] I4 완료일 없음\n  - 경량: 고쳤다.\n")
        self.assert_reports("I3: 경량 이슈는 [~] 상태를 쓰지 않음", "I4: 완료한 경량 이슈에 '완료일' 없음")

    def test_reports_light_issue_with_record_link_or_empty_result(self) -> None:
        light_h1 = "- [x] H1 급한 결함\n  - 경량:\n  - 완료일: 2026-10-31"
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1 급한 결함", light_h1)
                   + "- [x] I3 연결\n  - 경량: 했다.\n  - 연결 작업: M0-T1\n  - 완료일: 2026-13-01\n")
        self.assert_reports(
            "H1: 경량 결과가 비어 있음",
            "H1: 경량 이슈는 진행 중·완료 기록을 두지 않음",
            "I3: 경량 이슈는 연결 작업을 두지 않음",
            "I3: '완료일' 날짜 형식 오류: 2026-13-01",
        )


class PreservationTest(_TaskDocsTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def finish_m0_t2(self, record: str) -> None:
        open_m0 = "- [x] M0-T2 둘째 작업\n- [ ] M0-T3 셋째 작업"
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2 둘째 작업", open_m0))
        self.write("docs/Ongoing.md", _ONGOING.replace(_M0_T2_RECORD, ""))
        self.write("docs/Done.md", _DONE.replace("## M0-T1", record + "\n## M0-T1"))

    def moved_record(self) -> str:
        body = _M0_T2_RECORD.rstrip("\n")
        body = body.replace("- 시작일: 2026-10-31\n", "- 시작일: 2026-10-31\n- 완료일: 2026-10-31\n")
        return body + "\n\n### 변경 파일\n- `b.py`\n\n### 결과\n- 됨.\n\n### 검증\n- 통과\n"

    def test_record_moved_intact_passes(self) -> None:
        self.finish_m0_t2(self.moved_record())
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_lines_dropped_while_moving(self) -> None:
        self.finish_m0_t2(self.moved_record().replace("- 2026-10-31: 시작했다.\n", ""))
        self.assert_reports("M0-T2: 완료로 옮기며 빠진 줄 1개, 예: - 2026-10-31: 시작했다.")

    def test_reports_progress_line_removed_from_ongoing(self) -> None:
        self.write("docs/Ongoing.md", _ONGOING.replace("- 방식 A로 한다.", "- 방식 B로 한다."))
        self.assert_reports("M0-T2: 진행 중 기록에서 지워진 줄 1개, 예: - 방식 A로 한다.")

    def test_planning_lines_may_change_in_ongoing(self) -> None:
        self.write("docs/Ongoing.md", _ONGOING.replace("- 둘째 일을 한다.", "- 둘째 일을 다르게 한다."))
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_ongoing_record_that_vanished(self) -> None:
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1", "- [ ] H1"))
        self.write("docs/Ongoing.md", _ONGOING[: _ONGOING.index("## H1")])
        self.assert_reports("H1: 진행 중 기록이 완료로 옮겨지지 않고 사라짐")

    def test_records_moved_to_archive_are_preserved(self) -> None:
        roadmap = _ROADMAP.replace("- [~] M0-T2", "- [x] M0-T2")
        self.write("docs/Roadmap.md", roadmap)
        self.write("docs/Ongoing.md", _ONGOING.replace(_M0_T2_RECORD, ""))
        self.write("docs/Done.md", _DONE.replace("## M0-T1", _M0_T2_DONE + "\n## M0-T1"))
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "done")
        archive = _M0_T2_DONE + "\n" + _DONE_RECORDS
        self.write("docs/Done.md", _DONE_HEAD)
        self.write("docs/Done-M0.md", "# 완료 보관 M0 기반\n\n[완료](Done.md)\n\n" + archive)
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)
        self.write("docs/Done-M0.md", "# 완료 보관 M0 기반\n\n" + archive.replace("- 2026-10-30: 했다.\n", ""))
        self.assert_reports("M0-T1: 완료 기록에서 지워진 줄 1개, 예: - 2026-10-30: 했다.")

    def test_reports_changed_done_line(self) -> None:
        self.write("docs/Done.md", _DONE.replace("- 2026-10-30: 했다.", "- 2026-10-30: 다르게 했다."))
        self.assert_reports("M0-T1: 완료 기록에서 지워진 줄 1개, 예: - 2026-10-30: 했다.")


if __name__ == "__main__":
    unittest.main()
