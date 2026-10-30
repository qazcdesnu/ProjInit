"""Verify that the common files match the templates of the configured ProjInit version.

@doc: docs/design/Checkers.md#14-템플릿-일치-검사기
"""

import argparse
import sys
from pathlib import Path

from projinit.config import CONFIG_FILE, ConfigError, Project, load_project, report_config_error
from projinit.doclib import Problem
from projinit.init import package_version
from projinit.template import COMMON_FILES, TemplateError, render, render_values


def check_common_files(project: Project) -> list[Problem]:
    """Report common files that are missing or differ from their filled templates.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    """
    values = render_values(project.config)
    problems = []
    for relative in COMMON_FILES:
        path = project.root / relative
        try:
            expected = render(relative, values)
        except TemplateError as error:
            problems.append(Problem(project.root / CONFIG_FILE, 1, str(error)))
            continue
        if not path.is_file():
            problems.append(Problem(path, 1, "공통 파일 없음"))
        elif path.read_text(encoding="utf-8") != expected:
            problems.append(Problem(path, 1, "템플릿과 다름 (init --refresh-common으로 다시 만든다)"))
    return problems


def check_version(project: Project, running: str) -> list[Problem]:
    """Report a configured version that differs from the running checker's version.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    """
    config = project.config
    if config.command or config.version == running:
        return []
    return [Problem(project.root / CONFIG_FILE, 1, f"설정의 버전 {config.version}과 실행 중인 검사기 버전 {running}이 다름")]


def main(argv: list[str] | None = None) -> int:
    """Run the template and version checks and print problems; return the exit code.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        project = load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    running = package_version()
    problems = check_common_files(project) + check_version(project, running)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_template: 문제 {len(problems)}건")
        return 1
    print(f"check_template: 통과 (공통 파일 {len(COMMON_FILES)}개, 버전 {project.config.version or running})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
