# 小智AI ESP32 部署与配网 SOP（实战修订版）

> 适用板型：立创实战派 ESP32-S3（LCKFB-SZPI-ESP32-S3-VA）
> 服务端：xinnan-tech/xiaozhi-esp32-server（Python 版），部署于腾讯云
> 整理自 2026-10-24 一次完整跑通的实际操作。

## 0. 一句话结论
板子固件烧 `v2.5.2_lckfb-lichuang-dev.zip`；配网页高级选项填 OTA 地址 `http://43.142.134.217:8003/xiaozhi/ota/`；
服务器容器保持 Up、防火墙放行 8000/8003；断电重启板子即可连上自建服务器。

## 1. 目标与整体架构
- 板子（本地）：唤醒词检测 + 麦克风采集 + 扬声器播报，不跑大模型。
- 服务端（腾讯云）：ASR 语音识别 + LLM 大模型 + TTS 语音合成。
- 通信：板子经 WebSocket 连服务端；经 HTTP/OTA 接口获取服务器地址。

关键地址：
```
服务器公网 IP : 43.142.134.217
WebSocket 语音 : ws://43.142.134.217:8000/xiaozhi/v1/
HTTP/OTA/视觉  : http://43.142.134.217:8003/
OTA 地址(填板子): http://43.142.134.217:8003/xiaozhi/ota/
LLM 配置       : base_url=https://llm.chudian.site/v1  model=deepseek-v4-flash  (API Key 见服务器配置，勿外传)
```

## 2. 物料与硬件
- 立创实战派 ESP32-S3 开发板（LCKFB-SZPI-ESP32-S3-VA，16MB Flash / 8MB PSRAM）。
- USB-C 数据线（能传数据，非仅充电）。
- 2.4GHz Wi-Fi（板子不支持 5GHz，确认路由器开了 2.4G）。
- 电脑（Windows，Edge/Chrome 做 WebSerial 烧录与配网）。

## 3. 固件准备【坑1：固件选错】
GitHub Releases：78/xiaozhi-esp32，版本 v2.5.2。Assets 有 192 个文件，必须认准：
```
✅ 正确: v2.5.2_lckfb-lichuang-dev.zip   （ESP32-S3 版，本板型用这个）
❌ 错误: v2.5.2_lckfb-lichuang-c3-dev.zip （ESP32-C3 芯片版，不通用！）
```
- 旧版 xiaozhi.me 文档写的 `lichuang-dev.zip` 是老命名；v2.5.2 实际前缀加了 `lckfb-`，下载时展开 Assets 用 Ctrl+F 搜 "lckfb" 定位。
- 板型识别：包装/丝印写 LCKFB-SZPI-ESP32-S3-VA → 选带 `lckfb-lichuang-dev` 的 S3 固件。

## 4. 服务端部署（腾讯云）
镜像：`ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest`，一键脚本见 `scripts/deploy-aliyun.sh`。

### 4.1 部署后必须确认
1. 容器在运行：`sudo docker ps --filter name=xiaozhi-esp32-server` → STATUS 应为 Up。
2. 防火墙放行：腾讯云控制台「防火墙」（不是安全组）放行 TCP 8000 和 8003，来源 0.0.0.0/0。

### 4.2 配置核心项（~/xiaozhi-deploy/data/.config.yaml）
```
server:
  port: 8000            # WebSocket 语音
  http_port: 8003       # HTTP / OTA / 视觉
  websocket: ws://43.142.134.217:8000/xiaozhi/v1/
  vision_explain: http://43.142.134.217:8003/mcp/vision/explain
```
⚠️ 见坑4：配置里绝不能残留 `__PUBLIC_IP__` 占位符，否则板子被引导到无效地址。

### 4.3 改配置后重启
```
sed -i 's/__PUBLIC_IP__/43.142.134.217/g' ~/xiaozhi-deploy/data/.config.yaml
sudo docker restart xiaozhi-esp32-server
```

## 5. 板子烧录【坑2：误以为在线烧录收费】
工具：鹿戴马在线烧录 https://dev.16302.com/tools/xiaozhiinit（WebSerial，Edge/Chrome，需 USB 授权）。
- 烧官方固件本身免费；平台充值「绿豆」是鹿戴马自家增值服务（云编译/第三方固件），与自建服务器无关，可忽略。
- 烧录模式：板子按住 BOOT → 点网页开始/RST → 松 RST → 松 BOOT；成功提示「所选固件已成功烧录到设备中」。

## 6. 板子配网【最核心，坑3/4/5 都在这一步】
### 6.1 进配网模式（坑3：按 BOOT 进不去）
现象：立创实战派 S3 外壳内 BOOT 按钮凹陷，手指按不到/按了没反应；长按 BOOT 上电法在本案例无效。
✅ 推荐做法（绕过按钮，100% 有效）：
1. 让板子处于「已烧录但还没配网/或想重配」状态。
2. 关掉家里的 Wi-Fi（或把板子带到无熟悉 Wi-Fi 处），板子连不上 → 失败 3 次 → 自动进入配网。
3. 此时板子发 Xiaozhi-XXXX 热点，蓝灯闪。
备选：拔 USB → 按住 BOOT → 插 USB 上电 → 保持 3-5 秒松开（按钮可按到时）。

