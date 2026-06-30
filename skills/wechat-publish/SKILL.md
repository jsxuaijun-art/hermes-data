---
name: wechat-publish
description: 公众号自动写作→排版→发布工作流。用户说"写一篇关于XXX的公众号文章"，自动完成配图、排版、发布到「盈信税务0」草稿箱。
version: 1.1.0
author: Hermes Agent (for 江敏/盈信税务)
---

## 触发指令

用户说：
- "写一篇关于XXX的公众号文章"
- "写一篇XXX的文章"
- "发一篇XXX"

## 工作流（4步 — 含用户确认环节）

### 第0步：确认风格 + 发散建议

发文前先问两件事：

**① 排版风格**：列出当前可用风格编号让用户选，默认01。

**② 发散建议**：用户给主题后，先分析并提出2～5个可选的扩展角度，让用户圈定范围再动笔。格式：

```
💡 发散建议（可选加）
├ A. xxx — 一句话说明价值
├ B. xxx
├ C. xxx（简略）— 标注详略
└ 确认后出稿
```

### 第1步：写文章

1. **分析主题** → 理解文章中心思想、目标读者、写作目的

2. **文章结构套路**（2026.6.30 已验证的江姐偏好）：
   ```
   是什么 → 怎么定 → 多视角解析 → 常见坑 → 实操建议
   ```
   - 当话题对不同读者群体都有价值时，**分割受众**：上半篇给A群体，下半篇给B群体（如"创业新手篇"+"已有公司老板篇"），中间用 `---` + `# 下半篇：xxx篇` 隔开
   - 给**可套用的公式**（如：注册资本 = 行业门槛×1.5）
   - 关键对比用**表格**（`|概念|一句话解释|` 格式，右栏=大白话）
   - 每个坑/要点用**加粗导语**（如"坑一：xxx"），方便扫读
   - 结尾有**总结段落**或"一句话总结"金句
   - ⭐ 已成功参考模板：`references/article-structure-registered-capital-2026-06-30.md`（注册资本主题，含上下篇分割受众结构）

3. **写Markdown** → 含完整 frontmatter：

```yaml
---
title: 文章标题（吸引点击）
author: 苏州盈信财税
cover: /tmp/cover_article.jpg   # 发布前替换为 asset://xxx 或 http://127.0.0.1:8080/images/xxx.jpg
abstract: 120字以内摘要，显示在卡片上
---
```

4. **文章要求**：
   - 开头有钩子（黄金三秒）+ 场景切入（让读者觉得"说的就是我"）
   - 结构清晰（小标题分段）
   - 给具体方案/话术/模板/公式，不给抽象概念
   - 引用法规时标注具体条文号，但不堆砌法条
   - 结尾加「苏州盈信企业管理有限公司」品牌落款（**注意：不是「盈信企业管理（苏州）有限公司」**）

5. **出稿后给用户预览确认**，再推进到配图+发布。

### 第2步：配图

根据文章**中心思想**匹配图片，不是固定配外贸图：

| 话题 | 配图方向 | 图源 |
|------|----------|------|
| 财税政策/法规解读 | 政府大楼、公章、文件 | Unsplash/下载到服务器 |
| 公司注册/创业 | 写字楼、办公场景、营业执照 | Unsplash |
| 出口退税/外贸 | 港口、集装箱、货轮 | ✅ /tmp/cover_cargo.jpg 可用 |
| 节税筹划/税务合规 | 计算器、图表、财务分析 | Unsplash |
| 跨境电商 | 电脑、手机、线上购物 | Unsplash |
| 代理记账/会计 | 财务报表、数字、办公室 | Unsplash |
| 政策通知/提醒 | 日历、时钟、公告栏 | Unsplash |
| 通用/综合 | 财税相关中性图 | Unsplash |

