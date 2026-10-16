#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""画中画素材抓取器 —— 从网页按关键词定位段落，做元素级高清截图（2x）。

用法:
    python3 grab_pip_shot.py <url> "<关键词>" [文件名前缀]

产出（默认存 Windows 桌面）:
    画中画_<前缀>_数据段.png   含关键词的段落，2x 高清
    画中画_<前缀>_数据卡.png   同段上部裁切（横条卡片，适合画中画叠加）

页面需登录/验证码/强反爬抓不到时，会明确提示改由人工打开链接截图。
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print("ERROR: 需要 playwright —— pip install playwright && playwright install chromium")
    print(e)
    sys.exit(2)

DESKTOP = "/mnt/c/Users/Administrator/Desktop"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    kw = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "网页截图"
    outdir = Path(DESKTOP)
    outdir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in prefix if c not in '\\/:*?"<>|')

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            pg = b.new_page(viewport={"width": 1180, "height": 1000}, device_scale_factor=2)
            pg.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                pg.wait_for_selector("p:has-text('%s')" % kw, timeout=25000)
            except Exception:
                pass
            pg.wait_for_timeout(1800)
            loc = pg.locator("p:has-text('%s')" % kw).first
            if loc.count() == 0:
                pg.screenshot(path=str(outdir / ("画中画_%s_整页顶.png" % safe)))
                print("WARN: 未找到含关键词的段落，已改截页面顶部。请人工打开链接自行截图：")
                print(url)
                return
            loc.scroll_into_view_if_needed()
            pg.wait_for_timeout(400)
            f1 = outdir / ("画中画_%s_数据段.png" % safe)
            loc.screenshot(path=str(f1))
            from PIL import Image
            im = Image.open(f1)
            w, h = im.size
            cut = min(h, int(w * 0.088))
            f2 = outdir / ("画中画_%s_数据卡.png" % safe)
            im.crop((0, 0, w, cut)).save(f2)
            print("OK:", f1)
            print("OK:", f2)
            print("来源链接:", url)
        finally:
            b.close()


if __name__ == "__main__":
    main()
