# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M0-T2 미결정 사항 결정 (대상 언어, 강제 방식, 배포 방식)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#6-미결정-사항)

### 계획
- 미결정 사항 세 가지(대상 언어, 강제 방식, 배포 방식)를 사용자와 정한다.
- 결정마다 [제품 비전](ProductVision.md)의 미결정 사항에서 지우고 해당 문서에 반영한다.
- 결정 때문에 생기는 할 일은 [로드맵](Roadmap.md)에 태스크로 추가한다.

### 진행 기록
- 2026-10-31: 대상 언어를 결정했다. 제품 비전의 핵심 요구사항에 "개발 언어 독립"을 추가하고, 미결정 사항에서 대상 언어를 지웠다. 포인터 규약을 언어 독립으로 바꾸는 일을 M0-T8로 추가했다.
- 2026-10-31: 배포 방식을 따져 보다가, 구성 초안의 "검사기를 개발 의존성으로 설치"가 대상 프로젝트에 `pyproject.toml`이 있다고 전제한다는 것을 발견했다. 이는 개발 언어 독립 결정과 충돌하므로 `uvx` 실행을 선택지로 제시했다.
- 2026-10-31: 사용자가 두 질문의 뜻을 물어, M0-T2의 목적과 각 선택지의 장단점(막는 구멍, 설치 위치)을 설명한 뒤 다시 물었다. 강제 방식은 둘 다, 배포 방식은 git + uvx로 정했다. 제품 비전의 구성 초안에 반영하고 미결정 사항을 비웠다.

