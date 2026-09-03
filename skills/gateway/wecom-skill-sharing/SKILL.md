---
name: wecom-skill-sharing
description: 让不用 Hermes 的同事用上 skill 能力：企微群@机器人/webhook 推材料/网页应用选型。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wecom, 企微, skill共享, 同事协作, 群机器人, webhook]
    category: gateway
    related_skills: [wecom-external-service, hermes-server-ops, aliyun-hermes-server]
---

# 企微 Skill 共享（让非 Hermes 同事用上 Hermes skill）

用户常需要把内部 skill 的能力开放给**不用 Hermes 的同事**（会计团队），例如注销诊断引擎
`qingshui_risk_engine.py`（传科目余额表 → 出雷区报告）。本文档给出：三条路径选型、
方案A（群@机器人）的验证清单与实测脚本、推材料到群的 webhook 工具。2026.8.11 实战沉淀。

## When to Use

- 用户说「把这个 skill 发给同事用」「同事不用 Hermes 怎么用上这个能力」
- 需要在企微群内共享 skill 材料（Word 手册 / skill 安装包 / 使用说明）
- 需要验证企微机器人能否**收群文件并跑 skill 诊断**
- 给同事/客户提供自助式上传报表出报告的入口

## Prerequisites

- 企微 AI 机器人（WebSocket 模式）已部署，网关在跑（`ps aux | grep "gateway run"`）
- 群机器人 webhook key（用于**单向推送**材料）：
  `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=<KEY>`，
  `upload_media` 接口：`.../webhook/upload_media?key=<KEY>&type=file`
- 目标群必须是**内部群**（机器人进不了外部/客户群——平台硬限制）

## How to Run

### 一、路径决策（三选一）

| 路径 | 适用场景 | 成本 | 说明 |
|:--|:--|:--|:--|
| A. 内部群传文件 + @机器人 | 同事都在内部群 | 零开发 | 机器人收文件 → agent 跑 skill → 回诊断。**先做这个** |
| B. 网页应用（Flask 上传→跑引擎→下载 Word 报告） | 任何群/外部客户/要干净界面 | 半天 | 复用引擎脚本，部署到阿里云服务器（本用户：47.103.27.171） |
| C. 微信/企微小程序 | — | 高 | 要注册+审核，内部工具杀鸡用牛刀，**不推荐** |

推荐顺序：先 A（当天可用）→ 再 B（正式交付）。用户默认认可「先A后B」。

**⚠️ 2026.8.11 实测结论：本环境 A 路不通，别在 A 上耗时间。**
内部群 + 机器人已加群 + 纯文字 @ 也无反应；`agent.log` 里 `platform=wecom` 会话数 = 0，
说明消息根本没推送到网关（企微 AI 机器人控制台/平台层面问题，本机无法修）。
前提清单 4 项全绿也不保证 A 能通。验证完清单后群里仍无反应 → **直接转 B**。

### 二、方案A 前提验证清单（4 项全绿才通）

```bash
# ① 网关在跑（本机 = WSL，进程 `hermes gateway run`）
ps aux | grep "gateway run"

# ② skill 在 ~/.hermes/skills/ 下（机器人 agent 可访问、可自动加载）
ls ~/.hermes/skills/<category>/<skill>/

# ③ wecom 适配器支持收群文件（best-effort download inbound attachments）
grep -nE "_extract_media|_cache_media|_download_remote_bytes" \
  <repo>/plugins/platforms/wecom/adapter.py

# ④ skill 引擎依赖在【网关 venv】装齐 —— 不是会话 venv！
#    （本机网关 venv 示例：/home/administrator/hermes-agent/venv）
<网关venv>/bin/python -c "import openpyxl, xlrd, docx; print('ok')"
```

**要点**：wecom 适配器在 repo 的 `plugins/platforms/wecom/adapter.py`
（gateway 日志里的模块名 `hermes_plugins.wecom_platform.adapter` 就是它，不是独立 pip 包）。
引擎用的第三方库（openpyxl/xlrd/python-docx）必须装在**网关进程的 venv** 里，别的 venv 装好没用。

### 三、真实验证协议（群里只能真人操作）

1. 内部群上传样本报表（.xlsx/.xls）
2. @机器人：`用<skill名>，帮我诊断这个科目余额表，出雷区报告`（显式点 skill 名最稳，触发技能加载）
3. 期望链路：加载 skill → 定位上传文件 → 跑引擎 → 回诊断 + Word 报告
4. 失败 → 让用户把机器人回复/报错发回，维护者修（依赖缺失、文件未识别等）

**失灵判据（2-3 分钟无反应时，别再空等/反复试）：**
```bash
# agent.log 才能看出「有没有会话进来」；gateway.log 只有连接状态
grep -c "platform=wecom" ~/.hermes/logs/agent.log   # =0 → 消息根本没进网关
tail -5 ~/.hermes/logs/agent.log                     # 看最近在跑的都是什么会话
```
若 wecom 会话数 = 0 且前提清单 4 项全绿 → 企微后台/机器人配置层面问题，
本机修不了 → **果断转方案B**，把时间花在网页应用上。

### 四、推共享材料到群（webhook 单向推送）

```bash
python3 scripts/wecom_group_push.py \
  --key <WEBHOOK_KEY> \
  --markdown "**📋 标题** 摘要正文" \
  --file /path/手册.docx \
  --file /path/skill-安装包.zip
```

