# 视频号 sph 链接提取：机制与探测记录（2026.9.5 实战）

## 结论先行

`weixin.qq.com/sph/<id>` 链接的正文内容**需要微信 App 登录态才能拿到**，匿名环境（curl / 无头浏览器 / 直接 RPC）基本抓不到。诊断 3 步失败后立即走 SKILL.md 的「抓不到素材时的兜底协议」，不要继续逆向。

## 链接结构与跳转

- 用户给的：`https://weixin.qq.com/sph/ALMsV7V7Qk`（<id> 为短 id）
- 浏览器打开后跳转到：`https://channels.weixin.qq.com/finder-preview/pages/sph?id=<id>`
- curl 拿到的 HTML 只有 JS 壳：`<title>视频号</title>`，正文全 void

## SPA 数据流（从 JS bundle 逆向得出）

- 预览页 SPA（feed.js bundle）在进入页面时调 `Xa.getFeedInfo({baseReq:{generalToken: token}, shortUri: hash(id)})` 取 feed 的 sceneInfo（标题/发布者/互动数/封面）
- `generalToken` 来自 `se().token || cookie token` —— 微信 App 会话才有；匿名会话为空
- 无 token 时 SPA **不发任何数据网络请求**，页面渲染为空（只显示通用的「当前仅支持浏览视频，更多功能可通过微信扫码使用」）
- Playwright 抓网络请求实证：SPA 加载了 JS/CSS，但 12s 内 0 个数据接口调用、0 次 console 输出

## 探测过的端点（均无效/需登录态）

| 端点 | 方法 | 结果 |
|------|------|------|
| `channels.weixin.qq.com/mobile/commonFinderJsApi.html` | POST (action=openFinderFeed / getFeedInfo, feedID=短id) | `{"errCode":-1,"errMsg":"Cannot POST /mobile/commonFinderJsApi.html"}` — 外部只收 GET |
| `channels.weixin.qq.com/web/pages/feed?eid=<id>` | GET（手机微信 UA+Referer） | 200 但 58 字节错误壳，无内容 |
| `getFeedInfo` 直连 | 需 generalToken | 无 token 必拒 |
| 微信分享卡 OG/预览 | 无 | sph 链接不走标准 OG 标签，无匿名预览 |

## 判断流程（限时 3 步）

1. `curl -A "<手机微信UA>" -e "https://channels.weixin.qq.com/" <sph链接>` → 若只有 `<title>视频号</title>` 壳 → 判定闭源
2. 浏览器工具开一次：若只有「扫码使用」提示、正文空 → 停
3. playwright 无头 + 手机 UA：抓 network 请求，0 个数据调用 → 停，走兜底协议

## 兜底路径（不要编造）

1. 让用户粘贴视频文案/字幕/截图（真实内容 → 核实政策出处后写）
2. 让用户给主题关键词 → 官方政策原文（gov.cn/税务总局，文号+施行日期可溯源）原创
3. 环境问题修环境后重试

## 反模式（本次踩过，勿重复）

- ❌ 反复用不同 session/超时重试卡死的浏览器 daemon（环境问题，重试无效）
- ❌ 无 token 情况下无限逆向 feed.js/apisvr.js 找数据端点（找得到端点也没有 token 可调）
- ❌ 浏览器工具连纯 Python 探测都超时后继续等大超时（350s+ 都是白等）