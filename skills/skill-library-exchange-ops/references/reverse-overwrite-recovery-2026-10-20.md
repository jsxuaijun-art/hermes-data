# 本机 skill 改动被覆盖事件实录 + 恢复脚本（2026-10-20）

> **根因已二次修正**：首轮把覆盖归因于 `skill-exchange` cron 的 `install`，深挖后证明**错误**。真凶是 hermes-data **拉取脚本的 `rsync -a`**。下文时间线保留原样，末尾「根因修正」给出证据与判定法。

## 事件时间线

1. 本 session 改了 5 个本机 skill 源文件并验证 md5（wechat-publish 双副本、social-media/short-video-copywriting、creative/de-ai-copywriting、productivity/wechat-moments-marketing）。
2. 复制到 skill-library（canonical），md5 一致，commit+push（skill-library remote `f658aa1`）。
3. `bash ~/.hermes/sync-push.sh` 推 hermes-data。
4. 核验时发现本机 5 个源文件全部变回旧版（去AI味标记计数 0、**mtime 回退 10-16**）。
5. 首轮排查：无 curator/sync 进程在跑 → 查 `hermes cron` → 发现 `skill-exchange` 今天 09:50 补跑过 → **误判**为它反向覆盖。
6. 正确版本仍在 skill-library（a100a27b 等）且已 push；hermes-data 里已是旧版（sync-push 运行时本机已旧）。

## ★ 根因修正（2026-10-20 二次深挖）

**被证伪的假设**：`skilllib.py install` 反向覆盖本机。
证伪证据：
- 代码逻辑（install：本机文件与 lib 不同且未加 `--force` → **SKIP，报 conflict，不覆盖**）。注意必须确认不是 `--force` 调用。
- 09:50 的 exchange 日志实测 `wrote 16 new | 24 conflicts(SKIP)` —— 只新增，冲突全 SKIP。

**真凶**：hermes-data 的**拉取路径**用 rsync 把 GitHub 版本覆盖回本机。
- `devops/hermes-data-sync/scripts/hermes_pull.sh` 第 38 行：`rsync -a "$HERMES_SYNC_DIR"/skills/ ~/.hermes/skills/`
- `~/.hermes/sync-pull.sh` 第 21 行：`cp -rf skills/* /home/administrator/.hermes/skills/`（同理覆盖）
- `rsync -a` 保留源文件的 mtime → 本机文件 mtime 被"还原"成旧日期，这就是 mtime 回退的原因。

**判定要点（一句话区分）**：
- mtime 被还原成旧日期 = 拉取脚本 `rsync -a`/`cp -r` 覆盖（保留 mtime）。
- 只有新 skill 被写入、已有冲突全 SKIP = install。

**若 cron/拉取脚本会覆盖本机已改文件 → 预防**：改完当轮推 canonical + hermes-data；本机 `~/.hermes/skills/` 不是持久存储。

## 判定要点（别走弯路）

- 本机源被还原 ≠ 灾难：canonical 和 git remote 才是权威，正确版本都在。
- `author: Hermes Agent` 在 SKILL.md frontmatter ≠ curator-managed。`hermes-data-sync`、`cron-job-ops`、`wsl-hermes-env`、`skill-library-consolidation` 全是 created_by=None → autonomous 写入被拒。要改需 `hermes curator adopt <name>`（用户层面）。
- hermes-data 仓库里同名 skill 有多个副本：扁平 `skills/<名>`、嵌套 `skills/<类>/<名>`、`.archive/`。**只有嵌套路径是活动路径**。别拿扁平/归档副本的旧 md5 误判"同步失败"。

## 恢复脚本（from-canonical）

```python
import shutil, hashlib, os
def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()

lib = "/mnt/c/Users/Administrator/skill-library/skills"
mapping = {
  "wechat-publish/SKILL.md": [
    "/home/administrator/.hermes/skills/wechat-publish/SKILL.md",
    "/home/administrator/.hermes/skills/skills/wechat-publish/SKILL.md",   # 双层副本
  ],
  "short-video-copywriting/SKILL.md": [
    "/home/administrator/.hermes/skills/social-media/short-video-copywriting/SKILL.md",
  ],
  "de-ai-copywriting/SKILL.md": [
    "/home/administrator/.hermes/skills/creative/de-ai-copywriting/SKILL.md",
  ],
  "wechat-moments-marketing/SKILL.md": [
    "/home/administrator/.hermes/skills/productivity/wechat-moments-marketing/SKILL.md",
  ],
}
for rel, dsts in mapping.items():
    src = os.path.join(lib, rel)
    for dst in dsts:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
# 然后逐份 md5(lib) == md5(dst) 验证
```

## 恢复后重推

首次 `bash ~/.hermes/sync-push.sh` 已经把「还原后的旧版」推进了 hermes-data → **必须重跑一次**让正确版本补上。跑完核验：

- hermes-data 仓库里每个改过的 skill 嵌套活动路径 md5 == canonical。
- `cd /mnt/c/Users/Admin/hermes-sync && git status -sb` → `## main...origin/main`（无 ahead/behind）。
- `cd /mnt/c/Users/Administrator/skill-library && git status -sb` → 同上。
- 扁平/归档旧副本（如 `skills/short-video-copywriting`、`skills/.archive/...`）是历史残留，不一致不处理。

## 本次改过的 4 个 skill 的正确版本 md5（活动路径）

| skill | canonical md5 |
|---|---|
| wechat-publish（含 skills/wechat-publish 双层） | dc5a80ec |
| social-media/short-video-copywriting | 4d73f13c |
| creative/de-ai-copywriting | a100a27b |
| productivity/wechat-moments-marketing | 50832a43 |

> 这些 md5 只对本次 2026-10-20「去AI味」改动有效，后续任何编辑都会变——不要当永久断言，只作核验参考。
