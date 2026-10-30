"""The projinit init command: create the rule system in a folder, or rewrite its common documents.

@doc: docs/design/Templates.md#9-초기화-명령
@stub: M2-T2
"""

import sys
from pathlib import Path

from projinit.config import Project

# @doc: docs/design/Templates.md#9-초기화-명령
# @stub: M2-T2
DEFAULT_SOURCE = "git+https://github.com/qazcdesnu/ProjInit"
# @doc: docs/design/Templates.md#9-초기화-명령
# @stub: M2-T2
NO_REPOSITORY = "아직 없음"


class InitError(Exception):
    """A folder that cannot be initialized.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """


def package_version() -> str:
    """Return the version of the running projinit package.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """
    raise NotImplementedError


def repository_url(root: Path, given: str | None) -> str:
    """Return the remote repository address for the templates.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """
    raise NotImplementedError


def init_project(root: Path, repository: str | None) -> list[str]:
    """Write the common and initial files into a folder and return their relative paths.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """
    raise NotImplementedError


def refresh_common(project: Project) -> list[str]:
    """Rewrite the common files from the templates and return the ones that changed.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Initialize a folder or refresh its common documents; return the exit code.

    @doc: docs/design/Templates.md#9-초기화-명령
    @stub: M2-T2
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
