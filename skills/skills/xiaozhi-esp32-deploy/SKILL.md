---
name: xiaozhi-esp32-deploy
description: "Use this skill when deploying, flashing, or provisioning a 小智AI (XiaoZhi) ESP32-S3 voice companion robot (e.g. 立创实战派 LCKFB-SZPI-ESP32-S3-VA) to connect to a self-hosted xiaozhi-esp32-server. Covers firmware selection (v2.5.2_lckfb-lichuang-dev.zip), WebSerial flashing, Wi-Fi provisioning via 192.168.4.1, OTA redirection to a custom WebSocket server (ws://host:8000/xiaozhi/v1/), and common pitfalls such as wrong firmware, the __PUBLIC_IP__ placeholder bug, BOOT-button entry failure, 8000/8003 port confusion, and GET-vs-POST OTA text. Also covers enabling the RAG knowledge base via external RAGFlow (the Intent/plugins config trick)."
agent_created: true
---

# 小智AI ESP32 部署与配网技能

## Overview

End-to-end playbook for turning a 立创实战派 ESP32-S3 board into a 小智AI voice companion that
talks to a self-hosted `xiaozhi-esp32-server` (xinnan-tech Python edition) instead of the official
xiaozhi.me cloud. It encodes the exact firmware, addresses, commands, and the eight pitfalls found
during a real Tencent-Cloud deployment so the next run is fast and error-free.

## When to use

- User wants to build / re-flash / re-configure a 小智AI ESP32 voice robot.
- Board shows "激活设备 XXXXX" (still pointing at official xiaozhi.me) and must be redirected to a self-hosted server.
- Need the correct firmware filename, flashing tool, Wi-Fi provisioning steps, or OTA / WebSocket address.
- Troubleshooting: board won't enter provisioning mode, OTA returns text not JSON, server IP placeholder not replaced.

## Critical facts (memorize these)

- Board: LCKFB-SZPI-ESP32-S3-VA (ESP32-S3, 16MB Flash / 8MB PSRAM).
- Correct firmware: `v2.5.2_lckfb-lichuang-dev.zip` (S3). ❌ NOT `v2.5.2_lckfb-lichuang-c3-dev.zip` (C3 chip).
- Server IP (this deployment): `43.142.134.217` (Tencent Cloud, firewall not security-group).
- `ws://43.142.134.217:8000/xiaozhi/v1/`  ← WebSocket voice (port 8000).
- `http://43.142.134.217:8003/xiaozhi/ota/` ← OTA address to paste in board config (port 8003).
- Ports: 8000 = WebSocket voice; 8003 = HTTP / OTA / vision. Tencent Cloud "防火墙" must allow TCP 8000 + 8003 (source 0.0.0.0/0).
- LLM: base_url `https://llm.chudian.site/v1`, model `deepseek-v4-flash` (API key lives in server config; do not expose).
- Wake word: 「你好小智」. Board answers "我在这里哟" on wake, then listens for the real question.

## Workflow (condensed — full detail in references/sop.md)

1. **Server (one-time, already done):** container `xiaozhi-esp32-server` Up; firewall 8000/8003 open.
   If `.config.yaml` still contains `__PUBLIC_IP__`, run:
   `sed -i 's/__PUBLIC_IP__/43.142.134.217/g' ~/xiaozhi-deploy/data/.config.yaml && sudo docker restart xiaozhi-esp32-server`
2. **Firmware:** download `v2.5.2_lckfb-lichuang-dev.zip` from GitHub 78/xiaozhi-esp32 releases (search "lckfb").
3. **Flash:** Edge/Chrome → https://dev.16302.com/tools/xiaozhiinit (free for official firmware; "绿豆" is vendor credit, unrelated to self-host). Flash mode: hold BOOT → click start/RST → release RST → release BOOT.
4. **Enter provisioning (the hard part):** the 立创 shell's BOOT button is recessed and often un-pressable.
   ✅ Reliable method: turn off home Wi-Fi → board fails to connect 3× → auto-enters provisioning (emits Xiaozhi-XXXX AP, blue LED blinks).
5. **Configure:** PC joins Xiaozhi-XXXX AP → open http://192.168.4.1 → enter 2.4G Wi-Fi SSID/password →
   expand "高级选项" → OTA address = `http://43.142.134.217:8003/xiaozhi/ota/` → save ("配置成功").
6. **Apply:** unplug USB → wait 3s → replug.
7. **Verify:** screen no longer shows "激活设备 166840 / xiaozhi.me"; `sudo docker logs -f xiaozhi-esp32-server` shows the device connect; say 「你好小智」→ "我在这里哟" → ask a question → full ASR→LLM→TTS answer.

## Pitfalls (summary; table in references/sop.md)

- Wrong firmware (c3 vs s3) → board won't work.
- Believing online flashing is paid → it's free for official firmware.
- BOOT button can't be pressed → use the Wi-Fi-off 3-fail method.
- `__PUBLIC_IP__` placeholder not replaced → OTA points board at an invalid address (sed fix above).
- Confusing 8000 vs 8003 → OTA must use 8003.
- Mistaking the OTA GET text ("OTA接口运行正常…") for a broken endpoint → board uses POST and gets proper JSON `{"websocket":{"url":"ws://…:8000/xiaozhi/v1/"}}`.
- Thinking you must enter an activation code on xiaozhi.me → self-hosted connects directly, no code.
- Looking for "安全组" on Tencent Cloud → it's called "防火墙".

## Resources

- `references/sop.md` — full step-by-step SOP, architecture, 8-pitfall table, and a "completely correct next-time checklist".
- `references/rag.md` — enabling the RAG knowledge base via external RAGFlow (architecture, the Intent/plugins config trick, cloud-vs-self-host with 2026 pricing, full YAML snippet, troubleshooting).
- `references/continuation.md` — cross-machine "hand-off" checklist: what is done, the two open tasks (RAG enablement + Obsidian branch merge), environment facts, and the sandbox-network caveat. Use this when resuming on another computer.
- `scripts/deploy-aliyun.sh` — one-click Tencent-Cloud server deployment script (Docker + config + model download). Edit the IP placeholder handling before use on a fresh host.
