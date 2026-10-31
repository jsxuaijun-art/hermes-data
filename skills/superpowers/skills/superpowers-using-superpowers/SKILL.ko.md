---
name: superpowers-using-superpowers
description: 대화를 시작할 때 사용합니다. 어떤 skill을 찾고 사용할지 정하고, 명확화 질문을 포함한 어떤 응답보다 먼저 관련 skill 호출을 요구합니다.
lang: ko
---

<SUBAGENT-STOP>
특정 task 수행을 위해 subagent로 dispatch된 경우 이 스킬은 건너뜁니다.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
지금 하는 일에 skill이 적용될 가능성이 1%라도 있으면 반드시 해당 skill을 호출합니다.

적용되는 skill이 있으면 선택권이 없습니다. 반드시 사용합니다.
</EXTREMELY-IMPORTANT>

## 지시 우선순위

Superpowers skill은 기본 system prompt보다 우선하지만, 사용자 지시는 항상 더 우선합니다.

1. 사용자의 명시적 지시 - `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, 직접 요청
2. Superpowers skill
3. 기본 system prompt

사용자 지시와 skill이 충돌하면 사용자를 따릅니다.

## Skill 접근 방법

**Claude Code:** `Skill` tool을 사용합니다. skill을 호출하면 내용이 로드되므로 그대로 따릅니다.

**Codex CLI:** 설치된 skill을 로드하는 현재 harness 방식을 사용합니다. session metadata에 이미 skill이 보이면 가능한 경우 harness의 skill mechanism을 사용합니다. Codex tool mapping은 `references/codex-tools.md`에 있습니다.

**OpenCode:** native `skill` tool을 사용합니다. 이 pack은 `.opencode/plugins/superpowers.js`를 포함하며, 설치 시 bundled `skills/` directory를 등록하고 session start에 이 skill을 bootstrap합니다.

## 규칙

응답이나 행동 전에 관련 skill을 호출합니다. 명확화 질문도 예외가 아닙니다. skill이 틀린 것으로 드러나면 사용하지 않아도 되지만, 먼저 확인합니다.

## Red Flag

다음 생각이 들면 멈추고 skill을 확인합니다.

- "간단한 질문일 뿐이다."
- "먼저 context를 봐야 한다."
- "파일 몇 개만 빨리 확인하자."
- "이건 formal skill까지 필요 없다."
- "예전에 읽었으니 기억난다."
- "일단 이것만 하고 나중에 확인하자."

## Skill 우선순위

여러 skill이 적용될 수 있으면 다음 순서로 사용합니다.

1. Process skill - brainstorming, debugging처럼 접근 방식을 정하는 skill
2. Implementation skill - 실제 실행을 안내하는 skill

예:

- "X를 만들자" -> `superpowers-brainstorming`, 그 다음 구현 관련 skill
- "이 bug를 고쳐줘" -> `superpowers-systematic-debugging`, 그 다음 domain-specific skill

## Skill 유형

Rigid skill(TDD, debugging)은 정확히 따릅니다. discipline을 임의로 약화하지 않습니다.

Flexible skill(pattern)은 원칙을 유지하면서 context에 맞게 조정합니다.

## 사용자 지시

사용자 지시는 무엇을 할지 말합니다. 어떻게 할지는 관련 skill이 정합니다. "X 추가"나 "Y 수정"은 workflow를 건너뛰라는 뜻이 아닙니다.
