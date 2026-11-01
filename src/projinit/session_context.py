"""Print the session start context: the reference materials the agent should know about.

@doc: docs/design/Checkers.md#16-세션-시작-안내
"""

import argparse
import sys
from pathlib import Path

from projinit.check_materials import REFERENCE_DOC, material_files, unlisted_files
from projinit.config import Project, load_project
from projinit.doclib import display_path, iter_prose_lines

# @doc: docs/design/Checkers.md#16-세션-시작-안내
MAX_ITEMS = 100


def reference_context(project: Project) -> str:
    """Return the context text about the reference folder, or an empty string when it has no files.

    @doc: docs/design/Checkers.md#16-세션-시작-안내
    """
    files = material_files(project.reference_dir)
    if not files:
        return ""
    docs = project.config.docs.strip("/")
    folder = project.config.reference.strip("/")
    list_name = f"{docs}/{REFERENCE_DOC}"
    lines = [
        f"참고 자료: {folder}/에 자료 {len(files)}개가 있다. 작업을 시작할 때 이 중 관련 자료를 찾아 읽고 "
        f"진행 중 기록의 참고 자료 줄에 적는다({docs}/MaterialRule.md의 3.4 쓰는 방법)."
    ]
    list_doc = project.docs_dir / REFERENCE_DOC
    if list_doc.is_file():
        items = [line for _, line in iter_prose_lines(list_doc.read_text(encoding="utf-8")) if line.startswith("- ")]
        lines.append(f"목록 문서 {list_name}의 항목:")
        lines += _capped(items)
    else:
        lines.append(f"목록 문서 {list_name} 없음.")
    unlisted = unlisted_files(project.reference_dir, list_doc)
    if unlisted:
        lines.append("목록에 없는 자료:")
        lines += _capped([f"- {display_path(path, project.root)}" for path in unlisted])
    return "\n".join(lines)


def _capped(items: list[str]) -> list[str]:
    if len(items) <= MAX_ITEMS:
        return items
    return items[:MAX_ITEMS] + [f"- … 외 {len(items) - MAX_ITEMS}개"]


def main(argv: list[str] | None = None) -> int:
    """Print the session context and return 0 even when something goes wrong.

    @doc: docs/design/Checkers.md#16-세션-시작-안내
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        text = reference_context(load_project(root))
    except Exception:  # noqa: BLE001 - the session must start even when the context cannot be built
        return 0
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
