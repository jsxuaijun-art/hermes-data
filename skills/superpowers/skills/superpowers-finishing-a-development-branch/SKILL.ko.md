---
name: superpowers-finishing-a-development-branch
description: 구현이 완료되고 테스트가 통과했으며, merge, PR, 정리 등 통합 방법을 결정해야 할 때 사용합니다.
lang: ko
---

# 개발 Branch 마무리

## 개요

완료된 개발 작업을 검증하고, 환경을 감지하고, 사용자에게 명확한 통합 선택지를 제시한 뒤 선택한 절차를 수행합니다.

핵심 원칙: 테스트 검증 -> 환경 감지 -> 선택지 제시 -> 선택 실행 -> 정리.

시작할 때 알립니다: "superpowers-finishing-a-development-branch 스킬을 사용해 이 작업을 마무리하겠습니다."

## 1. 테스트 검증

선택지를 제시하기 전에 반드시 테스트를 실행합니다.

```bash
npm test / cargo test / pytest / go test ./...
```

실패하면 merge나 PR 선택지를 제시하지 않습니다. 실패 내용을 요약하고 고칩니다. 테스트를 실행할 수 없다면 이유와 대체 검증을 명확히 기록합니다.

## 2. Git 상태 확인

다음을 확인합니다.

```bash
git status --short
git branch --show-current
git log --oneline -5
```

사용자 변경과 내가 만든 변경을 구분합니다. 내가 만들지 않은 변경은 되돌리지 않습니다.

## 3. 환경 감지

현재 branch가 다음 중 어디에 해당하는지 확인합니다.

- 일반 branch
- git worktree
- PR branch
- detached HEAD
- submodule 내부

worktree라면 원래 repository 위치와 branch 이름을 확인합니다. submodule이라면 부모 repository를 임의로 수정하지 않습니다.

## 4. 사용자에게 선택지 제시

검증이 끝난 뒤 다음과 같이 선택지를 제시합니다.

```text
테스트가 통과했습니다. 다음 중 어떻게 마무리할까요?

1. 현재 branch 유지 - 여기서 계속 작업
2. PR 생성 - review를 위해 올림
3. main에 merge - 로컬 merge 수행
4. worktree 정리 - 변경 보존 후 작업공간 제거
5. 보류 - 아무 것도 통합하지 않음
```

실제 가능한 선택지만 제시합니다. 예를 들어 remote가 없으면 PR 생성을 기본 선택지로 두지 않습니다.

## 5. 선택 실행

사용자 선택에 따라 실행합니다.

PR 생성:
- remote와 base branch를 확인합니다.
- PR title/body를 작성합니다.
- 가능한 경우 CLI로 생성합니다.

merge:
- clean 상태와 최신 base를 확인합니다.
- merge 전후 테스트를 실행합니다.
- 충돌이 있으면 멈추고 보고합니다.

worktree 정리:
- 변경이 push되었거나 안전하게 보존됐는지 확인합니다.
- worktree 제거 전 사용자 승인을 받습니다.

보류:
- 현재 상태와 재개 방법을 남깁니다.

## 완료 보고

최종 답변에는 다음을 포함합니다.

- 실행한 검증 명령과 결과
- 선택한 통합 방식
- 생성된 PR 또는 merge 결과
- 남은 위험 또는 후속 작업
