---
name: chinese-business-doc-templates
description: 生成中文商务/法律文书模版（授权书、协议、委托书等），Word 交付桌面。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [document-template, legal, docx, chinese]
    related_skills: [word-documents, chinese-legal-research]
---

# 中文商务/法律文书模版生成

## When to Use

用户要「XX授权书 / 协议 / 委托书 / 证明 / 承诺书」类文书模版时使用。用户（财税从业者）常为短视频拍摄、客户服务等场景出这类文书，需求高频。

## 工作流（三步）

### 1. 检索范文（找结构参考，不是抄原文）

- **首选 360 搜索** `www.so.com/s?q=<关键词>`（requests+bs4 直抓，`h3` 标题+链接可解析）。搜狗 `www.sogou.com/web?query=` 有时返回空列表，作备用。
- 文库结果直链形如 `wenku.so.com/d/<id>`，requests 可打开。
- **关键技巧：360文库（wenku.so.com）正文是 JS 渲染，`soup.select("p")` 抓不到正文；但 `<meta name="description">` 携带文档开头片段**（常含正文前 60-100 字，字段会被截断，如"身份证号"→"份号码"、"联系方式"→"系方式"，需脑补还原）。用这个片段确认文档主题、结构、是"双方协议"还是"单方授权书"即可。
- 页面内 `DocInfo` JSON 正则解析常因嵌套引号失败——直接用 meta description 更稳。
- 完整正文需登录/付费，静态抓不到——**不要死磕**，片段+领域常识足够重建。
- web_search 工具未配置 provider 时不可用；用上面的 requests 直抓方案替代。

### 2. 按用户指定结构重建

用户会给出结构要求（例："一.授权人信息表格；二.授权内容；三.授权期限"）。严格按其结构组织，再加合理的补充条款（其他约定、签署区、争议解决）。产出**完整可用模版**，不是片段。

### 3. 出 Word 交付

- 用户要 Word → python-docx 生成 `.docx`。
- **保存路径：先查 `/mnt/d/OneDrive/Desktop/`（本机桌面在 D 盘 OneDrive，已确认），不存在才用 `/mnt/c/Users/Administrator/Desktop/`。**
- 中文字体：Normal 样式 + 每个 run 都设 `rFonts.set(qn('w:eastAsia'),'宋体')`，否则中文回退乱码。详见 word-documents skill（bundled，只读参考）。
- 表格用 `doc.add_table()` + `table.style='Table Grid'`，列宽 `Cm()`。
- 文件名用中文描述性命名：`抖音肖像权授权书.docx`。

## 交付时附专业提醒（用户看重，别省略）

按文书类型主动提醒：
- 授权书类：有偿/无偿必须明确勾选；用途范围越明确对授权方越安全、越宽对被授权方越有利——先问清用户是哪一方；期限填具体起止日，不写"长期/永久"；平台合规审核，建议签章后双方各留原件存档。
- 协议类：金额、支付方式、结算节点写清楚；转授权需书面同意；争议管辖约定。
- 用户要求"直接给能用的方案"——给成品，不解释过程废话。

## 已有模版

- `references/portrait-rights-authorization-template.md` — 抖音肖像权授权书完整模版（授权人信息表格/授权内容/授权期限/其他约定/签署区）+ 专业提醒 + python-docx 中文字体要点。
