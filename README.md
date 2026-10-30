# ProjInit

ProjInit은 **Claude Code 프로젝트 초기화 CLI**다. 빈 폴더에 문서와 코드 두 축의 규칙 체계를 깔아 주고, 그 폴더에서 Claude Code를 열어 `/start`를 입력하면 Claude가 만들 프로젝트를 물어보며 첫 작업을 시작한다. 어떤 프로젝트에서든 같은 방식으로 일하는 것이 목적이다.

> 상태: 개발 중이다. 첫 릴리스 `v0.1.0`은 아직 나오지 않았다. 지금은 아래 [미리 써 보기](#미리-써-보기) 방법으로 쓸 수 있다. 진행 상황은 [로드맵](docs/Roadmap.md)에 있다.

## 무엇을 해 주나

초기화한 프로젝트에서는 다음이 처음부터 갖춰져 있다.

- **문서 우선**: 문서를 먼저 쓰고 그 지시에 따라 코드를 쓴다. 진입 문서 `CLAUDE.md`에서 모든 규칙 문서로 이어진다.
- **문서 ↔ 코드 포인터**: 문서는 코드의 심볼을, 코드는 근거 문서를 가리킨다. 개발 언어와 무관하다(Python, JavaScript, TypeScript, Rust, C, C++, Go, Java).
- **작업 ID와 기록**: 모든 작업이 로드맵·이슈의 ID로 시작하고 끝나며, 진행 중·완료 기록이 남는다.
- **커밋과 PR 규칙**: 커밋 제목은 작업 ID로 시작하고, 작업마다 브랜치를 만들어 PR로 합친다.
- **자동 검사**: Claude가 턴을 끝낼 때(Stop hook), 커밋할 때(pre-commit, commit-msg), PR을 열 때(GitHub Actions) 규칙을 검사한다. 사람이 검사를 기억할 필요가 없다.

## 필요한 것

- [uv](https://docs.astral.sh/uv/) — ProjInit과 검사기를 실행한다.
- git
- [Claude Code](https://code.claude.com/)
- GitHub CLI `gh` — PR을 만들 때 (선택)

## 사용법

### 새 프로젝트 시작하기

`v0.1.0` 릴리스 뒤에는 이렇게 시작한다.

```sh
uvx --from git+https://github.com/qazcdesnu/ProjInit@v0.1.0 projinit init --root ~/my-project
cd ~/my-project
claude
```

Claude Code가 열리면 `/start`를 입력한다. Claude가 만들 프로젝트를 묻고, 대화로 제품 비전·시스템 구조 문서와 첫 로드맵을 쓴 뒤 첫 커밋을 한다.

원격 저장소가 이미 있으면 `--repository <주소>`로 알려 준다. 없으면 나중에 `projinit.toml`의 `template.repository`를 고치고 `projinit init --refresh-common`을 실행한다.

### 미리 써 보기

릴리스 전에는 이 저장소를 받아 그 코드로 초기화한다.

```sh
git clone https://github.com/qazcdesnu/ProjInit ~/ProjInit
uv run --project ~/ProjInit projinit init --root ~/my-project
cd ~/my-project
```

초기화된 프로젝트의 hook은 릴리스된 버전(`uvx … @v0.1.0`)을 부르도록 만들어지므로, 아직은 받아 둔 코드를 부르게 바꾼다. `projinit.toml`의 `[projinit]` 아래에 한 줄을 넣고 공통 파일을 다시 만든다.

```toml
command = "uv run --project /Users/<나>/ProjInit projinit"
```

```sh
uv run --project ~/ProjInit projinit init --refresh-common
claude
```

### 초기화가 만드는 것

| 구분 | 파일 |
| --- | --- |
| 진입 문서 | `CLAUDE.md` |
| 공통 규칙 문서 | `docs/`의 문서 작업·코드 작업·포인터·작업 관리·커밋·PR 규칙, 검증 도구 |
| 작업 관리 문서 | `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md` |
| 설정 | `projinit.toml` |
| 자동 검사 장치 | `.claude/settings.json`(Stop hook), `.githooks/pre-commit`, `.githooks/commit-msg`, `.github/workflows/verify.yml`, `.github/pull_request_template.md` |
| 첫 작업 명령 | `.claude/commands/start.md` (`/start`) |

제품 비전, 시스템 구조, 상세 설계 같은 프로젝트 고유 문서는 만들지 않는다. `/start`로 시작하는 첫 작업에서 사용자와 함께 쓴다. 자세한 구성은 [템플릿 구성 설계](docs/design/Templates.md)에 있다.

### 명령

사람이 직접 쓰는 명령은 `init` 하나다. 나머지는 hook과 CI가 부른다.

| 명령 | 하는 일 |
| --- | --- |
| `projinit init [--root <폴더>] [--repository <주소>]` | 폴더를 초기화한다. 만들 파일이 하나라도 이미 있으면 아무것도 쓰지 않는다. |
| `projinit init --refresh-common` | 공통 규칙 문서와 자동 검사 장치를 템플릿에서 다시 만든다. |
| `projinit check` | 모든 검사와 프로젝트 테스트를 한 번에 실행한다. 작업을 마치기 전에 직접 실행해도 된다. |
| `projinit commit-msg`, `commits`, `pr-order` | 커밋 메시지, PR 제목·브랜치, PR 순서를 검사한다(hook과 CI용). |

검사 항목과 설정 파일 형식은 [검증 도구](docs/VerificationTools.md)에 있다.

## 규칙 체계

규칙은 모두 `docs/`의 문서에 있고, [`CLAUDE.md`](CLAUDE.md)에서 [문서 인덱스](docs/index.md)를 거쳐 찾아간다. 주요 문서는 다음과 같다.

- [문서 작업 규칙](docs/DocumentationRule.md), [코드 작업 규칙](docs/CodeRule.md), [포인터 규약](docs/Traceability.md)
- [작업 관리 규칙](docs/TaskRule.md), [커밋 규칙](docs/CommitRule.md), [PR 규칙](docs/PullRequestRule.md)
- [검증 도구](docs/VerificationTools.md)

## ProjInit 개발하기

ProjInit도 자신이 만드는 규칙 체계를 그대로 따르며 개발한다([제품 비전](docs/ProductVision.md)).

```sh
git clone git@github.com:qazcdesnu/ProjInit.git
cd ProjInit
git config core.hooksPath .githooks
uv sync
uv run projinit check
```

공통 규칙 문서는 `src/projinit/templates/`가 원본이다. 공통 규칙을 바꿀 때는 템플릿을 고친 뒤 `uv run projinit init --refresh-common`으로 이 저장소의 문서에 반영한다. 구조와 개발 언어 규칙은 [시스템 구조](docs/Architecture.md)에 있다.
