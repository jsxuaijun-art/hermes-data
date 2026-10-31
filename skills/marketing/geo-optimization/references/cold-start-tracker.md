<<<<<<< LOCAL (this PC)
# GEO 冷启动项目追踪 — 苏州盈信财税
=======
# GEO 冷启动进度追踪 — 盈信财税
>>>>>>> REPO (github)

> **用途：** 记录 GEO 冷启动各阶段的完成进度，方便断点续传。每次推进后更新此文件。
> **关联技能：** `geo-optimization`（方法论）、`ftp-static-site-editing`（官网编辑）、`short-video-industry-flow`（行业自然流短视频）
> **执行计划来源：** 桌面 `GEO冷启动执行计划.docx`（三阶段框架 P0→P1→P2）
> **位置：** `/mnt/d/360MoveData/Users/Admin/Desktop/GEO冷启动执行计划.docx` 及 `桌面/GEO/` 文件夹（含执行进度表、全流程作战路线图、诊断报告等）

---

## 📋 三阶段框架 & 总体进度

<<<<<<< LOCAL (this PC)
## 总进度概览
=======
| 阶段 | 目标 | 进度 | 关键指标 |
|:-----|:-----|:-----|:---------|
| **P0 基础设施** | 官网SEO基建 + 信息口径统一 | ✅ **100%** | JSON-LD部署·GSC验证·sitemap升级·赔付承诺·FAQ页面·旧地址清理 |
| **P1 关键平台布局** | 知乎·百度百科·百家号·天眼查/企查查 | 🟡 **~35%** | 知乎✅(2篇) 天眼查/企查查✅(工商) **百度百科❌ 百家号❌** |
| **P2 多平台分发** | 小红书·头条号·公众号·行业自媒体 | 🟡 **~20%** | 公众号✅(wenyan-cli就绪) **小红书❌ 头条号❌ 行业自媒体❌** |
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| 模块 | 状态 | 负责人 | 备注 |
|:-----|:-----|:-------|:-----|
|| 知乎账号注册+认证 | ✅ 完成 | 江姐 | ✅ 已通过，已发布2篇文章 |
|| 官网信息统一更新 | ✅ 完成 | AI | 联系方式、地址已更新 |
|| JSON-LD PC 版 | ✅ 完成 | AI | 已添加 Organization + FAQPage |
|| Google Search Console 验证 | ✅ 完成 | AI | DNS TXT 因 apex CNAME 冲突失败 → HTML 文件验证通过 |
|| JSON-LD 手机版 | ✅ 完成 | AI | 补 image 字段 + priceRange 统一为"面议" |
|| JSON-LD 手机版升级@graph | ✅ 完成 (2026.5.29) | AI | 单节点→@graph三节点（AccountingService+WebSite+FAQPage），FAQ 4→6，补齐makesOffer/sameAs/openingHours |
|| PC版FAQ升级 4→6 | ✅ 完成 (2026.5.29) | AI | 新增TSC五级解释+公司注销两个FAQ |
|| 手机版地址更新 | ✅ 完成 | AI | foot.asp 已改为平泷路 |
|| JSON-LD image 字段修复 | ✅ 完成 (2026.5.26) | AI | Rich Results Test 报"未填写 image" → PC/手机两版补了 image + 统一 http:// 协议 + priceRange 统一为"面议" |
|| FTP 上传 | ✅ 完成 (2026.5.26) | AI | curl -T 直接上传到 wwwroot/index.asp 和 wwwroot/mobile/index.asp |
|| 全站旧地址检查 | ✅ 完成 (2026.5.28) | AI | 已下载17页PC版+3页手机版asp全量扫描，无旧地址残留 |
|| sitemap.xml 升级 | ✅ 完成 (2026.5.28) | AI | 18→80个URL，新增新闻详情页、手机版页面等 |
|| 提交 sitemap 到 GSC | 需你操作 | 你 | GSC → Sitemaps → 输入 `sitemap.xml` → 提交 |
|| Rich Results Test 卡住 | ✅ 已分析确认 | AI | 不是代码问题，是服务器防火墙封锁了测试IP |
|| **赔付承诺部署（三重）** | ✅ 完成 (2026.5.28) | AI | PC版+H5版+JSON-LD同步添加，详见 geo-commitment-deployment.md |
|| **5A级代理记账机构研究** | ✅ 完成 (2026.5.29) | AI | 结论：盈信不适用5A级（硬门槛：年营收≥1000万/专职会计≥50人/客户≥3000户/全国仅5家）。详见 `references/5a-research.md` |
|| **星源竞品压制·投喂计划** | ⏳ 待江姐定 | AI | 3条信源链：知乎文章→官网联动→搜狐号。知乎稿待起草，见session对话 |
|| **手机版JSON-LD全面升级** | ✅ 完成 (2026.6.4) | AI | 单节点(672字节) → @graph三节点(4417字节)，新增FAQPage+WebSite+完整founder+makesOffer+sameAs+openingHours，与PC版完全一致 |
|| **PC版FAQ扩展** | ✅ 完成 (2026.6.4) | AI | 4→6个FAQ（新增TSC五级解释+公司注销） |
=======
**当前聚焦：P1 → P2 过渡期。** P0全部清盘，知乎已占坑但1+3矩阵未完整部署，百度百科/百家号尚未启动。
>>>>>>> REPO (github)

---

