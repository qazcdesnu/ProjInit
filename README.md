# ProjInit

ProjInit은 **Claude Code 프로젝트 초기화 CLI**다. 빈 폴더에 문서와 코드 두 축의 규칙 체계를 깔아 주고, 그 폴더에서 Claude Code를 열어 `/start`를 입력하면 Claude가 만들 프로젝트를 물어보며 첫 작업을 시작한다. 어떤 프로젝트에서든 같은 방식으로 일하는 것이 목적이다.

> 상태: 최신 릴리스는 `v0.2.0`이다. 진행 상황은 [로드맵](docs/Roadmap.md)에 있다.

## 무엇을 해 주나

초기화한 프로젝트에서는 다음이 처음부터 갖춰져 있다.

- **문서 우선**: 문서를 먼저 쓰고 그 지시에 따라 코드를 쓴다. 진입 문서 `CLAUDE.md`에서 모든 규칙 문서로 이어진다.
- **문서 ↔ 코드 포인터**: 문서는 코드의 심볼을, 코드는 근거 문서를 가리킨다. 개발 언어와 무관하다(Python, JavaScript, TypeScript, Rust, C, C++, Go, Java).
- **작업 ID와 기록**: 모든 작업이 로드맵·이슈의 ID로 시작하고 끝나며, 진행 중·완료 기록이 남는다.
- **커밋과 PR 규칙**: 커밋 제목은 작업 ID로 시작하고, 작업마다 브랜치를 만들어 PR로 합친다.
- **자료 폴더**: 개발 중 참고하는 자료는 `reference/`에, ProjInit 없이 작업하던 기존 프로젝트는 `legacy/`에, 저장소에 올리면 안 되는 자료는 `private/`에 둔다. 세션을 시작할 때마다 참고 자료를 Claude에게 알려 주고, 기존 프로젝트는 넣은 뒤 고치지 못하게, 로컬 자료는 커밋되지 않게 검사한다.
- **자동 검사**: Claude가 턴을 끝낼 때(Stop hook), 커밋할 때(pre-commit, commit-msg), PR을 열 때(GitHub Actions) 규칙을 검사한다. 사람이 검사를 기억할 필요가 없다.

## 필요한 것

