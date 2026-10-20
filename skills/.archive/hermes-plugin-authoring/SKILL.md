---
name: hermes-plugin-authoring
description: 构建 Hermes 用户插件钩子：改写工具结果、启用与验证。
version: 1.0.0
author: 徐爱军（jsxuaijun-art）
license: Proprietary
metadata:
  hermes:
    tags: [hermes, plugin, hooks, development]
    category: devops
    related_skills: [desensitization, hermes-data-sync]
---

# Hermes 用户插件钩子开发 Skill

## 简介

构建/修改/验证 `~/.hermes/plugins/<name>/` 下的用户插件。核心是**钩子选型**：
Hermes 的钩子能力不对称——「改工具结果」只有一个正确位置
（`transform_tool_result`）。本 skill 沉淀 2026-09 实测结论
（`desensitize-read` 读入脱敏插件的完整开发 + 端到端验证）。

> Hermes 插件全量文档/契约见 bundled `hermes-agent` skill 与仓库 `AGENTS.md`；
> 本 skill 只沉淀「实战可用」的速查，不重复官方文档。

## When to Use

- 用户要求「读文件/终端/网页等工具内容进上下文前自动处理」（脱敏/改写/过滤/提醒）
- 需要在工具调用前后挂逻辑、注册新工具或 CLI 子命令
- 排查「插件写了但没生效 / 钩子没触发」

## Prerequisites

- Hermes 源码在 `~/hermes-agent`（读钩子契约、跑验证命令用）
- 插件三要素：`plugin.yaml`（manifest）＋ `__init__.py`（register）
- 用户插件目录：`~/.hermes/plugins/<name>/`

## 钩子选型（最重要的结论，查源码实测）

| 目的 | 钩子 | 说明 |
|---|---|---|
| 改工具**结果**（进上下文前） | `transform_tool_result`（另有 `transform_terminal_output`） | **唯一正解**：返回字符串即替换结果 |
| 改工具**参数** | `pre_tool_call` | 支持 block / approve / modify（改参数） |
| 观察（只读） | `post_tool_call` | **observer，改不了结果**（源码注释明示） |
| 生命周期 | `on_session_start/end`、`pre/post_llm_call` | 触发类事件，不传内容 |

**为什么「读文件前置脱敏」不能靠 `pre_tool_call`**：改参数拿不到 docx/xlsx/pdf
已提取的文本，得自己重新解析（无谓且易错）；`transform_tool_result` 拿到的是
**已提取文本**，直接替换即可。2026-09 实操：`post_tool_call` 已确认只读，改返回
无效；最终选型 `transform_tool_result`。

## 插件结构（最小范例）

```
~/.hermes/plugins/<name>/
├── plugin.yaml      # name/version/description/hooks: [transform_tool_result]
└── __init__.py      # register(ctx)：在 ctx 上注册所选钩子的回调
```

`plugin.yaml` 的 `hooks:` 列表声明会用到的钩子；`__init__.py` 的 `register(ctx)`
在插件加载时执行。注册方法名与签名以 `hermes_cli/plugins.py` 的 PluginContext
为准（进了本会话实测的 `security/desensitization` 对应插件是现成范本）。

## 启用（必踩的坑：用户插件是 opt-in）

1. 目录放进 `~/.hermes/plugins/` 只算「被发现」——**钩子不会注册**（列表里有、
   日志提示 not enabled，但什么都不会跑）。
2. 必须列入 `config.yaml` 的 `plugins.enabled`。正规做法：
   ```bash
   hermes plugins enable <name>      # 写入配置；下次会话生效
   ```
3. 除非要覆盖内置工具，**不要**授予 `--allow-tool-override`（特权；脱敏类插件
   不覆盖内置工具，无需授予）。

## 验证（写完必须真跑，别信"看起来加载了"）

