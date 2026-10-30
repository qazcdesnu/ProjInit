"""Verify that a commit message subject starts with known work IDs.

@doc: docs/design/Checkers.md#10-커밋-메시지-검사기
"""

import argparse
import sys
from pathlib import Path

from projinit.check_tasks import ISSUE_DOC, ROADMAP_DOC, parse_issues, parse_roadmap
from projinit.config import ConfigError, load_project, report_config_error

# @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
GIT_SUBJECT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")

_IN_PROGRESS = "(진행 중)"
_FORMAT = "<작업 ID>[, <작업 ID>...][(진행 중)]: <요약>"


def check_message(text: str, known: set[str]) -> list[str]:
    """Return the problems of a commit message against the known work IDs.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    subject = next(
        (line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")), None
    )
    if subject is None:
        return ["제목이 없음"]
    if subject.startswith(GIT_SUBJECT_PREFIXES):
        return []
    head, separator, summary = subject.partition(": ")
    if not separator or not summary.strip():
        return [f"제목은 '{_FORMAT}' 형식이어야 함: {subject}"]
    head = head.removesuffix(_IN_PROGRESS)
    ids = head.split(", ")
    if not all(ids):
        return [f"제목은 '{_FORMAT}' 형식이어야 함: {subject}"]
    return [f"로드맵·이슈에 없는 작업 ID: {work_id}" for work_id in ids if work_id not in known]


def main(argv: list[str] | None = None) -> int:
    """Check the commit message file given by the commit-msg hook; return the exit code.

    @doc: docs/design/Checkers.md#10-커밋-메시지-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("message_file", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    known: set[str] = set()
    for doc, parse in ((ROADMAP_DOC, parse_roadmap), (ISSUE_DOC, parse_issues)):
        if (project.docs_dir / doc).is_file():
            known.update(item.id for item in parse(project.docs_dir / doc)[0])
    problems = check_message(args.message_file.read_text(encoding="utf-8"), known)
    for problem in problems:
        print(f"커밋 메시지: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
