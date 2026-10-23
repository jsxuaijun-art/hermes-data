# 同名多副本去重实录（2026-10-20）

本文记录「字母序遮蔽」的**根治过程**、**首轮失败复盘**与最终实测数据。
配套脚本：`scripts/scan_same_name_copies.py`（默认只读，`--apply` 才删）。

---

## 1. 触发链（这个 skill 为什么存在）

1. 给 4 个写作类 skill 加了「交付前去AI味」环节（`wechat-publish` / `short-video-copywriting` /
   `wechat-moments-marketing` / `de-ai-copywriting`）。
2. 本机文件随后**被还原成旧版**（连 mtime 都退回），一度归因于 `skill-exchange` cron。
3. 深挖后发现归因错误：`skilllib.py install` 是**非破坏性**的（冲突 SKIP 不覆盖，日志
   `wrote 16 new | 24 conflicts(SKIP)`）。真正覆盖本机的是 **hermes-data 拉取脚本的 `rsync -a`**。
4. 进一步发现更狠的问题：**改的那份根本没被加载**。

## 2. 决定性发现：同名副本按路径字母序取第一份加载

```
agent/skill_commands.py
  iter_skill_index_files():  ... for path in sorted(matches): yield Path(path)
  scan_skill_commands():     if name in seen_names: continue
```

* 谁路径字典序小谁胜出。
* 顶层扁平 `~/.hermes/skills/<名>/` vs 分类嵌套 `~/.hermes/skills/<类>/<名>/` 并存时，
  扁平版常胜（`short-video-copywriting` < `social-media/short-video-copywriting`，`h` < `o`）。
* 实测后果：`/short-video-copywriting` 长期加载**扁平旧版**，改嵌套版等于白改。

全库实测：**94 组同名多副本**（按 frontmatter name），其中 **28 组内容不一致**，
**11 个业务 skill 实际加载的是旧版**。

## 3. 首轮失败的错在哪（务必别再犯）

首轮按 **目录名** 匹配做统一，三重错误：

| 错误 | 后果 |
|---|---|
| 用目录名当匹配键 | 目录名 ≠ 技能名真实存在（`agent-prompts/` 里装的是 `coze-tax-agent-prompt`）→ **错配文件、覆盖无关技能** |
| 没排除 `.archive/` | 改到 curator 归档副本（本不该动） |
| 覆盖面失控 | 报「175 个」大改，实际多数不需要动 |

**处置**：用动作前的全量 tar 备份**整体回滚**，改按 frontmatter `name:` 重做。

教训：**匹配键只能是 frontmatter `name:`（fallback 目录名），并排除 `.archive/`。**

## 4. 第二轮（成功）流程

```
① 全量备份
   tar czf ~/skill-dupes-backup/skills-full-20261020-120024.tar.gz -C ~/.hermes skills   # 838M
② 按 frontmatter name 归组，排除 .archive
   → 94 组重名；其中 90 组「内容完全一致」（可安全去重）、4 组「真冲突」（不动）
③ 先统一内容：以 canonical(skill-library) 覆盖各副本  → 7 组差异被修正（其余此前已一致）
④ 去重：每组保留路径最深的一份，删除其余
   → 删本机 88 份 + hermes-data 88 份（必须镜像，否则 rsync -a 还原 → 复发）
⑤ 验证：重名组 94 → 4；scan_skill_commands() 复核加载版含标志串「去AI味」
⑥ 推送：sync-push.sh（hermes-data）；skill-library 本轮无改动
```

### 为什么保留「路径最深」的那份

`skilllib.py install` 把 skill 装到 `~/.hermes/skills/<分类>/<名>`（**嵌套**），
**不写顶层扁平**。所以只有嵌套版能被 skilllib 重建与维持 —— 保留嵌套版才持久。
（注意：canonical `skill-library` 自身是扁平结构 `skills/<名>`，那是**库的存储形态**，
不代表本机加载形态。别把两者混为一谈。）

## 5. 最终实测数据

| 项 | 值 |
|---|---|
| 去重前重名组 | 94 |
| 去重后重名组 | **4**（全为真冲突） |
| 删除副本 | 本机 88 + hermes-data 88 |
| 全库唯一 skill | 396 |
| 双通道 | skill-library ✅ / hermes-data ✅，local==origin |

### 剩余 4 组真冲突（需人工改名，脚本不动）

| 组 | 情况 | 建议 |
|---|---|---|
| `research` | `deep-research/research`(中文) vs `research-en/research`(英文) | 英文版改名 `research-en` |
| `research-report` | 同上 | 同上 |
| `coze-tax-agent-prompt` | `coze-agent-engineering/agent-prompts/` 的 frontmatter name 撞名（canonical 里同样存在） | 修 `agent-prompts` 的 frontmatter name |
| `hermes-upgrade` | 不在 canonical 库 | 补进库或改名 |

## 6. 复核命令片段

```python
# 实际加载路径（唯一可靠判据）
import os; os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))
from agent.skill_commands import scan_skill_commands
c = scan_skill_commands()
p = c["/short-video-copywriting"]["skill_md_path"]
print(p, "去AI味" in open(p, encoding="utf-8").read())
```

```bash
# 备份目录绝不可放在 ~/.hermes/skills/ 内（含 SKILL.md 会被当新 skill 扫到）
ls -d ~/skill-dupes-backup/skills-full-*.tar.gz
```
