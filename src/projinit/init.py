"""The projinit init command: create the rule system in a folder, or rewrite its common documents.

@doc: docs/design/Templates.md#9-초기화-명령
"""

import argparse
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

from projinit.config import Config, ConfigError, Project, load_project, report_config_error
from projinit.template import COMMON_FILES, EXECUTABLE_FILES, INITIAL_FILES, TemplateError, render, render_values

# @doc: docs/design/Templates.md#9-초기화-명령
DEFAULT_SOURCE = "git+https://github.com/qazcdesnu/ProjInit"
# @doc: docs/design/Templates.md#9-초기화-명령
NO_REPOSITORY = "아직 없음"
# @doc: docs/design/Templates.md#9-초기화-명령
START_HINT = "이 폴더에서 Claude Code를 열고 /start를 입력하면 첫 작업을 시작합니다."


class InitError(Exception):
    """A folder that cannot be initialized.

    @doc: docs/design/Templates.md#9-초기화-명령
    """


def package_version() -> str:
    """Return the version of the running projinit package.

    @doc: docs/design/Templates.md#9-초기화-명령
    """
    return version("projinit")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def repository_url(root: Path, given: str | None) -> str:
    """Return the remote repository address for the templates.

    @doc: docs/design/Templates.md#9-초기화-명령
    """
    if given:
        return given
    if root.is_dir():
        origin = _git(root, "remote", "get-url", "origin")
        if origin.returncode == 0 and origin.stdout.strip():
            return origin.stdout.strip()
    return NO_REPOSITORY


def init_project(root: Path, repository: str | None) -> list[str]:
    """Write the common and initial files into a folder and return their relative paths.

    @doc: docs/design/Templates.md#9-초기화-명령
    """
    root = root.resolve()
    targets = COMMON_FILES + INITIAL_FILES
    existing = [relative for relative in targets if (root / relative).exists()]
    if existing:
        raise InitError(f"이미 있는 파일이 있어 초기화하지 않음: {', '.join(existing)}")
    settings = {"version": package_version(), "source": DEFAULT_SOURCE, "repository": repository_url(root, repository)}
    config = Config(
        version=settings["version"], source=settings["source"], template=(("repository", settings["repository"]),)
    )
    values = {**render_values(config), **settings}
    # Render everything first so that a template error leaves the folder untouched.
    rendered = {relative: render(relative, values) for relative in targets}
    for relative, text in rendered.items():
        _write(root / relative, text, relative in EXECUTABLE_FILES)
    if _git(root, "rev-parse", "--is-inside-work-tree").returncode != 0:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=root, check=True)
    return list(targets)


def _write(path: Path, text: str, executable: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def refresh_common(project: Project) -> list[str]:
    """Rewrite the common files from the templates and return the ones that changed.

    @doc: docs/design/Templates.md#9-초기화-명령
    """
    values = render_values(project.config)
    rendered = {relative: render(relative, values) for relative in COMMON_FILES}
    changed = []
    for relative, text in rendered.items():
        path = project.root / relative
        executable = relative in EXECUTABLE_FILES
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            if executable:
                path.chmod(0o755)
            continue
        _write(path, text, executable)
        changed.append(relative)
    return changed


def main(argv: list[str] | None = None) -> int:
    """Initialize a folder or refresh its common documents; return the exit code.

    @doc: docs/design/Templates.md#9-초기화-명령
    """
    parser = argparse.ArgumentParser(prog="projinit init", description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--repository")
    parser.add_argument("--refresh-common", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.refresh_common:
            changed = refresh_common(load_project(args.root))
            for relative in changed:
                print(f"다시 씀: {relative}")
            print(f"init: 공통 문서 {len(changed)}개를 다시 씀")
        else:
            created = init_project(args.root, args.repository)
            for relative in created:
                print(f"만듦: {relative}")
            print(f"init: 파일 {len(created)}개를 만듦")
            print(START_HINT)
    except ConfigError as error:
        return report_config_error(error)
    except (InitError, TemplateError) as error:
        print(f"init: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
