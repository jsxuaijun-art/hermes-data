---
name: superpowers-subagent-driven-development
description: 현재 session에서 독립 task가 있는 구현 계획을 실행할 때 사용합니다.
lang: ko
---

# Subagent 기반 개발

구현 계획을 task 단위로 실행합니다. 각 task마다 fresh subagent를 dispatch하고, 완료 후 spec compliance review와 code quality review를 거칩니다.

핵심 원칙: task마다 fresh subagent + 2단계 review = 빠르면서 품질 높은 반복.

## 계속 실행

사용자가 계획 실행을 요청했다면 task 사이에 "계속할까요?"라고 묻지 않습니다. 멈추는 이유는 다음뿐입니다.

- 스스로 해결할 수 없는 BLOCKED 상태
- 진행을 막는 진짜 모호성
- 모든 task 완료

## 사용 조건

사용합니다:

- 승인된 구현 계획이 있습니다.
- task가 대부분 독립적입니다.
- subagent를 사용할 수 있습니다.
- 현재 session에서 조정과 통합을 할 수 있습니다.

사용하지 않습니다:

- 아직 계획이 없습니다. 먼저 `superpowers-writing-plans`.
- 설계가 승인되지 않았습니다. 먼저 `superpowers-brainstorming`.
- task가 순차 의존성이 강합니다. `superpowers-executing-plans`가 더 적절할 수 있습니다.

## 절차

### 1. 계획 검토

계획 파일을 읽고 다음을 확인합니다.

- task가 작고 검증 가능함
- 파일 소유 범위가 분명함
- test-first가 가능한 부분이 표시됨
- 순서와 dependency가 현실적임
- 완료 조건이 명확함

문제가 있으면 실행 전에 사용자에게 제기합니다.

### 2. Task dispatch

각 implementation task마다 별도 subagent를 보냅니다. 지시문에는 다음을 포함합니다.

- task 목표
- 관련 계획 section
- 수정 가능한 파일 또는 모듈
- TDD 요구사항
- 실행할 검증 명령
- 다른 변경을 revert하지 말라는 지시
- 최종 보고 형식

subagent는 현재 session 전체 history를 받지 않습니다. 필요한 context만 제공합니다.

### 3. Spec compliance review

implementation agent가 끝나면 별도 reviewer에게 보냅니다.

확인 항목:

- 계획 task를 정확히 완료했는가
- 요구사항 누락이 있는가
- 범위를 벗어난 변경이 있는가
- 검증이 충분한가

문제가 있으면 implementation agent 또는 메인 session에서 수정합니다.

### 4. Code quality review

spec compliance가 통과한 뒤 code quality reviewer를 보냅니다.

확인 항목:

- bug, regression, edge case
- 유지보수성
- test 품질
- 단순성
- 기존 pattern 준수

critical/high issue는 다음 task 전에 해결합니다.

### 5. 통합과 검증

각 task 후 메인 session에서 변경을 확인하고 필요한 검증을 실행합니다. conflict나 중복 변경이 있으면 즉시 정리합니다.

### 6. 완료

모든 task가 끝나면 전체 구현에 대한 최종 code review를 수행하고, 전체 test suite를 실행한 뒤 `superpowers-finishing-a-development-branch`로 넘어갑니다.

## Subagent 지시문 원칙

- 독립적이고 작은 task를 줍니다.
- write scope를 명시합니다.
- 계획과 요구사항을 직접 포함합니다.
- "다른 사람의 변경을 되돌리지 말라"고 명시합니다.
- 결과에는 변경 파일, 검증, 남은 위험을 포함하게 합니다.

## 관련 스킬

- `superpowers-using-git-worktrees`
- `superpowers-writing-plans`
- `superpowers-requesting-code-review`
- `superpowers-finishing-a-development-branch`
- `superpowers-test-driven-development`
- `superpowers-executing-plans`
