# 小智AI 部署 — 跨机接力 / 待办续做清单

> 本文件供「其他电脑 / 另一轮 AI」接手继续执行。状态截至 2026-10-24。
> 对应技能：`xiaozhi-esp32-deploy`；对应 Obsidian 笔记：`30-Knowledge/小智AI部署_待办续做_跨机接力.md`

## 0. 一句话进度
固件烧录、配网（OTA 重定向到自建服务器）、全链路语音对话（唤醒→ASR→LLM→TTS）、人设均已跑通验证；Obsidian 笔记已合并进 main 并推送（2026-10-24）。当前**唯一未闭环的是 RAG 知识库**：`apply-rag-config.sh` 配置脚本已就绪并经本地实测（幂等+YAML 校验+守卫），只差 **RAGFlow 账号凭据** + **服务器 SSH 授权**。

## 1. 已完成（无需重做）
- [x] 服务端部署：腾讯云轻量 4核4G3M / Ubuntu24.04，容器 `xiaozhi-esp32-server` Up，防火墙放行 8000+8003。
- [x] 固件：`v2.5.2_lckfb-lichuang-dev.zip` 烧录成功（立创实战派 S3 版）。
- [x] 配网：OTA 地址 `http://43.142.134.217:8003/xiaozhi/ota/` 重定向到自建 WS `ws://43.142.134.217:8000/xiaozhi/v1/`（POST 实测返回正确 JSON）。
- [x] 全链路验证：喊「你好小智」→「我在这里哟」→ 问税务问题能准确口吻回答、声音流畅。
- [x] 人设：`.config.yaml` 的 prompt = 「盈信税务陪伴助手」。
- [x] 技能 `xiaozhi-esp32-deploy` 已建并双落位：`~/.workbuddy/skills/` + canonical 技能库（manifest 307）。
- [x] RAG 技术调研完成：确认小智 RAG = 对接外部 RAGFlow，`search_from_ragflow` 插件必须写进 `Intent.function_call.functions` 才装载（仅配 plugins 段无效，源码已确认）。
- [x] **服务器健康检查（2026-10-24）**：公网 OTA GET/POST + 8000 端口探测均正常，`__PUBLIC_IP__` 已修。
- [x] **Obsidian 分支合并（2026-10-24）**：`feature/xiaozhi-notes`（孤儿分支，3 篇笔记）已 `--allow-unrelated-histories` 合入 main 并推送（`ff360a4..848a2a5`）。做法：git worktree 干净目录合并，未碰本地脏工作区。
- [x] **`apply-rag-config.sh` 配置脚本就绪**：备份→三处幂等改动→容器内 YAML 校验→restart→摘要；实测三次运行字节级一致；守卫生效（base_url 带 `/api/v1/retrieval` 拒绝、有 `__PUBLIC_IP__` 残留拒绝、YAML 不过不重启）。

## 2. 待办1（主任务）：开通 RAGFlow 云版 + 配置服务器 RAG
### 2.0 当前状态（2026-10-24 晚）
- 阻塞项一：**RAGFlow 云版账号凭据**（API Key + 知识库 ID + 控制台地址）——需用户本人注册付费（入门版 ~$29/月）。
- 阻塞项二：**服务器 SSH 授权**——本机 `id_ed25519`（注释 jsxuaijun-art）未被服务器授权。解法：用户在服务器上执行
  `echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC1V0aGGxa+CDGM6Zu6ppBoZo/FA8d2WYWtfbuCHK99B jsxuaijun-art" >> ~/.ssh/authorized_keys`
- 两样到位后：上传 `apply-rag-config.sh` 到服务器，`export` 三个变量后 `bash apply-rag-config.sh` 即可（脚本自带备份/YAML校验/重启/摘要）。

### 2.1 费用（已查，2026-10-24）
- 免费版 $0/月：**无 API Key**，插件无法调用 → 不可用，跳过。
- 入门版（Starter）：β 折扣期约 **$29/月**（原价 $59）；5GB 存储、5000 额度/月、有 API Key → **盈信够用，首选**。
- 专业版（Pro）：约 $129/月（原价 $259）；50GB、20000 额度 → 资料多再升。
- 企业版：定制。
- 计费 β 期全计划限时折扣；除 DeepDoc PDF 解析外其余解析暂免费。
- 结论：注册 **ragflow.io 或 ragflow.cn 入门版**即可。

