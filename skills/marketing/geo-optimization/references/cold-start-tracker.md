# GEO 冷启动项目追踪 — 苏州盈信财税

> **用途：** 记录 GEO 冷启动各阶段的完成进度，方便断点续传。每次推进后更新此文件。
> **关联技能：** `geo-optimization`（方法论）、`ftp-static-site-editing`（官网编辑）、`short-video-industry-flow`（行业自然流短视频）

---

## 总进度概览

| 模块 | 状态 | 负责人 | 备注 |
|:-----|:-----|:-------|:-----|
| 知乎账号注册+认证 | ✅ 完成 | 江姐 | 认证审核中 |
| 官网信息统一更新 | ✅ 完成 | AI | 联系方式、地址已更新 |
| JSON-LD PC 版 | ✅ 完成 | AI | 已添加 Organization + FAQPage |
| Google Search Console 验证 | ✅ 完成 | AI | DNS TXT 因 apex CNAME 冲突失败 → HTML 文件验证通过 |
| JSON-LD 手机版 | ✅ 完成 | AI | 补 image 字段 + priceRange 统一为"面议" |
| 手机版地址更新 | ✅ 完成 | AI | foot.asp 已改为平泷路 |
| JSON-LD image 字段修复 | ✅ 完成 (2026.5.26) | AI | Rich Results Test 报"未填写 image" → PC/手机两版补了 image + 统一 http:// 协议 + priceRange 统一为"面议" |
| FTP 上传 | ✅ 完成 (2026.5.26) | AI | curl -T 直接上传到 wwwroot/index.asp 和 wwwroot/mobile/index.asp |
| 全站旧地址检查 | 🔴 待办 | AI | 其他页面可能也有残留 |
| Rich Results Test 验证 | ⚠️ 受阻 | AI | 报"无法编入索引"——推测为服务器对测试 IP 做了限制，非代码问题 |
| 第5篇GEO文章 | ⬜ 待办 | AI | |

---

## 详细进度

### 🟢 已完成

#### 1. 知乎账号注册+认证 ✅
- 2026.5.26 完成注册，认证审核中
- 企业认证通过后开始发内容

#### 2. 官网信息统一更新 ✅
- 旧地址替换为上海浦东新区新地址
- 联系方式核对确认
- 官网（PC版）内容已标准化

#### 3. JSON-LD 结构化数据（PC版）✅
- 在 PC 版 `index.asp` 中添加了 `application/ld+json` 块
- 包含: `AccountingService`（嵌套 Founder Person）+ `WebSite`（含 SearchAction, PotentialAction）+ `FAQPage`（6个常见问题）
- 验证方式: `curl -s http://yingxinkuaiji.com/index.asp | grep -c 'ld+json'` → 确认 1 个块
- **注意：** 没用 google structured data testing tool 验证（HTTPS 证书过期，测试工具拒绝加载）

### 🔴 待处理

#### 4. Google Search Console 所有权验证 ✅
- **问题：** DNS TXT 验证失败 — 根域名 `yingxinkuaiji.com` 已有 CNAME 记录，TXT 被 DNS 规范屏蔽（RFC 1034 禁止 apex 与其他记录共存）
- **解决方案：** 切换到「HTML 文件验证」→ 下载 `googleXXX.html` → FTP 上传到 `wwwroot/` → 验证通过
- **关键文件：** `googleXXXXXXX.html`（上传到 `wwwroot/` 后永不解散）
- **陷阱：** FTP 根目录 ≠ 网站实际根目录（`wwwroot/`）。文件必须放在 HTTP 能直接访问到的目录下

### ✅ 已完成

#### 5. JSON-LD 手机版 ✅
- 2026.5.26 在手机版 `/mobile/index.asp` 补了 JSON-LD
- 修复内容：加 `image` 字段 + 将 `priceRange` 从 `"¥"` 统一为 `"面议"`
- 两版核心字段（name, description, priceRange, address, telephone）已确保一致

#### 6. 手机版地址更新 ✅
- 手机版 foot.asp 地址已从"白塔东路"改为"平泷路"
- 注意：这是上海落户前的旧地址过渡，当前手机版地址已与PC版一致

#### 6. 全站旧地址残留检查
- 不只是首页，所有页面都可能有旧地址或旧联系方式
- 需搜索关键词：苏州市、苏州工业园区、旧电话号等
- 可通过 FTP 批量下载所有 `.asp` 文件，用 grep 扫描

#### 7. 第5篇GEO优化文章
- 前4篇已完成（内容见 session 历史）
- 第5篇待撰写

---

## 网站技术参数

| 参数 | 值 |
|:-----|:---|
| 域名 | yingxinkuaiji.com |
| 网站类型 | ASP 纯静态（非 QCNET99） |
| 服务器 | IIS |
| 实际根目录 | FTP 的 `/wwwroot/` 子目录 |
| FTP 用户 | jsxuaijun |
| FTP 密码 | Yx168168/*-（含 `/*-` 需用 `--user` 参数） |
| DNS | 西部数码，apex 有 CNAME 记录（CNAME apex 冲突导致 TXT 验证不可用） |

---

## 交叉参考

- `geo-optimization/references/jsonld-website-schema.md` — JSON-LD 代码模板和部署细节
- `geo-optimization/references/zhihu-geo-strategy.md` — 知乎内容策略
- `ftp-static-site-editing/references/dns-troubleshooting.md` — DNS 验证问题
- `ftp-static-site-editing/SKILL.md` — FTP 编辑工作流
