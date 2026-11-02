# Cited-Literature Word Report with Clickable Hyperlinks

When the user asks for "文献/论文逐一列出" and wants it as a formal report ("以报告的方式呈现,word格式"), build a .docx where every numbered citation carries a clickable URL (PubMed / NEJM / WHO / national-agency page). This was proven on 2026-10-29 (vaccine-safety literature report, 26 links).

## Workflow
1. For each citation give: full journal ref (authors, title, journal, year;vol(issue):pages, doi) + a source URL + a one-line "观点/关键结论".
2. Number references monotonically ACROSS the whole document — do not restart numbering per section. (This session reused [15][16][17] in a later section and had to renumber; duplicates confuse the user.)
3. Generate with python-docx; verify afterward (see below).
4. Re-issue the docx when the user asks to "融入到刚才的文档/重新输出" — regenerate from the same script with the additions rather than hand-editing XML.

## python-docx clickable-hyperlink recipe
python-docx has NO native hyperlink API; add one via raw OOXML:

```python
import docx  # python-docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_hyperlink(paragraph, url, text, color=(0x05, 0x63, 0xC1)):
    r_id = paragraph.part.relate_to(
        url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), r_id)
    run = OxmlElement('w:r'); rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), '%02x%02x%02x' % color); rPr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
    run.append(rPr)
    t = OxmlElement('w:t'); t.text = text; run.append(t)
    h.append(run); paragraph._p.append(h)
```

Usage: `p = doc.add_paragraph(); p.add_run('[%d] ' % n).bold = True; p.add_run(ref_text); p.add_run('  链接: '); add_hyperlink(p, url, url)`.

## Verify the generated docx programmatically (no LibreOffice needed)
```python
from docx import Document
import re, docx.opc.constants as c
d = Document(out)
paras = [p.text for p in d.paragraphs if p.text.strip()]
print('段落总数', len(paras))
print('编号引用', sum(1 for p in paras if re.match(r'^\[\d+\]', p)))
hl = [k for k, v in d.part.rels.items() if v.reltype.endswith('hyperlink')]
print('超链接数', len(hl))   # should equal the number of cited sources
```

## Pitfalls
- Do NOT renumber reference-line string literals with shell `sed` — it destroyed the opening quote of `cite(15, 'NSSM-200…` → `cite(24, .NSSM-200…`, breaking the Python string. Use the `patch` tool or `python str.replace` for edits inside code files with CJK + quotes.
- Keep citation numbers in the deliverable matching the order they appear; if you add a section mid-document, renumber everything once at the end.
- Word hyperlinks need `is_external=True` or Word won't treat them as live links.

## Vaccine-literature URL bank (verified 2026-10-29)
Autism / MMR / thimerosal:
- Wakefield 1998 Lancet (retracted): pubmed.ncbi.nlm.nih.gov/9500320/
- Taylor 1999 Lancet (no causal link): pubmed.ncbi.nlm.nih.gov/10376617/
- Lancet 2010 retraction notice: pubmed.ncbi.nlm.nih.gov/20137807/
- Madsen 2002 NEJM (DK 537k children): nejm.org/doi/full/10.1056/NEJMoa021134
- Hviid 2019 Ann Intern Med (DK 657k): pubmed.ncbi.nlm.nih.gov/30630190/
- Jain 2015 JAMA (95k high-risk): pubmed.ncbi.nlm.nih.gov/25898051/
- Taylor 2014 Vaccine meta-analysis: pubmed.ncbi.nlm.nih.gov/24814559/
- Madsen 2003 Pediatrics (thimerosal): pubmed.ncbi.nlm.nih.gov/12949289/
- IOM/NAM 2011 Adverse Effects of Vaccines: ncbi.nlm.nih.gov/books/NBK190024/
- Maglione 2014 Pediatrics systematic review: pubmed.ncbi.nlm.nih.gov/24624471/
- Childhood-cancer review (vaccination lowers risk): pmc.ncbi.nlm.nih.gov/articles/PMC7862764/
- Dana-Farber "No, vaccines won't give you cancer": blog.dana-farber.org/insight/2019/07/worth-the-shot-no-vaccines-wont-give-you-cancer/
Shingrix (shingles):
- Lal 2015 NEJM (ZOE-50): nejm.org/doi/full/10.1056/NEJMoa1501184
- Cunningham 2016 NEJM (ZOE-70): pubmed.ncbi.nlm.nih.gov/27626517/
- Zerbo 2024 Ann Intern Med (real-world): pubmed.ncbi.nlm.nih.gov/38190712/
- Sun 2021 Vaccine (real-world): sciencedirect.com/science/article/abs/pii/S0264410X21006423
HPV:
- Lei 2020 NEJM (cervical-cancer reduction): nejm.org/doi/full/10.1056/NEJMoa1917338
- Joura 2015 NEJM (9-valent): nejm.org/doi/full/10.1056/NEJMoa1405044
- Giuliano 2011 NEJM (males): nejm.org/doi/full/10.1056/NEJMoa0909537
- Garland 2007 NEJM (quadrivalent): nejm.org/doi/full/10.1056/NEJMoa061760
- WHO GACVS HPV safety page: who.int/groups/global-advisory-committee-on-vaccine-safety/topics/human-papillomavirus-vaccines/safety
- Brown 2026 SAE systematic review: pmc.ncbi.nlm.nih.gov/articles/PMC12959203/
Conspiracy claims:
- NSSM-200 original (Nixon Library PDF): nixonlibrary.gov/sites/default/files/virtuallibrary/documents/nssm/nssm_200.pdf
- FactCheck.org on Gates/depopulation: factcheck.org/2021/03/scicheck-video-targets-gates-with-old-clip-misleading-edit/
- CIGI on deliberate disinformation in global health: cigionline.org/articles/battles-influence-deliberate-disinformation-and-global-health-security/
- WHO GACVS vaccines-autism statement (2025-12-11): who.int/news/item/11-12-2025-statement-gacvs-vaccines-autism
