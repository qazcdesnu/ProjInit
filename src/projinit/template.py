"""Read the initialization templates and fill their placeholders.

@doc: docs/design/Templates.md#8-구현
"""

import re
from pathlib import Path

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

_PLACEHOLDER_RE = re.compile(r"\{\{([a-z0-9_]+)\}\}")


class TemplateError(Exception):
    """A template with placeholders that have no value.

    @doc: docs/design/Templates.md#8-구현
    """


def render(relative: str, values: dict[str, str]) -> str:
    """Return a template file with every placeholder replaced by its value.

    @doc: docs/design/Templates.md#8-구현
    """
    text = (TEMPLATE_DIR / relative).read_text(encoding="utf-8")
    missing = sorted({name for name in _PLACEHOLDER_RE.findall(text) if name not in values})
    if missing:
        raise TemplateError(f"{relative}: 값이 없는 빈 자리: {', '.join(missing)}")
    return _PLACEHOLDER_RE.sub(lambda match: values[match.group(1)], text)
