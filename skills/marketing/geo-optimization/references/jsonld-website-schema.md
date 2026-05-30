# 财税官网 JSON-LD 结构化数据实操手册

## 目标网站信息

- 域名：www.yingxinkuaiji.com（IIS, ASP纯静态站，非QCNET99）
- FTP：www.yingxinkuaiji.com，用户 jsxuaijun，密码 Yx168168/*-
- 实际网站根目录：`wwwroot/`（非FTP根目录）
- FTP根目录上的 index.asp 是备份/同步副本，真正服务的是 wwwroot/index.asp
- ⚠️ TLS 版本过旧（IIS SSL alert internal error），curl 必须用 `http://` 非 `https://`
- FTP 上传不走 TLS，可直接使用

## 🚨 首要原则：先检查线上已有内容（2026.5.26 实战教训）

**不要凭空制造 JSON-LD！先检查线上是否已有！**

**正确流程：**
1. `curl -s http://域名 | grep 'application/ld+json'` — 检查有没有
2. 如果有 → 下载原文件，在原有代码块里补充缺失字段
3. 如果没有 → 从零创建

**错误做法（2026.5.26 实战踩坑）：** 不检查线上就写了一个完整的 JSON-LD，上 FTP 才发现早就有了更完整的版本。结果是画蛇添足，多了第二个重复块。

**已有 JSON-LD（https://www.yingxinkuaiji.com as of 2026.5.26）：**
- `@graph` 结构，3个节点：
  - `AccountingService`（organization）：名称、电话x3、地址、创始人（高级会计师描述）、价格范围、营业时间、sameAs（知乎）、makesOffer
  - `WebSite`：站内搜索 SearchAction
  - `FAQPage`：3 个常见问题（注册费用/代账费用/注册流程）
- 这个版本已经很专业。每次只在原节点补字段，不要再新增第二个 `<script type="application/ld+json">` 块。

## Schema 类型选择

**推荐** `AccountingService`（Google 有专有 schema，语义最精准） + `WebSite` + `FAQPage`。不要只用泛化 `Organization`。

## FAQ Schema 选题策略

选老板问得最多但搜索量大的 6 个问题，覆盖：
- 注册公司"要多久/多少钱"
- 代理记账"费多少/怎么挑"
- 注销"多麻烦"
- 税务风险"怎么查"

FAQ 的 answer 中自然植入差异化卖点（高级会计师、许可证编号、协会成员），但不要硬广。

## 部署位置

放在首页 `</head>` 之前。

- **纯 ASP 网站（如 yingxinkuaiji.com）：** 下载→编辑→FTP 上传
  - 下载：`curl -sL ftp://域名/wwwroot/index.asp --user "用户:密码" -o 本地文件`
  - 上传：`curl -sL ftp://域名/wwwroot/index.asp --user "用户名:密码" -T 本地文件`
  - 编辑后验证：`curl -s http://域名 | grep -o 'application/ld+json' | wc -l`（确认只有1个块）
  - 可视化验证：`curl -s http://域名 | grep -o 'makesOffer\|@type\|faq'`（确认字段存在）
- **有 CMS 后台的网站：** 通过管理后台插入

## ⚠️ 关键陷阱：PC/手机双版本部署（2026.5.26 实战教训）

**中文 ASP 网站最常见的一个坑：网站有 PC 版和手机版两套代码。**

### 为什么这是个陷阱

| 问题 | 表现 |
|:--|:--|
| Google Rich Results Test 用移动端 UA | 自动被 JS 跳转到 `/mobile/` → 抓到的是手机版 |
| 手机版没有 JSON-LD | Google 返回「未检测到任何内容」|
| 手机版地址还是旧的 | 改 PC 版地址忘了改手机版 → 前台显示不一致 |
| 手机版 footer 用 include 文件 | 地址不在 index.asp 里，在 `foot.asp` 里 |

### 正确操作流程

```
第①步：找手机版文件位置
  → curl -s http://域名 | grep 'location.href.*mobile\|mobile/' 看跳转规则
  → 手机版通常是 /mobile/index.asp 或 /wap/index.asp

第②步：检查手机版有没有 JSON-LD
  → curl -s http://域名/mobile/ | grep 'application/ld+json' 
  （结果：0 → 没JSON-LD，1 → 已有，2+ → 重复了）

第③步：检查手机版地址
  → curl -s http://域名/mobile/ | grep '地址：'
  → 如果地址是 include 进来的：找 foot.asp 或 bottom.asp 等公用尾文件
  → FTP 下载：curl -sL ftp://域名/wwwroot/mobile/foot.asp -u "用户:密码" -o 本地文件

第④步：找到地址的源头
  → 查手机版 index.asp 末尾的 <!--#include file="xxx" --> 找到 footer 文件名
  → 修改 footer 里的地址文本

第⑤步：给手机版加 JSON-LD（和 PC 版保持一致）
  → 下载手机版首页
  → 在 </head> 前插入 JSON-LD（地址字段务必用新地址）
  → FTP 上传

第⑥步：全面扫描旧地址残留
  → curl -s http://域名/xxx | grep '旧地址关键词' 扫全站所有页面
  → 手机版的所有子页面（about.html, contact.html 等）也要扫
  → 旧地址关键词通常是搬走前的地址（如：白塔东路、容创意园等）
```

### 关键文件模式

| 类型 | 文件位置 | 说明 |
|:--|:--|:--|
| PC 版首页 | `wwwroot/index.asp` | JSON-LD 在这里 |
| 手机版首页 | `wwwroot/mobile/index.asp` | ⚠️ 容易被忽略 |
| 手机版 footer | `wwwroot/mobile/foot.asp` | 地址文本在这里（include 引入） |
| 手机版其他页面 | `wwwroot/mobile/about.html` 等 | 共用 foot.asp，地址自动更新 |
| 根目录备份 | `index.asp`（FTP 根目录） | 同步副本，忘了它也无伤大雅 |

### 旧地址残留扫描（改完新地址后必做）

```bash
# 扫描全站所有页面是否还有旧地址残留
# 替换下方关键词为实际旧地址
curl -s http://域名/ | grep '白塔东路'
curl -s http://域名/mobile/ | grep '白塔东路'
curl -s http://域名/mobile/about.html | grep '白塔东路'
curl -s http://域名/mobile/contact.html | grep '白塔东路'
curl -s http://域名/mobile/foot.asp | grep '白塔东路'

# 结果为空=全站已更新
# 有内容=该页面还有漏改
```

注意：纯 ASP 静态站没有数据库，地址写死在 .asp / .html 文件中，所以直接扫页面 HTML 文本即可。

## 🚨 重要前提：先验证网站所有权

**在部署 JSON-LD 之前或之后，必须先让 Google 知道「这是我的网站」。**

### Google Search Console 所有权验证操作步骤

第①步：登录 Google Search Console → 添加资源 → 输入域名
第②步：选「HTML 文件」验证 → 下载 `googleXXXX.html` 文件
第③步：FTP 上传到网站根目录（`wwwroot/`）
第④步：回 GSC 点「验证」→ Google 访问 `http://域名/文件名` 确认存在

**不验证的后果：**
- Rich Results Test 只能跑一次性 URL 检测
- 看不到后台积累的索引/搜索/报错数据
- 无法提交 sitemap
- 无法追踪 GEO 优化前后变化

---

## 🚨 Google Rich Results Test 常见报错（2026.5.26 实战）

### 报错 1：`未填写字段 "image"（非常严重）`

**原因：** `AccountingService` 是 `LocalBusiness` 的子类型，Google 要求 `LocalBusiness` 必填 `image`。

**修复：** 在 JSON-LD 的 `AccountingService` 节点内加 `"image"` 字段，值为网站真实品牌 Logo 的绝对 URL：
```json
"image": "http://www.yingxinkuaiji.com/images/logo_2.png",
```
不要用 SVG、Base64 或第三方 CDN 链接。

### 报错 2：`@id` / `url` 协议不匹配

**现象：** 网站用 `http://`，但 JSON-LD 内的 `@id` 和 `url` 写了 `https://`。Google 按协议匹配解析，不一致会导致识别异常。

**修复：** 统一为网站实际协议：
```
"@id": "http://www.yingxinkuaiji.com/#organization",
"url": "http://www.yingxinkuaiji.com",
```

**扫描：** `curl -s http://域名 | grep -oP '"@?id"?\s*:\s*"https://[^"]+'`

### 报错 3：中文弯引号混入 JSON（炸解析的隐形杀手）

**现象：** 从 360 浏览器、Word 或 WPS 复制内容到 JSON 时，中文全角引号 `""`（U+201C/U+201D）替换了英文半角 `""`（U+0022），`json.loads()` 直接爆炸。

**检出命令：**
```bash
python3 -c "
import json
with open('index.asp') as f: c = f.read()
s = c.find('{', c.find('application/ld+json'))
e = c.find('</script>', s)
for i,ch in enumerate(c[s:e]):
    if ch in '\u201c\u201d\u2018\u2019':
        print(f'中文引号在偏移 {i}: ...{repr(c[s+max(0,i-20):s+i+20])}...')
"
```

**预防：** 编辑 JSON 用 VS Code/Sublime/Notepad++，不用 Word/360浏览器/WPS。

### 报错 5：Rich Results Test 报「无法编入索引」或「无法测试此网址」（代码本身正确时）

**现象：** JSON-LD 格式和字段齐全，`curl` 测试页面能正常返回 200，但 Rich Results Test 报「无法编入索引，无法测试此网址」。

**典型错误信息（2026.5.26 实战）：**

```
抓取失败时间：2026年5月26日 19:44:46
所用用户代理: Google 检查工具 智能手机版
是否允许抓取？是
网页抓取: error
失败：Robots.txt 无法访问
是否允许编入索引？不适用
```

注意这个错误很具欺骗性——它说「Robots.txt 无法访问」，但实际测试 robots.txt 是可正常访问的。原因是 Google Rich Results Test 的测试 IP 段被服务器防火墙拦截，导致 Google 无法连接到服务器来确认 robots.txt 内容，于是报了这个错误。

**可能原因（按概率排序）：**

| 原因 | 概率 | 说明 |
|:-----|:-----|:-----|
| 🔴 服务器/防火墙拦截了 Google 测试爬虫 IP | 最高 | Rich Results Test 的测试 IP 段与 Googlebot 网页爬虫的 IP 段不同，不少国内 IIS 服务器对测试 IP 做了限制 |
| 🟡 网站使用 HTTP（非 HTTPS） | 中 | Rich Results Test 更偏好 HTTPS 站点，纯 HTTP 站点间歇性报「无法测试」|
| 🟡 Search Console 未验证站点所有权 | 中 | 未验证的域名在测试工具中受限 |
| 🟢 Robots.txt 语法错误导致解析失败 | 中 | 参考下方「robots.txt 格式陷阱」|
| 🟢 Google 工具临时性 Bug | 低 | 偶发性问题，换个时间重试或换个工具即可 |

**诊断方法：**

```bash
# ① 确认 Googlebot 能正常访问
curl -s -o /dev/null -w '%{http_code}' \
  -A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' \
  http://www.yingxinkuaiji.com/
# 返回 200 → 说明 Googlebot 畅通

# ② 确认无 noindex 标签
curl -s http://域名 | grep -i 'noindex\|nofollow'
# 没有输出 → 无拦截

# ③ 检查 robots.txt（注意：根目录和子目录下可能各有一个）
curl -s http://域名/robots.txt
echo "---"
curl -s http://域名/wwwroot/robots.txt  # 部分 IIS 的 wwwroot 子目录可能另有 robots.txt

# ④ 检查 robots.txt 语法是否正确（常见错误：Allow: * 而非 User-agent: *）
curl -s http://域名/robots.txt | head -5
```

### ⚠️ Robots.txt 格式陷阱（2026.5.26 实战）

**错误写法（被 Google 忽略或报错）：**
```
Allow: *
Disallow: /asps/
```
`Allow: *` 是无效语法。正确写法：
```
User-agent: *
Disallow: /asps/
```
**说明：** `Allow` 和 `Disallow` 都是路径指令，不是用户代理声明。第一行 `User-agent: *` 声明「以下规则适用于所有爬虫」，然后 `Disallow: /asps/` 禁止爬取该目录。`Allow: *` 会被视为允许访问路径名为 `*` 的资源，不代表「允许所有」。

**双目录检查：** yingxinkuaiji.com 的 FTP 结构有 `wwwroot/` 子目录存放真实网站文件，但访问 `http://域名/robots.txt` 时返回的是根目录下的 `robots.txt`。如果只改 `wwwroot/robots.txt` 而没改根的，不会生效。确认方式：访问 `http://域名/robots.txt` 检查返回内容。

**解决方案（选其一即可）：**

1. 不用 Rich Results Test，改用 **Search Console 网址检查** — 在 GSC 搜索栏输入首页 URL → 点「测试已发布网址」→ Google 会抓取并报告结构化数据状态（实际爬取，不走测试 IP）
2. 改用 **Schema.org 官方 Validator** — https://validator.schema.org/#url=http://域名/（对 HTTP 更友好）
3. 从 HTML 内容中提取 JSON-LD 离线验证（最可靠）：`python3 -c "import json; c=open('index.asp').read(); s=c.find('{',c.find('ld+json')); e=c.find('</script>',s); json.loads(c[s:e])"` → 无异常即格式正确

**核心判断原则：** 用 HTTP 工具（curl/wget）能正常返回 200 的页面 = Google 实际爬虫也能访问。Rich Results Test 报「无法编入索引」≠ 网站真的被 Google 拦了，更大概率是测试工具的 IP/协议受限。只要 Search Console 网址检查能跑出结构化数据结果，就算通过。

### 完整报错索引表

| 报错 | 常见原因 | 快速修复 |
|:-----|:---------|:---------|
| 未填写字段 "image"（非常严重） | `LocalBusiness` 子类型缺 image | 加网站 Logo 绝对 URL |
| @id / url 协议不匹配 | JSON-LD 写 https，网站实际 http | 统一为 `http://` |
| 中文弯引号炸解析 | 从 Word/WPS 复制的内容混入全角引号 | 用纯文本编辑器改 |
| 双版本字段不一致 | PC/手机版 schema 不同步 | 两版 core fields 同步为一致值 |
| 无法编入索引（代码正确时） | 测试 IP/协议受限（见报错5详解） | 换 GSC 网址检查或 Schema.org Validator |

### 报错 4：PC/手机双版本字段不一致

**现象：** PC 版 `priceRange: "面议"`，手机版 `priceRange: "¥"`。AI 抓取双版本时拿到矛盾数据，削弱信任。

**修复：** 两版核心字段（name, description, founder, priceRange, address, telephone, areaServed）必须完全一致。

**检查：**
```bash
curl -s http://域名 | grep -oP '"priceRange"\s*:\s*"[^"]+'
curl -s http://域名/mobile/ | grep -oP '"priceRange"\s*:\s*"[^"]+'
```

### 通用 JSON-LD 验证命令（改完必跑）

```bash
python3 -c "
import json, sys
with open('index.asp') as f: c = f.read()
start = c.find('{', c.find('application/ld+json'))
end = c.find('</script>', start)
text = c[start:end-1]
try:
    obj = json.loads(text)
    print('JSON 格式正确 ✅')
    if '@graph' in obj:
        for item in obj['@graph']:
            print(f'  - {item[\"@type\"]} | image: {item.get(\"image\", \"❌\")}')
    else:
        print(f'类型: {obj.get(\"@type\")} | image: {obj.get(\"image\", \"❌\")}')
except json.JSONDecodeError as e:
    print(f'JSON 格式错误 ❌: {e}')
    sys.exit(1)
"
```

---

## 部署后验证五步骤（含 GSC）

1. **手机版验证：** `curl -s http://域名/mobile/ | grep 'application/ld+json' | wc -l`
2. **PC 版验证：** `curl -s http://域名/index.asp | grep 'application/ld+json' | wc -l`
3. **Google Search Console 所有权验证** — 上传验证文件 → 点击验证 → 确认通过
4. **Google Rich Results Test** 贴首页 URL 测试（HTTPS 异常则跳过）
5. **字段级验证（2026.5.26 新增）：** 上传后检查关键字段是否已生效：
   ```bash
   curl -s http://域名 | grep -o '"image": "[^"]*"'
   curl -s http://域名/mobile/ | grep -o '"image": "[^"]*"'
   curl -s http://域名 | grep -o '"priceRange": "[^"]*"'
   curl -s http://域名/mobile/ | grep -o '"priceRange": "[^"]*"'
   ```
   确认两版 `image` 和 `priceRange` 值一致。
6. 过 24-48 小时后在多个 AI 平台搜品牌词观察变化

## 格式要求

使用 `@context` + `@type` JSON-LD，通过 `<script type="application/ld+json">` 嵌入。不推荐 Microdata 格式，JSON-LD 对 AI 搜索引擎最友好。

## 完整代码模板

见 `templates/jsonld-accounting-firm-full.json`