**配图执行流程：**
1. **封面图**：按「话题→配图方向」表精准选图。**每篇文章封面不能重复**，必须匹配中心思想（用户会直接退回通用图/重复图）。
2. **正文配图**：每篇文章**至少2～3张**正文配图。每张图放在对应章节位置，匹配该节的中心思想。
3. 从 Unsplash 搜索相关图片下载到阿里云服务器
4. **正文配图统一用 nginx 图片服务方案**（详见下方「✅ 方案A实操步骤」），不能用 asset:// 协议。
5. 若 Unsplash 下载失败，fallback 到 jsDelivr CDN 图片

**服务器下载命令：**
```bash
curl -L -o /tmp/cover_article.jpg "https://images.unsplash.com/photo-XXXX?w=800&q=80"
```

**⚠️ Unsplash API 已知问题**：当前 `client_id=2zRikF5UzsDfDgXPHFcFBhw48a7k4OzRIFHzCgXNM0A` 已返回 401。可用替代方案：
   - 直接使用已知的 Unsplash photo ID 直链（`https://images.unsplash.com/photo-XXXX?w=800&q=80`）
   - 或 jsDelivr CDN 兜底

### 第3步：发布

**⚠️ 发布前检查清单：**
- [ ] 封面图路径：优先用 `asset://` 协议（upload到wenyan后获得的ID），也可用 `http://127.0.0.1:8080/images/xxx.jpg`
- [ ] 作者字段：统一用「**苏州盈信财税**」（微信限制8个中文字符，「苏州盈信企业管理有限公司」11字会报错45110）
- [ ] 正文配图：必须用 `http://127.0.0.1:8080/images/xxx.jpg`，**禁止**在正文中用 `asset://` 协议（会报错40113）
- [ ] 公司落款：文章尾部必须写「**苏州盈信企业管理有限公司**」（主体全称，与作者字段不同）

**发布命令：**
```bash
NODE_OPTIONS='--experimental-require-module' \
node /usr/lib/node_modules/@wenyan-md/cli/dist/cli.js \
publish -f /tmp/article.md \
--server http://127.0.0.1:3000 \
-c /etc/wenyan/yingxin-theme.css
```

**服务器**：阿里云 ECS 47.103.27.171，wenyan-server 端口 3000

**排版主题**：`/etc/wenyan/yingxin-theme.css`（已生效，见下节）

## 排版主题

### 当前主题
路径：`/etc/wenyan/yingxin-theme.css`（服务器上）
特点：行间距1.75、标题带左侧色块、引用蓝边框灰背景、代码块圆角
|## 排版风格库（v2.0 — 多风格可选）

风格数据保存在服务器 `/etc/wenyan/themes/` 目录下，每份为一个 JSON + 对应 CSS 文件。
本地同步镜像：`~/.hermes/skills/wechat-publish/themes/`

### 当前已收录风格

| # | 风格名称 | 特点 | 来源 |
|:-:|:---------|:-----|:-----|
| 01 | 安信伯君（红底色） | 标题纯加粗，关键段红色强调 | 安信伯君管理咨询 |
| ... | （持续增加） |

### 风格拆解流程（用户发链接时）

当用户说"找到一篇排版好看的公众号文章"时：

1. 用户回复公众号文章链接
2. 用浏览器/curl打开链接，分析排版要素：
   - 正文字体大小、行间距
   - 标题样式（字号、颜色、装饰元素）
   - 引用块设计
   - 配色方案（主色、强调色）
   - 整体风格（简约/商务/活泼/文艺）
3. **提炼命名**：按「序号-来源公众号（核心特征）」格式命名，例如 `01-安信伯君-红底色`
4. 保存 JSON 风格档案到 `themes/` 目录
5. 将风格转化为 CSS，更新到服务器 `/etc/wenyan/themes/`
6. 回复用户：风格已入库，下次发文可选

### 发文前风格选择流程

**写文章前，先确认风格：**

```
→ 询问："这篇用哪个排版风格？当前可选：01安信伯君（红底色）..."
→ 用户选风格编号
→ 发文时引用对应的 CSS 文件
→ 若无指定，默认用 01安信伯君（红底色）
```

### 现有主题（作为 baseline）

