防误删sync_guard+P11见skill hermes-data-sync,wsl-hermes-env§9。注销skill勿改qingshui_risk_engine.py(把「期初」当「期末」),用前人工核对期末(C&G列)差>10%废弃。memories源=~/.hermes/memories/。
§
AI内容纪律(徐总2026.9.21,详Obsidian/AI内容纪律+skill content-evidence-discipline):A涉法文案→严禁幻觉先核实带文号依据清单;"法"=全部法律层面不限于税法(C非文案等同A严守;B创作文案豁免尽情发挥只守合规红线;交叉:B可飞但引法规/数据当卖点须有据)。占位规则(2026.10):结构需要可先"编造"但必须显式红标占位(【待填】/⚠待核实)+交付时逐条点名要用户替换;被点名一处编造→立即做全篇事实普查,勿只改那一处。
§
GEO必加载geo-optimization技能+8平台指南(百家号/知乎/网易号/新浪财经头条/企鹅号/搜狐号/今日头条/公众号)。中文、直接给能用方案。
§
公众号铁律：①涉政策/数据/法条绝对不写幻觉，引用标官方文号宁少勿错；②配图禁止复用历史图/建图库，每次生成或查高相关新图逐段对应；③模板：公司介绍(盈信2009-12-11/江敏创办/TSC5级438.11/17年)→核心业务→二维码→CTA三动作+话题5-8个勿漏→作者"苏州盈信企业管理"。交付统一C:\Users\Administrator\Desktop。
§
用户触发词约定：「朋友圈」→wechat-moments-marketing出文案+3张Unsplash图+拷桌面+企微API推XuAiJun勿问确认。「调用短视频skill」→自动同时调爬虫skill(python-web-scraping-setup)按主题搜信息，输出要超前超脱的上帝视角、提出不同观点并分析得头头是道。
§
文章改写:换措辞且打乱结构/重组角度逻辑链不雷同,五大事项类可重排拆分调侧重点。
§
Obsidian=第二知识库:D盘/mnt/d/obsidian-vault主库+obsidian_sync.sh,勿搬~/.hermes运行时(密钥/SQLite/--delete)。详obsidian skill。
§
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
§
hermes cron:create <schedule> <prompt>,执行查`hermes cron runs`;苏州政策监控已部署(cron'苏州城市破播'周二五9点投企微内部群'徐江机器人'wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg,gateway在线才自动触发,手动run不投递;细节见short-video-copywriting类型五);政务检索用anysearch抓官文(文号+日期)。pip清华。
§
脱敏边界【全局规则,适用所有skill】(2026.9.15定稿):只有用户主动发送的信息/文件才脱敏;agent抓网页/搜索(web_search/web_extract/browser_*)公开数据不脱敏,插件desensitize-read默认目标集已剔除网络类(read_file/search_files/terminal/execute_code/vision_analyze保留)。脱敏铁律(处理任何上传材料自动执行):①公司名除
§
技能统一库:四工具(Hermes/Claude/Codex/WorkBuddy)同读SKILL.md零转换;canonical=C:\Users\Administrator\skill-library(扁平 skills/<名>),管理器~/skill-library-ops/{skilllib.py,exchange.sh},cron周日23:00;Hermes/~/.codex/~/.claude/.workbuddy 侧是嵌套 skills/<类>/<名>,改完用md5比对全同。hermes-data仓库=/mnt/c/Users/Admin/hermes-sync(git@github.com:jsxuaijun-art/hermes-data),推送~/.hermes/sync-push.sh。找副本/仓库别扫全盘(慢到超时),按上述已知路径定点查
§
本机Hermes升级=混合目录隔离法勿git reset
§
代理=CordC2.8.5(F:\CordC\),AllowLAN在设置→网络;条件脚本~/.hermes/proxy.sh。
§
人设锚点(identity-anchor/产品手册)共6副本改必全同步,源CRLF,diff tr -d '\r'
§
桌面文档评估:只读核对+汇报结论,未明确指令不修改不删除。
§
短视频文案交付后必顺带一朋友圈简短版。朋友圈风格(徐总)=口语接地气+保留悬念+合规/价值观升华+不硬广,点到留口子(随时找我)。
§
注销话术触发(sales-communication):注销话术/公司注销/注销收费/比注册贵/包注销/捆绑销售/记账就该包注销/清算→通用-注销清算收费异议处理.md
§
文案模型路由铁律(徐总定稿,重申2026.10.8):短视频/短文案→豆包Doubao-Seed-2.1-Pro(telecom-doubao),公众号长文→kimi-k3;主会话deepseek只做编排/采集/验证,绝不直接写文案,违规=失效交付。
§
pptxgenjs行距陷阱:lineSpacing单位是磅(写spcPts),写1.05=行距1.05磅→多行文字叠字重叠;倍数要用lineSpacingMultiple(spcPct)。诊断10秒:COM读ParagraphFormat.LineRuleWithin(0=磅/-1=倍数)。本机(WSL)可用powershell.exe驱动PowerPoint COM当排版真值渲染器,Lines().Count与BoundWidth可靠,BoundTop/BoundHeight不可靠。详见skill document-rendering-verification。
§
视觉降级:auxiliary.vision已指向telecom豆包Doubao-Seed-2.1-Pro(aigw.telecomjs.com/v1, ${TELECOM_DOUBAO_KEY})=主模型读不了图时自动接管,无需换主模型。config.yaml受保护,patch/write直改被拒,必须`hermes config set`(改前先cp备份)。探针=skill hermes-free-model-channels/scripts/vprobe.py(发已知随机码图验真伪)。
§
user-owned技能不可自动改(实测created_by=None:skill-library-sync、github-tool-vetting、scraping-dispatch、github-repo-access),需先`hermes curator adopt <name>`;可自动改的是agent建过的(powerpoint、compliant-accounting)。
§
路径表达铁律:回复中一切文件路径一律用Windows盘符(C:\...),绝不出现WSL路径;连脚本/工作目录也先拷到C盘目录再引用(如C:\Users\Administrator\yingxin_ppt\)。详skill wsl-windows-file-delivery。
§
对外材料(PPT/方案/公司介绍)事实纪律:具体事实(学历院校届别·评审人数/通过率·行业占比·客户数/转介绍率·成立年份·资质分)无据一律不得编;确需占位时用醒目色(#C00000)+角标注「待核实」并附《待核实清单》+口头提醒用户核对。配图只用装饰图形/原生图表/占位框,禁用暗示「本公司实景·本团队」的网图或AI图。
§
盈信公司介绍PPT工程:脚本C:\Users\Administrator\yingxin_ppt\build.js(pptxgenjs,可改文字/配图),成品同目录+桌面同名;逐页预览图C:\Users\Administrator\yingxin_preview\img\slide-01..10.png;校验脚本qa/overlap/pixcheck/final_check.py同目录。
§
自动化脚本踩坑两则(实证):①write_file 生成的 .ps1 是 UTF-8 无 BOM,Windows PowerShell 5.1 按 ANSI 读→脚本内中文路径必乱码,COM 报「找不到文件」但文件明明在(报错文本本身也是乱码,别追它)。对策:.ps1 只留 ASCII+param() 传参,或中文名文件先 cp 成 ASCII 名再喂 COM;.docx 版校验脚本见 skill document-rendering-verification/scripts/docx_com_metrics.ps1。②脚本直读 config.yaml 的 api_key 常拿到 ${VAR} 字面量→401,须先由 os.environ 展开环境变量。
§
合规账报价表已入skill compliant-accounting:refs/13-合规账报价表与定价口径.md(4档12行官方阶梯)+templates/合规账报价表模板.docx+scripts/gen_quote.py(改价改顶部常量)。定价唯一源=13-参考;03-产品手册§八年费区间是旧口径勿混用。该skill有顶层与skills/skills/嵌套两份副本,内容已一致。
§
yt-dlp已装在Hermes venv(2026.08.19)。WSL侧ffmpeg=imageio-ffmpeg静态版(johnvansickle 7.0.2)，已symlink为~/.local/bin/ffmpeg(yt-dlp只认名字叫ffmpeg的二进制)。自动合并用法:venv/bin/yt-dlp --ffmpeg-location /home/administrator/.local/bin -f "bv*[height<=480]+ba/b[height<=480]" <url>。Windows侧ffmpeg 8.1(Winget,含ffprobe)可从WSL调用,但跨系统合并会因路径不通失败→下载+合并必须同系统。GitHub直连不稳,yt-dlp.exe易半途断(可用curl -C -续传或镜像)。B站视频国内直连约3-4MB/s。
§
视频号(weixin.qq.com/sph/)下载=徐总刚需"必须成功使用"，经常用。sph-video-downloader skill是user-owned(curator未接管,改需先`hermes curator adopt sph-video-downloader`)。解析凭据(奇云QIYUN_APP_ID/KEY 或 redfox REDFOX_API_KEY)截至2026-10均未配置，用户提供后先跑通全链路再交付。
§
微信视频号下载:走skill sph-video-downloader(奇云API首选,code=200,mediaUrl/video_url直链可达finder.video.qq.com)。奇云凭据(QIYUN_APP_ID/QIYUN_APP_KEY)已配置在本机密钥文件,须OCR史勿把值写进记忆/推送(会被同步到GitHub)。跑法:先加载本机密钥后执行skill的scripts/parse_download_qiyun.py <链接> <输出.mp4>。下载到桌面\视频号\目录。已实测成功(Arx1Bbahf5,29s竖屏)。要口播文案再交faster-whisper转写。
§
长文出稿铁律:第三方网关(telecom aigw)非流式调用有~90s响应上限,长稿会中途断/整单超时→必须stream=true流式直连。delegate_task走非流式,委派写长稿(文案/文章)易整体失败,失败要如实说+改流式重试。通用调用器=skill llm-longform-generation/scripts/stream_chat.py(密钥走环境变量名传入,勿内联)。
§
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
