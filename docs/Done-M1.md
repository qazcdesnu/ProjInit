# 완료 보관 M1 검사기 패키지

이 문서는 닫힌 마일스톤 M1의 완료 기록을 보관한다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 아직 닫히지 않은 마일스톤의 기록은 [완료](Done.md)에 있다.

## M1-T4 검증 도구 문서를 공통 문서와 검사기 설계 문서로 분리

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [패키지 구성](design/Package.md#7-검증-도구-문서의-분리)

### 계획
- 검사기 내부(모듈·함수·상수·테스트)를 담은 지금 검증 도구 문서를 `docs/design/Checkers.md`로 옮긴다.
- 검증 도구는 다른 프로젝트로 내보낼 공통 문서로 다시 쓴다. 코드 포인터와 ProjInit 전용 문서로 가는 링크를 두지 않는다.
- 코드와 테스트의 `@doc:` 포인터를 검사기 설계 문서로 옮긴다.

### 진행 기록
- 2026-10-31: 완료 기록(고칠 수 없음)에 검증 도구의 절 앵커로 가는 링크가 4개, 다른 문서에 23개 있었다. 앵커가 바뀌면 완료 기록의 링크가 깨지므로, 검증 도구의 절 제목 11개를 그대로 두고 내용만 공통 설명으로 바꿨다. 검사기 설계 문서도 같은 절 구성으로 만들어 코드 포인터 126개를 경로만 바꿔 옮겼다.
- 2026-10-31: 이 과정에서 "완료 기록은 고칠 수 없는데 문서 구조가 바뀌면 기록 안의 링크가 깨진다"는 체계 차원의 문제가 드러나 I11로 등록했다. 사용자의 버전 관리 질문은 I10으로 등록해 M2-T1에 연결했다.
- 2026-10-31: 공통 문서에 코드 포인터와 ProjInit 전용 문서로 가는 링크가 하나도 없고, 코드의 `@doc:` 포인터가 모두 검사기 설계 문서를 가리키는 것을 확인했다.
- 2026-10-31: M1의 마지막 태스크라 완료와 함께 M1을 닫고, 완료 문서의 기록(M1-T1~T4)을 `docs/Done-M1.md`로 그대로 옮겼다.

### 결정 사항
- 검증 도구(공통)는 무엇을 검사하고 어떻게 실행하는지, 검사기 설계(ProjInit 전용)는 그것을 어떻게 구현하는지 정한다. 둘이 다르면 검증 도구가 기준이다.
- 설정 파일 형식은 공통 문서인 검증 도구 11절로 옮겼다. 다른 프로젝트에는 패키지 구성 설계 문서가 없기 때문이다.

### 변경 파일
- `docs/VerificationTools.md`, `docs/design/Checkers.md`(신규), `docs/index.md`, `docs/Issue.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `src/projinit/*.py`, `tests/*.py`
- 추가: `docs/Done.md`, `docs/Done-M1.md`(신규)

### 결과
- 검증 도구는 다른 프로젝트로 그대로 내보낼 수 있는 공통 문서가 되었고, 검사기 구현은 이 저장소에만 있는 검사기 설계 문서가 정한다.
- M1(검사기 패키지)이 닫혔다.

### 검증
- `uv run projinit check`: 모두 통과

## M1-T3 hook이 부르는 `projinit` 실행 진입점 (`check`, `commit-msg`)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [패키지 구성](design/Package.md#3-명령), [검증 도구](VerificationTools.md#8-강제-장치-검사기)

### 계획
- `projinit` 명령(`cli.py`)과 하위 명령 `check`, `commit-msg`를 만든다.
- 강제 장치 검사기가 기대하는 hook 명령을 설정에서 만들게 한다.
- 이 저장소의 hook을 `uv run projinit …`으로 바꾸고, `tools/`의 임시 진입점과 디렉터리를 지운다.

### 진행 기록
- 2026-10-31: 문서를 고쳤다. 검증 도구의 hook 명령 상수 셋을 `HookCommands`, `projinit_command`, `hook_commands`로 바꾸고, 코드 작업 규칙에서 `tools/` 행을 지웠다.
- 2026-10-31: 목업을 두고 진행 중 커밋을 하려 했으나, pre-commit이 아직 `tools/`의 임시 진입점을 부르는데 문서에서는 그 진입점을 이미 빼서, 진입점을 지우면 hook이 깨지고 남기면 역방향 포인터 검사에 걸렸다. 작은 태스크라 진행 중 커밋 없이 구현까지 한 번에 했다.
- 2026-10-31: `cli.py`, `HookCommands`·`projinit_command`·`hook_commands`를 구현하고, 이 저장소의 Stop·pre-commit·commit-msg hook을 `uv run projinit …`으로 바꿨다. `tools/`를 지우고 설정의 코드 루트에서도 뺐다.
- 2026-10-31: 작업 중 사용자가 문서 버전 관리와 버전 호환 기능이 있는지 물었다. 이 태스크를 마친 뒤 답하기로 했다.

### 결정 사항
- 하위 명령은 해당 모듈의 `main`에 나머지 인자를 그대로 넘긴다. 인자 해석을 두 곳에 두지 않기 위해서다.
- hook 명령을 만들 수 없는 설정(`command`도 `source`·`version`도 없음)은 강제 장치 검사기가 설정 파일의 문제로 보고한다.

### 변경 파일
- `docs/VerificationTools.md`, `docs/CodeRule.md`, `docs/design/Package.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- 추가: `src/projinit/cli.py`(신규), `src/projinit/check_hooks.py`, `tests/test_cli.py`(신규), `tests/test_check_hooks.py`, `pyproject.toml`, `uv.lock`, `projinit.toml`, `.claude/settings.json`, `.githooks/pre-commit`, `.githooks/commit-msg`, `tools/`(삭제), `docs/Done.md`

### 결과
- `projinit check`, `projinit commit-msg` 명령이 생겼고, 이 저장소의 hook이 이 명령을 쓴다.
- 강제 장치 검사기는 설정에서 만든 hook 명령과 비교하므로, 다른 프로젝트에서는 `uvx --from <source>@v<version> projinit …` 명령을 검사한다.

### 검증
- `uv run projinit check`: 검사기 4개와 테스트 모두 통과

## M1-T2 검사기를 설치 가능한 패키지로 전환

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 관련 이슈: I8
- 근거 문서: [패키지 구성](design/Package.md)

### 계획
- 1단계: 문서를 최종 상태로 고치고, `tools/`의 검사기를 동작 그대로 `src/projinit/`으로 옮긴다. hook이 쓰는 `tools/run_checks.py`, `tools/check_commit_msg.py`는 임시 진입점으로 남긴다. 설정 모듈은 목업으로 두고 진행 중 커밋을 한다.
- 2단계: 설정 모듈을 구현하고, 고정된 경로 상수와 테스트 명령을 설정으로 바꾼다. 이 저장소에 `projinit.toml`을 둔다.

### 진행 기록
- 2026-10-31: 원격 저장소 주소가 정해져(I8) 설계 문서의 미결정 사항을 지우고 `source`를 `git+https://github.com/qazcdesnu/ProjInit`로 적었다.
- 2026-10-31: 설계 문서에 `Project` 객체와 설정 오류 처리를 덧붙였다. 경로 상수를 쓰던 함수는 루트 대신 `Project`를 받는다.
- 2026-10-31: 옮기면 `doclib.REPO_ROOT`(검사기 파일의 상위 디렉터리)가 `src/`를 가리키게 되어, 1단계에서는 두 단계 위로 맞추고 2단계에서 현재 디렉터리 기본값으로 바꾸기로 했다.
- 2026-10-31: 1단계를 마쳤다. 옮긴 상태에서 임시 진입점을 거쳐 모든 검사가 통과해 진행 중 커밋을 했다(d08b16b, 목업 10개). editable 설치가 처음 만든 `projinit.pth`에 숨김 속성이 붙지 않은 것도 확인했다(I4의 우려).
- 2026-10-31: 2단계에서 `config.py`를 구현하고, 경로가 필요한 함수가 루트 대신 `Project`를 받게 바꿨다. 화면 출력에만 루트를 쓰는 함수는 그대로 두었다. `doclib`의 경로 상수(`REPO_ROOT` 등 5개)를 지우고 `--root` 기본값을 현재 디렉터리로 바꿨다.
- 2026-10-31: 일괄 실행의 고정된 `unittest` 검사를 지우고, 설정의 `check.commands`를 셸로 실행하게 했다. 이 저장소의 `projinit.toml`에 테스트 명령을 적었다.
- 2026-10-31: 보관 안내 메시지가 `docs/` 같은 경로를 박아 쓰지 않도록 "Done-M0.md(같은 디렉터리)"로 바꿨다.

### 결정 사항
- 빌드 백엔드는 `uv_build`다.
- 옮기는 1단계와 설정을 넣는 2단계를 나눠, 옮기기만으로 검사가 통과하는지 먼저 확인한다.

### 변경 파일
- `docs/design/Package.md`, `docs/VerificationTools.md`, `docs/CodeRule.md`, `docs/TaskRule.md`, `docs/DocumentationRule.md`, `docs/Traceability.md`, `docs/ProductVision.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- `tools/*.py` → `src/projinit/*.py`, `src/projinit/__init__.py`, `src/projinit/config.py`(목업), `tools/run_checks.py`·`tools/check_commit_msg.py`(임시 진입점), `tests/*.py`, `tests/test_config.py`(목업), `pyproject.toml`, `uv.lock`
- 추가: `src/projinit/config.py`·`tests/test_config.py` 구현, `projinit.toml`(신규), `docs/Done.md`

### 결과
- 검사기가 `src/projinit/`의 설치 가능한 패키지가 되었고, 프로젝트마다 다른 경로와 테스트 명령을 `projinit.toml`로 정한다.
- 어느 디렉터리에서든 `--root`로 다른 프로젝트를 검사할 수 있다. 설정 오류는 `projinit.toml:<줄>: 설정 오류: …`로 보고된다.

### 검증
- `uv run python -m tools.run_checks`: 검사기 4개와 설정의 테스트 명령(테스트 91개) 모두 통과
- 다른 디렉터리에서 `--root`로 이 저장소를 검사해 통과했다.

## M1-T1 패키지 구성 상세 설계

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#4-구성-초안)

### 계획
- 검사기가 이 저장소에 묶여 있는 부분을 찾고, 다른 프로젝트에 설치해 쓸 수 있는 패키지 구성을 설계 문서로 정한다.

### 진행 기록
- 2026-10-31: 검사기 코드를 살펴 이 저장소에 묶인 부분을 찾았다. 고정된 경로 상수, 일괄 실행의 `unittest` 명령, hook의 `uv run python -m tools.…` 명령이다.
- 2026-10-31: 더 큰 문제로, 공통 규칙 문서인 검증 도구 문서가 검사기 내부 심볼을 가리키는 코드 포인터를 담고 있어 다른 프로젝트에 배포하면 포인터 검사가 모두 실패한다는 것을 발견했다. 문서를 공통 문서와 검사기 설계 문서로 나누는 일을 M1-T4로 추가했다.
- 2026-10-31: [패키지 구성](design/Package.md) 설계 문서를 쓰고 인덱스의 상세 설계 표에 링크했다.

### 결정 사항
- 검사기는 `src/projinit/`의 제품 코드가 되고, `projinit` 명령(`check`, `commit-msg`, 이후 `init`, `upgrade`)으로 실행한다.
- 프로젝트마다 다른 값(경로, 테스트 명령, ProjInit 버전과 출처, 실행 명령)은 루트의 `projinit.toml`에 둔다. Python이 아닌 프로젝트를 위해 `pyproject.toml`이 아닌 별도 파일로 한다.
- hook 명령은 설정에서 만든다. 이 저장소는 `uv run projinit`으로 작업 트리의 검사기를 쓰고, 다른 프로젝트는 `uvx --from <source>@v<version> projinit`을 쓴다.
- 문서만 쓰는 태스크라 목업 단계 없이 처리했다.

### 변경 파일
- `docs/design/Package.md`(신규), `docs/index.md`, `docs/Roadmap.md`, `docs/Done.md`

### 결과
- 패키지 구조, 명령, 설정 파일, hook 명령, 이 저장소의 자기 적용 방식, 검증 도구 문서 분리, 태스크 나누기가 설계 문서로 정해졌다.

### 검증
- `uv run python -m tools.run_checks`: 모두 통과
