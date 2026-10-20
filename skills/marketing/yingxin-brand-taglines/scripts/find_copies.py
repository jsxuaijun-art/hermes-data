#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定点盘点某个文件在各"副本根"下的分布：路径 + md5 + CRLF + 字节数。

用法:
    python3 find_copies.py canonical-identity-anchor.md
    python3 find_copies.py 03-产品手册.md

为什么需要它:
    这类人设/品牌文件在四个根下有多份副本（实测 canonical-identity-anchor.md
    高达 9 份）。凭记忆数副本 → 同步时改漏，且 md5 只有全量比对才暴露。
    全盘 find / 扫 / 太慢（超过工具超时，且 /mnt/d 的缓存目录噪音大），
    所以只扫四个实测收敛根。

判读:
    - 同 md5 分组；出现多组 = 存在"有意差异"（如 sales 版专属段）或漂移。
    - 有意差异要保留；漂移先 diff 确认再动手：
        diff <(tr -d '\r' < A) <(tr -d '\r' < B)     # 源文件常为 CRLF
"""
import hashlib
import sys
from pathlib import Path

ROOTS = [
    "/home/administrator/.hermes/skills",
    "/mnt/c/Users/Administrator/skill-library/skills",
    "/mnt/c/Users/Admin/hermes-sync/skills",
    "/mnt/d/obsidian-vault/_AI-Private/Hermes-Only/skills",
]


def find(name: str):
    hits = []
    for root in ROOTS:
        r = Path(root)
        if not r.exists():
            print("  (根不存在，跳过) %s" % root, file=sys.stderr)
            continue
        try:
            hits.extend(p for p in r.rglob(name) if p.is_file())
        except OSError as exc:  # 权限/IO 异常不要中断整轮盘点
            print("  (扫描失败 %s: %s)" % (root, exc), file=sys.stderr)
    return sorted(hits)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    name = sys.argv[1]
    hits = find(name)
    if not hits:
        print("未找到 %s（确认文件名，或该文件尚未落到四根之中）" % name)
        return 1

    groups = {}
    print("%-34s %-5s %8s  %s" % ("md5", "CRLF", "bytes", "path"))
    for p in hits:
        b = p.read_bytes()
        h = hashlib.md5(b).hexdigest()
        eol = "CRLF" if b"\r\n" in b else "LF"
        groups.setdefault(h, []).append(p)
        print("%-34s %-5s %8d  %s" % (h, eol, len(b), p))

    print("\n共 %d 份，%d 组不同内容:" % (len(hits), len(groups)))
    for h, ps in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print("  %s  x%d" % (h, len(ps)))
        for p in ps:
            print("      %s" % p)

    if len(groups) > 1:
        print(
            "\n[!] 存在内容差异：若属「有意差异」（如 sales 版专属反挂靠段）则保留；"
            "否则先 diff 确认再动手。改完必须重跑本脚本核对收敛：\n"
            "    同组内应全同；有意差异组之间应保持不同。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
