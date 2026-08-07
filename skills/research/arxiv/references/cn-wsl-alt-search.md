# 国内 WSL 环境下的替代搜索方案

> 前提：WSL 在国内网络环境下，Google、DuckDuckGo 等搜索 API 被墙，
> 但以下 API 可直连：NCBI E-utilities (PubMed)、arXiv、GitHub API、Semantic Scholar

## 核心原则

当 `web_search` 工具不可用时：
1. **不要放弃**——「没有直接搜网页的工具，你就要在github或其他渠道里搜索然后下载」（用户原话）
2. **针对问题类型选择替代 API**：
   - 医学/临床/药物/疫苗 → **PubMed E-utilities**（见 `references/pubmed-ncbi-eutilities.md`）
   - CS/ML/物理/数学 → **arXiv API**
   - 代码/项目/仓库 → **GitHub API**
   - 引用数据/论文推荐 → **Semantic Scholar API**
3. **最终交付物必须包含原文可查的链接和DOI/PMID**，不能只靠模型内部知识

## 实战模板：从搜索到 Word 文档的完整工作流

以下是在本会话中验证通过的可复用流程（Python）：

### 模板脚本

```python
from docx import Document
from docx.shared import RGBColor
import json, subprocess, os

def search_pubmed(query, max_results=15):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    res = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    data = json.loads(res.stdout)
    return data["esearchresult"]

def fetch_summaries(pmids_str):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids_str}&retmode=json"
    res = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    return json.loads(res.stdout)

# 1. 搜索
result = search_pubmed("shingles+vaccine+Alzheimer", 15)
pmids = result["idlist"]
print(f"命中 {result['count']} 篇")

# 2. 获取详情
summaries = fetch_summaries(",".join(pmids))

# 3. 筛选（剔除无关论文）
skip_uids = []
relevant = [uid for uid in summaries["result"]["uids"] if uid not in skip_uids]

# 4. 排序（按发表时间或相关度）
papers = []
for uid in relevant:
    p = summaries["result"][uid]
    papers.append({
        "title": p.get("title", ""),
        "journal": p.get("source", ""),
        "date": p.get("pubdate", ""),
        "doi": p.get("doi", ""),
        "pmid": uid,
        "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
    })

# 5. 生成 Word 文档
doc = Document()
for paper in papers:
    doc.add_heading(paper["title"], level=2)
    doc.add_paragraph(f"期刊：{paper['journal']}")
    doc.add_paragraph(f"时间：{paper['date']} | DOI: {paper['doi']}")
    doc.add_paragraph(f"链接：{paper['link']}")

output_path = "/mnt/c/Users/Admin/Desktop/研究总结.docx"
doc.save(output_path)
print(f"已保存：{output_path}")
```

### 依赖安装

```bash
# python-docx 用于生成 Word
pip install python-docx -i https://pypi.tuna.tsinghua.edu.cn/simple

# NCBI E-utilities 不需要任何 pip 包——直接用 curl + Python stdlib
```

### 国内镜像 pip 安装

WSL 直接 pip 经常超时，始终带上清华镜像：

```bash
pip install <包名> -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 已验证的可用 API（国内 WSL 直连）

| API | 域名 | 端口 | 测试结果 |
|-----|------|------|----------|
| NCBI E-utilities | eutils.ncbi.nlm.nih.gov | 443 | ✅ 始终可用 |
| arXiv | export.arxiv.org | 443 | ✅ 始终可用 |
| GitHub | api.github.com | 443 | ✅ 始终可用 |
| Semantic Scholar | api.semanticscholar.org | 443 | ✅ 始终可用 |
| **不可用** |
| Google | google.com / www.google.com | 443 | ❌ 被墙 |
| DuckDuckGo | duckduckgo.com | 443 | ❌ 被墙 |
| Bing（非国内版） | bing.com | 443 | ❌ 可能被限 |

## 搜索工具安装记录（失败经验）

```bash
# ❌ duckduckgo_search — 包装成功，但 DuckDuckGo 在中国被墙
pip install duckduckgo_search -i https://pypi.tuna.tsinghua.edu.cn/simple
# → 连接失败：DuckDuckGoSearchException

# ❌ googlesearch-python — 包装成功，但 Google 在中国被墙
pip install google -i https://pypi.tuna.tsinghua.edu.cn/simple
# → URLError: Network is unreachable

# ❌ baidupcs — 百度没有公开免费的搜索 API
pip install baidupcs -i https://pypi.tuna.tsinghua.edu.cn/simple
# → 没有可用 API
```

**结论：不要在这台 WSL 上试图用 Python 层的网页搜索工具。直接用 curl + 可直连的 API 即可。**

## 输出文件路径

Windows 桌面路径对应 WSL 路径：

```
Windows:  C:\Users\Admin\Desktop\
WSL:      /mnt/c/Users/Admin/Desktop/
```
