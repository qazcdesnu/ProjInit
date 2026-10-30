# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M2-T6 템플릿 일치 검사와 버전 일치 검사

- 시작일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md#5-버전-묶기-i10), [검증 도구](VerificationTools.md#14-템플릿-일치-검사기)

### 계획
- 공통 문서인 검증 도구에 템플릿 일치 검사기 절을 더하고(템플릿과 이 저장소 문서 모두), 검사기 설계에 구현 명세를 적는다.
- `check_template`을 만들어 `projinit check`에 넣는다. 템플릿 테스트의 자기 일치 테스트는 이 검사로 옮겨 지운다.

### 진행 기록
- 2026-10-31: PR #3~#5가 열려 있어 `m2-t3-install-devices` 위에 `m2-t6-template-check`를 쌓았다.
- 2026-10-31: 검증 도구는 공통 문서라 이 저장소의 문서와 템플릿을 함께 고쳤다. 이번 검사가 생기면 둘이 어긋날 때 바로 잡힌다.

### 결정 사항
- 템플릿 일치 검사는 공통 파일 전체(문서와 강제 장치 파일)를 본다. 강제 장치 파일의 명령도 버전에서 나오기 때문이다.
- 버전 일치 검사는 실행 명령이 지정된 저장소(이 저장소, 미리 써 보기 설정)에서 건너뛴다.

### 변경 파일
- `docs/VerificationTools.md`, `src/projinit/templates/docs/VerificationTools.md`, `docs/design/Checkers.md`, `docs/design/Templates.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
