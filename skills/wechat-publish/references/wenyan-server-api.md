# wenyan-server API 参考

> 阿里云 ECS（47.103.27.171）上运行的公众号发布服务
> 端口：3000 | 进程：wenyan-server（systemd service，PID ~739894）
> Node.js v20.20.2

## 服务器连接

```bash
# SSH 密码登录（仅限本 agent 使用）
SSH_ASKPASS=/tmp/sshpass.sh setsid ssh -o StrictHostKeyChecking=no -o BatchMode=no root@47.103.27.171 '<command>'
```

SSH_ASKPASS 脚本 `/tmp/sshpass.sh` 包含密码（仅 root 可读），由本 agent 自动维护。

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

## wenyan CLI 已知问题

`wenyan publish -f <file> --server <url>` 命令：
- ❌ 返回 EXIT_CODE=0 但无任何 stdout/stderr 输出
- ❌ 无法从 CLI 判断发布是否成功
- ❌ 无法获取 media_id
- ✅ 替代方案：直接用上面 3 个 API 端点

## wenyan core 渲染（生成 HTML payload）

```bash
cd /usr/lib/node_modules/@wenyan-md/cli
NODE_OPTIONS='--experimental-require-module' node -e "
import('/usr/lib/node_modules/@wenyan-md/core/dist/core.js').then(m => {
  const { prepareRenderContext } = m;
  const ctx = prepareRenderContext('/tmp/article_draft.md');
  console.log(JSON.stringify({
    renderResult: ctx.content,
    images: ctx.imageList || [],
    title: ctx.frontMatter.title,
    cover: ctx.frontMatter.cover,
    author: ctx.frontMatter.author,
    abstract: ctx.frontMatter.abstract || '',
    frontMatter: ctx.frontMatter,
    content: ctx.rawContent || ''
  }));
});
" 2>/dev/null > /tmp/publish_payload.json
```

## wenyan-server 日志

```bash
journalctl -u wenyan-server.service --no-pager -n 50
```

上传缓存目录：`/root/.config/wenyan-md/uploads/`
