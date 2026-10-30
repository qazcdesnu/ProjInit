"""Run every check at once, directly or as the Stop and pre-commit hooks.

@doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from projinit.doclib import REPO_ROOT

# @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
CHECKS = (
    ("check_docs", ("-m", "projinit.check_docs")),
    ("check_pointers", ("-m", "projinit.check_pointers")),
    ("check_tasks", ("-m", "projinit.check_tasks")),
    ("check_hooks", ("-m", "projinit.check_hooks")),
    ("unittest", ("-m", "unittest", "discover", "-s", "tests", "-t", ".")),
)

_SUMMARY_LINES = 40


@dataclass(frozen=True)
class CheckResult:
    """The outcome of one check.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """

    name: str
    returncode: int
    output: str


@dataclass(frozen=True)
class HookResponse:
    """What a hook prints and the exit code it returns.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """

    exit_code: int
    stdout: str = ""
    stderr: str = ""


def run_all(root: Path) -> list[CheckResult]:
    """Run every check as a subprocess of this interpreter, continuing past failures.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """
    results = []
    for name, args in CHECKS:
        command = [sys.executable, *args]
        if name != "unittest":
            command += ["--root", str(root)]
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True)
        results.append(CheckResult(name, completed.returncode, completed.stdout + completed.stderr))
    return results


def summarize(results: list[CheckResult]) -> str:
    """Describe the failed checks with the tail of their output.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """
    sections = []
    for result in results:
        if result.returncode == 0:
            continue
        tail = "\n".join(result.output.rstrip().splitlines()[-_SUMMARY_LINES:])
        sections.append(f"[{result.name}] 실패 (종료 코드 {result.returncode})\n{tail}")
    return "\n\n".join(sections)


def stop_hook_response(results: list[CheckResult], stop_hook_active: bool) -> HookResponse:
    """Block the first attempt to stop on failure; let a repeated attempt through with a warning.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """
    failed = [result.name for result in results if result.returncode != 0]
    if not failed:
        return HookResponse(0)
    if stop_hook_active:
        message = f"검사 실패가 남은 채 턴이 끝났습니다: {', '.join(failed)}"
        return HookResponse(0, stdout=json.dumps({"systemMessage": message}, ensure_ascii=False))
    guide = (
        "검증 검사가 실패했습니다. 실패를 고치거나, 진행 중인 작업이라 일부러 남기는 실패면 "
        "그 이유를 사용자에게 보고하세요."
    )
    return HookResponse(2, stderr=f"{guide}\n\n{summarize(results)}")


def _read_stop_hook_active() -> bool:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return False
    return isinstance(payload, dict) and bool(payload.get("stop_hook_active"))


def main(argv: list[str] | None = None) -> int:
    """Run every check, then report as a plain command or answer as a hook.

    @doc: docs/VerificationTools.md#9-일괄-실행과-자동-실행
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--hook", choices=("stop", "pre-commit"))
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.hook == "stop":
        stop_hook_active = _read_stop_hook_active()
        response = stop_hook_response(run_all(root), stop_hook_active)
        if response.stdout:
            print(response.stdout)
        if response.stderr:
            print(response.stderr, file=sys.stderr)
        return response.exit_code
    results = run_all(root)
    for result in results:
        print(f"{result.name}: {'통과' if result.returncode == 0 else '실패'}")
    if any(result.returncode != 0 for result in results):
        print(f"\n{summarize(results)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
