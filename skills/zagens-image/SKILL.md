---
name: zagens-image
display_name: 搜图
display_name_en: Image Search
description: "搜图、找图、配图、PPT配图、课件配图、可商用图片。必须安装并调用本机 zagens-image 引擎，下载到工作区后套画廊模板生成浏览页。试试说：帮我搜 3 张可商用的岳阳楼横版图。"
description_zh: "按关键字调用本机搜图引擎，筛可商用结果，下载到本地并生成带来源和署名的浏览页。"
description_en: "Search with the local image engine, keep commercially usable images, and save them with a gallery page, source, and attribution."
category: writing
version: 0.1.6
author: Zagens
allowed-tools: Read, Write, Bash
---
# 搜图

搜索和下载**只走本机 `zagens-image`**。本技能没有搜图程序，也不要自己写 Python、curl 或浏览器脚本。浏览页不要手写：下载后用 `templates/gallery.html`，由 `scripts/render-gallery.js` 套到引擎清单上。这个脚本不联网、不下载。

关键词见 @references/query-guide.md。对话样例见 @references/examples.md。字段见 @references/engine-contract.md。Windows 探测与沙箱见 @references/workbuddy-host.md。

## 引擎

本包不含 exe。引擎在 npm 全局 `node_modules\zagens-image\vendor\zagens-image.exe`，或 `~/.zagens-pro/bin/zagens-image.exe`。

1. **探测**（按当前 shell，勿混用变量）。以 stdout 里的版本号为准：
   - 先 `zagens-image --version`
   - PowerShell 再试 `& "$env:USERPROFILE\.zagens-pro\bin\zagens-image.exe" --version`，然后 `& "$(npm prefix -g)\node_modules\zagens-image\vendor\zagens-image.exe" --version`
   - Git Bash 再试 `"$HOME/.zagens-pro/bin/zagens-image.exe" --version`，然后 `"$(npm prefix -g)/node_modules/zagens-image/vendor/zagens-image.exe" --version`
   - **禁止**在 Bash 里写 `%USERPROFILE%`。三处都没有版本号才算未装。
2. **未安装**：不要改用其它方式把图下下来。非 Windows 先说明当前发行是 Windows x64，然后停下。Windows 上先用宿主的 PowerShell 工具跑本技能目录的 `scripts/ensure-workbuddy-sandbox.ps1`（把脚本路径交给 PowerShell；禁止在 Bash 里套 `powershell.exe -File`）。然后告知需要 **Node.js ≥ 16**，**征得同意后**执行 `npm install -g zagens-image@latest`，再用 `zagens-image --version` 验证。不要静默安装，不要让用户从裸链接下载可执行文件。安装指令只在本文件。安装失败就原样回报。
3. **已安装**：出件前用同一个 PowerShell 工具跑一次沙箱脚本（本轮已跑过可跳过）。脚本把 `~/.zagens-pro` 以及 npm 可用时的全局 prefix 与 cache 写入允许写入名单。

## 立刻做

1. 从用户的话里取 2–4 个实体词，写成英文。没说主题时用 `Yueyang Tower`，回复第一句说明这是默认示例。
2. 在用户工作区写入 `deliverables/assets/image-search/search.json`。没特别声明时：

```json
{
  "query": "Yueyang Tower",
  "sources": ["wikimedia"],
  "limit": 12,
  "orientation": "landscape",
  "license": "commercial",
  "min_width": 800
}
```

| 用户信号 | 改哪一项 |
|---|---|
| 竖图 / 头像 | `"orientation": "portrait"` |
| 方图 / 图标 | `"orientation": "square"` |
| PPT、课件、报告、可商用、对外 | `"sources": ["wikimedia"]` 且 `"license": "commercial"` |
| 点名必应、360 或百度 | `sources` 只放点名的源，`license` 用 `"any"`，回复里写明授权未知、不能当可商用 |
| 用户写了「不要文件」 | 先说明将用的 `query`，不跑引擎 |

`query` 不要写「高清、横版、背景图」。省略 `sources` 会四源一起搜，对外交付不要省略。样例在 `templates/search.json`。

3. 搜索：

```bash
zagens-image search --input-file "<用户工作区>/deliverables/assets/image-search/search.json"
```

4. 把 `result.items` 里选中的**完整候选**写入 `deliverables/assets/image-search/download.json`。不要手写 URL，不要删字段。下面的 `items: []` 只是占位，必须换成上一步的对象。默认下 3 张；用户指定张数就照做。`limit` 要比张数至少多 4。

```json
{
  "query": "Yueyang Tower",
  "items": [],
  "out_dir": "deliverables/assets/image-search",
  "max_count": 3,
  "min_width": 800,
  "write_html": true
}
```

5. 下载：

```bash
zagens-image download --workspace "<用户工作区>" --input-file "<用户工作区>/deliverables/assets/image-search/download.json"
```

6. 用画廊模板覆盖浏览页：

```bash
node "<本技能目录>/scripts/render-gallery.js" --manifest "<用户工作区>/deliverables/assets/image-search/image-manifest.json"
```

7. stdout 是一行 JSON。`ok:true` 且 `result.downloaded` > 0：列出每张 `relative_path`、`width`×`height`、`license`、`attribution`，并给出 manifest 和 `index.html`。用 Read 打开最多 3 张。主体明显不符就改具体英文查询，只重跑一次。`downloaded` 为 0：按 `suggestion` 缩短查询或去掉 `min_width`，只重跑一次。`ok:false` 时按下面的表处理一次。

`license_status` 为 `verified` 且许可证含 CC BY 时必须带署名；CC BY-SA 还可能要求相同方式共享。不要把远程 URL 交给 PPT。

## 不要

- 不要在没装引擎时搜图或下载。
- 不要编写下载脚本，不要打开网页抓图。
- 不要手写 HTML，也不要改 `templates/gallery.html`。
- 不要把图片写进技能安装目录。

## 失败后再做一次

| 现象 | 处理 |
|---|---|
| 找不到 `zagens-image` | 回到「引擎」，不要换一条下载途径 |
| `validation` | `search` 与 `download` 字段不要混在一个文件里 |
| `path_denied` | `out_dir` 改为 `deliverables/assets/image-search`，并带上 `--workspace` |
| `network_error` / `rate_limited` | 只重跑一次 |
| `below_min_size` 或结果为空 | 去掉 `min_width` 或缩短英文查询，只重跑一次 |
| 主体不符 | 改查询重跑一次 |
