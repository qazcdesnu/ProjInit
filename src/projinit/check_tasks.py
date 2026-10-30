"""Verify that roadmap, issue, ongoing and done documents agree by work ID.

@doc: docs/design/Checkers.md#6-작업-관리-검사기
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

from projinit.config import ConfigError, Project, load_project, report_config_error
from projinit.doclib import Problem, iter_prose_lines, strip_inline_code

# @doc: docs/design/Checkers.md#6-작업-관리-검사기
ROADMAP_DOC = "Roadmap.md"
# @doc: docs/design/Checkers.md#6-작업-관리-검사기
ISSUE_DOC = "Issue.md"
# @doc: docs/design/Checkers.md#6-작업-관리-검사기
ONGOING_DOC = "Ongoing.md"
# @doc: docs/design/Checkers.md#6-작업-관리-검사기
DONE_DOC = "Done.md"
# @doc: docs/design/Checkers.md#6-작업-관리-검사기
DONE_ARCHIVE_GLOB = "Done-M*.md"

_ID = r"M\d+-T\d+|[IH]\d+"
_ID_RE = re.compile(rf"(?:{_ID})")
# ASCII-only boundaries so that IDs followed by Korean particles ("M0-T6으로") still match.
_ID_REF_RE = re.compile(rf"(?<![0-9A-Za-z-])({_ID})(?![0-9A-Za-z-])")
_MILESTONE_RE = re.compile(r"^## M(\d+) \S")
_TASK_RE = re.compile(r"^- \[([ ~x])\] (M(\d+)-T(\d+)) \S")
_ISSUE_RE = re.compile(r"^- \[([ ~x])\] (([IH])(\d+)) \S")
_DETAIL_RE = re.compile(r"^\s+- ([^:]+):\s*(.*)$")
_RECORD_RE = re.compile(rf"^## ({_ID}) \S")
_FIELD_RE = re.compile(r"^- ([^:]+): (.*)$")
_SECTION_RE = re.compile(r"^### (.+?)\s*$")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DONE_SECTIONS = ("계획", "진행 기록", "결정 사항", "변경 파일", "결과", "검증")
_APPEND_ONLY_SECTIONS = ("진행 기록", "결정 사항")
_ARCHIVE_NAME_RE = re.compile(r"Done-M(\d+)\.md")
_TASK_ID_RE = re.compile(r"M(\d+)-T\d+")
_STATUS_LABELS = {" ": "[ ]", "~": "[~]", "x": "[x]"}


@dataclass(frozen=True)
class WorkItem:
    """A roadmap task or an issue with its status.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """

    id: str
    status: str
    path: Path
    line: int
    link: str | None = None
    light: str | None = None
    finished: str | None = None


@dataclass
class Record:
    """An entry of the ongoing or done document.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """

    id: str
    path: Path
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    sections: set[str] = field(default_factory=set)
    lines: list[tuple[str, str]] = field(default_factory=list)


def _read_lines(path: Path, text: str | None = None) -> list[tuple[int, str]]:
    return list(iter_prose_lines(path.read_text(encoding="utf-8") if text is None else text))


def _expect_next(numbers: dict[str, int], key: str, actual: int, first: int) -> int | None:
    """Record the number for a sequence and return the expected one if it is out of order."""
    expected = numbers.get(key, first - 1) + 1
    numbers[key] = actual
    return expected if actual != expected else None


def parse_roadmap(path: Path) -> tuple[list[WorkItem], list[Problem]]:
    """Read roadmap tasks and report format and numbering problems.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    items, problems = [], []
    numbers: dict[str, int] = {}
    milestone = None
    for number, line in _read_lines(path):
        if line.startswith("## "):
            match = _MILESTONE_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "마일스톤 제목 형식 오류: '## M<n> <이름>'이어야 함"))
                continue
            milestone = int(match.group(1))
            expected = _expect_next(numbers, "M", milestone, first=0)
            if expected is not None:
                problems.append(Problem(path, number, f"마일스톤 번호 차례 오류: M{expected}이어야 함"))
        elif line.startswith("- ["):
            match = _TASK_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "태스크 줄 형식 오류: '- [ ] M<n>-T<m> <설명>'이어야 함"))
                continue
            status, task_id = match.group(1), match.group(2)
            task_milestone, task_number = int(match.group(3)), int(match.group(4))
            items.append(WorkItem(task_id, status, path, number))
            if task_milestone != milestone:
                problems.append(Problem(path, number, f"{task_id}가 M{task_milestone} 마일스톤 아래에 있지 않음"))
                continue
            expected = _expect_next(numbers, f"M{milestone}", task_number, first=1)
            if expected is not None:
                problems.append(
                    Problem(path, number, f"태스크 번호 차례 오류: M{milestone}-T{expected}이어야 함")
                )
    return items, problems


