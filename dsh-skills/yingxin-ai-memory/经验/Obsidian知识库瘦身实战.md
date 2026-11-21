---
创作日期: 2026-08-31
作者: Hermes
标签: [运维, 经验, 知识库维护, git, 瘦身]
---

# Obsidian 知识库瘦身实战经验（2026-08-31）

## 背景
用户想「把 obsidian 所有文件转 md 让容量更小、更便于 AI 读取」，装完 markitdown(mdconv) 后顺带清理垃圾库。发现真正占空间的大头根本不是正文格式，而是 git 历史垃圾与图片。

## 关键认知（最先记住的三条）
1. **md 转 md 是白干**：库内 1100 个文件几乎全是 md，本来就最优，"转 md 省容量"不成立。真正胖的是图片 + git 历史，转 md 动不了它们。
2. **markitdown 的正确定位**：把「外部甩来的 PDF/Word/Excel/扫描件」一次性提成文字送进知识库，不是"批量重排已有笔记"。
3. **判断"总能瘦身"先做数据查证**：别猜，直接统计扩展名分布 + 大文件 TOP + .git 目录构成。

## 实测的命令（可直接复用）
```bash
# 1. 库内各扩展名数量（看是不是全是md）
find /mnt/d/obsidian-vault -type f | sed 's/.*\.//' | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn | head -30

# 2. 总大小 + 图片占用
du -sh /mnt/d/obsidian-vault
du -ch $(find . -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.gif' \)) | tail -1

# 3. 前15大文件（揪出 git 历史对象 / LFS 大块头）
find . -type f -printf '%s\t%p\n' | sort -rn | head -15 | awk -F'\t' '{printf "%.1fMB\t%s\n",$1/1048576,$2}'

# 4. 各 .git* 目录大小（损坏副本常以 .git.broken-* 命名）
du -sh /mnt/d/obsidian-vault/.git*

# 5. 确认 .git.broken 是无用副本再删（当前用的 .git HEAD 能解析 = 正常）
git -C /mnt/d/obsidian-vault rev-parse HEAD   # 有输出=当前git健康
```

## 本次结果
- 删掉 `.git.broken-20260809`（963M 损坏旧 git 历史副本）→ 库 1.2G → 211M，腾出约 1.0G。
- 余下 211M = .git 正常历史 95M（在用引擎，勿动）+ 图片 98M + 正文（很小），都合理。
- obsidian 库（ClewBible）每次更新后跑 obsidian_sync.sh 同步。

## 教训 / 边界
- **别对 `_AI-Private/` 各助手私藏区越权操作**，只清理用户明确点名/明显垃圾的东西。
- git 历史对象 pack 文件是有效历史，不要随便 gc/filter-branch 清（本机 git 引擎靠它工作），除非明确要重写历史。
- 清理前先判断"是否还有引用"：能 rev-parse HEAD 的当前 .git 是活的；带 .broken/timestamp 后缀的通常是废弃副本。