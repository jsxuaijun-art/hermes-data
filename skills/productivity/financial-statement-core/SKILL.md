---
name: financial-statement-core
description: 统一财务报表读取底座：科目余额表/三大报表 → 标准化JSON，一处读表口径、全 skill 复用。
version: 1.0.0
author: 徐爱军（jsxuaijun-art）
agent_created: true
license: Proprietary
tags: [财务, 报表, 科目余额表, 资产负债表, openpyxl, xlrd, 共享底座]
category: productivity
---

# 财务报表读取共享底座 Skill

**只做「读表取数」，不做业务分析、不做脱敏。** 把「文件 → 标准化科目/报表数据」这一层
从各业务 skill（注销 / 财报分析 / 格式转换 / 股权转让 / 科目合并）抽出来，统一口径、
一处修复处处生效。业务分析逻辑（雷区 / 对标 / 转换 / 净资产）留在各 skill 自己。

## When to Use
- 调用方需要读一份 科目余额表 / 资产负债表 / 利润表，并把行换成统一的结构。
- 想让多个财务类 skill 用**同一套读数口径**（期末取尾、双栏取 C/G、跳过现金流量表），避免各自实现导致口径漂移。
- 遇到「读数异常」（如注销引擎报资产 585 万但报表只有 74 万）时，先怀疑读数口径，回到本底座核对。

## 统一口径（铁律，全部来自 qingshui_risk_engine 实盘踩坑）
1. **科目余额表**：借贷列从**子行**识别；期末取【最后一组】借方/贷方（覆盖式取尾），第一组为**期初**——防止把期初误读成期末。
2. **资产负债表双栏** [A名称|B行次|C期末|D年初][E名称|F行次|G期末|H年初]：只读 **C/G（期末）**；**不取「最后非零数字列」**（会误中年初 H）。
3. **现金流量表 sheet 一律跳过**（行名会误匹雷区/风险关键词）。
4. 科目余额表**顶层科目 = 科目编码 4 位**者。
5. `totals`（资产/负债/权益）取资产负债表「资产总计/负债合计/所有者权益合计」权威值；**排除「负债和所有者权益总计」**（它是合计，不是权益）。
6. 文件/表结构自动识别：文件名含「科目余额表」，或表头含「科目名称/编码 + 借方/贷方子行」→ 判科目余额表；否则按财务报表解析。

## Prerequisites
- `openpyxl`（.xlsx）、`xlrd`（.xls）。两者都缺时：.xls 读不了、.xlsx 读不了——报错提示安装。
- 读表层**不做脱敏**；脱敏由各业务处理层负责。

## How to Run
```bash
python3 scripts/fs_reader.py --input <文件.xlsx|.xls> [--output out.json] \
        [--period end|begin|both] [--print-rows]
```
- 默认 `--period end`（期末）。
- `--print-rows`：只打印行列结构排查用（不输出正式 JSON）。
- 输出：标准化 JSON，含 `subject_balance`（科目余额表）与 `statement.balance_sheet/income_statement`（财务报表）、`totals`（权威总额）。

## 如何被其它 skill 引用（跨工具路径解析）
四工具（Hermes/Claude/Codex/WorkBuddy）各自有独立 skills 目录、无共享 Python 路径，
所以**不要 `import`**，而用「子进程调用 fs_reader.py + 消费 JSON」或「sys.path 指向本底座脚本目录」。
推荐子进程方式（与 agent 调脚本一致、解耦）：
```python
import subprocess, json, sys, os
def _find_fs_reader():
    env = os.environ.get("FS_READER"); 
    if env and os.path.isfile(env): return env
    here = os.path.dirname(os.path.abspath(__file__))
    for anc in [here, *__import__("pathlib").Path(here).parents]:
        c = os.path.join(str(anc), "financial-statement-core", "scripts", "fs_reader.py")
        if os.path.isfile(c): return c
    raise FileNotFoundError("未找到 financial-statement-core/scripts/fs_reader.py")
def read_report(path):
    fs = _find_fs_reader()
    out = subprocess.run([sys.executable, fs, "--input", path], capture_output=True, text=True)
    if out.returncode != 0: raise RuntimeError(out.stderr)
    return json.loads(out.stdout)
```
> 也可设环境变量 `FS_READER=/path/to/fs_reader.py` 免搜索。

## 消费字段速查
| 需要什么 | 读哪里 |
|---|---|
| 科目余额表 顶层科目净值 | `subject_balance.subjects_top`（dict 名→期末借贷净值） |
| 科目明细（编码/借贷/净值） | `subject_balance.detail[]` |
| 资产负债表期末各项 | `statement.balance_sheet.end` |
| 利润表本年累计 | `statement.income_statement.annual` |
| 权威总额（清税/净资产） | `totals.{assets,liabilities,equity}` |
| 读取告警（跳过现金流量表等） | `warnings[]` |

## Quick Reference
- 已踩坑与边界：`references/parsing-pitfalls.md`
- 科目编码→标准名/借贷方向/类别 口径字典：`references/subject-mapping.md`

## Verification
用一份真实/合成的科目余额表 + 资产负债表(xlsx/xls) 跑 `fs_reader.py`，核对：
1. 科目余额表：`subjects_top` 的期末值 = 最后一组借贷列（不是期初）。
2. 资产负债表：`statement.balance_sheet.end` 的数值来自 C/G（期末），且右栏负债权益项不缺失。
3. `totals` 的 equity 是「所有者权益合计」而非「负债和所有者权益总计」。
4. 现金流量表 sheet 出现在 `source.sheets_skipped`。
