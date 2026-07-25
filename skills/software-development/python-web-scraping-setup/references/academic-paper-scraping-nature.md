# 学术论文爬取：Nature 期刊家族实战（更新 2026.7.13）

## 目标

从 Nature 系列期刊获取论文信息：
- 元数据（标题、DOI、发表时间、作者、机构）
- 摘要（Abstract）
- Key Points（Nature Reviews 系列特有）
- Supplementary PDF
- References

## 核心原则

### 1. 先查 PubMed，确认论文状态

```python
from curl_cffi import requests
import re

# PubMed 搜索（DOI 或标题）
r = requests.get(
    f'https://pubmed.ncbi.nlm.nih.gov/?term={doi}&format=pubmed',
    impersonate='chrome120', timeout=15
)

pmc = re.search(r'PMC\d+', r.text)
if pmc:
    print(f'✅ PMC ID: {pmc.group(0)} — 可免费获取全文')
else:
    print('❌ 无 PMC ID — 非开放获取，大概率有 paywall')
```

**三种状态**：
| PubMed 状态 | 含义 | 行动 |
|-------------|------|------|
| 有 PMC ID | 开放获取/已存档 | 直接去 PubMed Central 下全文 PDF |
| 无 PMC ID，新发表 (<6月) | 付费墙，出版商独占期 | 只能捡免费碎片 |
| 无 PMC ID，发表>12月 | 可能已解锁但未入PMC | 检查作者存档/ResearchGate |

### 2. DOI 直链 → Nature 文章页（不要用搜索引擎绕路）

```python
s = requests.Session()
s.get('https://www.nature.com', impersonate='chrome120', timeout=10)
r = s.get(f'https://www.nature.com/articles/{doi}', impersonate='chrome120', timeout=15)
```

### 3. 源头和引用统一用 DOI 格式

DOI 号是唯一的，反爬的 x-meta 和搜索引擎都统一靠它。写 curl_cffi/Playwright 目标文件时，**明确引用 `s41571-026-01165-8` 的 `10.1038/` 前缀，不要写成小说**。

---

## 工作流 A：公开/免费文章

### 1. 元数据层 — curl_cffi + HTML meta tags

Nature 在原始 HTML 中埋了充足的 `meta` 标签（不需JS渲染）：

```python
metas = re.findall(r'<meta name="([^\"]+)" content="([^\"]+)"', text)
for name, content in metas:
    if name.startswith('citation_'):
        print(f'{name}: {content}')
```

**可直接获取字段**：
`citation_title`, `citation_author`, `citation_author_institution`, `citation_journal_title`, `citation_online_date`, `citation_pdf_url`, `citation_doi`, `citation_firstpage`/`citation_lastpage`, `citation_article_type`

### 2. 验证层 — Crossref API

```python
r = requests.get(f'https://api.crossref.org/works/{doi}', timeout=10)
data = r.json()
msg = data['message']
print(f'标题: {msg["title"][0]}')
for a in msg.get('author', []):
    print(f'作者: {a.get("given","")} {a.get("family","")}')
```

### 3. 内容层 — Playwright（domcontentloaded）

Nature 页面加载大量第三方 JS（广告、追踪、社交媒体），如果用 `wait_until='networkidle'` 会超时。

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto(url, wait_until='domcontentloaded', timeout=20000)  # ⚠️ 不能用 networkidle
```

## 工作流 B：付费墙文章（本文核心新增！）

当页面显示 "This is a preview of subscription content" 或 "Subscribe required" 时，进入**付费墙模式**——拿不到正文 PDF，但能捡回所有免费碎片。

### B1：捡免费碎片清单

| 碎片 | 能否免费拿到 | 获取方式 |
|------|------------|----------|
| Abstract | ✅ 总是免费 | 页面 HTML / meta `citation_abstract` |
| Key Points (Nature Reviews) | ✅ 总是展示 | Playwright 渲染后提取 |
| Supplementary PDF | ✅ 总是免费 | 页面上的`a[href$=".pdf"]` 直链 |
| References | ✅ 总是可见 | 页面底部 `<ol>` |
| 全文 HTML 正文 | ❌ 付费墙后 | 被 paywall 遮挡 |
| 全文 PDF | ❌ 单篇 €39.95 | 需购买 |
| 作者存档 | ⚠️ 不一定有 | 查 PubMed / ResearchGate / 机构官网 |

### B2：捡 Supplementary PDF

```python
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    # 启动浏览器
    ...
    page.goto(url, wait_until='domcontentloaded')
    
    # 提取 PDF 链接
    pdf_links = page.evaluate('''() => {
        const links = document.querySelectorAll('a[href$=".pdf"]');
        return Array.from(links).map(a => ({ text: a.innerText.trim(), href: a.href }));
    }''')
    
    for l in pdf_links:
        print(f'{l["text"]}: {l["href"]}')
