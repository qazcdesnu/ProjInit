"""The projinit upgrade command: move an initialized project to the running ProjInit version.

@doc: docs/design/Templates.md#10-갱신-명령
@stub: M5-T1
"""

import sys
from pathlib import Path

# @doc: docs/design/Templates.md#10-갱신-명령
# @stub: M5-T1
NEXT_STEP = ""


class UpgradeError(Exception):
    """A project that cannot be upgraded.

    @doc: docs/design/Templates.md#10-갱신-명령
    @stub: M5-T1
    """


def set_version(text: str, version: str) -> str:
    """Return the settings text with the projinit version replaced.

    @doc: docs/design/Templates.md#10-갱신-명령
    @stub: M5-T1
    """
    raise NotImplementedError


def upgrade_project(root: Path) -> tuple[str, str, list[str]]:
    """Move a project to the running version and return (old, new, rewritten files).

    @doc: docs/design/Templates.md#10-갱신-명령
    @stub: M5-T1
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Upgrade a project and print what changed; return the exit code.

    @doc: docs/design/Templates.md#10-갱신-명령
    @stub: M5-T1
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
