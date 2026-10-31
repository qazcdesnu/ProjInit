# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 닫힌 마일스톤의 기록은 [작업 관리 규칙](TaskRule.md#47-완료-기록-보관)에 따라 보관 문서로 옮긴다. 보관 문서: [M0 규칙 체계 정비](Done-M0.md), [M1 검사기 패키지](Done-M1.md), [M2 초기화](Done-M2.md), [M3 갱신](Done-M3.md), [M4 첫 적용](Done-M4.md), [M5 갱신](Done-M5.md). 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.


## I19 참고 자료 폴더와 기존 프로젝트를 넣는 폴더를 구분하기로 함 (기능 후보 정리)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md)

### 계획
- 제품 비전 7절의 "참고 프로젝트로 초기화" 후보를 사용자의 방침대로 두 후보로 나눈다.

### 진행 기록
- 2026-10-31: 다음에 할 일을 묻는 대화에서, 사용자가 참고 자료 폴더와 ProjInit 없이 작업하던 기존 개발 프로젝트를 넣는 폴더는 구분해야 한다고 했다. 전자는 개발 중에 계속 갱신되는 자료이고, 후자는 곧바로 아카이브 자료가 된다. 기존 후보는 두 가지를 `proto/` 하나로 섞어 적고 있었다.

### 결정 사항
- 두 기능은 폴더를 따로 둔다. 폴더 이름과 규칙(아카이브 자료를 고치지 못하게 하는 검사 등)은 기능을 로드맵에 넣을 때 정한다. 사용자가 정하지 않은 것은 추측해 채우지 않는다.

### 변경 파일
- `docs/ProductVision.md`, `docs/Issue.md`, `docs/Done.md`

### 결과
- 제품 비전 7절에 참고 자료 폴더(살아 있는 자료)와 기존 프로젝트로 초기화(곧바로 아카이브)가 별도 후보로 적혔다.

### 검증
- `uv run projinit check`: 모두 통과

## I18 README.md가 인덱스에 링크되지 않고, README를 언제 고치는지 정한 규칙이 없는 문제

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [문서 작업 규칙](DocumentationRule.md)

### 계획
- 문서 작업 규칙 2절에 README의 역할(프로젝트, 사용자·개발자, 코딩 에이전트를 잇는 문서)과, README에 적힌 내용이 바뀌는 작업은 같은 작업 안에서 README를 고친다는 규칙을 더한다.
- 고아 문서 금지를 README에도 적용한다. README가 있으면 인덱스에서 도달할 수 있어야 하며, 문서 링크 검사기가 이를 검사한다.
- 템플릿 인덱스의 제품 이해 표에 README 줄(아직 없음)을 두고, 작업 관리 규칙 4.8절의 첫 작업에서 README를 쓰면 인덱스에 링크하게 한다. 이 저장소의 인덱스에는 README를 링크한다.
- 이 저장소의 릴리스 절차(템플릿 구성 5절)에 README의 버전을 올리는 단계를 더하고, README의 설치 예시 버전이 패키지 버전과 같은지 테스트로 확인한다.
- 버전을 `0.1.4`로 올리고 병합 뒤 `v0.1.4` 태그를 붙인다.

### 진행 기록
- 2026-10-31: 사용자가 README가 `CLAUDE.md`나 인덱스에 언급·링크되어 있는지 물었다. 확인하니 README를 다루는 규칙(문서 작업 규칙 2절, 작업 관리 규칙 4.8절, 검증 도구)은 있지만 README로 가는 링크가 없고, 고아 문서 판정에서도 빠져 있었다. README를 언제 고치는지는 첫 작업 말고는 정해져 있지 않아, 지금까지 릴리스마다 README의 버전을 기억에 기대어 고쳤다.
- 2026-10-31: 사용자가 README는 프로젝트, 사용자·개발자, 코딩 에이전트 세 주체를 잇는 아주 중요한 문서라며 권장안대로 하라고 했다.

### 결정 사항
- README 링크는 `CLAUDE.md`가 아니라 인덱스에 둔다. `CLAUDE.md`에는 구체적인 내용을 두지 않기 때문이다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`
- 추가: `src/projinit/templates/docs/DocumentationRule.md`, `src/projinit/templates/docs/TaskRule.md`, `src/projinit/templates/docs/VerificationTools.md`, `src/projinit/templates/docs/index.md`, `docs/DocumentationRule.md`, `docs/TaskRule.md`, `docs/VerificationTools.md`, `docs/index.md`, `src/projinit/check_docs.py`, `tests/test_check_docs.py`, `tests/test_release.py`, `docs/design/Checkers.md`, `docs/design/Templates.md`, `README.md`, `pyproject.toml`, `uv.lock`, `docs/Done.md`

### 결과
- 문서 작업 규칙 2절이 README를 프로젝트, 사용자·개발자, 코딩 에이전트를 잇는 문서로 정하고, README에 적힌 내용을 바꾸는 작업은 같은 작업 안에서 README도 고치게 한다.
- README가 있으면 인덱스에서 도달할 수 있어야 하며, 문서 링크 검사기가 README를 고아 문서 판정에 넣는다. 진입 문서만 판정에서 뺀다.
- 새 프로젝트의 인덱스에는 README 줄(아직 없음)이 있고, 첫 작업에서 README를 쓰면 링크로 바꾼다. 이 저장소의 인덱스는 README를 링크한다.
- 이 저장소의 릴리스 절차에 README의 버전 고치기를 더했고, `tests/test_release.py`가 README의 `v<버전>`이 패키지 버전과 같은지 확인한다.
- 이미 초기화한 프로젝트는 인덱스가 갱신 대상이 아니므로, 0.1.4로 올린 뒤 README가 있으면 고아 문서로 걸린다. 그 프로젝트의 Claude가 업데이트 작업 안에서 인덱스에 README를 링크하면 된다.
- 병합 뒤 `v0.1.4` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 빈 폴더에서 `projinit init` 뒤 `check` 통과, README를 만들면 고아 문서로 보고, 인덱스에 링크하면 통과
