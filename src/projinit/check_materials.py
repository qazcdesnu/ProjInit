"""Verify the reference and legacy folders: every file listed, legacy projects left as they were.

@doc: docs/design/Checkers.md#15-자료-폴더-검사기
"""

from projinit.config import Project
from projinit.doclib import Problem

# @doc: docs/design/Checkers.md#15-자료-폴더-검사기
REFERENCE_DOC = "Reference.md"
# @doc: docs/design/Checkers.md#15-자료-폴더-검사기
LEGACY_DOC = "Legacy.md"


def check_listed(project: Project) -> list[Problem]:
    """Report material files that their folder's list document does not link.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    @stub: M6-T1
    """
    raise NotImplementedError


def check_legacy_frozen(project: Project) -> list[Problem]:
    """Report changes inside legacy projects already committed to HEAD.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    @stub: M6-T1
    """
    raise NotImplementedError


def check_nested_git(project: Project) -> list[Problem]:
    """Report .git entries under the legacy folder.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    @stub: M6-T1
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Run every material folder check and print problems; return the exit code.

    @doc: docs/design/Checkers.md#15-자료-폴더-검사기
    @stub: M6-T1
    """
    raise NotImplementedError
