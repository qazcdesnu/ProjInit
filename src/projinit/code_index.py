"""Analyse one code file into its symbols and its pointers to documents.

@doc: docs/VerificationTools.md#72-파일-분석
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

from tree_sitter import Node

from projinit.doclib import LANGUAGE_SUFFIXES, Problem
from projinit.languages import LANGUAGES, Definition, parse

_DOC_TAG_RE = re.compile(r"@doc:\s*(\S+)")
_STUB_TAG_RE = re.compile(r"@stub:\s*(\S+)")


@dataclass(frozen=True)
class SymbolRef:
    """A code symbol identified by its file and qualified name; the module is the empty name.

    @doc: docs/VerificationTools.md#72-파일-분석
    """

    file: Path
    qualname: str

    def is_related(self, other: "SymbolRef") -> bool:
        if self.file != other.file:
            return False
        mine, theirs = self.qualname, other.qualname
        return (
            mine == theirs
            or not mine
            or not theirs
            or mine.startswith(theirs + ".")
            or theirs.startswith(mine + ".")
        )


@dataclass(frozen=True)
class DocPointer:
    """A pointer from a code symbol to the document it is based on.

    @doc: docs/VerificationTools.md#72-파일-분석
    """

    symbol: SymbolRef
    line: int
    doc: Path
    anchor: str


@dataclass
class ModuleIndex:
    """The syntax tree analysis of one code file.

    @doc: docs/VerificationTools.md#72-파일-분석
    """

    path: Path
    symbols: dict[str, list[Definition]] = field(default_factory=dict)
    doc_pointers: list[DocPointer] = field(default_factory=list)
    problems: list[Problem] = field(default_factory=list)
    has_code: bool = False
    stubs: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class _Layout:
    """Where comments and code sit in a file, by zero-based row."""

    comments: list[Node] = field(default_factory=list)
    comment_rows: set[int] = field(default_factory=set)
    code_rows: set[int] = field(default_factory=set)
    first_code: tuple[int, int] | None = None


def index_module(path: Path, root: Path) -> ModuleIndex:
    """Parse a code file into its symbols and its pointers to documents.

    @doc: docs/VerificationTools.md#72-파일-분석
    """
    index = ModuleIndex(path)
    language = LANGUAGES[LANGUAGE_SUFFIXES[path.suffix]]
    tree = parse(language, path.read_bytes())
    error = _first_error(tree.root_node)
    if error is not None:
        index.problems.append(Problem(path, error.start_point.row + 1, "파싱 실패: 구문 오류"))
        return index
    layout = _scan(tree.root_node, language.comment_types)
    index.has_code = layout.first_code is not None
    index.symbols[""] = []
    starts: dict[int, str] = {}
    definitions = language.walk(tree.root_node)
    for definition in definitions:
        index.symbols.setdefault(definition.qualname, []).append(definition)
        starts.setdefault(definition.line, definition.qualname)
    docstrings = [(definition.qualname, definition.docstring) for definition in definitions]
    if language.module_docstring is not None:
        docstrings.insert(0, ("", language.module_docstring(tree.root_node)))
    for qualname, docstring in docstrings:
        if docstring is not None:
            _add_docstring_pointers(index, root, qualname, docstring)
            _add_stubs(index, *docstring)
    for comment in layout.comments:
        _add_comment_pointers(index, root, comment, layout, starts)
        _add_stubs(index, comment.start_point.row + 1, comment.text.decode("utf-8"))
    index.stubs.sort()
    return index


def _add_stubs(index: ModuleIndex, start: int, text: str) -> None:
    for offset, line in enumerate(text.splitlines()):
        for match in _STUB_TAG_RE.finditer(line):
            index.stubs.append((start + offset, match.group(1)))


def _first_error(node: Node) -> Node | None:
    if not node.has_error and not node.is_missing:
        return None
    if node.is_error or node.is_missing:
        return node
    for child in node.children:
        found = _first_error(child)
        if found is not None:
            return found
    return node


def _last_row(node: Node) -> int:
    # Line comments include their newline, so they end at column 0 of the following row.
    end = node.end_point
    if end.column == 0 and end.row > node.start_point.row:
        return end.row - 1
    return end.row


def _scan(root: Node, comment_types: frozenset[str]) -> _Layout:
    layout = _Layout()
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type in comment_types:
            layout.comments.append(node)
            layout.comment_rows.update(range(node.start_point.row, _last_row(node) + 1))
        elif node.child_count == 0:
            if node.end_byte > node.start_byte:
                layout.code_rows.update(range(node.start_point.row, _last_row(node) + 1))
                start = (node.start_point.row, node.start_point.column)
                if layout.first_code is None or start < layout.first_code:
                    layout.first_code = start
        else:
            stack.extend(reversed(node.children))
    layout.comments.sort(key=lambda comment: comment.start_byte)
    return layout


def _make_doc_pointer(symbol: SymbolRef, line: int, target: str, root: Path) -> DocPointer:
    path_part, _, anchor = target.partition("#")
    return DocPointer(symbol, line, (root / unquote(path_part)).resolve(), unquote(anchor))


def _add_docstring_pointers(index: ModuleIndex, root: Path, qualname: str, docstring: tuple[int, str]) -> None:
    start, text = docstring
    symbol = SymbolRef(index.path, qualname)
    for offset, line in enumerate(text.splitlines()):
        for match in _DOC_TAG_RE.finditer(line):
            index.doc_pointers.append(_make_doc_pointer(symbol, start + offset, match.group(1), root))


def _add_comment_pointers(
    index: ModuleIndex, root: Path, comment: Node, layout: _Layout, starts: dict[int, str]
) -> None:
    first_row = comment.start_point.row
    tags = [
        (first_row + 1 + offset, match.group(1))
        for offset, line in enumerate(comment.text.decode("utf-8").splitlines())
        for match in _DOC_TAG_RE.finditer(line)
    ]
    if not tags:
        return
    if first_row in layout.code_rows or _last_row(comment) in layout.code_rows:
        index.problems.append(Problem(index.path, tags[0][0], "코드와 같은 줄의 @doc 주석은 허용되지 않음"))
        return
    owner = _comment_owner(comment, layout, starts)
    if owner is None:
        index.problems.append(Problem(index.path, tags[0][0], "@doc 주석 아래에 심볼 정의가 없음"))
        return
    symbol = SymbolRef(index.path, owner)
    for line, target in tags:
        index.doc_pointers.append(_make_doc_pointer(symbol, line, target, root))


def _comment_owner(comment: Node, layout: _Layout, starts: dict[int, str]) -> str | None:
    row = _last_row(comment) + 1
    while row in layout.comment_rows and row not in layout.code_rows:
        row += 1
    if row in layout.code_rows and row + 1 in starts:
        return starts[row + 1]
    start = (comment.start_point.row, comment.start_point.column)
    if layout.first_code is None or start < layout.first_code:
        return ""
    return None
