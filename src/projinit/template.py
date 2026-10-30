"""Read the initialization templates and fill their placeholders.

@doc: docs/design/Templates.md#8-구현
@stub: M2-T5
"""

from pathlib import Path

# @doc: docs/design/Templates.md#8-구현
# @stub: M2-T5
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
# @doc: docs/design/Templates.md#8-구현
# @stub: M2-T5
COMMON_FILES: tuple[str, ...] = ()
# @doc: docs/design/Templates.md#8-구현
# @stub: M2-T5
INITIAL_FILES: tuple[str, ...] = ()


class TemplateError(Exception):
    """A template with placeholders that have no value.

    @doc: docs/design/Templates.md#8-구현
    @stub: M2-T5
    """


def render(relative: str, values: dict[str, str]) -> str:
    """Return a template file with every placeholder replaced by its value.

    @doc: docs/design/Templates.md#8-구현
    @stub: M2-T5
    """
    raise NotImplementedError
