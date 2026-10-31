"""Verify the bidirectional pointers between documents and code symbols.

@doc: docs/design/Checkers.md#4-포인터-검사기
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from projinit.code_index import ModuleIndex, SymbolRef, index_module
from projinit.config import ConfigError, Project, load_project, report_config_error
from projinit.doclib import (
    CODE_SUFFIXES,
    Problem,
    display_path,
    extract_links,
    find_code_files,
    find_doc_files,
    heading_anchors,
    is_external,
    resolve_link,
)
from projinit.check_tasks import ISSUE_DOC, ROADMAP_DOC, WorkItem, parse_issues, parse_roadmap
from projinit.languages import DEFINITION

_LINE_ANCHOR_RE = re.compile(r"L\d+(-L?\d+)?")


@dataclass(frozen=True)
class CodePointer:
    """A pointer from a document line to a code symbol.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """

    doc: Path
    line: int
    symbol: SymbolRef


def _describe(symbol: SymbolRef, root: Path) -> str:
    shown = display_path(symbol.file, root)
    return f"{shown}#{symbol.qualname}" if symbol.qualname else shown


def collect_code_pointers(
    project: Project, modules: dict[Path, ModuleIndex]
) -> tuple[list[CodePointer], list[Problem]]:
    """Gather pointers from documents to code and report those that do not resolve.

    Code files referenced from documents but outside the code roots are indexed into
    ``modules`` on demand.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    pointers = []
    problems = []
    root = project.root
    for doc in find_doc_files(project):
        doc = doc.resolve()
        for link in extract_links(doc, doc.read_text(encoding="utf-8")):
            if is_external(link.target):
                continue
            path, anchor = resolve_link(link)
            if path.suffix not in CODE_SUFFIXES or project.in_materials(path):
                continue
            if not path.is_file():
                problems.append(Problem(doc, link.line, f"코드 포인터 대상 파일 없음: {link.target}"))
                continue
            if _LINE_ANCHOR_RE.fullmatch(anchor):
                problems.append(Problem(doc, link.line, f"줄 번호 포인터는 금지됨: {link.target}"))
                continue
            if path not in modules:
                modules[path] = index_module(path, root)
            if anchor not in modules[path].symbols:
                problems.append(Problem(doc, link.line, f"구문 트리에 심볼 없음: {link.target}"))
                continue
            pointers.append(CodePointer(doc, link.line, SymbolRef(path, anchor)))
    return pointers, problems


def check_doc_pointers(root: Path, modules: dict[Path, ModuleIndex]) -> list[Problem]:
    """Report pointers from code whose target document or heading anchor is missing.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    problems = []
    anchor_cache: dict[Path, set[str]] = {}
    for module in modules.values():
        for pointer in module.doc_pointers:
            target = display_path(pointer.doc, root)
            if pointer.doc.suffix != ".md" or not pointer.doc.is_file():
                problems.append(Problem(module.path, pointer.line, f"근거 문서 없음: {target}"))
                continue
            if not pointer.anchor:
                continue
            if pointer.doc not in anchor_cache:
                anchor_cache[pointer.doc] = heading_anchors(pointer.doc.read_text(encoding="utf-8"))
            if pointer.anchor not in anchor_cache[pointer.doc]:
                problems.append(
                    Problem(module.path, pointer.line, f"앵커 없음: {target}#{pointer.anchor}")
                )
    return problems


def check_coverage(project: Project, modules: dict[Path, ModuleIndex]) -> list[Problem]:
    """Report modules and public top-level symbols in the code roots lacking a document pointer.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    problems = []
    for path in find_code_files(project):
        module = modules[path.resolve()]
        if not module.has_code:
            continue
        owners = {pointer.symbol.qualname for pointer in module.doc_pointers}
        if "" not in owners:
            problems.append(Problem(module.path, 1, "파일에 @doc 포인터 없음"))
        for qualname, definitions in module.symbols.items():
            if qualname in owners:
                continue
            for definition in definitions:
                if definition.kind == DEFINITION and definition.top_level and definition.public:
                    problems.append(
                        Problem(module.path, definition.line, f"공개 심볼 {qualname}에 @doc 포인터 없음")
                    )
                    break
    return problems


def check_reciprocity(
    root: Path, code_pointers: list[CodePointer], modules: dict[Path, ModuleIndex]
) -> list[Problem]:
    """Report pointers in either direction that have no pointer back between related symbols.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    doc_pointers = [pointer for module in modules.values() for pointer in module.doc_pointers]
    problems = []
    for code_pointer in code_pointers:
        # A symbol named by a document must know that document itself; the file header does not count.
        if not any(
            pointer.doc == code_pointer.doc
            and pointer.symbol.is_related(code_pointer.symbol)
            and (pointer.symbol.qualname or not code_pointer.symbol.qualname)
            for pointer in doc_pointers
        ):
            problems.append(
                Problem(
                    code_pointer.doc,
                    code_pointer.line,
                    f"역방향 포인터 없음: {_describe(code_pointer.symbol, root)} 또는 관련 심볼이 "
                    f"{display_path(code_pointer.doc, root)}를 가리켜야 함",
                )
            )
    for doc_pointer in doc_pointers:
        if not doc_pointer.doc.is_file():
            continue
        if not any(
            pointer.doc == doc_pointer.doc and pointer.symbol.is_related(doc_pointer.symbol)
            for pointer in code_pointers
        ):
            problems.append(
                Problem(
                    doc_pointer.symbol.file,
                    doc_pointer.line,
                    f"역방향 포인터 없음: {display_path(doc_pointer.doc, root)}가 "
                    f"{_describe(doc_pointer.symbol, root)} 또는 관련 심볼을 가리켜야 함",
                )
            )
    return problems


def check_stubs(project: Project, modules: dict[Path, ModuleIndex]) -> list[Problem]:
    """Report mock-up markers whose task is unknown or not in progress.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    items: dict[str, WorkItem] = {}
    for doc, parse in ((ROADMAP_DOC, parse_roadmap), (ISSUE_DOC, parse_issues)):
        if (project.docs_dir / doc).is_file():
            items.update((item.id, item) for item in parse(project.docs_dir / doc)[0])
    problems = []
    for module in modules.values():
        for line, task_id in module.stubs:
            item = items.get(task_id)
            if item is None:
                problems.append(Problem(module.path, line, f"목업의 작업 {task_id}가 로드맵·이슈에 없음"))
                continue
            status = items[item.link].status if item.link in items else item.status
            if status != "~":
                problems.append(Problem(module.path, line, f"작업 {task_id}가 진행 중([~])이 아닌데 목업이 남아 있음"))
    return problems


def main(argv: list[str] | None = None) -> int:
    """Run every pointer check and print problems; return the exit code.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    modules = {path.resolve(): index_module(path.resolve(), root) for path in find_code_files(project)}
    code_pointers, problems = collect_code_pointers(project, modules)
    problems = (
        [problem for module in modules.values() for problem in module.problems]
        + problems
        + check_doc_pointers(root, modules)
        + check_coverage(project, modules)
        + check_reciprocity(root, code_pointers, modules)
        + check_stubs(project, modules)
    )
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_pointers: 문제 {len(problems)}건")
        return 1
    doc_pointer_count = sum(len(module.doc_pointers) for module in modules.values())
    stub_count = sum(len(module.stubs) for module in modules.values())
    print(
        f"check_pointers: 통과 (문서→코드 {len(code_pointers)}개, 코드→문서 {doc_pointer_count}개, "
        f"목업 {stub_count}개)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
