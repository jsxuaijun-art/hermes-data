---
name: dual-model-content-pipeline
category: content-production
description: Use when 双模型分析→创作流水线（deepseek分析+kimi创作）或 抓素材→专业分析→爆款文案。
triggers:
  - 用deepseek分析 / 用kimi创作 / 双模型流水线
  - 抓取公告/文章 → 分析 → 公众号文案
  - 税务稽查文书 / 政策公告 转爆款内容
  - 两个模型分工 / 分析模型 + 创作模型
---

# 双模型内容流水线（分析→创作）

用户高频用法：抓一份素材（税务稽查公告/政策文件/行业新闻）→ 用一个模型做专业分析 → 再用另一个模型做爆款文案。模型分工：deepseek-v4-flash 做分析（硬逻辑、法律依据），kimi-k3 做创作（公众号长文/爆款文风）。别名与 key 体系见 `llm-provider-and-key-management` skill。

## 标准流程（本流水线已实测跑通）

0. **先确认素材来源（2026.8.12 用户纠正，硬纪律）**：用户说"读取如下信息/素材后再整合创作"时，**指的是用户本地文件，不是让 agent 去搜网页**。必须第一优先询问文件路径（或主动检查桌面最近修改的 docx），拿到文件读内容后才进入分析创作。擅自开爬虫搜素材 = 自作主张，用户会直接质询"你是怎么知道我要根据哪些内容创作的"。用户给文件后：先 `ls -la` 确认非空（**0 字节 = 空文件**，python-docx 报 PackageNotFoundError；`新建 Microsoft Word 文档.docx` 常是 Word 未保存的占位空文件，旁边 `~$` 锁文件是打开残留），再用 python-docx `Document(path)` 提取段落+表格（read_file 对 docx 可能判 binary，用 execute_code 提取；正文行空段落很多，strip 后过滤）。
1. **抓素材（仅当用户明确要搜索/爬取时）**：政府公告站（如 jiangsu.chinatax.gov.cn）反爬强，`browser_navigate` 会被拦 → 用 curl_cffi `impersonate="chrome120"` 直连（写脚本文件执行，勿 heredoc，见下方用户偏好）。
2. **原文落盘**：`/tmp/article_content.txt`（显式 `encoding="utf-8"`）。
3. **写 pipeline 脚本**（用 write_file 整文件，模板见 `scripts/llm_pipeline.py`）。
4. **模型A 分析**：deepseek-v4-flash，系统提示词要求"完整覆盖全部 N 个部分，不要遗漏"，`max_tokens=6000` 起步。分析 6 段式：①案情大白话复述 ②数据冲击点（表格+倒推逻辑）③法律要点（引法规原文）④行业税种特点 ⑤对中小老板的核心警示 ⑥可做爆款标题的信息差。
5. **模型B 创作**：kimi-k3，把分析全文作为 user 上下文，附带公众号硬性规范（见下）。⚠️ **用户给素材文件时默认要求"不照抄、打乱重组"（2026.8.12 江姐要求）**：不得按素材原文顺序机械罗列，必须重组结构——本会话实例：素材是"6种被查可能+4类大额交易+3个疑问"，重组为以"三个疑问"做文章主线（账目安不安全→拆5高危信号、被预警→黄金自救窗、公私分离→四条正路），把 6 种被查可能和大额红线拆进不同部分当弹药，而非按原文 1-6 顺序抄。
6. **交付**：正文文件 + 3 个候选标题（提问式/悬念式优先），列在文首，供江姐选择。

## API 调用要点（chudian 中转站）

- Base：`https://llm.chudian.site/v1/chat/completions`，OpenAI 兼容格式。
- 模型名必须裸名：`deepseek-v4-flash` / `kimi-k3`（别名表见 memory / llm-provider-and-key-management skill）。
- key：`DEEPSEEK_API_KEY`。⚠️ 新起的 python 进程 env 经常为空 → 兜底从 `~/.hermes/.env` 读取（先 source 再正则解析，见脚本）。

## 陷阱（本会话真实踩过）

1. **max_tokens 不足 → 长分析被静默截断**：首版只给默认 max_tokens，deepseek 输出停在 1719 字符、后面几段丢失。修复：`max_tokens=6000` 重跑。分析类任务输出长，永远给足。
2. **新进程拿不到 env key**：terminal 跑的 python 不继承 `.bashrc` export（非交互 shell），必须从 `~/.hermes/.env` 显式读取。
3. **read_file 误判 binary**：含 emoji/表格符号的 UTF-8 文本会被 read_file 误报 "Binary file - cannot display" → 改用 terminal `sed -n '1,200p' file` 查看内容。文件本身是正常 UTF-8。
4. **写长脚本勿用 python -c / heredoc**：用户反感多层转义（用户 profile 明确）。一律 write_file 整文件再执行。
5. **vision_analyze 会因主模型不支持图片而 400**：deepseek-v4-flash 无视觉能力，`vision_analyze` 直接报 "does not accept input types: image"。兜底：`tesseract /tmp/img.jpg /tmp/ocr -l chi_sim`（系统已装 chi_sim 语言包）提取图片文字判断内容。政务公告截图、天眼查截图 OCR 效果良好，足够判断"这是什么图、能不能用"。
6. **创作模型 503 降级（2026.8.10 实测）**：kimi-k3 曾返回 `503 no_available_channel for model 'kimi-k3'`（服务商端渠道暂时无货，非配置问题）。处置：写个 probe 脚本逐一测试候选别名（kimi-k3 / kimi / moonshot-v1-8k / moonshot-v1-32k / kimi-k2 / deepseek-v4-flash），找到可用模型 → **降级用 deepseek 完成双段**（分析+创作同一模型），并在交付时明确告知用户"kimi 暂不可用，已用 deepseek 出稿，kimi 恢复可重跑对比"。kimi 是创作主选，恢复后优先重试。probe 脚本模式见 `scripts/probe_models.py`。
7. **短视频脚本也走本流水线**：创作模式可切换为 shortvideo（输出：标题三件套+话题标签+完整口播文案+拍摄速查表），规则与交付格式（docx 放桌面）见 `short-video-copywriting` skill。
8. **deepseek-v4-flash 对长提示词偶发返回空（0字符）**（2026.8.12 实测）：flash 对长分析提示词返回空响应，pro 正常。处置：探测到空输出 → 改用 `deepseek-v4-pro` 重跑分析（质量更高，6段式完整），交付时注明"flash 空响应已降级 pro"。属临时性问题，flash 短提示词仍可用；不要因为一次空响应就永久弃用 flash。