### 6.2 电脑配网（纯电脑操作）
1. 电脑连上板子的 Xiaozhi-XXXX 热点（连热点时电脑会断网，配完切回原 Wi-Fi）。
2. 浏览器打开 http://192.168.4.1 。
3. 填 2.4G Wi-Fi 的 SSID + 密码（务必 2.4G）。
4. 展开「高级选项」，OTA 地址 填：`http://43.142.134.217:8003/xiaozhi/ota/` （端口 8003，不是 8000）。
5. 点保存/提交，页面显示「配置成功」。
6. 拔 USB 断电 → 等 3 秒 → 重插上电，让配置生效。

说明：OTA 地址是板子向服务器「询问自己该连哪个 WebSocket」的接口。板子发 POST 过去，服务端返回 JSON 里的 `websocket.url`（即 `ws://43.142.134.217:8000/xiaozhi/v1/`），固件据此连自建服务器。

坑5澄清：用浏览器直接 GET 这个 OTA 地址会看到一句中文「OTA接口运行正常…」——那只是给人看的健康检查文本，板子用的是 POST 拿 JSON，两码事，别被误导。实测 POST（带 device-id / client-id 头）返回：
```
{"server_time":{...},"firmware":{"version":"2.5.2","url":""},"websocket":{"url":"ws://43.142.134.217:8000/xiaozhi/v1/","token":""}}
```
固件 v2.5.2 用 cJSON 严格解析 `websocket` 对象，能正确拿到地址。

## 7. 验证与对话测试
1. 板子重启后看屏幕：✅ 不再显示「激活设备 166840 / xiaozhi.me」，不再催输验证码 → 成功。
2. 服务器看连接（铁证）：`sudo docker logs -f xiaozhi-esp32-server`，板子一连会刷设备上线/WebSocket 连接记录。
3. 唤醒测试：说「你好小智」，板子应答「我在这里哟」→ 唤醒词、联网、TTS 均正常。
4. 真实对话：唤醒后接着问「你好小智，你是谁？」或「讲讲小规模纳税人增值税」。能 ASR→LLM→TTS 正常问答，全链路成功。
注意：不需要在 xiaozhi.me 官网控制台输激活码——那是官方流程；自建服务器（xinnan-tech 版）连上即用。

## 8. 踩坑与困难速查表
| 编号 | 坑 / 困难 | 现象 | 正确做法 / 修复 |
|------|-----------|------|----------------|
| 坑1 | 固件选错 | 下成 c3 版或老命名 lichuang-dev.zip | 认准 v2.5.2_lckfb-lichuang-dev.zip（S3 版） |
| 坑2 | 以为在线烧录要付费 | 担心必须充值才能烧 | 烧官方固件免费；绿豆是鹿戴马增值服务，与自建无关 |
| 坑3 | 按 BOOT 进不了配网 | 立创壳内按钮凹陷按不到/长按无效 | 关 Wi-Fi→板子连失败3次→自动进配网（绕过按钮） |
| 坑4 | 服务器 IP 占位符未替换 | OTA 返回 ws://__PUBLIC_IP__:8000/... 无效 | sed 替换 __PUBLIC_IP__ 为真实IP + docker restart；脚本已改多源探测+校验 |
| 坑5 | 误以为 OTA 接口坏了 | 浏览器 GET 看到中文文本，以为不是 JSON | 板子用 POST 拿 JSON（含 websocket.url）；GET 文本只是健康检查 |
| 坑6 | 搞混 8000 与 8003 | 把 OTA 填成 8000 端口 | 8000=WebSocket语音；8003=HTTP/OTA/视觉，OTA 填 8003 |
| 坑7 | 误以为要控制台加设备 | 板子播「激活设备 166840」慌了 | 那是官方流程；自建服务器连上即用，无需激活码 |
| 坑8 | 腾讯云「安全组」找不到 | 在错误入口找端口放行 | 腾讯云叫「防火墙」，放行 8000/8003 TCP |

## 9. 下次再操作的「完全正确流程」Checklist
1. 【服务端，一次性】确认容器 Up + 防火墙 8000/8003 放行；若改过 .config.yaml 先 sed 替换占位符再 docker restart。
2. 【固件】GitHub 78/xiaozhi-esp32 v2.5.2，下 v2.5.2_lckfb-lichuang-dev.zip。
3. 【烧录】Edge 开 dev.16302.com/tools/xiaozhiinit，选该固件烧录（免费）。
4. 【进配网】关 Wi-Fi → 板子连失败3次 → 自动进配网（发 Xiaozhi-XXXX 热点）。
5. 【配网】电脑连热点 → 192.168.4.1 → 填 2.4G Wi-Fi → 高级选项 OTA 填 http://43.142.134.217:8003/xiaozhi/ota/ → 配置成功。
6. 【生效】拔 USB 断电 3 秒 → 重插上电。
7. 【验证】屏幕不再「激活设备」；服务器 docker logs -f 刷连接；喊「你好小智」→「我在这里哟」→ 问一句确认 LLM 问答正常。

## 10. 兜底与 FAQ
- 板子仍播「激活设备 166840」：确认 Wi-Fi 已连上；否则重进配网（关 Wi-Fi 法）重新填 OTA 再重启。
- OTA 法始终不生效：在配网页找「WebSocket 地址」输入框直接填 `ws://43.142.134.217:8000/xiaozhi/v1/`（比 OTA 更直接）。
- 服务器 docker logs 报错（连不上模型/LLM）：检查 LLM 配置（base_url / model / api_key）及 llm.chudian.site 可达性，属服务端大模型层问题，单独排查。
- 音色/角色：TTS 为 EdgeTTS zh-CN-XiaoxiaoNeural；角色 prompt 已设「盈信税务陪伴助手」，可在 .config.yaml 的 prompt 段修改。
