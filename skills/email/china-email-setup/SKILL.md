---
name: china-email-setup
description: "国内邮箱接入实战（网易163/QQ/企业微信邮箱）：himalaya v2 配置格式、授权码认证、Windows代理下载、openssl直连排查。bundle技能himalaya只覆盖v1格式且不可patch，v2经验全部放这里。"
version: 1.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, IMAP, SMTP, himalaya, 163, 网易, 企业微信, china]
---

# 国内邮箱接入（himalaya v2 实战）

## 触发条件

- 用户要求接入/配置邮箱（网易163、QQ、企业微信邮箱等国内邮箱）
- 用户提到授权码（163/QQ 的客户端授权码不是登录密码）
- himalaya 报错 `No backend matching auto` 或 `IMAP LOGIN failed` / `AUTHENTICATE PLAIN failed`

## 核心事实：himalaya v1 vs v2 配置格式不兼容

bundle 技能 `himalaya`（无法patch）里的配置全是 v1.x 格式，**v2.0.0 已废弃**：

| 项目 | v1.x（旧） | v2.x（新） |
|------|-----------|-----------|
| 账号段 | `[accounts.NAME]` + backend子表 | `[accounts.NAME]` + 扁平键 |
| IMAP服务器 | `backend.type="imap"` + `backend.host` + `backend.port` | `imap.server = "imap.163.com"` |
| 用户名 | `backend.login` | `imap.sasl.plain.username` 或 `imap.sasl.login.username` |
| 密码 | `backend.auth.cmd` | `imap.sasl.plain.password.raw`（明文）或 `.password.command`（安全，推荐） |
| SMTP | `message.send.backend.*` | `smtp.server` + `smtp.sasl.plain.*` |
| 列文件夹 | `folder list` | `mailbox list`（v2改名） |

**v2 报错特征**：`himalaya account check` 显示 `No backend matching auto`，账号 BACKENDS 列为空。

**v2 密码安全写法**（授权码不落配置明文，放独立文件）：

```toml
[accounts.wangyi163]
email = "jsxuaijun@163.com"
display-name = "江敏-163"
default = true

imap.server = "imap.163.com"
imap.sasl.plain.username = "jsxuaijun@163.com"
imap.sasl.plain.password.command = "cat ~/.config/himalaya/passwd_163"

smtp.server = "smtp.163.com:465"
smtp.sasl.plain.username = "jsxuaijun@163.com"
smtp.sasl.plain.password.command = "cat ~/.config/himalaya/passwd_163"
```

认证机制可选：`plain` / `login` / `oauthbearer` / `xoauth2` / `scram-sha-256`（在 `imap.sasl.<机制>.username` 下选择）。

## 网易163接入要点

1. **授权码 ≠ 登录密码**。须先在 mail.163.com → 设置 → POP3/SMTP/IMAP → 开启服务 → 生成客户端授权码（16位字母数字混合）。
2. **PLAIN 被 163 拒**：报 `BAD Request not ending with` → 换 `login` 机制（`imap.sasl.login.username/password.command`）。
3. **`Login error or password error` = 授权码本身不被认可**（服务未开启/授权码错误/已重置），不是配置问题。需回网页重新生成新授权码。
4. **⚠️ 账号拼写是最大陷阱**：常见邮箱名（如 `xuaijun`）很容易被误拼。一个字符差，授权码再对也登不上。排查时先让用户从网页版**复制完整邮箱地址**，不要手打。
5. **"Unsafe Login" 风控拦截 SELECT**：登录通过（`account check` 显示 IMAP/SMTP 都 OK，`LOGIN completed`），但读收件箱时报 `NO SELECT Unsafe Login. Please contact kefu@188.com`。这是网易检测到从新 IP/新设备登录的安全验证。**两种解法**：
   - **方案A（需用户操作）**：网页版 mail.163.com → 登录后确认新设备登录（短信/扫码验证）→ 再试 IMAP。注意网易对第三方客户端新 IP 风控很顽固，用户确认后可能仍报 Unsafe Login。
   - **方案B（推荐，实测管用）**：**网易对 POP3 通道放行**，IMAP 被风控拦时 POP3 能直接读。但 **himalaya 不支持 POP3**（`himalaya --version` 的 feature 列表里没有 `+pop3`），需用 Python `poplib` 脚本直连 `pop.163.com:995`。这正是绕过 163 风控的可靠落地路径（见 `scripts/read_163.py`）。
6. 服务器地址：
   - IMAP: `imap.163.com`（端口993，TLS）
   - SMTP: `smtp.163.com:465`（SMTPS）
7. **openssl 直连排查**（绕过 himalaya 看服务器原始响应）：
   ```bash
   timeout 15 bash -c '
   openssl s_client -connect imap.163.com:993 -quiet 2>/dev/null <<EOF
   a1 LOGIN jsxuaijun@163.com <授权码>
   a2 LOGOUT
   EOF' 2>&1 | grep -E 'a1 OK|a1 NO|a1 BAD'
   ```
   `a1 NO LOGIN Login error or password error` → 凭据问题，非配置问题。
8. **调试模式**：`RUST_LOG=debug himalaya account check` 可看到 SASL 认证交换过程（如 `challenge received, sending username` / `challenge received, sending password`），确认凭据是否成功发送到服务器。

## 企业微信邮箱（腾讯企业邮）接入要点

