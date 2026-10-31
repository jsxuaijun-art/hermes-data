# 小智 PC 控制（C 方案）——语音控制 Windows 电脑

> 2026-10-24 实现并实测。**服务器侧 2026-10-24 深夜部署完成，同日 23:52-23:54 全链路验收通过**（SSH=ubuntu 用户非 root；腾讯云控制台放行 TCP 8001 后实测：打开记事本×2/中文打字/打开文件管理器/打开"工作"均成功，服务器日志有完整 pc_control 调用记录）。
> 交付物：桌面「小智AI_PC控制_C方案_2026-10-24」（含 C方案落地总结_2026-10-24.txt）；本文件为归档说明。

## 架构

```
小智设备 →(WiFi/公网) 腾讯云 xiaozhi-esp32-server 容器
                        └─ pc_control 插件（plugins_func/functions/pc_control.py，新版接口）
                              ↓ ws://172.18.0.1:8001（= 容器网络网关，每台机都可能不同！）
                        pc-relay（宿主机 systemd 服务 pc-relay，端口 8001）
                              ↓ 电脑主动外连（CGNAT 无感）
                        本机 pc_agent.py → pyautogui
```

- 方向永远电脑→服务器，家里 CGNAT 不用管
- relay 只依赖 websockets；agent 依赖 websockets/pyautogui/pyperclip
- token 双端一致；relay 无 token 拒绝启动（防裸奔）
- **本次部署 token：`53bc4f5faf6c80f76c297c176df3cbeb`**（已内置 start-agent.bat）

## 四个组件（都在交付文件夹）

| 文件 | 位置 | 作用 |
|---|---|---|
| pc_agent.py | Windows 本机 | WebSocket 客户端 + pyautogui 执行 |
| start-agent.bat | Windows 本机 | 双击启动；自动装依赖（阿里云源）；自动挑 Python |
| pc_relay.py | 服务器宿主机 | asyncio+websockets 中转；agent 长连接、插件一问一答 |
| plugin_pc_control.py | 服务器容器内 | **新版接口**：`@register_function("pc_control", DESC, ToolType.SYSTEM_CTL)` + `ActionResponse` |
| deploy-pc-control.sh | 服务器 | 一键部署：抓接口参考→装插件→起 relay→改 config 三处（幂等+备份+YAML 校验）→重启→自检→失败自动回滚 |
| test_e2e.py | 本机 | 联调自测：模拟插件发指令，断言焦点后才打字 |

## 关键事实（2026-10-24 深夜部署时确认的服务器现状）

- **登录用户是 `ubuntu` 不是 root**（腾讯云 CVM Ubuntu 默认镜像；VM-0-15-ubuntu）；`ubuntu` 有免密 sudo；docker 命令必须加 sudo；部署目录 `/home/ubuntu/xiaozhi-deploy/`
- **小智版本较新，插件接口全变**：
  - 插件目录 `plugins_func/functions/`（平铺 .py，`auto_import_modules` 自动导入注册，不用改 register）
  - 注册方式 `@register_function(name, desc, ToolType)`，desc 是 `{"type":"function","function":{...}}` OpenAI 格式
  - 执行签名 `async def fn(conn, **llm_args)`，返回 `ActionResponse(Action.REQLLM, result, None)`（REQLLM=结果交回 LLM 组织语音回复；RESPONSE=直接念）
  - 配置读取 `conn.config.get("plugins", {}).get("<函数名>", {})`
  - 函数启用：`selected_module.Intent: function_call` + `Intent.function_call.type: function_call` + `functions: [名字]`（**overlay 列表整体替换 base**，不是合并）
  - **RAG 插件 `search_from_ragflow` 这版自带**（functions/ 里就有），RAG 只需配 `plugins.search_from_ragflow`（base_url 不带 `/api/v1/retrieval` 后缀，插件自己拼）
- **docker 网关是 172.18.0.1 不是 172.17.0.1**（compose 网络 xiaozhi-deploy_default）——deploy 脚本已改为 `docker inspect` 自动探测
- 服务器缺 python3-venv，deploy 脚本 apt 自动装（走腾讯云镜像源，很快）
- 函数列表日志（「当前支持的函数列表」）是**设备连接时**才打印，服务器重启后日志里没有是正常的，别误判失败
- 验证插件是否生效的正确姿势：容器内跑 `load_config()` 模拟加载链路断言（见下）

