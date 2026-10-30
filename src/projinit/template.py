"""Read the initialization templates and fill their placeholders.

@doc: docs/design/Templates.md#8-구현
"""

import re
from pathlib import Path

from projinit.check_hooks import projinit_command
from projinit.config import Config

# @doc: docs/design/Templates.md#8-구현
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
# @doc: docs/design/Templates.md#8-구현
COMMON_FILES = (
    "CLAUDE.md",
    "docs/DocumentationRule.md",
    "docs/CodeRule.md",
    "docs/Traceability.md",
    "docs/TaskRule.md",
    "docs/CommitRule.md",
    "docs/PullRequestRule.md",
    "docs/VerificationTools.md",
    ".claude/settings.json",
    ".githooks/pre-commit",
    ".githooks/commit-msg",
    ".github/workflows/verify.yml",
    ".github/pull_request_template.md",
)
# @doc: docs/design/Templates.md#8-구현
INITIAL_FILES = (
    "docs/index.md",
    "docs/Roadmap.md",
    "docs/Ongoing.md",
    "docs/Done.md",
    "docs/Issue.md",
    "projinit.toml",
)

# @doc: docs/design/Templates.md#8-구현
EXECUTABLE_FILES = (".githooks/pre-commit", ".githooks/commit-msg")

_PLACEHOLDER_RE = re.compile(r"\{\{([a-z0-9_]+)\}\}")


class TemplateError(Exception):
    """A template with placeholders that have no value.

    @doc: docs/design/Templates.md#8-구현
    """


def render_values(config: Config) -> dict[str, str]:
    """Return the placeholder values: the template table and the run command built from the settings.

    @doc: docs/design/Templates.md#8-구현
    """
    values = config.template_values
    command = projinit_command(config)
    if command is not None:
        values["projinit"] = command
    return values


def render(relative: str, values: dict[str, str]) -> str:
    """Return a template file with every placeholder replaced by its value.

    @doc: docs/design/Templates.md#8-구현
    """
    text = (TEMPLATE_DIR / relative).read_text(encoding="utf-8")
    missing = sorted({name for name in _PLACEHOLDER_RE.findall(text) if name not in values})
    if missing:
        raise TemplateError(f"{relative}: 값이 없는 빈 자리: {', '.join(missing)}")
    return _PLACEHOLDER_RE.sub(lambda match: values[match.group(1)], text)
