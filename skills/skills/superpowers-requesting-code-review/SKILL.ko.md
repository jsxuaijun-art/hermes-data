---
name: superpowers-requesting-code-review
description: task 완료, 주요 기능 구현, merge 전 요구사항 충족 여부를 검증할 때 사용합니다.
lang: ko
---

# 코드 리뷰 요청

작업 결과가 요구사항을 만족하는지 확인하기 위해 reviewer subagent를 보냅니다. reviewer에게는 현재 session history가 아니라 정확히 필요한 context만 제공합니다.

핵심 원칙: 일찍, 자주 리뷰합니다.

## 리뷰 요청 시점

필수:

- subagent-driven development의 각 task 이후
- 주요 기능 완료 후
- main merge 전

선택이지만 유용한 경우:

- 막혔을 때 fresh perspective가 필요할 때
- refactor 전 baseline을 확인할 때
- 복잡한 bug fix 후

## 요청 준비

1. 기준 SHA와 현재 SHA를 확인합니다.

```bash
git rev-parse HEAD
git diff --stat
git diff
```

2. reviewer에게 줄 정보를 정리합니다.

- 원래 요구사항 또는 계획
- 변경된 파일
- 검증 명령과 결과
- 특별히 봐야 할 위험

## Reviewer 지시문

```text
You are reviewing this change for correctness, requirement compliance, and regressions.

Context:
- Goal: <목표>
- Requirements: <요구사항>
- Changed files: <파일 목록>
- Verification run: <명령과 결과>

Review:
1. 요구사항 누락
2. bug 또는 regression
3. test gap
4. security 또는 data loss risk
5. maintainability 문제

Return findings first, ordered by severity, with file/line references.
If no issues, say so and mention residual risk.
```

필요하면 `superpowers-requesting-code-review/code-reviewer.md` 템플릿을 참고합니다.

## 결과 처리

reviewer 결과를 받은 뒤:

1. findings를 심각도별로 읽습니다.
2. 실제 코드와 대조합니다.
3. critical 또는 high issue는 진행 전에 수정합니다.
4. 틀린 지적이면 근거를 남깁니다.
5. 수정 후 관련 검증을 다시 실행합니다.

## 완료 기준

- critical/high finding이 남아 있지 않습니다.
- 수용한 finding은 수정되고 테스트됐습니다.
- 반려한 finding은 코드 근거가 있습니다.
- 최종 요약에 검증 결과를 포함합니다.
