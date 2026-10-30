"""Tests for reading the project settings file.

@doc: docs/design/Checkers.md#5-테스트
"""

import io
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit.check_docs import main as check_docs_main
from projinit.config import Config, ConfigError, load_config, load_project


class ConfigTest(RepoTestCase):
    """@doc: docs/design/Checkers.md#5-테스트"""

    def test_defaults_without_a_settings_file(self) -> None:
        self.assertEqual(load_config(self.root), Config())
        self.assertEqual(Config().code_roots, ("src", "tests"))

    def test_reads_settings(self) -> None:
        self.write(
            "projinit.toml",
            '[projinit]\nversion = "0.2.0"\n\n[paths]\ndocs = "doc"\ncode_roots = ["lib"]\n\n'
            '[check]\ncommands = ["cargo test"]\ncommit_baseline = "abc1234"\n',
        )
        config = load_config(self.root)
        self.assertEqual((config.version, config.docs, config.entry), ("0.2.0", "doc", "CLAUDE.md"))
        self.assertEqual((config.code_roots, config.check_commands), (("lib",), ("cargo test",)))
        self.assertEqual(config.commit_baseline, "abc1234")

    def test_reports_bad_settings(self) -> None:
        cases = {
            "[paths]\ndocs = \n": "TOML 형식 오류",
            "[paths]\ndoc = \"x\"\n": "모르는 키: paths.doc",
            "[extra]\nx = 1\n": "모르는 키: extra.x",
            "name = \"x\"\n": "모르는 키: name",
            "[paths]\ndocs = 3\n": "paths.docs는 문자열이어야 함",
            "[check]\ncommands = \"cargo test\"\n": "check.commands는 문자열 목록이어야 함",
        }
        for text, message in cases.items():
            self.write("projinit.toml", text)
            with self.assertRaises(ConfigError, msg=text) as raised:
                load_config(self.root)
            self.assertIn(message, str(raised.exception))
        self.write("projinit.toml", "[paths]\n\ndocs = \n")
        with self.assertRaises(ConfigError) as raised:
            load_config(self.root)
        self.assertEqual(raised.exception.line, 3)

    def test_project_paths(self) -> None:
        self.write("projinit.toml", '[paths]\ndocs = "doc"\nentry = "AGENTS.md"\ncode_roots = ["a", "b"]\n')
        project = load_project(self.root)
        self.assertEqual(project.docs_dir, self.root / "doc")
        self.assertEqual(project.entry_doc, self.root / "AGENTS.md")
        self.assertEqual(project.index_doc, self.root / "doc" / "index.md")
        self.assertEqual(project.code_roots, [self.root / "a", self.root / "b"])

    def test_checkers_report_settings_errors(self) -> None:
        self.write("projinit.toml", "[paths]\nnope = 1\n")
        output = io.StringIO()
        with redirect_stdout(output):
            code = check_docs_main(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "projinit.toml:1: 설정 오류: 모르는 키: paths.nope\n")
