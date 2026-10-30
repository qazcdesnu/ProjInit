# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M2-T2 `projinit init` 명령

- 시작일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md#9-초기화-명령)

### 계획
- `projinit init`(공통·처음 파일과 설정 파일 만들기, `git init`)과 `--refresh-common`을 만든다.
- 설정 파일을 템플릿으로 옮긴다.
- 이 저장소의 공통 문서를 `--refresh-common`으로 다시 만들어 템플릿과 같은지 확인한다.

### 진행 기록
- 2026-10-31: PR #3(M2-T5)이 아직 병합되지 않아, PR 규칙대로 그 브랜치 위에 `m2-t2-init-command`를 쌓았다.

### 결정 사항
- 원격 주소는 인자, git `origin`, "아직 없음" 순서로 정한다. 새 프로젝트에는 원격 저장소가 아직 없는 경우가 많기 때문이다.
- 초기화는 커밋하지 않는다(템플릿 구성 설계 1절). hook과 CI 설치는 M2-T3이 맡는다.

### 변경 파일
- `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