```bash
# ① 钩子是否注册（插件确实加载）——必须 import model_tools 才触发插件发现
cd ~/hermes-agent && python3 -c "
import os; os.environ['HERMES_HOME']=os.path.expanduser('~/.hermes')
import model_tools
from hermes_cli.lifecycle import has_hook
print('hook 已注册:', has_hook('transform_tool_result'))"

# ② 端到端：真调工具，断言返回内容已被处理（脚本见本 skill scripts/）
python3 ~/.hermes/skills/devops/hermes-plugin-authoring/scripts/verify_transform_hook.py
```

② 脚本造含目标模式的临时文件，真走 `model_tools.handle_function_call('read_file', {...})`，
断言：敏感内容已替换、脱敏形式在位、无关数字未被误改。

## 编写要点

- **非阻断**：钩子体 try/except，任何异常原样放行——处理失败绝不卡死主流程。
- **收窄范围**：只处理目标工具名；处理 agent 自身产出（`write_file` / `patch` /
  `skill_manage` 等结果）会自伤。**按数据来源分桶**（2026-09-15 实测，用户定边界
  「只脱敏用户主动发送的信息/文件，agent 抓网页/搜索的公开数据不脱敏」）：目标工具集
  拆成「本地/用户上传类」（read_file / search_files / terminal / execute_code /
  vision_analyze）与「网络抓取类」（web_search / web_extract / browser_*，**不处理**）。
  分桶直接体现在模块级 `_DEFAULT_TARGET_TOOLS` set 里；`DESENSITIZE_READ_TOOLS`
  环境变量可运行时覆盖（每次调用动态读 `os.environ`）。
- **控制成本**：transform 钩子在每次匹配调用都跑，设大小上限（≥2MB 跳过）。
- **结果形态**：`transform_tool_result` 收到的 result 可能是 dict 或 JSON 字符串，
  兼容两种；返回字符串即替换。
- **正则识别固定格式**，词表兜底无格式字段（姓名/公司名依赖上下文或精确词表）。

## Pitfalls

1. **插件写了没生效** → 八成是没启用：`has_hook(...)` 返回 False 时先
   `hermes plugins enable <name>`，**重开会话**后再验。
2. **本会话内别承诺「已生效」**：enable 写配置、**下次会话**才加载；当前会话钩子不活跃。
3. **多机部署**：hooks 插件目录已随 `hermes_push.sh` 同步（2026-09 起含
   `~/.hermes/plugins/`），但每台机要各自 `hermes plugins enable`；本地词表类文件
   （如 `leak-blocklist.txt`，含真实身份）刻意不同步、需各机自建。
4. **别用 `post_tool_call` 改结果**：只观察，改写了也不生效。
5. **别凭记忆写钩子 API**：新增钩子先读 `hermes_cli/plugins.py` /
   `hermes_cli/lifecycle.py` 的真实签名与调用点；`transform_tool_result` 返回
   字符串即替换是实测验证过的契约。
6. **姓名/无格式字段识别有上限**：上下文正则（如 `法定代表人：杨建国`）只认
   「字段名＋冒号」形式；游离出现的姓名要词表兜底，别宣称全覆盖。
7. **改插件源码≠当前会话生效**：`_DEFAULT_TARGET_TOOLS` 这类**模块级常量在插件
   import（进程启动）时定值**，改了源码当前会话仍是旧逻辑，必须**重开会话**才能
   验证；`DESENSITIZE_READ_TOOLS` 等环境变量虽每次调用动态读 `os.environ`，但外部
   改不了已运行进程的环境——结论统一：**插件任何改动（源码/配置）都要新会话才生效**，
   向用户说明时别承诺「本次已生效」。

## Verification

- `has_hook(...)` 探针返回 True
- 端到端脚本断言通过（见「验证」）
- 目标非处理范围内容（金额等）确认未被误改

## 关联

- `security/desensitization`：读入脱敏规则与四类敏感主体定义
- `hermes-data-sync`：推送前 `leak_scan.py` 扫描 + plugins/ 同步清单