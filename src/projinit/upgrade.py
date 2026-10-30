"""The projinit upgrade command: move an initialized project to the running ProjInit version.

@doc: docs/design/Templates.md#10-갱신-명령
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from projinit.config import CONFIG_FILE, ConfigError, load_project, report_config_error
from projinit.init import package_version, refresh_common
from projinit.template import TemplateError

# @doc: docs/design/Templates.md#10-갱신-명령
NEXT_STEP = (
    "바뀐 파일은 아직 커밋하지 않았습니다. Claude Code에서 "
    "\"ProjInit 업데이트를 작업으로 등록해 커밋해 줘\"라고 맡기세요(작업 관리 규칙 4.9절)."
)

_VERSION_LINE_RE = re.compile(r'^version\s*=\s*"[^"]*"\s*$', re.MULTILINE)
_TABLE_RE = re.compile(r"^\[(.+)\]\s*$")


class UpgradeError(Exception):
    """A project that cannot be upgraded.

    @doc: docs/design/Templates.md#10-갱신-명령
    """


def set_version(text: str, version: str) -> str:
    """Return the settings text with the projinit version replaced.

    @doc: docs/design/Templates.md#10-갱신-명령
    """
    lines = text.splitlines(keepends=True)
    table = None
    header = None
    for number, line in enumerate(lines):
        match = _TABLE_RE.match(line.strip())
        if match:
            table = match.group(1).strip()
            if table == "projinit":
                header = number
            continue
        if table == "projinit" and _VERSION_LINE_RE.match(line.rstrip("\n")):
            lines[number] = f'version = "{version}"\n'
            return "".join(lines)
    if header is None:
        return f'[projinit]\nversion = "{version}"\n\n' + text
    lines.insert(header + 1, f'version = "{version}"\n')
    return "".join(lines)


def upgrade_project(root: Path) -> tuple[str, str, list[str]]:
    """Move a project to the running version and return (old, new, rewritten files).

    @doc: docs/design/Templates.md#10-갱신-명령
    """
    project = load_project(root)
    if project.config.command:
        raise UpgradeError("설정에 실행 명령(projinit.command)이 있어 버전을 고정하지 않는 프로젝트다. init --refresh-common을 쓴다.")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=project.root, capture_output=True, text=True)
    if status.returncode == 0 and status.stdout.strip():
        raise UpgradeError("커밋하지 않은 변경이 있다. 진행 중인 작업과 섞이지 않도록 먼저 커밋하거나 정리한다.")
    old, new = project.config.version, package_version()
    path = project.root / CONFIG_FILE
    path.write_text(set_version(path.read_text(encoding="utf-8"), new), encoding="utf-8")
    changed = refresh_common(load_project(project.root))
    return old, new, changed


def main(argv: list[str] | None = None) -> int:
    """Upgrade a project and print what changed; return the exit code.

    @doc: docs/design/Templates.md#10-갱신-명령
    """
    parser = argparse.ArgumentParser(prog="projinit upgrade", description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        old, new, changed = upgrade_project(args.root)
    except ConfigError as error:
        return report_config_error(error)
    except (UpgradeError, TemplateError) as error:
        print(f"upgrade: {error}")
        return 1
    print(f"upgrade: {old or '(없음)'} → {new}")
    for relative in [CONFIG_FILE, *changed]:
        print(f"바뀜: {relative}")
    print(NEXT_STEP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
