# 에이전트 지원 설계

이 문서는 ProjInit으로 초기화한 프로젝트를 Claude Code 말고 다른 코딩 에이전트(먼저 Codex)에서도 같은 규칙 체계로 쓰게 하는 방법을 정한다(M8). 공통 파일의 구성은 [템플릿 구성 설계](Templates.md)에, 검사기 구현은 [검사기 설계](Checkers.md)에 있다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 원칙

사용자는 호환성을 위해 일반화하다가 Claude와 Codex 모두에서 성능이 떨어지면 안 된다고 했다. 그래서 다음을 지킨다.

- **같은 것은 하나로**: 규칙 문서, git hook, CI, 검사기는 에이전트와 무관하다. 그대로 둔다.
- **다른 것은 에이전트별로**: 진입 파일, hook 설정, 시작 명령은 각 에이전트가 가장 잘 쓰는 고유 방식으로 만든다. 둘 다 쓸 수 있는 공통 형식으로 맞추지 않는다.
- **Claude Code는 그대로**: Claude용 파일과 hook 출력은 지금과 한 글자도 다르지 않다. Codex를 켜도 Claude 쪽은 바뀌지 않는다.
- **켠 에이전트의 파일만 만든다**: 쓰지 않는 에이전트의 파일로 저장소를 어지럽히지 않는다.

## 2. 무엇이 다른가

공식 문서로 확인한 차이다(2026-11-02).

| 장치 | Claude Code | Codex |
| --- | --- | --- |
| 진입 파일 | `CLAUDE.md` | `AGENTS.md`. 저장소 루트부터 작업 폴더까지 폴더마다 하나를 이어 붙이고, 합계 32KiB까지 읽는다. |
| hook 설정 | `.claude/settings.json`의 `hooks` | `.codex/hooks.json`의 `hooks`. 이벤트·matcher·`type: "command"` 구조와 필드 이름이 거의 같다. |
| hook 실행 위치 | `$CLAUDE_PROJECT_DIR`로 프로젝트 루트를 안다 | 세션의 작업 폴더에서 실행한다. 루트 변수가 없어 `git rev-parse --show-toplevel`로 찾는다. |
| Stop으로 막기 | 종료 코드 2와 표준 오류. 입력의 `stop_hook_active`로 두 번째 종료를 안다. | 같다(종료 코드 2와 표준 오류, `stop_hook_active`). 다만 종료 코드 0이면 표준 출력이 JSON이어야 한다. |
| SessionStart 안내 | 표준 출력이 맥락에 들어간다 | 같다. 일반 텍스트 표준 출력이 개발자 맥락에 들어간다. |
| hook 신뢰 | 별도 절차 없음 | 프로젝트 `.codex/` 층을 신뢰해야 하고, hook마다 `/hooks`에서 신뢰해야 돈다. 내용이 바뀌면 다시 신뢰해야 한다. |
| 시작 명령 | `.claude/commands/start.md`의 `/start` | 프로젝트 단위 사용자 명령이 없다. skill `.agents/skills/start/SKILL.md`를 `$start`로 부른다. |

## 3. 설정

- [설정](../VerificationTools.md#11-설정)의 `projinit.agents`에 쓸 에이전트를 적는다. 값은 `claude`, `codex`이며 기본은 `["claude"]`다. 이미 초기화한 프로젝트는 설정에 이 키가 없으므로 지금처럼 Claude만 쓴다.
- 새로 초기화할 때는 `projinit init --agent codex`처럼 `--agent`를 여러 번 줄 수 있다. 주지 않으면 `claude`다.
- 나중에 켜려면 설정의 `projinit.agents`를 고치고 `init --refresh-common`을 실행한다. 끈 에이전트의 파일은 지우지 않는다. 사용자가 고친 것일 수 있어서다. 대신 [템플릿 일치 검사기](../VerificationTools.md#14-템플릿-일치-검사기)가 검사하지 않는다.
- `claude`를 빼는 것도 허용한다. `CLAUDE.md`는 에이전트와 상관없이 규칙 문서 체계의 루트([설정](../VerificationTools.md#11-설정)의 `paths.entry`)이므로 언제나 만든다.

## 4. 에이전트별 공통 파일

[공통 파일](Templates.md#1-초기화가-만드는-것) 중 다음은 그 에이전트를 켰을 때만 만든다.

| 에이전트 | 파일 | 하는 일 |
| --- | --- | --- |
| claude | `.claude/settings.json`, `.claude/commands/start.md` | Stop·SessionStart hook, `/start` |
| codex | `AGENTS.md` | Codex 진입 문서. 첫 줄 제목만 빼고 `CLAUDE.md`와 같다. |
| codex | `.codex/hooks.json` | Stop·SessionStart hook. 명령은 `git rev-parse --show-toplevel`로 루트에 간 뒤 실행한다. Stop은 `check --hook stop --agent codex`다. |
| codex | `.agents/skills/start/SKILL.md`, `.agents/skills/start/agents/openai.yaml` | `$start` skill. 명시적으로 부를 때만 쓴다(`allow_implicit_invocation: false`). 사용자가 다른 말을 할 때 첫 작업 절차가 끼어들지 않게 하기 위해서다. |

## 5. 진입 문서 `AGENTS.md`

- 본문은 `CLAUDE.md`와 같다. 규칙 문서로 가는 링크만 있으므로 에이전트와 무관하다. 둘을 다르게 두면 한쪽 규칙만 바뀌는 일이 생긴다. 템플릿 테스트가 두 템플릿의 본문이 같은지 확인한다.
- `CLAUDE.md`에서 `AGENTS.md`를 가져오게(`@AGENTS.md`) 하지 않는다. Claude Code의 읽기 방식을 바꾸지 않기 위해서다.
- [문서 링크 검사기](../VerificationTools.md#3-문서-링크-검사기)는 `AGENTS.md`가 있으면 `CLAUDE.md`와 같은 진입 문서 검사(인덱스 링크, 형식)를 하고 고아 문서 판정에서 뺀다.

## 6. 시작 skill

- `SKILL.md`는 frontmatter의 `name: start`와 `description`, 본문으로 이뤄진다. 본문은 `/start` 명령과 같은 지시이되, 읽는 진입 문서 이름만 Codex가 읽는 `AGENTS.md`로 쓴다.
- `agents/openai.yaml`의 `policy.allow_implicit_invocation: false`로 명시 호출(`$start`)만 허용한다.
- 템플릿 테스트가 skill 본문과 `/start` 명령 본문이 진입 문서 이름만 빼고 같은지 확인한다.

## 7. 작업 범위

- M8-T1: 설정 `projinit.agents`, `init --agent`, 에이전트별 공통 파일, `AGENTS.md`, 시작 skill, 진입 문서 검사, 규칙 문서와 README의 에이전트 표현.
- M8-T2: Codex hook(`.codex/hooks.json`), `check --hook stop --agent codex`, 강제 장치 검사기의 Codex 검사, 시나리오 테스트.
- M8-T3: 실제 Codex CLI로 진입 문서, `$start`, hook 신뢰와 Stop 막기, 세션 시작 안내를 확인하고 `0.3.0`으로 올린다.