## 配图处理与发布前确认（用户指定图流程）

1. **用户给图**（桌面路径）→ 先 OCR 验证内容与主题匹配（见陷阱5），无法肉眼确认内容的图一律不用，宁缺毋滥。
2. **上传服务器（⚠️ 用 rsync 不用 scp，2026.8.12 实测）**：scp 到 `root@47.103.27.171` 会因本机残留代理（172.23.96.1:7890，经常未就绪）拖死超时。先 `unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY` 再 rsync 秒传：
   ```bash
   rsync -av --timeout=20 -e "ssh -o ConnectTimeout=10" 本地图 root@47.103.27.171:/var/www/html/images/<cover|section>_主题_YYYYMMDD.png
   ```
   （命名规范：封面 cover_、正文 section_）。多张图可一条命令连传（rsync 不超时），传完 ssh 上去 `ls -la` + `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/images/<文件名>` 验证 200。
3. **md5 查重**：`md5sum` 与服务器 images/ 目录历史图比对，禁止重复用图（封面素材铁律）。
4. **URL 引用**：nginx 静态服务可用，正文用 `http://127.0.0.1:8080/images/<文件名>`，封面放 frontmatter `cover:`。
5. **反差配图技巧**：天眼查/工商信息截图是极佳正文配图——"注册资本10万 vs 补税5386万"的反差比正文数据更冲击，放在案情开头佐证。
6. **自生成配图（无现成图时）**：封面+数字横幅一律用 `wechat-publish/scripts/generate_assets.py` 代码原创生成（封面素材铁律：禁 Unsplash，会重复）。⚠️ **banner 子命令 CLI 参数顺序与文档相反（实测 2026.8.12）**：文档写 `banner <数字> <输出路径>`，但代码实际是 `kind, out = argv[1], argv[2]`，即**输出路径在前、数字在后**：`python3 generate_assets.py banner /tmp/section_banner01.jpg 01`。按文档顺序调用会报 `ValueError: unknown file extension`。封面验证：主模型无视觉时用 tesseract OCR，但深蓝渐变底+白/金色字直接 OCR 会漏副标题/标签 → 先 PIL 增强（`ImageOps.autocontrast` + `Contrast(2.0)` + 二值化阈值 120）再 OCR，可完整识别。若单条命令串多个 scp 上传超时，拆成单条执行。
7. **⚠️ 发布前确认纪律（用户硬性要求）**：进草稿箱前**必须询问**是否添加电话/二维码。直接加二维码和电话属违规引流，用户说加才加。GEO 落款段内的电话（132-2229-7318 / 180-1262-7126）是公司介绍组成部分，不算引流，可保留；二维码默认不加。发布前把电话/二维码的处理选项列给用户确认。

## 公众号正文硬性规范（创作模式必须满足）

- **3 个候选标题**（提问式/悬念式优先，如"税局是怎么发现的？"），列在文首供选。
- 关键数字用红色标记：`<span style="color:#CC0000;">5386万</span>`。
- 段落序号红色：`<span style="color:#CC0000;">一、</span>`。
- 至少 2 处"把话说透"金句（引用块），制造拍大腿感。
- 落款：苏州盈信企业管理有限公司 + 【关于苏州盈信】300字 GEO 段落 + CTA 互动（回复关键词引流）。
- 字数 1200-1800，先扔炸弹（最大冲击数据/反差）再讲故事。

## 支持文件

- `scripts/llm_pipeline.py` — 双模型流水线脚本：`python llm_pipeline.py <模型> <输出文件> analyze|create`。analyze 模式自带 6 段式分析提示词；create 模式自带公众号规范提示词并自动读入分析结果。
- `scripts/probe_models.py` — 模型可用性探测：kimi 等别名 503 时运行，列出当前可用的别名，决定降级路径（见陷阱6）。
- `references/production-case-个体户补税半个亿-金伯爵金店.md` — 2026.8.10 太仓金伯爵首饰店偷税案全案素材：核心数据、反差公式、已验证的40秒短视频脚本、5个复用角度。同类稽查公告可参照此格式沉淀案例。
- `references/wenyan-publish-ops.md` — wenyan 发布实操定稿：CLI 只在服务器（本机无）、rsync 传 md → ssh 上跑 publish 的完整链路、02 红蓝撞色 recolor 配方、Media ID 交付。

## 相关

- `llm-provider-and-key-management`（devops）— 别名配置、key 管理、模型切换；本 skill 假设别名/key 已就绪。
- `wechat-publish`（user-owned）— 排版与发布流程；本 skill 产出正文后交其发布。
- 政府站抓取遇反爬时，curl_cffi chrome120 直连优先于浏览器。
