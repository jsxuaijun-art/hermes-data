# -*- coding: utf-8 -*-
"""pip_grab3.py - PIP grabber v3: JS pick LAST content element containing kw, center it, shoot viewport.
usage: python3 pip_grab3.py <url> <out.jpg> <kw> [shift_up_px]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
JS = """(kw) => {
  const all = [...document.querySelectorAll('p,li,td,h1,h2,h3,div,span')];
  const hits = all.filter(e => e.innerText && e.innerText.includes(kw));
  if (!hits.length) return null;
  const el = hits[hits.length - 1];
  el.scrollIntoView({block: 'center'});
  const r = el.getBoundingClientRect();
  return {y: r.top};
}"""

def run(url, out, kw, shift=180):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 780}, device_scale_factor=2, user_agent=UA)
        pg.goto(url, wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(4000)
        res = pg.evaluate(JS, kw)
        if res is None:
            print("NO_KW_MATCH"); b.close(); return
        pg.wait_for_timeout(1500)
        pg.mouse.wheel(0, -int(shift))
        pg.wait_for_timeout(900)
        pg.screenshot(path=out)
        print("OK", out, Path(out).stat().st_size)
        b.close()

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 180)
