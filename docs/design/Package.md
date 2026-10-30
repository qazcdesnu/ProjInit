# 패키지 구성 상세 설계

이 문서는 검사기를 다른 프로젝트에도 설치해 쓸 수 있는 `projinit` 패키지로 만드는 구성을 정한다. 근거는 [제품 비전](../ProductVision.md#4-구성-초안)의 구성 초안(검사기는 프로젝트에 복사하지 않고, 버전을 고정해 `uvx`로 실행한다)과 [자기 적용 원칙](../ProductVision.md#3-핵심-요구사항)이다. 구현은 [로드맵](../Roadmap.md)의 M1-T2, M1-T3, M1-T4가 맡는다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 지금 구조의 문제

검사기는 지금 이 저장소의 `tools/` 패키지이고, 이 저장소에서만 돌아간다.

| 문제 | 지금 | 다른 프로젝트에서 생기는 일 |
| --- | --- | --- |
| 고정된 경로 | 문서 디렉터리, 진입 문서, 코드 루트(`src`, `tools`, `tests`), 작업 관리 문서 경로가 코드 상수다. | 구조가 다른 프로젝트를 검사할 수 없다. |
| 고정된 테스트 명령 | 일괄 실행이 `python -m unittest discover -s tests`를 실행한다. | Rust·TypeScript 프로젝트의 테스트를 돌릴 수 없다. |
| 고정된 hook 명령 | hook이 `uv run python -m tools.…`를 실행한다. | 그 프로젝트에는 `tools/`가 없다. |
| 검사기 내부를 담은 공통 문서 | [검증 도구](../VerificationTools.md)는 공통 규칙 문서인데, 검사기 내부 심볼을 가리키는 코드 포인터를 담고 있다. | 템플릿으로 배포하면 그 프로젝트에는 검사기 코드가 없어서 포인터 검사가 모두 실패한다. |

## 2. 패키지 구조

검사기는 이 저장소의 제품 코드가 된다. [코드 작업 규칙](../CodeRule.md#2-디렉터리-구조)대로 `src/` 아래에 둔다.

```text
src/projinit/
  __init__.py
  cli.py            명령줄 진입점 (projinit 명령)
  config.py         프로젝트 설정 파일 읽기
  doclib.py         ← tools/doclib.py
  languages.py      ← tools/languages.py
  code_index.py     ← tools/code_index.py
  check_docs.py     ← tools/check_docs.py
  check_pointers.py ← tools/check_pointers.py
  check_tasks.py    ← tools/check_tasks.py
  check_hooks.py    ← tools/check_hooks.py
  check_commit_msg.py ← tools/check_commit_msg.py
  run_checks.py     ← tools/run_checks.py
```

- 모듈 이름과 역할은 지금 `tools/`와 같게 옮긴다. 옮기면서 동작을 바꾸지 않는다. 동작 변경은 아래 절의 설정 도입에 한정한다.
- 옮긴 뒤 `tools/`에는 검사기가 남지 않는다. `tools/`는 [코드 작업 규칙](../CodeRule.md#2-디렉터리-구조)대로 이 저장소만의 개발 도구 자리로 남는다.
- 빌드 백엔드는 `uv_build`, 패키지 이름은 `projinit`, Python 요구 버전과 의존성(`tree-sitter`, 언어별 문법 패키지)은 지금 `pyproject.toml` 그대로다.

## 3. 명령

`pyproject.toml`의 `[project.scripts]`로 `projinit` 명령을 만든다. 하위 명령은 다음과 같다.

| 명령 | 하는 일 | 지금의 대응 |
| --- | --- | --- |
| `projinit check` | 모든 검사를 한 번에 실행한다. `--hook stop`, `--hook pre-commit`을 받는다. | `tools.run_checks` |
| `projinit check docs` 등 | 검사 하나만 실행한다. 이름은 `docs`, `pointers`, `tasks`, `hooks`. | `tools.check_*` |
| `projinit commit-msg <파일>` | 커밋 메시지를 검사한다. `commit-msg` hook이 실행한다. | `tools.check_commit_msg` |
| `projinit init`, `projinit upgrade` | M2, M3에서 만든다. | 없음 |

모든 명령은 `--root <경로>`를 받으며, 기본값은 현재 디렉터리다. 지금처럼 검사기 파일 위치로부터 루트를 정하지 않는다. 설치된 패키지는 검사할 프로젝트 밖에 있기 때문이다.

## 4. 프로젝트 설정 파일

프로젝트마다 다른 값은 프로젝트 루트의 `projinit.toml`에 둔다. Python이 아닌 프로젝트에도 쓸 수 있도록 `pyproject.toml`의 `[tool.*]`가 아닌 별도 파일로 한다. 표준 라이브러리 `tomllib`로 읽는다.

```toml
[projinit]
version = "0.1.0"                   # 이 프로젝트가 쓰는 ProjInit 버전 (git 태그 v0.1.0)
source = "git+https://…/ProjInit"   # 설치 출처
command = ""                        # 비우면 version과 source로 만든다

[paths]
docs = "docs"
entry = "CLAUDE.md"
code_roots = ["src", "tests"]

[check]
commands = ["cargo test"]           # 검사 뒤에 이어서 실행할 프로젝트 명령 (테스트 등)
```

- 파일이 없거나 키가 빠지면 기본값을 쓴다. 기본값은 위 예시의 `paths` 값과 빈 `check.commands`다.
- 작업 관리 문서(`Roadmap.md` 등)와 보관 문서의 이름, 인덱스 이름(`index.md`)은 공통 규칙이 정하는 것이므로 설정하지 않고 `paths.docs` 아래에 고정한다.
- `check.commands`는 셸 명령으로 루트에서 차례로 실행하며, 일괄 실행의 검사 하나로 취급한다. 이것으로 개발 언어에 맞는 테스트를 돌린다.
- 지금 코드 상수(`CODE_ROOTS` 등)는 설정을 읽는 함수로 바뀐다. 상수를 직접 쓰던 함수는 설정 객체를 인자로 받는다.

## 5. hook 명령

hook이 실행하는 명령은 설정의 `projinit.command`다. 비어 있으면 `uvx --from <source>@v<version> projinit`으로 만든다. 그래서 버전을 바꾸려면 설정 파일 한 곳만 바꾸면 된다.

| 장치 | 실행하는 명령 |
| --- | --- |
| Stop hook | `cd "$CLAUDE_PROJECT_DIR" && <command> check --hook stop` |
| pre-commit | `<command> check --hook pre-commit` |
| commit-msg | `<command> commit-msg "$1"` |

[강제 장치 검사기](../VerificationTools.md#8-강제-장치-검사기)는 고정된 문자열 대신 설정에서 만든 명령과 비교한다. hook 파일을 만들고 고치는 일은 `init`과 `upgrade`(M2, M3)가 맡는다.

## 6. 이 저장소 자신

[자기 적용 원칙](../ProductVision.md#3-핵심-요구사항)대로 이 저장소도 같은 설정 파일과 같은 `projinit` 명령으로 검사한다. 다른 점은 다음 둘뿐이다.

- `projinit.command = "uv run projinit"`: 이 저장소는 `projinit` 패키지 자체이므로, 설치된 버전이 아니라 작업 트리의 코드로 검사한다. 고친 검사기가 곧바로 자기 자신을 검사한다.
- `check.commands = ["uv run python -m unittest discover -s tests -t ."]`: 검사기 테스트를 돌린다.

## 7. 검증 도구 문서의 분리

[검증 도구](../VerificationTools.md)를 두 문서로 나눈다.

| 문서 | 내용 | 코드 포인터 | 배포 |
| --- | --- | --- | --- |
| 검증 도구 (공통) | 검사기가 무엇을 검사하는지, 명령, 출력 형식, 자동 실행 장치와 그 동작, 설정 파일 | 없음 | 템플릿으로 모든 프로젝트에 배포 |
| 검사기 설계 (`docs/design/Checkers.md`) | 검사기의 모듈, 자료형, 함수, 상수와 테스트 구성 | 있음 | ProjInit 저장소에만 둔다 |

- 공통 문서에는 코드 포인터를 두지 않는다. 다른 프로젝트에는 검사기 코드가 없기 때문이다.
- 검사기 코드의 `@doc:` 포인터는 대부분 검사기 설계 문서를 가리키게 바뀐다. 공통 규칙 문서(포인터 규약, 작업 관리 규칙 등)를 직접 근거로 하는 코드는 그 문서를 함께 가리킬 수 있지만, 그러면 [상호 참조 규칙](../Traceability.md#5-상호-참조-규칙)상 그 공통 문서가 코드를 가리켜야 하므로 피한다.
- 공통 규칙 문서와 프로젝트 고유 문서의 전체 경계는 M2-T1에서 정한다. 이 분리는 그 경계의 첫 사례다.

## 8. 작업 나누기

| 태스크 | 범위 |
| --- | --- |
| M1-T2 | `src/projinit/`로 옮기고, 설정 파일(`config.py`)을 도입해 고정된 경로와 테스트 명령을 설정으로 바꾼다. 이 저장소에 `projinit.toml`을 둔다. |
| M1-T3 | `projinit` 명령(`cli.py`)과 하위 명령을 만들고, hook 명령을 설정에서 만들게 바꾼다. 이 저장소의 hook을 `uv run projinit`으로 바꾼다. |
| M1-T4 | 검증 도구 문서를 공통 문서와 검사기 설계 문서로 나누고, 검사기 코드의 포인터를 옮긴다. |

M1-T2와 M1-T3 사이에는 `tools.run_checks` 등 기존 모듈 실행 경로가 한동안 남아 hook이 계속 동작하게 한다. 예를 들어 `tools/`에 `projinit`의 함수를 부르는 얇은 진입점을 두었다가 M1-T3에서 지운다.

## 9. 미결정 사항

- git 원격 저장소 주소: 설정 파일의 `source`에 들어간다. 다른 프로젝트에 설치하는 M2부터 필요하다.