def parse_issues(path: Path) -> tuple[list[WorkItem], list[Problem]]:
    """Read issues with their detail fields and report format and numbering problems.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    items, problems = [], []
    numbers: dict[str, int] = {}
    for number, line in _read_lines(path):
        if line.startswith("- ["):
            match = _ISSUE_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "이슈 줄 형식 오류: '- [ ] I<n> <제목>' 또는 H<n>이어야 함"))
                continue
            prefix, issue_number = match.group(3), int(match.group(4))
            items.append(WorkItem(match.group(2), match.group(1), path, number))
            expected = _expect_next(numbers, prefix, issue_number, first=1)
            if expected is not None:
                problems.append(Problem(path, number, f"이슈 번호 차례 오류: {prefix}{expected}이어야 함"))
            continue
        match = _DETAIL_RE.match(line)
        if not match or not items:
            continue
        name, value = match.group(1).strip(), match.group(2).strip()
        if name == "연결 작업":
            if not _ID_RE.fullmatch(value):
                problems.append(Problem(path, number, f"연결 작업이 작업 ID가 아님: {value}"))
                continue
            items[-1] = replace(items[-1], link=value)
        elif name == "경량":
            items[-1] = replace(items[-1], light=value)
        elif name == "완료일":
            items[-1] = replace(items[-1], finished=value)
    return items, problems


def parse_records(path: Path, text: str | None = None) -> tuple[list[Record], list[Problem]]:
    """Read ongoing or done records, from the given text if any, and report malformed or duplicate headings.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    records: list[Record] = []
    problems = []
    seen: set[str] = set()
    current = None
    section = ""
    for number, line in _read_lines(path, text):
        if line.startswith("## "):
            match = _RECORD_RE.match(line)
            current = None
            if not match:
                problems.append(Problem(path, number, "기록 제목 형식 오류: '## <작업 ID> <제목>'이어야 함"))
                continue
            if match.group(1) in seen:
                problems.append(Problem(path, number, f"중복 기록: {match.group(1)}"))
                continue
            seen.add(match.group(1))
            current = Record(match.group(1), path, number)
            current.lines.append(("", line.rstrip()))
            section = ""
            records.append(current)
        elif current is not None:
            if line.strip():
                current.lines.append((section, line.rstrip()))
            heading = _SECTION_RE.match(line)
            if heading:
                section = heading.group(1)
                current.sections.add(section)
                continue
            field_match = _FIELD_RE.match(line)
            if field_match and not current.sections:
                current.fields[field_match.group(1).strip()] = field_match.group(2).strip()
    return records, problems


