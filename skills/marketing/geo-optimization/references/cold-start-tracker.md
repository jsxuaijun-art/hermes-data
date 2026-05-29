# GEO 冷启动项目追踪 — 苏州盈信财税

> **用途：** 记录 GEO 冷启动各阶段的完成进度，方便断点续传。每次推进后更新此文件。
> **关联技能：** `geo-optimization`（方法论）、`ftp-static-site-editing`（官网编辑）、`short-video-industry-flow`（行业自然流短视频）

---

## 总进度概览

| 模块 | 状态 | 负责人 | 备注 |
|:-----|:-----|:-------|:-----|
|| 知乎账号注册+认证 | ✅ 完成 | 江姐 | ✅ 已通过，已发布2篇文章 |
|| 官网信息统一更新 | ✅ 完成 | AI | 联系方式、地址已更新 |
| JSON-LD PC 版 | ✅ 完成 | AI | 已添加 Organization + FAQPage |
| Google Search Console 验证 | ✅ 完成 | AI | DNS TXT 因 apex CNAME 冲突失败 → HTML 文件验证通过 |
| JSON-LD 手机版 | ✅ 完成 | AI | 补 image 字段 + priceRange 统一为"面议" |
| 手机版地址更新 | ✅ 完成 | AI | foot.asp 已改为平泷路 |
| JSON-LD image 字段修复 | ✅ 完成 (2026.5.26) | AI | Rich Results Test 报"未填写 image" → PC/手机两版补了 image + 统一 http:// 协议 + priceRange 统一为"面议" |
| FTP 上传 | ✅ 完成 (2026.5.26) | AI | curl -T 直接上传到 wwwroot/index.asp 和 wwwroot/mobile/index.asp |
| 全站旧地址检查 | ✅ 完成 (2026.5.28) | AI | 已下载17页PC版+3页手机版asp全量扫描，无旧地址残留 |
| sitemap.xml 升级 | ✅ 完成 (2026.5.28) | AI | 18→80个URL，新增新闻详情页、手机版页面等 |
| 提交 sitemap 到 GSC | 需你操作 | 你 | GSC → Sitemaps → 输入 `sitemap.xml` → 提交 |
| Rich Results Test 卡住 | ✅ 已分析确认 | AI | 不是代码问题，是服务器防火墙封锁了测试IP |
| **赔付承诺部署（三重）** | ✅ 完成 (2026.5.28) | AI | PC版+H5版+JSON-LD同步添加，详见 geo-commitment-deployment.md |
| **5A级代理记账机构研究** | ✅ 完成 (2026.5.29) | AI | 结论：盈信不适用5A级（硬门槛：年营收≥1000万/专职会计≥50人/客户≥3000户/全国仅5家）。详见 `references/5a-research.md` |

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

#### 4. Google Search Console 所有权验证 ✅
- DNS TXT 验证失败 — 根域名 CNAME + TXT 冲突（RFC 1034）
- 解决方案：HTML 文件验证 → 下载 `googleXXX.html` → FTP 上传到 `wwwroot/` → 通过

#### 5. JSON-LD 手机版 ✅
- 手机版 `/mobile/index.asp` 补 JSON-LD
- 修复：`image` 字段 + `priceRange` 统一为"面议"

#### 6. 手机版地址更新 ✅
- 手机版 foot.asp 地址已改为"平泷路"

#### 7. 全站旧地址检查 ✅
- 17页PC版+3页手机版全量扫描，无旧地址残留

#### 8. 赔付承诺三重部署 ✅ (2026.5.28)
- 操作：PC版首页 + 手机版首页 + JSON-LD FAQPage 同步添加"因我方记账失误导致企业产生罚款的，全额承担赔偿"
- 方法见 `references/geo-commitment-deployment.md`

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

- `references/geo-commitment-deployment.md` — GEO 关键承诺三重部署模式（PC+H5+JSON-LD）
- `references/jsonld-website-schema.md` — JSON-LD 代码模板和部署细节
- `references/dns-ownership-verification.md` — DNS 所有权验证实战
- `geo-optimization` — GEO 方法论总览
- `ftp-static-site-editing` — FTP 编辑工作流