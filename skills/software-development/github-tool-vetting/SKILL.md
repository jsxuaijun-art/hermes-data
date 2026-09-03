---
name: github-tool-vetting
description: 核实GitHub开源项目的真实版本、维护状态与使用风险，再给安装建议。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, open-source, verification, 开源工具核实]
    category: software-development
    related_skills: [scraping-dispatch]
---

# GitHub 开源工具核实 (github-tool-vetting) Skill

当用户从文章/短视频/公众号看到某个 GitHub 开源工具（爬虫、AI、效率工具等），问"值不值得装/是不是最新/靠不靠谱"时，先回官方源核实再下结论。本技能提供一套无需本地 shell 的核实方法，并内置针对财税从业者客户的合规与风险评估框架。

## When to Use
- 用户问"XX GitHub 项目值不值得安装/使用"
- 用户转述某教程声称的版本号、star 数、功能，需要甄别真伪
- 需要评估采集/爬虫类工具对业务（内容选题、调研）的合规与账号风险
- 用户拿着一个项目名/仓库链接来求证"这是不是最新版"

## Prerequisites
- 能用 web_extract 访问 github.com / raw.githubusercontent.com / api.github.com（无需 shell）
- 若命令行可用，`git ls-remote --tags https://github.com/<owner>/<repo>.git` 可拿权威 tag 列表；但 no-shell 路径通常已足够回答"是否最新"

## Quick Reference
no-shell 核实清单（web_extract 可直接解析 JSON 与 raw 文本）：

| 核实对象 | URL | 回答什么 |
|---|---|---|
| 仓库主页 | github.com/<owner>/<repo> | star/fork 当刻值、README 主张、商业版引流 |
| Releases 页 | github.com/<owner>/<repo>/tags | "There aren't any releases here" = 无正式发版 |
| Latest release API | api.github.com/repos/<owner>/<repo>/releases/latest | 404 = 无 release |
| Tags API | api.github.com/repos/<owner>/<repo>/tags?per_page=20 | `[]` = 无 git tag |
| 版本文件 | raw.githubusercontent.com/<owner>/<repo>/main/pyproject.toml（或 package.json） | 常是包开发号(0.1.0)，非对外版本 |

## Procedure
1. 从用户转述中定位官方仓库 owner/repo；警惕同名山寨/改版仓库。
2. 用 Quick Reference 清单逐项核实：当刻 star 数、有无 release/tag、README 是否声明版本号、免责声明与 LICENSE。
3. 判断版本号真伪：若官方任何表面（release/tag/README/版本文件）都无 "vX.Y.Z" 字样，而教程声称某版本——该版本号是杜撰或抄旧的，向用户明说。
4. 读免责声明与 LICENSE 判断商用边界（爬虫类项目几乎标配"仅供学习研究、禁止商业用途"，有的还挂中国爬虫违法案例库链接）。
5. 按用户业务做风险与替代评估：
   - 该工具解决的需求，是否有更轻的替代（平台官方榜单、web_search/agent 直接检索）
   - 账号风险：用个人引流主账号跑高频采集有封号风险
   - 数据边界：抓来的内容只能当选题线索/调研素材，引用必须回验原文与官方文号（公众号铁律：严禁AI幻觉、不确信不写）
6. 给结论骨架：需求 ↔ 替代方案 ↔ 装机/维护成本 ↔ 风险，最后提议"装上跑一个最小示例再定"，让用户零成本决策。

## Pitfalls
- 教程/公众号声称的"最新版本号"大多不可信；官方无 release/tag 的项目根本没有版本概念，clone main 即最新。
- pyproject.toml / package.json 的 version 字段常是包开发号（如 0.1.0），不代表对外项目版本。
- star 数随时间变化，回复引用"约X万"或当场核实，勿用教程里的旧数。
- README 写着"开源"不等于可以放心商用；注意商业版/Pro 引流、赞助位，如实点出。
- 用户的主引流账号（如微信营销号生态关联的抖音/小红书号）绝不可用于爬虫试验。

## Verification
- 每条结论都能指向官方来源（仓库页/API 返回/raw 文件），表述用"官方页面显示…"。
- 若受限于环境拿不到权威数字（如 shell 被拒、API 受限），如实说明"未取得官方完整 tag，但已确认…"，不编造。

## References
- references/mediacrawler-case.md — MediaCrawler 具体核实证据链与风险结论（2026-08 实操）。