```

下载：

```python
from curl_cffi import requests
r = requests.get(pdf_url, impersonate='chrome120', timeout=30)
if r.content[:5] == b'%PDF-':  # 确认是 PDF
    with open(path, 'wb') as f:
        f.write(r.content)
```

### B3：提取 Key Points（Nature Reviews 系列专有）

```python
keypoints_text = page.evaluate('''() => {
    const heading = Array.from(document.querySelectorAll('h2, h3, strong'))
        .find(el => el.innerText.trim() === 'Key points');
    if (!heading) return '';
    let container = heading;
    for (let i = 0; i < 4; i++) {
        if (container.parentElement) container = container.parentElement;
    }
    return container.innerText;
}''')
```

有时 Key Points 没有唯一容器 ID（嵌入在普通段落中）。备选方案：搜索关键词"China is a major contributor"等特征句。

### B4：提取 Abstract

```python
abstract_text = page.evaluate('''() => {
    const abs = document.querySelector('#Abs1-content, [data-test="abstract-text"], .c-article-abstract');
    return abs ? abs.innerText : '';
}''')
```

### B5：提取 References

```python
refs_text = page.evaluate('''() => {
    const refs = document.querySelector('ol.c-article-references-list, ol[data-test="references"]');
    if (!refs) return '';
    return Array.from(refs.querySelectorAll('li')).map(li => li.innerText).join('\\n\\n');
}''')
```

### B6：提取 Supplementary PDF 中的文本

```python
import subprocess
# pdftotext（需要系统安装 poppler-utils）
result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], 
                       capture_output=True, text=True, timeout=15)
text = result.stdout
```

## 翻译输出规范

当拿不到全文 PDF 但捡回了多个免费碎片时，**统一组织为结构化中英对照文档**：

### 输出文件清单

| 文件 | 内容 |
|------|------|
| `{doi}_KeyPoints_中英对照.md` | Key Points 6条 + Abstract 全文中英对照 |
| `{doi}_Supplementary_中英对照.md` | 所有附表 + 文本框的中英翻译 |
| `{doi}_Supplementary.pdf` | 原始 PDF（原封不动） |

### Key Points + Abstract 翻译格式示例

```markdown
# 标题
# 中文标题
## Key Points / 核心要点

**KP1**
EN: ...
CN: ...

---

**Abstract / 摘要**
EN: ...
CN: ...
```

### Supplementary 翻译格式

表格类：
```markdown
## Supplementary Table 1 | 英文标题
## 附表1 | 中文标题

| 英文列 | 中文列 | 数值 | 说明 |
|--------|--------|------|------|
| Lung   | 肺     | 25.3 | ASMR |
```

文本框类（无表格）：
```markdown
## Supplementary Box 1 | 英文标题
## 补充框1 | 中文标题

### 个人层面 / Individual level
- 🟡 英文
- 🟡 中文
```

## 已知坑点

### Nature 搜索反爬
- **中文搜索** → 直接 CAPTCHA
- **最佳路径**：知道 DOI 直接访问文章页，不要搜

### Playwright `networkidle` 超时
Nature 页面至少加载 30+ 第三方资源。`networkidle` 永远不会触发。只能用 `domcontentloaded`。

### JSON-LD 结构化数据不可靠
多个 `<script type="application/ld+json">` 块，curl_cffi 拿到的原始 HTML 中部分为空。
**用 `citation_*` meta 标签代替**。

### Supplementary PDF 文本提取
`pdftotext` 需要 `poppler-utils` 包。WSL 可能未安装，先检查：
```bash
which pdftotext || sudo apt-get install -y poppler-utils
```

### PubMed 响应含 paywall 信息
PubMed 响应文本中查找 "Subscribe required" 比找 PMC ID 更直接：
- 有 PMC ID = 全文免费
- 无 PMC ID + "Subscribe required" = 付费墙
- 无 PMC ID + 无订阅提示 = 需进一步检查

## 工具选择对比

| 工具 | 元数据 | 摘要 | Key Points | Supplementary | 稳定性 | 是否需要浏览器 |
|------|--------|------|------------|---------------|--------|--------------|
| curl_cffi | ✅ citation_* meta | ❌ 需JS渲染 | ❌ | ❌ | ✅ 高 | ❌ |
| Crossref API | ✅ 作者列表 | ❌ | ❌ | ❌ | ✅ 极高 | ❌ |
| Playwright domcontentloaded | ✅ | ✅ | ✅ | ✅ 链接发现 | ⚠️ 依赖浏览器 | ✅ |
| pdftotext | ❌ | ❌ | ❌ | ✅ 文本提取 | ✅ 工具存在时 | ❌ |

## 已记录案例索引

| 日期 | DOI | 状态 | 输出 |
|------|-----|------|------|
| 2026.7.6 | 六合一工作流（公开文章） | ✅ 全部免费 | 见 SKILL.md 原文 |
| **2026.7.13** | **10.1038/s41571-026-01165-8** | **🔒 付费墙** | **KeyPoints + Supplementary 中英对照** |
