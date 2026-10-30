"""Temporary entry point for the hooks until the projinit command replaces it.

@doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
"""

import sys

from projinit.check_commit_msg import main

if __name__ == "__main__":
    sys.exit(main())
