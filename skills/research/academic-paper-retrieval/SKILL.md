---
name: academic-paper-retrieval
description: Retrieve metadata, authors, institutions, abstract, funding, and citation data for any academic paper by DOI — even when the publisher's website blocks direct access. Uses Crossref API (no auth needed) and OpenAlex API for enriched author-affiliation data. Fallback chain when paywalled/bot-protected sites block access.
---

# Academic Paper Retrieval by DOI

Use this when a user asks you to find details of a specific academic paper (identified by DOI), and the publisher's website is paywalled, bot-protected, or otherwise inaccessible.

## Standard Retrieval Chain

### Step 1: Try the DOI resolver directly

```bash
curl -sL "https://doi.org/<DOI>" -H "Accept: text/html,application/json" 2>&1 | head -50
```

If it resolves fine (no CAPTCHA), navigate the page normally. If blocked by bot protection (Radware, Cloudflare, hCaptcha, etc.), skip this and go to Step 2.

### Step 2: Crossref API (metadata backbone)

Crossref's REST API returns structured metadata for every registered DOI. **No API key needed, no rate limits for single lookups.**

```bash
curl -sL "https://api.crossref.org/works/<DOI>" | python3 -m json.tool
```

Key fields in `data['message']`:
- `title`: paper title (array, join with space)
- `author`: array of `{given, family, ORCID, affiliation}`
- `published-print`/`published-online`: date-parts `[[year, month, day]]`
- `container-title`: journal name
- `volume`, `issue`, `page`
- `DOI`, `URL`
- `abstract`: often embedded as `<jats:p>` XML (extract the text content)
- `link`: array of URLs for full-text/PDF access
- `funder`: funding sources with DOIs and award numbers
- `reference-count`: number of references/citations
- `license`: OA licensing info
- `type`: e.g. `journal-article`
- `is-referenced-by-count`: how many times cited by other Crossref works

**Warning**: `abstract` comes as XML (`<jats:p>...</jats:p>`). Strip HTML tags to get plain text:

```python
import re
abstract_xml = data['message'].get('abstract', '')
abstract = re.sub(r'<[^>]+>', '', abstract_xml)
```

**Warning**: `affiliation` in Crossref is frequently **empty** (`[]`). The publisher often doesn't submit this data. Don't report this as N/A — move to OpenAlex instead.

### Step 3: OpenAlex API (enriched author-affiliation data)

OpenAlex aggregates paper metadata from multiple sources including Crossref, PubMed, and institutional repositories. It has better affiliation coverage.

```bash
curl -sL "https://api.openalex.org/works/doi:<DOI>"
```

Key enriched fields:
- `authorships[i].author.display_name`: full author name
- `authorships[i].institutions[j].display_name`: institution name
- `authorships[i].countries`: country list
- `concepts`: topic/category descriptors with relevance scores (0-1)
- `primary_location.source.display_name`: journal name
- `open_access.status`: 'gold', 'hybrid', 'green', 'bronze', 'closed'
- `open_access.oa_url`: direct OA link if available
- `cited_by_count`: cross-citation count

### Step 4: Try direct PDF (if needed)

Some publishers serve PDFs through a more permissive endpoint than their HTML pages:

```bash
curl -sL "https://doi.org/<DOI>/pdf" -o /tmp/paper.pdf -w "%{http_code}"
file /tmp/paper.pdf
```

**Check**: Some sites return a JavaScript redirect page named `.pdf` — verify with `file` that it's actually a PDF, not an HTML/CAPTCHA page.

### Step 5: Other fallbacks

- **PubMed / PubMed Central**: If it's a biomedical paper, try `https://pubmed.ncbi.nlm.nih.gov/<PMID>/` or `https://www.ncbi.nlm.nih.gov/pmc/articles/<PMCID>/`
- **arXiv**: For preprints that later got published, search by DOI or title at `https://export.arxiv.org/api/query?search_query=doi:<DOI>`
- **CORE API**: Aggregates OA papers: `https://api.core.ac.uk/v3/search/works?q=<DOI>`
- **Unpaywall / OA Button**: Check if an OA version exists
- **Sci-Hub**: Last resort, often blocked by DNS/ISP

## Example Extraction Script

This is the pattern used in the successful Sparks et al. 2026 retrieval:

```python
import json, subprocess

doi = "10.1088/1748-9326/ae499f"

# Step 1: Crossref
result = subprocess.run(
    ["curl", "-sL", f"https://api.crossref.org/works/{doi}"],
    capture_output=True, text=True
)
cr = json.loads(result.stdout)['message']

# Step 2: OpenAlex (enriched)
result2 = subprocess.run(
    ["curl", "-sL", f"https://api.openalex.org/works/doi:{doi}"],
    capture_output=True, text=True
)
oa = json.loads(result2.stdout)

# Authors with institutions
for a in oa.get('authorships', []):
    name = a['author']['display_name']
    insts = [i['display_name'] for i in a.get('institutions', [])]
    print(f"{name}: {'; '.join(insts) if insts else 'N/A'}")
```

## Author Display Template

When presenting author information to the user, use this format:

```
**第一作者/通讯作者**: Full Name (Institution)
**所有作者 (N位)**: Name1 (Inst1), Name2 (Inst2), ...
```

### When institution data is available from OpenAlex but not Crossref
- Present OpenAlex's institutions as primary. Flag the limitation: "Crossref API does not include affiliation data for this paper; data below is from OpenAlex."

## Pitfalls

- **IOP Science** (iop.org) uses Radware Bot Manager — blocks all curl/browser requests without hCaptcha. Skip directly to Crossref + OpenAlex.
- **Elsevier/ScienceDirect** often returns 403 or a session-check page. Same fallback.
- **Crossref abstract field** contains raw `<jats:p>` XML. Always strip tags before presenting.
- **Crossref affiliation field** is frequently empty — this is a known gap in the data. Always cross-check with OpenAlex.
- **PDF redirect trick**: Some publishers return a JS redirecting page with a `.pdf` extension. Always run `file` on downloaded PDFs to verify.
- **OpenAlex has a rate limit** (~10 req/s for no-key access). Fine for single lookups; for batch queries, register for a free API key.
- **Some DOIs redirect to a different DOI** (e.g., when a preprint is published). Follow the redirect.
