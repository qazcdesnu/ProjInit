"""Read the project settings file that tells the checkers where things are.

@doc: docs/design/Checkers.md#11-설정
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

# @doc: docs/design/Checkers.md#11-설정
CONFIG_FILE = "projinit.toml"
# @doc: docs/design/Checkers.md#11-설정
INDEX_NAME = "index.md"

# (table, key) in the settings file -> Config field and whether it holds a list of strings.
_KEYS = {
    ("projinit", "version"): ("version", False),
    ("projinit", "source"): ("source", False),
    ("projinit", "command"): ("command", False),
    ("paths", "docs"): ("docs", False),
    ("paths", "entry"): ("entry", False),
    ("paths", "code_roots"): ("code_roots", True),
    ("check", "commands"): ("check_commands", True),
    ("check", "commit_baseline"): ("commit_baseline", False),
}
_TOML_LINE_RE = re.compile(r"line (\d+)")


@dataclass(frozen=True)
class Config:
    """Settings of one project, with defaults for every key.

    @doc: docs/design/Checkers.md#11-설정
    """

    version: str = ""
    source: str = ""
    command: str = ""
    docs: str = "docs"
    entry: str = "CLAUDE.md"
    code_roots: tuple[str, ...] = ("src", "tests")
    check_commands: tuple[str, ...] = ()
    commit_baseline: str = ""
    template: tuple[tuple[str, str], ...] = ()

    @property
    def template_values(self) -> dict[str, str]:
        return dict(self.template)


@dataclass(frozen=True)
class Project:
    """A project to check: its root and settings, and the paths they define.

    @doc: docs/design/Checkers.md#11-설정
    """

    root: Path
    config: Config

    @property
    def docs_dir(self) -> Path:
        return self.root / self.config.docs

    @property
    def entry_doc(self) -> Path:
        return self.root / self.config.entry

    @property
    def index_doc(self) -> Path:
        return self.docs_dir / INDEX_NAME

    @property
    def code_roots(self) -> list[Path]:
        return [self.root / code_root for code_root in self.config.code_roots]


class ConfigError(Exception):
    """A settings file that cannot be read or holds wrong keys or values.

    @doc: docs/design/Checkers.md#11-설정
    """

    def __init__(self, message: str, line: int = 1) -> None:
        super().__init__(message)
        self.line = line


def load_config(root: Path) -> Config:
    """Read the settings file of a project, or return the defaults when there is none.

    @doc: docs/design/Checkers.md#11-설정
    """
    path = root / CONFIG_FILE
    if not path.is_file():
        return Config()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        match = _TOML_LINE_RE.search(str(error))
        raise ConfigError(f"TOML 형식 오류: {error}", int(match.group(1)) if match else 1) from error
    values: dict[str, object] = {}
    for table, entries in data.items():
        if not isinstance(entries, dict):
            raise ConfigError(f"모르는 키: {table}")
        if table == "template":
            values["template"] = tuple((key, _checked(f"template.{key}", value, False)) for key, value in entries.items())
            continue
        for key, value in entries.items():
            if (table, key) not in _KEYS:
                raise ConfigError(f"모르는 키: {table}.{key}")
            name, is_list = _KEYS[(table, key)]
            values[name] = _checked(f"{table}.{key}", value, is_list)
    return Config(**values)


def _checked(key: str, value: object, is_list: bool) -> object:
    if is_list:
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ConfigError(f"{key}는 문자열 목록이어야 함")
        return tuple(value)
    if not isinstance(value, str):
        raise ConfigError(f"{key}는 문자열이어야 함")
    return value


def load_project(root: Path) -> Project:
    """Return the project at a root with its settings.

    @doc: docs/design/Checkers.md#11-설정
    """
    root = root.resolve()
    return Project(root, load_config(root))


def report_config_error(error: ConfigError) -> int:
    """Print a settings error as a problem line and return the exit code.

    @doc: docs/design/Checkers.md#11-설정
    """
    print(f"{CONFIG_FILE}:{error.line}: 설정 오류: {error}")
    return 1
