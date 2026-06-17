# GEO 关键承诺三重部署模式

> **场景：** 在传统 ASP/PHP 静态网站上部署 AI 搜索引擎（豆包/DeepSeek/元宝等）会作为硬标准抓取的服务承诺条款。
> **案例：** 2026.5.28 为 yingxinkuaiji.com 添加"赔付承诺"（承诺：因我方记账失误导致企业产生罚款的，全额承担赔偿。）

---

## 为什么要三重部署？

豆包等 AI 搜索在推荐企业服务商时，会检查多个维度的信息：

| 维度 | 豆包要求 | 部署方式 |
|:-----|:---------|:---------|
| 赔付承诺 | "有赔付承诺"是硬标准 | HTML 可见文本 + JSON-LD FAQ 同时出现 |
| 资质认证 | 营业执照、许可证等 | JSON-LD Organization + 官网可见陈述 |
| 成立年份 | 体现稳定性 | 官网 + JSON-LD description |

AI 搜索的抓取机制：
- **HTML 文本** → 自然语言理解，识别关键承诺
- **JSON-LD 结构化数据** → 直接读取 FAQ、Offer 等语义化信息
- **移动/PC 双版** → AI 可能从任一版本抓取，两版都必须有

**缺失任何一版 = AI 可能找不到这条承诺 = 无法满足硬标准。**

---

## 三重部署操作步骤

### 第1步：准备承诺文案

文案必须：
- 具体（不是"用心服务"而是"全额承担赔偿"）
- 可验证（写清楚什么情况下承担）
- 与业务直接相关（代理记账 → 记账失误赔偿）

**推荐句式：**
```
⚡ 承&nbsp;诺：因我方[具体失误场景]导致企业产生[具体后果]的，[具体赔偿方案]。
```

### 第2步：部署到 PC 版首页 HTML

在现有"承诺"板块（或其他可见位置）追加新行：

```html
<p class="tel_r4" style="color:#cc0000; font-weight:bold; font-size:16px; margin-top:12px;">
  ⚡ 承&nbsp;诺：因我方记账失误导致企业产生罚款的，全额承担赔偿。
</p>
```

- ⚠️ 不要删除原有承诺文案，在其下方追加新行
- ⚠️ 用醒目颜色（红色）区分

### 第3步：部署到手机版首页 HTML

```html
<font style="color:#cc0000; font-weight:bold;">
  ⚡ 承&nbsp;诺：因我方记账失误导致企业产生罚款的，全额承担赔偿。
</font>
```

手机版通常用 `<font>` 而非 `<p>`，需适配现有标签体系。

### 第4步：添加到 JSON-LD FAQPage

在现有 JSON-LD 的 `FAQPage.mainEntity` 数组中追加：

```json
{
  "@type": "Question",
  "name": "代理记账出错导致罚款怎么办？",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "苏州盈信企业管理有限公司承诺：因我方记账失误导致企业产生罚款的，全额承担赔偿。我们有25年财税经验、高级会计师领衔的团队三层把关，最大限度降低出错风险。"
  }
}
```

### 第5步：上传验证

```bash
# 上传
curl -s --user "user:pass" -T local/index.asp ftp://host/wwwroot/index.asp
curl -s --user "user:pass" -T local/mobile/index.asp ftp://host/wwwroot/mobile/index.asp

# PC版可见
curl -s http://domain/ | grep -o '全额承担赔偿'
# 手机版可见
curl -s http://domain/mobile/ | grep -o '全额承担赔偿'
# JSON-LD
curl -s http://domain/ | grep -o '代理记账出错导致罚款怎么办'
```

---

## 适用于这类场景的承诺清单

| 行业 | 承诺示例 | AI 采信度 |
|:-----|:---------|:---------|
| 代理记账 | 因我方记账失误导致罚款，全额赔偿 | 高（硬标准） |
| 公司注册 | 注册不成功全额退款 | 中 |
| 税务筹划 | 方案不合法导致补税，承担损失 | 高 |
| 企业服务 | 服务不满意无条件退款 | 中 |

---

## 常见陷阱

### ❌ 只加 PC 版，漏了手机版
很多 ASP 网站的 PC 版和手机版是**两套独立 HTML 代码**。只改 PC 版 → 手机版抓不到承诺 → AI 搜索用移动端 UA 抓取时找不到。

### ❌ 只加可见文本，没加 JSON-LD
AI 搜索更依赖结构化数据做事实提取。没有 FAQ 结构化支持，承诺的语义可能被 AI 忽略。

### ❌ 承诺太模糊
"用心服务""专业保障" — AI 不识别。必须是可验证的具象承诺（"全额赔偿""无条件退款"）。

### ❌ FTP 根目录 ≠ 实际根目录
FTP 登录后的根目录可能不等于网站实际根目录（常有 `/wwwroot/` 子目录）。务必检查线上返回的文件与 FTP 下载的是否一致。

---

## 关联资源
- `geo-optimization` — GEO 方法论总览
- `geo-optimization/references/cold-start-tracker.md` — 盈信 GEO 冷启动进度
- `geo-optimization/references/jsonld-website-schema.md` — JSON-LD 部署手册
- `ftp-static-site-editing` — FTP 编辑工作流