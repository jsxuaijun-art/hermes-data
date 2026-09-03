# China 网络环境·搜索/检索渠道能力总览（2026-08-14 实测+盘点）

> 用途：写财税观点/风险类文章要**核实案例数字、查官方通报、找素材源**时，先按表选对渠道，别在不可行的路上耗时间。
> 本机环境：WSL(Ubuntu) China 网络，无全局代理（Clash 只绑 127.0.0.1:7890 给 GitHub）。
> 详见 `software-development/python-web-scraping-setup`（bundled，只读）里的逐项实操参考。

## 通用搜索引擎（核实数字/查政策用）

| 渠道 | 实测能力 | 方法 | 备注 |
|:-----|:---------|:-----|:-----|
| 搜狗 sogou.com | ✅ 可用 | requests+bs4 直抓 `https://www.sogou.com/web?query=` | **会被限流**（返回空）→ 换 360，别同引擎反复重试 |
| 360 so.com | ✅ 可用 | requests+bs4 直抓 `https://www.so.com/s?q=` | 支持 `site:` 限定，较稳 |
| 百度 | ⚠️ 受限 | requests 直抓触发验证码；浏览器偶可过 | 不稳，不首选 |
| 谷歌 | ❌ 不可达 | 被墙；除非临时走 127.0.0.1:7890 代理 | 默认排除 |
| 必应 cn.bing | ⚠️ 偏科 | requests/浏览器可抓 | 中文政务/长查询分词错乱，政务检索基本不可用 |
| 头条/神马等 | ⚠️ 未稳定验证 | requests 可试 | 反爬看情况，用前先小测 |

> 内置 `web_search` 工具在部分环境可能未配置 provider（报"未配置"）——直接落回上表 requests 直抓/浏览器方案，别卡住。

## 新媒体平台（找素材/观点源用）

| 平台 | 能力 | 方法 |
|:-----|:-----|:-----|
| 抖音（单视频内容） | ✅ 强 | **Hermes 内置浏览器路线实测可行**：短链→`curl -L` 解析 video id→用带完整参数的分享 URL `browser_navigate`→页面内 `browser_console` fetch `/aweme/v1/web/aweme/detail/?aweme_id=<id>&aid=6383...` 拿 desc/作者/数据/章节要点/评论区。页面内 fetch 自带登录 cookie，绕 acrawler 签名。完整步骤见 `wechat-publish`「抖音获取步骤」（2026.8.2 验证） |
| 公众号 | ⚠️ 半强 | 搜狗微信 `weixin.sogou.com/weixin?type=2` requests 抓标题+长摘要；要 mp.weixin 直链用搜狗网页版，但秒传链正文是 JS 壳、自动化读不到全文 |
| 视频号 | ❌ 封闭 | 进不了任何搜索引擎；只能浏览器开 JS 渲染页读标题/发布者 |
| 微博 | ⚠️ 待实测 | 搜索反爬较强，可试 requests/浏览器，本会话未验证，用前先小测 |
| 小红书 | ⚠️ 强反爬 | 未验证可行路线，默认不承诺 |
| B站 | ⚠️ 可试 | 有搜索，requests/API 可试，本会话未验证 |

## 关键规则

- **数字/政策只认官方源**：搜狗/360 结果里挑官方媒体（新华社/央广网/中新网）或官方通报（税务局/证监会）；自媒体二手解读仅作线索。**引用前必须重新核实**（守"严禁AI幻觉"铁律）。已核实案例库见本 skill 正文。
- **搜狗/360 结果里的跳转链**（`/link`、`so.com/link?m=`）requests 直解返回 400，须用浏览器点开取落地 URL。
- **分目标选路线**：抓"单个内容"→优先 Hermes 内置浏览器（browser_navigate+browser_console fetch）；抓"批量列表/爆款数据"→才走爬虫工具阶梯（见 `software-development/python-web-scraping-setup`），不行就方案B人工采集。