def check_states(items: list[WorkItem], ongoing: list[Record], done: list[Record]) -> list[Problem]:
    """Report status marks that disagree with ongoing and done records.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    problems = []
    by_id: dict[str, WorkItem] = {}
    for item in items:
        if item.id in by_id:
            problems.append(Problem(item.path, item.line, f"중복 작업 ID: {item.id}"))
        else:
            by_id[item.id] = item
    ongoing_ids = {record.id for record in ongoing}
    done_ids = {record.id for record in done}
    for item in by_id.values():
        has_ongoing, has_done = item.id in ongoing_ids, item.id in done_ids
        if item.light is not None:
            problems.extend(_check_light(item, has_ongoing or has_done))
            continue
        if item.link is not None:
            problems.extend(_check_linked(item, by_id, has_ongoing or has_done))
            continue
        label = _STATUS_LABELS[item.status]
        if has_ongoing != (item.status == "~"):
            state = "있음" if has_ongoing else "없음"
            problems.append(Problem(item.path, item.line, f"{item.id}: 상태 {label}인데 진행 중 기록 {state}"))
        if has_done != (item.status == "x"):
            state = "있음" if has_done else "없음"
            problems.append(Problem(item.path, item.line, f"{item.id}: 상태 {label}인데 완료 기록 {state}"))
    for record in ongoing + done:
        if record.id not in by_id:
            problems.append(Problem(record.path, record.line, f"로드맵·이슈에 없는 작업의 기록: {record.id}"))
    return problems


def _check_light(item: WorkItem, has_record: bool) -> list[Problem]:
    problems = []
    if not item.light:
        problems.append(Problem(item.path, item.line, f"{item.id}: 경량 결과가 비어 있음"))
    if item.status == "~":
        problems.append(Problem(item.path, item.line, f"{item.id}: 경량 이슈는 [~] 상태를 쓰지 않음"))
    if has_record:
        problems.append(Problem(item.path, item.line, f"{item.id}: 경량 이슈는 진행 중·완료 기록을 두지 않음"))
    if item.link is not None:
        problems.append(Problem(item.path, item.line, f"{item.id}: 경량 이슈는 연결 작업을 두지 않음"))
    if item.status == "x" and item.finished is None:
        problems.append(Problem(item.path, item.line, f"{item.id}: 완료한 경량 이슈에 '완료일' 없음"))
    elif item.finished is not None and _parse_date(item.finished) is None:
        problems.append(Problem(item.path, item.line, f"{item.id}: '완료일' 날짜 형식 오류: {item.finished}"))
    return problems


def _check_linked(item: WorkItem, by_id: dict[str, WorkItem], has_record: bool) -> list[Problem]:
    target = by_id.get(item.link)
    if target is None:
        return [Problem(item.path, item.line, f"{item.id}: 연결 작업 {item.link}가 없음")]
    problems = []
    if target.link is not None:
        problems.append(Problem(item.path, item.line, f"{item.id}: 연결 작업 {item.link}가 다시 다른 작업에 연결됨"))
    if target.status != item.status:
        problems.append(
            Problem(
                item.path,
                item.line,
                f"{item.id}: 상태 {_STATUS_LABELS[item.status]}가 연결 작업 {item.link}의 "
                f"{_STATUS_LABELS[target.status]}와 다름",
            )
        )
    if has_record:
        problems.append(Problem(item.path, item.line, f"{item.id}: 연결 작업이 있는 이슈는 자체 기록을 두지 않음"))
    return problems


def check_records(ongoing_path: Path, ongoing: list[Record], done: list[Record]) -> list[Problem]:
    """Report missing fields and sections, bad dates, done order and the ongoing placeholder rule.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    problems = []
    for record in ongoing:
        problems.extend(_check_record(record, ("시작일",), ("계획",)))
    problems.extend(_check_done(done))
    placeholders = [number for number, line in _read_lines(ongoing_path) if line.strip() == "없음"]
    if not ongoing and not placeholders:
        problems.append(Problem(ongoing_path, 1, "진행 중 기록이 없으면 '없음'을 적어야 함"))
    for number in placeholders if ongoing else []:
        problems.append(Problem(ongoing_path, number, "진행 중 기록이 있는데 '없음'이 남아 있음"))
    return problems


