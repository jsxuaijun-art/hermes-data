# 搜图关键词改写

## 基本规则

- 每次只用 2–4 个高信息量实体词。
- “高清、横版、竖版、背景图、PPT 配图”等不是实体词，改用 `min_width`、`min_height`、`orientation`。
- Wikimedia Commons 优先英文通名、专名或拉丁学名；中文可用于 Bing、360、百度。
- 首次零结果时只改写一次：删掉修饰词，再把核心实体翻译为英文。仍为空就如实说明。
- 不凭空补地点、年代、作者或风格。用户没给主题时用 `Yueyang Tower`，并说明这是默认示例，不要停轮追问。

## 常用中英术语

- 岳阳楼 → `Yueyang Tower`
- 洞庭湖 → `Dongting Lake`
- 排针 → `pin header`
- 排母 → `female header`
- 排线 → `ribbon cable`
- 板对板连接器 → `board-to-board connector`
- 端子 → `terminal`
- 紫藤 → `wisteria`
- 牡丹 → `peony`
- 故宫 → `Forbidden City`

## 示例

“3 张可商用的岳阳楼横版高清图”：

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

张数、输出目录和浏览页写在 download 请求里，不要放进 search。见 `engine-contract.md`。

“全网找岳阳楼水墨配图”可对实验源使用 `岳阳楼 水墨`；Wikimedia 单独查询
`Yueyang Tower painting`，不要把四源最低公分母强行写成同一个长查询。