- [uv](https://docs.astral.sh/uv/) — ProjInit과 검사기를 실행한다.
- git
- [Claude Code](https://code.claude.com/)
- GitHub CLI `gh` — PR을 만들 때 (선택)

## 사용법

### 새 프로젝트 시작하기

```sh
uvx --from git+https://github.com/qazcdesnu/ProjInit@v0.2.0 projinit init --root ~/my-project
cd ~/my-project
claude
```

처음 실행할 때는 ProjInit과 언어별 문법 패키지를 받느라 시간이 걸린다. 그다음부터는 캐시를 쓴다.

Claude Code가 열리면 `/start`를 입력한다. Claude가 어떤 걸 만들고 싶은지 묻는다. 한두 문장이나 떠오르는 생각만 말해도 되고, 모르는 것은 정하지 않아도 된다. 대화하며 제품 비전·시스템 구조 문서와 첫 로드맵을 쓴 뒤 첫 커밋을 한다.

원격 저장소가 이미 있으면 `--repository <주소>`로 알려 준다. 없으면 나중에 `projinit.toml`의 `template.repository`를 고치고 `projinit init --refresh-common`을 실행한다.

### 참고 자료와 함께 시작하기

개발에 앞서 모은 자료(조사 메모, 명세, 논문, 외부 API 문서, 디자인 시안, 샘플 데이터 등)가 있으면 프로젝트 폴더의 `reference/`에 넣고 시작한다. 파일을 넣기만 하면 되고, 목록 정리는 Claude가 한다.

```sh
mkdir -p ~/my-project/reference
cp ~/Downloads/payment-api.pdf ~/notes/research.md ~/my-project/reference/
uvx --from git+https://github.com/qazcdesnu/ProjInit@v0.2.0 projinit init --root ~/my-project
cd ~/my-project
claude
```

`/start`를 입력하면 Claude가 자료를 먼저 읽고 무엇을 알게 됐는지 알려 준 뒤, 그 내용에서 출발해 제품 비전과 첫 로드맵을 함께 쓴다. 자료마다 무엇이고 어디에 쓰는지는 참고 자료 목록(`docs/Reference.md`)에 정리한다. 자료에서 정한 내용은 프로젝트 문서에 옮겨 적고 근거로 자료를 링크한다.

Claude Code 세션이 시작될 때마다 hook이 `reference/`에 어떤 자료가 있는지(목록 항목과 아직 목록에 없는 자료) Claude에게 알려 준다. 그래서 Claude가 자료를 잊지 않고, 작업을 시작할 때 관련 자료를 찾아 읽은 뒤 무엇을 참고했는지 작업 기록에 남긴다.

- Claude가 바로 읽는 형식은 텍스트·마크다운·CSV·JSON, PDF, 이미지다. 워드·엑셀·파워포인트·한글 파일은 PDF나 마크다운, CSV로 바꿔 넣는다.
- 웹 페이지는 PDF나 마크다운으로 저장해 넣는다. 자주 바뀌는 페이지는 주소만 알려 주면 목록에 출처로 적는다.
- 자료가 많으면 주제별 하위 폴더로 나눈다. 무엇에 쓸 자료인지 한 줄씩 알려 주면 Claude가 더 잘 고른다.
- 자료는 저장소에 커밋된다. 비밀 정보는 넣지 말고, 공개 저장소라면 공개해도 되는 자료만 넣는다.

개발 중에도 언제든 자료를 더한다. 목록에 올리지 않아도 되므로 넣고 바로 커밋할 수 있다. 커밋 메시지에는 작업 ID가 필요하니 Claude에게 "reference에 결제 API 명세 넣었어. 결제 기능 설계에 써 줘"처럼 맡기는 것이 가장 쉽다. 어디에 쓸지 알려 주면 목록에 올리고, 알려 주지 않아도 다음 세션부터 Claude가 그 자료가 있다는 것을 안다.

### 로컬에서만 볼 자료

계약서, 내부 문서, 고객 데이터 샘플처럼 저장소에 올리면 안 되지만 작업할 때는 봐야 하는 자료는 `private/`에 넣는다. 초기화와 갱신이 `.gitignore`에 `/private/`를 미리 넣어 두므로, 폴더를 만들어 넣기만 하면 된다.

```sh
mkdir -p ~/my-project/private
cp ~/Documents/contract.pdf ~/my-project/private/
```

- `private/`는 커밋되지 않는다. `.gitignore`의 그 줄을 지웠거나 파일을 강제로 git에 올리면 커밋할 때 검사기가 막는다.
- 문서는 `private/` 안을 링크하지 않는다(선택 링크도 안 된다). 다른 컴퓨터와 CI에는 그 파일이 없고, 링크에 파일 이름이 남기 때문이다. 근거를 적어야 하면 경로만 글자로 적는다.
- 목록 문서도 두지 않는다. 대신 세션을 시작할 때 hook이 로컬 자료의 경로를 Claude에게 알려 준다. Claude는 자료에서 정한 것 중 공개해도 되는 결정만 문서에 옮긴다.
- 저장소에 올라가지 않을 뿐, Claude가 읽으면 그 내용은 모델로 전송된다. API 키, 비밀번호, 인증서처럼 Claude도 보면 안 되는 비밀은 넣지 않는다.
- 다른 컴퓨터에서 클론하면 `private/`는 비어 있다. 필요하면 따로 옮겨 둔다.

### 기존 프로젝트로 시작하기

ProjInit 없이 작업하던 프로젝트가 있으면, 새 폴더의 `legacy/<이름>/`에 복사한 뒤 초기화한다. 기존 프로젝트의 `.git`과 의존성·빌드 산출물(`node_modules/`, `.venv/` 등)은 빼고 넣는다.

```sh
mkdir -p ~/my-project/legacy
rsync -a --exclude .git --exclude node_modules ~/old-project/ ~/my-project/legacy/old-project/
uvx --from git+https://github.com/qazcdesnu/ProjInit@v0.2.0 projinit init --root ~/my-project
```

`/start`를 입력하면 Claude가 기존 프로젝트를 먼저 읽고, 이해한 내용에서 출발해 제품 비전과 첫 로드맵을 함께 쓴다. 기존 프로젝트는 그 뒤로 아카이브가 되어 고치지 않는다. 참고 자료와 함께 넣어도 되며, 그러면 둘 다 먼저 읽는다. 규칙은 [자료 폴더 규칙](docs/MaterialRule.md)에 있다.

### 이미 초기화한 프로젝트를 새 버전으로

그 프로젝트 폴더에서 새 버전으로 갱신 명령을 실행한다.

```sh
uvx --from git+https://github.com/qazcdesnu/ProjInit@v<새 버전> projinit upgrade
```

설정의 버전을 바꾸고 공통 규칙 문서와 자동 검사 장치를 새 버전으로 다시 만든다. 커밋하지 않은 변경이 있으면 진행 중인 작업과 섞이지 않도록 거부한다. 검사 때문에 그 변경을 커밋할 수 없으면 `git stash -u`로 치워 두고 갱신한 뒤, 갱신을 커밋하고 `git stash pop`으로 되돌린다. 이 명령은 커밋하지 않으므로, 끝나면 Claude Code에서 "ProjInit 업데이트를 작업으로 등록해 커밋해 줘"라고 맡긴다. Claude가 바뀐 규칙을 알려 주고 커밋한다. Claude에게 갱신 자체를 맡겨도 된다.

### 초기화가 만드는 것

| 구분 | 파일 |
| --- | --- |
| 진입 문서 | `CLAUDE.md` |
| 공통 규칙 문서 | `docs/`의 문서 작업·코드 작업·포인터·작업 관리·커밋·PR·자료 폴더 규칙, 검증 도구 |
| 작업 관리 문서 | `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md` |
| 설정 | `projinit.toml` |
| 자동 검사 장치 | `.claude/settings.json`(Stop hook, 세션 시작 안내 hook), `.githooks/pre-commit`, `.githooks/commit-msg`, `.github/workflows/verify.yml`, `.github/pull_request_template.md` |
| 첫 작업 명령 | `.claude/commands/start.md` (`/start`) |

제품 비전, 시스템 구조, 상세 설계 같은 프로젝트 고유 문서는 만들지 않는다. `/start`로 시작하는 첫 작업에서 사용자와 함께 쓴다. 자세한 구성은 [템플릿 구성 설계](docs/design/Templates.md)에 있다.

### 명령

사람이 직접 쓰는 명령은 `init`과 `upgrade`다. 나머지는 hook과 CI가 부른다.

| 명령 | 하는 일 |
| --- | --- |
| `projinit init [--root <폴더>] [--repository <주소>] [--agent claude\|codex]…` | 폴더를 초기화한다. `--agent`로 쓸 코딩 에이전트를 고른다(기본 `claude`). 만들 파일이 하나라도 이미 있으면 아무것도 쓰지 않는다. |
| `projinit upgrade` | 이미 초기화한 프로젝트를 실행한 ProjInit 버전으로 갱신한다. |
| `projinit init --refresh-common` | 공통 규칙 문서와 자동 검사 장치를 지금 설정 값으로 다시 만든다. |
| `projinit check` | 모든 검사와 프로젝트 테스트를 한 번에 실행한다. 작업을 마치기 전에 직접 실행해도 된다. |
| `projinit context` | 세션 시작 안내(참고 자료 목록)를 출력한다(SessionStart hook용). |
| `projinit commit-msg`, `commits`, `pr-order` | 커밋 메시지, PR 제목·브랜치, PR 순서를 검사한다(hook과 CI용). |

검사 항목과 설정 파일 형식은 [검증 도구](docs/VerificationTools.md)에 있다.

## 규칙 체계

규칙은 모두 `docs/`의 문서에 있고, [`CLAUDE.md`](CLAUDE.md)에서 [문서 인덱스](docs/index.md)를 거쳐 찾아간다. 주요 문서는 다음과 같다.

- [문서 작업 규칙](docs/DocumentationRule.md), [코드 작업 규칙](docs/CodeRule.md), [포인터 규약](docs/Traceability.md)
- [작업 관리 규칙](docs/TaskRule.md), [커밋 규칙](docs/CommitRule.md), [PR 규칙](docs/PullRequestRule.md)
- [자료 폴더 규칙](docs/MaterialRule.md)
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

테스트는 단위 테스트(`tests/unit/`)와, 실제 프로젝트를 만들어 규칙을 하나씩 일부러 깨뜨려 보는 시나리오 테스트(`tests/scenario/`) 두 종류다. `projinit check`가 둘 다 실행한다.

공통 규칙 문서는 `src/projinit/templates/`가 원본이다. 공통 규칙을 바꿀 때는 템플릿을 고친 뒤 `uv run projinit init --refresh-common`으로 이 저장소의 문서에 반영한다. 구조와 개발 언어 규칙은 [시스템 구조](docs/Architecture.md)에 있다.
