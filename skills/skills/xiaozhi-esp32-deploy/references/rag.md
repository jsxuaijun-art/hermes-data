# 小智 RAG 知识库配置（RAGFlow）

## 架构（必须知道）
- 小智服务端 `xiaozhi-esp32-server` 本身**不带向量库**。
- RAG = 对接外部 **RAGFlow**：RAGFlow 负责文档解析 / 切片 / 向量化 / 检索；服务端插件 `search_from_ragflow` 在对话时让 LLM 判断是否需要查知识库，查到后把片段喂回 LLM 生成回答。
- 插件源码读取配置：`conn.config["plugins"]["search_from_ragflow"]`，字段：`base_url` / `api_key` / `dataset_ids`。
- 插件只调用 `POST {base_url}/api/v1/retrieval`（**base_url 末尾不要带** `/api/v1/retrieval`，插件会自动拼）。

## 关键坑（源码确认，别踩）
- 插件**不是**写了 `plugins` 段就生效！可用工具列表来自 `config["Intent"][selected_intent]["functions"]`。
- 默认 `Intent: nointent` 没有 `functions` 列表 → 插件根本不会被装载，光填 `plugins` 段无效。
- 必须：把 `Intent` 切成 `function_call`（或 `intent_llm`），并在其 `functions:` 里加 `- search_from_ragflow`。
- `function_call` 模式要求 LLM 支持 function calling；本项目用 `deepseek-v4-flash`（OpenAI 接口）支持，OK。
- `handle_exit_intent` / `play_music` 是系统默认自动装载，**不要**在 functions 里重复写。

## 决策：RAGFlow 从哪来（含费用，2026-10-24 核实）
> ⚠️ **免费版 $0/月没有 API Key** → 小智插件靠 API 调用检索，**免费版直接不可用**，至少入门版。

| 方案 | 月费（β 折扣 / 原价，USD） | 容量 | API Key | 建议 |
|---|---|---|---|---|
| 云版·免费 | $0 | 0.1GB / 500 额度 | ❌ 无 | 不可用（无 API） |
| 云版·入门 Starter | ~$29 / $59 | 5GB / 5000 额度 | ✅ | ✅ 盈信首选，文档量小够用 |
| 云版·专业 Pro | ~$129 / $259 | 50GB / 20000 额度 | ✅ | 资料多再升 |
| 自建 | 服务器成本 | 自定义 | ✅ | ⚠️ 需 ≥8–16G 内存，当前 4G 实例跑不动，升配后再上 |

- 计费 β 期全计划限时折扣；当前仅 DeepDoc PDF 解析计费，其余解析暂免费。
- 结论：**注册 ragflow.io 或 ragflow.cn 入门版**即可跑通 RAG。

## 操作步骤（纯电脑）
1. **RAGFlow 侧**：新建知识库 → 上传文档（PDF / Word / Markdown / TXT）→ 点「解析」等状态变「已解析」→ 复制 **API Key** 与 **知识库 ID**。
2. **服务器** `~/xiaozhi-deploy/data/.config.yaml`：
   - `selected_module.Intent: function_call`
   - `Intent.function_call.functions` 增加 `- search_from_ragflow`
   - 末尾新增 `plugins.search_from_ragflow` 段（见下）。
3. 重启：`sudo docker restart xiaozhi-esp32-server`
4. **验证**：问一个只有知识库才有的具体问题；`sudo docker logs -f xiaozhi-esp32-server` 应刷出 `search_from_ragflow` 检索记录。

## 配置片段（直接抄）
```yaml
selected_module:
  # …其他保持不变…
  Intent: function_call

Intent:
  nointent:
    type: nointent
  function_call:
    type: function_call
    functions:
      - search_from_ragflow

plugins:
  search_from_ragflow:
    description: "当用户咨询具体税务政策、税率、申报口径、优惠、案例时，调用本方法从盈信税务知识库检索权威信息后回答"
    base_url: "http://<RAGFLOW地址>:9380"   # 云版用控制台给的地址；自建填 http://服务器IP:9380
    api_key: "ragflow-xxxx"                  # RAGFlow「设置 → API」生成
    dataset_ids: ["你的知识库ID"]            # 知识库详情页的 ID（字符串）
```

## 排查
- 仍按通用知识答（没用到资料）：检查 `dataset_ids` / `api_key` / `base_url` 是否填对、知识库是否已「解析」、`functions` 列表是否真的加了那行、容器已重启。
- 日志报连接 RAGFlow 失败：确认 RAGFlow 服务地址/端口可达、API Key 有效、防火墙放行（自建需放 9380）。