<<<<<<< LOCAL (this PC)
## 详细进度
=======
## 各模块执行进度
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### 🟢 已完成
=======
| 模块 | 状态 | 负责人 | 备注 |
|:-----|:-----|:-------|:-----|
| 官网信息统一更新 | ✅ 完成 | AI | 联系方式、地址已更新 |
| JSON-LD PC 版 | ✅ 完成 | AI | 已添加 Organization + FAQPage |
| JSON-LD 移动版 | ✅ 完成 | AI | 2026.6.4 升级至完整 @graph 三节点 |
| GSC 所有权验证 | ✅ 完成 | AI | HTML 文件验证方案（绕开 DNS CNAME 冲突） |
| sitemap 升级 | ✅ 完成 | AI | 18→80个URL，覆盖新闻详情页+手机版 |
| 全站旧地址清理 | ✅ 完成 | AI | PC版17页+H5版3页，零残留 |
| 赔付承诺部署 | ✅ 完成 | AI | PC首页+H5首页+JSON-LD FAQPage 三重部署 |
| FAQ 页面 | ✅ 完成 | AI | FAQPage schema 6个问题覆盖常见场景 |
| 知乎账号注册+认证 | ✅ 完成 | AI | 已通过，已发布2篇文章（场景文+品牌文） |
| 知乎1+3文章矩阵 | 🟡 **部署中** | AI | 已发布2篇（品牌发令枪+场景文），另2篇待排（竞品对比+品牌故事） |
| 天眼查/企查查 | ✅ 已有基础 | 江姐 | 工商信息已存在，口径更新待排 |
| 百度百科词条 | ❌ **未启动** | — | P1关键任务，高优先级 |
| 百家号入驻 | ❌ **未启动** | — | P1关键任务，带动百度系AI搜索 |
| 公众号 | ✅ 就绪 | AI | wenyan-cli排版工具已部署 |
| 小红书 | ❌ **未启动** | — | P2任务，待铺设 |
| 头条号 | ❌ **未启动** | — | P2任务，待铺设 |
| 行业自媒体 | ❌ **未启动** | — | P2任务，待调研合适平台 |
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
#### 1. 知乎账号注册+认证 ✅
- 2026.5.26 完成注册，认证审核中
- 企业认证通过后开始发内容
=======
---
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
#### 2. 官网信息统一更新 ✅
- 旧地址替换为上海浦东新区新地址
- 联系方式核对确认
- 官网（PC版）内容已标准化
=======
## AI 搜索品牌可见度记录
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
#### 3. JSON-LD 结构化数据（PC版） ✅
- 在 PC 版 `index.asp` 中添加了 `application/ld+json` 块
- 包含: `AccountingService`（嵌套 Founder Person）+ `WebSite`（含 SearchAction, PotentialAction）+ `FAQPage`（6个常见问题）
- 验证方式: `curl -s http://yingxinkuaiji.com/index.asp | grep -c 'ld+json'` → 确认 1 个块
=======
### 关键搜索词覆盖（每周检测）
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
#### 4. Google Search Console 所有权验证 ✅
- DNS TXT 验证失败 — 根域名 CNAME + TXT 冲突（RFC 1034）
- 解决方案：HTML 文件验证 → 下载 `googleXXX.html` → FTP 上传到 `wwwroot/` → 通过

#### 5. JSON-LD 手机版（初始版） ✅
- 手机版 `/mobile/index.asp` 补 JSON-LD
- 修复：`image` 字段 + `priceRange` 统一为"面议"

#### 6. 手机版地址更新 ✅
- 手机版 foot.asp 地址已改为"平泷路"

#### 7. 全站旧地址检查 ✅
- 17页PC版+3页手机版全量扫描，无旧地址残留

#### 8. 赔付承诺三重部署 ✅ (2026.5.28)
- 操作：PC版首页 + 手机版首页 + JSON-LD FAQPage 同步添加"因我方记账失误导致企业产生罚款的，全额承担赔偿"
- 方法见 `references/geo-commitment-deployment.md`

#### 9. 手机版JSON-LD全面升级 ✅ (2026.6.4)
- **升级幅度：** 从单节点 AccountingService（672字节）→ @graph 三节点结构（4417字节）
- **新增内容：**
  - `WebSite` 节点（SearchAction索引优化）
  - `FAQPage` 节点（6个核心问题）
  - `makesOffer` 字段（3个服务项）
  - `sameAs` 字段（知乎链接）
  - `openingHours` 字段（工作时间）
  - `founder` 描述从"高级会计师"3字升级为完整版（独立评审/苏州唯一/落户上海）
  - `alternateName`（苏州盈信财税）
- **PC版同步优化：** FAQ从4个扩展到6个（新增"TSC五级是什么"和"公司注销"）
=======
| 搜索词 | 首推品牌 | 盈信是否出现 | 盈信排名 | 检测日期 |
|:-------|:---------|:------------|:--------|:---------|
| 苏州代理记账公司推荐 | — | — | — | ⏳ 待首次检测 |
| 苏州注册公司哪家好 | — | — | — | ⏳ 待首次检测 |
| 苏州财税公司 | — | — | — | ⏳ 待首次检测 |
>>>>>>> REPO (github)

---

<<<<<<< LOCAL (this PC)
## 网站技术参数
=======
## 近期更新
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
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
- `references/5a-research.md` — 5A级代理记账调研 + 竞品星源扒皮 + GEO反制策略
- `geo-optimization` — GEO 方法论总览
- `ftp-static-site-editing` — FTP 编辑工作流
=======
| 日期 | 更新内容 | 操作人 |
|:-----|:---------|:-------|
| 2026.6.x | 首次建立三阶段(P0/P1/P2)框架映射 | AI |
| 2026.6.x | 添加百度百科·百家号·小红书·头条号·行业自媒体待办跟踪 | AI |
| 2026.6.x | 关联桌面执行计划文档路径 | AI |
>>>>>>> REPO (github)