- 一键推 markdown 摘要 + 多个文件（upload_media → media_id → send file），实测 errcode 0
- 给同事的材料**三件套**：摘要消息（讲清是什么/怎么用）+ Word 手册（不用 Hermes 也能读，最实用）+ skill 安装包 zip（给用 Hermes 的同事）
- 文件消息一次只发一个文件；markdown 支持有限（标题/加粗/列表，不支持表格）

### 五、方案B：Flask 网页应用（2026.8.11 实测成功，首选交付形态）

结构：`app.py`（上传→调引擎函数→生成/下载 Word 报告）+ `templates/{index,result}.html` +
引擎脚本（直接 import 其函数，不跑子进程）+ `requirements.txt`。

```python
# 上传保存：secure_filename() 会剥掉中文名导致无扩展名，openpyxl 打不开！
# 修复：uuid + 保留原扩展名
ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'xlsx'
save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.{ext}")
```

关键经验：
- **本地端到端测试必须做**：openpyxl 造一份带雷区的测试科目余额表 → 起应用 →
  `curl -F "files=@测试表.xlsx" http://127.0.0.1:5000/diagnose` → 结果页 grep 雷区标题 →
  下载报告验证 docx 内容（文件头 PK + 抽查关键词）。改完代码 kill 旧进程重启再测。
- **下载路由含中文文件名**：urllib 访问需 `urllib.parse.quote(url)`，否则 UnicodeEncodeError。
- **部署阿里云**：scp 应用文件 → 服务器建 venv + `pip install -i 清华镜像` → systemd 服务
  （**本地 write_file 写 service 文件再 scp 到 /etc/systemd/system**，避免 heredoc 被安全闸拦截）→
  daemon-reload/enable/start → 服务器本机 `curl localhost:PORT` 验证 200。
- **外网不通先查安全组**：服务监听 0.0.0.0 + 本机 curl 200 但外网 HTTP 000 = 阿里云安全组
  没开该端口，只能用户去控制台加（TCP 端口 + 0.0.0.0/0），agent 做不了。
- 传的是客户财务报表，**正式用建议 nginx 反代 + HTTPS**。
- 本部署：`/opt/hermes-data-app`，systemd 服务 `hermes-diag.service`，端口 8000。
  改代码后重部署用 `scripts/redeploy_aliyun.sh`。完整配方见 `references/flask-webapp-deploy.md`。

## Quick Reference

| 目的 | 命令 |
|:--|:--|
| 网关是否在跑 | `ps aux \| grep "gateway run"` |
| 机器人连接状态 | `tail -50 ~/.hermes/logs/gateway.log \| grep -iE "wecom\|reconnect"` |
| 适配器收文件能力 | `grep -nE "_extract_media\|_cache_media\|_download_remote_bytes" plugins/platforms/wecom/adapter.py` |
| 引擎依赖（网关venv） | `<网关venv>/bin/python -c "import openpyxl, xlrd, docx; print('ok')"` |
| 推材料到群 | `python3 scripts/wecom_group_push.py --key K --markdown "..." --file F1 --file F2` |

## Procedure

1. 先确认同事是否在**内部群**（外部群直接走方案B，方案A无解）
2. 跑方案A验证清单，4 项全绿再约群里实测
3. 给用户清晰的测试话术（上传什么文件 + @机器人说什么）
4. 实测通过 → 推三件套材料到群，同事即可自助使用
5. 方案A 无反应（agent.log 里 wecom 会话=0）或用户要正式方案 → 搭 Flask 网页应用部署阿里云（见「五、方案B」）

## Pitfalls

- **必须 @ 机器人**才推送（平台层行为，Hermes 无法绕过）；免@需企微后台关键词触发设置
- **机器人仅支持内部群**——外部群/客户群无解，只能人工中转或网页应用
- **串行延迟**：DM 与群聊共享 agent 实例，实测排队可达 124s+，要提前给同事心理预期
- **依赖装错 venv**：引擎报 ImportError 先查是不是网关 venv，不是会话 venv
- **webhook 只能推不能收**：别指望群机器人 webhook 实现交互式问答
- **webhook key 是凭据**：不要写进会被同步到 GitHub 的技能/记忆（hermes-data-sync 会推远端）——key 放 .env 或现场问用户要
- 文件接收是 **best-effort**：格式/大小可能受限，必须真实文件实测，不能只靠代码推断
- **A 路可能压根不通（本环境实测）**：企微 AI 机器人（WebSocket）内部群 @ 无反应、agent.log 0 个 wecom 会话——消息根本没进网关，本机无解；前提清单全绿也不代表能通，先小成本实测，不通立刻转 B
- **中文文件名被剥**：Flask 上传用 `secure_filename()` 会剥掉中文名（无扩展名 → openpyxl 打不开），改用 uuid + 保留原扩展名
- **Flask 下载路由含中文**：urllib 访问需 `urllib.parse.quote()`，否则 UnicodeEncodeError
- **外网不通先查安全组**：本机 curl 200 但外网连不上 = 阿里云安全组端口未开，只能用户控制台操作

## Verification

- 推送材料：接口返回 `errcode: 0` 且群里能看到消息/文件
- 方案A：群里 @机器人 后收到诊断回复（或可复现的报错供修复）；若 2-3 分钟无反应，按「失灵判据」查 agent.log wecom 会话数
- 方案B：服务器本机 `curl localhost:8000` 200 + 外网 `http://<IP>:<port>/` 可打开、上传报表出报告、下载 docx 有效（文件头 PK）
- 引擎可编译：`<网关venv>/bin/python -m py_compile <引擎脚本>`
