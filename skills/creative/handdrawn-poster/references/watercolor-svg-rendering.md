# Watercolor / hand-drawn SVG rendering (cairosvg, this WSL env)

## Fonts (OFL CJK handwriting, via jsDelivr - reachable from China, raw.githubusercontent also works)
- Ma Shan Zheng (brush): `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/mashanzheng/MaShanZheng-Regular.ttf`
- ZCOOL KuaiLe (rounded handwritten): `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf`
- Zhi Mang Xing (scrawly): `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/zhimangxing/ZhiMangXing-Regular.ttf`
- Install: `mkdir -p /usr/share/fonts/truetype/custom && cp *.ttf /usr/share/fonts/truetype/custom/ && fc-cache -f`. Fontconfig family names: "Ma Shan Zheng", "ZCOOL KuaiLe", "Zhi Mang Xing".
- Verify loaded: `fc-list | grep -iE "ma shan|zcool|zhi mang"`.

## Render commands (cairosvg via system python)
```
/usr/bin/python3 -c "import cairosvg; \
  cairosvg.svg2png(url='p.svg', write_to='p.png', output_width=3300, output_height=4668); \
  cairosvg.svg2pdf(url='p.svg', write_to='p.pdf', output_width=1100, output_height=1556)"
```
From `execute_code`, call it through subprocess (sandbox python lacks cairosvg):
```
subprocess.run(["/usr/bin/python3","-c",code], capture_output=True, text=True, timeout=300)
```

## Filter safety in cairosvg
- SAFE: feGaussianBlur (soft washes, shadows, glow-via-feMerge), feDisplacementMap (uneven / brush edges), radial + linear gradients.
- BREAKS (renders whole image BLACK): `feTurbulence` + `feColorMatrix` noise-over-noise overlay. Never build a full-page grain rect this way; skip the grain entirely.

## Verify the handwriting font is really used (not fallback to wqy)
Render the same CJK string once per family at the same size, count ink pixels (<128 luminance in PIL), compare. Different counts across families => glyphs differ => font loaded, not fallback. (Reference ink counts at 500x80 for the sample string: wqy 5807, MaShan 3909, ZCOOL 6301, ZhiMang 3525.)

## Layout without visual feedback
You cannot eyeball the result when the model rejects images. So:
- Keep every block's bounding box inside the inner frame; recompute when you nudge coordinates.
- Prefer generous block sizes over tight ones; keep gap doodles in the margins so nothing collides with text.
- Plan 2-3 staggered columns, not a perfect grid; give blocks random-but-small tilt; after moving a block re-check its right/top edges stay in-frame.
