---
name: superpowers
description: 이 스킬 컬렉션에서 Superpowers 방법론을 설치, 테스트, 조정, 호출할 때 사용합니다. superpowers 접두어가 붙은 스킬 라이브러리와 OpenCode, Codex CLI, Claude Code용 설정 및 검증 절차를 제공합니다.
version: 5.1.0-meta.1
user-invocable: true
source: https://github.com/obra/superpowers
license: MIT
lang: ko
---

# Superpowers 스킬 팩

이 스킬은 Jesse Vincent의 Superpowers 프로젝트를 `meta-skills` 저장소 형식에 맞게 조정한 것입니다. 섞여 있는 스킬 컬렉션에서도 출처가 분명하도록 모든 포함 workflow skill 이름에 `superpowers-` 접두어를 붙였습니다.

## 포함된 스킬

핵심 workflow skill은 `skills/` 아래에 있습니다.

- `superpowers-using-superpowers`
- `superpowers-brainstorming`
- `superpowers-using-git-worktrees`
- `superpowers-writing-plans`
- `superpowers-subagent-driven-development`
- `superpowers-executing-plans`
- `superpowers-test-driven-development`
- `superpowers-systematic-debugging`
- `superpowers-verification-before-completion`
- `superpowers-requesting-code-review`
- `superpowers-receiving-code-review`
- `superpowers-dispatching-parallel-agents`
- `superpowers-finishing-a-development-branch`
- `superpowers-writing-skills`

## 이 저장소에서의 사용 방식

사용자가 Superpowers 방식의 작업을 요청하면 가장 구체적인 prefixed skill을 로드합니다. `superpowers-using-superpowers`는 부트스트랩과 방향 안내 용도로만 사용합니다.

사용자의 전역 agent 설정에 hook을 조용히 설치하지 마십시오. hook이 유용해 보이면 `references/harness-installation.md`를 읽고, 변경될 파일을 정확히 설명한 뒤 현재 workspace 밖에 쓰기 전에 승인을 받습니다.

## 지원 하네스

이 팩은 다음 환경을 위한 메타데이터와 설정 안내를 포함합니다.

- Codex CLI: `.codex-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json` 및 선택적 session-start hook
- OpenCode: `.opencode/plugins/superpowers.js`

설치, hook 설정, 문제 해결, cross-harness packaging 작업에서는 `references/harness-installation.md`를 읽습니다.

운영 세부사항은 별도 reference로 나뉩니다.

- `references/opencode.md`: OpenCode 설치, 업데이트, cache, Windows, tool mapping 동작
- `references/polyglot-hooks.md`: Claude Code cross-platform hook 동작
- `references/testing.md`: static 및 integration test 전략

## 검증

이 팩을 편집한 뒤 구조 검사를 실행합니다.

```bash
python3 skills/superpowers/scripts/validate.py skills/superpowers
```

검증기는 frontmatter 이름, 필수 plugin 파일, hook 참조, OpenCode bootstrap 경로, 운영 reference, 접두어가 빠진 bundled skill 이름을 확인합니다.

## Upstream 출처

원본 프로젝트: <https://github.com/obra/superpowers>

저자: Jesse Vincent

라이선스: MIT. 사본은 `references/UPSTREAM-LICENSE`에 있습니다.
