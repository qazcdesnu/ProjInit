# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M8-T1 에이전트 설정, Codex 진입 문서와 시작 skill

- 시작일: 2026-11-02
- 근거 문서: [에이전트 지원 설계](design/Agents.md)
- 참고 자료: 없음

### 계획
- 에이전트 지원 설계 문서를 쓴다. Claude Code의 동작은 바꾸지 않고, Codex용 파일을 옆에 더하는 방식이다.
- 설정 `projinit.agents`(기본 `["claude"]`)와 `init --agent codex`. 에이전트별 공통 파일을 나눈다.
- Codex 진입 문서 `AGENTS.md`(`CLAUDE.md`와 본문이 같음)와 시작 skill `.agents/skills/start/`(`$start`, 명시 호출만).
- 문서 링크 검사기가 `AGENTS.md`도 진입 문서로 다룬다.

### 진행 기록
- 2026-11-02: 사용자가 다른 코딩 에이전트가 세션 시작 때 읽는 문서를 조사하라고 했다. Codex는 `AGENTS.md`, Antigravity는 `AGENTS.md`나 `GEMINI.md`를 읽지만, 강제 장치(hook, 시작 명령)는 도구마다 다르다고 답했다. 사용자가 Codex 호환까지 먼저 진행하되, 호환성을 위해 일반화하다가 Claude와 Codex 모두에서 성능이 떨어지면 안 된다고 했다.
