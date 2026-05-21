---
name: enterprise-profit-calculator
description: 企业利润计算器 - 适用于小微企业利润核算，支持增值税、附加税、企业所得税自动计算
category: productivity
---

# 企业利润计算器

适用于中小微企业的利润核算 Python 脚本，内置2026年税收政策。

## 功能

- 营业收入、营业成本和各项费用录入
- 增值税自动计算（小规模纳税人/一般纳税人可选）
- 城建税、教育费附加、地方教育费附加计算
- 企业所得税自动计算（适用小型微利5%优惠）
- 输出完整利润报表 + 财务指标（毛利率、净利率、费用收入比、综合税负率）
- 结果自动导出至 profit_report.json

## 内嵌税收政策（2026年）

- **小规模纳税人**：月销售额 ≤ 10万（季度30万）免征增值税
- **小规模纳税人**：超过部分按 1% 征收率（有效期至2027年12月31日）
- **小型微利企业**：年应纳税所得额 ≤ 300万，实际税率 5%（有效期至2027年12月31日）
- **小型微利企业**：年应纳税所得额 > 300万，适用 25% 税率

## 文件结构

- `SKILL.md` — 本文件（技能说明）
- `references/profit_calculator.py` — 利润计算器 Python 脚本

## 使用方法

### 方式一：直接写入桌面文件（首选）

用户说"生成利润计算器"或"我要利润计算脚本"时：

1. 读取 `references/profit_calculator.py` 获取脚本内容
2. 用 `write_file` 写入用户桌面 `profit_calculator.py`
3. 告知用户双击即可运行

### 方式二：手动复制（当 write_file 写盘失败时）

当 `write_file` 工具不可用时（某些受限环境），提供完整的脚本代码文本让用户手动复制粘贴到桌面文件。步骤：

1. 读取 `references/profit_calculator.py` 获取脚本内容
2. 在回复中展示完整代码
3. 指导用户：打开记事本 → 粘贴代码 → 另存为 `profit_calculator.py` 到桌面（编码选 UTF-8）

### 方式三：文件管理器复制已有文件

脚本已保存在 skill 目录中，用户可以：

1. 打开文件资源管理器
2. 地址栏输入 `%USERPROFILE%\.hermes\skills\productivity\enterprise-profit-calculator\references\`
3. 复制 `profit_calculator.py` 到桌面

### 运行

```bash
python profit_calculator.py
```

按提示依次输入收入、成本、费用等数字即可。

### 依赖

Python 3.6+，标准库，无需安装第三方包。

## 注意事项

- 2028年起增值税1%征收率和所得税5%优惠可能变化，需届时更新脚本
- 城建税默认按5%计算（县城/建制镇标准），市区7%需手动改
- 文件中 policy display strings 要和计算逻辑同时更新，保持一致性
