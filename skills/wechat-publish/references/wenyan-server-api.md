# wenyan-server API 参考

> 阿里云 ECS（47.103.27.171）上运行的公众号发布服务
> 端口：3000 | 进程：wenyan-server（systemd service，PID ~739894）
> Node.js v20.20.2

## 服务器连接

```bash
# SSH 密钥登录（推荐，本环境可用）
ssh -o StrictHostKeyChecking=no root@47.103.27.171 '<command>'

# SSH 密码登录（备用，需 SSH_ASKPASS 脚本）
SSH_ASKPASS=/tmp/sshpass.sh setsid ssh -o StrictHostKeyChecking=no -o BatchMode=no root@47.103.27.171 '<command>'
```

SSH_ASKPASS 脚本 `/tmp/sshpass.sh` 包含密码（仅 root 可读），由本 agent 自动维护。
**2026.6.30 确认：SSH key 认证可用（~/.ssh/id_ed25519），无需密码脚本。**

## API 端点

### 1. 健康检查
```
GET http://localhost:3000/
```
返回：`{"status":"ok","message":"wenyan-md server is running"}`

### 2. 上传文件
```
POST http://localhost:3000/upload
Content-Type: multipart/form-data
Body: file=@<filepath>
```

用途：上传封面图（jpg/png）或 JSON 载荷文件

返回（上传封面图）：
```json
{"fileId":"550e8400-e29b-41d4-a716-446655440000","url":"asset://550e8400-e29b-41d4-a716-446655440000.jpg"}
```

返回（上传 JSON 载荷）：
```json
{"fileId":"1d7db3db-b000-4608-9c23-f4a63cb157cd.json"}
```

上传后的文件存储在 `/root/.config/wenyan-md/uploads/` 目录。

### 3. 发布到微信草稿箱
```
POST http://localhost:3000/publish
Content-Type: application/json
Body: {"fileId": "<fileId_from_upload>"}
```

返回（⚠️ 注意嵌套 JSON 结构）：
```json
{"output": "{\"media_id\":\"ZIKXbXZdS_X3B-GDVk11B0VpI8V9DFvV3LwAji2qJEWkYMIrBotKcXkaiCWPdVev\"}"}
```

media_id 提取方式（Python 3）：
```python
import json
resp = json.loads(raw_response)
if 'output' in resp and isinstance(resp['output'], str):
    inner = json.loads(resp['output'])
    media_id = inner.get('media_id', '')
```

## JSON 载荷格式（用于 /upload 后发布）

```json
{
  "renderResult": "<全文渲染后的 HTML，含 wenyan 样式>",
  "images": [],
  "title": "文章标题",
  "cover": "asset://<封面图UUID>.jpg",
  "author": "盈信税务 / 江敏",
  "abstract": "120字以内摘要，显示在卡片上",
  "frontMatter": {
    "title": "文章标题",
    "author": "盈信税务",
    "cover": "asset://<封面图UUID>.jpg",
    "abstract": "摘要",
    "image_list": [],
    "date": "2026-06-23T00:00:00.000Z"
  },
  "content": "全文 Markdown 原文"
}
```

注意：
- `cover` 字段必须是 asset:// 协议的 URL（来自 /upload 上传封面图的返回）
- `renderResult` 里的图片引用需已通过 /upload 上传
- `content` 字段为原始 Markdown 内容

## wenyan CLI 发布（推荐，一键完成）

`wenyan publish -f <file> --server <url>` 命令（2026.6.30 已验证）：
- ✅ 发布成功时输出 `"发布成功，Media ID: <id>"`
- ✅ 可正常获取 media_id
- ⚠️ `@wenyan-md/core` 包未安装，核心渲染嵌入在 CLI 包内，直接调 CLI 即可

**2026.6.30 实测工作命令：**
```bash
NODE_OPTIONS='--experimental-require-module' \
node /usr/lib/node_modules/@wenyan-md/cli/dist/cli.js \
publish -f /tmp/article_draft.md \
--server http://localhost:3000 \
-c /etc/wenyan/yingxin-theme.css
```

**完整工作流（3步 vs 旧4步）：**

以前需要：上传封面 → 手动调用 core 渲染 → 上传 payload → 发布
现在简化：上传封面 → CLI publish（一步完成渲染+发布）

```
Step 1: scp 文章到服务器 → /tmp/article_draft.md
Step 2: curl Unsplash 封面图 → /tmp/cover_article.jpg
Step 3: curl POST /upload 上传封面 → 拿到 asset:// URL
Step 4: sed 替换 cover 路径 → 运行 CLI publish → 拿到 Media ID
```

> 注：`wenyan-server` 的 `/` 端点返回 `Cannot GET /`（非错误），已确认 `/upload` 和 `/publish` 端点正常工作。

## wenyan core 渲染（⚠️ 核心包未单独安装，直接调 CLI 即可）

`@wenyan-md/core` 包**未安装在服务器上**（`/usr/lib/node_modules/@wenyan-md/core/` 不存在），核心渲染能力已嵌入 CLI 包内。

不要单独调 core 渲染 —— 直接用 `CLI publish` 一步完成。
如仍需要手动生成 HTML payload，可改用 CLI 的 serve 或传入主题参数。

## wenyan-server 日志

```bash
journalctl -u wenyan-server.service --no-pager -n 50
```

上传缓存目录：`/root/.config/wenyan-md/uploads/`
