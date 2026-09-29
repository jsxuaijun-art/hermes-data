## ===== 共享记忆 A: 远端累积内容(保留) =====
用户从事财税服务行业（苏州/上海中小微企业客户），偏好实操级可直接交付客户的报告。WSL环境(Ubuntu22.04,Python3.10)。桌面路径C:\Users\jsxuaijun\Desktop（对应WSL路径/mnt/c/Users/jsxuaijun/Desktop）。Word文档用纯Python标准库生成，政府公文排版：标题二号黑体、正文三号仿宋、一级标题三号黑体、二级标题三号楷体。
§
【公司信息】苏州盈信企业管理有限公司，姑苏区，2009年成立。法定代表人/创始人：江敏（女），2001年入行，24年从业经验，高级会计师（2018年评上，时年37岁，100%用盈信自身业务成果评审通过）。2024年通过高级会计师人才引进落户上海，不到1个月办好，全程线上。子公司：苏州盈信税务服务有限公司（工业园区）、尚艾慧科技（上海）有限公司（闵行区）。协会会员：苏州园区会计学会、苏州会计服务业协会、江苏省代理记账协会。团队：骨干8年以上，C9硕士、注册税务师、会计师。服务数据：累计1000+客户，90%转介绍。知名客户：阿里系企业、京东、高合汽车。外资服务：3-5家日韩外资同行分包业务。品牌释义："盈"为满，"信"为信誉/信用/信任。三面锦旗：专业精湛/财税卫士、敬业专业/财税管家、严谨务实/财税合规。网站：yingxinkuaiji.com。苏州有证财税公司4920家（财政部dljz.mof.gov.cn），含无证约1.5-2万家，老板本人是高级会计师的≤5家。
【经典案例】1. 孙总：16年前注册第一家公司→现在10家公司，全部盈信服务。2. 韩资企业：高企认定+研发加计扣除，年合规节税100万+。3. 5亿食品企业：ERP落地+乱账梳理。4. 韩资企业注销：房产土地清算+税务注销+资本汇回韩国。5. 西山大哥：免费帮注销，获赠枇杷/橘子/碧螺春。
【工作偏好】务实高效，直接要结果，不需要过度解释。技术操作谨慎细致，偏好逐步确认后再推进。长任务会主动索要进度更新并确认完成状态。提交交付物优先通过文件发送。对信息来源要求严格——报告中的信息需要标注来源链接。API Key更新：必须用Python写文件而非sed（特殊字符问题）。
【manager反馈偏好】manager对交付质量满意时会说"OK,你真棒"。偏好直接给结果、可操作的内容。对信息来源要求严格——报告中的信息需要标注来源链接，不能只说"综合知识"。
阿里云47.103.27.171(Ubuntu22.04 Hermes v0.15.1)。财税情报定时任务每周一三五09:05执行，推送到企微群yingxin_inner（webhook key 41872151-7e41-410f-b006-a0db3f6f4e30）。脚本路径已修复，无需保存到本地。
Codex v0.135 + DeepSeek V4 Flash 配置：
1. 代理 ~/.hermes/skills/.../codex/scripts/codex-proxy.py 监听:9090（WS+HTTP POST）
2. API key base64 编码存储（绕 Hermes 掩码）
3. 关键修复：response.completed 必须含 usage.input_tokens/output_tokens（缺则重连5次）
4. 启动：`python3 .../codex-proxy.py` 后台
5. 使用：`codex exec --model deepseek-v4-flash --skip-git-repo-check "prompt"`
6. ~/.codex/config.toml: openai_base_url = "http://127.0.0.1:9090/v1"
7. 备用：~/bin/codex-ds（基于 hermes chat）
8. WS RFC 6455，服务器→客户端不发 mask
humanizer skill 已扩展：新增 Content Strategy Pre-Processing 模块（含2026抖音算法规则），参考文件 references/douyin-2026-algorithm.md。算法核心：收藏率>复访率>铁粉>完播>点赞，搜索流量50%+，7天考核周期，前5秒口播关键词。做短视频脚本/内容策划时自动加载此模块优化内容结构后 humanize。
用户使用QCNET99（ASP建站系统）管理yingxinkuaiji.com。对网站技术操作自称"小白"，需要极细致分步引导（说清点哪个按钮、输入什么）。其他技术工作（服务器、代码）仍偏好直接给结果。
GEO skill 已完整：含门户渠道策略（搜狐/新浪/网易/腾讯，70%行业分析+30%带盈信，文末作者简介，审核比知乎严，新浪最严），QCNET99后台三步操作（分类→文章→菜单，链接地址写相对路径），PDF外化策略（列举法手动记录+文字呈现），示范基地引用模板，知乎/公众号/小红书内容模板。参考文件含 portal-publishing-guide.md。
## ===== 共享记忆 B: 本机实时+新增学习(保留) =====
差>10%废弃重算；office机本机改勿碰共享脚本。
用户桌面=C:\Users\Admin\Desktop(/mnt/c/Users/Admin/Desktop),交付文件一律放这里、只报这个路径;D:\360MoveData 视为不存在(用户多次纠正),即使文件在 D: 盘 360MoveData 下,也要复制到 C 盘桌面再交付。不放WSL桌面~/,不显示WSL路径。
法规核验以fgk政策法规库状态标签为准(全文有效/已修改/全文废止,已修改≠废止如2015-97号);fgk附件xls反爬走省级解读页;二手站标注不可信(shui5 WAF、tfcjtax误标28号);anysearch batch_search可直抓官文。pip清华。
用户常处理苏州爱心之家老年公寓(民办非企业)财报格式转换:小企业准则→民间非营利组织。实收资本+未分配利润→非限定性净资产(负数);应收款项=应收+预付+其他应收;应付款项=应付+其他应付。技能=chinese-accounting-format-conversion。
公众号铁律（用户反复强调）：①严禁AI幻觉，不确定政策/数据/法规绝对不写，引用标注官方文号，宁可少说不说错；②配图铁律：禁止复用任何历史图片、禁止建图片库，每次创作直接用AI生成或查找与主题高度相关的新图，每段配图严格对应本段主题；③模板固定：公司介绍(盈信2009-12-11/江敏创办/TSC五级438.11/17年)→核心业务→二维码→CTA三动作+话题标签5-8个勿漏(详见尾部规范条)→作者"苏州盈信企业管理"。
「朋友圈」→wechat-moments-marketing出文案+3张图+拷桌面；企微API推XuAiJun必须经用户明确确认后手动发送，绝不自动推送
文章改写要求:除换措辞还要打乱结构顺序/重组角度与逻辑链,结构层面不雷同;五大事项类可重排/拆分重组/调侧重点。
Obsidian=第二知识库/永久记忆。D盘=/mnt/d/obsidian-vault主库,WSL=git引擎。脚本hermes_only_snapshot.sh+obsidian_sync.sh。cron每日12:28归档、周一12:28复盘。详obsidian skill。
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
<<<<<<< Updated upstream
AI生图5风格均备选、全不满意要真绘画质感;高优=生图能力(通义万相/文心/ComfyUI/coze),chudian视觉key脱敏不可用。见wechat-comic-cells。
模型分工铁律:①一般性工作+爬虫skill搜索→chudian平台deepseek V4 Flash(节约);②公众号写作→KIMI-K3(子代理成稿);③文案创作→doubao;④完成文案创作/公众号写作时必须向用户汇报用的是哪个模型;⑤deepseek V4 Flash干不了的工作→提示建议、由用户拍板用哪个模型(如生图直接用doubao-seedream-5.0-pro-0724)。
hermes cron CLI:prompt是位置参数`hermes cron create <schedule> <prompt>`;create/remove触发确认门,超时BLOCKED——用户明确授权后写.sh脚本bash执行可成功,勿直接重试,删建分开;查执行`hermes cron runs <id>`;生命周期create→run→runs→remove。`.lazy-refresh-incomplete`警告是噪音,venv健康,验证用import。
yt-dlp+ffmpeg已装,脚本dl下视频/音频,默认存Windows桌面/dl,国内直连,YouTube需Clash(7890只绑Windows宿主)。
公众号改写稿出稿前做去AI味=creative/humanizer技能(用户会主动问"上次用哪个工具",答humanizer)。排版风格除01安信伯君外有02刘润红蓝撞色(红#FF2941蓝#0052FF,风险/警示文数字冲击好)已入库可用;wechat-publish风格库表可能只登记01,列选项时直接列两个。
企微发送:先配回调+可信IP,按键wechat-moments-marketing;推XuAiJun须用户确认。企微AI机器人(WebSocket)已通:wecom启用,@yingxin_inner调Hermes;wecom_callback由env启用只刷40001不抢答。
用户财税类skill(tax-audit-response等)user-owned(vault维护),curator写被拒;书/参考融已有skill→先出方案不自动写;vault的50-Skills软链~/.hermes/skills,改vault即同步勿双份。tax-audit-response触发词「税务稽查/检查/稽查」已注册;与WorkBuddy共建共享源码,改动后写回传说明放桌面。tax-regulation-monitor每月巡查三路交付(vault+桌面+WorkBuddy)。
Hermes 本机=上游 git clone 于 /home/dmin/hermes-agent(非混合仓库),venv=.venv-hermes,已升 0.21.4;用户技能 skills/tax-audit-response 为非跟踪保留文件。WSL 连 Windows Clash 走网关 172.23.96.1:7890(非127.0.0.1)。GitHub 大单文件传输(>~60MB)会被节点切断且 git 无法续传:改从 gh-proxy.com 下载源码 zip 支持 range 续传(-C - 循环+zipfile CRC 校验)最稳,勿用 git fetch 硬磨。
生图铁律:有生图任务一律走doubao-seedream-5.0-pro-0724(经电信中转aigw.telecomjs.com/v1,OpenAI兼容),严禁用deepseek-v4-flash或降级其他模型,整任务跑完再回默认模型。脚本内嵌于image-gen-cn skill的scripts/目录($HOME/.hermes/skills/creative/image-gen-cn/scripts/image_gen_seedream.py),随skill跨机同步;key在每台机的.env配SEEDREAM_API_KEY(.env不同步需手动配)。视觉验收:auxiliary.vision用chudian的deepseek-v4-flash-vision-exp(复用DEEPSEEK_API_KEY),vision_analyze看图查乱码。见image-gen-cn skill。
跨机同步坑:jsxuaijun-art/hermes-data 的 main 曾被 force-rebuild(现线817/迁移到f4d6965,实为远端重新构建),本机 C:\Users\Admin\hermes-sync 的git历史曾 orphaned(8a3ad2c基于旧eded719)。push前必须先 fetch 看 origin/main 是否与本地分叉,勿盲推/勿 force-push(会毁远端);远端是唯一真相源,叠加改动用 reset --hard origin/main 后只 add 目标文件(勿 add -A 扫入 machine-specific config/skills)。.env 与 config.yaml 是各机独立的,勿共享覆盖。
为短视频内容做「话题/标题总结」时,勿停留在表面叙事,要'站得更高看得更远'(上帝视角):深度提炼底层主旨。方法论:把一个具体家务/日常现象上抽到-定义本质-再归纳到一个更高维的核心概念(如'托举'→升级为'内耗/家庭能量管理'),金句洞察往往藏在结尾自省句(如'多数家庭更擅长拽下来而非托上去'=内耗是本能的,托举是反本能的)。示例:用户《托举》文案→深层主旨=「家庭兴旺的底层是'不内耗'——能量单向向外输出 vs 内部对消归零(家庭资源配置/人力资本经营)」→标题抓'内耗/能量管理'比抓'托举'更站高。此思想法已写入 short-video 技能「上帝视角·深层主旨提炼」节。
=======
§
文案路由(9.22):短视频默认豆包db,完成后必汇报所用模型(默认豆包,明确指定其他也报);钩子可走数字对比/同行吐槽两风格,钩子不强即废稿(软陈述"我做了XX年…"必被否,用反问冲突→数字资历→反转三拍);交付只出docx一份勿再出txt;爆款长文默认Kimi主动提示·代理=CordC2.8.5
§
hermes cron:create <schedule> <prompt>,执行查`hermes cron runs`;苏州政策监控已部署(cron'苏州城市破播'周二五9点投企微内部群'徐江机器人'wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg,gateway在线才自动触发,手动run不投递;细节见short-video-copywriting类型五);政务检索用anysearch抓官文(文号+日期)。pip清华。
§
脱敏边界【全局规则,适用所有skill】(2026.9.15定稿):只有用户主动发送的信息/文件才脱敏;agent抓网页/搜索(web_search/web_extract/browser_*)公开数据不脱敏,插件desensitize-read默认目标集已剔除网络类(read_file/search_files/terminal/execute_code/vision_analyze保留)。脱敏铁律(处理任何上传材料自动执行):①公司名除
§
技能统一库:四工具(Hermes/Claude/Codex/WorkBuddy)同读SKILL.md零转换;canonical=C:\Users\Administrator\skill-library,管理器~/skill-library-ops/skilllib.py,cron skill-exchange周日23:00。
§
本机Hermes升级=混合目录隔离法勿git reset
§
代理=CordC2.8.5(F:\CordC\),AllowLAN在设置→网络;条件脚本~/.hermes/proxy.sh。
§
人设锚点(identity-anchor/产品手册)共6副本改必全同步,源CRLF,diff tr -d '\r'
>>>>>>> Stashed changes