def _check_done(done: list[Record]) -> list[Problem]:
    problems = []
    previous: date | None = None
    for record in done:
        problems.extend(_check_record(record, ("시작일", "완료일"), _DONE_SECTIONS))
        finished = _parse_date(record.fields.get("완료일", ""))
        if finished is None:
            continue
        if previous is not None and finished > previous:
            problems.append(Problem(record.path, record.line, f"{record.id}: 완료 기록은 완료일이 늦은 것부터 놓아야 함"))
        previous = finished
    return problems


def _check_record(record: Record, fields: tuple[str, ...], sections: tuple[str, ...]) -> list[Problem]:
    problems = []
    for name in fields:
        value = record.fields.get(name)
        if value is None:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 필드 없음"))
        elif _parse_date(value) is None:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 날짜 형식 오류: {value}"))
    for name in sections:
        if name not in record.sections:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 절 없음"))
    return problems


def _parse_date(value: str) -> date | None:
    if not _DATE_RE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def check_preservation(
    project: Project, ongoing_path: Path, done_path: Path, ongoing: list[Record], done: list[Record]
) -> list[Problem]:
    """Report lines of records in the last commit that were dropped from the current records.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    problems = []
    current_ongoing = {record.id: record for record in ongoing}
    current_done = {record.id: record for record in done}
    root = project.root
    head_ongoing = _head_records(root, ongoing_path)
    head_done = _head_records(root, done_path) + [
        record for path in _head_archive_paths(project) for record in _head_records(root, path)
    ]
    for old in head_ongoing:
        if old.id in current_ongoing:
            kept = [line for section, line in old.lines if section in _APPEND_ONLY_SECTIONS]
            problems += _missing_lines(old, kept, current_ongoing[old.id], "진행 중 기록에서 지워진 줄")
        elif old.id in current_done:
            kept = [line for _, line in old.lines]
            problems += _missing_lines(old, kept, current_done[old.id], "완료로 옮기며 빠진 줄")
        else:
            problems.append(Problem(ongoing_path, 1, f"{old.id}: 진행 중 기록이 완료로 옮겨지지 않고 사라짐"))
    for old in head_done:
        if old.id not in current_done:
            problems.append(Problem(done_path, 1, f"{old.id}: 완료 기록이 사라짐"))
            continue
        problems += _missing_lines(old, [line for _, line in old.lines], current_done[old.id], "완료 기록에서 지워진 줄")
    return problems


def _head_records(root: Path, path: Path) -> list[Record]:
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError:
        return []
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"HEAD:{relative}"], capture_output=True, encoding="utf-8"
    )
    if shown.returncode != 0:
        return []
    return parse_records(path, shown.stdout)[0]


def _head_archive_paths(project: Project) -> list[Path]:
    root = project.root
    docs = project.docs_dir.relative_to(root).as_posix()
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "--name-only", "HEAD", f"{docs}/"],
        capture_output=True,
        encoding="utf-8",
    )
    if listed.returncode != 0:
        return []
    return [root / name for name in listed.stdout.splitlines() if Path(name).match(DONE_ARCHIVE_GLOB)]


def _missing_lines(old: Record, required: list[str], current: Record, label: str) -> list[Problem]:
    present = {line for _, line in current.lines}
    missing = [line for line in required if line not in present]
    if not missing:
        return []
    return [Problem(current.path, current.line, f"{old.id}: {label} {len(missing)}개, 예: {missing[0]}")]


def find_done_archives(project: Project) -> list[Path]:
    """Return the archive documents of closed milestones.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    return sorted(project.docs_dir.glob(DONE_ARCHIVE_GLOB))