### 결정 사항
- 대상 언어: 문서 관리 도구(검사기·검증기)는 uv 환경의 Python으로 만든다. 대상 프로젝트의 개발 코드 언어와는 완전히 독립적이며, 문서와 코드는 포인터로만 연결된다. [제품 비전](ProductVision.md#3-핵심-요구사항)에 반영했다.
- 지금의 [포인터 규약](Traceability.md)은 Python AST에 묶여 있어 이 결정과 맞지 않는다. 규약 변경은 M0-T8에서 한다.
- 강제 방식: Claude Code Stop hook과 git pre-commit을 둘 다 쓴다. Stop hook은 Claude가 작업 중에 바로잡게 하고, pre-commit은 사람의 커밋까지 막아 서로 다른 구멍을 막는다. 구현은 M0-T3(규칙)과 M2-T3(설치)이 맡는다.
- 배포 방식: git 저장소의 태그로 배포하고, 대상 프로젝트는 버전만 고정해 `uvx`로 실행한다. PyPI 배포는 하지 않는다. 구현은 M1-T2(패키지 전환)와 M2-T1(설정 형식 설계)이 맡는다.

### 변경 파일
- `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Ongoing.md`

### 결과
- 미결정 사항 세 가지가 모두 정해져 [제품 비전](ProductVision.md#4-구성-초안)에 반영되었다. 이후 태스크는 이 방향을 전제로 설계한다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 47개 통과

## I2 자기 적용 원칙 명시: 작업 중 발견한 두 축 구조의 개선을 이 작업 공간과 제품 양쪽에 반영

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#3-핵심-요구사항)

### 계획
- 사용자가 밝힌 재귀 구조(규칙 체계를 만드는 CLI를 그 규칙 체계 안에서 개발하고, 발견한 개선을 양쪽에 반영)를 제품 비전에 적는다.
- 원본과 사본이 어긋나지 않게 검사하는 일을 로드맵에 추가한다.

### 진행 기록
- 2026-10-31: 사용자가 "작업 중 문서와 코드 두 축이 맞물리는 구조의 개선점을 발견하면 지금 작업 공간과 작업물에 모두 반영해야 한다"고 지시했다.
- 2026-10-31: 기존 문서에는 "이 저장소는 그 규칙을 스스로 따른다"만 있고 되먹임과 원본 관리는 없었다. 제품 비전 핵심 요구사항 7을 추가하고, 구성 초안의 공통 규칙 문서 행에 원본을 명시했다. M3-T3을 추가했다.

### 결정 사항
- 공통 규칙과 검사기의 원본은 이 저장소의 공통 규칙 문서와 `tools/` 하나다. 별도 템플릿 사본을 손으로 관리하지 않는다. 구체적인 템플릿 구성은 M2-T1에서 정한다.
- 원본과 이 저장소 사본의 일치 검사는 템플릿이 생기는 M3-T3에서 검사기로 만든다. 지금은 사본이 원본 자체라서 검사할 대상이 없다.

### 변경 파일
- `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Done.md`

### 결과
- 자기 적용과 되먹임이 제품 요구사항으로 문서에 남아, 다음 작업자도 개선을 양쪽에 반영해야 함을 안다.

### 검증
- 검증 명령 네 개 모두 통과

## I1 최종 목표 명시: Claude Code 프로젝트 초기화 CLI, 첫 세션에서 만들 프로젝트를 물으며 시작

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#1-목적)

### 계획
- 사용자가 밝힌 최종 사용 흐름을 제품 비전의 목적과 핵심 요구사항에 반영한다.
- 구현할 일을 로드맵 태스크로 추가한다.

### 진행 기록
- 2026-10-31: M0-T8 진행 중에 사용자가 최종 목표를 밝혔다. "특정 폴더를 초기화하고, 그 폴더에서 Claude Code를 시작해 세션을 열면 무슨 개발 프로젝트를 하고 싶은지 물어보며 시작하게 세팅해 주는 Claude Code 프로젝트 초기화 CLI."
- 2026-10-31: 제품 비전의 목적에 최종 사용 흐름을, 핵심 요구사항에 "첫 세션 시작 안내"를, 구성 초안에 "첫 세션 안내" 장치를 추가했다. 구현은 M2-T4로 로드맵에 추가했다.

### 결정 사항
- 첫 세션 안내는 프로젝트 고유 문서가 아직 비어 있을 때만 동작한다. 채워진 뒤에는 묻지 않는다.
- 장치의 구체적인 방식(SessionStart hook, `CLAUDE.md` 지시 등)은 M2-T4의 상세 설계에서 정한다.

### 변경 파일
- `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`

### 결과
- 제품 비전이 ProjInit을 "Claude Code 프로젝트 초기화 CLI"로 정의하고, 초기화 → Claude Code 시작 → 첫 세션에서 만들 프로젝트를 묻는 흐름을 목표로 둔다.
- 구현은 M2-T4가 맡는다.

### 검증
- 검증 명령 네 개 모두 통과 (M0-T8과 같은 시점에 실행)

## M0-T8 개발 언어에 독립적인 포인터 규약과 검사기 (Python AST 의존 제거)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 관련 이슈: I1
- 근거 문서: [포인터 규약](Traceability.md), [검증 도구](VerificationTools.md#7-코드-분석-모듈)

### 계획
- 포인터 규약을 언어 독립 형식으로 다시 쓰고, 언어별 심볼 규칙 표를 둔다.
- 검증 도구 문서에 언어 모듈(`tools/languages.py`)과 파일 분석 모듈(`tools/code_index.py`)을 명세한다.
- `tree-sitter`와 언어별 문법 패키지를 `uv add`로 추가하고, 포인터 검사기를 tree-sitter 기반으로 바꾼다.
- 언어마다 테스트를 쓴다.

### 진행 기록
- 2026-10-31: 사용자가 범용 방식으로 하라고 지시했다. tree-sitter를 골랐다.
- 2026-10-31: `tree-sitter-language-pack` 1.x는 문법을 실행할 때 `~/.cache`로 내려받는다는 것을 임시 uv 환경에서 확인했다. 버전을 고정할 수 없고 오프라인에서 깨지므로 쓰지 않는다. 대신 문법을 휠에 담은 언어별 패키지를 쓴다.
- 2026-10-31: 포인터 규약, 검증 도구, 코드 작업 규칙을 고쳤다. 이 시점에 포인터 검사기는 새 심볼이 없어서 실패하며, 그 실패 목록이 구현할 목록이다.
- 2026-10-31: 구현 중 C++ `namespace`·Rust `mod`·TS `namespace`를 "정의"로 두면 블록을 열 때마다 포인터가 필요해진다는 것을 발견했다. 코드를 쓰기 전에 규약에 "네임스페이스" 분류를 추가해 커버리지에서 뺐다.
- 2026-10-31: `tree-sitter` 0.26.0에서 노드를 순회하다 세그폴트가 났다. 같은 순회가 0.25.2에서는 정상이라 `tree-sitter>=0.25.2,<0.26`으로 고정했다.
- 2026-10-31: 한 줄 docstring의 `@doc:` 태그가 닫는 따옴표까지 경로로 읽는 문제를 고쳤다. docstring은 따옴표를 뺀 `string_content` 노드를 쓴다.
- 2026-10-31: 진행 중에 사용자가 최종 목표를 밝혀 I1로 등록하고 처리했다.

### 결정 사항
- 파서: tree-sitter와 언어별 문법 패키지. Python도 같은 방식으로 파싱해 경로를 하나로 둔다.
- 지원 언어: Python, JavaScript, TypeScript(TSX 포함), Rust, C, C++, Go, Java. [포인터 규약](Traceability.md#7-언어별-심볼-규칙)에 표로 둔다.
- 한정 이름의 구분자는 언어와 무관하게 `.`이다.
- 주석 포인터의 소속 규칙을 바꿨다. 이제 주석과 정의 사이에 빈 줄이 올 수 없다. 대신 파일의 첫 코드보다 앞에 있는 주석은 파일에 속한다. Python 밖의 언어에서 모듈 포인터를 달 곳이 필요하기 때문이다.

- 심볼 분류는 정의, 값, 네임스페이스 셋이다. 네임스페이스는 커버리지 대상이 아니며 그 안쪽은 바깥과 같은 수준으로 본다.
- `tree-sitter`는 0.26 미만으로 고정한다(0.26.0 세그폴트).

### 변경 파일
- 문서: `docs/Traceability.md`, `docs/VerificationTools.md`, `docs/CodeRule.md`, `docs/index.md`, `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`
- 신규: `tools/languages.py`, `tools/code_index.py`, `tests/test_languages.py`, `tests/test_code_index.py`
- 수정: `tools/doclib.py`, `tools/check_pointers.py`, `tests/test_check_pointers.py`, `pyproject.toml`, `uv.lock`

### 결과
- 포인터 검사기가 Python, JavaScript, TypeScript(TSX), Rust, C, C++, Go, Java 코드를 같은 포인터 형식으로 검사한다.
- 검사기 자체는 uv 환경의 Python이고, 문법은 `uv.lock`으로 고정된 패키지에 들어 있어 실행할 때 내려받지 않는다.

### 검증
- `uv run python -m tools.check_docs`: 통과 (문서 12개)
- `uv run python -m tools.check_pointers`: 통과 (문서→코드 69개, 코드→문서 61개)
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 47개 통과

## M0-T1 AgentVis의 공통 규칙 문서와 검사기를 출발점으로 복사

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#2-출발점)

### 계획
- AgentVis에서 공통 규칙 문서, 검사기, 검사기 테스트, uv 설정을 복사한다.
- AgentVis 고유 내용을 걷어 내고, 이 저장소의 제품 비전과 로드맵을 작성한다.
- 검증을 통과시키고 `git init`과 첫 커밋을 한다.

### 진행 기록
- 2026-10-31: AgentVis 세션에서 사용자 지시(AgentVis의 이슈 `I5`)로 이 저장소를 만들었다.
- 2026-10-31: 복사한 문서에서 AgentVis 고유 내용을 고쳤다. 인덱스의 제품·상세 설계 항목, 코드 작업 규칙의 `src/` 설명, 작업 관리 규칙의 기록 예시가 대상이었다.
- 2026-10-31: AgentVis 대화에서 논의한 내용(목적, 구성 초안, 출발 시점의 약점, 미결정 사항)을 [제품 비전](ProductVision.md)에 옮겨, 이 저장소의 세션이 그 대화 없이 시작할 수 있게 했다.

### 결정 사항
- 복사한 문서: `CLAUDE.md`, `docs/index.md`, `docs/DocumentationRule.md`, `docs/CodeRule.md`, `docs/Traceability.md`, `docs/TaskRule.md`, `docs/VerificationTools.md`
- 복사한 코드: `tools/`(`doclib`, `check_docs`, `check_pointers`, `check_tasks`), `tests/`(검사기 테스트)
- 복사하지 않은 것: AgentVis의 제품 비전, 데이터 소스, 시스템 구조, 상세 설계, 작업 기록
- git 사용자 정보는 전역이 아닌 저장소 로컬 설정으로 둔다.

### 변경 파일
- 신규: 위 복사 파일 전체, `docs/ProductVision.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md`, `pyproject.toml`, `uv.lock`

### 결과
- 이 저장소가 자기 규칙 체계를 갖추고, 검사기로 그 규칙을 검증할 수 있는 상태로 시작한다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 27개 통과
