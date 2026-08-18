# Node.js 无 sudo 安装指南（适用于 ima-skill）

## 适用场景

- WSL / Linux 环境
- `node --version` 报错 `command not found`
- 无 sudo 权限（或 sudo 需要密码但不可用）

## 安装步骤

```bash
# 1. 下载二进制包 (v20 LTS, x86_64)
curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz \
  -o /tmp/node.tar.xz

# 2. 解压到用户目录
mkdir -p ~/.local/node
tar -xf /tmp/node.tar.xz -C ~/.local/node --strip-components=1

# 3. 临时加入 PATH（当前 shell）
export PATH="$HOME/.local/node/bin:$PATH"

# 4. 持久化到 bashrc
echo 'export PATH="$HOME/.local/node/bin:$PATH"' >> ~/.bashrc

# 5. 验证
node --version   # 应输出 v20.18.0
npm --version    # 应输出 10.8.2
```

## 验证 ima_api 可调用

```bash
SKILL_DIR="$HOME/.hermes/skills/ima-skill"
node "$SKILL_DIR/ima_api.cjs" \
  "openapi/wiki/v1/search_knowledge_base" \
  '{"query":"","cursor":"","limit":5}' \
  2>/dev/null
# 成功应返回 {"code":0,"msg":"success","data":{...}}
```

## 踩坑记录

- 不要用 `apt install nodejs`（需要 sudo）
- 不要用 `snap install node`（需要 sudo）
- 二进制包方式不需要任何管理员权限
- 安装后首次调用 `.cjs` 时确保 `SKILL_DIR` 路径正确指向 ima-skill 目录