路径：`/etc/wenyan/yingxin-theme.css`（服务器上，作为各风格的 baseline）
特点：行间距1.75、引用蓝边框灰背景、代码块圆角

## 发布节奏

- **固定发布日**：周二、周四
- 到发布日主动询问："今天要发一篇吗？"
- 用户也可随时主动要求写文章

## 发布后

- 回复用户："✅ 文章已发布到「盈信税务0」草稿箱，去审核吧"
- 附 Media ID 供核对
- 用户去公众号后台 → 草稿箱 → 审核 → 手动群发

## 注意事项

- 封面图和正文中至少需要一张图（微信要求）
- 无需用户二次排版，wenyan + 自定义CSS自动渲染完成
- 封面图路径必须是服务器本地绝对路径或 HTTP(S) URL
- 不要用 file:// 前缀，直接用 /tmp/xxx.jpg
- Unsplash 图片需先 curl 下载到本地，wenyan 内置 HTTP 客户端不支持 Unsplash CDN

### ⚠️ 正文配图的已知限制（2026-06-30 已验证）

`wenyan publish` CLI **不支持在正文中使用 `asset://` 协议引用图片**。如果 markdown 正文里有 `![alt](asset://xxx.jpg)`，发布会失败（WeChat 错误码 40113）。

**正文配图的可行方案（按推荐优先级）：**

| 方案 | 操作 | 说明 |
|:-----|:-----|:-----|
| ✅ A. 阿里云ECS本地nginx服务 | 在服务器上搭建nginx图片直链 → `![](http://localhost:8080/images/xxx.jpg)` | wenyan原生支持，自动化，已验证可用 |
| B. HTTPS直链（阿里云OSS等） | 把图传到图床，正文用 `![](https://...)` | 可靠但需额外配置CDN |
| C. 后台上传 | 先发到草稿箱（不含正文图），让用户进公众号后台手工插入 | 最简单，但用户不喜欢 |

### ✅ 方案A实操步骤（2026-06-30 验证通过）

**核心原理：** 在阿里云ECS上搭nginx静态文件服务（端口8080），从Unsplash下载主题相关图片放入服务目录，markdown正文中用 `http://localhost:8080/images/xxx.jpg` 引用。wenyan publish 时自动抓取图片上传到微信CDN，文章发布后图片走微信HTTPS。

**① 确保nginx安装并配置图片服务**

```bash
cat > /etc/nginx/sites-available/images << 'EOF'
server {
    listen 8080;
    root /var/www/html;
    index index.html;
    server_name _;
    location / {
        try_files $uri $uri/ =404;
        add_header Access-Control-Allow-Origin *;
    }
}
EOF
ln -sf /etc/nginx/sites-available/images /etc/nginx/sites-enabled/images
nginx -t && systemctl reload nginx
```

**② 下载图片并放入服务目录**

```bash
mkdir -p /var/www/html/images
# 封面图（按话题→配图方向表精准选图）
curl -L -o /var/www/html/images/cover.jpg "https://images.unsplash.com/photo-XXXX?w=800&q=80"
# 正文配图（每张配图对应一个章节的主题，不能通用）
curl -L -o /var/www/html/images/section1.jpg "https://images.unsplash.com/photo-XXXX?w=800&q=80"
```

**③ 在 markdown 中引用**

frontmatter 封面改为 HTTP 直链：
```yaml
cover: http://localhost:8080/images/cover.jpg
```

正文配图用标准 markdown 语法：
```markdown
![配图说明](http://localhost:8080/images/section1.jpg)
```

**④ 直接 publish** — wenyan 自动抓取图片并上传微信CDN。

**⚠️ 已知坑：**
- 封面图和正文图都不能用 `asset://` 协议，统一用 `http://localhost:8080/...`
- 每张配图必须**匹配它所在章节的中心思想**（用户会直接退回通用图）
- Unsplash API key `client_id=2zRikF5UzsDfDgXPHFcFBhw48a7k4OzRIFHzCgXNM0A` 已失效（401），用已知photo ID直链代替
