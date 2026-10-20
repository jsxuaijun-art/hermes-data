# zagens-image 契约速查

搜索和下载只走这里。安装与探测在根 `SKILL.md`。没有版本号时不要改用脚本或网页抓图。

可商用、PPT、课件、对外交付使用 `sources: ["wikimedia"]` 与 `license: "commercial"`。用户点名必应、360 或百度时，`sources` 只放点名的源，并说明授权未知。

除标准 `--help` / `--version` 纯文本外，业务命令 stdout 都是一个 JSON 信封：

```json
{"engine":"zagens-image","ok":true,"op":"search","result":{}}
```

失败时读取 `code`、`error`、`suggestion`。复杂 JSON 一律用 `--input-file`。

## 能力与 schema

```bash
zagens-image schema capabilities
zagens-image schema search
zagens-image schema download
```

## search

只搜索，不写文件：

```bash
zagens-image search --input-file .zagens/image-search.json
```

完整输入：

```json
{
  "query": "Yueyang Tower",
  "sources": ["wikimedia"],
  "limit": 12,
  "min_width": 1200,
  "min_height": 0,
  "orientation": "landscape",
  "license": "commercial"
}
```

- `sources`：`wikimedia` / `bing` / `360` / `baidu`
- `orientation`：`any` / `landscape` / `portrait` / `square`
- `license`：`any` / `reusable` / `commercial`
- `limit`：1–100

省略 `sources` 时默认四源轮询。Wikimedia 使用官方 API 并返回作者与许可证；
其他三个源是实验网页接口，授权默认为 `unknown`。对外交付必须显式使用
`["wikimedia"]` + `license:"commercial"`。

候选在 `result.items[]`，关键字段：

```json
{
  "id": "wikimedia:7d10ac82e81a",
  "source": "wikimedia",
  "title": "Yueyang Tower.jpg",
  "image_url": "https://...",
  "download_url": "https://...",
  "thumbnail_url": "https://...",
  "source_page": "https://commons.wikimedia.org/...",
  "width": 6014,
  "height": 1729,
  "original_width": 6014,
  "original_height": 1729,
  "delivery_width": 1920,
  "delivery_height": 552,
  "license": "CC BY 3.0",
  "license_url": "https://creativecommons.org/licenses/by/3.0/",
  "author": "Author",
  "license_status": "verified",
  "experimental_source": false,
  "suitability_score": 86,
  "match_reasons": ["标题命中 2 个关键词", "分辨率 1920×1280", "方向匹配"],
  "risk_flags": []
}
```

引擎会聚合所有指定源、URL 去重、计算适配度，并在最终结果中至少保留每个有结果
数据源的一张候选（结果上限不小于源数量时）。输出按 `suitability_score` 降序；
这只是元数据初筛，最终仍须下载后目视。兼容字段 `width/height` 是原图尺寸；
`delivery_width/delivery_height` 是默认下载 URL 的预计交付尺寸，并钳制为不超过
原图尺寸（服务端声称会把 600px 小图上采到 1920px 时仍报告 600px）。尺寸过滤与评分
按该钳制尺寸计算。

关键词只写 2–4 个实体词。不要把“高清、横版、背景图”塞进查询；这些要求分别用
`min_width`、`orientation` 表达。Wikimedia 优先英文名，详见 `query-guide.md`。

## download

`items` 必须放 search 返回的完整候选对象：

```bash
zagens-image download --workspace . --input-file .zagens/image-download.json
```

```json
{
  "query": "Yueyang Tower",
  "items": [],
  "out_dir": "deliverables/assets/image-search",
  "max_count": 6,
  "min_width": 1200,
  "min_height": 0,
  "max_bytes": 20971520,
  "max_pixels": 40000000,
  "prefer_original": false,
  "write_html": true
}
```

安全边界：

- `out_dir` 必须是 `--workspace` 内相对路径；
- 仅公网 HTTP(S)，每次重定向重新校验；
- 单图默认上限 20 MiB、4000 万像素；
- 只接受 PNG/JPEG/GIF/WebP 文件头；拒绝 SVG；
- 图片、manifest、HTML 使用原子写。
- `query` 只用于 HTML 标题；浏览页可筛选、排序、放大及勾选复制本地路径。
- 默认优先 `download_url`（Wikimedia 通常为最长边 1920px 的交付图）；需要原图时显式设
  `prefer_original:true`，仍受体积与像素上限约束。
- 同目录重跑按内容 SHA-256 / 稳定候选 ID 合并 manifest；已有 HTML 会从合并清单重渲染。
- HTTP User-Agent 为 `Zagens-Image/<version> (+https://zagens.com)`；同主机请求至少间隔
  500ms，HTTP 429 自动按 500/1500/4000ms 退避。

成功结果：

```json
{
  "downloaded": 6,
  "failed": 0,
  "downloaded_this_run": 1,
  "failed_this_run": 0,
  "assets": [{
    "path": "C:/workspace/deliverables/assets/image-search/wikimedia_example_a1b2c3d4e5f6.jpg",
    "relative_path": "deliverables/assets/image-search/wikimedia_example_a1b2c3d4e5f6.jpg",
    "width": 1920,
    "height": 1280,
    "original_width": 6014,
    "original_height": 4010,
    "delivery_width": 1920,
    "delivery_height": 1280,
    "sha256": "a1b2c3d4e5f6...",
    "license_status": "verified",
    "attribution": "\"Example\" — Author — CC BY 4.0 — https://commons.wikimedia.org/..."
  }],
  "failures": [],
  "manifest": "C:/workspace/deliverables/assets/image-search/image-manifest.json",
  "html": "C:/workspace/deliverables/assets/image-search/index.html"
}
```

下载结果里的 `width/height` 是文件头实测尺寸，`original_*` 保留搜索时报告的原图尺寸，
`delivery_*` 回填实际落盘尺寸（包括 `prefer_original:true`）。`downloaded/failed`
是合并后清单总数，
`*_this_run` 是本次执行数量。`any/reusable/commercial` 在 Commons 的结果可能接近，
但语义边界仍不同；“可商用”只接受 `license_status:"verified"`，不能把 unknown 推断为可用。
