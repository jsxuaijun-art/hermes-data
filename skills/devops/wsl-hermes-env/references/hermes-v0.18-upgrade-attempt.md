# Hermes v0.17 → v0.18 升级尝试失败记录

## 场景

2026-07-04 用户在 WSL 环境中想要执行 `hermes update`。

## 尝试过的命令

### 1. 直连 PyPI（默认源）

```bash
pip install --upgrade hermes-agent
```

结果：超时。国内直连 PyPI 极慢（< 100KB/s），文件约 9.3MB。

### 2. 阿里云镜像源

```bash
pip install --upgrade hermes-agent -i https://mirrors.aliyun.com/pypi/simple/
```

结果：cryptography 46.0.7（约 4.5MB）下载到一半超时。

### 3. 后台下载 + 长超时

```bash
pip install --upgrade hermes-agent --default-timeout=120
```

结果：proxy 自动介入（bashrc 设置了 `http_proxy=http://172.23.96.1:7890`），代理连不上。

### 4. 取消代理重试

```bash
pip install --upgrade hermes-agent --proxy ""
```

结果：无效。`--proxy ""` 不覆盖环境变量 `http_proxy`。

### 5. bash --norc 绕过

```bash
env -i HOME="$HOME" PATH="$PATH" bash --norc -c 'pip install --upgrade hermes-agent'
```

结果：下载到 80%+ 后被杀（后台进程被代理超时触发 SIGTERM）。

### 6. 从缓存安装

```bash
pip install --upgrade hermes-agent --no-index --find-links /home/dmin/.cache/pip/
```

结果：缓存不完整（缺少 Pillow 12.2.0），fallback 又走回代理。

## 最终结论

国内 WSL 环境到 PyPI 的网络极不稳定，v0.18.0 未安装成功。维持 v0.17.0。

## 用户偏好

**不要反复尝试不同变体。** 尝试 1-2 次失败后，直接汇报状态给用户，让用户决定下一步（手动下载 .whl 或等待网络改善）。

## 可行替代方案（未执行）

- 用户从 Windows 浏览器下载 .whl 文件，本地 `pip install`（浏览器走代理带宽约 1.3 MB/s，比 CLI 快很多）
- 等网络较好时再试
- 通过阿里云 ECS 下载后 scp 到 WSL
