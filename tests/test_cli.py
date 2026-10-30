"""Tests for the projinit command.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import unittest
from contextlib import redirect_stderr
from unittest import mock

from projinit import cli


class CliTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_subcommands_hand_arguments_to_their_module(self) -> None:
        for name, target in (("check", "run_checks"), ("commit-msg", "check_commit_msg")):
            with mock.patch.dict(cli._SUBCOMMANDS, {name: mock.Mock(return_value=7)}):
                self.assertEqual(cli.main([name, "--root", "x", "y"]), 7, target)
                cli._SUBCOMMANDS[name].assert_called_once_with(["--root", "x", "y"])

    def test_unknown_subcommand_is_rejected(self) -> None:
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(["nope"])


if __name__ == "__main__":
    unittest.main()
