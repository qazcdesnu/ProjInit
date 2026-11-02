# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 닫힌 마일스톤의 기록은 [작업 관리 규칙](TaskRule.md#47-완료-기록-보관)에 따라 보관 문서로 옮긴다. 보관 문서: [M0 규칙 체계 정비](Done-M0.md), [M1 검사기 패키지](Done-M1.md), [M2 초기화](Done-M2.md), [M3 갱신](Done-M3.md), [M4 첫 적용](Done-M4.md), [M5 갱신](Done-M5.md), [M6 자료 폴더](Done-M6.md), [M7 테스트 체계](Done-M7.md). 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.



## M8-T2 Codex hook과 강제 장치 검사

- 시작일: 2026-11-02
- 완료일: 2026-11-02
- 근거 문서: [에이전트 지원 설계](design/Agents.md#2-무엇이-다른가), [검증 도구](VerificationTools.md#9-일괄-실행과-자동-실행)
- 참고 자료: 없음

### 계획
- `.codex/hooks.json` 템플릿: Stop은 `check --hook stop --agent codex`, SessionStart는 `context`. 저장소 루트는 `git rev-parse --show-toplevel`로 찾는다.
- `check --hook stop --agent codex`: 통과하면 `{}`를 출력한다(Codex는 종료 코드 0일 때 JSON을 요구한다). 막기와 두 번째 허용은 Claude와 같다. Claude의 출력은 바꾸지 않는다.
- 강제 장치 검사기는 켠 에이전트의 hook만 검사한다. Codex hook 검사를 더한다.
- 초기화 안내에 Codex의 프로젝트·hook 신뢰 단계를 넣는다. 시나리오 테스트에 Codex 프로젝트를 더한다.

### 진행 기록
- 2026-11-02: M8-T1에 이어 시작했다.
- 2026-11-02: `.codex/hooks.json` 템플릿, `check --hook stop --agent codex`, `check_codex_hooks`를 구현했다. 강제 장치 검사기는 켠 에이전트의 hook만 본다. 초기화 안내에 Codex의 프로젝트·hook 신뢰 단계를 넣었다.
- 2026-11-02: 시나리오 `test_agent_rules.py`(9개)를 더했다. `.codex/hooks.json`의 명령을 하위 폴더에서 실제로 실행해 Stop의 통과(`{}`), 막기(종료 코드 2), 두 번째 허용, SessionStart 안내를 확인했다. Codex를 켜도 Claude 파일이 Claude만 쓰는 기준 프로젝트와 같다.

### 결정 사항
- Codex hook 명령은 `git rev-parse --show-toplevel`로 루트를 찾는다. Codex는 세션의 작업 폴더에서 hook을 실행하고 루트 변수를 주지 않는다.
- Codex용 출력 차이는 통과할 때의 `{}` 하나다. 막기와 허용은 Claude와 같은 응답을 쓴다. Claude의 응답은 바뀌지 않았다(단위 테스트로 확인).
- Codex 설정 형식이 Claude Code와 같아 hook 해석 함수를 함께 쓴다. 형식이 다른 에이전트를 더할 때는 따로 만든다.

### 변경 파일
- `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/.codex/hooks.json`(새 파일), `docs/VerificationTools.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/check_hooks.py`, `run_checks.py`, `template.py`, `init.py`
- `tests/unit/test_check_hooks.py`, `test_run_checks.py`, `test_init.py`, `tests/scenario/test_agent_rules.py`(새 파일)
- `docs/design/Agents.md`, `docs/design/Checkers.md`, `docs/design/Templates.md`

### 결과
- Codex를 켜면 `.codex/hooks.json`이 Stop에서 검사하고 SessionStart에서 자료를 알린다. 강제 장치 검사기가 이 hook을 검사한다.
- 실제 Codex에서의 확인은 M8-T3에서 한다.

### 검증
- `uv run projinit check`: 모두 통과


## M8-T1 에이전트 설정, Codex 진입 문서와 시작 skill

- 시작일: 2026-11-02
- 완료일: 2026-11-02
- 근거 문서: [에이전트 지원 설계](design/Agents.md)
- 참고 자료: 없음

### 계획
- 에이전트 지원 설계 문서를 쓴다. Claude Code의 동작은 바꾸지 않고, Codex용 파일을 옆에 더하는 방식이다.
- 설정 `projinit.agents`(기본 `["claude"]`)와 `init --agent codex`. 에이전트별 공통 파일을 나눈다.
- Codex 진입 문서 `AGENTS.md`(`CLAUDE.md`와 본문이 같음)와 시작 skill `.agents/skills/start/`(`$start`, 명시 호출만).
- 문서 링크 검사기가 `AGENTS.md`도 진입 문서로 다룬다.

### 진행 기록
- 2026-11-02: 사용자가 다른 코딩 에이전트가 세션 시작 때 읽는 문서를 조사하라고 했다. Codex는 `AGENTS.md`, Antigravity는 `AGENTS.md`나 `GEMINI.md`를 읽지만, 강제 장치(hook, 시작 명령)는 도구마다 다르다고 답했다. 사용자가 Codex 호환까지 먼저 진행하되, 호환성을 위해 일반화하다가 Claude와 Codex 모두에서 성능이 떨어지면 안 된다고 했다.
- 2026-11-02: 공식 문서로 Codex의 진입 파일(`AGENTS.md`), hook(`.codex/hooks.json`, `stop_hook_active`, 종료 코드 2, hook 신뢰), skill(`.agents/skills`, `$start`, 명시 호출 정책)을 확인하고 에이전트 지원 설계를 썼다. 이 컴퓨터에는 Codex가 설치되어 있지 않아 실제 확인은 M8-T3에서 한다.
- 2026-11-02: 설정 `projinit.agents`, `init --agent`, 에이전트별 공통 파일(`AGENT_FILES`, `common_files`), `AGENTS.md`와 시작 skill 템플릿, 여러 진입 문서 검사를 구현했다. 규칙 문서의 Claude 표현 중 에이전트와 무관한 곳만 "에이전트"로 바꾸고, Claude 고유 설명은 그대로 두었다.
- 2026-11-02: 설계 문서끼리 서로의 함수를 코드 포인터로 걸었더니 그 함수에 두 번째 근거 문서를 요구했다. 다른 설계 문서의 함수는 절 링크와 인라인 코드로 적었다.

### 결정 사항
- Claude용 파일과 hook 출력은 바꾸지 않는다. Codex를 켜도 Claude 쪽은 같다([에이전트 지원 설계](design/Agents.md#1-원칙)).
- 기본 에이전트는 Claude 하나다. 이미 초기화한 프로젝트는 설정에 키가 없어도 지금처럼 동작한다.
- 시작 skill 본문은 Codex가 실제로 읽는 `AGENTS.md`를 가리킨다. 에이전트마다 자기 방식대로 만든다는 원칙에 따른다.
- 끈 에이전트의 파일은 지우지 않고 검사하지 않는다.

### 변경 파일
- `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/design/Agents.md`(새 문서)
- 템플릿: `src/projinit/templates/AGENTS.md`, `.agents/skills/start/SKILL.md`, `.agents/skills/start/agents/openai.yaml`(새 파일), `projinit.toml`, `docs/DocumentationRule.md`, `CodeRule.md`, `TaskRule.md`, `PullRequestRule.md`, `MaterialRule.md`, `VerificationTools.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/config.py`, `template.py`, `init.py`, `doclib.py`, `check_docs.py`, `check_template.py`
- `tests/unit/test_config.py`, `test_template.py`, `test_init.py`, `test_check_docs.py`
- `docs/design/Templates.md`, `docs/design/Checkers.md`, `docs/design/Package.md`, `README.md`

### 결과
- `projinit init --agent codex`로 Codex용 진입 문서와 `$start` skill을 만든다. 설정의 `agents`를 바꾸고 `init --refresh-common`으로 나중에 켤 수도 있다.
- `AGENTS.md`도 진입 문서로 검사한다. 템플릿 테스트가 `AGENTS.md`와 `CLAUDE.md`, skill과 `/start`의 본문이 어긋나지 않게 지킨다.
- Codex의 hook은 아직 없다(M8-T2).

### 검증
- `uv run projinit check`: 모두 통과


## I26 초기화와 갱신이 `.gitignore`에 로컬 자료 폴더를 넣음

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [자료 폴더 규칙](MaterialRule.md#5-로컬-자료-폴더-private), [템플릿 구성 설계](design/Templates.md#9-초기화-명령)
- 참고 자료: 없음

### 계획
- 초기화, `--refresh-common`, 갱신이 `.gitignore`에 `/<private>/` 줄이 없으면 더한다. 파일이 없으면 만든다. 다른 줄은 건드리지 않는다.
- 자료 폴더 규칙 5절과 작업 관리 규칙 4.8절에서 사용자나 에이전트가 줄을 넣는 절차를 뺀다. 자료 폴더 검사기는 그 줄을 지웠을 때의 안전망으로 남긴다.
- README에서 `echo "/private/" >> .gitignore`를 뺀다. 버전 `0.1.11`.

### 진행 기록
- 2026-11-01: 사용자가 README의 `.gitignore`에 줄을 넣는 단계를 보고, 미리 넣어 두면 되는 일을 사용자에게 시키는 게 맞냐고 했다. I24에서 초기화가 이미 있는 파일을 만들 수 없다는 이유로 검사만 하기로 했는데, `.gitignore`는 파일 전체가 아니라 줄 하나만 보장하면 되므로 그 이유가 맞지 않았다.
- 2026-11-01: `ensure_ignored`를 구현해 초기화와 `refresh_common`(갱신 포함)이 부르게 했다. 이 저장소의 `.gitignore`에도 `/private/`가 더해졌다.
- 2026-11-01: 임시 폴더에서 시험했다. 빈 폴더 초기화가 `.gitignore`를 만들고 `git add -A`가 로컬 자료를 스테이징하지 않았다. `v0.1.10`으로 초기화한 프로젝트(기존 `.gitignore` 있음)를 갱신하자 기존 줄은 그대로 두고 `/private/`만 더했다.

### 결정 사항
- `.gitignore`는 공통 파일로 만들지 않고 줄 하나만 보장한다. 기존 저장소의 `.gitignore`를 덮어쓰지 않고, 초기화를 막지도 않는다.
- 이미 있는지는 그 저장소의 `.gitignore` 줄로만 판단한다. 전역 제외 설정은 다른 컴퓨터에 없으므로 세지 않는다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/docs/MaterialRule.md`, `TaskRule.md`, `VerificationTools.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/init.py`, `tests/test_init.py`, `docs/design/Templates.md`, `docs/design/Materials.md`
- `.gitignore`, `README.md`, `pyproject.toml`, `uv.lock`

### 결과
- 초기화, `init --refresh-common`, 갱신이 `.gitignore`에 `/private/` 줄이 없으면 더한다. 사용자가 할 일이 없다.
- 버전 `0.1.11`. 병합 뒤 `v0.1.11` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 시험: 위 진행 기록대로 동작

## I24 로컬 자료 폴더 `private/`

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [자료 폴더 규칙](MaterialRule.md), [검증 도구](VerificationTools.md)
- 참고 자료: 없음

### 계획
- 자료 폴더 규칙에 로컬 자료 폴더 `private/`를 더한다. git에서 빼고(`.gitignore`), 목록 문서를 두지 않고, 어떤 문서도 링크하지 않는다(선택 링크 포함). 근거로 적을 때는 경로를 인라인 코드로 쓰고, 문서에는 공개해도 되는 결정만 옮긴다. 모델에는 내용이 전송되므로 Claude도 보면 안 되는 비밀은 넣지 않는다.
- 문서 링크 검사기: 로컬 자료 폴더로 가는 링크를 문제로 보고한다.
- 자료 폴더 검사기: 로컬 자료가 git에서 빠지지 않았거나 추적·스테이징되었으면 문제로 보고한다.
- 세션 시작 안내에 로컬 자료의 경로를 더한다.
- 설정 `paths.private`, README, 설계 문서. 버전 `0.1.10`.

### 진행 기록
- 2026-11-01: 사용자가 보안 때문에 로컬에서 작업할 때만 볼 파일을 넣는 공간이 필요하다고 했다. `private/` 설계를 제안했고, 사용자가 진행하되 GitHub에 올라가지 않을 뿐 아니라 링크에서도 제외되어야 한다고 했다.
- 2026-11-01: 목업을 만들자 포인터 확인이 새 심볼(`Project.in_private` 등)에 대해 오탐을 냈다. 작업을 stash로 치워 두고 I25로 먼저 고쳤다. 이슈 번호가 차례대로여야 해서 I24의 이슈 줄과 이 기록은 I25의 진행 중 커밋에 함께 넣었다.
- 2026-11-01: 문서 링크 검사기, 자료 폴더 검사기, 세션 시작 안내를 구현하고 테스트를 더했다. 첫 작업 절차와 작업 시작 기록에 로컬 자료를 다루는 방법을 더했다.
- 2026-11-01: 임시 폴더에서 시험했다. `.gitignore` 없이 `private/`에 파일을 넣으면 자료 폴더 검사기가 보고하고, 더하면 통과했다. 문서에서 `private/` 파일을 링크하면 문서 링크 검사기가 보고했다. `context`가 로컬 자료를 알렸다. `git add .`는 로컬 자료를 스테이징하지 않았고, `git add -f`로 강제로 넣은 커밋은 pre-commit이 거부했다.

### 결정 사항
- `private/`는 일반 링크도 선택 링크도 금지한다. 사용자가 정했다([자료 폴더 설계](design/Materials.md#2-결정)).
- `.gitignore`는 만들지 않고 검사만 한다. 초기화는 이미 있는 파일을 만들 수 없다.
- 로컬 자료를 읽으면 내용이 모델로 전송된다는 점을 규칙과 README에 적고, 에이전트도 보면 안 되는 비밀은 넣지 않게 했다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/CLAUDE.md`, `docs/MaterialRule.md`, `docs/DocumentationRule.md`, `docs/TaskRule.md`, `docs/VerificationTools.md`, `docs/index.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/config.py`, `src/projinit/check_docs.py`, `src/projinit/check_materials.py`, `src/projinit/session_context.py`
- `tests/test_check_docs.py`, `tests/test_check_materials.py`, `tests/test_session_context.py`
- `docs/index.md`, `docs/design/Checkers.md`, `docs/design/Materials.md`, `docs/design/Package.md`
- `README.md`, `pyproject.toml`, `uv.lock`

### 결과
- 로컬 자료 폴더 `private/`: git에서 빼고, 어떤 문서도 링크하지 않으며, 목록 문서를 두지 않는다. 세션 시작 안내가 로컬에서만 그 경로를 알린다.
- 무시되지 않거나 추적된 로컬 자료는 커밋할 때 막힌다. `private/` 안으로 가는 링크는 문서 링크 검사기가 막는다.
- 설정 `paths.private`로 위치를 바꿀 수 있다.
- 버전 `0.1.10`. 병합 뒤 `v0.1.10` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 시험: 위 진행 기록대로 동작

## I25 새 심볼은 포인터 확인에서 뺀다

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [포인터 규약](Traceability.md#9-어긋났을-때의-우선순위)
- 참고 자료: 없음

### 계획
- 포인터 규약 9절: 문서 포인터의 대상 심볼이 `HEAD`에 없던 새 심볼이면 확인이 필요 없다. 그 심볼을 가리키는 코드 포인터가 먼저 있었을 수 없다.
- 포인터 검사기의 `check_confirmations`가 `HEAD`의 그 파일에 대상 심볼이 없으면 건너뛰게 하고, 테스트를 더한다.

### 진행 기록
- 2026-11-01: I24에서 `Project`에 새 메서드를 더하고 설계 문서에서 링크하자, `Project` 클래스의 `@doc`이 `HEAD`에 있었다는 이유로 포인터 확인이 요구되었다. 새 심볼이라 오탐이다. I24 작업을 stash로 치워 두고 먼저 고친다.
- 2026-11-01: `check_confirmations`가 대상 심볼이 `HEAD`에 없으면 건너뛰게 했다. 새 테스트는 고치기 전 코드에서 실패하고 고친 뒤 통과한다.

### 결정 사항
- 새 심볼 판정은 `HEAD`의 그 파일 분석 결과에 한정 이름이 있는지로 한다. 파일 자체가 `HEAD`에 없으면 이미 건너뛴다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/docs/Traceability.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/check_pointers.py`, `tests/test_check_pointers.py`, `docs/design/Checkers.md`

### 결과
- `HEAD`에 없던 새 심볼로 거는 문서 포인터는 부모 심볼에 `@doc`이 있어도 포인터 확인을 요구하지 않는다.
- 버전은 I24와 함께 `0.1.10`으로 올린다.

### 검증
- `uv run projinit check`: 모두 통과

## I23 참고 자료 목록 강제를 빼고 세션 시작 때 자료를 알림

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [자료 폴더 규칙](MaterialRule.md), [검증 도구](VerificationTools.md)
- 참고 자료: 없음

### 계획
- 자료 폴더 검사기에서 `reference/`의 목록 검사를 뺀다. `Reference.md`는 선택 문서가 된다. `legacy/`의 목록 검사는 그대로 둔다.
- 세션 시작 hook(`SessionStart`)이 `<projinit> context`를 실행해, `reference/`의 자료와 목록 항목, 목록에 없는 자료를 Claude의 맥락에 넣는다. 강제 장치 검사기가 이 hook도 검사한다.
- 작업 관리 규칙 4.1과 5절: 작업을 시작할 때 관련 자료를 확인하고 진행 중 기록에 `- 참고 자료:` 줄을 남긴다. 검사기로 강제하지는 않는다.
- 갱신 명령의 거부 메시지에 `git stash -u`로 치워 두고 갱신하는 방법을 더한다.
- README, 설계 문서. 버전 `0.1.9`.

### 진행 기록
- 2026-11-01: 사용자가 0.1.7로 초기화한 프로젝트에서 `reference/`에 자료를 넣고 커밋하자 자료 폴더 검사기가 막았고, 갱신도 커밋하지 않은 변경 때문에 거부되었다고 알렸다. 사용자가 참고 자료는 참고할 수도 안 할 수도 있으니 목록 강제를 빼고, 참고하지 않는 문제는 따로 풀자고 했다. 세션 시작 hook과 기록 줄(규칙만)을 제안했고 사용자가 진행하라고 했다.
- 2026-11-01: 규칙과 설계 문서를 고치고 목업을 만들어 진행 중 커밋을 했다. 자료 폴더 검사기, 강제 장치 검사기, `context` 하위 명령, 갱신 거부 메시지를 구현하고 테스트를 고치고 더했다.
- 2026-11-01: 임시 폴더에서 시험했다. 목록 없이 `reference/`에 자료를 넣어도 검사가 통과하고, `context`가 자료와 목록 항목, 목록에 없는 자료를 출력했다. `v0.1.7`로 초기화한 프로젝트에 커밋하지 않은 자료가 있을 때 갱신이 `git stash -u` 안내와 함께 거부되었고, 안내대로 하면 0.1.9로 갱신되어 SessionStart hook이 들어가고 검사가 통과했다.

### 결정 사항
- `legacy/`의 목록 검사는 그대로 둔다. 한 번 넣는 아카이브라 목록 한 줄이 부담이 아니다([자료 폴더 설계](design/Materials.md#2-결정)).
- 진행 중 기록의 `참고 자료` 줄은 규칙으로만 두고 검사하지 않는다. 사용자와 정한 대로 hook부터 시작한다.
- `참고 자료` 줄은 링크가 아니라 인라인 코드 경로로 적는다. 자료는 지워질 수 있고 완료 기록은 고칠 수 없다.
- `context`는 어떤 오류에도 종료 코드 0이다. 세션 시작을 막지 않는다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/docs/MaterialRule.md`, `TaskRule.md`, `VerificationTools.md`, `src/projinit/templates/.claude/settings.json`, 그리고 다시 만든 이 저장소의 같은 파일
- `src/projinit/check_materials.py`, `src/projinit/check_hooks.py`, `src/projinit/session_context.py`, `src/projinit/cli.py`, `src/projinit/upgrade.py`
- `tests/test_check_materials.py`, `tests/test_check_hooks.py`, `tests/test_session_context.py`
- `docs/design/Checkers.md`, `docs/design/Materials.md`, `docs/design/Package.md`, `docs/design/Templates.md`
- `README.md`, `pyproject.toml`, `uv.lock`

### 결과
- `reference/`에 자료를 넣고 목록 없이 커밋할 수 있다. `Reference.md`는 선택 문서다.
- 세션이 시작될 때마다(재개, 맥락 압축 뒤 포함) SessionStart hook이 `reference/`의 자료를 Claude의 맥락에 넣는다. 강제 장치 검사기가 이 hook이 설치되었는지 검사한다.
- 작업을 시작할 때 관련 자료를 찾아 읽고 진행 중 기록의 `참고 자료` 줄에 남긴다.
- 갱신 거부 메시지가 `git stash -u`로 빠져나가는 방법을 알려 준다.
- 버전 `0.1.9`. 병합 뒤 `v0.1.9` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 시험: 위 진행 기록대로 동작

## I22 참고 자료를 넣고 쓰는 방법 보강

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [자료 폴더 규칙](MaterialRule.md)

### 계획
- 자료 폴더 규칙 3절을 나눠, 넣는 것·형식·넣는 방법·쓰는 방법·고치고 지우기를 적는다. 목록 항목에 어디에 쓰는 자료인지를 더하고, 작업을 시작할 때 목록에서 관련 자료를 찾아 읽게 한다. 자료에서 정한 내용은 문서에 옮겨 적고 자료를 링크한다.
- 목록 문서는 자료 폴더 규칙과 템플릿 인덱스가 선택 링크로 가리키게 해, 만들기만 하면 인덱스에서 도달하게 한다.
- 작업 관리 규칙 4.8절: `reference/`에 자료가 있으면 첫 작업이 먼저 읽는다.
- README에 참고 자료와 함께 시작하는 방법과 개발 중에 자료를 더하는 방법을 적는다. 버전 `0.1.8`.

### 진행 기록
- 2026-11-01: 사용자가 기존 프로젝트로 시작하는 기능처럼, 개발에 앞서 찾아본 자료를 Claude Code가 참고하게 넣는 방법의 설명이 부족하다고 했다.
- 2026-11-01: 자료 폴더 규칙 2·3절, 작업 관리 규칙 4.8절, 검증 도구 15절, 템플릿 인덱스를 고치고 공통 문서를 다시 만들었다. README에 참고 자료와 함께 시작하는 절을 더했다.
- 2026-11-01: 임시 폴더에서 `reference/`에 자료를 넣고 초기화했다. 목록 문서가 없으면 자료 폴더 검사기가 알리고, 만들면 통과했다. 인덱스에서 목록 줄을 지운 상태(이미 초기화한 프로젝트를 갱신한 경우)도 자료 폴더 규칙의 선택 링크로 고아 문서가 되지 않았다.

### 결정 사항
- 목록 문서는 자료 폴더 규칙과 템플릿 인덱스가 선택 링크로 가리킨다. 갱신만으로 기존 프로젝트에도 적용된다([자료 폴더 설계](design/Materials.md#2-결정)).
- 자료는 근거, 결정은 문서. 자료에서 정한 것은 프로젝트 문서에 옮겨 적고 자료를 링크한다.
- 형식은 권장만 하고 검사하지 않는다. 검사기는 바꾸지 않았다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 템플릿: `src/projinit/templates/docs/MaterialRule.md`, `TaskRule.md`, `VerificationTools.md`, `index.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `docs/design/Materials.md`, `README.md`, `pyproject.toml`, `uv.lock`

### 결과
- 자료 폴더 규칙이 참고 자료를 무엇을, 어떤 형식으로, 어떻게 넣고, 에이전트가 어떻게 쓰는지 정한다. 항목에 "쓰는 곳"을 적고, 작업을 시작할 때 목록에서 관련 자료를 찾아 읽는다.
- 첫 작업은 `reference/`의 자료를 먼저 읽고 그 자료에서 출발한다.
- README에 참고 자료와 함께 시작하는 방법과 개발 중에 자료를 더하는 방법이 있다.
- 버전 `0.1.8`. 병합 뒤 `v0.1.8` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 시험: 위 진행 기록대로 동작

## I21 README가 없어도 되게 하고, 있으면 정해진 위치에 있어야 하는 문서를 가리키는 선택 링크

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [문서 작업 규칙](DocumentationRule.md)

### 계획
- 문서 작업 규칙 3절에 선택 링크 `[이름](path "선택")`를 정한다. 대상이 없으면 깨진 링크가 아니고, 있으면 일반 링크처럼 검사한다.
- 문서 작업 규칙 2절: README는 없어도 된다. 있으면 루트에 두고, 2절의 README 선택 링크로 인덱스에서 도달한다. 공통 문서가 링크하므로 갱신만 하면 이미 초기화한 프로젝트도 손댈 곳이 없다.
- 템플릿 인덱스의 README 줄을 선택 링크로 바꾸고, 작업 관리 규칙 4.8절에서 "README 줄을 링크로 바꾼다"를 뺀다.
- 문서 링크 검사기가 선택 링크를 해석한다. 버전 `0.1.7`.

### 진행 기록
- 2026-11-01: 사용자가 `upgrade`가 인덱스에 README 링크를 자동으로 넣는지 물었다. 인덱스는 갱신 대상이 아니라 넣지 않는다고 답했다. 사용자가 README 링크는 모든 프로젝트에서 같으니 일률적으로 걸 수 있지 않냐고 했고, 공통 문서에서 링크하되 README가 없으면 링크가 깨진다고 답했다. 사용자가 README는 없어도 된다는 규칙과 함께, 있으면 반드시 그 위치에 있어야 하지만 없어도 되는 선택 링크를 더하라고 했다.

- 2026-11-01: 규칙과 검사기를 고쳤다. 템플릿 테스트의 "공통 문서는 만든 파일로만 링크한다"가 README 선택 링크에 걸려, 선택 링크를 그 검사에서 빼고 템플릿 구성 4절에 적었다.
- 2026-11-01: 임시 폴더에서 시험했다. 초기화 직후(README 없음) 통과, README를 만들면 인덱스를 고치지 않아도 통과, README를 다른 곳에 두면 고아 문서로 보고, 인덱스에서 README 줄을 지운 상태(이미 초기화한 프로젝트를 갱신한 경우)도 문서 작업 규칙의 선택 링크로 통과했다.

### 결정 사항
- 선택 표시는 마크다운 링크 제목(`"선택"`)으로 한다. 마크다운 문법 안에 있어 화면에 보이지 않고, 링크와 표시가 떨어지지 않는다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`
- 템플릿: `src/projinit/templates/docs/DocumentationRule.md`, `TaskRule.md`, `VerificationTools.md`, `index.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/doclib.py`, `src/projinit/check_docs.py`, `tests/test_check_docs.py`, `tests/test_template.py`, `docs/design/Checkers.md`, `docs/design/Templates.md`
- `README.md`, `pyproject.toml`, `uv.lock`, `docs/Done.md`

### 결과
- 선택 링크 `[이름](path "선택")`: 대상이 없으면 깨진 링크가 아니고, 있으면 일반 링크처럼 검사하고 따라간다. 그래서 그 문서는 없어도 되지만, 있으면 링크가 가리키는 위치에 있어야 한다.
- README는 없어도 된다. 공통 문서인 문서 작업 규칙 2절이 README를 선택 링크로 가리키므로, 이미 초기화한 프로젝트도 갱신만 하면 인덱스를 고치지 않고 README가 도달 가능해진다.
- 버전 `0.1.7`. 병합 뒤 `v0.1.7` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 임시 폴더 시험: 위 진행 기록대로 동작

## I20 문서→코드 포인터와 코드→문서 포인터가 어긋날 때의 우선순위와 수정 순서를 검사기로 강제

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [포인터 규약](Traceability.md)

### 계획
- 포인터 규약에 "어긋났을 때의 우선순위" 절을 더한다: 문서→코드 포인터가 기준이고, 문서→코드를 먼저 고친 뒤 그 결과로 코드→문서를 고친다.
- 포인터 검사기를 단계로 나눈다. 문서→코드 포인터에 문제가 있으면 그것만 보고하고 코드 쪽 검사는 하지 않는다.
- 상호 참조 위반은 문서→코드 포인터에서 계산한 코드 쪽 수정안(달아야 할 `@doc:` 줄)으로 보고한다. 받아 주는 문서 포인터가 없는 `@doc:`은 문서에서 판단하라고 보고한다.
- 포인터 확인 검사: 새로 생기거나 대상이 바뀐 문서→코드 포인터가 가리키는 심볼에 `HEAD`부터 그 문서를 가리키는 `@doc:`이 있었으면, 진행 중 기록에 확인 줄(`- 포인터 확인: <문서> → <코드>#<심볼>: <이유>`)이 있어야 통과한다.
- 버전 `0.1.6`.

### 진행 기록
- 2026-11-01: 사용자가 포인터 우선순위 규칙이 반영되어 있는지 물었다. 문서 작업 규칙의 "문서가 기준"과 코드 작업 규칙의 "이름을 바꿀 때 문서 포인터 먼저"는 있지만, 두 방향 포인터 사이의 우선순위와 수정 순서는 없었다. 검사기도 두 방향 위반을 같은 형식으로 보고했다.
- 2026-11-01: 사용자가 자연어 규약만이 아니라 검사기가 순서를 계약대로 강제할 수 있는지 물었다. 단계 검사와 수정안 계산은 강제할 수 있지만, 맞던 문서 포인터를 코드의 `@doc:`에 맞춰 옮기는 수정은 결과 상태만으로는 구분할 수 없다고 답했다. 사용자가 그 경우를 찾아 에이전트가 검증하게 하자고 했고, `HEAD`와 비교해 "코드 포인터가 먼저 있었고 문서 포인터가 따라온" 변경을 찾아 확인 줄을 요구하기로 했다.

- 2026-11-01: 규약(포인터 규약 9절), 검증 도구, 코드 작업 규칙, 검사기 설계와 목업을 먼저 커밋했다(3b3be69).
- 2026-11-01: 구현했다. 확인 검사는 `HEAD`의 문서 링크와 `HEAD`의 코드 파일을 분석해 비교하며, 분석기에 파일 대신 내용을 넘길 수 있게 했다. 테스트 주석에 `@doc:`을 글자 그대로 썼다가 포인터로 해석되어 문장을 바꿨다.
- 2026-11-01: 사용자가 말한 경우를 그대로 시험했다. `load`를 가리키는 문서와 `load`의 `@doc:`을 커밋한 뒤 `@doc:`을 `save`로 잘못 옮겨 커밋하면, 검사기는 `load`에 달 `@doc:` 줄을 계산해 알려 준다. 여기서 문서 링크를 `save`로 옮겨 맞추면 상호 참조는 맞지만 `포인터 확인 필요`로 막힌다.

### 결정 사항
- 확인 줄은 진행 중 문서에 둔다. 커밋 전 작업 트리에서만 의미가 있고(`HEAD`에 들어가면 더는 새 포인터가 아니다), 기록으로 남아 PR에서 사용자가 볼 수 있기 때문이다.
- 코드에 `@doc:` 줄을 자동으로 써 넣지는 않는다. 언어마다 주석과 docstring 위치가 달라 남의 코드를 고치는 위험이 크다.

### 변경 파일
- `docs/Issue.md`, `docs/Ongoing.md`
- 템플릿: `src/projinit/templates/docs/Traceability.md`, `VerificationTools.md`, `CodeRule.md`, 그리고 다시 만든 이 저장소의 같은 문서
- `src/projinit/check_pointers.py`, `src/projinit/doclib.py`, `src/projinit/code_index.py`, `tests/test_check_pointers.py`, `docs/design/Checkers.md`
- `README.md`, `pyproject.toml`, `uv.lock`, `docs/Done.md`

### 결과
- 포인터 규약 9절: 문서→코드 포인터가 기준이고, 문서→코드를 먼저 고친 뒤 그 결과로 코드→문서를 고친다.
- 포인터 검사기는 문서→코드 포인터 문제가 있으면 그것만 보고하고 코드 쪽 검사를 하지 않는다.
- 상호 참조 위반은 대상 심볼 위치에, 링크가 있는 절의 앵커로 계산한 `@doc:` 줄과 함께 보고한다. 받아 주는 문서 포인터가 없는 `@doc:`은 문서에서 판단하라고 보고한다.
- 코드 포인터가 먼저 있었고 문서 포인터가 그것을 따라 생기거나 바뀌면, 진행 중 기록에 이유를 적은 확인 줄이 있어야 통과한다.
- 버전 `0.1.6`. 병합 뒤 `v0.1.6` 태그를 붙인다.

### 검증
- `uv run projinit check`: 모두 통과
- 사용자가 말한 경우(맞던 문서 포인터를 잘못 옮긴 `@doc:`에 맞춤)를 임시 저장소에서 재현: 확인 필요로 막힘
