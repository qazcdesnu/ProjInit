"""Print the session start context: the reference materials the agent should know about.

@doc: docs/design/Checkers.md#16-세션-시작-안내
"""

import argparse
import sys
from pathlib import Path

from projinit.config import Project

# @doc: docs/design/Checkers.md#16-세션-시작-안내
MAX_ITEMS = 100


def reference_context(project: Project) -> str:
    """Return the context text about the reference folder, or an empty string when it has no files.

    @doc: docs/design/Checkers.md#16-세션-시작-안내
    @stub: I23
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Print the session context and return 0 even when something goes wrong.

    @doc: docs/design/Checkers.md#16-세션-시작-안내
    @stub: I23
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
