"""Verify that the common files match the templates of the configured ProjInit version.

@doc: docs/design/Checkers.md#14-템플릿-일치-검사기
@stub: M2-T6
"""

import sys

from projinit.config import Project
from projinit.doclib import Problem


def check_common_files(project: Project) -> list[Problem]:
    """Report common files that are missing or differ from their filled templates.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    @stub: M2-T6
    """
    raise NotImplementedError


def check_version(project: Project, running: str) -> list[Problem]:
    """Report a configured version that differs from the running checker's version.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    @stub: M2-T6
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Run the template and version checks and print problems; return the exit code.

    @doc: docs/design/Checkers.md#14-템플릿-일치-검사기
    @stub: M2-T6
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
