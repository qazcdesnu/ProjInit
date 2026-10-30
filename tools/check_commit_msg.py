"""Verify that a commit message subject starts with known work IDs.

@doc: docs/VerificationTools.md#10-커밋-메시지-검사기
@stub: M0-T6
"""

import sys

# @doc: docs/VerificationTools.md#10-커밋-메시지-검사기
# @stub: M0-T6
GIT_SUBJECT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")


def check_message(text: str, known: set[str]) -> list[str]:
    """Return the problems of a commit message against the known work IDs.

    @doc: docs/VerificationTools.md#10-커밋-메시지-검사기
    @stub: M0-T6
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Check the commit message file given by the commit-msg hook; return the exit code.

    @doc: docs/VerificationTools.md#10-커밋-메시지-검사기
    @stub: M0-T6
    """
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
