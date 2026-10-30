# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M1-T2 검사기를 설치 가능한 패키지로 전환

- 시작일: 2026-10-31
- 근거 문서: [패키지 구성](design/Package.md)

### 계획
- 1단계: 문서를 최종 상태로 고치고, `tools/`의 검사기를 동작 그대로 `src/projinit/`으로 옮긴다. hook이 쓰는 `tools/run_checks.py`, `tools/check_commit_msg.py`는 임시 진입점으로 남긴다. 설정 모듈은 목업으로 두고 진행 중 커밋을 한다.
- 2단계: 설정 모듈을 구현하고, 고정된 경로 상수와 테스트 명령을 설정으로 바꾼다. 이 저장소에 `projinit.toml`을 둔다.

### 진행 기록
- 2026-10-31: 원격 저장소 주소가 정해져(I8) 설계 문서의 미결정 사항을 지우고 `source`를 `git+https://github.com/qazcdesnu/ProjInit`로 적었다.
- 2026-10-31: 설계 문서에 `Project` 객체와 설정 오류 처리를 덧붙였다. 경로 상수를 쓰던 함수는 루트 대신 `Project`를 받는다.
- 2026-10-31: 옮기면 `doclib.REPO_ROOT`(검사기 파일의 상위 디렉터리)가 `src/`를 가리키게 되어, 1단계에서는 두 단계 위로 맞추고 2단계에서 현재 디렉터리 기본값으로 바꾸기로 했다.

### 결정 사항
- 빌드 백엔드는 `uv_build`다.
- 옮기는 1단계와 설정을 넣는 2단계를 나눠, 옮기기만으로 검사가 통과하는지 먼저 확인한다.

### 변경 파일
- `docs/design/Package.md`, `docs/VerificationTools.md`, `docs/CodeRule.md`, `docs/TaskRule.md`, `docs/DocumentationRule.md`, `docs/Traceability.md`, `docs/ProductVision.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- `tools/*.py` → `src/projinit/*.py`, `src/projinit/__init__.py`, `src/projinit/config.py`(목업), `tools/run_checks.py`·`tools/check_commit_msg.py`(임시 진입점), `tests/*.py`, `tests/test_config.py`(목업), `pyproject.toml`, `uv.lock`
