# Google Search Console 域名所有权验证 — DNS/HTML 双方案实战手册

## 场景：根域名（apex domain）验证失败

**症状：** 在 Google Search Console 添加 `yingxinkuaiji.com`（无 www），选择 DNS TXT 验证，添加记录后 GSC 反复报"验证失败"。

**根因：** **CNAME 记录与 TXT 记录在 apex 域名的冲突。**

| DNS 记录类型 | 在 apex 域名上 | 问题 |
|:--|:--|:--|
| CNAME | `@  IN  CNAME  www.yingxinkuaiji.com` | ⚠️ RFC 1034 禁止 apex 与其他记录共存 |
| TXT | `@  IN  TXT  "google-site-verification=xxx"` | 同上 apex，无法共存 |

**解释：** DNS 规范规定，如果 apex 域名（裸域名，不带 www）存在 CNAME 记录，则该域名**不得存在任何其他记录类型**（SOA/NS 除外）。所以 TXT 记录虽然添加了，DNS 解析器不会返回它。

---

## 救援方案：HTML 文件验证

当 DNS TXT 因 CNAME 冲突不可用时，换 HTML 文件验证即可。

### 操作步骤

```
第①步：GSC → 添加资源 → 输入域名 → 选「HTML 文件」验证
第②步：下载 `googleXXXXXXX.html` 文件
第③步：FTP 上传到网站实际根目录（不是 FTP 根目录）
第④步：回到 GSC 点「验证」
第⑤步：GSC 请求 http://域名/googleXXXXXXX.html → 存在即通过
```

### ⚠️ 关键陷阱

| 陷阱 | 说明 | 预防 |
|:--|:--|:--|
| **根目录不对** | 中文 ASP 站常有 FTP 根目录和实际网站根目录两层 | 上传前 `curl http://域名/file.html` 确认文件能访问到 |
| **文件名不要改** | 文件名就是验证令牌，改了 GSC 不认 | 直接上传原文件名 |
| **TLS 不影响** | HTML 验证走 HTTP 即可，HTTPS 证书过期不影响 | 用 `http://域名/文件名` 访问确认 |
| **验证通过后文件别删** | 删了 GSC 会掉所有权 | 保留在根目录，忽略它 |

### 验证确认

```bash
# 上传后确认可访问
curl -s http://域名/googleXXXXXXX.html

# 返回文件内容 = 成功
# 返回 404/403 = 路径不对，调整目录
```

---

## 为什么这属于 GEO 工作

| GEO 环节 | 关联 |
|:--|:--|
| JSON-LD 部署 | 需要 GSC 验证后才能用 Rich Results Test 持续追踪 |
| 网站状态监控 | GSC 提供索引/报错数据，是 GEO 效果评估入口 |
| Schema.org 标记 | 只能在已验证的网站上检查结构化数据健康度 |
| Sitemap 提交 | GSC 验证后才能提交 sitemap 加速收录 |

**一句话：** GSC 所有权验证是 GEO 基建的"前提的前提"——没验证，后面所有技术优化都查不到效果。

---

## 相关知识

- 腾讯 DNS 解析（DNSPod）：支持 CNAME 加速（只针对国内线路），不影响国外 DNS 查询
- 西部数码 DNS：纯标准 DNS，不支持 CNAME 与 TXT 共存
- 如果无法上传文件到网站（纯 API 站/无服务器站），可尝试 Google Tag Manager 或 Google Analytics 验证——需要网站支持添加跟踪代码

## 与 JSON-LD 手册的关联

该文件与 `references/jsonld-website-schema.md` 配合使用：
1. 先按本文完成 GSC 所有权验证
2. 再按 jsonld-website-schema.md 部署 JSON-LD
3. 验证后回 GSC 查看 Rich Results 报告
