# 企微回调基础设施 + URL 验证排障 (2026.9 实测)

## 服务器回调设施（复用，勿另起炉灶）
- ECS: `47.103.27.171`（root SSH）
- 域名: `callback.yingxinkuaiji.com`（Let's Encrypt 证书）
- nginx: `/wecom/callback` → proxy 到 `127.0.0.1:8800`
- 后端: `/opt/wecom-bot/hermes_bridge.py`
- systemd 单元: `wecom-bridge.service`（WeCom Callback Bridge -> Hermes）
- 凭证三件套（新 Agent 配「接收消息」直接复用，加密方式选**安全模式**）：
  - CorpID: `wwc7fc356cf7297e7f`
  - Token: `e23hCHGJGmTmFyAxswEb4G`
  - EncodingAESKey: `ELNEV9LRSaAERI88WQru5wGrB7IDhgcQHTbpSi7yOIH`

## 报错「openapi回调地址请求不通过」的三个根因（按排查顺序）
1. **nginx rewrite 路径错位**：若 nginx 把 `/wecom/callback` 重写成 `/wecom` 再转发，而后端路由是 `/wecom/callback`，验签请求打到后端就 404。
   判定：`curl http://127.0.0.1:8800/wecom/callback` → 命中(403 验签失败) ；`/wecom` → 404。
   修：去掉 rewrite，让 `/wecom/callback` 原样透传，`nginx -t && systemctl reload nginx`。
2. **sites-enabled 旧备份抢域名**：reload 时报 `conflicting server name` 是信号——sites-enabled 里残留 `callback.bak.<时间戳>` 与正式配置抢同一域名，nginx 可能加载了带 bug 的旧备份。
   修：把失效备份移出 sites-enabled，再 reload 验证。
3. **wechatpy check_signature 参数顺序错位（最常见真病根）**：
   - wechatpy `WeChatCrypto.check_signature(self, signature, timestamp, nonce, echo_str)` —— 参数顺序是 **(签名, 时间戳, nonce, echostr)**。
   - 老代码误写成 `check_signature(timestamp, nonce, echostr, msg_signature)`，全参数错位 → 验签永远失败 → 控制台一直「不通过」。
   - 修：`check_signature(msg_signature, timestamp, nonce, echostr)`。
   - 改完 `hermes_bridge.py` 后用 `systemctl restart wecom-bridge.service`，`ss -ltnp | grep 8800` 确认新 pid 在听。

## 验证：无需控制台，端到端模拟微信 URL 验证
跑 `scripts/verify_wecom_callback.py`（传入 Token/AESKey/CorpID/URL），它按企业微信「安全模式」构造一次真实 GET 验签请求并比对回包。要点（脚本已内建）：
- 用 `wechatpy.enterprise.crypto.PrpCrypto`，**key 必须是 base64 解码后的 bytes**：`base64.b64decode(AES + '=')`（直接传字符串报 `key must be bytes-like`）。
- `PrpCrypto(key).encrypt(echostr, corp_id)` 返回 **bytes**，参与排序/签名前要 `.decode()` 成 str。
- `msg_signature = sha1(''.join(sorted([TOKEN, timestamp, nonce, encrypted])).hexdigest()`。
- GET `URL?msg_signature=&timestamp=&nonce=&echostr=<encrypted>`，**响应 body == 明文 echostr** 即 URL 验证通过，可放心回到控制台点保存。
