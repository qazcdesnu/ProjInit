"""Verify document links, the entry document, and that no document is orphaned.

@doc: docs/VerificationTools.md#3-문서-링크-검사기
"""

import argparse
import sys
from collections import deque
from pathlib import Path

from tools.doclib import (
    CODE_SUFFIXES,
    DOCS_DIR,
    ENTRY_DOC,
    INDEX_DOC,
    REPO_ROOT,
    Problem,
    extract_links,
    find_doc_files,
    heading_anchors,
    is_external,
    iter_prose_lines,
    resolve_link,
    strip_inline_code,
)


def check_links(root: Path) -> list[Problem]:
    """Report links whose target file, directory or document anchor is missing.

    @doc: docs/VerificationTools.md#3-문서-링크-검사기
    """
    problems = []
    anchor_cache: dict[Path, set[str]] = {}
    for doc in find_doc_files(root):
        for link in extract_links(doc, doc.read_text(encoding="utf-8")):
            if is_external(link.target):
                continue
            path, anchor = resolve_link(link)
            if path.suffix in CODE_SUFFIXES:
                continue
            if not path.exists():
                problems.append(Problem(doc, link.line, f"링크 대상 없음: {link.target}"))
                continue
            if anchor and path.suffix == ".md":
                if path not in anchor_cache:
                    anchor_cache[path] = heading_anchors(path.read_text(encoding="utf-8"))
                if anchor not in anchor_cache[path]:
                    problems.append(Problem(doc, link.line, f"앵커 없음: {link.target}"))
    return problems


def check_entry(root: Path) -> list[Problem]:
    """Report a missing entry document or a missing link from it to the index.

    @doc: docs/VerificationTools.md#3-문서-링크-검사기
    """
    entry = root / ENTRY_DOC
    if not entry.is_file():
        return [Problem(entry, 1, "진입 문서 없음")]
    index = (root / INDEX_DOC).resolve()
    for link in extract_links(entry, entry.read_text(encoding="utf-8")):
        if not is_external(link.target) and resolve_link(link)[0] == index:
            return []
    return [Problem(entry, 1, f"진입 문서에 {INDEX_DOC} 링크 없음")]


def check_entry_format(root: Path) -> list[Problem]:
    """Report lines of the entry document that go beyond a title, one purpose paragraph and link lists.

    @doc: docs/VerificationTools.md#3-문서-링크-검사기
    """
    entry = root / ENTRY_DOC
    if not entry.is_file():
        return []
    text = entry.read_text(encoding="utf-8")
    lines = text.splitlines()
    prose = {number for number, _ in iter_prose_lines(text)}
    docs_dir = (root / DOCS_DIR).resolve()
    body_start = _purpose_end(lines)
    problems = []
    if not lines or not lines[0].startswith("# "):
        problems.append(Problem(entry, 1, "진입 문서는 '# ' 제목으로 시작해야 함"))
    for number, line in enumerate(lines, start=1):
        if number not in prose:
            problems.append(Problem(entry, number, "진입 문서에 코드 블록을 쓸 수 없음"))
        elif strip_inline_code(line) != line:
            problems.append(Problem(entry, number, "진입 문서에 인라인 코드를 쓸 수 없음"))
        elif number > body_start and line.strip() and not _is_entry_item(entry, docs_dir, line):
            problems.append(Problem(entry, number, "진입 문서에는 '## ' 제목과 하위 문서 링크 목록 줄만 쓸 수 있음"))
    return problems


def _purpose_end(lines: list[str]) -> int:
    """Return the line number of the last line of the purpose paragraph after the title."""
    number = 1
    while number < len(lines) and not lines[number].strip():
        number += 1
    while number < len(lines) and lines[number].strip():
        number += 1
    return number


def _is_entry_item(entry: Path, docs_dir: Path, line: str) -> bool:
    if line.startswith("## "):
        return True
    if not line.startswith("- "):
        return False
    for link in extract_links(entry, line):
        if is_external(link.target):
            continue
        path = resolve_link(link)[0]
        if path.suffix == ".md" and docs_dir in path.parents:
            return True
    return False


def find_orphans(root: Path) -> list[Problem]:
    """Report documents under the docs directory unreachable from the index.

    @doc: docs/VerificationTools.md#3-문서-링크-검사기
    """
    index = (root / INDEX_DOC).resolve()
    if not index.is_file():
        return [Problem(index, 1, "인덱스 문서 없음")]
    reachable = {index}
    queue = deque([index])
    while queue:
        doc = queue.popleft()
        for link in extract_links(doc, doc.read_text(encoding="utf-8")):
            if is_external(link.target):
                continue
            path = resolve_link(link)[0]
            if path.suffix == ".md" and path.is_file() and path not in reachable:
                reachable.add(path)
                queue.append(path)
    docs_dir = (root / DOCS_DIR).resolve()
    return [
        Problem(doc, 1, f"고아 문서: {INDEX_DOC}에서 도달할 수 없음")
        for doc in find_doc_files(root)
        if doc.resolve().is_relative_to(docs_dir) and doc.resolve() not in reachable
    ]


def main(argv: list[str] | None = None) -> int:
    """Run every document check and print problems; return the exit code.

    @doc: docs/VerificationTools.md#3-문서-링크-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    root = parser.parse_args(argv).root.resolve()
    problems = check_links(root) + check_entry(root) + check_entry_format(root) + find_orphans(root)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_docs: 문제 {len(problems)}건")
        return 1
    print(f"check_docs: 통과 (문서 {len(find_doc_files(root))}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
