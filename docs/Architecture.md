# 시스템 구조

이 문서는 ProjInit 저장소의 디렉터리 구조, 개발 언어와 스타일, 테스트 방식을 정한다. 공통 [코드 작업 규칙](CodeRule.md)이 프로젝트마다 정하라고 남긴 부분이다. 패키지의 모듈 구성은 [패키지 구성 설계](design/Package.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## 1. 디렉터리 구조

| 경로 | 용도 |
| --- | --- |
| `docs/` | 모든 문서. 코드 작업의 규칙이다. |
| `src/` | 제품 코드. `src/projinit/`이 `projinit` 패키지이며, `src/projinit/templates/`가 초기화 템플릿 원본이다([템플릿 구성 설계](design/Templates.md)). |
| `tests/` | 자동 테스트. |
| `pyproject.toml`, `.python-version`, `uv.lock` | uv 프로젝트 설정. [2. 언어와 스타일](#2-언어와-스타일)을 따른다. |
| `projinit.toml` | 검사기 설정. [검증 도구의 설정](VerificationTools.md#11-설정)에 규정된다. |
| `.claude/` | Claude Code 프로젝트 설정(`settings.json`). 검사기를 자동 실행하는 Stop hook을 둔다. [검증 도구](VerificationTools.md#9-일괄-실행과-자동-실행)에 규정된다. |
| `.githooks/` | 저장소에 포함하는 git hook. `pre-commit`과 `commit-msg`를 둔다. [검증 도구](VerificationTools.md#9-일괄-실행과-자동-실행)와 [커밋 규칙](CommitRule.md#5-강제)에 규정된다. |
| `.github/` | PR 템플릿과 CI. [PR 규칙](PullRequestRule.md)과 [검증 도구의 CI](VerificationTools.md#12-ci)에 규정된다. |

새로운 최상위 디렉터리가 필요하면 이 표를 먼저 수정한다.

## 2. 언어와 스타일

- 개발 언어는 Python이다.
- Python은 **반드시 uv 환경에서** 사용한다.
  - Python 버전은 uv가 관리하며 `.python-version`(현재 `3.12`)과 `pyproject.toml`의 `requires-python`으로 고정한다.
  - 모든 Python 실행은 `uv run`을 거친다. 시스템 Python(`python3`)이나 직접 만든 가상 환경을 쓰지 않는다.
  - 의존성은 `uv add`(개발용은 `uv add --dev`)로만 추가·제거한다. `pip`를 직접 쓰지 않는다. `uv.lock`은 저장소에 포함한다.
- `src/projinit/`의 코드는 표준 라이브러리와, 여러 언어의 코드를 파싱하기 위한 `tree-sitter` 및 언어별 문법 패키지(`tree-sitter-<언어>`)만 사용한다. 문법은 실행할 때 내려받지 않고 패키지에 포함된 것을 쓰며, 버전은 `uv.lock`으로 고정한다.
- 스타일은 PEP 8을 따른다.
  - 모듈·함수·변수 이름은 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE`.
  - 모듈 내부 전용 심볼은 이름 앞에 `_`를 붙인다.
- 모든 함수의 인자와 반환값에 타입 힌트를 단다. `list[str]`, `str | None` 같은 내장 문법을 쓴다.

## 3. 테스트

[코드 작업 규칙의 테스트 종류](CodeRule.md#51-테스트-종류) 중 둘을 둔다.

| 종류 | 폴더 | 이름 | 하는 일 |
| --- | --- | --- | --- |
| 단위 | `tests/unit/` | `test_<대상 모듈>.py` | 모듈 하나를 임시 저장소에서 검사한다. 검사기는 `main`이나 검사 함수를 직접 부른다. |
| 종단(시나리오) | `tests/scenario/` | `test_<규칙 영역>.py` | 초기화로 실제 프로젝트를 만들고 규칙을 하나씩 일부러 깨뜨려, 검사기가 맞는 메시지로 잡는지 본다. 실제 git hook과 Stop hook도 실행한다([검사기 설계의 시나리오 테스트](design/Checkers.md#51-시나리오-테스트)). |

- `src/projinit/`는 평평한 패키지라 단위 테스트 폴더 안에 하위 폴더를 두지 않는다.
- 공통 도구는 `tests/support.py`(임시 저장소 `RepoTestCase`)에 둔다.
- 테스트 프레임워크는 표준 라이브러리 `unittest`를 사용한다. 설정의 프로젝트 명령으로 `uv run python -m unittest discover -s tests -t .`를 실행하며, 두 종류를 모두 찾는다.
- 새 규칙이나 검사를 더하면 단위 테스트와 함께, 그 규칙을 일부러 깨뜨리는 시나리오도 더한다.
- 시나리오 테스트도 Stop hook에서 돌므로 빨라야 한다. 기준 프로젝트는 한 번만 만들어 경우마다 복사하고, 검사기는 같은 프로세스에서 부른다. 실제 hook을 확인하는 경우만 명령으로 실행한다.
