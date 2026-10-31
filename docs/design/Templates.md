# 템플릿 구성 상세 설계

이 문서는 `projinit init`이 새 프로젝트에 무엇을 만드는지, 그 원본(템플릿)을 어디에 어떻게 두는지, 공통 규칙과 프로젝트 고유 문서의 경계, 문서와 검사기 버전을 어떻게 묶는지(I10) 정한다. 근거는 [제품 비전](../ProductVision.md#3-핵심-요구사항)의 초기화·분리·자기 적용 요구사항과 [구성 초안](../ProductVision.md#4-구성-초안)이다. 구현은 [로드맵](../Roadmap.md)의 M2 태스크가 맡는다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 초기화가 만드는 것

빈 폴더(또는 아래 파일이 하나도 없는 기존 폴더)에서 `projinit init`을 실행하면 다음을 만든다.

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 진입 문서 | `CLAUDE.md` | 공통. 문서를 읽는 순서만 정한다. |
| 공통 규칙 문서 | `docs/DocumentationRule.md`, `docs/CodeRule.md`, `docs/Traceability.md`, `docs/TaskRule.md`, `docs/CommitRule.md`, `docs/PullRequestRule.md`, `docs/VerificationTools.md` | 공통. 템플릿 그대로(빈 자리만 채움). |
| 인덱스 | `docs/index.md` | 공통 문서 목록과, 프로젝트 고유 문서가 들어갈 자리 |
| 작업 관리 문서 | `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md` | 처음에만 만든다. 로드맵에는 첫 세션이 할 태스크 하나(`M0-T1 제품 비전과 첫 로드맵 작성`)만 있다. |
| 설정 | `projinit.toml` | ProjInit 버전과 출처, 빈 프로젝트 명령, 템플릿 값 |
| 강제 장치 | `.claude/settings.json`, `.githooks/pre-commit`, `.githooks/commit-msg`, `.github/workflows/verify.yml`, `.github/pull_request_template.md` | 공통. 설정에서 만든 명령을 빈 자리에 넣는다. 버전이 바뀌면 명령도 바뀌므로 공통 문서와 함께 다시 만든다. |
| 첫 세션 안내 | `.claude/commands/start.md` | 공통. `/start` 명령으로, 작업 관리 규칙의 [첫 작업](../TaskRule.md#48-첫-작업) 절차를 따르라고만 적는다. 절차 자체는 규칙 문서에 둔다. |

- 프로젝트 고유 문서(제품 비전, 시스템 구조, 상세 설계)는 만들지 않는다. 인덱스에 자리만 두고, 첫 세션이 사용자와 대화해 만든다(M2-T4).
- 폴더가 git 저장소가 아니면 `git init`을 하고, `core.hooksPath`를 `.githooks`로 설정한다. 커밋은 하지 않는다. 첫 커밋은 첫 세션이 커밋 규칙대로 한다.
- 만들 파일이 하나라도 이미 있으면 아무것도 쓰지 않고 그 파일 목록을 알려 주며 실패한다. 기존 파일을 덮어쓰지 않기 위해서다.
- 커밋 이력의 기준 커밋(`check.commit_baseline`)은 비워 둔다. 초기화한 저장소의 커밋은 처음부터 커밋 규칙을 따르기 때문이다. 기존 이력이 있는 저장소라면 사용자가 기준 커밋을 정해 적는다.

## 2. 공통과 고유의 경계

공통 규칙 문서에는 어느 프로젝트에서나 같은 내용만 둔다. 지금 이 저장소의 공통 문서에는 ProjInit에만 맞는 내용이 섞여 있어 템플릿으로 옮길 때 나눈다.

| 문서 | 섞여 있는 고유 내용 | 처리 |
| --- | --- | --- |
| 코드 작업 규칙 | 디렉터리 표(`src/projinit/`, `projinit.toml` 등), 언어와 스타일(Python, uv, PEP 8, 의존성 제한) | 공통 부분(문서 우선 절차, 추적성, 테스트·검증·변경 원칙)만 남긴다. 디렉터리 구조와 언어·스타일은 프로젝트 고유 문서 **시스템 구조**(`docs/Architecture.md`)로 옮긴다. |
| 포인터 규약 | 제품 비전으로 가는 링크 | 링크를 지우고 문장만 남긴다. |
| PR 규칙 | 원격 저장소 주소 | 템플릿 빈 자리 `{{repository}}`로 바꾼다. |
| 문서 작업 규칙, 작업 관리 규칙 | `uv run python -m projinit.check_*` 명령 | 검증 도구의 `<projinit> check`를 가리키는 문장으로 바꾼다. |
| 작업 관리 규칙 | 기록 예시의 경로(`design/Templates.md`, `src/projinit/init.py`) | 코드 블록 안의 예시라 검사에는 걸리지 않지만, 어느 프로젝트에도 맞는 일반적인 예로 바꾼다. |

규칙: **공통 문서는 공통 문서와 인덱스로만 링크한다.** 제품 비전, 시스템 구조, 상세 설계, 코드로 가는 링크는 공통 문서에 두지 않는다. 그런 링크가 있으면 다른 프로젝트에서 대상이 없어 깨진다. 이 규칙은 템플릿 테스트(아래 4절)가 검사한다.

ProjInit 자신도 같은 경계를 따른다. 이 저장소의 `docs/Architecture.md`에 `src/projinit/` 구조와 Python·uv 규칙을 둔다.

## 3. 템플릿 원본

[자기 적용 원칙](../ProductVision.md#3-핵심-요구사항)대로 원본은 하나다.

- 원본은 패키지 안의 `src/projinit/templates/`다. 패키지와 함께 배포되므로 `uvx`로 받은 어느 버전에서든 그 버전의 템플릿을 쓴다.
- 이 저장소의 공통 문서(`CLAUDE.md`, 위 1절의 공통 규칙 문서)는 템플릿을 이 저장소의 값으로 채운 결과와 **같아야 한다**. 다르면 검사기가 잡는다(5절). 그래서 공통 규칙을 고칠 때는 템플릿을 고치고 다시 만든다.
- 다시 만드는 명령은 `projinit init --refresh-common`이다. 공통 문서만 템플릿에서 다시 쓰고 다른 파일은 건드리지 않는다. 이전에 미룬 갱신 기능(`upgrade`) 전체가 아니라, 공통 문서를 다시 쓰는 일만 한다.

**빈 자리**: 템플릿 안의 `{{이름}}`을 `projinit.toml`의 `[template]` 표의 값으로 바꾼다. 이름은 영문 소문자·숫자·`_`만 쓴다. 그래서 문서에서 빈 자리를 설명할 때 `{{이름}}`처럼 한글로 쓰면 빈 자리로 보지 않는다. 지금 필요한 것은 `repository`(원격 저장소 주소) 하나다. 값이 없는 빈 자리가 남으면 초기화가 실패한다.

## 4. 템플릿 테스트

템플릿 자체를 테스트로 검사한다.

- 템플릿을 임시 폴더에 초기화한 결과가 검증 전체(`projinit check`)를 통과한다. 즉 빈 프로젝트가 처음부터 규칙을 지키는 상태다.
- 공통 문서의 링크가 공통 문서와 인덱스로만 간다.
- 모든 빈 자리가 채워진다.

## 5. 버전 묶기 (I10)

문서와 검사기는 한 쌍이므로 `projinit.toml`의 `version` 하나로 묶는다.

- 초기화는 실행 중인 ProjInit의 버전을 `version`에 적고, 그 버전의 템플릿으로 공통 문서를 만들며, 그 버전의 검사기를 부르는 hook 명령을 건다.
- 새 검사 **템플릿 일치 검사**: 공통 문서가 실행 중인 검사기의 템플릿을 설정의 값으로 채운 결과와 같은지 본다. 다르면 문서마다 문제를 보고한다. 누가 공통 문서를 손으로 고쳤거나, 설정의 버전만 올린 경우에 걸린다.
- 새 검사 **버전 일치 검사**: 실행 중인 검사기의 버전이 설정의 `version`과 같은지 본다. `projinit.command`가 지정된 저장소(ProjInit 자신처럼 작업 트리의 검사기를 쓰는 곳)는 버전을 고정하지 않으므로 건너뛴다.
- 두 검사는 `projinit check`에 들어간다. 구현은 [검사기 설계의 템플릿 일치 검사기](Checkers.md#14-템플릿-일치-검사기)에 있다.

**릴리스**: ProjInit의 버전은 `pyproject.toml`의 `version`이다. 릴리스는 `main`에 병합된 뒤 그 커밋에 `v<버전>` 태그를 붙여 원격에 올린다. 다른 프로젝트는 그 태그로 설치한다(`uvx --from <source>@v<버전> projinit`). 첫 릴리스는 `v0.1.0`이다.

버전을 올리는 작업에서는 [README](../../README.md)의 상태 줄과 설치 예시의 버전도 새 버전으로 고친다. README에 적힌 `v<버전>`이 모두 `pyproject.toml`의 버전과 같은지 [tests/test_release.py](../../tests/test_release.py)가 확인하므로, 빠뜨리면 검증에서 걸린다.

## 6. 작업 나누기

| 순서 | 태스크 | 범위 |
| --- | --- | --- |
| 1 | M2-T5 | 템플릿 원본 만들기. 공통 문서를 2절대로 나눠 `src/projinit/templates/`로 옮기고, 이 저장소에 시스템 구조 문서를 만든다. 템플릿 테스트(4절). |
| 2 | M2-T2 | `projinit init`과 `--refresh-common`. 이 저장소의 공통 문서를 템플릿에서 다시 만든다. |
| 3 | M2-T3 | 초기화할 때 강제 장치(hook, CI, PR 템플릿)와 `core.hooksPath` 설치. |
| 4 | M2-T6 | 템플릿 일치 검사와 버전 일치 검사(5절, I10). |
| 5 | M2-T4 | 첫 세션 안내. |
| 6 | M2-T7 | `v0.1.0` 릴리스와, 빈 폴더에서 초기화부터 첫 세션까지 처음부터 끝까지 시험. |

## 7. 미결정 사항

- **원격 저장소 공개 여부**: `source = "git+https://github.com/qazcdesnu/ProjInit"`로 설치하려면 저장소가 공개여야 한다. 비공개로 두면 다른 컴퓨터에서는 그 컴퓨터의 GitHub 인증(SSH 키 등)이 있어야 설치된다. M2-T7 전에 정한다.

## 8. 구현

[src/projinit/template.py](../../src/projinit/template.py)가 템플릿을 읽고 빈 자리를 채운다. 템플릿 파일은 `src/projinit/templates/` 아래에 초기화한 프로젝트와 같은 상대 경로로 둔다.

- [TEMPLATE_DIR](../../src/projinit/template.py#TEMPLATE_DIR): 템플릿 디렉터리.
- [COMMON_FILES](../../src/projinit/template.py#COMMON_FILES): 공통 파일의 상대 경로. `CLAUDE.md`, 1절의 공통 규칙 문서 일곱 개, 강제 장치 파일 다섯 개, 첫 세션 안내 명령 파일이다. 이 저장소의 같은 파일은 템플릿을 채운 결과와 같아야 한다.
- [INITIAL_FILES](../../src/projinit/template.py#INITIAL_FILES): 처음에만 만드는 파일의 상대 경로. 인덱스, 작업 관리 문서 네 개, 설정 파일이다.
- [TemplateError](../../src/projinit/template.py#TemplateError): 값이 없는 빈 자리가 있을 때의 오류.
- [EXECUTABLE_FILES](../../src/projinit/template.py#EXECUTABLE_FILES): 실행 권한을 줄 파일. `.githooks/pre-commit`, `.githooks/commit-msg`.
- [render_values](../../src/projinit/template.py#render_values): `Config`를 받아 빈 자리 값 사전을 만든다. 설정의 `[template]` 값에, 설정에서 만든 실행 명령 `projinit`([강제 장치 검사기의 `projinit_command`](Checkers.md#8-강제-장치-검사기))을 더한다. 실행 명령을 만들 수 없으면 넣지 않는다. 강제 장치 템플릿은 이 실행 명령 하나만 빈 자리로 두고 나머지 명령 부분(`check --hook stop` 등)은 직접 적는다. hook 명령 전체를 빈 자리로 두면 그 안의 큰따옴표가 JSON 설정 파일을 깨기 때문이다. 채운 결과가 강제 장치 검사기가 기대하는 명령과 같은지는 테스트가 확인한다.
- [render](../../src/projinit/template.py#render): 템플릿 파일 하나의 상대 경로와 값 사전을 받아, 모든 `{{이름}}`을 값으로 바꾼 내용을 돌려준다. 값이 없는 빈 자리가 있으면 그 이름들을 담아 `TemplateError`를 낸다.

테스트는 [tests/test_template.py](../../tests/test_template.py)다.

- 모든 템플릿 파일이 값과 함께 채워지고, 값이 빠지면 오류가 난다.
- 채운 공통 문서의 링크가 공통 파일과 처음 만드는 파일로만 간다(2절).
- 공통 파일과 처음 만드는 파일을 임시 폴더에 채워 쓰면 문서 링크 검사와 작업 관리 검사를 통과한다. 강제 장치까지 포함한 검증 전체 통과는 [초기화 명령](#9-초기화-명령)의 테스트가 시험한다.

## 9. 초기화 명령

[src/projinit/init.py](../../src/projinit/init.py)가 `projinit init`을 구현한다.

```sh
projinit init [--root <폴더>] [--repository <원격 저장소 주소>]
projinit init --refresh-common [--root <폴더>]
```

- 설정 파일도 템플릿(`src/projinit/templates/projinit.toml`)이며 처음 만드는 파일에 들어간다. 빈 자리는 `version`(실행 중인 ProjInit 버전), `source`(설치 출처), `repository`(원격 저장소 주소)다. 설정 파일을 먼저 채운 뒤, 그 설정으로 `render_values`를 만들어 나머지 파일을 채운다.
- [DEFAULT_SOURCE](../../src/projinit/init.py#DEFAULT_SOURCE): 설치 출처의 기본값 `git+https://github.com/qazcdesnu/ProjInit`.
- [NO_REPOSITORY](../../src/projinit/init.py#NO_REPOSITORY): 원격 저장소가 아직 없을 때 쓰는 값 `아직 없음`. 원격 저장소를 만들면 설정의 `template.repository`를 고치고 `--refresh-common`으로 공통 문서를 다시 만든다.
- [package_version](../../src/projinit/init.py#package_version): 실행 중인 `projinit` 패키지의 버전.
- [repository_url](../../src/projinit/init.py#repository_url): 원격 저장소 주소를 정한다. 인자로 받은 값, git `origin` 주소, `NO_REPOSITORY` 순서다.
- [init_project](../../src/projinit/init.py#init_project): 폴더와 원격 주소를 받아 공통 파일, 처음 만드는 파일(설정 파일 포함)을 채워 쓰고, 만든 파일의 상대 경로 목록을 돌려준다. 하나라도 이미 있으면 아무것도 쓰지 않고 그 목록을 담아 `InitError`를 낸다. 폴더가 git 저장소가 아니면 `git init`을 하고, `core.hooksPath`를 `.githooks`로 설정한다. `EXECUTABLE_FILES`에는 실행 권한을 준다. 폴더가 없으면 만든다.
- [refresh_common](../../src/projinit/init.py#refresh_common): `Project`를 받아 공통 파일을 `render_values`의 값으로 다시 채워 쓰고(실행 권한 포함), 내용이 바뀐 파일의 상대 경로 목록을 돌려준다. 다른 파일은 건드리지 않는다.
- [InitError](../../src/projinit/init.py#InitError): 초기화할 수 없을 때의 오류.
- [START_HINT](../../src/projinit/init.py#START_HINT): 초기화를 마친 뒤 출력하는 사용법. Claude Code를 열고 `/start`를 입력하라는 안내다.
- [main](../../src/projinit/init.py#main): 위 두 동작을 실행하고, 만들거나 바꾼 파일을 한 줄씩 출력한다. 초기화한 경우 마지막에 `START_HINT`를 출력한다. 오류는 `init: <메시지>`로 출력하고 종료 코드 1로 끝난다.
- `projinit` 명령의 하위 명령 `init`이 이 `main`을 부른다.

테스트는 [tests/test_init.py](../../tests/test_init.py)다. 빈 폴더 초기화 결과의 파일 목록과 검증 전체(`check`의 모든 검사기) 통과, hook 실행 권한과 `core.hooksPath`, git 저장소 생성, 원격 주소 결정 순서, 이미 있는 파일 때문에 실패하면 아무것도 쓰지 않음, `--refresh-common`이 고친 공통 문서를 되돌리고 다른 파일은 그대로 둠을 검사한다.

## 10. 갱신 명령

[src/projinit/upgrade.py](../../src/projinit/upgrade.py)가 `projinit upgrade`를 구현한다. 이미 초기화한 프로젝트를 실행 중인 ProjInit 버전으로 옮긴다. 새 버전의 패키지로 실행하므로(`uvx --from <source>@v<새 버전> projinit upgrade`), 이 명령이 들어간 버전부터 그 이전 버전으로 초기화한 모든 프로젝트를 올릴 수 있다.

```sh
projinit upgrade [--root <폴더>]
```

- [UpgradeError](../../src/projinit/upgrade.py#UpgradeError): 갱신할 수 없을 때의 오류.
- [set_version](../../src/projinit/upgrade.py#set_version): 설정 파일 내용과 버전을 받아 `[projinit]` 표의 `version` 값을 바꾼 내용을 돌려준다. 다른 줄과 주석은 그대로 둔다. `version` 줄이 없으면 `[projinit]` 제목 바로 아래에 넣는다.
- [upgrade_project](../../src/projinit/upgrade.py#upgrade_project): 폴더를 받아 다음을 하고, (이전 버전, 새 버전, 다시 쓴 공통 파일 목록)을 돌려준다.
  1. 설정에 실행 명령(`projinit.command`)이 있으면 `UpgradeError`다. 그런 프로젝트는 버전을 고정하지 않으므로 `init --refresh-common`을 쓴다.
  2. git 작업 트리에 커밋하지 않은 변경이 있으면 `UpgradeError`다. 갱신이 진행 중인 작업과 섞이지 않게 하기 위해서다.
  3. 설정의 `version`을 실행 중인 버전으로 바꾸고, [refresh_common](../../src/projinit/init.py#refresh_common)으로 공통 파일을 다시 만든다.
- [NEXT_STEP](../../src/projinit/upgrade.py#NEXT_STEP): 갱신을 마친 뒤 출력하는 다음 할 일. 바뀐 파일을 Claude Code에서 작업으로 등록해 커밋하게 하라는 안내다.
- [main](../../src/projinit/upgrade.py#main): 갱신하고 바뀐 파일과 `NEXT_STEP`을 출력한다. 오류는 `upgrade: <메시지>`로 출력하고 종료 코드 1로 끝난다. `projinit` 명령의 하위 명령 `upgrade`가 이 `main`을 부른다.

테스트는 [tests/test_upgrade.py](../../tests/test_upgrade.py)다. 이전 버전 프로젝트의 갱신(버전, 공통 파일, 설정의 다른 줄 유지), 커밋하지 않은 변경이 있을 때와 실행 명령이 있을 때의 거부, `version` 줄이 없는 설정을 검사한다.

