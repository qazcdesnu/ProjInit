# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 닫힌 마일스톤의 기록은 [작업 관리 규칙](TaskRule.md#47-완료-기록-보관)에 따라 보관 문서로 옮긴다. 보관 문서: [M0 규칙 체계 정비](Done-M0.md), [M1 검사기 패키지](Done-M1.md), [M3 갱신](Done-M3.md). 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M2-T1 템플릿 구성 상세 설계 (공통 규칙과 프로젝트 고유 문서의 경계)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#3-핵심-요구사항)
- 관련 이슈: I10

### 계획
- `projinit init`이 만드는 것, 공통과 고유의 경계, 템플릿 원본의 위치, 문서와 검사기 버전 묶기(I10)를 설계 문서로 정한다.

### 진행 기록
- 2026-10-31: PR #1(I12)이 병합되어, PR 규칙대로 그 작업 브랜치를 로컬과 원격에서 지우고 최신 `main`에서 `m2-t1-template-design` 브랜치를 만들었다.
- 2026-10-31: 공통 규칙 문서에서 다른 프로젝트로 그대로 내보내면 안 되는 부분을 찾았다. 코드 작업 규칙의 디렉터리 표와 Python·uv 스타일, 포인터 규약의 제품 비전 링크, PR 규칙의 원격 주소, 문서·작업 관리 규칙의 `projinit.check_*` 명령이다.
- 2026-10-31: [템플릿 구성](design/Templates.md) 설계 문서를 쓰고 인덱스에 링크했다. 설계에서 나온 일을 M2-T5(템플릿 원본), M2-T6(일치 검사), M2-T7(릴리스와 처음부터 끝까지 시험)으로 로드맵에 추가했다.
- 2026-10-31: 작업 중 사용자가 병합하면 브랜치를 지워야 하지 않느냐고 물었다. 이미 PR 규칙 4절대로 지웠음을 원격 목록으로 확인해 알렸다.

### 결정 사항
- 템플릿 원본은 패키지 안 `src/projinit/templates/` 하나다. 이 저장소의 공통 문서는 템플릿을 이 저장소의 값으로 채운 결과와 같아야 하고, `projinit init --refresh-common`으로 다시 만든다.
- 공통 문서는 공통 문서와 인덱스로만 링크한다. 코드 작업 규칙의 디렉터리 구조와 언어·스타일은 프로젝트 고유 문서인 시스템 구조(`docs/Architecture.md`)로 옮긴다.
- 문서와 검사기는 `projinit.toml`의 `version` 하나로 묶는다(I10). 템플릿 일치 검사와 버전 일치 검사를 `projinit check`에 넣는다. 릴리스는 `main`의 커밋에 `v<버전>` 태그를 붙인다.
- 초기화는 커밋하지 않는다. 첫 커밋은 첫 세션이 커밋 규칙대로 한다.
- 설계 문서만 쓰는 태스크라 목업 단계 없이 처리했다.

### 변경 파일
- `docs/design/Templates.md`(신규), `docs/index.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/ProductVision.md`, `docs/Done.md`

### 결과
- 초기화의 산출물, 공통과 고유의 경계, 템플릿 원본과 빈 자리, 버전 묶기, 남은 M2 태스크의 순서가 정해졌다.

### 검증
- `uv run projinit check`: 모두 통과

## I12 AgentVis에서 분리 후 추가된 커밋 규칙과 PR 규칙(쌓는 작업 브랜치, CI, PR 순서 검사)을 ProjInit에 반영

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [커밋 규칙](CommitRule.md), [PR 규칙](PullRequestRule.md)

### 계획
- AgentVis(`i21-stacked-prs` 브랜치)의 커밋 규칙·PR 규칙과 바뀐 기존 문서를 ProjInit에 맞게 옮긴다.
- 커밋 메시지 검사기를 이력·커밋 시점·PR 검사로 넓히고, PR 순서 검사기, CI 워크플로, PR 템플릿을 만든다.
- 순서: 문서 → 검사기·테스트 → `core.hooksPath` 확인 → 검증 전체 통과 → 완료 처리.

