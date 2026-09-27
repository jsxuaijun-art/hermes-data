差>10%废弃重算；office机本机改勿碰共享脚本。
§
用户桌面=C:\Users\Admin\Desktop(/mnt/c/Users/Admin/Desktop),交付文件一律放这里、只报这个路径;D:\360MoveData 视为不存在(用户多次纠正),即使文件在 D: 盘 360MoveData 下,也要复制到 C 盘桌面再交付。不放WSL桌面~/,不显示WSL路径。
§
法规核验以fgk政策法规库状态标签为准(全文有效/已修改/全文废止,已修改≠废止如2015-97号);fgk附件xls反爬走省级解读页;二手站标注不可信(shui5 WAF、tfcjtax误标28号);anysearch batch_search可直抓官文。pip清华。
§
用户常处理苏州爱心之家老年公寓(民办非企业)财报格式转换:小企业准则→民间非营利组织。实收资本+未分配利润→非限定性净资产(负数);应收款项=应收+预付+其他应收;应付款项=应付+其他应付。技能=chinese-accounting-format-conversion。
§
公众号铁律（用户反复强调）：①严禁AI幻觉，不确定政策/数据/法规绝对不写，引用标注官方文号，宁可少说不说错；②配图铁律：禁止复用任何历史图片、禁止建图片库，每次创作直接用AI生成或查找与主题高度相关的新图，每段配图严格对应本段主题；③模板固定：公司介绍(盈信2009-12-11/江敏创办/TSC五级438.11/17年)→核心业务→二维码→CTA三动作+话题标签5-8个勿漏(详见尾部规范条)→作者"苏州盈信企业管理"。
§
「朋友圈」→wechat-moments-marketing出文案+3张图+拷桌面；企微API推XuAiJun必须经用户明确确认后手动发送，绝不自动推送
§
文章改写要求:除换措辞还要打乱结构顺序/重组角度与逻辑链,结构层面不雷同;五大事项类可重排/拆分重组/调侧重点。
§
Obsidian=第二知识库/永久记忆。D盘=/mnt/d/obsidian-vault主库,WSL=git引擎。脚本hermes_only_snapshot.sh+obsidian_sync.sh。cron每日12:28归档、周一12:28复盘。详obsidian skill。
§
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
§
AI生图5风格均备选、全不满意要真绘画质感;高优=生图能力(通义万相/文心/ComfyUI/coze),chudian视觉key脱敏不可用。见wechat-comic-cells。
§
模型分工铁律:①一般性工作+爬虫skill搜索→chudian平台deepseek V4 Flash(节约);②公众号写作→KIMI-K3(子代理成稿);③文案创作→doubao;④完成文案创作/公众号写作时必须向用户汇报用的是哪个模型;⑤deepseek V4 Flash干不了的工作→提示建议、由用户拍板用哪个模型(如生图直接用doubao-seedream-5.0-pro-0724)。
§
hermes cron CLI:prompt是位置参数`hermes cron create <schedule> <prompt>`;create/remove触发确认门,超时BLOCKED——用户明确授权后写.sh脚本bash执行可成功,勿直接重试,删建分开;查执行`hermes cron runs <id>`;生命周期create→run→runs→remove。`.lazy-refresh-incomplete`警告是噪音,venv健康,验证用import。
§
yt-dlp+ffmpeg已装,脚本dl下视频/音频,默认存Windows桌面/dl,国内直连,YouTube需Clash(7890只绑Windows宿主)。
§
公众号改写稿出稿前做去AI味=creative/humanizer技能(用户会主动问"上次用哪个工具",答humanizer)。排版风格除01安信伯君外有02刘润红蓝撞色(红#FF2941蓝#0052FF,风险/警示文数字冲击好)已入库可用;wechat-publish风格库表可能只登记01,列选项时直接列两个。
§
企微发送:先配回调+可信IP,按键wechat-moments-marketing;推XuAiJun须用户确认。企微AI机器人(WebSocket)已通:wecom启用,@yingxin_inner调Hermes;wecom_callback由env启用只刷40001不抢答。
§
用户财税类skill(tax-audit-response等)user-owned(vault维护),curator写被拒;书/参考融已有skill→先出方案不自动写;vault的50-Skills软链~/.hermes/skills,改vault即同步勿双份。tax-audit-response触发词「税务稽查/检查/稽查」已注册;与WorkBuddy共建共享源码,改动后写回传说明放桌面。tax-regulation-monitor每月巡查三路交付(vault+桌面+WorkBuddy)。
§
Hermes 本机=上游 git clone 于 /home/dmin/hermes-agent(非混合仓库),venv=.venv-hermes,已升 0.21.4;用户技能 skills/tax-audit-response 为非跟踪保留文件。WSL 连 Windows Clash 走网关 172.23.96.1:7890(非127.0.0.1)。GitHub 大单文件传输(>~60MB)会被节点切断且 git 无法续传:改从 gh-proxy.com 下载源码 zip 支持 range 续传(-C - 循环+zipfile CRC 校验)最稳,勿用 git fetch 硬磨。
§
生图铁律:有生图任务一律走doubao-seedream-5.0-pro-0724(经电信中转aigw.telecomjs.com/v1,OpenAI兼容),严禁用deepseek-v4-flash或降级其他模型,整任务跑完再回默认模型。脚本内嵌于image-gen-cn skill的scripts/目录($HOME/.hermes/skills/creative/image-gen-cn/scripts/image_gen_seedream.py),随skill跨机同步;key在每台机的.env配SEEDREAM_API_KEY(.env不同步需手动配)。视觉验收:auxiliary.vision用chudian的deepseek-v4-flash-vision-exp(复用DEEPSEEK_API_KEY),vision_analyze看图查乱码。见image-gen-cn skill。
§
跨机同步坑:远端唯一真相源,勿盲推/勿force-push;改memories等跨机累积共享文件=合并勿覆盖——本机实时MEMORY.md≠远端多机累积版,cp整文件进同步夹会清仓(commit显示rewrite 99%/巨量diff=信号);恢复=git show旧commit:path取回远端版→awk按行去重合并→双grep校验新旧都在→再推;push前先fetch看与origin/main分叉。.env与config.yaml各机独立勿共享覆盖。
§
为短视频内容做「话题/标题总结」时,勿停留在表面叙事,要'站得更高看得更远'(上帝视角):深度提炼底层主旨。方法论:把一个具体家务/日常现象上抽到-定义本质-再归纳到一个更高维的核心概念(如'托举'→升级为'内耗/家庭能量管理'),金句洞察往往藏在结尾自省句(如'多数家庭更擅长拽下来而非托上去'=内耗是本能的,托举是反本能的)。示例:用户《托举》文案→深层主旨=「家庭兴旺的底层是'不内耗'——能量单向向外输出 vs 内部对消归零(家庭资源配置/人力资本经营)」→标题抓'内耗/能量管理'比抓'托举'更站高。此思想法已写入 short-video 技能「上帝视角·深层主旨提炼」节。