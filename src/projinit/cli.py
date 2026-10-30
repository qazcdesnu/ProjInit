"""The projinit command and the subcommands that the hooks of a project call.

@doc: docs/VerificationTools.md#1-실행-방법
"""

import argparse
import sys
from collections.abc import Callable

from projinit import check_commit_msg, run_checks

_SUBCOMMANDS: dict[str, Callable[[list[str] | None], int]] = {
    "check": run_checks.main,
    "commit-msg": check_commit_msg.main,
}


def main(argv: list[str] | None = None) -> int:
    """Hand the remaining arguments to the module behind the subcommand; return its exit code.

    @doc: docs/VerificationTools.md#1-실행-방법
    """
    parser = argparse.ArgumentParser(prog="projinit", description=__doc__.splitlines()[0])
    parser.add_argument("subcommand", choices=sorted(_SUBCOMMANDS))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parsed = parser.parse_args(argv)
    return _SUBCOMMANDS[parsed.subcommand](parsed.args)


if __name__ == "__main__":
    sys.exit(main())
