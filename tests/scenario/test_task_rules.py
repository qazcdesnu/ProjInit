"""Scenarios that break the task rules.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import unittest

from tests.scenario.project import ScenarioCase

_RECORD_BODY = "\n### 계획\n- 없음\n\n### 진행 기록\n- 없음\n\n### 결정 사항\n- 없음\n\n### 변경 파일\n- 없음\n\n### 결과\n- 없음\n"


class TaskRulesTest(ScenarioCase):
    """@doc: docs/design/Checkers.md#51-시나리오-테스트"""

    def test_in_progress_task_without_record(self) -> None:
        self.append("docs/Roadmap.md", "- [~] M0-T3 셋째\n")
        self.assert_caught("check_tasks", "M0-T3: 상태 [~]인데 진행 중 기록 없음")

    def test_issue_number_gap(self) -> None:
        self.append("docs/Issue.md", "- [ ] I4 넷째\n  - 등록일: 2026-11-01\n")
        self.assert_caught("check_tasks", "이슈 번호 차례 오류: I3이어야 함")

    def test_duplicate_issue(self) -> None:
        self.append("docs/Issue.md", "- [ ] I1 또\n  - 등록일: 2026-11-01\n")
        self.assert_caught("check_tasks", "I1")

    def test_record_of_unknown_task(self) -> None:
        self.append("docs/Ongoing.md", "\n## I77 모름\n\n- 시작일: 2026-11-01\n\n### 계획\n- x\n")
        self.assert_caught("check_tasks", "로드맵·이슈에 없는 작업의 기록: I77")

    def test_changed_done_record(self) -> None:
        self.replace("docs/Done.md", "- 처음 상태.", "- 바꾼 상태.")
        self.assert_caught("check_tasks", "M0-T1: 완료 기록에서 지워진 줄")

    def test_removed_done_record(self) -> None:
        text = self.read("docs/Done.md")
        self.write("docs/Done.md", text[: text.index("\n## M0-T1")] + "\n")
        self.assert_caught("check_tasks", "M0-T1")

    def test_done_task_without_record(self) -> None:
        self.append("docs/Roadmap.md", "- [x] M0-T3 셋째\n")
        self.assert_caught("check_tasks", "M0-T3: 상태 [x]인데 완료 기록 없음")

    def test_done_record_without_section(self) -> None:
        self.append("docs/Issue.md", "- [x] I3 셋째\n  - 등록일: 2026-11-01\n")
        self.replace("docs/Done.md", "\n## M0-T1", f"\n## I3 셋째\n\n- 시작일: 2026-11-01\n- 완료일: 2026-11-01\n{_RECORD_BODY}\n## M0-T1")
        self.assert_caught("check_tasks", "I3: '검증' 절 없음")

    def test_light_issue_without_result(self) -> None:
        self.replace("docs/Issue.md", "  - 경량: 오타를 고쳤다.", "  - 경량:")
        self.assert_caught("check_tasks", "경량")

    def test_finished_light_issue_without_date(self) -> None:
        self.replace("docs/Issue.md", "  - 완료일: 2026-11-01\n", "")
        self.assert_caught("check_tasks", "I1: 완료한 경량 이슈에 '완료일' 없음")

    def test_bad_date(self) -> None:
        self.replace("docs/Ongoing.md", "- 시작일: 2026-11-01", "- 시작일: 2026/11/01")
        self.assert_caught("check_tasks", "I2: '시작일' 날짜 형식 오류: 2026/11/01")

    def test_none_line_next_to_a_record(self) -> None:
        self.append("docs/Ongoing.md", "\n없음\n")
        self.assert_caught("check_tasks", "진행 중 기록이 있는데 '없음'이 남아 있음")

    def test_malformed_task_line(self) -> None:
        self.append("docs/Roadmap.md", "- [?] M0-T3 이상한 상태\n")
        self.assert_caught("check_tasks", "태스크 줄 형식 오류")

    def test_milestone_number_gap(self) -> None:
        self.append("docs/Roadmap.md", "\n## M2 셋째\n\n- [ ] M2-T1 x\n")
        self.assert_caught("check_tasks", "마일스톤 번호 차례 오류: M1이어야 함")

    def test_removed_progress_line(self) -> None:
        self.replace("docs/Ongoing.md", "- 2026-11-01: 목업을 만들었다.\n", "")
        self.assert_caught("check_tasks", "I2: 진행 중 기록에서 지워진 줄")

    def test_done_records_out_of_order(self) -> None:
        self.append("docs/Issue.md", "- [x] I3 셋째\n  - 등록일: 2026-11-01\n")
        self.append("docs/Done.md", f"\n## I3 셋째\n\n- 시작일: 2026-11-02\n- 완료일: 2026-11-02\n{_RECORD_BODY}\n### 검증\n- 없음\n")
        self.assert_caught("check_tasks", "완료 기록은 완료일이 늦은 것부터 놓아야 함")

    def test_archive_of_unknown_milestone(self) -> None:
        self.write("docs/Done-M5.md", "# 완료 M5\n\n[i](index.md)\n")
        self.replace("docs/Done.md", "보관 문서로 옮긴다.", "보관 문서로 옮긴다. [M5](Done-M5.md).")
        self.assert_caught("check_tasks", "M5")

    def test_unknown_id_in_text(self) -> None:
        self.replace("docs/Ongoing.md", "- later를 만든다.", "- later를 만든다. M9-T9와 관련.")
        self.assert_caught("check_tasks", "알 수 없는 작업 ID 참조: M9-T9")

    def test_finished_issue_with_ongoing_record(self) -> None:
        self.replace("docs/Issue.md", "- [~] I2", "- [x] I2")
        self.assert_caught("check_tasks", "I2: 상태 [x]인데 진행 중 기록 있음")

    def test_ongoing_record_without_plan(self) -> None:
        self.replace("docs/Ongoing.md", "### 계획\n- later를 만든다.\n\n", "")
        self.assert_caught("check_tasks", "I2: '계획' 절 없음")


if __name__ == "__main__":
    unittest.main()
