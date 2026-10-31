---
name: superpowers-test-driven-development
description: 기능, bugfix, refactor, 동작 변경을 구현하기 전에 사용합니다.
lang: ko
---

# Test-Driven Development (TDD)

## 개요

테스트를 먼저 작성합니다. 실패하는 것을 확인합니다. 통과에 필요한 최소 코드를 작성합니다.

핵심 원칙: 실패를 보지 않은 테스트는 올바른 것을 검증하는지 알 수 없습니다.

## 사용 시점

항상 사용:

- 새 기능
- bug fix
- refactor
- 동작 변경

예외는 사용자에게 확인합니다.

- throwaway prototype
- generated code
- 단순 config 파일
- 테스트 불가능한 spike

## Red-Green-Refactor

### RED

실패하는 test를 먼저 작성합니다.

요구사항 하나만 검증합니다. 너무 넓은 integration test로 시작하지 말고, 가능한 가장 작은 관찰 가능한 behavior를 고릅니다.

RED 단계에서 반드시 확인합니다.

```bash
<test command>
```

실패 이유가 기대한 이유인지 확인합니다. 엉뚱한 import error나 setup failure면 test가 아직 유효하지 않습니다.

### GREEN

테스트를 통과시키는 최소 구현을 작성합니다.

금지:

- 미래 요구사항 미리 구현
- 불필요한 abstraction
- test를 약하게 만들기
- failure를 숨기기

통과 확인:

```bash
<same test command>
```

### REFACTOR

테스트가 통과한 상태에서 구조를 개선합니다. 중복 제거, 이름 개선, 기존 pattern 정렬을 수행합니다. 각 refactor 후 test를 다시 실행합니다.

## 테스트 선택

좋은 테스트:

- user-visible behavior 또는 public contract를 검증합니다.
- 실패 원인이 분명합니다.
- production implementation을 그대로 복제하지 않습니다.
- deterministic합니다.

나쁜 테스트:

- mock만 검증합니다.
- 내부 구현 세부사항에 과하게 묶입니다.
- 너무 많은 behavior를 한 test에 넣습니다.
- 실패하지 않는 것을 확인하지 않았습니다.

자세한 안티패턴은 `testing-anti-patterns.md`를 참고합니다.

## Bug fix 절차

1. bug를 재현하는 test를 작성합니다.
2. test가 현재 코드에서 실패하는 것을 확인합니다.
3. root cause를 고칩니다.
4. test가 통과하는 것을 확인합니다.
5. 관련 regression suite를 실행합니다.

bug의 원인을 모르면 먼저 `superpowers-systematic-debugging`을 사용합니다.

## 기존 코드가 테스트하기 어려울 때

즉시 큰 refactor를 하지 않습니다.

1. 현재 behavior를 보호하는 characterization test를 작성합니다.
2. 작은 seam을 만듭니다.
3. 원하는 새 behavior에 대한 failing test를 작성합니다.
4. 최소 변경으로 통과시킵니다.

## 완료 기준

- 새 test가 먼저 실패했습니다.
- 같은 test가 변경 후 통과했습니다.
- 관련 suite가 통과했습니다.
- refactor 후에도 통과합니다.
- 실패와 통과 evidence를 보고할 수 있습니다.
