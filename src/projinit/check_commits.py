"""Verify commit messages, work branch names and pull request titles against the work-ID conventions.

@doc: docs/design/Checkers.md#10-커밋-메시지-검사기
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from projinit.check_tasks import ISSUE_DOC, ROADMAP_DOC, parse_issues, parse_roadmap
from projinit.config import ConfigError, Project, load_project, report_config_error
from projinit.doclib import Problem

# @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
SUBJECT_MAX_LENGTH = 72
# @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
GIT_SUBJECT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")

_ID = r"M\d+-T\d+|[IH]\d+"
_IN_PROGRESS = "(진행 중)"
_SUBJECT_RE = re.compile(rf"^((?:{_ID})(?:, (?:{_ID}))*)(\(진행 중\))?: (\S.*)$")
_BRANCH_RE = re.compile(r"^(m\d+-t\d+|[ih]\d+)((?:-[a-z0-9]+)+)$")
_FORMAT = "<작업 ID>[, <작업 ID>…][(진행 중)]: <요약>"
# Field and record separators that cannot appear in commit messages.
_FIELD_SEP, _RECORD_SEP = "\x1f", "\x1e"


def work_statuses(project: Project) -> dict[str, str]:
    """Map every roadmap task and issue ID to its status mark.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    statuses: dict[str, str] = {}
    for doc, parse in ((ROADMAP_DOC, parse_roadmap), (ISSUE_DOC, parse_issues)):
        path = project.docs_dir / doc
        if path.is_file():
            statuses.update((item.id, item.status) for item in parse(path)[0])
    return statuses


def parse_subject(subject: str) -> tuple[list[str], bool, str] | None:
    """Split a subject line into its work IDs, in-progress mark and summary, or return None if malformed.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    match = _SUBJECT_RE.match(subject)
    if not match:
        return None
    return match.group(1).split(", "), match.group(2) is not None, match.group(3)


def check_message(
    message: str, statuses: dict[str, str], require_started: bool, is_pr_title: bool = False
) -> list[str]:
    """Return the convention violations of one commit message or pull request title.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    lines = [line.rstrip() for line in message.splitlines() if not line.startswith("#")]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    if not lines:
        return ["빈 커밋 메시지"]
    subject = lines[0]
    if subject.startswith(GIT_SUBJECT_PREFIXES):
        return []
    problems = []
    if len(subject) > SUBJECT_MAX_LENGTH:
        problems.append(f"제목 줄이 {SUBJECT_MAX_LENGTH}자를 넘음 ({len(subject)}자)")
    if len(lines) > 1 and lines[1]:
        problems.append("제목 다음 줄은 비어 있어야 함")
    parsed = parse_subject(subject)
    if parsed is None:
        problems.append(f"제목 형식 오류: '{_FORMAT}'이어야 함")
        return problems
    ids, in_progress, summary = parsed
    if in_progress and is_pr_title:
        problems.append(f"PR 제목에는 {_IN_PROGRESS}를 붙이지 않음")
    if summary.endswith("."):
        problems.append("요약은 마침표로 끝내지 않음")
    for work_id in sorted({work_id for work_id in ids if ids.count(work_id) > 1}):
        problems.append(f"제목에 같은 작업 ID가 반복됨: {work_id}")
    for work_id in dict.fromkeys(ids):
        status = statuses.get(work_id)
        if status is None:
            problems.append(f"로드맵·이슈에 없는 작업 ID: {work_id}")
        elif require_started and status == " ":
            problems.append(f"시작하지 않은 작업([ ])의 ID: {work_id}")
    return problems


def check_branch(name: str, statuses: dict[str, str]) -> list[str]:
    """Return the convention violations of a work branch name.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    match = _BRANCH_RE.match(name)
    if not match:
        return [f"브랜치 이름 형식 오류: '<작업 ID 소문자>-<설명>'이어야 함: {name}"]
    work_id = match.group(1).upper()
    if work_id not in statuses:
        return [f"로드맵·이슈에 없는 작업 ID의 브랜치: {work_id}"]
    return []


def commit_messages(root: Path, revision_range: str) -> list[tuple[str, str]]:
    """Return (short hash, message) of the non-merge commits in a revision range.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    output = subprocess.run(
        ["git", "log", "--no-merges", f"--format=%h{_FIELD_SEP}%B{_RECORD_SEP}", revision_range],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    commits = []
    for record in output.split(_RECORD_SEP):
        if _FIELD_SEP in record:
            short_hash, message = record.split(_FIELD_SEP, 1)
            commits.append((short_hash.strip(), message))
    return commits


def main(argv: list[str] | None = None) -> int:
    """Check one message file, a pull request title and branch, or the history; return the exit code.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--message-file", type=Path)
    parser.add_argument("--subject")
    parser.add_argument("--branch")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    statuses = work_statuses(project)
    problems = []
    if args.subject is not None or args.branch is not None:
        texts = []
        if args.subject is not None:
            texts += [f"PR 제목: {text}" for text in check_message(args.subject, statuses, True, is_pr_title=True)]
        if args.branch is not None:
            texts += check_branch(args.branch, statuses)
        problems = [Problem(Path("PR"), 1, text) for text in texts]
        checked = 1
    elif args.message_file is not None:
        message = args.message_file.read_text(encoding="utf-8")
        problems = [Problem(args.message_file, 1, text) for text in check_message(message, statuses, True)]
        checked = 1
    else:
        baseline = project.config.commit_baseline
        has_commits = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=root, capture_output=True)
        try:
            commits = commit_messages(root, f"{baseline}..HEAD" if baseline else "HEAD") if has_commits.returncode == 0 else []
        except subprocess.CalledProcessError as error:
            commits = []
            problems.append(Problem(root, 1, f"git log 실패: {error.stderr.strip()}"))
        for short_hash, message in commits:
            problems += [
                Problem(Path(f"commit {short_hash}"), 1, text) for text in check_message(message, statuses, False)
            ]
        checked = len(commits)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_commits: 문제 {len(problems)}건")
        return 1
    print(f"check_commits: 통과 (커밋 {checked}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