### 진행 기록
- 2026-10-31: 사용자가 AgentVis에서 ProjInit을 분리한 뒤(AgentVis I5) 공통 규칙 체계에 추가된 커밋 규칙과 PR 규칙을 반영하라고 지시했다. 이슈로 등록하고 M0-T6과 연결하라고 했다.
- 2026-10-31: M0-T6은 완료되어 `Done-M0.md`에 보관되어 있다. `연결 작업`으로 묶으면 이 이슈가 시작부터 `[x]`여야 하고 자기 기록을 둘 수 없으므로, 일반 이슈로 등록하고 이슈 줄에 `관련 작업: M0-T6`을 적었다. M0-T6의 보관 기록에는 이 이슈를 가리키는 줄을 덧붙였다.
- 2026-10-31: 새 규칙을 이 작업부터 따랐다. `main`이 아닌 작업 브랜치 `i12-commit-pr-rules`에서 진행한다.
- 2026-10-31: 지금까지의 커밋 25개에 새 메시지 규칙을 미리 적용해 보니 모두 맞았다. 사용자의 기준대로 기준 커밋을 첫 커밋 `18e5cf3`으로 정했다.
- 2026-10-31: 문서를 고친 뒤 `check_commits`(기존 `check_commit_msg`를 넓힘), `check_pr_order`, `projinit` 하위 명령 `commits`·`pr-order`, 설정 키 `check.commit_baseline`, 테스트, CI 워크플로, PR 템플릿을 만들었다. 테스트 두 개는 기대값(제목 길이, 커밋 수)을 잘못 세어 실패했고 기대값을 고쳤다.
- 2026-10-31: `core.hooksPath`는 이미 `.githooks`였다. 빈 커밋으로 commit-msg hook을 시험해, 마침표로 끝나는 요약과 시작하지 않은 작업 ID가 모두 거부되는 것을 확인했다.
- 2026-10-31: 새 PR 규칙대로 작업 브랜치에 커밋해 push하고 PR을 만들었다. 병합은 사용자가 한다.

### 결정 사항
- ProjInit의 `(진행 중)` 표기(M0-T6에서 정함, 이력에 여러 번 쓰임)는 커밋 규칙에 남긴다. PR 제목에는 쓰지 않는다.
- 검사기는 `src/projinit/`에 둔다. 기존 `check_commit_msg`를 `check_commits`로 넓히고, `projinit` 명령에 `commits`, `pr-order` 하위 명령을 더한다. commit-msg hook은 그대로 `projinit commit-msg`다.
- 기준 커밋은 검사기 코드의 상수가 아니라 `projinit.toml`의 `check.commit_baseline`에 둔다. 검사기는 여러 프로젝트가 함께 쓰는 패키지이기 때문이다.
- 커밋 이력 검사는 `projinit check`에 넣는다. 그래서 Stop hook, pre-commit, CI에서 함께 돈다.
- CI의 저장소 사본에는 `core.hooksPath` 설정이 없어 강제 장치 검사기가 실패하므로, 워크플로에서 그 설정을 먼저 한다.
- 커밋 규칙과 PR 규칙은 초기화가 만드는 템플릿에도 들어간다. 원격 저장소 주소처럼 프로젝트마다 다른 부분은 M2-T1에서 템플릿의 빈 자리로 정한다.

### 변경 파일
- `docs/CommitRule.md`(신규), `docs/PullRequestRule.md`(신규), `docs/TaskRule.md`, `docs/CodeRule.md`, `docs/VerificationTools.md`, `docs/design/Checkers.md`, `docs/ProductVision.md`, `docs/index.md`, `CLAUDE.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done-M0.md`
- 추가: `src/projinit/check_commits.py`(신규, `check_commit_msg.py`를 대신함), `src/projinit/check_pr_order.py`(신규), `src/projinit/cli.py`, `src/projinit/config.py`, `src/projinit/run_checks.py`, `tests/test_check_commits.py`(신규, `test_check_commit_msg.py`를 대신함), `tests/test_check_pr_order.py`(신규), `tests/test_cli.py`, `tests/test_config.py`, `tests/test_run_checks.py`, `projinit.toml`, `.github/workflows/verify.yml`(신규), `.github/pull_request_template.md`(신규), `docs/Done.md`

