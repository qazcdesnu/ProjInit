# 검증 도구

이 문서는 문서와 코드의 규칙 준수를 자동으로 검증하는 도구를 규정한다. 도구는 `tools/` 패키지에 있으며 [코드 작업 규칙](CodeRule.md#3-언어와-스타일)이 허용한 의존성만 사용한다. 검증하는 규칙은 [문서 작업 규칙](DocumentationRule.md), [포인터 규약](Traceability.md), [작업 관리 규칙](TaskRule.md)과 이 문서의 [자동 실행](#9-일괄-실행과-자동-실행) 규칙이다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## 1. 실행 방법

모든 명령은 저장소 루트에서 uv 환경으로 실행한다([코드 작업 규칙](CodeRule.md#3-언어와-스타일)).

```sh
uv run python -m tools.check_docs        # 문서 링크와 고아 문서 검사
uv run python -m tools.check_pointers    # 문서 ↔ 코드 포인터 검사
uv run python -m tools.check_tasks       # 작업 ID 기준 작업 관리 문서 정합성 검사
uv run python -m tools.check_hooks       # 강제 장치(Stop hook, pre-commit) 설치 검사
uv run python -m unittest discover -s tests -t .   # 도구 자체의 테스트
uv run python -m tools.run_checks        # 위 검사 전체를 한 번에 실행
```

- 문제가 없으면 종료 코드 0으로 끝나고 통과 요약을 한 줄 출력한다.
- 문제가 있으면 문제마다 `<저장소 기준 경로>:<줄>: <메시지>` 형식으로 한 줄씩 출력하고 종료 코드 1로 끝난다.
- 모든 검사기는 `--root <경로>` 옵션으로 검사할 저장소 루트를 바꿀 수 있다. 기본값은 이 저장소의 루트다.

## 2. 공통 모듈

[tools/doclib.py](../tools/doclib.py)는 검사기들이 공유하는 프로젝트 구성 상수와 마크다운 해석 기능을 제공한다.

**프로젝트 구성 상수**

| 상수 | 값 | 의미 |
| --- | --- | --- |
| [REPO_ROOT](../tools/doclib.py#REPO_ROOT) | `tools/`의 상위 디렉터리 | 기본 저장소 루트 |
| [INDEX_DOC](../tools/doclib.py#INDEX_DOC) | `docs/index.md` | 고아 문서 판정의 출발점 |
| [ENTRY_DOC](../tools/doclib.py#ENTRY_DOC) | `CLAUDE.md` | 작업자가 가장 먼저 읽는 진입 문서 |
| [DOCS_DIR](../tools/doclib.py#DOCS_DIR) | `docs` | 문서 디렉터리 |
| [CODE_ROOTS](../tools/doclib.py#CODE_ROOTS) | `src`, `tools`, `tests` | 커버리지 검사 대상 코드 디렉터리 |
| [LANGUAGE_SUFFIXES](../tools/doclib.py#LANGUAGE_SUFFIXES) | 확장자 → 언어 이름 (`.py` → `python` 등) | 코드 파일로 취급하는 확장자와 그 언어. 목록은 [포인터 규약](Traceability.md#7-언어별-심볼-규칙)의 언어 표와 같다. |
| [CODE_SUFFIXES](../tools/doclib.py#CODE_SUFFIXES) | `LANGUAGE_SUFFIXES`의 키 | 코드 포인터로 취급하는 링크 대상 확장자 |

**자료형**

- [Problem](../tools/doclib.py#Problem): 검사에서 발견된 문제 하나. 파일 경로, 줄 번호, 메시지를 가지며 [Problem.format](../tools/doclib.py#Problem.format)으로 출력 형식 문자열을 만든다.
- [Link](../tools/doclib.py#Link): 문서에서 찾은 마크다운 링크 하나. 출처 문서, 줄 번호, 표시 이름, 원본 대상 문자열을 가진다.

**함수**

- [find_doc_files](../tools/doclib.py#find_doc_files): 검사 대상 문서 목록. `ENTRY_DOC`과 `docs/` 아래의 모든 `.md` 파일이다.
- [find_code_files](../tools/doclib.py#find_code_files): `CODE_ROOTS` 아래의 모든 코드 파일 목록. 없는 디렉터리는 건너뛴다.
- [extract_links](../tools/doclib.py#extract_links): 문서 본문에서 링크를 찾는다. 이미지 링크(`![...](...)`), 펜스 코드 블록(```` ``` ````, `~~~`) 안, 인라인 코드 안의 링크는 제외한다.
- [is_external](../tools/doclib.py#is_external): `http://`, `https://`, `mailto:`로 시작하는 외부 링크인지 판정한다. 외부 링크는 검사하지 않는다.
- [resolve_link](../tools/doclib.py#resolve_link): 링크 대상을 (절대 경로, 앵커)로 나눈다. `#앵커`만 있는 링크는 출처 문서 자신을 가리킨다. 앵커는 URL 디코딩한다.
- [slugify](../tools/doclib.py#slugify): 제목 문자열을 앵커로 바꾼다. 규칙은 [문서 작업 규칙](DocumentationRule.md#3-링크-규칙)에 있다.
- [display_path](../tools/doclib.py#display_path): 출력용 경로 문자열. 저장소 루트 기준 상대 경로이며, 루트 밖이면 절대 경로다. [Problem.format](../tools/doclib.py#Problem.format)과 검사기 메시지가 함께 쓴다.
- [heading_anchors](../tools/doclib.py#heading_anchors): 문서의 모든 ATX 제목(`#` ~ `######`, 코드 블록 밖)의 앵커 집합. 같은 앵커가 반복되면 두 번째부터 `-1`, `-2`를 붙인다.
- [iter_prose_lines](../tools/doclib.py#iter_prose_lines): 펜스 코드 블록 밖의 줄을 (줄 번호, 줄)로 차례로 돌려준다. 펜스 줄 자체도 제외한다.
- [strip_inline_code](../tools/doclib.py#strip_inline_code): 줄에서 인라인 코드 구간을 지운다. 여는 백틱 수와 같은 수의 백틱으로 닫힌 구간을 지운다.

## 3. 문서 링크 검사기

[tools/check_docs.py](../tools/check_docs.py)는 [문서 작업 규칙](DocumentationRule.md)의 링크 규칙과 고아 문서 금지 규칙을 검증한다.

- [check_links](../tools/check_docs.py#check_links): 모든 문서의 링크를 검사한다.
  - 외부 링크와 코드 파일 링크는 건너뛴다. 코드 파일 링크는 [포인터 검사기](#4-포인터-검사기)가 검사한다.
  - 대상 파일이나 디렉터리가 없으면 문제다.
  - 대상이 `.md` 문서이고 앵커가 있으면, 대상 문서에 그 앵커가 있어야 한다.
- [check_entry](../tools/check_docs.py#check_entry): `ENTRY_DOC`이 존재하고 `INDEX_DOC`으로 가는 링크를 가지는지 검사한다.
- [check_entry_format](../tools/check_docs.py#check_entry_format): `ENTRY_DOC`이 [진입 문서 형식](DocumentationRule.md#7-진입-문서)을 지키는지 검사한다. 위반한 줄마다 문제를 보고한다.
  - 첫 줄이 `# ` 제목이어야 한다. 그 뒤 빈 줄 다음의 연속된 줄들이 목적 문단이다.
  - 목적 문단 뒤의 빈 줄이 아닌 줄은 `## ` 제목이거나, `- `로 시작하고 `docs/` 아래 `.md` 문서로 가는 링크를 가진 줄이어야 한다.
  - 펜스 코드 블록은 줄 위치와 상관없이 문제이며, 인라인 코드가 있는 줄도 문제다.
- [find_orphans](../tools/check_docs.py#find_orphans): `INDEX_DOC`에서 문서 간 링크를 따라 너비 우선 탐색을 하고, 도달하지 못한 `docs/` 아래 문서를 고아 문서로 보고한다. `INDEX_DOC`이 없으면 그 자체를 문제로 보고한다.
- [main](../tools/check_docs.py#main): 네 검사를 실행하고 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다.

## 4. 포인터 검사기

[tools/check_pointers.py](../tools/check_pointers.py)는 [포인터 규약](Traceability.md)을 검증한다.

**자료형**

- [CodePointer](../tools/check_pointers.py#CodePointer): 문서 → 코드 포인터. 출처 문서, 줄, 대상 심볼을 가진다.
- 심볼, 코드 → 문서 포인터, 파일 분석 결과는 [7. 코드 분석 모듈](#7-코드-분석-모듈)의 자료형을 쓴다.

**함수**

- [collect_code_pointers](../tools/check_pointers.py#collect_code_pointers): 모든 문서에서 코드 포인터를 모으고 검사한다. 대상 파일이 없거나, 앵커가 줄 번호 형식(`L` 뒤에 숫자)이거나, 구문 트리에 해당 한정 이름이 없으면 문제다. 코드 루트 밖의 코드 파일은 가리키는 문서가 있을 때 분석한다.
- [check_doc_pointers](../tools/check_pointers.py#check_doc_pointers): 코드 → 문서 포인터의 대상 문서와 앵커가 존재하는지 검사한다.
- [check_coverage](../tools/check_pointers.py#check_coverage): [커버리지 규칙](Traceability.md#4-커버리지-규칙)을 검사한다.
  - 코드가 없는 파일(`ModuleIndex.has_code`가 거짓)은 건너뛴다.
  - 파일 자체에 포인터가 없으면 1줄에 문제를 보고한다.
  - 분류가 정의이고 최상위이며 공개인 심볼마다, 같은 한정 이름의 심볼 중 하나라도 포인터를 가져야 한다. 없으면 그 심볼의 시작 줄에 문제를 보고한다.
- [check_reciprocity](../tools/check_pointers.py#check_reciprocity): [상호 참조 규칙](Traceability.md#5-상호-참조-규칙)을 두 방향 모두 검사한다.
- [main](../tools/check_pointers.py#main): `CODE_ROOTS`의 코드 파일과 문서가 가리키는 코드 파일을 모두 분석하고, 위 검사를 실행해 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다.

## 5. 테스트

각 도구의 동작은 아래 테스트가 검증한다. 테스트는 임시 디렉터리에 작은 저장소를 만들어 `--root`와 같은 방식으로 검사기를 실행한다.

- [tests/support.py](../tests/support.py): 테스트 공통 기반. [RepoTestCase](../tests/support.py#RepoTestCase)는 테스트마다 임시 저장소 루트(`self.root`)를 만들고 지우며, [RepoTestCase.write](../tests/support.py#RepoTestCase.write)로 그 아래에 파일을 만든다.
- [tests/test_doclib.py](../tests/test_doclib.py): 링크 추출(코드 블록·인라인 코드·이미지 제외), 앵커 생성(한글, 중복 제목).
- [tests/test_check_docs.py](../tests/test_check_docs.py): 깨진 링크, 없는 앵커, 고아 문서, 진입 문서 누락, 정상 저장소, 진입 문서 형식(정상, 코드 블록, 인라인 코드, 링크 없는 목록 줄, 추가 문단, 제목 누락).
- [tests/test_check_pointers.py](../tests/test_check_pointers.py): 정상 양방향 포인터, 없는 심볼, 줄 번호 포인터, 주석 포인터, 소속 없는 주석 포인터, 커버리지 누락, 역방향 포인터 누락, Python 밖의 언어로 된 저장소.
- [tests/test_code_index.py](../tests/test_code_index.py): 주석 포인터의 소속(바로 아래 정의, 파일 머리, 빈 줄로 떨어진 경우, 코드와 같은 줄), 블록 주석 안의 여러 태그, 구문 오류.
- [tests/test_check_hooks.py](../tests/test_check_hooks.py): 정상 설치, settings 파일 누락·형식 오류·명령 불일치, pre-commit 누락·실행 권한 없음·명령 불일치, `core.hooksPath` 미설정, git 저장소가 아닌 경우.
- [tests/test_run_checks.py](../tests/test_run_checks.py): 실행할 검사 목록, Stop hook 응답(통과, 첫 실패에서 막기, 이미 막힌 뒤 허용과 사용자 경고), 실패 요약의 길이 제한.
- [tests/test_languages.py](../tests/test_languages.py): 언어마다 [포인터 규약](Traceability.md#7-언어별-심볼-규칙)의 표에 있는 정의·값·이름 붙이기·공개 규칙. `LANGUAGES`와 `LANGUAGE_SUFFIXES`의 일치.
- [tests/test_check_tasks.py](../tests/test_check_tasks.py): 정상 저장소, 형식 오류, 번호 누락, 상태와 기록의 불일치, 연결 작업, 기록 필드·절 누락, 완료 순서, `없음` 규칙, 알 수 없는 ID 참조(한글 조사가 붙은 ID 포함), 경량 이슈(정상, `[~]` 상태, 기록이 있는 경우, 완료일 누락, 빈 결과, 연결 작업), 기록 보존(그대로 옮긴 경우 통과, 옮기며 줄이 빠진 경우, 진행 중 기록의 진행 기록 줄을 지운 경우, 진행 중 기록이 사라진 경우, 완료 기록의 줄이 바뀐 경우, git 저장소가 아닌 경우).

## 6. 작업 관리 검사기

[tools/check_tasks.py](../tools/check_tasks.py)는 [작업 관리 규칙](TaskRule.md)을 작업 ID 기준으로 검증한다. 해석하는 문서 형식은 [작업 관리 규칙의 문서 형식](TaskRule.md#6-문서-형식)에 있다.

**상수**

| 상수 | 값 |
| --- | --- |
| [ROADMAP_DOC](../tools/check_tasks.py#ROADMAP_DOC) | `docs/Roadmap.md` |
| [ISSUE_DOC](../tools/check_tasks.py#ISSUE_DOC) | `docs/Issue.md` |
| [ONGOING_DOC](../tools/check_tasks.py#ONGOING_DOC) | `docs/Ongoing.md` |
| [DONE_DOC](../tools/check_tasks.py#DONE_DOC) | `docs/Done.md` |

**자료형**

- [WorkItem](../tools/check_tasks.py#WorkItem): 로드맵의 태스크 또는 이슈 하나. ID, 상태 문자(` `, `~`, `x`), 출처 문서, 줄, 연결 작업 ID, 경량 결과, 완료일(셋 다 없으면 `None`)을 가진다.
- [Record](../tools/check_tasks.py#Record): 진행 중·완료 문서의 기록 하나. ID, 출처 문서, 줄, 필드 사전, 절 이름 집합, 본문 줄 목록을 가진다. 본문 줄은 제목 줄을 포함한 빈 줄이 아닌 줄을 (속한 절 이름, 줄 끝 공백을 뗀 줄)로 담으며, 절 앞의 줄은 절 이름이 빈 문자열이다.

**함수**

- [parse_roadmap](../tools/check_tasks.py#parse_roadmap): 로드맵에서 태스크를 읽는다. 형식에 맞지 않는 `- [` 줄과 `##` 제목, 마일스톤 밖이나 다른 마일스톤 아래의 태스크, 차례가 맞지 않는 마일스톤·태스크 번호를 문제로 보고한다.
- [parse_issues](../tools/check_tasks.py#parse_issues): 이슈 문서에서 이슈와 세부 필드(연결 작업, 경량, 완료일)를 읽는다. 형식 오류와 접두어별 번호 차례를 검사한다.
- [parse_records](../tools/check_tasks.py#parse_records): 진행 중 또는 완료 문서에서 기록을 읽는다. 문서 내용을 따로 넘기면 파일 대신 그 내용을 읽는다(`HEAD`의 내용을 읽을 때 쓴다). 작업 ID로 시작하지 않는 `##` 제목과 같은 문서 안의 중복 기록을 문제로 보고한다.
- [check_states](../tools/check_tasks.py#check_states): 상태와 기록의 대응을 검사한다.
  - 경량 이슈([가벼운 작업 경로](TaskRule.md#46-가벼운-작업-경로)): `[~]`가 아니어야 하고, 진행 중·완료 기록과 연결 작업이 없어야 하며, 경량 결과가 비어 있지 않아야 한다. `[x]`이면 올바른 형식의 완료일이 있어야 한다. 경량 이슈에는 아래의 일반 규칙을 적용하지 않는다.
  - 로드맵과 이슈 전체에서 ID는 하나뿐이어야 한다.
  - 연결 작업이 없는 항목: `[~]`이면 진행 중 기록만, `[x]`이면 완료 기록만 있어야 하고, `[ ]`이면 어느 기록도 없어야 한다.
  - 연결 작업이 있는 항목: 연결 작업이 존재하고 그 자신은 연결 작업이 없어야 하며, 상태가 연결 작업과 같고, 자체 기록이 없어야 한다.
  - 로드맵·이슈에 없는 ID의 기록은 문제다.
- [check_preservation](../tools/check_tasks.py#check_preservation): [기록 보존 검사](TaskRule.md#65-기록-보존-검사)를 한다. `git show HEAD:<문서>`로 마지막 커밋의 진행 중·완료 문서를 읽는다. 빠진 줄은 기록마다 하나의 문제로 보고하며, 빠진 줄 수와 첫 번째 빠진 줄을 메시지에 담는다.
- [check_records](../tools/check_tasks.py#check_records): 기록의 필수 필드·절, 날짜 형식, 완료 기록의 순서(`완료일`이 늦은 것부터), 진행 중 문서의 `없음` 규칙을 검사한다.
- [check_references](../tools/check_tasks.py#check_references): 작업 관리 문서 네 개의 본문(코드 블록·인라인 코드 제외)에 나온 작업 ID가 모두 존재하는지 검사한다. ID 앞뒤가 영문자·숫자·`-`가 아니면 ID로 인식하므로 `M0-T6으로`처럼 한글 조사가 붙어도 찾는다.
- [main](../tools/check_tasks.py#main): 네 문서를 읽어 기록 보존 검사를 포함한 위 검사를 실행하고 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다. 문서가 없으면 그 자체를 문제로 보고한다.

## 7. 코드 분석 모듈

코드 파일을 [tree-sitter](https://tree-sitter.github.io/)로 파싱해 심볼과 코드 → 문서 포인터를 찾는다. [포인터 검사기](#4-포인터-검사기)가 쓴다.

### 7.1 언어 모듈

[tools/languages.py](../tools/languages.py)는 [포인터 규약의 언어별 심볼 규칙](Traceability.md#7-언어별-심볼-규칙)을 구현한다. 언어마다 문법 패키지(`tree-sitter-python`, `tree-sitter-rust` 등)를 쓴다.

**자료형**

- [Definition](../tools/languages.py#Definition): 구문 트리에서 찾은 심볼 하나. 한정 이름, 시작 줄(데코레이터·어트리뷰트 등 포함), 분류(`definition`, `value`, `namespace` 중 하나), 최상위 여부, 공개 여부, docstring(시작 줄과 원문, 없으면 `None`)을 가진다. 최상위와 공개의 뜻은 [커버리지 규칙](Traceability.md#4-커버리지-규칙)에 있다.
- [Language](../tools/languages.py#Language): 언어 하나. 이름, 주석 노드 종류, 문법, 구문 트리에서 `Definition` 목록을 만드는 함수, 모듈 docstring을 찾는 함수(Python만, 다른 언어는 `None`)를 가진다.

**상수**

- [LANGUAGES](../tools/languages.py#LANGUAGES): 언어 이름 → `Language`. 키는 [LANGUAGE_SUFFIXES](../tools/doclib.py#LANGUAGE_SUFFIXES)의 값과 같아야 한다.

**함수**

- [parse](../tools/languages.py#parse): 소스를 그 언어로 파싱해 구문 트리를 돌려준다. 언어별 파서는 한 번만 만든다.

### 7.2 파일 분석

[tools/code_index.py](../tools/code_index.py)는 코드 파일 하나를 분석한다.

**자료형**

- [SymbolRef](../tools/code_index.py#SymbolRef): 코드 심볼 하나를 (파일 절대 경로, 한정 이름)으로 나타낸다. 모듈 자체는 한정 이름이 빈 문자열이다. [SymbolRef.is_related](../tools/code_index.py#SymbolRef.is_related)는 [상호 참조 규칙](Traceability.md#5-상호-참조-규칙)의 "관련 있다"를 판정한다.
- [DocPointer](../tools/code_index.py#DocPointer): 코드 → 문서 포인터. 출처 심볼, 줄, 대상 문서 절대 경로, 앵커를 가진다.
- [ModuleIndex](../tools/code_index.py#ModuleIndex): 코드 파일 하나의 분석 결과. 한정 이름 → `Definition` 목록 사전(`symbols`, 모듈은 빈 이름), 코드 → 문서 포인터 목록(`doc_pointers`), 분석 중 발견한 문제 목록(`problems`), 주석 말고 코드가 있는지(`has_code`)를 가진다.

**함수**

- [index_module](../tools/code_index.py#index_module): 코드 파일을 분석해 `ModuleIndex`를 만든다.
  - 언어는 확장자로 정한다.
  - 구문 트리에 오류 노드가 있으면 첫 오류 위치에 `파싱 실패` 문제를 보고하고, 심볼 없이 돌려준다.
  - 심볼: 모듈(빈 이름)과 `Language`의 함수가 찾은 `Definition`을 등록한다.
  - docstring 포인터: 모듈과 각 `Definition`의 docstring에서 `@doc:` 줄을 찾는다. 줄 번호는 docstring 시작 줄에 docstring 안의 줄 위치를 더한 값이다.
  - 주석 포인터: 구문 트리의 주석 노드에서 `@doc:`을 찾고, [포인터 규약](Traceability.md#31-주석)에 따라 소속 심볼을 정한다. 줄 번호는 태그가 있는 줄이다. 코드와 같은 줄에 있거나 소속 심볼이 없으면 문제다.

## 8. 강제 장치 검사기

[tools/check_hooks.py](../tools/check_hooks.py)는 [9. 일괄 실행과 자동 실행](#9-일괄-실행과-자동-실행)의 장치가 설치되어 있는지 검사한다. 장치가 빠지면 검사기가 자동으로 돌지 않는데, 그 사실을 아무도 모르게 되는 것을 막는다.

**상수**

| 상수 | 값 |
| --- | --- |
| [CLAUDE_SETTINGS](../tools/check_hooks.py#CLAUDE_SETTINGS) | `.claude/settings.json` |
| [STOP_HOOK_COMMAND](../tools/check_hooks.py#STOP_HOOK_COMMAND) | `cd "$CLAUDE_PROJECT_DIR" && uv run python -m tools.run_checks --hook stop` |
| [PRE_COMMIT_HOOK](../tools/check_hooks.py#PRE_COMMIT_HOOK) | `.githooks/pre-commit` |
| [PRE_COMMIT_COMMAND](../tools/check_hooks.py#PRE_COMMIT_COMMAND) | `uv run python -m tools.run_checks --hook pre-commit` |
| [HOOKS_PATH](../tools/check_hooks.py#HOOKS_PATH) | `.githooks` |

**함수**

- [check_stop_hook](../tools/check_hooks.py#check_stop_hook): `CLAUDE_SETTINGS`가 있고 JSON으로 읽히며, `hooks.Stop` 아래에 명령이 정확히 `STOP_HOOK_COMMAND`인 command hook이 있는지 검사한다.
- [check_pre_commit](../tools/check_hooks.py#check_pre_commit): `PRE_COMMIT_HOOK`이 있고, 실행 권한이 있으며, `PRE_COMMIT_COMMAND`를 담고 있는지 검사한다.
- [check_hooks_path](../tools/check_hooks.py#check_hooks_path): 루트가 git 저장소이고, git 설정 `core.hooksPath`가 `HOOKS_PATH`인지 검사한다. 이 설정은 저장소에 포함되지 않으므로 클론할 때마다 한 번 해 줘야 하며, 이 검사가 빠뜨린 것을 알려 준다.
- [main](../tools/check_hooks.py#main): 세 검사를 실행하고 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다.

## 9. 일괄 실행과 자동 실행

검사기를 작업자의 기억에 맡기지 않고 자동으로 실행한다([제품 비전](ProductVision.md#4-구성-초안)). 장치는 두 가지이며 서로 다른 구멍을 막는다.

| 장치 | 실행 시점 | 실패하면 |
| --- | --- | --- |
| Claude Code Stop hook | Claude가 턴을 끝내려 할 때 | 첫 시도에서는 턴 종료를 막고 실패 요약을 Claude에게 돌려준다. 이미 한 번 막힌 뒤의 종료(`stop_hook_active`)는 허용하고, 남은 실패를 사용자에게 경고로 보여 준다. |
| git pre-commit | 사람이든 Claude든 커밋하려 할 때 | 커밋을 거부한다. |

Stop hook이 두 번째 종료를 허용하는 이유는 [코드 작업 규칙](CodeRule.md#1-문서-우선-작업-절차)이 진행 중인 작업에서 포인터 검사기가 일부러 실패하는 상태를 허용하기 때문이다. 이때 Claude는 실패를 고치거나, 남긴 이유를 사용자에게 보고해야 한다. 끝없이 막으면 작업 중에 사용자에게 질문할 수도 없게 된다.

**설치**

- `.claude/settings.json`에 `hooks.Stop` command hook으로 [STOP_HOOK_COMMAND](../tools/check_hooks.py#STOP_HOOK_COMMAND)를 둔다.
- `.githooks/pre-commit`에 [PRE_COMMIT_COMMAND](../tools/check_hooks.py#PRE_COMMIT_COMMAND)를 실행하는 셸 스크립트를 두고 실행 권한을 준다.
- 클론한 뒤 한 번 `git config core.hooksPath .githooks`를 실행한다. 빠뜨리면 [강제 장치 검사기](#8-강제-장치-검사기)가 Stop hook에서 알려 준다.
- pre-commit은 스테이징한 내용이 아니라 작업 트리를 검사한다.

[tools/run_checks.py](../tools/run_checks.py)는 모든 검사를 한 번에 실행하고, hook으로 불렸을 때의 응답을 만든다.

**상수와 자료형**

- [CHECKS](../tools/run_checks.py#CHECKS): 실행할 검사의 (이름, 명령 인자) 목록. `check_docs`, `check_pointers`, `check_tasks`, `check_hooks`, `unittest` 순서다. 검사기는 `--root`로 루트를 넘기고, 테스트는 루트에서 `unittest discover -s tests -t .`로 실행한다.
- [CheckResult](../tools/run_checks.py#CheckResult): 검사 하나의 결과. 이름, 종료 코드, 출력(표준 출력과 표준 오류를 합친 것)을 가진다.
- [HookResponse](../tools/run_checks.py#HookResponse): hook에 돌려줄 응답. 종료 코드, 표준 출력, 표준 오류를 가진다.

**함수**

- [run_all](../tools/run_checks.py#run_all): `CHECKS`를 차례로 현재 Python 인터프리터의 하위 프로세스로 실행해 `CheckResult` 목록을 돌려준다. 하나가 실패해도 나머지를 실행한다.
- [summarize](../tools/run_checks.py#summarize): 실패한 검사마다 이름과 출력의 마지막 40줄을 모은 요약 문자열을 만든다.
- [stop_hook_response](../tools/run_checks.py#stop_hook_response): Stop hook 응답을 만든다.
  - 모두 통과: 종료 코드 0, 출력 없음.
  - 실패, `stop_hook_active`가 거짓: 종료 코드 2, 표준 오류에 요약과 "고치거나, 진행 중인 작업이라 남기는 실패면 그 이유를 사용자에게 보고하라"는 안내.
  - 실패, `stop_hook_active`가 참: 종료 코드 0, 표준 출력에 `systemMessage`로 실패한 검사 이름을 담은 JSON.
- [main](../tools/run_checks.py#main): `--root`와 `--hook`(`stop` 또는 `pre-commit`) 옵션을 받는다.
  - `--hook`이 없거나 `pre-commit`: 각 검사의 결과를 한 줄씩 출력하고, 실패가 있으면 요약을 출력한 뒤 종료 코드 1로 끝난다.
  - `--hook stop`: 표준 입력의 JSON에서 `stop_hook_active`를 읽고 `stop_hook_response`의 응답대로 출력하고 끝난다. 입력이 비었거나 JSON이 아니면 `stop_hook_active`를 거짓으로 본다.

