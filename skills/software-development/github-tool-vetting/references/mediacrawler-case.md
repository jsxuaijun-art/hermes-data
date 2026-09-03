# MediaCrawler 核实案例（2026-08 实操）

用户问：MediaCrawler 值不值得装；"v0.20.5 是最新版本吗？"

## 结论
值得装，但定位为低频、小批量调研辅助；v0.20.5 不是官方版本号，项目无任何 tag/release。

## 核实证据链（no-shell 完成）
1. 仓库主页（web_extract github.com/NanmiCoder/MediaCrawler）：当刻约 63.9k star / 12.4k fork，README 有 MediaCrawlerPro 商业版引流、Sponsor、BrowserAct 广告位。作者 程序员阿江-Relakkes / NanmiCoder。
2. Releases 页：`There aren't any releases here` —— 无正式发版。
3. `api.github.com/repos/NanmiCoder/MediaCrawler/releases/latest` → 404。
4. `api.github.com/repos/NanmiCoder/MediaCrawler/tags?per_page=20` → `[]`（无 git tag）。
5. `raw.githubusercontent.com/NanmiCoder/MediaCrawler/main/pyproject.toml` → `version = "0.1.0"`（包开发号）；依赖含 playwright、pyexecjs、xhshow（xhs 签名）、wordcloud；`[[tool.uv.index]]` 默认清华源 `https://pypi.tuna.tsinghua.edu.cn/simple`。
6. README 全文无版本号 → "v0.20.5" 只能来自第三方教程/转载，非官方。
7. 官方文档 nanmicoder.github.io/MediaCrawler/：推荐 uv 管理依赖、Python 3.11、Node ≥16（抖音/知乎需要）、playwright install；运行示例 `uv run main.py --platform xhs --lt qrcode --type search`；支持 CSV/JSON/SQLite/MySQL。
8. 免责声明：明令"仅供学习参考、禁止商业用途"，附 HiddenStrawberry/Crawler_Illegal_Cases_In_China 违法案例库链接。

## 能力与原理
- 平台：小红书、抖音、快手、B站、微博、贴吧、知乎；关键词搜索/指定ID/二级评论/创作者主页/登录态缓存/IP代理池/评论词云。
- 原理：Playwright 浏览器自动化保登录态，JS 表达式取签名，无需逆向加密；新版支持 CDP 连接本地 Chrome 复用登录态降风控。
- 商业版 MediaCrawlerPro：断点续爬、多账号+IP代理池、去 Playwright、完整 Linux 支持、自媒体内容拆解 Agent。

## 风险要点（对财税从业者客户）
- 商用红线：抓来内容仅作选题线索/调研素材，引用必须回验原文与官方文号。
- 账号风险：高频采集触发平台风控（滑块/IP限制/封号），用户的主引流账号不可用于试验。
- 技术门槛：Chrome + Python + Node + Playwright，出问题多为登录态/风控，需人维护。

## 决策框架（本次给用户的建议）
- 轻量选题调研：平台创作灵感榜 + agent 直接 web_search/web_extract 即可，不必上爬虫。
- 深度调研（某主题全量高赞内容+评论区风向导出表）：才值得装，且低频小批量。
- 交付节奏：先免费出一轮"热点+同行内容"调研 → 不够再装最小示例评估 → 最后决定投入。