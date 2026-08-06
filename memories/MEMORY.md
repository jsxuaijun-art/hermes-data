Windows batch files (.bat) with non-ASCII characters (Chinese, box-drawing symbols, Unicode symbols) break on Chinese Windows systems when saved as UTF-8. Both UTF-8 without BOM AND with BOM can fail — BOM bytes get read as literal text (锘緻echo). The only reliable fix is to rewrite with pure ASCII only: English text, `=/-` for separators, `[OK]/[FAIL]/[INFO]` for status indicators. Applies to Hermes同步-拉取.bat and Hermes同步-推送.bat on all 4 machines.
§
WSL distro 名：江敏笔记本=Ubuntu22.04（无短横线）；本机=Ubuntu。Windows 访问 WSL 文件用 \\wsl.localhost\Ubuntu\（公众号素材目录 \\wsl.localhost\Ubuntu\home\administrator\公众号素材\）。用户桌面文件在 /mnt/d/OneDrive/Desktop/（OneDrive重定向），找用户发来的docx直接看那里，别搜/mnt/c全盘（超时）。
§
WSL(China)网页/政务检索: 首选搜狗sogou.com+360so.com(requests+bs4直抓,搜狗跳转链接反爬但数据列表可抓,360支持site:);cn.bing政务错乱、Baidu/DDG/Google不可达。查微信公众号用搜狗微信weixin.sogou.com/weixin?type=2(可抓标题摘要,正文被antispider拦)；视频号是封闭生态不进搜索引擎。详见skill chinese-government-site-retrieval。No proxy. pip清华。
§
用户（徐爱军）常处理苏州爱心之家老年公寓（民办非企业）的财务报表格式转换：小企业会计准则→民间非营利组织。要点：实收资本+未分配利润→非限定性净资产（负数），应收款项=应收账款+预付账款+其他应收款，应付款项=应付账款+其他应付款。技能已保存为 chinese-accounting-format-conversion。
§
用户要求提到 GEO 时必须加载 geo-optimization 技能 + 8平台独立指南(百家号/网易号/新浪财经头条/企鹅号/搜狐号/今日头条/知乎/公众号)。偏好中文、直接给能用的方案没说废话。
§
知识库存储原则：存方法不存结果，存经验不存指令。实战经验(窗口实然口径)>法规>网上，先查各skill实战经验库(敏感标[敏感]先请示)。
§
公众号铁律（用户反复强调）：①严禁AI幻觉，不确定政策/数据/法规绝对不写，引用标注官方文号，宁可少说不说错；②配图铁律：禁止复用任何历史图片、禁止建图片库，每次创作直接用AI生成或查找与主题高度相关的新图，每段配图严格对应本段主题；③模板固定：公司介绍(盈信2009-12-11/江敏创办/TSC五级438.11/17年)→核心业务→二维码→CTA三动作+话题标签5-8个勿漏(详见尾部规范条)→作者"苏州盈信企业管理"。
§
用户触发词约定：「朋友圈」→wechat-moments-marketing出文案+3张Unsplash图+拷桌面+企微API推XuAiJun勿问确认。「调用短视频skill」→自动同时调爬虫skill(python-web-scraping-setup)按主题搜信息，输出要超前超脱的上帝视角、提出不同观点并分析得头头是道。
§
文章改写要求：不仅要换措辞，更要打乱原文结构顺序、重新组织角度和逻辑链条。单纯"换说法"不够，必须做到结构层面不雷同。五大事项类内容可以重新排序、拆分重组、调整侧重点。
§
Obsidian=第二知识库/永久记忆。D盘=/mnt/d/obsidian-vault主库,WSL=git引擎(push obsidian-vault)。脚本hermes_only_snapshot.sh+obsidian_sync.sh。cron每日12:28归档、周一12:28复盘。更新后跑obsidian_sync.sh。详obsidian skill。
§
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
§
素材注入skill只能作「备选项/备选方法之一」(像公众号排版风格库多选一)，不得写成唯一必选、不得绑架工作流，无关主题按原流程走不用它。例：抖音高赞泛粉素材已按此定位注入short-video-copywriting第九节+wechat-publish内容素材库。