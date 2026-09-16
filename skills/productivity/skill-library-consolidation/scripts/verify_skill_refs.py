#!/usr/bin/env python3
"""校验一个 skill 内所有 `references/xxx.md` 引用是否解析到真实文件。

用途：合并 / 删除 / 改名 / 重指 reference 之后跑一次，确保没有吊链。
母skill 动辄几十个 reference，人工核对必漏。

用法：
    python3 verify_skill_refs.py [skill_dir]        # 默认当前目录
    python3 verify_skill_refs.py ~/.hermes/skills/communication/sales-communication

退出码：0 = 全部解析；1 = 存在真吊链。

⚠ 关键坑（本脚本存在的原因）：
母skill 里的引用有两种风格并存 ——
  (A) 全路径：`references/00-核心弹药库/core-logic.md`   → 相对 skill 根解析
  (B) 仅文件名：`references/client-group-welcome-template.md`
      但文件其实躺在 `references/05-关系维护/` 下（同级引用习惯写法）
只按 (A) 解析会把所有 (B) 误报成 BROKEN。脚本对 (B) 依次尝试：
先同目录，再全 references 树按文件名搜索，命中即算「解析成功（同级式）」。
只有当全树都搜不到同名文件时，才判定为真吊链。
"""

import re
import sys
from pathlib import Path

REF_RE = re.compile(r"references/((?:[^`\s\)\[\]]|\.)+\.md)")


def main() -> int:
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(".")
    refs_root = root / "references"
    if not refs_root.is_dir():
        print(f"[!] 不是 skill 目录（缺 references/）: {root}")
        return 1

    # 全 references 树按文件名建索引，处理「同级式」引用
    by_name: dict[str, list[Path]] = {}
    for p in refs_root.rglob("*.md"):
        by_name.setdefault(p.name, []).append(p)

    ok_full, ok_sibling, broken, self_ref = [], [], [], []
    for f in sorted(root.rglob("*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for m in REF_RE.finditer(txt):
            rel = m.group(1)
            target = refs_root / rel
            if target.exists():
                ok_full.append((f, rel))
                continue
            if target.resolve() == f.resolve():
                self_ref.append((f, rel))  # 文件引用自己，通常是说明性文字
                continue
            # 「同级式」：只看末段文件名，在整棵树里找
            hits = by_name.get(Path(rel).name, [])
            if hits:
                ok_sibling.append((f, rel, hits[0].relative_to(root)))
                continue
            broken.append((f, rel))

    total = len(ok_full) + len(ok_sibling) + len(broken) + len(self_ref)
    print(f"skill: {root}")
    print(f"引用总数 {total}｜全路径命中 {len(ok_full)}｜同级式命中 {len(ok_sibling)}｜真吊链 {len(broken)}")

    if self_ref:
        print("\n-- 自引用（多为说明文字，通常无害）--")
        for f, rel in self_ref:
            print(f"  {f.relative_to(root)} -> {rel}")

    if ok_sibling:
        print("\n-- 同级式命中（能解析，但建议改全路径更稳）--")
        for f, rel, hit in ok_sibling:
            print(f"  {f.relative_to(root)} -> {rel}  ⇒ 实际 {hit}")

    if broken:
        print("\n-- ✗ 真吊链（必须修）--")
        for f, rel in broken:
            print(f"  {f.relative_to(root)} -> references/{rel}")
        print("\n退出码 1")
        return 1

    print("\nOK：无吊链。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
