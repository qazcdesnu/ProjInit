"""Shared problem reporting, file discovery and markdown parsing for the checkers.

@doc: docs/design/Checkers.md#2-공통-모듈
"""

import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from projinit.config import Project

# @doc: docs/design/Checkers.md#2-공통-모듈
README_DOC = "README.md"
# @doc: docs/design/Checkers.md#2-공통-모듈
LANGUAGE_SUFFIXES = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "tsx",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
    ".go": "go",
    ".java": "java",
}
# @doc: docs/design/Checkers.md#2-공통-모듈
CODE_SUFFIXES = tuple(LANGUAGE_SUFFIXES)

_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")
_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
# A backreference so that ``` `` `x` `` ``` style spans close on the same run length.
_INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
# @doc: docs/design/Checkers.md#2-공통-모듈
OPTIONAL_TITLE = "선택"
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")


@dataclass(frozen=True)
class Problem:
    """A single verification failure at a file location.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """

    path: Path
    line: int
    message: str

    def format(self, root: Path) -> str:
        return f"{display_path(self.path, root)}:{self.line}: {self.message}"


def actual_case(path: Path, root: Path) -> str | None:
    """Return the on-disk spelling of a path inside the root when it differs from the given one only in case.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    root = root.resolve()
    absolute = path if path.is_absolute() else root / path
    absolute = Path(os.path.normpath(absolute))
    if not absolute.is_relative_to(root) or not absolute.exists():
        return None
    current, parts, differs = root, [], False
    for part in absolute.relative_to(root).parts:
        try:
            entries = os.listdir(current)
        except OSError:
            return None
        if part not in entries:
            matches = [entry for entry in entries if entry.lower() == part.lower()]
            if not matches:
                return None
            part, differs = matches[0], True
        parts.append(part)
        current = current / part
    return "/".join(parts) if differs else None


def display_path(path: Path, root: Path) -> str:
    """Return the path relative to the repository root when it lies inside it.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


@dataclass(frozen=True)
class Link:
    """A markdown link found in a document.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """

    source: Path
    line: int
    text: str
    target: str
    optional: bool = False


def find_doc_files(project: Project) -> list[Path]:
    """Return the entry documents, the README if any, and every markdown file under the docs directory.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    docs = [entry for entry in project.entry_docs if entry.is_file()]
    readme = project.root / README_DOC
    if readme.is_file():
        docs.append(readme)
    docs_dir = project.docs_dir
    if docs_dir.is_dir():
        docs.extend(sorted(docs_dir.rglob("*.md")))
    return docs


def find_code_files(project: Project) -> list[Path]:
    """Return every code file under the code roots, skipping missing roots.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    files = []
    for directory in project.code_roots:
        if not directory.is_dir():
            continue
        for suffix in CODE_SUFFIXES:
            files.extend(sorted(directory.rglob(f"*{suffix}")))
    return files


def iter_prose_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, line) for lines outside fenced code blocks.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        match = _FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def strip_inline_code(line: str) -> str:
    """Remove inline code spans from a line.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    return _INLINE_CODE_RE.sub("", line)


def extract_links(source: Path, text: str) -> list[Link]:
    """Return links in prose, ignoring images, fenced code blocks and inline code.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    links = []
    for number, line in iter_prose_lines(text):
        for match in _LINK_RE.finditer(strip_inline_code(line)):
            links.append(Link(source, number, match.group(1), match.group(2), match.group(3) == OPTIONAL_TITLE))
    return links


def is_external(target: str) -> bool:
    """Return whether the link target leaves the repository.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    return target.startswith(_EXTERNAL_PREFIXES)


def resolve_link(link: Link) -> tuple[Path, str]:
    """Split a link target into an absolute path and a decoded anchor.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    path_part, _, anchor = link.target.partition("#")
    if path_part:
        path = (link.source.parent / unquote(path_part)).resolve()
    else:
        path = link.source.resolve()
    return path, unquote(anchor)


def slugify(heading: str) -> str:
    """Turn heading text into its anchor.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    text = heading.replace("`", "")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def section_anchor(text: str, line: int) -> str:
    """Return the anchor of the section a line belongs to, or an empty string before any heading.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    return next((anchor for number, anchor in reversed(_heading_lines(text)) if number <= line), "")


def _heading_lines(text: str) -> list[tuple[int, str]]:
    headings = []
    seen: dict[str, int] = {}
    for number, line in iter_prose_lines(text):
        match = _HEADING_RE.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        headings.append((number, slug if count == 0 else f"{slug}-{count}"))
    return headings


def heading_anchors(text: str) -> set[str]:
    """Return the anchors of every ATX heading outside code blocks.

    @doc: docs/design/Checkers.md#2-공통-모듈
    """
    return {anchor for _, anchor in _heading_lines(text)}
