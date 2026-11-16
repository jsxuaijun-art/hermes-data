---
name: superpowers-executing-plans
description: 별도 session에서 review checkpoint와 함께 작성된 구현 계획을 실행할 때 사용합니다.
lang: ko
---

# 계획 실행

## 개요

계획을 로드하고 비판적으로 검토한 뒤, 모든 task를 실행하고 완료 보고를 합니다.

시작할 때 알립니다: "superpowers-executing-plans 스킬을 사용해 이 계획을 구현하겠습니다."

Superpowers는 subagent 접근 권한이 있을 때 더 잘 작동합니다. subagent가 있는 Claude Code나 Codex 환경이라면 가능하면 `superpowers-subagent-driven-development`를 사용하고, 그렇지 않으면 이 스킬로 순차 실행합니다.

## 절차

### 1. 계획 로드와 검토

1. 계획 파일을 읽습니다.
2. 모호한 요구사항, 누락된 파일, 위험한 순서, 테스트 공백을 찾습니다.
3. 문제나 질문이 있으면 시작 전에 사용자에게 제기합니다.
4. 문제가 없으면 task 목록을 만들고 진행합니다.

### 2. task 실행

각 task마다:

1. task를 `in_progress`로 표시합니다.
2. 계획의 지시를 그대로 따릅니다.
3. 필요한 경우 `superpowers-test-driven-development`를 적용합니다.
4. 변경 직후 해당 task의 검증 명령을 실행합니다.
5. 실패하면 root cause를 찾고 고칩니다.
6. 통과하면 task를 완료 표시합니다.

계획에 없는 큰 refactor를 추가하지 않습니다. 필요하면 사용자에게 계획 수정이 필요하다고 말합니다.

### 3. 중간 checkpoint

계획이 checkpoint를 지정하면 거기서 멈춰 결과를 요약합니다. checkpoint가 없다면 계속 진행합니다. 단, 다음 상황에서는 멈춥니다.

- 요구사항이 실제 코드와 충돌합니다.
- 중요한 설계 결정이 누락됐습니다.
- 검증이 실행 불가능하고 대체 검증도 없습니다.
- 작업을 계속하면 사용자 변경을 덮어쓸 위험이 있습니다.

### 4. 완료

모든 task가 끝나면:

1. 전체 test suite 또는 계획의 최종 검증을 실행합니다.
2. 결과를 증거와 함께 요약합니다.
3. `superpowers-finishing-a-development-branch`를 사용해 branch 완료 절차로 넘어갑니다.

## 관련 스킬

- `superpowers-using-git-worktrees` - 격리 workspace 확인 또는 생성
- `superpowers-writing-plans` - 실행할 계획 생성
- `superpowers-finishing-a-development-branch` - 완료 후 통합 절차
