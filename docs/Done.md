# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M0-T1 AgentVis의 공통 규칙 문서와 검사기를 출발점으로 복사

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#2-출발점)

### 계획
- AgentVis에서 공통 규칙 문서, 검사기, 검사기 테스트, uv 설정을 복사한다.
- AgentVis 고유 내용을 걷어 내고, 이 저장소의 제품 비전과 로드맵을 작성한다.
- 검증을 통과시키고 `git init`과 첫 커밋을 한다.

### 진행 기록
- 2026-10-31: AgentVis 세션에서 사용자 지시(AgentVis의 이슈 `I5`)로 이 저장소를 만들었다.
- 2026-10-31: 복사한 문서에서 AgentVis 고유 내용을 고쳤다. 인덱스의 제품·상세 설계 항목, 코드 작업 규칙의 `src/` 설명, 작업 관리 규칙의 기록 예시가 대상이었다.
- 2026-10-31: AgentVis 대화에서 논의한 내용(목적, 구성 초안, 출발 시점의 약점, 미결정 사항)을 [제품 비전](ProductVision.md)에 옮겨, 이 저장소의 세션이 그 대화 없이 시작할 수 있게 했다.

### 결정 사항
- 복사한 문서: `CLAUDE.md`, `docs/index.md`, `docs/DocumentationRule.md`, `docs/CodeRule.md`, `docs/Traceability.md`, `docs/TaskRule.md`, `docs/VerificationTools.md`
- 복사한 코드: `tools/`(`doclib`, `check_docs`, `check_pointers`, `check_tasks`), `tests/`(검사기 테스트)
- 복사하지 않은 것: AgentVis의 제품 비전, 데이터 소스, 시스템 구조, 상세 설계, 작업 기록
- git 사용자 정보는 전역이 아닌 저장소 로컬 설정으로 둔다.

### 변경 파일
- 신규: 위 복사 파일 전체, `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md`, `pyproject.toml`, `uv.lock`

### 결과
- 이 저장소가 자기 규칙 체계를 갖추고, 검사기로 그 규칙을 검증할 수 있는 상태로 시작한다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 27개 통과
