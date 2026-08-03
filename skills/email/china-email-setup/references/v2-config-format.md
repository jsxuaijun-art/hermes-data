# himalaya v2.x 配置格式（官方 config.sample.toml 提取，2026.8 验证）

配置文件路径：`~/.config/himalaya/config.toml`（v2 也支持 `$XDG_CONFIG_HOME/himalaya/config.toml`）

## v2 账号结构（扁平键，无 backend 子表）

```toml
[accounts.NAME]
email = "user@example.com"
display-name = "Your Name"
default = true

# ---- IMAP ----
imap.server = "imap.163.com"            # 裸 host[:port] 默认按 imaps:// 处理
# imap.server = "imap://example.com:143"  # 明文+STARTTLS
# imap.server = "imaps://example.com:993" # 隐式TLS
# imap.tls.provider = "rustls" | "native-tls"
# imap.starttls = false

# ---- IMAP 认证（三选一，用哪个写哪个）----
# 机制1: plain（默认推荐）
imap.sasl.plain.username = "user@example.com"
imap.sasl.plain.password.raw = "***"
# imap.sasl.plain.password.command = "pass show example"
# 机制2: login（163 PLAIN 被拒时用这个）
# imap.sasl.login.username = "user@example.com"
# imap.sasl.login.password.command = "cat ~/.config/himalaya/passwd_163"
# 机制3: oauthbearer / xoauth2 / scram-sha-256

# ---- SMTP ----
smtp.server = "smtp.163.com:465"
# smtp.server = "smtp://example.com:587"

# ---- SMTP 认证（与IMAP同理）----
smtp.sasl.plain.username = "user@example.com"
smtp.sasl.plain.password.raw = "***"
# smtp.sasl.plain.password.command = "cat ~/.config/himalaya/passwd_163"
```

## v2 与 v1 关键差异速查

| 项目 | v1.x（废弃） | v2.x |
|------|-------------|------|
| IMAP服务器 | `backend.type="imap"` + `backend.host` + `backend.port` | `imap.server` |
| 加密 | `backend.encryption.type` | 由 URL scheme 决定（imaps:// 或 imap://+starttls） |
| 用户名 | `backend.login` | `imap.sasl.<机制>.username` |
| 密码 | `backend.auth.cmd` | `imap.sasl.<机制>.password.raw` 或 `.password.command` |
| SMTP | `message.send.backend.*` | `smtp.server` + `smtp.sasl.*` |
| 文件夹 | `folder list` | `mailbox list` |
| 验证 | — | `himalaya account check`（v2新增诊断命令） |

## 全局配置示例

```toml
# 下载目录
# downloads-dir = "~/downloads"
# 表格样式
# table.preset = "││──╞═╪╡┆    ┬┴┌┐└┘"
# envelope.list.datetime-fmt = "%F %R%:z"
# envelope.list.page-size = 50
```

## 诊断命令

```bash
himalaya account check          # v2 专用：逐账号检测 imap/smtp 连通与认证
himalaya account list           # 列出账号
himalaya --account NAME ...     # 指定账号
himalaya mailbox list           # v2 列文件夹（v1 是 folder list）
```
