#!/usr/bin/env python3
"""
scan_same_name_copies.py — 同名多副本扫描 / 去重（skill-library-exchange-ops）

默认【只读】：报告重名组、内容是否一致、实际加载哪份、将会删哪些副本。
加 --apply 才真正删除，并把删除镜像到 hermes-data（否则 rsync -a 会还原）。

关键设计（每条都对应一个真实踩过的坑）：
  * 匹配键 = SKILL.md frontmatter 的 name:（不是目录名！目录名≠技能名真实存在）
  * 排除 .archive/（curator 归档，不被加载，不一致是正常的）
  * 只对“内容完全一致”的重名组去重；“内容不一致”的是真冲突，只报告不删
  * 每组保留路径最深的那份（skilllib 只装分类嵌套版，嵌套版才持久）
  * 删除镜像到 hermes-data，否则拉取脚本 rsync -a 会把扁平副本还原、遮蔽复发

用法：
    # 只读报告
    python3 scripts/scan_same_name_copies.py

    # 执行去重（先自行备份！脚本会检查备份目录存在）
    tar czf ~/skill-dupes-backup/skills-full-$(date +%Y%m%d-%H%M%S).tar.gz -C ~/.hermes skills
    python3 scripts/scan_same_name_copies.py --apply

之后必须复核加载路径：
    python3 scripts/scan_same_name_copies.py --check-loaded /short-video-copywriting
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
from collections import defaultdict

ROOT = os.path.expanduser("~/.hermes/skills")
HD = "/mnt/c/Users/Admin/hermes-sync/skills"
ARCHIVE_MARK = os.sep + ".archive"
BACKUP_DIR = os.path.expanduser("~/skill-dupes-backup")


def md5f(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()[:8]
    except OSError:
        return "0"


def fm_name(skill_md: str) -> str | None:
    """读 frontmatter 的 name:（唯一正确的匹配键）。失败返回 None。"""
    try:
        with open(skill_md, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4000)
    except OSError:
        return None
    m = re.search(r'^name:\s*["\']?([^\n"\']+)', head, re.MULTILINE)
    return m.group(1).strip() if m else None


def collect(root: str) -> dict[str, list[str]]:
    """按 frontmatter name 归组所有 skill 目录（排除 .archive）。"""
    byname: dict[str, list[str]] = defaultdict(list)
    if not os.path.isdir(root):
        return byname
    for dp, _dns, fns in os.walk(root):
        if ARCHIVE_MARK in dp:
            continue
        if "SKILL.md" in fns:
            key = fm_name(os.path.join(dp, "SKILL.md")) or os.path.basename(dp)
            byname[key].append(dp)
    return byname


def loaded_path(skill_key: str) -> str | None:
    """用 scan_skill_commands() 实测真正加载的那份（唯一可靠方法）。"""
    try:
        from agent.skill_commands import scan_skill_commands  # type: ignore
    except Exception as exc:  # 不在 hermes repo/venv 下时降级
        print(f"  (无法 import scan_skill_commands: {exc})", file=sys.stderr)
        return None
    cmds = scan_skill_commands()
    entry = cmds.get(skill_key) or cmds.get(skill_key.lstrip("/"))
    return (entry or {}).get("skill_md_path")


def report(root: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    byname = collect(root)
    dups = {n: ps for n, ps in byname.items() if len(ps) > 1}
    consistent, conflict = {}, {}
    for name, paths in dups.items():
        if len({md5f(os.path.join(p, "SKILL.md")) for p in paths}) == 1:
            consistent[name] = paths
        else:
            conflict[name] = paths

    print(f"扫描根目录 : {root}")
    print(f"唯一 skill : {len(byname)}")
    print(f"重名组     : {len(dups)}  (= 内容一致 {len(consistent)} + 真冲突 {len(conflict)})")
    if conflict:
        print("\n[真冲突] 内容不一致的重名组 —— 两个不同 skill 撞名，需人工改名，脚本不会动：")
        for name in sorted(conflict):
            print(f"  {name}")
            for p in sorted(conflict[name]):
                print(f"      {md5f(os.path.join(p, 'SKILL.md'))}  {p.replace(root, '~')}")
    return dups, consistent


def apply_dedupe(root: str, consistent: dict[str, list[str]], hd: str, dry: bool) -> None:
    if not dry and not os.path.isdir(BACKUP_DIR):
        sys.exit(f"拒绝执行：先备份。mkdir -p {BACKUP_DIR} && "
                 f"tar czf {BACKUP_DIR}/skills-full-$(date +%Y%m%d-%H%M%S).tar.gz -C ~/.hermes skills")

    del_local = del_hd = 0
    for name in sorted(consistent):
        paths = consistent[name]
        keep = max(paths, key=lambda x: x.count(os.sep))  # 最深 = skilllib 托管的嵌套版
        for p in paths:
            if p == keep:
                continue
            rel = os.path.relpath(p, root)
            print(f"  [{'DRY' if dry else 'DEL'}] {name:42s} {p.replace(root, '~')}")
            if not dry:
                shutil.rmtree(p, ignore_errors=True)
                del_local += 1
            # 镜像到 hermes-data，否则 rsync -a 会把它还原回来 → 遮蔽复发
            hp = os.path.join(hd, rel)
            if os.path.isdir(hp):
                print(f"        [{'DRY' if dry else 'DEL'}] hermes-data → {rel}")
                if not dry:
                    shutil.rmtree(hp, ignore_errors=True)
                    del_hd += 1
        print(f"        保留: {keep.replace(root, '~')}")

    print(f"\n{'[DRY-RUN] 将删除' if dry else '已删除'}: 本机 {del_local} 份 / hermes-data {del_hd} 份")


def main() -> None:
    ap = argparse.ArgumentParser(description="同名多副本扫描/去重（默认只读）")
    ap.add_argument("--root", default=ROOT, help=f"本机 skills 根目录（默认 {ROOT}）")
    ap.add_argument("--hermes-data", default=HD, help=f"hermes-data skills 目录（默认 {HD}）")
    ap.add_argument("--apply", action="store_true", help="真正执行删除（默认只报告）")
    ap.add_argument("--check-loaded", metavar="SKILL", help="只查某个 skill 的实际加载路径后退出")
    args = ap.parse_args()

    if args.check_loaded:
        print(loaded_path(args.check_loaded) or "(未找到)")
        return

    _dups, consistent = report(args.root)
    if consistent:
        apply_dedupe(args.root, consistent, args.hermes_data, dry=not args.apply)
    else:
        print("\n无「内容一致」的重名组，无需去重。")

    print("\n复核提示：改完后重跑本脚本（重名组数应下降），"
          "并用 --check-loaded 确认改过的 skill 仍加载预期版本。")


if __name__ == "__main__":
    main()
