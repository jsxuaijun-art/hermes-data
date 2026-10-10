# Web-page evidence screenshots (element-level, 2x, OCR-verified)

**Scope:** when the deliverable is an **image cropped out of a web page** — a video
picture-in-picture overlay, an article illustration, an evidence page inside a deck or
report, a "source screenshot" attached to a claim. This is the image analogue of the
render-verification rule in SKILL.md: *the bytes existing proves nothing about whether
the artifact is usable.*

Origin: 2026-10-10, capturing a 最高人民法院 annual-report statistic for use as a
talking-head video overlay.

## 1. The failure that motivates this file

First attempt = the browser's **full-page screenshot**. It looked fine opened at full
size, and was **useless**: scaled into a phone-sized overlay (~1/4 of the frame) the
body text is a few pixels tall — unreadable.

Root cause: a full-page capture spends its pixel budget on "a whole document", while the
final viewing surface is a small corner of a phone screen. **Crop to the element and
render at 2x density.**

## 2. Working recipe

1. **Screenshot the element, never the page** — find the paragraph by keyword, then
   `locator.screenshot()`.
2. **`device_scale_factor=2`** on the page context — doubles pixel density so
   body-size text survives being shrunk into an overlay.
3. **`wait_for_selector` before capturing** — government / portal / news pages are
   usually JS-rendered; a bare `goto` + screenshot captures an empty shell.

```python
pg = b.new_page(viewport={"width": 1180, "height": 1000}, device_scale_factor=2)
pg.goto(url, wait_until="domcontentloaded", timeout=60000)
pg.wait_for_selector("p:has-text('%s')" % kw, timeout=25000)
loc = pg.locator("p:has-text('%s')" % kw).first
loc.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
loc.screenshot(path=out)          # element-level, NOT page.screenshot
```

Optional second output: crop the top ~8.8% of that element into a narrow banner
"data card" — a horizontal strip is easier to overlay without covering the speaker.

## 3. Verify before delivering (the step that makes this a *verification* discipline)

Read the produced image back with `vision_analyze` and confirm the key figures are
legible. In the originating session this step mattered: the OCR read-back confirmed
「17.53万件，同比上升51.07%」 was crisp before the image was handed over. Deliverable
screenshots that are blurry, cropped mid-glyph, or clipped by a sticky header fail here.

## 4. Sourcing discipline

- Prefer the **official** page (gov.cn, official media, the primary report) over
  second-hand reposts.
- You may add red boxes / arrows; **never alter a number** — a doctored screenshot is a
  forged document.
- Every image ships with its **source + date** in the caption/notes.
- Hand the user the **openable URL**, not just the file name, so they can verify or
  re-crop it themselves.

## 5. When the page cannot be captured (do not grind)

Login walls, CAPTCHAs, or aggressive anti-bot measures → stop retrying and hand over
**link + keyword + location**, e.g. *"open <url>, Ctrl+F `17.53万件`, section （四）"*.
The user capturing it manually is a complete, honest delivery.

## 6. Pitfalls

- **Do not deliver a full-page long screenshot as an overlay asset.** That is the entire
  reason for this file.
- **Long scripts must be written to disk before running, not inlined into a single
  tool-call argument** — an inline multi-KB script was truncated mid-file (syntax error at
  line 15). Write the file, syntax-check, then execute.
- **First use needs a browser**: `pip install playwright && playwright install chromium`.
- A keyword with no matching element degrades to a page-top screenshot; treat that output
  as a signal to fall back to manual capture, not as a success.