```bash
# 验证 pc_control 在生效配置里（不依赖设备连接）
sudo docker exec -w /opt/xiaozhi-esp32-server xiaozhi-esp32-server python -c "
import asyncio
from config.config_loader import load_config
cfg = asyncio.run(load_config())
m = cfg['selected_module']['Intent']
assert cfg['Intent'][m]['type'] == 'function_call' and 'pc_control' in cfg['Intent'][m]['functions']
print('OK')"
```

## 指令集

open_app（应用映射表+未收录直接喊 exe 名）/ type（中文长文走剪贴板粘贴，完成后还原剪贴板）/ scroll / hotkey；click/move 默认拒绝（`PC_AGENT_ALLOW_POINTER=1` 才开）。

## 踩过的坑（重要，改代码前先读）

1. **焦点竞争**：`start notepad` 后窗口要 0.5-2s 才出现并抢焦点，立刻 ctrl+v 会把字打进别的窗口（实测污染过一次用户的记事本，文件未保存才幸免）。解法：open_app 轮询等新窗口→`_force_foreground`（AttachThreadInput 绕过前台限制）。
2. **Win11 记事本所有窗口共用一个进程**：检测新窗口必须比 hwnd 而不是 pid。
3. **exe 名比较**：进程名带 `.exe`，`os.path.basename(target)` 要先补后缀再比。
4. **文档类应用防偷焦点**：记事本/Office 已有带标题窗口时，fallback 只翻「无标题」窗口；用户开着文档绝不偷焦点。
5. **type 焦点守卫**：本会话 open_app 置顶过的窗口，type 前核对当前前台 hwnd，不符且非无标题窗口→拒绝（返回 ok=True+引导消息，让小智直接念出来，别用 ok=False 的"执行失败"前缀）。
6. **多 agent 并发坑**：relay 取 `next(iter(AGENTS))` 即第一个在线的 agent。测试时旧 agent 进程没杀会导致指令发给旧代码——换测试对象前必须先停旧进程。
7. **pip 源**：清华源这次查不到 websockets，阿里云源可用（`-i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`）。
8. **部署安全**：deploy 脚本改 config 必须 备份→幂等→容器内 YAML 校验→不过就中止→重启后日志 grep pc_control 报错即自动回滚（主服务要保命）。
9. **SSH 授权粘贴坑**：用户粘贴 `echo "ssh-ed25519 AAAA..."` 时丢了 `ed25519` 后面的空格导致 Permission denied；且服务器登录用户是 ubuntu 不是 root，钥匙写进 `/home/ubuntu/.ssh/authorized_keys` 才有效，连接要用 `ubuntu@`。
10. **docker 网关因部署而异**：本例 172.18.0.1（compose 网络）；换机器/换部署必须先 `docker inspect` 探测，别信 172.17.0.1 的默认值。
11. **容器内 websockets 已存在**（14.2），deploy 脚本里的 pip 安装只是兜底。
12. **服务器实际无软件防火墙**：实测 ufw 是 **inactive**（根本没启用），8001 的唯一关卡就是腾讯云控制台防火墙；公网握手超时（DROP，timeout 而非 refused）基本可断定是控制台规则没加。加固别随手 `ufw enable`——必须先 `allow 22/tcp` 再 enable，否则把自己关在门外。

## 部署实录（本次命令流，可复现）

```bash
# 0) SSH（ubuntu 用户；root 连不上是正常的）
ssh ubuntu@43.142.134.217
# 1) 传文件
scp pc_relay.py plugin_pc_control.py deploy-pc-control.sh ubuntu@43.142.134.217:/tmp/
# 服务器上：mkdir -p ~/pc-control && mv /tmp/{pc_relay,plugin_pc_control,deploy-pc-control}.py ...
# 2) 部署（幂等，可重跑）
cd ~/pc-control && PC_CONTROL_TOKEN=53bc4f5faf6c80f76c297c176df3cbeb bash deploy-pc-control.sh
# 3) 腾讯云控制台放行 TCP 8001（唯一必须用户操作的步骤）
# 4) 本机双击 start-agent.bat → 喊「你好小智，打开记事本」
```

## 边界与安全

- 延迟 1.5-3s（ASR+LLM 决策），只做粗粒度：开应用/口述成稿/翻页/按键
- 小智看不见屏幕；设备旁任何人喊话都能控电脑（不用时关 agent 窗口）
- pyautogui FAILSAFE：鼠标甩到左上角即中止
- 停用：服务器 `sudo systemctl stop pc-relay`；回滚：恢复 `.config.yaml.bak.*` + `sudo docker restart xiaozhi-esp32-server`
