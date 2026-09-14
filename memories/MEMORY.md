防误删sync_guard.sh+P11见skill hermes-data-sync,wsl-hermes-env§9亦然。注销skill(company-deregistration勿改)qingshui_risk_engine.py把「期初」当「期末」诊断,临注销公司必错,用前人工核对期末(C&G列),差>10%废弃。同步夹memories源=~/.hermes/memories/。
§
交付文件默认放Windows桌面/mnt/c/Users/Admin/Desktop(用户名Admin),不放WSL桌面~/,不显示WSL路径。不生成md文件——除非写清打开方式，否则直接不生成(交付用docx/txt)。Clash代理只绑127.0.0.1:7890:Github用curl.exe --proxy,pip前unset代理。Windows hermes用uv装,WSL调.exe需Start-Process。
§
政务/法律条文检索用anysearch CLI batch_search 可直抓权威官文(文号+施行日期)，已实操验证(法释〔2025〕4号等)。pip清华。
§
用户（徐爱军）常处理苏州爱心之家老年公寓（民办非企业）的财务报表格式转换：小企业会计准则→民间非营利组织。要点：实收资本+未分配利润→非限定性净资产（负数），应收款项=应收账款+预付账款+其他应收款，应付款项=应付账款+其他应付款。技能已保存为 chinese-accounting-format-conversion。
§
用户要求提到 GEO 时必须加载 geo-optimization 技能 + 8平台独立指南(百家号/网易号/新浪财经头条/企鹅号/搜狐号/今日头条/知乎/公众号)。偏好中文、直接给能用的方案没说废话。
§
公众号铁律（用户反复强调）：①严禁AI幻觉，不确定政策/数据/法规绝对不写，引用标注官方文号，宁可少说不说错；②配图铁律：禁止复用任何历史图片、禁止建图片库，每次创作直接用AI生成或查找与主题高度相关的新图，每段配图严格对应本段主题；③模板固定：公司介绍(盈信2009-12-11/江敏创办/TSC五级438.11/17年)→核心业务→二维码→CTA三动作+话题标签5-8个勿漏(详见尾部规范条)→作者"苏州盈信企业管理"。
§
用户触发词约定：「朋友圈」→wechat-moments-marketing出文案+3张Unsplash图+拷桌面+企微API推XuAiJun勿问确认。「调用短视频skill」→自动同时调爬虫skill(python-web-scraping-setup)按主题搜信息，输出要超前超脱的上帝视角、提出不同观点并分析得头头是道。
§
文章改写要求:除换措辞还要打乱结构顺序/重组角度与逻辑链,结构层面不雷同;五大事项类可重排/拆分重组/调侧重点。
§
Obsidian=第二知识库/永久记忆。D盘=/mnt/d/obsidian-vault主库,WSL=git引擎(push obsidian-vault)。脚本hermes_only_snapshot.sh+obsidian_sync.sh。cron每日12:28归档、周一12:28复盘。更新后跑obsidian_sync.sh。详obsidian skill。
§
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
§
人工HTML/SVG分镜5风格存备选、用户全不满意——要真AI生图专业质感。最高优先任务=生图能力(coze/image_gen/ComfyUI/文心/通义万相),chudian视觉key脱敏不可用,用户会再给风格链接。参考wechat-comic-cells。
§
模型分工自动切换:子代理跑kimi-k3成稿+主会话deepseek编排,爆款写作默认派子代理不手切。
§
hermes cron CLI(2026.8实测):prompt是位置参数`hermes cron create <schedule> <prompt>`,无--prompt;子命令无log,查执行用`hermes cron runs <id>`;生命周期create→run(手动)→runs→remove。cron前`.lazy-refresh-incomplete`警告是噪音,venv其实健康(核心模块6/6 import通过),验证用import非警告。
§
脱敏铁律(处理任何上传材料自动执行):涉①公司名称②统一社会信用代码③法定代表人姓名/身份证号一律先脱敏再进对话/入库/同步。①公司名除"有限公司"外汉字逐字取拼音首字母大写(示例:甲乙丙丁（苏州）有限公司→JYBD（SZ）有限公司,简称同步);②信用代码18位保留前10位、末8位全X;③法人姓名前两字→TT(杨建国→TT国)。真实主体交付物(如提交税局报告)仅本地留真实版,公开仓库/skill库/同步一律脱敏。