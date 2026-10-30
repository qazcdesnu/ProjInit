"""Tests for the projinit command.

@doc: docs/design/Checkers.md#5-테스트
"""

import io
import unittest
from contextlib import redirect_stderr
from unittest import mock

from projinit import cli


class CliTest(unittest.TestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_subcommands_hand_arguments_to_their_module(self) -> None:
        for name in ("check", "commits", "pr-order"):
            with mock.patch.dict(cli._SUBCOMMANDS, {name: mock.Mock(return_value=7)}):
                self.assertEqual(cli.main([name, "--root", "x", "y"]), 7, name)
                cli._SUBCOMMANDS[name].assert_called_once_with(["--root", "x", "y"])

    def test_commit_msg_hands_the_file_as_message_file(self) -> None:
        with mock.patch("projinit.check_commits.main", return_value=0) as checked:
            self.assertEqual(cli.main(["commit-msg", "MSG", "--root", "x"]), 0)
        checked.assert_called_once_with(["--message-file", "MSG", "--root", "x"])

    def test_unknown_subcommand_is_rejected(self) -> None:
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(["nope"])


if __name__ == "__main__":
    unittest.main()
