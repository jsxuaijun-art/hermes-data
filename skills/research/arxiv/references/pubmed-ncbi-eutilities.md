# PubMed / NCBI E-utilities — Biomedical Research API

Use when arxiv doesn't cover the domain (medicine, biology, clinical trials). No API key required. Rate limit: ~3-10 req/sec.

## Quick Start

```bash
# 1. Search PubMed for papers
PMID_LIST=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+QUERY&retmax=10&retmode=json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(d['esearchresult']['idlist']))")

# 2. Fetch paper summaries
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=$PMID_LIST&retmode=json"
```

## Step-by-Step Workflow

### Step 1: Search (esearch)

```bash
URL="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
curl -s "$URL?db=pubmed&term=shingles+vaccine+Alzheimer&retmax=15&retmode=json"
```

Parameters:
- `db`: `pubmed` (mandatory)
- `term`: Search query. Use `+` for AND; quotes encoded as `%22`
- `retmax`: Max results (default 20, max 100000)
- `retmode`: `json` or `xml`
- `retstart`: Pagination offset

Returns JSON with an `idlist` array of PMIDs.

### Step 2: Fetch Summaries (esummary)

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=41338191,41053450,40551502&retmode=json"
```

Key fields in response:
- `title`: Paper title
- `source`: Journal name
- `pubdate`: Publication date
- `authors[].name`: Author list
- `doi`: DOI identifier
- `pmc`: PMC ID (if open access)
- `elocationid`: Full DOI link
- `fulljournalname`: Full journal name
- `attributes`: Contains `"Has Abstract"` if abstract is available

### Step 3: Fetch Full Abstract (efetch)

```bash
# XML with abstract
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=41338191&retmode=xml&rettype=abstract"

# Text format
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=41338191&retmode=text&rettype=abstract"
```

### Step 4: Access Full Text

```bash
# PMC open access (when pmid has pmc field)
curl -s "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12851904/pdf/" -o paper.pdf

# DOI link (most reliable)
# https://doi.org/10.1016/j.cell.2025.11.007
```

## Search Query Tips

| Pattern | Example | Result |
|---------|---------|--------|
| AND (tokenize) | `shingles+vaccine+Alzheimer` | All terms |
| Phrase search | `%22staged+surgery%22` | Exact phrase |
| Field prefix | `dementia[ti]` | Title only |
| MeSH terms | `Alzheimer%20disease[MeSH]` | MeSH indexing |
| Author search | `Taquet+M[au]` | Specific author |
| Year range | `2024:2026[dp]` | Date range |

Translation System: E-utilities auto-expands search terms using MeSH mappings. Check the `querytranslation` field in esearch response to see what it actually searched.

## Full Workflow Script (Python)

```python
import json, subprocess

def search_pubmed(query, max_results=10):
    """Search PubMed and return PMID list + translation info."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    res = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    data = json.loads(res.stdout)
    return data["esearchresult"]

def fetch_summaries(pmids):
    """Fetch detailed summaries for a list of PMIDs (comma-separated)."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids}&retmode=json"
    res = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    return json.loads(res.stdout)

# Example usage
result = search_pubmed("shingles+vaccine+Alzheimer", 15)
pmids = ",".join(result["idlist"])
print(f"Found {result['count']} papers. Translation: {result['querytranslation']}")

summaries = fetch_summaries(pmids)
for uid, paper in summaries["result"].items():
    if uid == "uids": continue
    print(f"\n--- PMID: {uid} ---")
    print(f"Title: {paper.get('title', 'N/A')}")
    print(f"Journal: {paper.get('source', 'N/A')}")
    print(f"Date: {paper.get('pubdate', 'N/A')}")
    print(f"DOI: {paper.get('doi', 'N/A')}")
    print(f"Link: https://pubmed.ncbi.nlm.nih.gov/{uid}/")
```

## When to Use Which

| Source | Best For | Format | API Key |
|--------|----------|--------|---------|
| arxiv | CS, ML, Physics, Math, Stats | XML | None |
| PubMed (E-utilities) | Medicine, Biology, Clinical, Pharma | JSON/XML | None |
| Semantic Scholar | Citation data, recommendations | JSON | Optional |
| Google Scholar | Broad search, legal, humanities | Scraping only | N/A |

## Pitfalls

- No `web_search` tool available? Use E-utilities as fallback for any biomedical question
- arxiv search for medical topics returns irrelevant papers (SIR models, generic vaccine dynamics) — don't default to arxiv for clinical questions
- esearch returns `querytranslation` — always check it to confirm the system understood your intent
- Not all papers have free full text; check `pmc` field in esummary
- Rate limit: ~10 req/sec for E-utilities; no API key required
- If esummary doesn't include an abstract, use efetch with `rettype=abstract`
