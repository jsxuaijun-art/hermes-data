#!/usr/bin/env python3
"""Validate the meta-skills Superpowers adaptation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


EXPECTED = {
    "superpowers-brainstorming",
    "superpowers-dispatching-parallel-agents",
    "superpowers-executing-plans",
    "superpowers-finishing-a-development-branch",
    "superpowers-receiving-code-review",
    "superpowers-requesting-code-review",
    "superpowers-subagent-driven-development",
    "superpowers-systematic-debugging",
    "superpowers-test-driven-development",
    "superpowers-using-git-worktrees",
    "superpowers-using-superpowers",
    "superpowers-verification-before-completion",
    "superpowers-writing-plans",
    "superpowers-writing-skills",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text()


def frontmatter_name(skill_md: Path) -> str:
    text = read(skill_md)
    match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    if not match:
        fail(f"{skill_md} missing frontmatter name")
    return match.group(1).strip().strip("'\"")


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if not root.exists():
        fail(f"{root} does not exist")

    top = root / "SKILL.md"
    if frontmatter_name(top) != "superpowers":
        fail("top-level SKILL.md must be named superpowers")

    skills_dir = root / "skills"
    found = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    if found != EXPECTED:
        fail(f"skill directories mismatch: missing={sorted(EXPECTED - found)} extra={sorted(found - EXPECTED)}")

    for name in sorted(EXPECTED):
        skill_md = skills_dir / name / "SKILL.md"
        actual = frontmatter_name(skill_md)
        if actual != name:
            fail(f"{skill_md} has name {actual!r}, expected {name!r}")

    codex = json.loads(read(root / ".codex-plugin" / "plugin.json"))
    claude = json.loads(read(root / ".claude-plugin" / "plugin.json"))
    marketplace = json.loads(read(root / ".claude-plugin" / "marketplace.json"))
    package = json.loads(read(root / "package.json"))
    if codex.get("name") != "superpowers" or codex.get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json must expose superpowers skills at ./skills/")
    if claude.get("name") != "superpowers":
        fail(".claude-plugin/plugin.json must be named superpowers")
    if marketplace.get("name") != "superpowers-dev":
        fail(".claude-plugin/marketplace.json must expose superpowers-dev")
    if package.get("main") != ".opencode/plugins/superpowers.js":
        fail("package.json must point OpenCode at .opencode/plugins/superpowers.js")
    if not (root / ".opencode" / "INSTALL.md").exists():
        fail(".opencode/INSTALL.md missing")

    for ref in ("harness-installation.md", "opencode.md", "testing.md", "polyglot-hooks.md", "UPSTREAM-LICENSE"):
        if not (root / "references" / ref).exists():
            fail(f"references/{ref} missing")

    opencode = read(root / ".opencode" / "plugins" / "superpowers.js")
    if "superpowers-using-superpowers" not in opencode:
        fail("OpenCode plugin must bootstrap superpowers-using-superpowers")

    hook = read(root / "hooks" / "session-start")
    if "superpowers-using-superpowers" not in hook:
        fail("Claude session-start hook must load superpowers-using-superpowers")

    unprefixed = []
    for skill_md in skills_dir.glob("*/SKILL.md"):
        name = frontmatter_name(skill_md)
        if name != "superpowers" and not name.startswith("superpowers-"):
            unprefixed.append(f"{skill_md}:{name}")
    if unprefixed:
        fail("unprefixed skill names found: " + ", ".join(unprefixed))

    print(f"OK: validated {len(EXPECTED)} superpowers-prefixed skills in {root}")


if __name__ == "__main__":
    main()
