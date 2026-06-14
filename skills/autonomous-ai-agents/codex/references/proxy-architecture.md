# Translation Proxy: Responses API → Chat Completions

翻译代理将 Codex CLI 的 Responses API 转换为标准 Chat Completions API。

## 版本说明

| 版本 | 支持的 Codex 版本 | 传输层 | 策略 | 状态 |
|------|-------------------|--------|------|------|
| **v1** | **v0.135.x** | **HTTPS** | **拒绝 WS（426）→ Codex 降级为 HTTPS POST + streaming** | **✅ 正常工作** |
| v2 | v0.139.0+ | WebSocket | 接受 WS 升级，双向翻译帧 | ❌ 结构性不兼容 |

## v1 架构（当前工作版本）

```
Codex CLI ──GET /v1/responses──→ Proxy(:9090)
  │  (WS Upgrade)                  │
  │←──426 Upgrade Required─────────┤
  │  (HTTP)                        │
  │                                │
  │──POST /v1/responses──────────→ │
  │  (Responses API JSON)          │
  │                                ├─translate() → Chat Completions
  │                                ├─POST /v1/chat/completions (stream=True) → DeepSeek
  │                                ├─SSE chunks → output_text.delta events
  │←─chunked HTTP streaming────────┤
  │  (delta → done → completed)    │
```

## 通信流程 (v1)

1. **WS 升级被拒**：Codex 发送 `GET /v1/responses` 带 `Upgrade: websocket`
2. **426 Upgrade Required**：代理拒绝 WS 升级
3. **HTTPS 降级**：Codex v0.135.x 自动降级为 HTTP POST 到 `/v1/responses`
4. **翻译请求**：将 Responses API JSON 翻译为 Chat Completions 格式
5. **调用 DeepSeek**：`POST https://api.deepseek.com/v1/chat/completions`，`stream=True`
6. **SSE 流处理**：逐条读取 DeepSeek 的 SSE streaming chunks
7. **流式响应**：通过 HTTP chunked encoding 返回 `output_text.delta` → `done` → `completed`

### 关键翻译细节

**input 处理：** Codex 发送的 `input` 字段是数组，每个 item 有 `role` 和 `content`。
- `content` 可能是字符串或对象数组（如 `[{"type": "input_text", "text": "..."}]`）
- `role: "developer"` 必须映射为 `role: "system"`

**instructions 处理：** Codex 发送 `instructions` 作为顶层字段，合并为 system 消息。

**streaming 响应序列：**
```
output_text.delta（×N）→ output_text.done → output_item.done → response.completed
```

## 核心设计

### 1. 多线程 TCP Server（非 HTTPServer）

Python 的 `HTTPServer` 是单线程的——一个 WebSocket 连接是长连接，会阻塞后续请求。使用原生 socket threading：

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.listen(10)
while True:
    client, addr = server.accept()
    threading.Thread(target=serve_client, args=(client, addr), daemon=True).start()
```

### 2. 手动 HTTP 请求解析

代理自己解析原始 HTTP 请求字节（检测 `\r\n\r\n`），判断是 WS 升级还是 HTTPS POST。这样做是因为 WS 连接需要 101 响应后继续使用同一个 socket。

### 3. WebSocket 帧解析（零外部依赖）

RFC 6455 帧格式：

- **Opcode 1**（text frame）→ UTF-8 JSON
- **Opcode 8**（close frame）→ 断开连接
- **Opcode 9**（ping）→ 回复 pong（opcode 0xA）
- **Masked frames** → 客户端→服务器必须 mask（RFC 6455）
- **Extended length** → 126 = 16位长度，127 = 64位长度

### 4. 翻译映射

Responses API → Chat Completions：

| Responses 字段 | Chat 字段 |
|----------------|-----------|
| `input`（字符串） | `messages[].role=user, content=input` |
| `input`（数组） | 多条消息；role `developer` → `system` |
| `instructions` | `messages[0].role=system` |
| `max_output_tokens` | `max_tokens` |
| `tools[].type=function` | `tools[].function={name, description, parameters}` |

Chat Completions → Responses API：

| Chat 字段 | Responses 字段 |
|-----------|----------------|
| `choices[0].message.content` | `output[].content[].type=output_text` |
| `choices[0].message.tool_calls` | `output[].type=function_call` |
| `model` | `model` |
| `usage` | `usage` |

## 常见失败模式

### 1. "Invalid JSON: Expecting value: line 1 column 1 (char 0)"
**原因：** WS 收到了 frame 但 payload 不是合法 JSON。通常是 mask 解码偏移量算错了。

**修复：** 确保 mask key 从 `self.buf[off:off+4]` 读取，`off` 已经递增过 extended-length 字节。

### 2. `[WS] addr: 2b`（帧太短）
**原因：** 发送端构造的 WS frame 在 payload ≥ 126 字节时没有正确使用 extended length。如果长度字节设置为 `0x80 | len` 而没有 extended-length 标志（126），服务器只读 2 字节作为整个 payload。

**修复：**
```python
if len(payload) < 126:
    frame.append(0x80 | len(payload))
elif len(payload) < 65536:
    frame.append(0x80 | 126)
    frame.extend(struct.pack('>H', len(payload)))
```

### 3. 升级后立即断开
**原因：** handle_ws 线程因 `recv_frame()` 返回 None 而退出。客户端发送了无效 frame。

**修复：** 检查客户端 frame 构造。确保 opcode=0x1（text frame），FIN bit 已设置。

### 4. 代理启动失败（端口未监听）  
**原因：** 代理进程启动时崩溃。最常见的原因是 `DEEPSEEK_API_KEY` 未找到或值为 `***`。  

**排查：**  
```bash  
bash -c 'source ~/.hermes/.env && echo "${#DEEPSEEK_API_KEY} chars"'  
python3 -u ~/.hermes/skills/.../codex-proxy.py 2>&1  
```  

### 5. 代理启动成功但 API 返回 401 Unauthorized  
**原因：** 后端指向 `llm.chudian.site/v1` 但 proxy 使用的 `DEEPSEEK_API_KEY`（`sk-bba...`）是官方 DeepSeek 的 key，chudian 要求 `sk-ag-` 前缀的 key。  

**对策：**  
- 使用 `codex-ds`（基于 hermes chat）替代原生 codex → key 由 Hermes 运行时解密 ✅  
- 或手动将 chudian 的 `sk-ag-` key 写入 `~/.codex/auth.json` 的 `OPENAI_API_KEY` 字段  
```bash  
# ~/.codex/auth.json（手动写入）  
{"auth_mode": "apikey", "OPENAI_API_KEY": "***"}  
```  
- 或修改 proxy 脚本中的 `BACKEND_URL` 为 `https://api.deepseek.com/v1`，使用官方 `DEEPSEEK_API_KEY`（但用的是官方模型，非 chudian 的 deepseek-v4-flash）
