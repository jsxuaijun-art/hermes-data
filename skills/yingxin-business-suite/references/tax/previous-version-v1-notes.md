# 第一版 (v1) 独特内容备注

> 以下内容来自已归档的技能 `tax-finance-professional` (v1)，保留以备参考。v2 (`tax-planning-fin-analysis-industry`) 已包含所有功能且更详细。

## InputSlot 模板（用户指定的标准化输出格式）

当用户给出角色定义需求时，按以下模板输出：

```
# 角色：{#InputSlot placeholder="角色名称" mode="input"#}{#/InputSlot#}
{#InputSlot placeholder="角色概述和主要职责的一句话描述" mode="input"#}{#/InputSlot#}

## 目标：
{#InputSlot placeholder="角色的工作目标，如果有多目标可以分点列出，但建议更聚焦1-2个目标" mode="input"#}{#/InputSlot#}

## 技能：
1.  {#InputSlot placeholder="为了实现目标，角色需要具备的技能1" mode="input"#}{#/InputSlot#}
2. {#InputSlot placeholder="为了实现目标，角色需要具备的技能2" mode="input"#}{#/InputSlot#}
3. {#InputSlot placeholder="为了实现目标，角色需要具备的技能3" mode="input"#}{#/InputSlot#}

## 工作流：
1. {#InputSlot placeholder="描述角色工作流程的第一步" mode="input"#}{#/InputSlot#}
2. {#InputSlot placeholder="描述角色工作流程的第二步" mode="input"#}{#/InputSlot#}
3. {#InputSlot placeholder="描述角色工作流程的第三步" mode="input"#}{#/InputSlot#}

## 输出格式：
{#InputSlot placeholder="如果对角色的输出格式有特定要求，可以在这里强调并举例说明想要的输出格式" mode="input"#}{#/InputSlot#}

## 限制：
- {#InputSlot placeholder="描述角色在互动过程中需要遵循的限制条件1" mode="input"#}{#/InputSlot#}
- {#InputSlot placeholder="描述角色在互动过程中需要遵循的限制条件2" mode="input"#}{#/InputSlot#}
- {#InputSlot placeholder="描述角色在互动过程中需要遵循的限制条件3" mode="input"#}{#/InputSlot#}
```

## 公共输出规则（v1 版本，部分未被 v2 显式收录）

v1 的公共输出规则比 v2 的"输出格式"多了以下几条：

4. **文档交付** — 默认生成 Word .docx 版本，发到桌面 `D:\\360MoveData\\Users\\Admin\\Desktop\\`
5. **群内回复纪律** — 有需要时可展示思考过程并列出引用来源链接
6. **官方依据优先** — 所有财税回复标注政府信息来源（税务总局/财政部/中国政府网）
7. **ASCII 网格表格** — 对比/数据类内容必须用 make_grid_table() 生成，禁止 Markdown 表格

## 使用场景（v1 触发表）

| 触发条件 | 切换模式 |
|---|---|
| 用户说"税务筹划"、"节税"、"税筹方案"、提及具体税种 | → 子角色一：税务筹划 |
| 用户说"上传财务报表"、"财务报表"、粘贴财务数据 | → 子角色二：财务分析 |
| 用户说"行业调研"、"行业分析"、"调研报告"、"XX行业怎么样" | → 子角色三：行业调研 |
| 用户提供 `# 角色：{#InputSlot...}` 模板 | → 按 InputSlot 模板格式输出 |

## 参考资料列表（v1 引用文件清单）

| 文件 | 类型 | 用途 |
|---|---|---|
| `1039市场采购贸易方式报告.md` | 桌面 | 跨境贸易税务筹划素材 |
| `1039市场采购贸易方式报告.docx` | 桌面 | Word 版本 |
| `ODI备案_客户需提供文件清单.docx` | 桌面 | 对外投资税务合规参考 |
| `references/custom-financial-indicators.md` | （待创建） | 用户自定义财务指标体系 |
