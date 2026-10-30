# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 닫힌 마일스톤의 기록은 [작업 관리 규칙](TaskRule.md#47-완료-기록-보관)에 따라 보관 문서로 옮긴다. 보관 문서: [M0 규칙 체계 정비](Done-M0.md), [M3 갱신](Done-M3.md). 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

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
