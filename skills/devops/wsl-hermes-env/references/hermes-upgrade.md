# Hermes 升级工作流

## 本地（WSL）

### 前置条件

```bash
# Python ≥ 3.11
python3 --version   # 如果 < 3.11
sudo apt install python3.11
```

### 新建 venv

```bash
cd /tmp
python3.11 -m venv hermes-upgrade
source hermes-upgrade/bin/activate
```

### 下载 + 安装

```bash
# 最快方式：走代理
export http_proxy=http://172.23.96.1:7890
export https_proxy=http://172.23.96.1:7890

# 下载（~27MB, ~20s）
curl -L -o hermes.tar.gz https://github.com/nousresearch/hermes-agent/archive/refs/tags/vX.Y.Z.tar.gz

# 解压（注意：tar 有时会超时漏掉 tools/ 目录，需单独补解）
tar xzf hermes.tar.gz
# cd 进解压目录，检查 tools/ 是否完整
ls hermes-agent-*/tools/   # 如果为空，单独解压 tools 子目录

# 安装
cd hermes-agent-*/
pip install -e .
```

### CLI 变更注意

新版 CLI 用 `chat -q` 代替旧版 `chat -z`。

### 验证

```bash
hermes version
hermes chat -q 'hello'
```

---

## 云端（阿里云 ECS 47.103.27.171）

### 自动化 SSH（sshpass）

```bash
sshpass -p '密码' ssh root@47.103.27.171 'hermes version'
# 或 scp 升级包上去再安装
```

### 坑

- **fail2ban**：连续失败 SSH 会封 IP，需先解封或改用密钥登录
- **Gateway 重启**：需协调业务中断窗口，通知用户后再执行

### 推荐流程

1. 先本地测试新版本
2. 通知业务窗口
3. sshpass 上传 + 安装
4. 重启 Gateway
5. 验证连通性
