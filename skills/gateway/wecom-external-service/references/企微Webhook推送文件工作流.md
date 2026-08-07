# 企微Webhook推送文件工作流

> 适用场景：需要将文档（Word/Markdown/图片等）推送到企微内部群/客户群
> 方式：通过企微群Webhook机器人API

---

## 一、前置条件

1. 在目标企微群中创建Webhook机器人（群设置 → 群机器人 → 添加机器人）
2. 获得Webhook URL，格式：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## 二、发送流程

### 步骤1：上传文件获取 media_id

```python
import requests

KEY = "your-webhook-key"
DOCX_PATH = "/path/to/document.docx"

upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={KEY}&type=file"

with open(DOCX_PATH, "rb") as f:
    resp = requests.post(
        upload_url,
        files={"media": (os.path.basename(DOCX_PATH), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
result = resp.json()
# {"errcode": 0, "errmsg": "ok", "type": "file", "media_id": "xxx", "created_at": "1234567890"}
media_id = result["media_id"]
```

### 步骤2：发送Markdown摘要消息（可选）

```python
markdown_msg = {
    "msgtype": "markdown",
    "markdown": {
        "content": "# 标题\n\n摘要内容..."
    }
}
requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={KEY}", json=markdown_msg)
```

### 步骤3：发送文件

```python
file_msg = {
    "msgtype": "file",
    "file": {"media_id": media_id}
}
resp = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={KEY}", json=file_msg)
# {"errcode": 0, "errmsg": "ok"}
```

## 三、支持的文件类型

| 文件类型 | MIME类型 | 说明 |
|---------|----------|------|
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Word文档 |
| .pdf | application/pdf | PDF文件 |
| .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | Excel |
| .jpg/.png | image/jpeg, image/png | 图片 |
| .txt | text/plain | 文本文件 |

文件大小限制：20MB以内。

## 四、常见问题

### Q: Markdown发送后显示乱码？
A: 企微Webhook的markdown格式支持有限，不要用太复杂的表格或代码块。

### Q: 文件上传失败(errmsg: media file size too big)？
A: 文件超过20MB限制，需压缩或拆分。

### Q: 可以同时发多个文件吗？
A: 不支持一次API调用多文件。需要多次调用，每次上传+发送一个文件。

---

## 五、完整代码模板

```python
import requests, json, os

def push_to_wecom_group(webhook_key, docx_path, summary_md=None):
    """推送到企微群"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    # 1. 上传文件
    upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={webhook_key}&type=file"
    with open(docx_path, "rb") as f:
        r = requests.post(upload_url, files={"media": (os.path.basename(docx_path), f, 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    rj = r.json()
    assert rj["errcode"] == 0, f"上传失败: {rj}"
    
    # 2. 发摘要（可选）
    if summary_md:
        requests.post(url, json={"msgtype": "markdown", "markdown": {"content": summary_md}})
    
    # 3. 发文件
    r = requests.post(url, json={"msgtype": "file", "file": {"media_id": rj["media_id"]}})
    return r.json()
```