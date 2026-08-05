# 视频号(WeChat Channels)链接内容提取方法 — 2026.8.5 实战验证

视频号链接形如 `https://weixin.qq.com/sph/XXXX` 或 `channels.weixin.qq.com/finder-preview/pages/sph?id=XXXX`。
这是 SPA，返回的 HTML 只有 JS 壳（`#app` 空 div），**必须执行 JS 才能拿到内容**。curl 直接抓只会得到 2.5KB 的跳转壳。

## 提取方法（playwright + chromium headless）

Web 版视频号能拿到**标题 / 发布者 / 互动数据 / 封面**，但**拿不到视频逐字稿**（见下）。

```python
# 关键：用移动端 UA + viewport，等 SPA 渲染，并拦截 get_feed_info 接口
ctx = browser.new_context(
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
               "AppleWebKit/605.1.15 (KHTML, like Gecko) "
               "Version/16.0 Mobile/15E148 Safari/604.1",
    viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
page.on("response", <拦截 get_feed_info 响应 body>)
```

触发到的关键接口：`https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info`
POST body：`{"baseReq":{},"shortUri":"AjHoukrpWl"}`（shortUri 即链接中 `sph/` 后那串）。

响应 JSON 结构（实测字段）：
- `data.authorInfo.nickname` → 发布者昵称（本案例拿到"国家税务总局"官方认证号）
- `data.authorInfo.headImgUrl` → 头像
- `data.authorInfo.authIconUrl` → 非空=企业认证号（注意：这是强信任背书信号，适合判断值得改编的权威素材）
- `data.feedInfo.description` → 标题/描述（含 #话题标签）
- `data.feedInfo.coverUrl` → 封面图（stodownload 带 token，浏览器 UA+Referer 可下载）
- `data.feedInfo.forwardCountFmt` / 页面其余数字 → 转发/赞/评论/收藏

页面渲染文本已足够拿到：标题、日期（如"2026年8月4日"）、发布方、四项互动数。

## 关键限制：拿不到视频逐字稿

视频号网页版对未登录访客提示 **"可前往微信观看此内容 / 前往微信"**，视频 `<video>` 元素不加载真实视频流。
因此：
- **无法**从网页版抓视频 MP4/逐字字幕/口播内容。
- 想 100% 还原视频内容 → 按 skill 主文档思路，请用户**在微信里保存视频发本地路径**，再用 ffmpeg + faster-whisper 转逐字稿。

## 遇到结构方案有得写的情况

即便拿不到逐字稿，只要标题+发布方清晰（尤其官方权威号，如税务总局），主题方向已经明确。作为财税专家可直接按标题主题出「上半篇普法 + 下半篇实操」结构方案，不必卡在"没有逐字稿"上。逐字稿只是锦上添花，不是前提。

## 反爬注意

- 视频号不强制验证码，playwright headless 就能过（用移动端 UA 更稳）。
- 媒体判断：`stodownload?encfilekey` 返回 `image/jpg`（封面图），不是视频，别误判。
