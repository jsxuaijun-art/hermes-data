# 对话示例

## 可商用横版图

**用户：**

> 帮我搜 3 张可商用的岳阳楼横版图，下载到本地。

**Agent：**

1. 按根 `SKILL.md` 探测 `zagens-image`。没有版本号就先安装，不要改用其它下载方式。
2. 写入 `deliverables/assets/image-search/search.json`：

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

3. `zagens-image search --input-file "<用户工作区>/deliverables/assets/image-search/search.json"`
4. 把选中的完整 `result.items` 写入 `download.json`（`max_count` 为 3，`out_dir` 为 `deliverables/assets/image-search`，`write_html` 为 true），再执行 `zagens-image download --workspace "<用户工作区>" --input-file "<用户工作区>/deliverables/assets/image-search/download.json"`。
5. `node "<本技能目录>/scripts/render-gallery.js" --manifest "<用户工作区>/deliverables/assets/image-search/image-manifest.json"`
6. 列出每张本地路径、尺寸、许可证和 `attribution`，并给出 `index.html`。用 Read 看最多 3 张。主体不是岳阳楼就改短查询，只重跑一次。

## 只说「搜图」

**用户：**

> 帮我搜图。

不要追问主题。引擎已安装（或用户已同意安装）时，按上一节做完。回复第一句写：未指定主题，先按岳阳楼示例下载了 3 张，要换主题直接说。

## 用户点名实验源

**用户：**

> 用必应再找 6 张岳阳楼。

仍只调用 `zagens-image`。`sources` 为 `["bing"]`，`license` 为 `"any"`，`limit` 至少 10。回复写明必应授权不可核，不能当作可商用。不要另外做一套 Wikimedia 下载。
