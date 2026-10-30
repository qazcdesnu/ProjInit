"""Verify that the hooks which run the checks automatically are installed.

@doc: docs/VerificationTools.md#8-강제-장치-검사기
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from projinit.config import ConfigError, load_project, report_config_error
from projinit.doclib import Problem

# @doc: docs/VerificationTools.md#8-강제-장치-검사기
CLAUDE_SETTINGS = ".claude/settings.json"
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
STOP_HOOK_COMMAND = 'cd "$CLAUDE_PROJECT_DIR" && uv run python -m tools.run_checks --hook stop'
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
PRE_COMMIT_HOOK = ".githooks/pre-commit"
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
PRE_COMMIT_COMMAND = "uv run python -m tools.run_checks --hook pre-commit"
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
COMMIT_MSG_HOOK = ".githooks/commit-msg"
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
COMMIT_MSG_COMMAND = 'uv run python -m tools.check_commit_msg "$1"'
# @doc: docs/VerificationTools.md#8-강제-장치-검사기
HOOKS_PATH = ".githooks"


def check_stop_hook(root: Path) -> list[Problem]:
    """Report a missing or malformed Claude Code Stop hook that runs the checks.

    @doc: docs/VerificationTools.md#8-강제-장치-검사기
    """
    path = root / CLAUDE_SETTINGS
    if not path.is_file():
        return [Problem(path, 1, f"Claude Code 설정 없음: {CLAUDE_SETTINGS}")]
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [Problem(path, error.lineno, f"JSON 형식 오류: {error.msg}")]
    groups = settings.get("hooks", {}).get("Stop", []) if isinstance(settings, dict) else []
    commands = [
        hook.get("command")
        for group in groups
        if isinstance(group, dict)
        for hook in group.get("hooks", [])
        if isinstance(hook, dict) and hook.get("type") == "command"
    ]
    if STOP_HOOK_COMMAND not in commands:
        return [Problem(path, 1, f"Stop hook에 검사 명령 없음: {STOP_HOOK_COMMAND}")]
    return []


def check_pre_commit(root: Path) -> list[Problem]:
    """Report a missing, non-executable or unrelated git pre-commit hook.

    @doc: docs/VerificationTools.md#8-강제-장치-검사기
    """
    return _check_git_hook(root, PRE_COMMIT_HOOK, PRE_COMMIT_COMMAND)


def check_commit_msg_hook(root: Path) -> list[Problem]:
    """Report a missing, non-executable or unrelated git commit-msg hook.

    @doc: docs/VerificationTools.md#8-강제-장치-검사기
    """
    return _check_git_hook(root, COMMIT_MSG_HOOK, COMMIT_MSG_COMMAND)


def _check_git_hook(root: Path, relative: str, command: str) -> list[Problem]:
    path = root / relative
    name = path.name
    if not path.is_file():
        return [Problem(path, 1, f"{name} hook 없음: {relative}")]
    problems = []
    if not os.access(path, os.X_OK):
        problems.append(Problem(path, 1, f"{name} hook에 실행 권한 없음"))
    if command not in path.read_text(encoding="utf-8"):
        problems.append(Problem(path, 1, f"{name} hook에 검사 명령 없음: {command}"))
    return problems


def check_hooks_path(root: Path) -> list[Problem]:
    """Report when git is not configured to use the repository's hooks directory.

    @doc: docs/VerificationTools.md#8-강제-장치-검사기
    """
    inside = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True
    )
    if inside.returncode != 0:
        return [Problem(root, 1, "git 저장소가 아님")]
    configured = subprocess.run(
        ["git", "-C", str(root), "config", "--get", "core.hooksPath"], capture_output=True, text=True
    ).stdout.strip()
    if configured != HOOKS_PATH:
        return [
            Problem(root, 1, f"git core.hooksPath가 {HOOKS_PATH}가 아님 (git config core.hooksPath {HOOKS_PATH})")
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    """Run every hook installation check and print problems; return the exit code.

    @doc: docs/VerificationTools.md#8-강제-장치-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args(argv).root.resolve()
    try:
        load_project(root)
    except ConfigError as error:
        return report_config_error(error)
    problems = check_stop_hook(root) + check_pre_commit(root) + check_commit_msg_hook(root) + check_hooks_path(root)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_hooks: 문제 {len(problems)}건")
        return 1
    print("check_hooks: 통과 (Stop hook, pre-commit, commit-msg, core.hooksPath)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
