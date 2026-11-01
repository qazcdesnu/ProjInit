"""Verify the bidirectional pointers between documents and code symbols.

@doc: docs/design/Checkers.md#4-포인터-검사기
"""

import argparse
import re
import subprocess
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
    section_anchor,
)
from projinit.check_tasks import ISSUE_DOC, ONGOING_DOC, ROADMAP_DOC, WorkItem, parse_issues, parse_roadmap
from projinit.languages import DEFINITION

_LINE_ANCHOR_RE = re.compile(r"L\d+(-L?\d+)?")
# @doc: docs/design/Checkers.md#4-포인터-검사기
CONFIRM_PREFIX = "- 포인터 확인: "


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

    A document pointer is the reference: its missing back pointer is reported at the code
    symbol with the exact @doc line to add, computed from the document.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    doc_pointers = [pointer for module in modules.values() for pointer in module.doc_pointers]
    problems = []
    doc_texts: dict[Path, str] = {}
    for code_pointer in code_pointers:
        # A symbol named by a document must know that document itself; the file header does not count.
        if any(
            pointer.doc == code_pointer.doc
            and pointer.symbol.is_related(code_pointer.symbol)
            and (pointer.symbol.qualname or not code_pointer.symbol.qualname)
            for pointer in doc_pointers
        ):
            continue
        if code_pointer.doc not in doc_texts:
            doc_texts[code_pointer.doc] = code_pointer.doc.read_text(encoding="utf-8")
        anchor = section_anchor(doc_texts[code_pointer.doc], code_pointer.line)
        doc = display_path(code_pointer.doc, root)
        symbol = code_pointer.symbol
        definitions = modules[symbol.file].symbols.get(symbol.qualname) or []
        where = symbol.qualname or "파일 머리"
        problems.append(
            Problem(
                symbol.file,
                definitions[0].line if definitions else 1,
                f"역방향 포인터 없음: {doc}:{code_pointer.line}이 {_describe(symbol, root)}을 가리킴. "
                f"{where}에 @doc: {doc}{'#' + anchor if anchor else ''}를 단다",
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
                    f"받아 주는 문서 포인터 없음: {display_path(doc_pointer.doc, root)}가 "
                    f"{_describe(doc_pointer.symbol, root)} 또는 관련 심볼을 가리키지 않음. "
                    "문서가 이 심볼을 뜻하는지 문서에서 판단한다",
                )
            )
    return problems


def _git_show(root: Path, relative: str) -> str | None:
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"HEAD:{relative}"], capture_output=True, encoding="utf-8"
    )
    return shown.stdout if shown.returncode == 0 else None


def _head_code_links(root: Path, doc: Path) -> set[tuple[Path, str]]:
    text = _git_show(root, display_path(doc, root))
    if text is None:
        return set()
    pairs = set()
    for link in extract_links(doc, text):
        if is_external(link.target):
            continue
        path, anchor = resolve_link(link)
        if path.suffix in CODE_SUFFIXES:
            pairs.add((path, anchor))
    return pairs


def _confirmed(lines: list[str], expected: str) -> bool:
    for line in lines:
        line = line.strip()
        if line.startswith(CONFIRM_PREFIX + expected) and line[len(CONFIRM_PREFIX + expected) :].strip():
            return True
    return False


def check_confirmations(
    project: Project, code_pointers: list[CodePointer], modules: dict[Path, ModuleIndex]
) -> list[Problem]:
    """Report new document pointers that followed an older code pointer without a recorded confirmation.

    @doc: docs/design/Checkers.md#4-포인터-검사기
    """
    root = project.root
    if subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", "HEAD"], capture_output=True).returncode != 0:
        return []
    ongoing = project.docs_dir / ONGOING_DOC
    lines = ongoing.read_text(encoding="utf-8").splitlines() if ongoing.is_file() else []
    head_links: dict[Path, set[tuple[Path, str]]] = {}
    head_modules: dict[Path, ModuleIndex | None] = {}
    problems = []
    for pointer in code_pointers:
        symbol = pointer.symbol
        if pointer.doc not in head_links:
            head_links[pointer.doc] = _head_code_links(root, pointer.doc)
        if (symbol.file, symbol.qualname) in head_links[pointer.doc]:
            continue
        if symbol.file not in head_modules:
            text = _git_show(root, display_path(symbol.file, root))
            head = None if text is None else index_module(symbol.file, root, text.encode("utf-8"))
            head_modules[symbol.file] = head if head is not None and not head.problems else None
        head = head_modules[symbol.file]
        if head is None or not any(
            old.doc == pointer.doc
            and old.symbol.is_related(symbol)
            and (old.symbol.qualname or not symbol.qualname)
            for old in head.doc_pointers
        ):
            continue
        doc = display_path(pointer.doc, root)
        expected = f"{doc} → {_describe(symbol, root)}:"
        if not _confirmed(lines, expected):
            problems.append(
                Problem(
                    pointer.doc,
                    pointer.line,
                    f"포인터 확인 필요: {_describe(symbol, root)}의 @doc이 이 문서 포인터보다 먼저 있었음. "
                    f"문서를 다시 읽고 진행 중 기록에 `{CONFIRM_PREFIX}{expected} <이유>`를 남긴다",
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
    code_pointers, pointer_problems = collect_code_pointers(project, modules)
    problems = (
        [problem for module in modules.values() for problem in module.problems]
        + pointer_problems
        + check_stubs(project, modules)
    )
    if pointer_problems:
        for problem in problems:
            print(problem.format(root))
        print(f"check_pointers: 문서→코드 포인터 문제 {len(pointer_problems)}건을 먼저 고친다. 코드 쪽 검사는 그 뒤에 한다")
        return 1
    problems += (
        check_doc_pointers(root, modules)
        + check_coverage(project, modules)
        + check_reciprocity(root, code_pointers, modules)
        + check_confirmations(project, code_pointers, modules)
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
