# 완료 보관 M2 초기화

이 문서는 닫힌 마일스톤 M2의 완료 기록을 보관한다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 아직 닫히지 않은 마일스톤의 기록은 [완료](Done.md)에 있다.

## M2-T7 `v0.1.0` 릴리스와 빈 폴더에서 처음부터 끝까지 시험

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md#5-버전-묶기-i10)

### 계획
- 모든 기능이 병합된 `main`에 `v0.1.0` 태그를 붙여 원격에 올린다.
- 빈 폴더에서 README의 "새 프로젝트 시작하기" 명령 그대로 초기화하고, 검사와 hook을 시험한다.
- 사용자가 Claude Code에서 `/start`로 첫 작업을 시작해 보고, 그 결과로 완료 처리한다.

### 진행 기록
- 2026-10-31: 사용자가 PR #7, #8을 병합하고 "테스트 해볼까?"라고 했다. 저장소가 공개(PUBLIC)임을 확인했다. 병합된 작업 브랜치를 로컬과 원격에서 지웠다.
- 2026-10-31: `main`의 `ff5432d`(PR #8 병합 커밋)에 주석 달린 태그 `v0.1.0`을 붙여 원격에 올렸다.
- 2026-10-31: 임시 폴더에서 `uvx --from git+https://github.com/qazcdesnu/ProjInit@v0.1.0 projinit init`을 실행했다. 처음에는 GitHub에서 받아 빌드하고 tree-sitter와 문법 패키지 8개를 받느라 오래 걸렸다(사용자가 "왜 이렇게 오래 걸리냐"고 물었다). 파일 20개가 만들어졌고 hook은 `uvx --from …@v0.1.0 projinit`을 부르게 설치되었다. `projinit check`의 검사 6개가 모두 통과했다.
- 2026-10-31: 첫 작업 절차대로 `M0-T1`을 시작 처리하고 `M0-T1(진행 중): ProjInit으로 초기화`로 첫 커밋을 했다. pre-commit과 commit-msg가 통과해 커밋되었고, 커밋에 약 7.5초가 걸렸다. 작업 ID 없는 메시지는 commit-msg가 거부했다. 캐시가 생긴 뒤 `projinit check` 한 번은 약 4초다.
- 2026-10-31: 임시 폴더의 문서를 고칠 때 `uv run` 없이 시스템 `python3`를 한 번 썼다. 결과에는 영향이 없지만 규칙 위반이다.
- 2026-10-31: 사용자가 직접 초기화한 폴더에서 Claude Code를 열고 `/start`를 입력했다. Claude가 `M0-T1`을 시작 처리하고(로드맵 `[~]`, 진행 중 기록), `main`이 없어 작업 브랜치를 만들지 않았으며, 검사를 통과시킨 뒤 목적·사용자·필수 기능·언어와 기술 스택·테스트 방식·원격 저장소를 묻고, 정하지 않은 것은 "미결정"으로 남기겠다고 안내했다. 사용자는 "아주 만족스럽다, 더 사용해 보겠다"고 했다.
- 2026-10-31: M2의 마지막 태스크라 완료와 함께 M2를 닫고, 완료 문서의 기록을 `docs/Done-M2.md`로 그대로 옮겼다.

### 결정 사항
- 릴리스 태그는 주석 달린 태그로 붙인다.
- `/start`로 시작하는 첫 세션은 대화형이라 이 세션에서 시험할 수 없어 사용자가 시험한다.

### 변경 파일
- `docs/Roadmap.md`, `docs/Ongoing.md`
- 저장소 밖: 원격 태그 `v0.1.0`
- 추가: `docs/Done.md`, `docs/Done-M2.md`(신규)

### 결과
- `v0.1.0`이 릴리스되어, 어느 컴퓨터에서든 README의 명령으로 새 프로젝트를 초기화하고 Claude Code에서 `/start`로 첫 작업을 시작할 수 있다.
- M2(초기화)가 닫혔다.

### 검증
- `uv run projinit check`: 모두 통과
- 빈 폴더 처음부터 끝까지: `uvx …@v0.1.0 projinit init` → `projinit check` 통과 → 첫 커밋(hook 통과) → 잘못된 커밋 거부 → 사용자의 `/start` 첫 세션 정상.

## I13 README.md 작성 (사용법과 기본 정보), 루트 README를 허용하는 문서 규칙과 링크 검사

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [문서 작업 규칙](DocumentationRule.md#2-형식)

### 계획
- 문서 작업 규칙에 루트 `README.md`를 소개·사용법 문서로 허용하는 예외를 더한다(템플릿에서 고쳐 다시 만든다).
- 문서 링크 검사가 README의 링크도 검사하게 한다.
- 첫 작업 절차에 README 쓰기를 넣는다.
- ProjInit의 README를 쓴다.

### 진행 기록
- 2026-10-31: 사용자가 "말로 설명만 하지 말고 README.md를 만들어야지, 사용법과 기본 정보는 README.md에 두는 게 기본 중의 기본"이라고 지적했다. 문서 작업 규칙이 루트에 `CLAUDE.md`만 허용하고 있어 규칙부터 고쳤다.
- 2026-10-31: PR #3~#6은 병합되었고 #7이 열려 있어 `m2-t4-start-command` 위에 `i13-readme`를 쌓았다.
- 2026-10-31: 템플릿(문서 작업 규칙, 검증 도구, 작업 관리 규칙)을 고치고 `--refresh-common`으로 이 저장소에 반영했다. `doclib`에 `README_DOC`을 두고 `find_doc_files`가 README를 포함하게 했다.
- 2026-10-31: README에 소개, 무엇을 해 주나, 필요한 것, 사용법(새 프로젝트, 미리 써 보기, 초기화가 만드는 것, 명령), 규칙 체계, ProjInit 개발하기를 썼다.

### 결정 사항
- README는 소개와 사용법만 담고 규칙과 설계는 `docs/`로 링크한다. 같은 내용이 두 곳에 있으면 어긋나도 알 수 없기 때문이다.
- README는 링크 검사 대상이지만 고아 문서 판정에는 넣지 않는다. 인덱스가 아니라 저장소 첫 화면에서 읽는 문서이기 때문이다.
- 초기화된 프로젝트도 첫 작업에서 README를 쓰게 했다. 초기화가 README를 만들지는 않는다. 내용이 전부 프로젝트 고유이기 때문이다.

### 변경 파일
- `README.md`(신규), `src/projinit/templates/docs/DocumentationRule.md`, `src/projinit/templates/docs/VerificationTools.md`, `src/projinit/templates/docs/TaskRule.md`, `docs/DocumentationRule.md`, `docs/VerificationTools.md`, `docs/TaskRule.md`, `docs/design/Checkers.md`, `src/projinit/doclib.py`, `tests/test_check_docs.py`, `docs/Issue.md`, `docs/Ongoing.md`

### 결과
- 저장소 첫 화면의 README에서 ProjInit이 무엇인지, 어떻게 설치·실행하는지(릴리스 뒤와 미리 써 보기), 초기화가 무엇을 만드는지 알 수 있다.
- README의 링크도 검사되고, 초기화된 프로젝트도 첫 작업에서 README를 쓴다.

### 검증
- `uv run projinit check`: README 링크 포함 모두 통과

## M2-T4 첫 세션에서 만들 프로젝트를 묻고 제품 비전과 첫 로드맵을 채우는 시작 안내

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#3-핵심-요구사항), [템플릿 구성](design/Templates.md#1-초기화가-만드는-것)

### 계획
- 첫 작업 절차를 작업 관리 규칙(공통)에 적고, 그 절차를 부르는 `/start` 명령 파일을 템플릿에 둔다.
- 첫 커밋을 `main`에 하는 예외를 PR 규칙에 적는다.
- 초기화가 끝나면 사용법(`/start`)을 출력한다.

### 진행 기록
- 2026-10-31: 제품 비전은 "사용자가 입력하지 않아도 Claude가 먼저 묻는다"였다. Claude Code 공식 문서를 확인하니 대화형 세션에서 Claude가 먼저 말하게 하는 기능은 없고, SessionStart hook은 맥락이나 사용자 안내만 넣는다. `claude "첫 프롬프트"`로 여는 방법은 있다.
- 2026-10-31: 사용자가 "세션 열자마자 Claude가 물어볼 필요 없이, 이미 있는 명령으로 시작하면 되지 않느냐"고 했다. 프로젝트 슬래시 명령 `/start`(`.claude/commands/start.md`)로 정했다. 기본 명령 `/init`과 겹치지 않게 이름을 골랐다.
- 2026-10-31: PR #3~#6 위에 `m2-t4-start-command`를 쌓았다. 이번부터 공통 문서는 템플릿을 고친 뒤 `projinit init --refresh-common`으로 이 저장소에 반영했다(작업 관리 규칙, PR 규칙, 코드 작업 규칙, `/start` 명령 파일).
- 2026-10-31: 초기화 테스트에 `/start` 명령 파일과 마지막 안내 문구 확인을 더했다. 작은 작업이라 진행 중 커밋 없이 완료까지 한 번에 했다.

### 결정 사항
- 첫 작업 절차는 작업 관리 규칙 4.8절에 두고, 명령 파일은 그 절을 따르라고만 적는다. 구체적인 규칙은 문서에만 둔다는 원칙 때문이다.
- 저장소의 첫 커밋(`M0-T1`)은 `main`에 한다. 아직 `main`이 없어 작업 브랜치의 출발점이 없기 때문이다.
- 명령 파일은 공통 파일이라 이 저장소에도 생긴다. 이 저장소에서 `/start`는 쓸 일이 없지만, 템플릿 일치 검사를 예외 없이 유지한다.
- 제품 비전 요구사항 6을 `/start`로 시작하는 것으로 고쳤다.

### 변경 파일
- `docs/ProductVision.md`, `docs/design/Templates.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `src/projinit/templates/docs/TaskRule.md`, `src/projinit/templates/docs/PullRequestRule.md`, `src/projinit/templates/docs/CodeRule.md`, `src/projinit/templates/.claude/commands/start.md`(신규), `docs/TaskRule.md`, `docs/PullRequestRule.md`, `docs/CodeRule.md`, `.claude/commands/start.md`(신규), `src/projinit/template.py`, `src/projinit/init.py`, `tests/test_init.py`

### 결과
- 초기화한 폴더에서 Claude Code를 열고 `/start`를 입력하면, Claude가 만들 프로젝트를 물으며 첫 작업(`M0-T1`)을 규칙대로 시작한다. 초기화가 마지막에 이 사용법을 알려 준다.

### 검증
- `uv run projinit check`: 모두 통과

## M2-T6 템플릿 일치 검사와 버전 일치 검사

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 관련 이슈: I10
- 근거 문서: [템플릿 구성](design/Templates.md#5-버전-묶기-i10), [검증 도구](VerificationTools.md#14-템플릿-일치-검사기)

### 계획
- 공통 문서인 검증 도구에 템플릿 일치 검사기 절을 더하고(템플릿과 이 저장소 문서 모두), 검사기 설계에 구현 명세를 적는다.
- `check_template`을 만들어 `projinit check`에 넣는다. 템플릿 테스트의 자기 일치 테스트는 이 검사로 옮겨 지운다.

### 진행 기록
- 2026-10-31: PR #3~#5가 열려 있어 `m2-t3-install-devices` 위에 `m2-t6-template-check`를 쌓았다.
- 2026-10-31: 검증 도구는 공통 문서라 이 저장소의 문서와 템플릿을 함께 고쳤다. 이번 검사가 생기면 둘이 어긋날 때 바로 잡힌다.
- 2026-10-31: 첫 진행 중 커밋에서 상호 참조 검사가, 검사기 설계 문서가 `init.package_version`을 직접 가리키는데 그 함수는 템플릿 구성 문서만 근거로 둔다는 것을 잡았다. 검사기 설계에서는 템플릿 구성 문서의 절로 링크하도록 고쳐 커밋했다(3495c8b).
- 2026-10-31: `check_template`과 테스트를 구현해 `projinit check`에 넣고, 템플릿 테스트의 자기 일치 테스트를 지웠다. 이 저장소도 새 검사를 통과했다.
- 2026-10-31: 초기화한 임시 폴더의 공통 문서에 한 줄을 더하자 템플릿 일치 검사가 잡는 것을 확인했다.

### 결정 사항
- 템플릿 일치 검사는 공통 파일 전체(문서와 강제 장치 파일)를 본다. 강제 장치 파일의 명령도 버전에서 나오기 때문이다.
- 버전 일치 검사는 실행 명령이 지정된 저장소(이 저장소, 미리 써 보기 설정)에서 건너뛴다.

### 변경 파일
- `docs/VerificationTools.md`, `src/projinit/templates/docs/VerificationTools.md`, `docs/design/Checkers.md`, `docs/design/Templates.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- 추가: `src/projinit/check_template.py`(신규), `src/projinit/run_checks.py`, `tests/test_check_template.py`(신규), `tests/test_template.py`, `tests/test_run_checks.py`, `docs/Done.md`

### 결과
- 공통 문서와 강제 장치 파일을 손으로 고치거나 설정의 버전만 올리면 `projinit check`가 잡는다. 문서와 검사기가 같은 버전으로 묶인다(I10).

### 검증
- `uv run projinit check`: `check_template` 포함 모두 통과

## M2-T3 초기화할 때 강제 장치 설치

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md#9-초기화-명령)

### 계획
- 강제 장치 파일 다섯 개를 템플릿으로 만들어 공통 파일에 넣고, 설정에서 만든 명령으로 빈 자리를 채운다.
- 초기화할 때 hook 실행 권한과 `core.hooksPath`를 설정한다.
- 갓 초기화한 저장소가 검증 전체를 통과하는지 테스트한다.

### 진행 기록
- 2026-10-31: PR #4(M2-T2) 위에 `m2-t3-install-devices`를 쌓았다.
- 2026-10-31: 갓 초기화한 저장소에는 커밋이 없어 커밋 이력 검사의 `git log`가 실패한다는 것을 설계 중에 발견했다. 커밋이 없으면 0개로 보도록 검사기 설계를 고쳤다.
- 2026-10-31: 설계와 목업으로 진행 중 상태를 커밋했다(0056004).
- 2026-10-31: hook 명령 전체를 빈 자리로 두면 그 안의 큰따옴표가 `.claude/settings.json`을 깬다는 것을 알고, 실행 명령 `{{projinit}}` 하나만 빈 자리로 두도록 설계를 고쳤다.
- 2026-10-31: 강제 장치 템플릿 다섯 개, `render_values`, 실행 권한과 `core.hooksPath` 설정, 빈 저장소의 커밋 이력 처리를 구현했다. 이 저장소에 `--refresh-common`을 실행하니 CI 파일의 주석 한 줄만 다시 쓰였다.
- 2026-10-31: 갓 초기화한 폴더에서 `check`의 모든 검사기(문서, 포인터, 작업 관리, 강제 장치, 커밋 이력)가 통과하는 것을 테스트로 확인했다.

### 결정 사항
- 강제 장치 파일은 공통 파일로 다룬다. hook 명령이 설정의 버전에서 나오므로, 버전이 바뀌면 `--refresh-common`으로 함께 다시 써야 하기 때문이다.
- GitHub Actions 식(`${{ … }}`)은 공백과 점이 있어 빈 자리 문법(`{{영문 소문자·숫자·_}}`)과 겹치지 않는다.

### 변경 파일
- `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- 추가: `src/projinit/templates/.claude/settings.json`·`.githooks/pre-commit`·`.githooks/commit-msg`·`.github/workflows/verify.yml`·`.github/pull_request_template.md`(신규), `src/projinit/template.py`, `src/projinit/init.py`, `src/projinit/check_commits.py`, `tests/test_init.py`, `tests/test_template.py`, `.github/workflows/verify.yml`, `docs/Done.md`

### 결과
- `projinit init`이 문서와 설정에 더해 Stop hook, pre-commit, commit-msg, CI, PR 템플릿을 설치하고 `core.hooksPath`를 설정한다. 갓 초기화한 폴더가 처음부터 검증 전체를 통과한다.

### 검증
- `uv run projinit check`: 모두 통과

## M2-T2 `projinit init` 명령

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md#9-초기화-명령)

### 계획
- `projinit init`(공통·처음 파일과 설정 파일 만들기, `git init`)과 `--refresh-common`을 만든다.
- 설정 파일을 템플릿으로 옮긴다.
- 이 저장소의 공통 문서를 `--refresh-common`으로 다시 만들어 템플릿과 같은지 확인한다.

### 진행 기록
- 2026-10-31: PR #3(M2-T5)이 아직 병합되지 않아, PR 규칙대로 그 브랜치 위에 `m2-t2-init-command`를 쌓았다.
- 2026-10-31: 설계를 쓰고 목업을 만들어 진행 중 상태를 커밋했다(314b420).
- 2026-10-31: 설정 파일 템플릿, `init.py`, `projinit init` 하위 명령, 테스트를 구현했다. 이 저장소에 `--refresh-common`을 실행하니 다시 쓴 공통 문서가 0개라 템플릿과 같음을 확인했다.
- 2026-10-31: 초기화 결과의 문서 링크 검사에서 PR 규칙이 링크하는 `.github/pull_request_template.md`가 없어 실패했다. 그 파일은 M2-T3이 설치하므로, 그 전까지 테스트에서 빈 파일로 둔다.
- 2026-10-31: 임시 폴더에서 `projinit init`을 실행해 파일 14개와 git 저장소가 만들어지는 것을 확인했다.

### 결정 사항
- 원격 주소는 인자, git `origin`, "아직 없음" 순서로 정한다. 새 프로젝트에는 원격 저장소가 아직 없는 경우가 많기 때문이다.
- 초기화는 커밋하지 않는다(템플릿 구성 설계 1절). hook과 CI 설치는 M2-T3이 맡는다.

### 변경 파일
- `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- 추가: `src/projinit/init.py`(신규), `src/projinit/templates/projinit.toml`(신규), `src/projinit/template.py`, `src/projinit/cli.py`, `tests/test_init.py`(신규), `tests/test_template.py`, `tests/test_cli.py`, `docs/Done.md`

### 결과
- `projinit init`으로 빈 폴더에 공통 규칙 문서, 처음 작업 관리 문서, 설정 파일을 만들고 git 저장소를 연다.
- `projinit init --refresh-common`으로 공통 문서를 템플릿에서 다시 만든다. 이제 공통 규칙은 템플릿을 고친 뒤 이 명령으로 이 저장소에 반영한다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 초기화: 파일 14개, `.git` 생성

## M2-T5 템플릿 원본 만들기 (공통 문서 분리, 시스템 구조 문서, 템플릿 테스트)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [템플릿 구성](design/Templates.md)

### 계획
- 공통 규칙 문서에서 ProjInit 전용 내용을 떼어 내고, 이 저장소의 시스템 구조 문서(`docs/Architecture.md`)를 만든다.
- 공통 파일과 처음 만드는 파일의 템플릿을 `src/projinit/templates/`에 두고, 빈 자리를 채우는 `template.py`와 설정의 `[template]` 표를 만든다.
- 템플릿 테스트를 쓴다.

### 진행 기록
- 2026-10-31: PR #2가 병합되어 그 브랜치를 지우고 최신 `main`에서 `m2-t5-template-source`를 만들었다.
- 2026-10-31: 코드 작업 규칙의 디렉터리 표(ProjInit 전용 행), 언어와 스타일(Python·uv·PEP 8), 테스트(unittest)를 시스템 구조 문서로 옮기고, 그 절에는 공통 원칙만 남겼다. 절 제목은 그대로 두었다. 문서·작업 관리 규칙의 `projinit.check_*` 명령, 포인터 규약의 제품 비전 링크, 커밋 규칙의 기준 커밋 해시와 예시, PR 규칙과 작업 관리 규칙의 예시를 공통 표현으로 바꿨다.
- 2026-10-31: 문서를 고친 뒤 `template.py`와 `Config.template_values` 목업을 만들어 진행 중 상태를 커밋했다(b07b666, 목업 8개).
- 2026-10-31: 검증 도구의 설정 예시에 빈 자리 글자가 그대로 있어 템플릿을 채울 때 예시까지 바뀌는 문제를 발견했다. 빈 자리 이름을 영문 소문자·숫자·`_`로 좁히고 예시에서 그 글자를 뺐다.
- 2026-10-31: 공통 파일 8개와 처음 만드는 파일 5개의 템플릿을 만들고, `render`, 설정의 `[template]` 표, 템플릿 테스트를 구현했다. 빌드한 패키지에 템플릿 13개가 모두 들어가는 것을 확인했다.

### 결정 사항
- 공통 문서에서 시스템 구조 문서로는 링크하지 않는다. 초기화 직후에는 그 문서가 없기 때문이다. 대신 "인덱스의 제품 이해 절에 있다"고 적는다.
- 인덱스는 처음에만 만드는 파일로 다룬다. 프로젝트 고유 문서가 생기면 프로젝트가 고치기 때문이다.
- PR 규칙의 원격 주소는 템플릿에서 빈 자리 `{{repository}}`가 되고, 이 저장소의 값은 `projinit.toml`의 `[template]`에 둔다.
- 템플릿 테스트가 이 저장소의 공통 파일이 템플릿과 같은지 본다. 그래서 M2-T2에서 `--refresh-common`이 생기기 전까지는 공통 규칙을 고칠 때 문서와 템플릿을 함께 고쳐야 한다.

### 변경 파일
- `docs/Architecture.md`(신규), `docs/CodeRule.md`, `docs/DocumentationRule.md`, `docs/TaskRule.md`, `docs/Traceability.md`, `docs/CommitRule.md`, `docs/PullRequestRule.md`, `docs/VerificationTools.md`, `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/design/Package.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`
- 추가: `src/projinit/template.py`(신규), `src/projinit/templates/`(신규, 13개 파일), `src/projinit/config.py`, `tests/test_template.py`(신규), `projinit.toml`, `docs/Done.md`

### 결과
- 초기화에 쓸 템플릿 원본이 패키지 안에 생겼고, 공통 문서에서 ProjInit 전용 내용이 빠졌다.
- 템플릿을 빈 폴더에 채우면 문서 링크 검사와 작업 관리 검사를 통과하고, 공통 문서는 공통 파일로만 링크한다.

### 검증
- `uv run projinit check`: 모두 통과
- 빌드한 wheel에 `projinit/templates/` 13개 파일이 들어 있다.

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
