"""Read the project settings file that tells the checkers where things are.

@doc: docs/VerificationTools.md#11-설정
@stub: M1-T2
"""

from dataclasses import dataclass, field
from pathlib import Path

# @doc: docs/VerificationTools.md#11-설정
# @stub: M1-T2
CONFIG_FILE = "projinit.toml"
# @doc: docs/VerificationTools.md#11-설정
# @stub: M1-T2
INDEX_NAME = "index.md"


@dataclass(frozen=True)
class Config:
    """Settings of one project, with defaults for every key.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """

    version: str = ""
    source: str = ""
    command: str = ""
    docs: str = "docs"
    entry: str = "CLAUDE.md"
    code_roots: tuple[str, ...] = ("src", "tests")
    check_commands: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Project:
    """A project to check: its root and settings, and the paths they define.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """

    root: Path
    config: Config

    @property
    def docs_dir(self) -> Path:
        raise NotImplementedError

    @property
    def entry_doc(self) -> Path:
        raise NotImplementedError

    @property
    def index_doc(self) -> Path:
        raise NotImplementedError

    @property
    def code_roots(self) -> list[Path]:
        raise NotImplementedError


class ConfigError(Exception):
    """A settings file that cannot be read or holds wrong keys or values.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """


def load_config(root: Path) -> Config:
    """Read the settings file of a project, or return the defaults when there is none.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """
    raise NotImplementedError


def load_project(root: Path) -> Project:
    """Return the project at a root with its settings.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """
    raise NotImplementedError


def report_config_error(error: ConfigError, root: Path) -> int:
    """Print a settings error as a problem line and return the exit code.

    @doc: docs/VerificationTools.md#11-설정
    @stub: M1-T2
    """
    raise NotImplementedError
