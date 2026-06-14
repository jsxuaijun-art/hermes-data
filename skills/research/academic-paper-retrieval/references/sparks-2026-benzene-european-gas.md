# Worked Example: Sparks et al. 2026 — Benzene in European Natural Gas

**Session**: 2026-05-31
**DOI**: 10.1088/1748-9326/ae499f
**Publisher**: IOP Publishing (Environmental Research Letters)
**Access**: Blocked by Radware Bot Manager (hCaptcha)

## Publisher Block Pattern

IOP Science uses Radware Bot Manager with:
- hCaptcha challenge
- JavaScript-based browser fingerprinting (mouse/touch tracking, DOM inspection)
- IP-based reputation checking

Standard `curl` and `browser_navigate` (Playwright Chromium) both failed. The browser error was:
```
Chrome exited early (exit code: 127) without writing DevToolsActivePort
... error while loading shared libraries: libnspr4.so
```

## Successful Retrieval Chain

### 1. Crossref API (metadata)
```bash
curl -sL "https://api.crossref.org/works/10.1088/1748-9326/ae499f"
```
Returned: title, all 17 authors, volume/issue/pages, funding (Wellcome Trust + European Climate Foundation), abstract (as `<jats:p>` XML), reference count (62), license (CC BY 4.0), online date (2026-03-25), print date (2026-03-28).

**Limitation**: All `affiliation` fields were empty arrays `[]`. Crossref simply doesn't have them for this paper.

### 2. OpenAlex API (enriched author-affiliation data)
```bash
curl -sL "https://api.openalex.org/works/doi:10.1088/1748-9326/ae499f"
```
Returned: full author-institution mapping (see below), topic concepts (Benzene 0.86, Natural gas 0.70), OA status.

## Key Findings

### Author Institutions

| Author | Institution |
|---|---|
| Tamara L Sparks | Healthy Start |
| Yannai S Kashtan | Healthy Start; Stanford University |
| Sebastian T Rowland | Healthy Start |
| Eric D Lebel | Healthy Start |
| Jackson S W Goldman | Healthy Start |
| Colin Finnegan | Stanford University |
| Gan Huang | Healthy Start |
| Nicole Lucha | Healthy Start |
| Abenezer Shankute | Stanford University |
| Nick Heath | Healthy Start |
| Sofia Bisogno | Healthy Start |
| Kelsey R Bilsback | Healthy Start |
| Anchal Garg | Stanford University |
| Lee Ann L Hill | Healthy Start |
| Robert B Jackson | Stanford University |
| Seth B C Shonkoff | Lawrence Berkeley National Lab; Berkeley Public Health; Healthy Start |
| Drew R Michanowicz | Healthy Start |

**"Healthy Start"** = PSE Healthy Start (PSE = Physicians, Scientists, and Engineers for Healthy Energy), a nonprofit research institute focused on public health and energy.

### Abstract (plain text)

> Consumer-grade natural gas leaks contribute to methane-induced climate change and can degrade air quality. However, limited leakage and gas composition data exist outside of North America. Here, we measured stove-off gas leakage in 35 homes and chemically characterized 78 unburned gas samples from residential stoves across seven cities in the United Kingdom, Netherlands, and Italy. On average, benzene in unburned gas was substantially elevated compared to North America (9 to 73 times higher), while sulfur-based odorants were lower. Modeling of indoor and outdoor benzene enhancements from gas leaks showed potential for hazardous benzene exposure, often undetectable by odor. Three of 35 homes exhibited a stove-off leak that, combined with city-median benzene in gas, resulted in modeled benzene enhancements above the European Union's annual limit value (1.6 ppbv). The combination of high benzene and relatively low odorization in natural gas suggests that hazardous leaks are likely underreported in Europe.

### Prior Work Context

This is the European sequel to the team's 2022 study:
- **Sparks TL et al. (2022)** "Benzene in consumer-grade natural gas" — *Environmental Science & Technology* — found benzene in US natural gas
- This 2026 paper extends the analysis to Europe and finds the problem is **worse**: 9-73× higher benzene, weaker odorants

## Metadata Summary for Quick Reference

| Field | Value |
|---|---|
| DOI | 10.1088/1748-9326/ae499f |
| Journal | Environmental Research Letters |
| Volume | 21 |
| Issue | 6 |
| Article # | 064008 |
| Published | 25 March 2026 (online) |
| Authors | 17 |
| Refs | 62 |
| License | CC BY 4.0 |
| Funding | Wellcome Trust (321500/Z/24/Z); European Climate Foundation (G-2211-65243) |
| First Author | Tamara L Sparks |
| Key Institution | Stanford University + PSE Healthy Start + Lawrence Berkeley National Lab |
