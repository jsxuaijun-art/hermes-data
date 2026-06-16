# IMA 凭证配置记录（徐爱军）

## 凭证获取页面

- https://ima.qq.com/agent-interface（需登录 ima.qq.com）

## 必需凭证

- **Client ID** — 页面显示的一串字符
- **API Key** — 页面显示的密钥字符串

## 存储位置

| 文件 | 内容 |
|------|------|
| `~/.config/ima/client_id` | Client ID |
| `~/.config/ima/api_key` | API Key |

权限：`chmod 600 ~/.config/ima/{client_id,api_key}`

## API 认证方式

所有请求在 Header 中携带：

```
ima-openapi-clientid: <client_id>
ima-openapi-apikey: <api_key>
Content-Type: application/json
```

Base URL: `https://ima.qq.com`
