"""A real project built once from the current code, copied per scenario and broken on purpose.

@doc: docs/design/Checkers.md#51-시나리오-테스트
"""

import atexit
import importlib
import io
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from projinit.config import load_project
from projinit.init import init_project, refresh_common
from projinit.run_checks import CHECKS

# @doc: docs/design/Checkers.md#51-시나리오-테스트
COMMAND = f"{shlex.quote(sys.executable)} -m projinit.cli"

_FEATURE = """# 기능 설계

이 문서는 기능을 정한다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 기능

- [app](../../src/app.py): 앱 모듈.
- [run](../../src/app.py#run): 실행한다.
- [Parser](../../src/app.py#Parser): 해석기.
- [later](../../src/app.py#later): 나중에 만든다.
- [util](../../src/util.ts), [helper](../../src/util.ts#helper): 도우미.
- [기존 앱](../../legacy/old/main.py): 예전 구현.
"""

_APP = '''"""App.

@doc: docs/design/Feature.md#1-기능
"""


def run() -> int:
    """Run.

    @doc: docs/design/Feature.md#1-기능
    """
    return 0


class Parser:
    """Parse.

    @doc: docs/design/Feature.md#1-기능
    """

    def parse(self) -> None:
        pass


def later() -> None:
    """Later.

    @doc: docs/design/Feature.md#1-기능
    @stub: I2
    """
    raise NotImplementedError
'''

_UTIL = """// @doc: docs/design/Feature.md#1-기능

// @doc: docs/design/Feature.md#1-기능
export function helper(): number {
  return 1;
}
"""

_DONE = """
## M0-T1 제품 비전과 첫 로드맵 작성

- 시작일: 2026-11-01
- 완료일: 2026-11-01

### 계획
- 첫 작업.

### 진행 기록
- 2026-11-01: 시작했다.

### 결정 사항
- 없음

### 변경 파일
- 없음

### 결과
- 처음 상태.

### 검증
- 검사 통과.
"""

_ONGOING = """
## I2 나중 기능

- 시작일: 2026-11-01
- 참고 자료: 없음

### 계획
- later를 만든다.

### 진행 기록
- 2026-11-01: 목업을 만들었다.
"""

_ISSUES = """- [x] I1 오타
  - 등록일: 2026-11-01
  - 경량: 오타를 고쳤다.
  - 완료일: 2026-11-01
- [~] I2 나중 기능
  - 등록일: 2026-11-01
"""

_baseline: Path | None = None


def _run(command: list[str], cwd: Path, stdin: str | None = None) -> tuple[int, str]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, input=stdin)
    return completed.returncode, completed.stdout + completed.stderr


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{path}: 바꿀 문자열 없음: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run_checks(root: Path) -> dict[str, tuple[int, str]]:
    results = {}
    for name, module in CHECKS:
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                code = importlib.import_module(module).main(["--root", str(root)])
            except SystemExit as exit_:
                code = exit_.code if isinstance(exit_.code, int) else 1
        results[name] = (code, output.getvalue())
    return results


def baseline() -> Path:
    """Build the baseline project once per process and return its root.

    @doc: docs/design/Checkers.md#51-시나리오-테스트
    """
    global _baseline
    if _baseline is not None:
        return _baseline
    holder = Path(tempfile.mkdtemp(prefix="projinit-scenario-")).resolve()
    atexit.register(shutil.rmtree, holder, ignore_errors=True)
    root = holder / "base"
    root.mkdir()
    for command in (["init", "-q", "-b", "main"], ["config", "user.name", "t"], ["config", "user.email", "t@t"]):
        _run(["git", *command], root)
    init_project(root, None)
    _replace(root / "projinit.toml", "[projinit]\n", f"[projinit]\ncommand = {json.dumps(COMMAND)}\n")
    refresh_common(load_project(root))
    _write(root, "docs/design/Feature.md", _FEATURE)
    _replace(
        root / "docs/index.md",
        "| _(아직 없음)_ | 상세 설계 문서를 만들면 여기에 링크한다. | |",
        "| [기능 설계](design/Feature.md) | 기능 | M0-T1 |",
    )
    _write(root, "src/app.py", _APP)
    _write(root, "src/util.ts", _UTIL)
    _replace(root / "docs/Roadmap.md", "- [ ] M0-T1 제품 비전과 첫 로드맵 작성", "- [x] M0-T1 제품 비전과 첫 로드맵 작성\n- [ ] M0-T2 다음 작업")
    _write(root, "docs/Done.md", (root / "docs/Done.md").read_text(encoding="utf-8") + _DONE)
    _replace(root / "docs/Issue.md", "등록된 이슈 없음.\n", _ISSUES)
    _replace(root / "docs/Ongoing.md", "\n없음\n", _ONGOING)
    _write(root, "reference/notes.md", "# 메모\n")
    _write(root, "legacy/old/main.py", "print('old')\n")
    _write(root, "docs/Legacy.md", "# 기존 프로젝트 목록\n\n전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.\n\n- [예전 앱](../legacy/old/): 예전 구현.\n")
    _write(root, "private/secret.txt", "secret\n")
    failed = {name: output for name, (code, output) in _run_checks(root).items() if code}
    if failed:
        raise AssertionError(f"기준 프로젝트가 검사를 통과하지 않음: {failed}")
    _run(["git", "add", "-A"], root)
    code, output = _run(["git", "commit", "-q", "-m", "M0-T1: 첫 작업"], root)
    if code:
        raise AssertionError(f"기준 프로젝트를 커밋하지 못함:\n{output}")
    _baseline = root
    return root


class ScenarioCase(unittest.TestCase):
    """A test case with a fresh copy of the baseline project as self.root.

    @doc: docs/design/Checkers.md#51-시나리오-테스트
    """

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve() / "project"
        shutil.copytree(baseline(), self.root, symlinks=True)

    def write(self, relative: str, text: str) -> Path:
        _write(self.root, relative, text)
        return self.root / relative

    def read(self, relative: str) -> str:
        return (self.root / relative).read_text(encoding="utf-8")

    def append(self, relative: str, text: str) -> None:
        self.write(relative, self.read(relative) + text)

    def replace(self, relative: str, old: str, new: str) -> None:
        _replace(self.root / relative, old, new)

    def remove(self, relative: str) -> None:
        (self.root / relative).unlink()

    def git(self, *args: str) -> tuple[int, str]:
        return _run(["git", *args], self.root)

    def commit(self, message: str, *options: str) -> tuple[int, str]:
        self.git("add", "-A")
        return self.git("commit", "-q", *options, "-m", message)

    def projinit(self, *args: str, stdin: str | None = None) -> tuple[int, str]:
        return _run([*shlex.split(COMMAND), *args], self.root, stdin)

    def checks(self) -> dict[str, tuple[int, str]]:
        """Run every checker in this process and return name -> (exit code, output).

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        """
        return _run_checks(self.root)

    def assert_caught(self, checker: str, needle: str) -> None:
        """Assert that the checker fails and its output holds the needle.

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        """
        code, output = self.checks()[checker]
        self.assertNotEqual(code, 0, f"{checker}가 통과함:\n{output}")
        self.assertIn(needle, output)

    def assert_clean(self) -> None:
        """Assert that every checker passes.

        @doc: docs/design/Checkers.md#51-시나리오-테스트
        """
        failed = {name: output for name, (code, output) in self.checks().items() if code}
        self.assertEqual(failed, {})
