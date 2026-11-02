# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M8-T2 Codex hook과 강제 장치 검사

- 시작일: 2026-11-02
- 근거 문서: [에이전트 지원 설계](design/Agents.md#2-무엇이-다른가), [검증 도구](VerificationTools.md#9-일괄-실행과-자동-실행)
- 참고 자료: 없음

### 계획
- `.codex/hooks.json` 템플릿: Stop은 `check --hook stop --agent codex`, SessionStart는 `context`. 저장소 루트는 `git rev-parse --show-toplevel`로 찾는다.
- `check --hook stop --agent codex`: 통과하면 `{}`를 출력한다(Codex는 종료 코드 0일 때 JSON을 요구한다). 막기와 두 번째 허용은 Claude와 같다. Claude의 출력은 바꾸지 않는다.
- 강제 장치 검사기는 켠 에이전트의 hook만 검사한다. Codex hook 검사를 더한다.
- 초기화 안내에 Codex의 프로젝트·hook 신뢰 단계를 넣는다. 시나리오 테스트에 Codex 프로젝트를 더한다.

### 진행 기록
- 2026-11-02: M8-T1에 이어 시작했다.
