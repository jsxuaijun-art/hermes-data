---
name: superpowers-systematic-debugging
description: bug, test failure, 예상과 다른 동작을 만났을 때 fix를 제안하기 전에 사용합니다.
lang: ko
---

# 체계적 디버깅

## 개요

무작위 fix는 시간을 낭비하고 새 bug를 만듭니다. 빠른 patch는 근본 원인을 가립니다.

핵심 원칙: fix를 시도하기 전에 항상 root cause를 찾습니다.

## 철칙

```text
ROOT CAUSE 조사 없이 FIX 금지
```

Phase 1을 완료하지 않았다면 fix를 제안할 수 없습니다.

## 사용 시점

다음 모든 기술 문제에 사용합니다.

- test failure
- production bug
- 예상과 다른 behavior
- flaky test
- performance regression
- build 또는 deploy failure

## Phase 1: 문제 관찰

증상을 정확히 기록합니다.

- 어떤 명령이 실패했는가
- 실제 output은 무엇인가
- 기대 output은 무엇인가
- 언제부터 발생했는가
- 재현 가능한가

명령을 직접 실행해 fresh evidence를 확보합니다. 다른 사람의 설명만 믿지 않습니다.

## Phase 2: 범위 좁히기

문제가 어디에서 시작되는지 찾습니다.

- 최근 변경 확인
- 관련 test를 더 좁게 실행
- input과 output 경계 확인
- 로그 또는 state를 추가로 관찰
- binary search가 가능하면 사용

목표는 "어느 component가 잘못됐다"가 아니라 "어떤 원인 때문에 어떤 상태가 만들어졌다"까지 좁히는 것입니다.

## Phase 3: 가설 검증

가설을 세우고, 각 가설을 증명하거나 반증할 실험을 합니다.

좋은 가설:

- 구체적입니다.
- 관찰 가능한 예측을 만듭니다.
- 틀렸을 때 버릴 수 있습니다.

나쁜 가설:

- "아마 timing 문제"
- "dependency 문제 같음"
- "cache 때문일 수도"

각 실험은 하나의 변수만 바꿉니다.

## Phase 4: Fix

root cause가 확인된 뒤에만 fix합니다.

1. 실패를 재현하는 test를 먼저 작성합니다.
2. test가 실패하는 것을 확인합니다.
3. 최소한의 fix를 적용합니다.
4. test가 통과하는지 확인합니다.
5. 관련 regression test를 실행합니다.

test 작성에는 `superpowers-test-driven-development`를 사용합니다.

## 방어적 보강

root cause를 고친 뒤 같은 종류의 문제가 다시 생기지 않도록 필요한 만큼만 보강합니다.

- validation
- clearer error
- regression test
- monitoring 또는 logging
- invariant check

하지만 symptom을 숨기는 방어 코드는 만들지 않습니다.

## 완료 전 검증

완료 주장 전에 `superpowers-verification-before-completion`을 사용합니다. "고친 것 같다"가 아니라 fresh verification evidence가 있어야 합니다.

## 관련 자료

필요할 때 같은 디렉터리의 reference를 읽습니다.

- `root-cause-tracing.md`
- `defense-in-depth.md`
- `condition-based-waiting.md`
