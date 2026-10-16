# -*- coding: utf-8 -*-
"""grab_pip_card.py - 证据型画中画抓图器 (v3)

用途：把「文案里引用的数据/政策」直接抓成真实截图，交给用户剪进视频/做数据卡，
      而不是只给一个"来源：某某报告"让人自己去搜去截。

用法：
    python3 grab_pip_card.py <url> <out.jpg> "<关键词>" [上移像素=180]

原理与为什么这样写（三代演进，别无脑换回旧写法）：
  v1 元素级截图   -> 只截到关键词那一段 <p>，常只有一行 60px 高，做不了数据卡
  v2 get_by_text  -> Playwright 文本定位常先命中导航/页脚同名文本，页面滚不动，截回来只有页头
  v3 本脚本       -> 在 DOM 里取【最后一个】含关键词的内容元素（正文通常在导航之后），
                     scrollIntoView({block:'center'}) 居中，再上移一点留出上下文，截整屏。
                     1280x780 @2x (=2560x1560) 输出，手机上看得清。

抓完必做：tesseract <out.jpg> stdout -l chi_sim | head -20   # OCR 回读验图，防抓到广告页/导航/空页
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

JS_PICK = """(kw) => {
  const all = [...document.querySelectorAll('p,li,td,h1,h2,h3,div,span')];
  const hits = all.filter(e => e.innerText && e.innerText.includes(kw));
  if (!hits.length) return null;
  const el = hits[hits.length - 1];          // 最后一个：跳过导航/页脚，落在正文
  el.scrollIntoView({block: 'center'});
  const r = el.getBoundingClientRect();
  return {y: r.top};
}"""


def run(url: str, out: str, kw: str, shift: int = 180) -> None:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 780},
                        device_scale_factor=2, user_agent=UA)
        pg.goto(url, wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(4000)                      # 等懒加载/字体
        if pg.evaluate(JS_PICK, kw) is None:
            print("NO_KW_MATCH")
            b.close()
            return
        pg.wait_for_timeout(1500)
        pg.mouse.wheel(0, -int(shift))                 # 上移，多留一点上文
        pg.wait_for_timeout(900)
        pg.screenshot(path=out)
        print("OK", out, Path(out).stat().st_size)
        b.close()


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3],
        int(sys.argv[4]) if len(sys.argv) > 4 else 180)