def check_archives(
    tasks: list[WorkItem], done: list[Record], archives: dict[Path, list[Record]]
) -> list[Problem]:
    """Report misplaced, duplicate or malformed records across the done document and its archives.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    closed = _closed_milestones(tasks)
    problems = []
    placed = {record.id for record in done}
    for path, records in archives.items():
        name = _ARCHIVE_NAME_RE.fullmatch(path.name)
        milestone = int(name.group(1)) if name else None
        if milestone is None:
            problems.append(Problem(path, 1, "보관 문서 이름은 'Done-M<n>.md'여야 함"))
        elif milestone not in closed:
            problems.append(Problem(path, 1, f"닫히지 않은 마일스톤 M{milestone}의 보관 문서"))
        problems.extend(_check_done(records))
        for record in records:
            if record.id in placed:
                problems.append(Problem(path, record.line, f"{record.id}: 완료 기록이 두 곳 이상에 있음"))
            placed.add(record.id)
            task = _TASK_ID_RE.fullmatch(record.id)
            if task and milestone is not None and int(task.group(1)) != milestone:
                problems.append(Problem(path, record.line, f"{record.id}: M{milestone} 보관 문서에 다른 마일스톤의 태스크 기록"))
    for record in done:
        task = _TASK_ID_RE.fullmatch(record.id)
        if task and int(task.group(1)) in closed:
            problems.append(
                Problem(
                    record.path,
                    record.line,
                    f"{record.id}: 닫힌 마일스톤의 기록은 {DONE_ARCHIVE_GLOB.replace('*', task.group(1))}(같은 디렉터리)로 옮겨야 함",
                )
            )
    return problems


def _closed_milestones(tasks: list[WorkItem]) -> set[int]:
    statuses: dict[int, list[str]] = {}
    for task in tasks:
        match = _TASK_ID_RE.fullmatch(task.id)
        if match:
            statuses.setdefault(int(match.group(1)), []).append(task.status)
    return {milestone for milestone, marks in statuses.items() if all(mark == "x" for mark in marks)}


def check_references(paths: list[Path], known: set[str]) -> list[Problem]:
    """Report work IDs mentioned in prose that are not defined in the roadmap or issues.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    problems = []
    for path in paths:
        for number, line in _read_lines(path):
            for match in _ID_REF_RE.finditer(strip_inline_code(line)):
                if match.group(1) not in known:
                    problems.append(Problem(path, number, f"알 수 없는 작업 ID 참조: {match.group(1)}"))
    return problems


def main(argv: list[str] | None = None) -> int:
    """Run every task document check and print problems; return the exit code.

    @doc: docs/design/Checkers.md#6-작업-관리-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    paths = [project.docs_dir / doc for doc in (ROADMAP_DOC, ISSUE_DOC, ONGOING_DOC, DONE_DOC)]
    missing = [Problem(path, 1, "작업 관리 문서 없음") for path in paths if not path.is_file()]
    if missing:
        problems = missing
    else:
        roadmap_path, issue_path, ongoing_path, done_path = paths
        tasks, problems = parse_roadmap(roadmap_path)
        issues, issue_problems = parse_issues(issue_path)
        ongoing, ongoing_problems = parse_records(ongoing_path)
        done, done_problems = parse_records(done_path)
        archives: dict[Path, list[Record]] = {}
        for archive_path in find_done_archives(project):
            archives[archive_path], archive_problems = parse_records(archive_path)
            done_problems += archive_problems
        all_done = done + [record for records in archives.values() for record in records]
        items = tasks + issues
        problems += (
            issue_problems
            + ongoing_problems
            + done_problems
            + check_states(items, ongoing, all_done)
            + check_records(ongoing_path, ongoing, done)
            + check_archives(tasks, done, archives)
            + check_preservation(project, ongoing_path, done_path, ongoing, all_done)
            + check_references(paths + list(archives), {item.id for item in items})
        )
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_tasks: 문제 {len(problems)}건")
        return 1
    print(f"check_tasks: 통과 (작업 {len(items)}개, 진행 중 {len(ongoing)}개, 완료 {len(done)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
