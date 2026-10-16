---
name: law-to-skill
description: >
  把一部/一批中国法律、法规、暂行条例转为可精确引用的结构化 Skill 群（主路由 + 子 skill 路由 +
  references/全文.md）。典型触发："把XX法做成skill"、"公司法/税收法律建skill"、"用 book-to-skill
  方法论建法律 skill 群"。复用已验证的维基文库抓取→清洗→生成→条号自测流程，避开代理重试、
  <onlyinclude> 整段包裹、模板锁正文、3 位数中文条号等坑。agent_created: true
version: 1.0.0
agent_created: true
---

# 法律文本 → 结构化 Skill 群（law-to-skill）

## 适用
把法律/行政法规（公司法、各税法、民法典等）建成「主路由 + 子 skill + references/全文.md」，
每个条号都从全文抽取核对，防幻觉。

## 数据源与抓取（关键坑）
- 源：维基文库 `https://zh.wikisource.org/w/index.php?title=<标题>&action=raw`（raw wikitext）。
- **网络**：本机 Bash 沙箱走 `127.0.0.1:5339` 代理；**Python urllib 被沙箱禁网（SIGTERM），
  一律用 `curl`**。`curl` 偶发 TLS 握手失败（curl:35），须重试（每次 25s 超时 ×5 次）。
- 修正后法律（企税/个税/征管/环保/车船/土增/船舶吨税等）主页是 transclude 桩，要抓
  `XX法 (YYYY年)` 版本子页（如 `中华人民共和国企业所得税法 (2018年)`）。
- 个别暂行条例正文锁在 `{{国务院令法规|N}}` 模板：改用 MediaWiki API
  `action=parse&prop=text&format=json` 展开 HTML，再剥离标签取正文。
- URL 含中文用 `curl -G --data-urlencode "title=..."` 编码。

## 清洗（clean.py 要点）
- 迭代删 `{{...}}` 模板（处理嵌套）；去 `[[链接]]`（保留显示文本）；去 `<ref>`/`<br>`/标签。
- **`== 章节 ==` → `## 章节`**；`'''第X条'''` 去粗体留原文。
- ⚠️ 多部法律正文整段包在 `<onlyinclude>...</onlyinclude>`，**只能去标签、留正文**，
  误删该 span 会清空全文（公司法/企税等版本子页均如此）。
- ⚠️ 自测/计数正则须含「百/千」：`第([一二三四五六七八九十百千零0-9]+)条`，否则
  "第一百六十八条" 这类 3 位数条文计数归零、误判条号缺失。

## 生成（gen_skills.py）
- 解析 `## 第X章` 得结构索引；取每章首末条号作范围；摘录前 N 条原文作「重点条文摘录」。
- 优先级高的法律（公司法/增值税/企税/个税/征管/印花税）写「高频场景→步骤→条文」，
  引用条号用 `fmt_cite` 校验：不在全文则标「（第N条，以全文为准）」，杜绝幻觉。
- 单部法律 → 一个 skill（含全文）；多部同类（如 17 部税法）→ 主路由 `tax-law` + 每部子 skill。
- 单部多章且实务需分主题（如公司法 15 章）→ 主路由 + 按主题分组子 skill
  （split_company.py：按章切片到 `references/本章全文.md`）。

## 自测（selftest2.py）
- 对每个含 `references/全文.md` 或 `references/本章全文.md` 的 skill，抽出 SKILL.md 中
  "第N条" 与全文 present 集合比对，**要求 0 缺失**。
- 对路由器（company-law / tax-law）校验其引用的子 skill 目录均存在。

## 产物位置
- skill：`~/.workbuddy/skills/<name>/`（name 用 kebab，税法子 skill 前缀 `tax-`）。
- 中间脚本/源文：`law_build/`（fetch_ws.sh / clean.py / gen_skills.py / split_company.py /
  selftest2.py / src/ 原始 / clean/ 清洗后）。

## 注意事项
- 引用具体优惠比例/起征点/留抵退税等随国务院·税务总局文件变动，skill 不替代现行有效规范性文件。
- 司法解释（公司法解释二、征管法实施细则等）属外部口径，引用时结合，不混入法律正文。
