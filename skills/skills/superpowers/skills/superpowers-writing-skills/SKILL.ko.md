---
name: superpowers-writing-skills
description: 새 skill을 만들거나, 기존 skill을 수정하거나, 배포 전에 skill이 작동하는지 검증할 때 사용합니다.
lang: ko
---

# Skill 작성

## 개요

Skill 작성은 process documentation에 TDD를 적용하는 일입니다.

먼저 pressure scenario를 만들고, skill 없이 agent가 실패하는지 확인하고, skill을 작성한 뒤, 같은 scenario에서 agent가 올바르게 행동하는지 검증합니다.

핵심 원칙: skill 없이 실패하는 것을 보지 않았다면, 그 skill이 실제로 무엇을 가르치는지 알 수 없습니다.

필수 배경: `superpowers-test-driven-development`의 RED-GREEN-REFACTOR 원칙을 이해해야 합니다. 이 skill은 그 원칙을 문서 작성에 적용합니다.

## Skill이란

Skill은 검증된 기술, pattern, tool, workflow를 재사용 가능한 형태로 정리한 reference guide입니다.

Skill은 다음이어야 합니다.

- 반복 사용 가능한 technique
- 명확한 trigger
- 구체적 절차
- 검증 가능한 행동

Skill은 다음이 아닙니다.

- 한 번 해결한 문제의 회고
- 일반적인 조언 모음
- 과도한 배경 설명
- tool 없이도 모델이 이미 아는 내용의 장문 설명

## 작성 절차

### RED: 실패 사례 정의

skill이 필요한 압박 상황을 만듭니다.

- agent가 어떤 잘못된 shortcut을 택하는가
- 어떤 rationalization을 하는가
- 어떤 결과가 실패인가
- 성공 행동은 무엇인가

가능하면 subagent나 별도 session으로 baseline을 확인합니다. 의도한 답을 노출하지 않습니다.

### GREEN: 최소 skill 작성

실패를 막는 데 필요한 최소 지침을 작성합니다.

Frontmatter:

```yaml
---
name: skill-name
description: 언제 이 skill을 사용해야 하는지 구체적으로 설명합니다.
---
```

Body:

- 핵심 원칙
- 언제 사용/사용하지 않는지
- 절차
- checklist
- 필요한 reference 파일 링크
- 검증 방법

### REFACTOR: 간결화

중복과 장황함을 줄입니다. 모델이 이미 아는 일반론은 제거하고, 이 workflow에 꼭 필요한 guardrail만 남깁니다.

## Description 작성

Description은 skill trigger입니다. 가장 중요합니다.

좋은 description:

- 사용자가 어떤 요청을 할 때 적용되는지 말합니다.
- 숨은 상황도 포함합니다.
- 너무 넓지 않습니다.

나쁜 description:

- "helps with code"
- "best practices"
- "useful workflow"

## Body 작성 원칙

- 명령은 구체적으로 씁니다.
- 반드시 지켜야 하는 gate는 명확히 표시합니다.
- 예외 조건을 씁니다.
- workflow는 순서가 보이게 씁니다.
- 긴 reference는 별도 file로 뺍니다.
- agent가 합리화할 지점을 미리 차단합니다.

## Reference와 script

`SKILL.md`는 핵심 workflow만 담습니다.

다음은 reference로 분리합니다.

- 긴 예시
- API 문서
- 상세 pattern catalog
- platform별 세부 설정

반복적이고 fragile한 작업은 script로 만듭니다.

## 검증

skill을 배포하기 전에 다음을 확인합니다.

- frontmatter가 유효합니다.
- description이 trigger를 충분히 설명합니다.
- pressure scenario에서 원하는 행동을 유도합니다.
- 불필요한 context가 없습니다.
- 관련 reference가 실제로 존재합니다.
- 검증 방법이 명시되어 있습니다.

## 결과물

완료된 skill은 다음을 만족해야 합니다.

- `SKILL.md`가 root에 있습니다.
- optional `references/`, `scripts/`, `assets/`만 포함합니다.
- README, INSTALLATION_GUIDE, CHANGELOG 같은 별도 문서를 남발하지 않습니다.
- 필요한 경우 harness metadata를 포함합니다.
- 테스트 또는 검증 절차가 있습니다.
