# 独立研究可信度评估方法论

从零开始对一个主题进行独立学术/专业研究，并评估证据可信度。适用于客户问"听说X有风险，是真的吗？"这类需要独立判断的场景。

## 适用场景

客户（或您）听到一个专业主张时：
- "微塑料有致癌作用"
- "某成分有毒"
- "某税收政策已出台"
- "某技术有害"

需要：独立查证 → 评估可信度 → 给出清晰判断。

## 检索渠道

| 渠道 | 用途 | 说明 |
|------|------|------|
| **OpenAlex API** (`api.openalex.org/works`) | 学术论文检索 | 免费，无需Key。按引用排序找高影响力论文 |
| **PubMed / Google Scholar** | 生命科学/医学 | 微塑料/癌症类优先覆盖 |
| **arXiv** | 预印本 | 较新研究但未同行评审 |
| **政府/机构官网** | 政策/官方声明 | WHO IARC、FDA、EFSA等 |
| **新闻来源** | 社会影响 | 仅作为"公众关注度"参考，不作为证据 |

## 论文分析方法

获取论文列表后，逐个检查：

### 1. 期刊质量
- 期刊名 + IF（影响因子）：Molecular Cancer (IF>27)、Environmental Science & Technology (IF>10) 为顶刊
- 期刊隶属：Nature旗下、ACS、Elsevier 等为正规出版社
- 低质信号：掠夺性期刊、MDPI部分低分期刊

### 2. 引用量
- ⭐>100：高影响力，已被同行大量关注
- ⭐50-100：中上水平
- ⭐<10且新论文：可能尚未被充分认可

### 3. 论文类型
- **Original article**（原始研究）：有实验数据，可信度最高
- **Review/Systematic review**（综述）：汇总他人研究，提出假说，非结论性
- **Meta-analysis**（荟萃分析）：综合多项原始研究，统计学强度高
- **Commentary/Editorial**（评论/社论）：观点性文章，不视为证据
- **Preprint**（预印本）：未同行评审，谨慎对待

### 4. 开放获取 (OA)
- OA论文可查看全文，核实细节
- 非OA论文只能看摘要，判断可能不完整

### 5. 作者机构
- 知名大学/研究机构产出更可靠
- 单一作者或不知名机构谨慎看待

## 证据层次（由强到弱）

```
★ 确定致癌（IARC Group 1）— 需大规模流行病学研究
  例：吸烟、石棉、PM2.5（2020年代才确认）

★★★ 强烈提示 — 职业暴露流行病学 + 机制明确
  例：PVC微塑料工人肝脏癌风险升高

★★☆ 初步关联 — 检测到暴露证据 + 细胞实验
  例：微塑料已在人肝/血/心中检出 + 体外实验显示DNA损伤

★★ 机制合理 — 细胞/动物实验支持，无人群数据
  例：氧化应激→炎症→癌变路径在细胞层面已证实

★☆ 提出假说 — 综述建议但缺乏原始研究
  例：多个综述文章汇总已有文献后提出的研究方向

★ 未经证实 — 媒体炒作，无同行评审
  例：自媒体文章引用了一篇综述的综述的综述
```

## 给客户的表达框架

不用把方法论倒给客户，而是结构化输出：

### 结构

1. **核心结论（一句话）**："目前的研究表明…，但尚未确定…"
2. **证据来源**：列出关键论文（期刊名+年份+引用数）
3. **判断依据**：现有证据在哪个层次+缺什么
4. **行动建议**："值得关注但不必恐慌"或"需要立即采取措施"
5. **免责声明**："这是基于公开研究的独立分析，不作为专业医疗/法律意见"

### 示例（微塑料致癌）

```
目前的研究结论不是'微塑料确定致癌'，而是'现有证据强烈提示
微塑料可能致癌，机制合理，人体内已检出，急需更多研究'。
这和1990年代PM2.5致癌的研究进程很像——当时也是机制+职业
暴露先出，等了10年才有大规模人群数据最终确认。
```

## Python 检索脚本（模板）

```python
import urllib.request, json

def search_papers(query, max_results=15):
    """搜论文，按引用量排序"""
    url = f'https://api.openalex.org/works?filter=title_and_abstract.search:{urllib.parse.quote(query)},publication_year:2020-2026&sort=cited_by_count:desc&per_page={max_results}'
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read()).get('results', [])

def analyze_paper(doi):
    """分析单篇论文"""
    with urllib.request.urlopen(f'https://api.openalex.org/works/doi:{doi}', timeout=10) as r:
        d = json.loads(r.read())
    return {
        'title': d.get('title',''),
        'journal': d.get('primary_location',{}).get('source',{}).get('display_name',''),
        'year': d['publication_year'],
        'citations': d['cited_by_count'],
        'type': d['type'],  # 'review' vs 'article'
        'oa': d['open_access']['is_oa'],
        'authors': [a['author']['display_name'] for a in d.get('authorships',[])[:4]],
        'concepts': [(c['display_name'], c['score']) for c in d.get('concepts',[])[:5]],
    }
```

## 注意事项

- 大多数学术搜索API（Scopus、Web of Science）需要付费订阅。**OpenAlex免费且覆盖广**，适合快速检索
- 仅看论文标题可能有误导——某些论文标题"微塑料致癌"但内容是综述或动物实验
- 区分"相关"和"因果"——微塑料在癌组织中被检出≠微塑料导致了癌症
- 2023-2025年发表的论文中有大量AI辅助写作，质量参差，优先看引用量高的
- 客户想要的是"要不要担心"的明确答案，不要给出模棱两可的学术废话