1. **服务器地址**：
   - IMAP: `imap.exmail.qq.com`（端口993，TLS）
   - SMTP: `smtp.exmail.qq.com:465`（SMTPS）
2. **认证机制**：支持 `AUTH=PLAIN` 和 `AUTH=LOGIN`（服务器 CAPABILITY 直接返回，无需像 163 那样强制切换机制）。
3. **授权码获取**（非管理员也可自行生成）：
   - 打开网页版企业邮箱 exmail.qq.com → 扫码登录
   - 设置 → 客户端设置 → 生成「客户端专用密码」（即授权码）
   - 如果找不到该选项 → 需要管理员在**企业微信管理后台**（admin.weixin.qq.com）→ 协作 → 邮件 → 邮箱设置 → 开启「允许第三方客户端收发邮件」
   - **⚠️ 用户反馈：客户端授权功能可能与企业邮『会员/付费』绑定**。找不到入口或管理员关不掉时别耗时间，判断是否需开通会员；若用户没意愿掏钱，直接放弃该邮箱接入，先用 163。
4. **himalaya v2 配置示例**（与 163 格式一致，仅换服务器地址和账号）：
   ```toml
   [accounts.yingxin]
   email = "xuaijun@yingxinkuai.com"
   display-name = "江敏-企微"
   default = false

   imap.server = "imap.exmail.qq.com"
   imap.sasl.plain.username = "xuaijun@yingxinkuai.com"
   imap.sasl.plain.password.command = "cat ~/.config/himalaya/passwd_yingxin"

   smtp.server = "smtp.exmail.qq.com:465"
   smtp.sasl.plain.username = "xuaijun@yingxinkuai.com"
   smtp.sasl.plain.password.command = "cat ~/.config/himalaya/passwd_yingxin"
   ```
5. **openssl 直连测试**：
   ```bash
   timeout 15 bash -c '
   openssl s_client -connect imap.exmail.qq.com:993 -quiet 2>/dev/null <<EOF
   a1 LOGIN xuaijun@yingxinkuai.com <授权码>
   a2 LOGOUT
   EOF' 2>&1 | grep -E 'a1 OK|a1 NO|a1 BAD'
   ```

## Windows代理下载（国内网络安装）

install.sh 从 GitHub 下载二进制经常超时。Windows 宿主机有代理时直接走：

```bash
WIN_IP=172.23.96.1   # 从 /etc/resolv.conf 或 ip route 查宿主机IP
# 先查最新版本（GitHub API）
curl -s --proxy "http://$WIN_IP:7890" https://api.github.com/repos/pimalaya/himalaya/releases/latest | grep tag_name
# 下载 x86_64-linux 二进制
curl -sL --proxy "http://$WIN_IP:7890" -o /tmp/himalaya \
  https://github.com/pimalaya/himalaya/releases/download/v2.0.0/himalaya-x86_64-linux.tar.gz
tar -xzf /tmp/himalaya.tar.gz -C /tmp && mv /tmp/himalaya ~/.local/bin/
```

## 配置验证（区分"本地配置健康" vs "外部凭据有效"）

配置本身可本地验证（TOML语法、键名、密码文件存在与权限、二进制版本）；**授权码是否被服务器认可必须联网测，验证脚本测不了**。

验证要点：
- TOML 用 python `tomllib.load` 解析
- 密码文件权限应为 `600`
- `himalaya --version` 确认 v2.x
- 联网认证结果只能靠 `himalaya account check` / openssl 直连

## himalaya v2 常用命令速查

| 操作 | v1.x 命令 | v2.x 命令 |
|------|-----------|-----------|
| 列文件夹 | `himalaya folder list` | `himalaya mailbox list` |
| 读邮件列表 | `himalaya envelope list --folder Inbox` | `himalaya envelope list -m Inbox` |
| 账号检查 | — | `himalaya account check` |
| 配置验证 | — | `himalaya account check --verbose` |

v2 的 `envelope list` 用 `-m <NAME>` 指定邮箱（mailbox），不再用 `--folder`。

## 待办状态（2026.8）

- 网易163 `jsxuaijun@163.com`：✅ **已通过 POP3 通道落地**（IMAP 被 Unsafe Login 风控拦，himalaya 无 POP3，改用 `scripts/read_163.py` 读信）。授权码已在脚本中，可直接读 25 封邮件。
- 企业微信邮箱 `xuaijun@yingxinkuai.com`：服务器待确认在线，但**客户端专密码入口用户找不到，疑似需会员/付费** → 用户倾向放弃，暂缓。

## 支撑文件

- `references/v2-config-format.md` — himalaya v2.x 完整配置格式（官方 sample 提取），含 v1/v2 差异速查表
- `scripts/probe-163-imap.sh` — openssl 直连探测 163 授权码是否有效（用法见脚本头注释）
- `scripts/read_163.py` — **POP3 读信脚本**（163 被 IMAP 风控时的落地方案，himalaya 无 POP3，用此脚本直连 pop.163.com:995）。复制到桌面改 USER/PASS 即可用。
- **每日监控落地**：`~/.hermes/scripts/read_163_daily.py` 是 read_163.py 的摘要版（读最近5封，无邮件静默），已注册为 cron「网易163·每日邮件监控」（`--script --no-agent`，每天09:05，**零 token**）。新邮箱接入也可照此套一个 daily 监控 cron。详见 hermes-15-level-upgrade `references/week1-email-mcp.md`。
