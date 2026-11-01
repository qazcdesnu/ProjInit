"""A real project built once from the current code, copied per scenario and broken on purpose.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import shlex
import sys
import unittest
from pathlib import Path

# @doc: docs/design/Checkers.md#51-시나리오-테스트
COMMAND = f"{shlex.quote(sys.executable)} -m projinit.cli"


def baseline() -> Path:
    """Build the baseline project once per process and return its root.

    @doc: docs/design/Checkers.md#51-시나리오-테스트
    @stub: M7-T3
    """
    raise NotImplementedError


class ScenarioCase(unittest.TestCase):
    """A test case with a fresh copy of the baseline project as self.root.

    @doc: docs/design/Checkers.md#51-시나리오-테스트
    """

    def checks(self) -> dict[str, tuple[int, str]]:
        """Run every checker in this process and return name -> (exit code, output).

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        @stub: M7-T3
        """
        raise NotImplementedError

    def assert_caught(self, checker: str, needle: str) -> None:
        """Assert that the checker fails and its output holds the needle.

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        @stub: M7-T3
        """
        raise NotImplementedError

    def assert_clean(self) -> None:
        """Assert that every checker passes.

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        @stub: M7-T3
        """
        raise NotImplementedError
