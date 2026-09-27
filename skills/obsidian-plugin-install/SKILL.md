---
name: obsidian-plugin-install
description: 手动（离线/命令行）把社区插件装进指定 Obsidian vault，并把口播/俗称的插件名核对成真实插件 ID。当用户要求"帮我装 Obsidian 插件"、"把插件装到 vault 里"、"批量安装 Obsidian 插件"，或给出的插件名在社区市场里搜不到（俗称、谐音、AI 编造名）时使用。
agent_created: true
---

# Obsidian 插件命令行安装

## 何时用

- 用户要求直接装插件到 vault，而不是让他自己去 GUI 点（GUI 路线：`设置 → 第三方插件 → 浏览`）。
- 插件名来自短视频/文案，往往是俗称或谐音（如 "Scollider"、"Ocrai"、"Adding toolbar"），需要先核对真实 ID。

## 关键约束（踩过的坑）

1. **本机直连 GitHub 极慢**：`raw.githubusercontent.com` 和 release 下载都会 timeout（curl exit 28）。
   一律走镜像 `https://ghfast.top/<原 github url>`，失败再退回直连。
2. **不要用 Node 起 curl 子进程**：Windows 下 `execFileSync/spawnSync('curl',...)` 报 `EBUSY` 并瞬间返回，
   看起来像下载失败但其实是根本没执行。改用**纯 bash 脚本**调 curl。
3. **别猜插件 ID**。先用权威清单核对。

## 步骤

### 1. 核对插件真实 ID

```bash
curl -sL --max-time 120 -o cp.json \
  "https://ghfast.top/https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json"
# 约 2.4MB / 8084 个插件
node -e "const l=require('./cp.json');l.filter(p=>p.id.includes('KEY')||(p.name||'').toLowerCase().includes('KEY')).forEach(p=>console.log(p.id,'|',p.name,'|',p.repo))"
```

内置核心插件（Templates、Daily notes、Canvas 等）不用下载，直接改
`<vault>/.obsidian/core-plugins.json` 里对应键为 `true`。

### 2. 下载文件

每个插件需要 `manifest.json` + `main.js`（+ 可选 `styles.css`），放到
`<vault>/.obsidian/plugins/<插件ID>/`。

```bash
REPO=blacksmithgu/obsidian-dataview; ID=dataview
DIR=/d/obsidian-vault/.obsidian/plugins/$ID; mkdir -p $DIR
for f in manifest.json main.js styles.css; do
  curl -sL --max-time 600 \
    "https://ghfast.top/https://github.com/$REPO/releases/latest/download/$f" -o "$DIR/$f"
done
```

校验：`styles.css` <300 字节多半是 404 页面，删掉；`manifest.json` 里的 `id` 必须等于目录名，
不等就以 manifest 的 id 重命名目录（例：Claudian 的真实 id 是 `realclaudian`）。

### 3. 写启用清单

`<vault>/.obsidian/community-plugins.json` 写入已安装 id 数组（已存在就合并去重）：

```json
["dataview","docxer","editing-toolbar"]
```

### 4. 收尾

- Obsidian **运行时改文件不生效**，确认进程未运行或提醒用户重启：
  `tasklist | grep -i obsidian`
- 提醒用户：关闭安全模式（设置 → 第三方插件 → 关闭"安全模式"）才会加载第三方插件。
- 提醒 `minAppVersion` 兼容：新插件（如 Excalidraw ≥1.8.7、Claudian ≥1.13.0）在旧版 Obsidian 上会报错。

## 常用插件 ID 速查

| 俗称 / 功能 | 真实 id | repo |
|---|---|---|
| 编辑工具栏（Word 式） | `editing-toolbar` | pkm-er/obsidian-editing-toolbar |
| 最近文件 | `recent-files-obsidian` | tgrosinger/recent-files-obsidian |
| Word 转 Markdown | `docxer` | developer-mike/obsidian-docxer |
| PDF/OCR 转 Markdown | `marker-api`（名叫 OCR-AI） | l3-n0x/obsidian-marker |
| 小红书导入 | `xiaohongshu-importer` | bnchiang96/xiaohongshu-importer |
| 自动汇总表格 | `dataview` | blacksmithgu/obsidian-dataview |
| 白板绘图 | `obsidian-excalidraw-plugin` | zsviczian/obsidian-excalidraw-plugin |
| 笔记内嵌 AI（Claude Code） | `realclaudian` | yishentu/claudian |
| 高级模板 | `templater-obsidian` | silentvoid13/Templater |

## vault 位置

用户 vault：`D:\obsidian-vault`（Git Bash 里 `/d/obsidian-vault`）。
`.gitignore` 只忽略 `.obsidian/plugins/*/data.json`，插件本体可入库。
