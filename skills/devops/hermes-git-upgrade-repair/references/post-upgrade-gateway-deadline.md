# 升级后 "Error: Gateway starting: deadline" 诊断与修复

场景：Hermes v0.20.6 → v0.22.5（gh-proxy zip 覆盖安装/快照式升级）后，
`hermes` / `hermes chat` 启动即报 `Error: Gateway starting: deadline` 退出。
2026-10-29 WSL 实测。

## 关键判断链

1. **先隔离包装层**。`hermes` 命令可能是 alias/wrapper（本机 `hermes` aliased 到
   `~/.hermes/hermes-wsl.sh`，它先跑云端企微检查再 `exec .../bin/hermes chat`）。
   直接探测底层二进制区分「二进制坏了」vs「wrapper/服务层问题」：
   ```bash
   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY   # 本机直连信道需清代理
   /home/dmin/.venv-hermes/bin/hermes --version           # 能跑 = 二进制健康
   /home/dmin/.venv-hermes/bin/hermes --help | head       # 列 gateway 子命令
   ```
2. **看 systemd user unit 状态**：
   ```bash
   systemctl --user status hermes-gateway
   ```
   `Active: failed (Result: exit-code)`、Main PID `status=1/FAILURE` → 旧 gateway
   已停但新版起不来。journal 里常同时有
   `Shutdown diagnostic — other hermes processes running`（旧 chat 进程残留）。
3. **根因**：zip 覆盖只换磁盘代码，`~/.config/systemd/user/hermes-gateway.service`
   的 ExecStart 仍指向旧安装（旧目录/旧参数），新版 gateway 启动流程与之不兼容，
   CLI 的健康检查死等（deadline）后报错退出。

## 修复（顺序执行）

```bash
hermes gateway stop            # 停旧服务（必要时 systemctl --user stop）
pkill -f "hermes_cli.main gateway"   # 清残留，别误杀当前 chat 进程
hermes gateway install         # 重写 unit 到当前安装 + 自动 start
hermes gateway status          # 验证 active(running)，且不再超时
```

`hermes gateway install` 实测关键输出：
```
↻ Repairing outdated user systemd service ...
✓ User service definition updated
✓ User service started
```

## 验证要点

- unit 里 ExecStart 的 sys.path 指向**新版**源码目录
  （`sys.path.insert(0, '<新版目录>')`），不再是旧路径。
- `journalctl --user -u hermes-gateway -b` 无 exit-code=1，有新 Main PID。
- 重启后在**新终端**跑 `hermes`（wrapper 或裸二进制均可）不再卡 deadline。

## 顺带观察

- 新 gateway 可能打 SQLite WAL-reset 警告（linked SQLite 3.37.2 旧于 3.51.3）——
  属 `hermes update` 可自修复的提示，不影响功能，勿当故障。
- zip 覆盖安装后 `hermes --version` 显示 `vunknown / Install method: unknown`
  属正常（乱入目录无 `.git`），功能正常，别误判。
- 排查时直接调 `/home/dmin/.venv-hermes/bin/hermes <subcmd>` 绕开 hermes-wsl.sh
  wrapper，避免其云端 SSH 检查干扰判断。
