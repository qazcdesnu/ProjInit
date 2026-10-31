# 완료 보관 M6 자료 폴더

이 문서는 닫힌 마일스톤 M6의 완료 기록과, 그때 완료 문서에 있던 이슈의 완료 기록을 보관한다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 아직 닫히지 않은 마일스톤의 기록은 [완료](Done.md)에 있다.

## M6-T1 참고 자료 폴더 `reference/`와 기존 프로젝트 폴더 `legacy/`의 규칙과 검사기

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [자료 폴더 설계](design/Materials.md)
- 관련 이슈: I19

### 계획
- 자료 폴더 설계 문서를 쓰고, 공통 규칙 문서 `MaterialRule.md`(자료 폴더 규칙)를 템플릿에 더한다. 진입 문서, 문서 작업 규칙, 포인터 규약, 작업 관리 규칙 4.8절, 검증 도구, 템플릿 인덱스를 함께 고친다.
- 설정에 `paths.reference`, `paths.legacy`를 더한다.
- 자료 폴더 검사기 `check_materials`를 만든다: 목록 문서가 모든 자료를 링크하는지, `legacy/`의 기존 프로젝트가 넣은 뒤 바뀌지 않았는지, `legacy/` 안에 `.git`이 없는지.
- 포인터 검사기는 자료 폴더 안 코드 파일 링크를 포인터로 보지 않고, 문서 링크 검사기가 그 파일이 있는지만 본다.
- 제품 비전 7절의 후보를 M6으로 옮기고, README에 기존 프로젝트로 시작하는 방법을 적는다. 버전 `0.1.5`.

### 진행 기록
- 2026-10-31: I19에서 두 폴더를 나누기로 한 뒤, 사용자가 두 폴더의 이름과 규칙을 잘 만들어 달라고 했다. 이름은 `reference/`와 `legacy/`로 정했다. `archive`는 완료 기록 보관(`Done-M<n>.md`)과 헷갈리고, `legacy`는 "ProjInit 이전의 프로젝트"라는 뜻이 바로 드러나기 때문이다.

- 2026-10-31: 진행 중 기록, 설계 문서, 공통 규칙 문서, 목업을 먼저 커밋했다(a8ac040). 진입 문서에 인라인 코드(`reference/`)를 썼다가 진입 문서 형식 검사에 걸려 글로만 적었다.
- 2026-10-31: 검사기를 구현하고 일괄 실행에 넣었다. 빈 폴더에 `.git`이 든 기존 프로젝트와 참고 자료를 넣고 초기화해 보니, 목록 문서 없음과 중첩 `.git`을 보고했다. `.git`을 빼고 목록 문서를 쓰자 통과했고, 고아 문서 검사가 목록 문서를 인덱스에 링크하라고 알렸다. 커밋 뒤 기존 프로젝트 파일을 고치면 보고하고, 참고 자료를 고치는 것은 허용했다.

### 결정 사항
- 자료는 문서가 아니므로 `docs/` 밖에 두고, 대신 목록 문서(`docs/Reference.md`, `docs/Legacy.md`)가 모든 자료를 링크하게 해 에이전트와 사람이 자료를 찾을 수 있게 한다.
- `legacy/`의 불변은 완료 기록 보존처럼 git `HEAD`와 비교해 검사한다.

### 변경 파일
- `docs/Roadmap.md`, `docs/Ongoing.md`
- `docs/design/Materials.md`, `docs/design/Checkers.md`, `docs/design/Templates.md`, `docs/design/Package.md`, `docs/index.md`, `docs/ProductVision.md`
- 템플릿: `src/projinit/templates/CLAUDE.md`, `src/projinit/templates/docs/MaterialRule.md`(새 문서), `DocumentationRule.md`, `Traceability.md`, `TaskRule.md`, `VerificationTools.md`, `index.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/check_materials.py`(새 검사기), `src/projinit/config.py`, `src/projinit/check_docs.py`, `src/projinit/check_pointers.py`, `src/projinit/run_checks.py`, `src/projinit/template.py`
- `tests/test_check_materials.py`, `tests/test_check_docs.py`, `tests/test_check_pointers.py`, `tests/test_run_checks.py`
- `README.md`, `pyproject.toml`, `uv.lock`, `docs/Roadmap.md`, `docs/Done.md`, `docs/Done-M6.md`

### 결과
- 참고 자료는 `reference/`, 기존 프로젝트는 `legacy/<이름>/`에 둔다. 공통 규칙 [자료 폴더 규칙](MaterialRule.md)이 두 폴더와 목록 문서(`docs/Reference.md`, `docs/Legacy.md`)를 정한다.
- 자료 폴더 검사기가 목록에 없는 자료, 커밋된 기존 프로젝트의 변경, 기존 프로젝트 안의 `.git`을 보고한다. 자료 폴더 안 코드 파일 링크는 포인터가 아니라 파일 링크로 검사한다.
- `legacy/`에 기존 프로젝트를 넣고 초기화하면, 첫 작업이 그 프로젝트를 먼저 읽고 제품 비전과 첫 로드맵을 쓴다. README에 그 방법을 적었다.
- 이미 초기화한 프로젝트는 갱신하면 새 규칙 문서를 받는다. 문서 작업 규칙에서 링크하므로 인덱스를 고치지 않아도 고아 문서가 되지 않는다.
- 버전 `0.1.5`. 병합 뒤 `v0.1.5` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과(검사기 7개와 테스트)
- 빈 폴더에서 기존 프로젝트·참고 자료를 넣고 초기화부터 커밋 뒤 변경까지 시험: 위 진행 기록대로 동작

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
