---
name: superpowers-writing-plans
description: 여러 단계가 필요한 task의 spec 또는 요구사항이 있을 때, 코드를 만지기 전에 사용합니다.
lang: ko
---

# 구현 계획 작성

## 개요

코드베이스 맥락이 거의 없는 engineer도 따라 할 수 있을 만큼 구체적인 구현 계획을 작성합니다. 어떤 파일을 만질지, 어떤 코드를 쓸지, 어떤 test를 실행할지, 어떤 문서를 확인할지까지 포함합니다.

시작할 때 알립니다: "superpowers-writing-plans 스킬을 사용해 구현 계획을 만들겠습니다."

계획 저장 위치: `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

사용자 선호 위치가 있으면 그것을 따릅니다.

## Scope 확인

spec이 여러 독립 subsystem을 포함하면 별도 plan으로 나눌 것을 제안합니다. 각 plan은 독립적으로 작동하고 테스트 가능한 결과를 만들어야 합니다.

## 파일 구조 먼저 정의

task를 쓰기 전에 생성 또는 수정할 파일 목록과 각 파일의 책임을 정합니다. decomposition 결정은 여기서 고정합니다.

## 계획 형식

계획은 다음을 포함합니다.

1. 목표 요약
2. 현재 코드베이스 맥락
3. 변경할 파일 목록
4. task checklist
5. 각 task의 정확한 작업 내용
6. test-first 지시
7. 검증 명령
8. rollback 또는 위험 notes

각 task는 2-5분 단위로 작게 만듭니다. 너무 큰 task는 쪼갭니다.

## Task 작성 규칙

각 task에는 다음이 있어야 합니다.

- 목적
- 수정할 파일
- 구체적인 단계
- 작성할 test
- 통과 기준
- 실행할 명령

예:

```markdown
- [ ] Task 3: Add validation for empty title
  - File: `src/form.ts`
  - Test: add failing test in `src/form.test.ts`
  - Implementation: reject empty title before save
  - Verify: `npm test -- form.test.ts`
```

## TDD 통합

동작 변경 task는 test-first로 작성합니다.

계획에는 다음 문구를 포함합니다.

```text
For agentic workers: REQUIRED SUB-SKILL: Use superpowers-test-driven-development for behavior changes.
```

## 실행 방식 선택

계획 마지막에 실행 옵션을 제시합니다.

- subagent 사용 가능: `superpowers-subagent-driven-development`
- subagent 없음 또는 순차 실행: `superpowers-executing-plans`

## 완료 기준

계획이 완료되면 사용자가 승인할 수 있을 만큼 명확해야 합니다. 승인 전에는 구현하지 않습니다.
