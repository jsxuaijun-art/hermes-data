# 第1周 · L5 MCP + 邮箱接入（2026-08-02 更新）

## 关键认知（先讲清楚，避免白配）
1. **企业微信已经打通，不是本周任务**。企微走 Hermes gateway 平台通道（wecom/wecom_callback），
   云端已 connected。评估 L5 时企微不计数——MCP 的缺口是"外部工具"：邮箱/Notion/API。
2. **邮箱是本周真正要补的**。目标是让智能体自动读客户邮件、申报通知、政策推送。
3. 本地 WSL 的 `wecom.enabled: false` 是正确的，别去改（防与云端抢 WebSocket 独占连接）。

## ✅ 网易163邮箱：已落地（实测跑通）
- **接入方式**：himalaya 无 POP3，163 的 IMAP 被 "Unsafe Login" 风控拦（新IP/新设备，用户网页确认后仍顽固）。
  **POP3 通道放行**，最终用 Python `poplib` 直连 `pop.163.com:995` 读信（见 china-email-setup 的 `read_163.py`）。
- **账号陷阱（耗了最多时间）**：正确账号是 `jsxuaijun@163.com`（j-s-**x**-u-a-i-j-u-n），
  早期误配 `jsuxaijun@163.com`（少个 x）→ 授权码再对也登不上。排查时务必让用户**从网页版复制完整地址**，不要手打。
- **授权码（2026-08 有效）**：`ZDeZEYw9SZUgJq2M`（POP3/SMTP 均已开启）。旧码 `XQe5QTQTfLJ36Zjz` 已作废。
- **能读什么**：中国电信电子发票、天眼查监控日报、网易安全通知等。
- **⚠️ Unsafe Login 判别**：LOGIN 通过但 SELECT 被拦（`NO SELECT Unsafe Login`）= 网易对新IP风控，
  不是配置问题。不要反复重试触发更高风控，直接切 POP3。

## ✅ L4/L13/L14 落地装置：零成本每日邮件监控 cron（本会话新建）
- **cron job**：「网易163·每日邮件监控」`e2e47848a29a`
  - 调度 `5 9 * * *`（每天09:05，错开9:00的销售搜索任务）
  - 脚本 `~/.hermes/scripts/read_163_daily.py`（POP3 读最近5封，输出简短摘要；无邮件=静默不打扰）
  - 模式 `--script --no-agent`（**零 token，纯脚本**）→ 这就是 L13(零成本监控)+L14(门控) 的实证，也是 L4 单模型下控成本的正道。
- **新增邮件处理**：用户对某封说"读全文/处理"→ 我用 poplib 单独拉那封的完整正文+附件信息。
- 验证方式：`python3 ~/.hermes/scripts/read_163_daily.py` 手动触发确认输出；cron 侧看 `hermes cron list` 的 last_status。

## ❌ 企业微信邮箱 `xuaijun@yingxinkuai.com`：暂缓
- 服务器 `imap.exmail.qq.com:993` / `smtp.exmail.qq.com:465` 在线。
- 客户端专用密码入口用户找不到，疑似与"会员/付费"绑定 → 用户倾向放弃，不做无谓耗时间。若后续开通会员再回补。

## MCP（L5 正式落地，未做）
- 邮箱走的是 himalaya/POP3 本地 CLI，**不是 MCP** —— L5 的 `mcp_servers` 段仍为空，保持 ❌。
- 若要正式升 L5：走 `config.yaml mcp_servers`，stdio transport，npx 包，env 段显式传 IMAP/SMTP 凭据
  （native-mcp 环境变量过滤，密钥不能靠全局 env 透传，必须写在 `env:` 段）。

## 本周验收状态（2026-08-02）
- [x] 智能体能读网易163收件箱并输出摘要（POP3，25封可读）
- [x] 每日定时邮件监控已上线（cron `--no-agent`，零成本）
- [x] 已掌握 L4 单模型下控成本路径（Pitfall 0/0b）
- [ ] config.yaml 出现非空 `mcp_servers` 段 → L5 从 ❌ 升 ⚠️/✅（未做，企微邮箱暂缓，MCP 留待后续）
