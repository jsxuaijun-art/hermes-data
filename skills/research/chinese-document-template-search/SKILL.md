---
name: chinese-document-template-search
description: 查找中文合同/授权书等文档模版时，交付真实搜索来源而非自制成品。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [search, document, template, chinese, retrieval]
    category: research
    related_skills: [python-web-scraping-setup, chinese-business-doc-templates]
---

# 中文文档模版检索 Skill

用户要求"搜索/查找"某类中文文档模版（授权书、合同、协议、证明等）时，
本技能定义交付标准：**交付真实搜索结果（来源链接 + 结构摘录），不是自制成品**。
只有当正文确实拿不到、且用户明确同意后，才按真实结构制作成品。

## When to Use

- 用户说"搜索/查找/找一份 X 文档/模版/范本"
- 用户给出目标结构要求（如"一.授权人信息表格；二.授权内容；三.授权期限"）
- 需要判断网上现成模版是否符合要求、或给用户选择真实来源

## Prerequisites

- requests + bs4 可用（Hermes 主环境已预装）
- 网络环境为中国可直连（WSL China：首选 360 + 搜狗，Baidu/Google 不可达）

## How to Run

```python
import requests
from bs4 import BeautifulSoup
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
# 360: https://www.so.com/s?q=<关键词>
# 搜狗: https://www.sogou.com/web?query=<关键词>
r = requests.get(url, headers=headers, timeout=15); r.encoding = r.apparent_encoding
```

## Quick Reference

1. 多引擎并行搜：360 so.com + 搜狗 sogou.com（关键词带"范本/全文/模板"变体）
2. 收集真实来源：标题 + 链接 + 可读性判断
3. 提取结构骨架：360 文库详情页 `meta[name=description]` 含文档开头骨架；搜狗摘要含完整条款名
4. 对照用户结构要求，判断哪些源符合
5. 汇报：按相关度排序的来源表（链接 + 结构摘录 + 能否读全文），给选项
6. **先问，再制作** —— 制作永远是最后手段

## Procedure

1. **多引擎搜**：同一关键词分别打 360 和搜狗（可加"范本/模板/全文/律师精选"变体）。
2. **解析结果**：抓标题 + href。注意 360 的跳转链 `so.com/link?m=...` 是短链，requests 解不开。
3. **逐源探测可读性**：
   - 360 文库详情页 `wenku.so.com/d/<id>`：静态抓 `meta description` 拿开头骨架
   - 搜狗网页版：摘要已含条款骨架（如"1.3 授权使用的方式 1.4 授权使用的范围"）
   - 文库类（360/百度/道客巴巴/人人文库/MBA智库）：全文需登录，只报摘要
4. **对照结构要求**：用户给的三段结构（授权人信息表格/授权内容/授权期限）是否在这些源中出现，逐源标注。
5. **汇报并给选项**：
   - 真实可点击链接 + 每源结构摘录 + 可获取性标注（能读全文 / 只有骨架）
   - 选项 A：深入某篇（按用户场景选最贴近的，尽量拼出全文）
   - 选项 B：按真实结构制作成品 —— **先问，得到同意才做**
6. **得到同意后才制作**（如生成 Word 放桌面），并说明依据的真实结构来源。

## Pitfalls

- **"搜索"≠"制作"**（用户 2026-08 明确纠正）：不要搜到一半就自作主张产出成品。
- **360 跳转链** `so.com/link?m=...`：短链过期返回 400/404，解不出落地 URL；web_extract 也常失效。
- **华律网 66law.cn 合同频道**：2026-08 实测频道搜索 URL 已 404。
- **mp.weixin 秒传链接**：正文是 JS 模板壳，自动化环境读不到全文，勿承诺能读正文。
- **文库全文**：360文库/百度文库/道客巴巴全文需登录+客户端，静态抓不到，别浪费时间绕。
- **勿无限追抓**：骨架 + 摘要已足以判断结构、给用户选择时，就停止抓取，进入汇报。
- 汇报用真实链接；拿不到全文时如实说明"只能看开头骨架"，不编造正文。

## Verification

- 汇报中包含每个来源的真实可点击链接
- 每个来源标注了可获取性（能读全文 / 只有骨架）
- 末尾给了用户明确选项（深入某篇 / 按骨架制作），且制作前已获同意
- 未在用户说"搜索"时擅自产出成品文档

详细实测记录（2026-08 抖音肖像权授权书案例 + 各源可获取性矩阵 + 通用结构知识）
见 `references/douyin-portrait-authorization-sources.md`。
