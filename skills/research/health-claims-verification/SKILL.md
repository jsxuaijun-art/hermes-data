---
name: health-claims-verification
description: Verify health claims with foreign authoritative sources.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, health, factcheck, sources, verification]
    category: research
---

# Health-Claims Verification

Verify circulated health/vaccine/medical claims the user has been exposed to, when they ask for "国外" perspectives or need to ground a personal health decision. Uses US/EU regulators, WHO, fact-checking organizations, polls, and academic literature — never domestic-first or anecdotal answers.

## When to Use
- User pastes a viral article / set of claims full of conspiracy or exaggerated-harm framing (vaccine → autism, "depopulation / bioweapon," heavy-metal toxicity, gene war) and wants the real picture.
- User explicitly asks for 国外/foreign sources because domestic search results are biased, censored, or all saying the same thing.
- User must make a concrete personal health decision (which vaccine/drug) and wants grounded risk/benefit numbers before seeing a doctor.

## Prerequisites
- Network + proxy if foreign sites are blocked (user's `~/.hermes/proxy.sh` handles this).
- No credentials needed — all sources below are public.

## How to Run
1. Identify the user's CONCRETE decision or exact product (e.g., "GSK Shingrix") and answer that FIRST — it is their real question, ahead of the theory.
2. Research in this order:
   - Regulators/health agencies: FDA, CDC, EMA, WHO (GACVS statements), national agencies.
   - Fact-checkers: FactCheck.org, AP, Reuters, Snopes, AFP Fact Check.
   - Polls (for "what does the public believe"): Pew, Gallup, KFF, Annenberg APPC.
   - Academia: PubMed/Cochrane, immunize.org, Johns Hopkins, Dana-Farber.
3. Pull the exact product's official Package Insert / SmPC — the ingredient list is decisive (e.g., "this vaccine has no aluminum/mercury" halts half the fears).
4. Give EVERY claim in the user's text an explicit verdict: 属实 / 曲解 / 伪造 / 无法证实.
5. Do NOT overcorrect: state which part of the user's worry is REAL (real side-effect probabilities, real risk signal), then weigh by actual numbers.
6. Deliver as a plain-text .txt to the Windows Desktop (user's no-markdown preference) OR as a .docx when the user asks for a 报告 / "word格式" — with every citation as a clickable hyperlink.

## Quick Reference (established verdicts)
- **Shingrix (GSK shingles)**: recombinant non-live vaccine; NO aluminum adjuvance and NO thimerosal/mercury. Adjuvant AS01 = MPL 50 µg + QS-21 50 µg + gE 50 µg + excipients. 2 doses i.m. 2–6 months apart. >90% efficacy (trial: ZOE-50 97.2% Lal 2015 NEJM; ZOE-70 89.8% Cunningham 2016 NEJM). Real-world: Zerbo 2024 Ann Intern Med ~76% 2-dose, Sun 2021 Vaccine confirms. Common side effects: injection pain ~78%, myalgia ~45%, fatigue ~45%, headache ~38%, fever ~21%; most last 2–3 days; younger people react more. Only confirmed rare serious risk: GBS ~3–7 excess cases/million (FDA added a warning — regulators actively disclose, they do not hide). Regulators: benefit outweighs risk for 50+.
- **Autism**: origin = Wakefield 1998 Lancet paper (data fabricated, retracted, UK license revoked). WHO GACVS (Dec 2025) + IOM/NAM + cohorts of >1.8M children: no causal link with MMR, thimerosal, or aluminum.
- **"Vaccines cause leukemia/cancer/brain tumor/depression"**: unsupported; 2021 systematic review shows vaccination REDUCES childhood leukemia risk (Dana-Farber: vaccines do not cause cancer).
- **HPV vaccine (Gardasil/Gardasil 9/Cervarix)**: among the most evidence-backed cancer-prevention vaccines. Lei 2020 NEJM (Swedish national cohort): quadrivalent HPV vaccination substantially reduces invasive cervical cancer; Joura 2015 NEJM (9-valent), Giuliano 2011 NEJM (males), Garland 2007 NEJM. WHO GACVS: HPV vaccines "extremely safe" — large cohorts (Danish-Swedish ~1M girls, US ~200k, 540k-pregnancy surveillance) find no causal link to autoimmune disease (incl. MS), GBS, CRPS/POTS, or adverse pregnancy outcomes; Brown 2026 systematic review: no consistent evidence of increased serious AEs.
- **NSSM-200 (Kissinger report, 1974)**: real document, but it is about family planning + economic development in developing countries; it contains NO vaccine-as-weapon content. "Vaccine depopulation" framing is a misreading.
- **"Bill Gates depopulation"**: debunked by FactCheck.org / AP / Snopes. His 2010 TED idea: fewer child deaths → smaller families → slower population growth.
- **"Gene war against Chinese" / "Snowden 200-year extinction"**: no verifiable foreign source; treated as unverifiable disinformation (King's College London / CIGI study these as disinformation topics).

## Procedure
1. If not already clear, confirm the concrete decision/product with the user before researching broadly.
2. Fetch the exact product's official ingredient & side-effect data (FDA PI / EMA SmPC / CDC safety page).
3. One verdict per claim in the user's text, each tied to an authoritative source.
4. Present real risks with the regulator-published probabilities so the user can compare benefit vs. risk numerically.
5. Close with an actionable step (e.g., a "bring this checklist to your doctor" section — contraindications, GBS history, allergy, schedule).
6. Save deliverable to Windows Desktop (C:\Users\Administrator\Desktop). Default `.txt`; `.docx` for a formal report — every citation carries a clickable hyperlink, numbering references monotonically across the whole document (see `references/cited-literature-report-and-docx-links.md`).

## Pitfalls
- User says "不再关注X / 这不是重点" → drop X immediately; do not keep re-arguing a dropped topic.
- Emphasize foreign/allowed-verification sources when the user explicitly asked for them; domestic single-source views are not the answer.
- Do NOT claim "1只疫苗 100% 安全" and do NOT claim "vaccines cause X" — real side effects exist; quote the published probability and the page.
- Do NOT invent numbers: use only published figures (e.g., 3–7 GBS/million) with the source URL.
- State clearly that the final medical decision belongs to the licensed physician — this is information assembly, not medical advice.
- Delivery format: plain-text .txt, NOT markdown, for summaries (hard preference, 2026-10-29). But when the user asks for a 报告 / "word格式", produce a .docx instead of insisting on .txt. Answer the "txt vs word 哪个更耗token" question: reading cost is identical; only generation differs (docx slightly more). See `deliverable-handoff` skill for path conventions.

## Verification
- Every numeric claim in the deliverable maps to a listed source URL.
- The "aluminum/mercury absent" style claims must come from the specific product's Package Insert, not from a general statement about "vaccines."
- Re-check the current date-sensitive items (e.g., FDA warning revisions) against the page you cite before finalizing.

## References
- `references/foreign-health-verification-sources.md` — compact URL bank + claim-verdict template from the first verified run.
- `references/cited-literature-report-and-docx-links.md` — build a cited-literature Word report with clickable hyperlinks (python-docx OXML recipe + verification + numbering pitfalls), plus the full vaccine-literature URL bank (autism cohorts, Shingrix, HPV).
