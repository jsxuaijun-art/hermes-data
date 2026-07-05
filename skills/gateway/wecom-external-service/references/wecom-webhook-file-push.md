# 企微Webhook文件推送工作流

> 场景：通过企微群Webhook机器人推送文档/消息到内部群
> 来源：2026.7.1 实战（利润合规20条政策文档推送）

## 前置条件

- 目标群已添加「群机器人」→ 获取Webhook URL
- Webhook地址格式：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx`

## 推送步骤

### 1. 发送Markdown消息（推荐做摘要）

```python
import requests

KEY = "your-webhook-key"
url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={KEY}"

msg = {
    "msgtype": "markdown",
    "markdown": {
        "content": "# 标题\n\n正文内容..."
    }
}

resp = requests.post(url, json=msg)
```

### 2. 上传文件获取media_id

```python
upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={KEY}&type=file"

with open("文件路径.docx", "rb") as f:
    resp = requests.post(upload_url, files={
        "media": ("文件名.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    })

result = resp.json()
media_id = result["media_id"]  # 后续发送文件用
```

### 3. 发送文件消息

```python
file_msg = {
    "msgtype": "file",
    "file": {"media_id": media_id}
}
resp = requests.post(url, json=file_msg)
```

## 支持的文件类型

| 格式 | Content-Type | 说明 |
|------|-------------|------|
| .docx | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Word文档 |
| .pdf | `application/pdf` | PDF文件 |
| .xlsx | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Excel |
| .jpg/png | `image/jpeg` / `image/png` | 图片（也可用图片消息类型） |

## 限制

- 文件大小上限：20MB
- 每个Webhook每分钟最多20条消息
- media_id有效期为3天
- 群机器人Webhook不支持推送到外部群（仅内部群有效）
