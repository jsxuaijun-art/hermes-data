---
name: superpowers-using-git-worktrees
description: 현재 workspace와 분리된 feature work가 필요하거나 구현 계획 실행 전에 격리 workspace를 보장할 때 사용합니다.
lang: ko
---

# Git Worktree 사용

## 개요

작업이 격리된 workspace에서 진행되도록 보장합니다. 먼저 platform native worktree 기능을 선호하고, 없으면 manual git worktree를 사용합니다.

핵심 원칙: 기존 격리를 먼저 감지하고, native 도구를 우선하며, 그 다음 git fallback을 사용합니다.

시작할 때 알립니다: "superpowers-using-git-worktrees 스킬을 사용해 격리 workspace를 설정하겠습니다."

## Step 0: 기존 격리 감지

새 worktree를 만들기 전에 이미 격리된 workspace인지 확인합니다.

```bash
git rev-parse --git-dir
git rev-parse --git-common-dir
git branch --show-current
```

주의: submodule 내부에서도 `git-dir`과 `git-common-dir`이 다를 수 있습니다. submodule인지 확인한 뒤 판단합니다.

## Step 1: 현재 상태 확인

```bash
git status --short
git remote -v
git branch --show-current
```

dirty worktree가 있으면 사용자 변경을 보호합니다. 내가 만들지 않은 변경을 stash, reset, checkout으로 없애지 않습니다.

## Step 2: Branch 이름 결정

작업 목적을 설명하는 짧은 이름을 사용합니다.

예:

- `feature/add-export-flow`
- `fix/login-timeout`
- `chore/update-superpowers`

충돌하면 suffix를 붙입니다.

## Step 3: Worktree 생성

native tool이 있으면 사용합니다. 없으면 git을 사용합니다.

```bash
git worktree add ../<repo>-<branch-name> -b <branch-name>
```

base branch가 필요하면 먼저 확인합니다. remote fetch가 필요할 수 있지만, 네트워크 작업은 환경 정책을 따릅니다.

## Step 4: Setup과 baseline 검증

새 workspace에서 dependency와 baseline test를 확인합니다.

```bash
pwd
git status --short
<project setup command>
<baseline test command>
```

baseline이 실패하면 작업을 시작하지 말고 보고합니다. 기존 실패인지 새 환경 문제인지 구분합니다.

## Step 5: 다음 작업

격리 workspace가 준비되면 implementation plan 실행으로 넘어갑니다.

- 계획이 없으면 `superpowers-writing-plans`
- 계획이 있고 subagent가 가능하면 `superpowers-subagent-driven-development`
- subagent가 없으면 `superpowers-executing-plans`

## 정리

작업 완료 후에는 `superpowers-finishing-a-development-branch`를 사용해 merge, PR, 보류, worktree 제거를 결정합니다. 완료 전에 임의로 worktree를 삭제하지 않습니다.
