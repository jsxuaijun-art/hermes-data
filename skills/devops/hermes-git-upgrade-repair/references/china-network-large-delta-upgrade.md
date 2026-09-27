# China 网络大增量升级 · gh-proxy zip 断点续传 + 快照提交法（2026.9 实测，v0.20.x → v0.21.4）

## 结论先行
- 本次是**月度大增量**（0.20.x→0.21.4，git delta ~66MB / 333k objects）。反复尝试证明：
  - **git fetch 经代理拉大包会在收尾处被节点切断**（curl 92 HTTP/2 CANCEL、curl 56 GnuTLS
    early-EOF），且 **git 无法续传 pack——每次重试都从零开始**（实测 5 次 × 共 2.6h 全废）。
  - gh-proxy.com 的 **git** 端点同样被限速（~30KB/s），不可接受。
  - **gh-proxy.com 的 zip 下载支持 HTTP 206 断点续传**（源码整包 83.5MB），`curl -C -`
    循环可自愈穿越节点断流。
- 可靠路径 = **zip 断点续传 + 全量 CRC 校验 + 快照提交升级**。

## 1. 断点续传下载（自愈循环）
```bash
url="https://gh-proxy.com/https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
for i in $(seq 1 20); do
  curl -L -C - --http1.1 -o /tmp/hermes-main.zip "$url" && break
  echo "retry $i"; sleep 3
done
```
- `--http1.1` 避开 HTTP/2 early-EOF 重置（proxy 节点对 HTTP/2 流极不稳定）。
- `-C -` 断点续传：任何断流后重跑从已下载处继续，不自废武功。

## 2. 全量 CRC 校验（必做，勿跳过）
```bash
python3 - <<'PY'
import zipfile
z = zipfile.ZipFile('/tmp/hermes-main.zip')
bad = z.testzip()
print('ALL OK' if bad is None else f'BAD CRC: {bad}', f'{len(z.namelist())} entries')
PY
```
⚠️ 旧 partial 若来自早前 SSL-EOF 中断，**可能已损坏**：即便续传后文件"完成"，zip 仍是坏的
（本次实测：38MB partial 续传完成后 unzip 报 `bad CRC on agent/agent_init.py`）。
**校验失败 → 删掉整包重新下载**，绝不要续传中毒的 partial。

## 3. 快照式升级（适用于干净 upstream clone：`.git` 即上游仓库，无本地数据 commit）
原理：把新版源码树整体 commit 成一个"升级快照"（父提交 = 旧 HEAD），
**回滚始终是一条 `git reset --hard <tag>`**——比 rsync 覆盖更可回退、历史更清晰。

```bash
cd /home/dmin/hermes-agent
git tag pre-upgrade-$(date +%Y%m%d)          # ① 回滚点
unzip -q /tmp/hermes-main.zip -d /tmp/hu
rsync -a --delete /tmp/hu/hermes-agent-main/ . \
  --exclude='.git' --exclude='venv' --exclude='.env' \
  --exclude='skills/' --exclude='.gitignore' --exclude='.gitattributes'
# --delete 安全前提：确认 untracked 用户文件（如 skills/tax-audit-response）已被 exclude
# 覆盖；该目录通常也在 .gitignore 里，git add -A 不会吞掉它（升级后用 git status 复核）
git add -A && git commit -m "Upgrade to upstream main v0.21.4"
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
~/.venv-hermes/bin/pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

回滚：`git reset --hard pre-upgrade-<日期>` + 重装依赖。
升级后清理：删 `.git/objects/pack/tmp_pack_*`（多次失败 fetch 残留的大文件）、
`git remote remove <临时remote>`、`git config --unset http.proxy https.proxy`（仓库级）。

## 4. 验证
```bash
~/.venv-hermes/bin/python -c "import run_agent, hermes_cli; print('IMPORT OK')"
~/.venv-hermes/bin/hermes --version     # Hermes Agent v0.21.4 ...
timeout 90 ~/.venv-hermes/bin/hermes doctor | grep -E 'Version files consistent|Security Advisories'
```
`hermes doctor` 显示 `Version files consistent (0.21.4)` = 磁盘代码与 pyproject 一致。

## 5. 错误串速查
| 报错 | 含义 | 处置 |
|------|------|------|
| `curl: (92) HTTP/2 stream 0 was not closed cleanly ... CANCEL` | 大单文件被节点切断 | 加 `--http1.1`，用 `-C -` 续传 |
| `curl: (56) GnuTLS recv error (-110): The TLS connection was non-properly closed` | 同上的 TLS 变体 | 同上 |
| `unzip: ... bad CRC` / `zipfile testzip BAD CRC` | partial 本身损坏 | **整包重下**，勿续传 |
| `hermes --version` 报 `Update available — run 'hermes update'` | **正常假象**：快照提交后上游又前进几个 commit | 版本号正确（v0.21.4）即忽略 |

## 6. 其它实测事实
- WSL 连 Windows Clash：Clash 只绑 `127.0.0.1:7890`（Windows 宿主）；WSL 侧用网关
  `172.23.96.1:7890`（不要用 127.0.0.1）。
- git 端点与 zip 端点的网络行为不同：git pack 一次大传输必被切断且无法续传；
  zip 走 codeload 分片 + range 续传，反而最稳。
