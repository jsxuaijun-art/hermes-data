---
name: wechat-publish
description: 公众号自动写作→排版→发布工作流。用户说"写一篇关于XXX的公众号文章"，自动完成配图、排版、发布到「盈信税务0」草稿箱。
version: 1.0.0
author: Hermes Agent (for 江敏/盈信税务)
---

## 触发指令

用户说：
- "写一篇关于XXX的公众号文章"
- "写一篇XXX的文章"
- "发一篇XXX"

## 工作流（3步全自动）

### 第1步：写文章

1. **分析主题** → 理解文章中心思想、目标读者、写作目的
2. **写Markdown** → 含完整 frontmatter：

```yaml
---
title: 文章标题（吸引点击）
author: 盈信税务
cover: /tmp/cover_article.jpg   # 配图路径（见第2步）
abstract: 120字以内摘要，显示在卡片上
---
```

3. **文章要求**：
   - 开头有钩子（黄金三秒）
   - 结构清晰（小标题分段）
   - 给具体方案/话术/模板，不给抽象概念
   - 结尾加盈信税务品牌落款

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
1. 从 Unsplash 搜索相关图片（用 curl 从服务器下载）
2. 下载到阿里云服务器 `/tmp/cover_article.jpg`
3. 在 frontmatter 中引用 `cover: /tmp/cover_article.jpg`
4. 若 Unsplash 下载失败，fallback 到 jsDelivr CDN 图片

**服务器下载命令：**
```bash
curl -L -o /tmp/cover_article.jpg "https://images.unsplash.com/photo-XXXX?w=800&q=80"
```

### 第3步：发布

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
