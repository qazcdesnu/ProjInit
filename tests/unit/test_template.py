"""Tests for the initialization templates.

@doc: docs/design/Templates.md#8-구현
"""

import io
import unittest
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from projinit import check_docs, check_tasks
from projinit.doclib import extract_links, is_external, resolve_link
from projinit.config import Config
from projinit.template import AGENT_FILES, COMMON_FILES, INITIAL_FILES, TemplateError, common_files, render

_VALUES = {
    "repository": "git@github.com:me/demo.git",
    "version": "0.1.0",
    "source": "git+https://example.com/ProjInit",
    "projinit": "uvx --from git+https://example.com/ProjInit@v0.1.0 projinit",
    "agents": '["claude", "codex"]',
}
_ALL_COMMON = common_files(Config(agents=("claude", "codex")))
_DEVICE_FILES: tuple[str, ...] = ()


class RenderTest(unittest.TestCase):
    """@doc: docs/design/Templates.md#8-구현"""

    def test_every_template_renders_and_needs_its_values(self) -> None:
        for relative in _ALL_COMMON + INITIAL_FILES:
            self.assertNotIn("{{repository}}", render(relative, _VALUES), relative)
        self.assertIn("git@github.com:me/demo.git", render("docs/PullRequestRule.md", _VALUES))
        with self.assertRaises(TemplateError) as raised:
            render("docs/PullRequestRule.md", {})
        self.assertEqual(str(raised.exception), "docs/PullRequestRule.md: 값이 없는 빈 자리: repository")


class AgentFilesTest(unittest.TestCase):
    """@doc: docs/design/Templates.md#8-구현"""

    def test_common_files_follow_the_configured_agents(self) -> None:
        self.assertEqual(common_files(Config()), COMMON_FILES + AGENT_FILES["claude"])
        self.assertEqual(common_files(Config(agents=("codex",))), COMMON_FILES + AGENT_FILES["codex"])
        both = COMMON_FILES + AGENT_FILES["claude"] + AGENT_FILES["codex"]
        self.assertEqual(common_files(Config(agents=("codex", "claude"))), both)
        self.assertEqual(common_files(Config(agents=())), COMMON_FILES)

    def test_codex_entry_matches_the_claude_entry(self) -> None:
        claude = render("CLAUDE.md", _VALUES).split("\n", 1)
        codex = render("AGENTS.md", _VALUES).split("\n", 1)
        self.assertEqual((claude[0], codex[0]), ("# CLAUDE.md", "# AGENTS.md"))
        self.assertEqual(codex[1], claude[1])

    def test_start_skill_matches_the_start_command(self) -> None:
        command = render(".claude/commands/start.md", _VALUES).split("---\n", 2)[2]
        skill = render(".agents/skills/start/SKILL.md", _VALUES).split("---\n", 2)
        self.assertIn("name: start\n", skill[1])
        self.assertEqual(skill[2], command.replace("CLAUDE.md", "AGENTS.md"))
        self.assertIn("allow_implicit_invocation: false", render(".agents/skills/start/agents/openai.yaml", _VALUES))


class RenderedProjectTest(RepoTestCase):
    """@doc: docs/design/Templates.md#8-구현"""

    def setUp(self) -> None:
        super().setUp()
        for relative in _ALL_COMMON + INITIAL_FILES:
            self.write(relative, render(relative, _VALUES))
        for relative in _DEVICE_FILES:
            self.write(relative, "")

    def test_common_documents_link_only_to_generated_files(self) -> None:
        generated = {(self.root / relative).resolve() for relative in _ALL_COMMON + INITIAL_FILES + _DEVICE_FILES}
        for relative in _ALL_COMMON:
            path = self.root / relative
            for link in extract_links(path, path.read_text(encoding="utf-8")):
                if is_external(link.target) or link.optional:
                    continue
                self.assertIn(resolve_link(link)[0], generated, f"{relative}:{link.line} {link.target}")

    def test_generated_documents_pass_the_document_and_task_checks(self) -> None:
        for checker in (check_docs, check_tasks):
            output = io.StringIO()
            with redirect_stdout(output):
                code = checker.main(["--root", str(self.root)])
            self.assertEqual(code, 0, output.getvalue())


if __name__ == "__main__":
    unittest.main()
