# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M2-T5 템플릿 원본 만들기 (공통 문서 분리, 시스템 구조 문서, 템플릿 테스트)

- 시작일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md)

### 계획
- 공통 규칙 문서에서 ProjInit 전용 내용을 떼어 내고, 이 저장소의 시스템 구조 문서(`docs/Architecture.md`)를 만든다.
- 공통 파일과 처음 만드는 파일의 템플릿을 `src/projinit/templates/`에 두고, 빈 자리를 채우는 `template.py`와 설정의 `[template]` 표를 만든다.
- 템플릿 테스트를 쓴다.

### 진행 기록
- 2026-10-31: PR #2가 병합되어 그 브랜치를 지우고 최신 `main`에서 `m2-t5-template-source`를 만들었다.
- 2026-10-31: 코드 작업 규칙의 디렉터리 표(ProjInit 전용 행), 언어와 스타일(Python·uv·PEP 8), 테스트(unittest)를 시스템 구조 문서로 옮기고, 그 절에는 공통 원칙만 남겼다. 절 제목은 그대로 두었다. 문서·작업 관리 규칙의 `projinit.check_*` 명령, 포인터 규약의 제품 비전 링크, 커밋 규칙의 기준 커밋 해시와 예시, PR 규칙과 작업 관리 규칙의 예시를 공통 표현으로 바꿨다.

### 결정 사항
- 공통 문서에서 시스템 구조 문서로는 링크하지 않는다. 초기화 직후에는 그 문서가 없기 때문이다. 대신 "인덱스의 제품 이해 절에 있다"고 적는다.
- 인덱스는 처음에만 만드는 파일로 다룬다. 프로젝트 고유 문서가 생기면 프로젝트가 고치기 때문이다.
- PR 규칙의 원격 주소는 템플릿에서 빈 자리 `{{repository}}`가 되고, 이 저장소의 값은 `projinit.toml`의 `[template]`에 둔다.

### 변경 파일
- `docs/Architecture.md`(신규), `docs/CodeRule.md`, `docs/DocumentationRule.md`, `docs/TaskRule.md`, `docs/Traceability.md`, `docs/CommitRule.md`, `docs/PullRequestRule.md`, `docs/VerificationTools.md`, `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/design/Package.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