### 2.2 执行步骤（凭据到位后）
1. RAGFlow 云版：新建知识库（如「盈信税务知识库」）→ 上传税务文档（PDF / Word / MD / TXT）→「解析」等「已解析」→ 复制 **API Key**（设置 → API）与**知识库 ID**（详情页）。
   建议先传 5-10 份高频品类（小规模免征额/税率速查、代开 vs 个体户税负对比、各税种税率表），宁精勿滥。
2. 服务器 `~/xiaozhi-deploy/data/.config.yaml` 由 `apply-rag-config.sh` 自动改三处：
   - `selected_module.Intent: function_call`
   - `Intent.function_call.functions` 加 `- search_from_ragflow`
   - 末尾 `plugins.search_from_ragflow` 段（base_url / api_key / dataset_ids）
3. 脚本自动 `sudo docker restart xiaozhi-esp32-server`。
4. **验证**：问一个只有知识库才有的具体问题；`sudo docker logs -f xiaozhi-esp32-server` 应刷出 `search_from_ragflow` 检索记录。

### 2.3 关键坑（别踩）
- 免费版没 API Key，别浪费时间。
- 只改 `plugins` 段不生效，必须加 `functions` 列表那行。
- `base_url` 末尾**不要**带 `/api/v1/retrieval`（脚本有守卫会拒绝）。
- 自建 RAGFlow 需 ≥8–16G 内存，当前实例 4G 跑不动，先云版。
- 云版 RAGFlow 是服务器主动外访，不用再动腾讯云防火墙。

## 3. 待办2：Obsidian 分支合并进 main —— 【已完成 2026-10-24】
- [x] `feature/xiaozhi-notes`（**孤儿分支**，与 main 无共同祖先）已合入 main 并推送：`ff360a4..848a2a5`，3 篇笔记 +187 行零冲突。
- 合并方式备忘（本机 `/d/obsidian-vault` 工作区脏，勿直接在上面 merge）：
  ```bash
  cd /d/obsidian-vault
  git worktree add --detach <临时目录> origin/main
  cd <临时目录>
  git merge origin/feature/xiaozhi-notes --allow-unrelated-histories --no-edit
  git push origin HEAD:main
  git worktree remove <临时目录>   # 在 /d/obsidian-vault 里执行
  ```
- 遗留：本机本地 main 仍是 ahead 1 / behind 8 分叉态 + 有未提交 `_AI-Private` 改动，按用户常规同步流程处理，不特意动。

## 4. 环境速查（下一台电脑必看）
- 服务器：腾讯云轻量 4核4G3M / Ubuntu24.04 / IP `43.142.134.217`（防火墙放行 8000+8003）。
- 部署目录：`~/xiaozhi-deploy`；配置：`~/xiaozhi-deploy/data/.config.yaml`；容器：`xiaozhi-esp32-server`。
- LLM：`https://llm.chudian.site/v1`，`deepseek-v4-flash`（key 在配置里，勿泄露）。
- WS 地址：`ws://43.142.134.217:8000/xiaozhi/v1/`；OTA：`http://43.142.134.217:8003/xiaozhi/ota/`。
- 板子：立创实战派 LCKFB-SZPI-ESP32-S3-VA（ESP32-S3）；唤醒词「你好小智」。

## 5. 沙箱网络坑（重要）
- WorkBuddy 沙箱到 GitHub 的**大批量传输会被掐断**（实测 fetch 下到 73% 就 early EOF，或挂死无连接）。
- ✅ 可做：小文本提交（几 KB）推送没问题（feature 分支 3.59 KiB 成功过）。
- ❌ 勿做：在沙箱里 `git push` 整个 vault（2088 文件 / ~10MB）或全量 clone。
- 正确做法：大同步放到用户正常网络的电脑做；沙箱只推小笔记更新。

## 6. 已验证命令速查
```bash
# 占位符修复（若 .config.yaml 仍有 __PUBLIC_IP__）
sed -i 's/__PUBLIC_IP__/43.142.134.217/g' ~/xiaozhi-deploy/data/.config.yaml && sudo docker restart xiaozhi-esp32-server
# 看连接
sudo docker logs -f xiaozhi-esp32-server
# 看配置是否生效（应显示真实 IP，无 __PUBLIC_IP__）
grep -n "websocket\|vision_explain" ~/xiaozhi-deploy/data/.config.yaml
```
