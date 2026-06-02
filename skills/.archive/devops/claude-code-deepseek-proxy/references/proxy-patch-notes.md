# anthropic-proxy Patch 记录

## 文件位置
`/home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy/index.js`

## 快速检查 patch 是否还在
```bash
cd /home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy
grep -c "fastify.head" index.js   # 应为 1（Patch #1）
grep -c "JSON.stringify" index.js # 应为 1（Patch #2）
grep -c "toolName" index.js       # 应为 2（Patch #3 的定义 + 使用）
```

## Patch #1: 添加 HEAD / 和 GET / 健康检查路由
**定位命令:** `grep -n "reply.type" index.js`（在这行之前插入）
**作用:** Claude Code 交互模式启动时会先发 HEAD / 检查

```javascript
// 添加健康检查路由（Claude Code 需要）
fastify.head('/', async (request, reply) => {
  reply.code(200).send()
})
fastify.get('/', async (request, reply) => {
  reply.code(200).send()
})
```

## Patch #2: 修复 tool_call 格式（OpenAI 标准）
**定位命令:** `grep -n "function: {" index.js | head -1`
**问题:** 原代码嵌套了两层 `function` 对象，缺少顶层 `id` 和 `type`
**替换前（错误）:**
```javascript
      function: {
        type: 'function',
        id: toolCall.id,
        function: {
          name: toolCall.name,
          parameters: toolCall.input,
        },
      }
```
**替换后（正确）:**
```javascript
      id: toolCall.id,
      type: 'function',
      function: {
        name: toolCall.name,
        arguments: JSON.stringify(toolCall.input),
      },
```

## Patch #3: 修复 tool_result 消息缺 name 字段
**定位命令:** `grep -n "tool_call_id: toolResult" index.js`
**问题:** DeepSeek API 要求 tool role 消息必须有 name 字段
**替换前（缺 name）:**
```javascript
            messages.push({
              role: 'tool',
              content: toolResult.text || toolContent,
              tool_call_id: toolResult.tool_use_id,
            })
```
**替换后（补 name）:**
```javascript
            // 查找之前 assistant 消息中匹配的 tool_use_id
            let toolName = 'unknown_tool'
            for (const prevMsg of payload.messages) {
              if (prevMsg.role === 'assistant' && Array.isArray(prevMsg.content)) {
                const found = prevMsg.content.find(c => c.type === 'tool_use' && c.id === toolResult.tool_use_id)
                if (found) { toolName = found.name; break }
              }
            }
            messages.push({
              role: 'tool',
              content: toolResult.text || toolContent,
              tool_call_id: toolResult.tool_use_id,
              name: toolName,
            })
```

## 验证所有 patch 正确性
```bash
cd /home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy

echo "Patch #1 (HEAD route): $(grep -c 'fastify.head' index.js)/1"
echo "Patch #2 (JSON.stringify): $(grep -c 'JSON.stringify' index.js)/1"
echo "Patch #2 (no parameters): $(grep -c 'parameters:' index.js)/0 (should NOT exist in tool_calls)"
echo "Patch #3 (tool name lookup): $(grep -c 'toolName' index.js)/2"
```

## 重装后 patch 全部丢失？重新打一遍
```bash
PROXY_DIR="/home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy"
cd "$PROXY_DIR"

# 备份
cp index.js index.js.bak

# Patch #1: 在 POST 路由前插入 HEAD / 和 GET /
LINE=$(grep -n "reply.type" index.js | cut -d: -f1)
sed -i "${LINE}i\\\nfastify.head('/', async (request, reply) => {\\n  reply.code(200).send()\\n})\\nfastify.get('/', async (request, reply) => {\\n  reply.code(200).send()\\n})\n" index.js

# Patch #2 和 #3 手动，因为嵌套结构复杂
echo "手动修补完后重启："
echo "kill \$(cat /tmp/deepseek-proxy.pid) && bash /home/dmin/.local/bin/deepseek-proxy-daemon.sh"
```
