# GitHub API 远程访问（无需本地 clone）

当同步目录未设置或不可用时，通过 GitHub REST API 直接读取远程仓库内容。

## 前提条件

- 仓库是 **public**（`jsxuaijun-art/hermes-data` 是 public）
- 网络可达 github.com（从中国可能需要代理/VPN）

## 常用操作

### 查看仓库根目录结构

```bash
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/contents?ref=main"
```

返回 JSON 数组，每个元素包含：
- `name` — 文件名
- `type` — "file" 或 "dir"
- `size` — 文件字节数
- `download_url` — 直接下载链接（file 类型特有）
- `html_url` — GitHub 页面链接

### 查看子目录

```bash
# 查看 memories/ 目录
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/contents/memories?ref=main"

# 查看 skills/ 目录
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/contents/skills?ref=main"
```

### 读取文件内容（base64 解码）

```bash
FILE_PATH="skills/geo-optimization/SKILL.md"
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/contents/$FILE_PATH?ref=main" \
  | python3 -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

### 直接下载（适合大文件）

```bash
# raw.githubusercontent.com 更快，但有时网络不稳定
curl -s "https://raw.githubusercontent.com/jsxuaijun-art/hermes-data/main/skills/geo-optimization/SKILL.md"
```

### 查看最近提交记录

```bash
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/commits?per_page=5" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
for c in data:
    msg = c['commit']['message'].split('\n')[0]
    date = c['commit']['committer']['date'][:10]
    print(f'{date}  {msg}')"
```

### 查看某次提交的改动文件

```bash
COMMIT_SHA="f5b6d5515b205d4b6962c565c74a50ff00cdc63a"
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/commits/$COMMIT_SHA" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
files = data.get('files', [])
for f in files:
    print(f[\"status\"], f[\"filename\"])"
```

## 局限

| 操作 | API 能否 | 替代方案 |
|------|---------|---------|
| 读取文件 | ✅ 可（base64 或 raw） | — |
| 查看目录 | ✅ 可 | — |
| 查看提交历史 | ✅ 可 | — |
| 写入/推送 | ❌ 不可 | 需要本地 git clone + push |
| 大文件（>1MB） | ⚠️ API 有 1MB 限制 | raw.githubusercontent.com |

## 何时使用

1. **新机器首次设置** — 先看看远程有什么，再决定要不要完整克隆
2. **同步出问题但急需某个文件** — 直接下载单个文件到 WSL
3. **Hermes Agent 需要访问远程 skill 但本地没同步** — 通过 API 读取并加载