### 결과
- ProjInit이 AgentVis와 같은 커밋 규칙과 PR 규칙을 따른다. 작업은 작업 브랜치에서 하고, 커밋 즉시 push하며, PR로 `main`에 합친다.
- 커밋 메시지는 커밋할 때(commit-msg hook), 일괄 검사 때(이력), PR 때(제목·브랜치·순서, CI) 검사된다.
- 두 규칙은 초기화가 만드는 템플릿에도 들어간다고 제품 비전에 적었다.

### 검증
- `uv run projinit check`: 문서, 포인터, 작업 관리, 강제 장치, 커밋 이력(24개), 테스트 모두 통과
- commit-msg hook이 규칙에 어긋난 커밋 두 개를 거부했다.

## I11 완료 기록은 고칠 수 없는데 문서 구조가 바뀌면 기록 안의 링크가 깨지는 문제

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [작업 관리 규칙](TaskRule.md#45-기록-보존)

### 계획
- 기록에서 고칠 수 있는 부분(링크 대상)과 고칠 수 없는 부분(문장, 링크 표시 이름, 인라인 코드)을 규칙으로 나눈다.
- 기록 보존 검사가 링크 대상을 지운 형태로 줄을 비교하게 하고 테스트를 쓴다.

### 진행 기록
- 2026-10-31: M1-T4에서 검증 도구를 나눌 때, 완료 기록의 링크가 깨지지 않도록 절 제목을 억지로 유지했다. 근본 문제로 보고 등록했다.
- 2026-10-31: 사용자가 "완료 기록에서 내용은 고치지 못하게 하는 식으로 고칠 수 있는 부분과 고칠 수 없는 부분을 미리 구분해 둘 수 있는지" 고민해 보라고 했다. 낡는 것은 사실이 아니라 링크가 가리키는 위치라는 점에서, 링크 대상만 고칠 수 있게 하자고 제안했고 사용자가 진행하라고 했다.
- 2026-10-31: 작업 관리 규칙 4.5절과 6.5절에 예외와 비교 방법을 적고, 기록 보존 검사가 양쪽 줄에서 링크 대상을 지운 뒤 비교하게 했다(`_without_link_targets`). 링크 대상만 바꾼 경우 통과하고 표시 이름을 바꾼 경우 걸리는 테스트를 넣었다.

### 결정 사항
- 고칠 수 있는 것은 마크다운 링크의 대상뿐이다. 링크 표시 이름, 문장, 필드 값, 인라인 코드 안의 경로는 고칠 수 없다.
- 완료 기록의 링크도 문서 링크 검사기가 계속 검사한다. 깨지면 대상을 고친다.
- 링크를 검사에서 빼는 방법, 커밋 해시로 고정한 링크, 링크를 별도 절로 모으는 방법은 쓰지 않는다. 각각 깨진 링크를 모르게 되거나, 검증할 수 없거나, 기록 쓰기가 무거워진다.

### 변경 파일
- `docs/TaskRule.md`, `docs/design/Checkers.md`, `docs/Issue.md`, `docs/Ongoing.md`
- 추가: `src/projinit/check_tasks.py`, `tests/test_check_tasks.py`, `docs/Done.md`

### 결과
- 문서를 개편해 완료 기록의 링크가 깨지면 링크 대상을 고쳐 따라갈 수 있다. 기록의 문장과 링크 표시 이름은 여전히 고칠 수 없다.
- 앞으로 문서 구조를 바꿀 때 완료 기록 때문에 절 제목을 억지로 유지하지 않아도 된다.

### 검증
- `uv run projinit check`: 모두 통과
