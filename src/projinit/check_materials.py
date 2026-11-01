"""Verify the material folders: legacy files listed and left as they were, private files kept out of git.

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


def material_files(folder: Path) -> list[Path]:
    """Return the files under a material folder, outside .git, sorted.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.rglob("*") if path.is_file() and ".git" not in path.relative_to(folder).parts)


def unlisted_files(folder: Path, list_doc: Path) -> list[Path]:
    """Return the files of a material folder that the list document does not link.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    files = material_files(folder)
    if not list_doc.is_file():
        return files
    linked = {
        resolve_link(link)[0]
        for link in extract_links(list_doc.resolve(), list_doc.read_text(encoding="utf-8"))
        if not is_external(link.target)
    }
    top = folder.resolve()
    return [
        path
        for path in files
        if not any(candidate in linked for candidate in (path.resolve(), *path.resolve().parents) if candidate.is_relative_to(top))
    ]


def check_listed(project: Project) -> list[Problem]:
    """Report legacy files that the legacy list document does not link.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    files = material_files(project.legacy_dir)
    if not files:
        return []
    list_doc = project.docs_dir / LEGACY_DOC
    if not list_doc.is_file():
        return [Problem(files[0], 1, f"목록 문서 없음: {project.config.docs}/{LEGACY_DOC}")]
    return [
        Problem(path, 1, f"목록 문서에 없는 자료: {project.config.docs}/{LEGACY_DOC}에 링크 필요")
        for path in unlisted_files(project.legacy_dir, list_doc)
    ]


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


def check_private(project: Project) -> list[Problem]:
    """Report private files that git does not ignore or already tracks.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    """
    root = project.root
    files = material_files(project.private_dir)
    if not files or _git(root, "rev-parse", "--is-inside-work-tree").returncode != 0:
        return []
    private = project.config.private.strip("/")
    tracked = _git(root, "-c", "core.quotePath=false", "ls-files", "--", f"{private}/").stdout.splitlines()
    problems = [Problem(root / path, 1, "로컬 자료가 git에 추적됨: git rm --cached로 빼고 커밋하지 않는다") for path in tracked if path]
    relative = [path.relative_to(root).as_posix() for path in files]
    ignored = subprocess.run(
        ["git", "-C", str(root), "-c", "core.quotePath=false", "check-ignore", "--no-index", "--stdin"],
        input="\n".join(relative) + "\n",
        capture_output=True,
        encoding="utf-8",
    ).stdout.splitlines()
    if set(relative) - set(ignored):
        problems.append(
            Problem(project.private_dir, 1, f"로컬 자료가 git에서 빠지지 않음: .gitignore에 /{private}/를 더한다")
        )
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
    problems = check_listed(project) + check_legacy_frozen(project) + check_private(project) + check_nested_git(project)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_materials: 문제 {len(problems)}건")
        return 1
    counts = (len(material_files(project.reference_dir)), len(material_files(project.legacy_dir)))
    print(f"check_materials: 통과 (참고 자료 {counts[0]}개, 기존 프로젝트 파일 {counts[1]}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
