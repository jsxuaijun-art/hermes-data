# 同名多副本「字母序遮蔽」实测与批量修复（2026-10-20）

## 背景

上一轮给 4 个 skill 接入「交付前去 AI 味」流程、同步 canonical 并推送双通道后，
发现本机 `~/.hermes/skills/creative/de-ai-copywriting/SKILL.md` 的新增章节「消失」。
初判为 skill-exchange cron 反向覆盖，深挖后**推翻了该结论**，真正问题是**加载遮蔽**。

## 决定性代码证据

`agent/skill_commands.py`：

```python
def iter_skill_index_files(root: Path) -> Iterator[Path]:
    ...
    for path in sorted(matches):      # ← 字典序排序
        yield Path(path)

def scan_skill_commands():
    seen_names = set()
    for index_file in iter_skill_index_files(root):
        name = ...                     # frontmatter name
        if name in seen_names:
            continue                   # ← 同名只取先遍历到的（即字母序最小）
        seen_names.add(name)
```

结论：**同名 skill 的胜负 = 路径字典序**。与 mtime、是否"分类嵌套"、是否 skilllib 管理**全都无关**。

（`skills/` 这一层**不在**排除目录里，所以 `~/.hermes/skills/skills/wechat-publish` 也会被扫到。）

## 全库实测数据

- `~/.hermes/skills/` 下 SKILL.md 总数：512 份目录 / 407 个唯一 name
- **同名多副本：95 个 skill**
- **内容不一致（md5 不同）：28 个**
- **「实际加载 != 最新版」：约 20 个**（批量修复处理了 19 个）

用户业务关键 skill 中招 **11 个**（加载的都是顶层扁平旧版，mtime 10-12；正确版在嵌套目录，mtime 10-16）：

```
client-group-welcome        client-group-welcome/          vs  marketing/
corporate-tax-planning      corporate-tax-planning/        vs  tax-planning/
coze-tax-agent-prompt       coze-tax-agent-prompt/         vs  skills/reference-material-integration/
english-learning            english-learning/              vs  productivity/
financial-mini-program      financial-mini-program/        vs  productivity/
generate-docx-without-python-docx  <flat>                 vs  productivity/
manager-xu-business-registration   <flat>                  vs  social-media/
markdown-to-word-converter  <flat>                         vs  productivity/
memory-management           <flat>                         vs  productivity/
short-video-ad              <flat>                         vs  social-media/
short-video-general         <flat>                         vs  social-media/
```

外加 `short-video-copywriting`（`short-` < `social-media/`，h<o，扁平旧版胜出）——
**上一轮加进嵌套版的「去 AI 味」章节从未被加载过**。

反例（扁平版字母序**更大**，嵌套版胜出 → 正常）：
`wechat-publish`（`w`>`s`，`skills/wechat-publish` 赢）、
`wechat-moments-marketing`（`productivity/` 赢）、`de-ai-copywriting`（`creative/` 赢）。

## 批量修复脚本（非破坏）

```python
import os, shutil, hashlib, time
from collections import defaultdict
ROOT="/home/administrator/.hermes/skills"
HD  ="/mnt/c/Users/Admin/hermes-sync/skills"
LIB ="/mnt/c/Users/Administrator/skill-library/skills"
BK  ="/home/administrator/skill-dupes-backup/"+time.strftime("%Y%m%d-%H%M%S")  # 必须在 skills/ 之外!

def md5(p):
    try: return hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
    except: return None
def mt(p):
    try: return os.path.getmtime(p)
    except: return 0

copies=defaultdict(list)
for dp,_,fn in os.walk(ROOT):
    if any(x in {'.git','.hub','.archive','.venv','venv','node_modules','__pycache__'} for x in dp.split(os.sep)):
        continue
    if "SKILL.md" in fn: copies[os.path.basename(dp)].append(os.path.join(dp,"SKILL.md"))

os.makedirs(BK, exist_ok=True)
for n, paths in sorted(copies.items()):
    if len(paths)<2 or len(set(md5(p) for p in paths))==1: continue
    win    = sorted(paths)[0]                 # 实际加载的那份
    newest = max(paths, key=mt)               # 最新内容
    if md5(win)==md5(newest): continue
    dstbk=os.path.join(BK,n,"SKILL.md"); os.makedirs(os.path.dirname(dstbk),exist_ok=True)
    shutil.copyfile(win,dstbk)                # 备份旧加载版
    for t in (win, os.path.join(HD,n,"SKILL.md"), os.path.join(LIB,n,"SKILL.md")):
        if os.path.exists(os.path.dirname(t)): shutil.copyfile(newest,t)
```

## 复核（必做，勿只信文件系统）

```python
import os, sys
os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))
sys.path.insert(0, "<repo>")           # 用 <repo>/venv/bin/python 跑
from agent.skill_commands import scan_skill_commands
c = scan_skill_commands()
for n in [...]:
    print(n, c["/"+n]["skill_md_path"])
```

修复后实测：11 个业务 skill 的活动路径全部指向最新版且与 canonical md5 一致；
`short-video-copywriting` 加载版含「去 AI 味」✅。

## 收尾

- 备份：`~/skill-dupes-backup/<时间戳>/`（19 份，260K）
- 双通道推送并核验 `local==origin/main`：skill-library commit `fix: 同步canonical至最新版(消除同名副本遮蔽) + 短视去AI味`、hermes-data 走 `~/.hermes/sync-push.sh`。

## 未处理（需用户定夺）

27 个「互有增减」的真冲突副本（两版各有独有内容，非单纯新旧），**不可自动合并**（会丢内容）：
`github`、`geo-optimization`、`research-*`、`axolotl`/`unsloth`/`trl-fine-tuning`、
`yingxin-business-suite`、`workbuddy-output` 等；另 `hermes-upgrade`、`memory-management`
在 canonical 里无对应条目。

根治方案：消除双份并存（以 canonical 为准清掉扁平遗留副本，保留备份），需用户批准。
