"""Verify the reference and legacy folders: every file listed, legacy projects left as they were.

@doc: docs/design/Checkers.md#15-자료-폴더-검사기
"""

import argparse
import subprocess
import sys
from pathlib import Path

from projinit.config import ConfigError, Project, load_project, report_config_error
from projinit.doclib import Problem, extract_links, is_external, resolve_link

# @doc: docs/design/Checkers.md#15-자료-폴더-검사기
REFERENCE_DOC = "Reference.md"
# @doc: docs/design/Checkers.md#15-자료-폴더-검사기
LEGACY_DOC = "Legacy.md"


def _material_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.rglob("*") if path.is_file() and ".git" not in path.relative_to(folder).parts)


def check_listed(project: Project) -> list[Problem]:
    """Report material files that their folder's list document does not link.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    problems = []
    for folder, name in ((project.reference_dir, REFERENCE_DOC), (project.legacy_dir, LEGACY_DOC)):
        files = _material_files(folder)
        if not files:
            continue
        list_doc = project.docs_dir / name
        if not list_doc.is_file():
            problems.append(Problem(files[0], 1, f"목록 문서 없음: {project.config.docs}/{name}"))
            continue
        linked = {
            resolve_link(link)[0]
            for link in extract_links(list_doc.resolve(), list_doc.read_text(encoding="utf-8"))
            if not is_external(link.target)
        }
        top = folder.resolve()
        for path in files:
            path = path.resolve()
            if not any(candidate in linked for candidate in (path, *path.parents) if candidate.is_relative_to(top)):
                problems.append(Problem(path, 1, f"목록 문서에 없는 자료: {project.config.docs}/{name}에 링크 필요"))
    return problems


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, encoding="utf-8")


def check_legacy_frozen(project: Project) -> list[Problem]:
    """Report changes inside legacy projects already committed to HEAD.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    root = project.root
    legacy = project.config.legacy.strip("/")
    listed = _git(root, "ls-tree", "--name-only", "HEAD", f"{legacy}/")
    if listed.returncode != 0:
        return []
    committed = {line for line in listed.stdout.splitlines() if line}
    if not committed:
        return []
    status = _git(root, "-c", "core.quotePath=false", "status", "--porcelain", "--untracked-files=all", "--", f"{legacy}/")
    problems = []
    for line in status.stdout.splitlines():
        for relative in line[3:].split(" -> "):
            if any(relative == folder or relative.startswith(f"{folder}/") for folder in committed):
                problems.append(Problem(root / relative, 1, "커밋된 기존 프로젝트를 바꿈: 기존 프로젝트는 고치지 않는다"))
    return problems


def check_nested_git(project: Project) -> list[Problem]:
    """Report .git entries under the legacy folder.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    if not project.legacy_dir.is_dir():
        return []
    return [Problem(path, 1, "기존 프로젝트 안의 .git: 빼고 넣는다") for path in sorted(project.legacy_dir.rglob(".git"))]


def main(argv: list[str] | None = None) -> int:
    """Run every material folder check and print problems; return the exit code.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    problems = check_listed(project) + check_legacy_frozen(project) + check_nested_git(project)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_materials: 문제 {len(problems)}건")
        return 1
    counts = (len(_material_files(project.reference_dir)), len(_material_files(project.legacy_dir)))
    print(f"check_materials: 통과 (참고 자료 {counts[0]}개, 기존 프로젝트 파일 {counts[1]}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
