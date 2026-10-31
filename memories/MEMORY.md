公众号尾部(2026.10.19徐总定稿):总结+话题标签5-8个+作者落款默认收尾;公司介绍+核心业务+CTA两动作(收藏/转发)每次必带;二维码/电话/免费资料/CTA'关注'除非用户明确说否则一律不放。电话132-2229-7318/180-1262-7126。
§
公众号改写/去AI味:出稿前用creative/humanizer去AI味。改写=换措辞+打乱结构顺序+重组角度逻辑链,结构层面不雷同,五大事项类可重排/拆分/调侧重点。排版风格:01安信伯君、02刘润红蓝撞色(红#FF2941蓝#0052FF,风险/警示文数字冲击好)。对外稿不写本行业具体价档(200元/年)→统一'超低价代理记账';他行业官方数字可写;低价四条路含AI代账
§
AI内容纪律(徐总2026.9.21,详Obsidian/AI内容纪律+skill content-evidence-discipline):涉法文案→严禁幻觉先核实带文号依据清单;"法"=全部法律层面不限于税法(非文案等同A严守;B创作文案豁免尽情发挥只守合规红线;交叉:引法规/数据当卖点须有据)。占位规则(2026.10):结构需要可先"编造"但必须显式红标占位(【待填】/⚠待核实)+交付时逐条点名要用户替换;被点名一处编造→立即全篇事实普查,勿只改那一处。
§
GEO必加载geo-optimization技能+8平台指南(百家号/知乎/网易号/新浪财经头条/企鹅号/搜狐号/今日头条/公众号)。中文、直接给能用方案。
§
触发词约定:「朋友圈」→wechat-moments-marketing出文案+3张图+拷桌面;企微API推XuAiJun必须经用户明确确认后手动发,绝不自动推送。「调用短视频skill」→自动同时调爬虫skill(python-web-scraping-setup)按主题搜信息,输出超前超脱的上帝视角、提不同观点并分析透。短视频文案交付后必附一朋友圈简短版(徐总风格=口语接地气+留悬念+合规/价值观升华+不硬广,点到留口子)。
§
Obsidian=第二知识库/永久记忆:D盘=/mnt/d/obsidian-vault主库,WSL=git引擎,脚本hermes_only_snapshot.sh+obsidian_sync.sh,cron每日12:28归档、周一12:28复盘。勿搬~/.hermes运行时(密钥/SQLite/--delete)。详obsidian skill。
§
跨机同步:远端唯一真相源,勿盲推/勿force-push;改memories等跨机累积共享文件=合并勿覆盖(cp整文件会清仓,commit rewrite99%/巨量diff=信号);恢复=git show旧commit:path取回远端版→awk按行去重→双grep校验→再推;push前先fetch看与origin/main分叉。.env与config.yaml各机独立勿共享覆盖。
§
技能统一库:四工具(Hermes/Claude/Codex/WorkBuddy)同读SKILL.md零转换;canonical=C:\Users\Administrator\skill-library(扁平skills/<名>),管理器~/skill-library-ops/{skilllib.py,exchange.sh},cron周日23:00;各端侧是嵌套skills/<类>/<名>,改完用md5比对全同。hermes-data仓库=/mnt/c/Users/Admin/hermes-sync(git@github.com:jsxuaijun-art/hermes-data),推送~/.hermes/sync-push.sh。找副本/仓库别扫全盘(慢到超时),按已知路径定点查。
§
user-owned技能不可自动改(实测skill-library-sync、github-tool-vetting、scraping-dispatch、github-repo-access、sph-video-downloader、tax-audit-response、short-video-copywriting(根+social-media双份)、llm-longform-generation等),需先`hermes curator adopt <name>`;agent建过的(powerpoint、compliant-accounting)可自动改。用户财税类skill由vault维护,50-Skills软链~/.hermes/skills,改vault即同步勿双份;tax-audit-response触发词「税务稽查/检查/稽查」已注册,与WorkBuddy共建,改动后写回传说明放桌面;tax-regulation-monitor每月三路交付(vault+桌面+WorkBuddy)。
§
本机Hermes实装=/home/dmin/hermes-agent-v0.20.6,2026.10.29 zip覆盖升v0.22.5,无.git故--version显vunknown(正常);/home/dmin/hermes-agent=另份独立源码副本勿动;venv=.venv-hermes;gateway=用户systemd hermes-gateway.service,代码换新后旧unit过时→『Gateway starting: deadline』,修法=`hermes gateway install`重生unit;hermes alias=~/.hermes/hermes-wsl.sh(企微云端逻辑)。WSL连Windows Clash走172.23.96.1:7890。config.yaml受保护须`hermes config set`(改前cp备份)。GitHub大单文件被节点切断,gh-proxy.com下zip续传(-C -循环+CRC校验)最稳。
§
视觉降级:auxiliary.vision已指向telecom豆包Doubao-Seed-2.1-Pro(aigw.telecomjs.com/v1,${TELECOM_DOUBAO_KEY})=主模型读不了图时自动接管,无需换主模型。探针=skill hermes-free-model-channels/scripts/vprobe.py(发已知随机码图验真伪)。
§
代理=CordC2.8.5(F:\CordC\),AllowLAN在设置→网络;条件脚本~/.hermes/proxy.sh。yt-dlp+ffmpeg已装(WSL侧ffmpeg=imageio-ffmpeg静态版,已symlink为~/.local/bin/ffmpeg;Windows侧ffmpeg8.1含ffprobe)。脚本dl下视频/音频默认存Windows桌面/dl,国内直连,YouTube需Clash(7890只绑Windows宿主);下载+合并必须同系统(跨系统路径不通)。
§
视频号(weixin.qq.com/sph/)下载=徐总刚需必须成功使用,经常用;走skill sph-video-downloader(奇云API首选code=200,直链finder.video.qq.com;凭据QIYUN_APP_ID/KEY已配本机密钥文件,勿把值写进记忆/推送以免同步GitHub);执行scripts/parse_download_qiyun.py <链接> <输出.mp4>→桌面\视频号\;要口播文案再交faster-whisper转写。
§
长文出稿铁律:第三方网关(telecom aigw)非流式调用有~90s响应上限,长稿会中途断/整单超时→必须stream=true流式直连。delegate_task走非流式,委派写长稿(文案/文章)易整体失败,要如实说+改流式重试。通用调用器=skill llm-longform-generation/scripts/stream_chat.py(密钥走环境变量名传入,勿内联)。
§
hermes cron:prompt是位置参数`hermes cron create <schedule> <prompt>`;create/remove触发确认门超时BLOCKED——用户明确授权后写.sh脚本bash执行可成功,勿直接重试,删建分开;查执行`hermes cron runs <id>`;生命周期create→run→runs→remove。苏州政策监控已部署(cron'苏州城市破播'周二五9点投企微内部群'徐江机器人'wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg,gateway在线才自动触发,手动run不投递;细节见short-video-copywriting类型五)。.lazy-refresh-incomplete警告是噪音,venv健康。
§
法规核验以fgk政策法规库状态标签为准(全文有效/已修改/全文废止,已修改≠废止如2015-97号);fgk附件xls反爬走省级解读页;二手站标注不可信(shui5 WAF、tfcjtax误标28号);anysearch batch_search可直抓官文。pip清华。
§
脱敏边界【全局规则,适用所有skill】:只有用户主动发送的信息/文件才脱敏;agent抓网页/搜索(web_search/web_extract/browser_*)公开数据不脱敏,desensitize-read默认目标集已剔除网络类(read_file/search_files/terminal/execute_code/vision_analyze保留)。处理任何上传材料(①公司名称②统一社会信用代码③法定代表人姓名/身份证号)一律先脱敏再进对话/入库/同步。①公司名除"有限公司"外汉字逐字取拼音首字母大写(甲乙丙丁(苏州)有限公司→JYBD(SZ)有限公司,简称同步);②信用代码18位保留前10位、末8位全X;③法人姓名前两字→TT(杨建国→TT国)。真实主体交付物仅本地留真实版。desensitize-read只拦工具读入(次日会话生效),用户直接发文字靠人工纪律;用户明确不要本地词表存真实身份(勿再提议)。2026.9.15定稿,详skill security/desensitization。
§
防误删sync_guard+P11见skill hermes-data-sync,wsl-hermes-env§9。注销skill勿改qingshui_risk_engine.py(把「期初」当「期末」),用前人工核对期末(C&G列)差>10%废弃;office机本机改勿碰共享脚本。memories源=~/.hermes/memories/。
§
人设锚点(identity-anchor/产品手册)共6副本改必全同步,源CRLF,diff tr -d '\r'。
§
D:\360MoveData 实际存在（360迁移），会存放用户桌面文件；用户给该路径时按实际存在读取勿默认不存在。默认交付仍放 C:\Users\Admin\Desktop，只报Windows路径不报WSL
§
对外材料(PPT/方案/公司介绍)事实纪律:具体事实(学历院校届别/评审人数通过率/行业占比/客户数转介绍率/成立年份/资质分)无据一律不得编;确需占位用醒目色#C00000+角标注「待核实」+附《待核实清单》+口头提醒用户核对。配图只用装饰图形/原生图表/占位框,禁用暗示「本公司实景·本团队」的网图或AI图。
§
盈信公司介绍PPT工程:脚本C:\Users\Administrator\yingxin_ppt\build.js(pptxgenjs,可改文字/配图),成品同目录+桌面同名;逐页预览C:\Users\Administrator\yingxin_preview\img\slide-01..10.png;校验脚本qa/overlap/pixcheck/final_check.py同目录。
§
pptxgenjs行距陷阱:lineSpacing单位是磅(写spcPts),写1.05=行距1.05磅→多行叠字重叠;倍数要用lineSpacingMultiple(spcPct)。诊断10秒:COM读ParagraphFormat.LineRuleWithin(0=磅/-1=倍数)。本机(WSL)可用powershell.exe驱动PowerPoint COM当排版真值渲染器,Lines().Count与BoundWidth可靠,BoundTop/BoundHeight不可靠。详见skill document-rendering-verification。
§
自动化脚本踩坑两则:①write_file生成的.ps1是UTF-8无BOM,Windows PowerShell 5.1按ANSI读→脚本内中文路径必乱码,COM报「找不到文件」但文件明明在(报错文本本身也是乱码,别追它);对策.ps1只留ASCII+param()传参,或中文名文件先cp成ASCII名再喂COM。②脚本直读config.yaml的api_key常拿到${VAR}字面量→401,须先由os.environ展开。.docx校验脚本见skill document-rendering-verification/scripts/docx_com_metrics.ps1。
§
合规账报价表已入skill compliant-accounting:refs/13-合规账报价表与定价口径.md(4档12行官方阶梯)+templates/合规账报价表模板.docx+scripts/gen_quote.py(改价改顶部常量)。定价唯一源=13-参考;03-产品手册§八年费区间是旧口径勿混用。该skill有顶层与skills/skills两份副本,内容已一致。
§
用户常处理苏州爱心之家老年公寓(民办非企业)财报格式转换:小企业准则→民间非营利组织。实收资本+未分配利润→非限定性净资产(负数);应收款项=应收+预付+其他应收;应付款项=应付+其他应付。技能=chinese-accounting-format-conversion。
§
企微发送:先配回调+可信IP,见wechat-moments-marketing;推XuAiJun须用户确认。企微AI机器人(WebSocket)已通:wecom启用,@yingxin_inner调Hermes;wecom_callback由env启用只刷40001不抢答。
§
注销话术触发(sales-communication):注销话术/公司注销/注销收费/比注册贵/包注销/捆绑销售/记账就该包注销/清算→通用-注销清算收费异议处理.md。
§
为短视频做「话题/标题总结」要'站得更高看得更远'(上帝视角):把具体家务/日常现象上抽到-定义本质-再归纳到更高维核心概念,金句洞察常藏结尾自省句(如'多数家庭更擅长拽下来而非托上去'=内耗是本能的,托举是反本能的)。示例《托举》→主旨「家庭兴旺的底层是'不内耗'——能量单向向外输出 vs 内部对消归零」→标题抓'内耗/能量管理'比抓'托举'更站高。已写入short-video技能「上帝视角·深层主旨提炼」节。
§
视觉路由陷阱(2026.10.11定位修复,跨机必读):中转站llm.chudian.site的deepseek-v4-flash实为纯文本,但models.dev在线目录误标supports_vision=True→vision_analyze判定native→把base64图塞进tool-result历史→主模型每轮400『不支持以下输入类型:image』且错误体不匹配恢复短语表(仍判non-retryable)→全会话卡死。修复=能力覆盖:`hermes config set providers.deepseek.models.deepseek-v4-flash.supports_vision false`(config.yaml受保护,改前cp备份),令_model_supports_vision()=False,历史图自动转auxiliary.vision文本描述。换任何『目录说能看图但中转实际纯文本』的模型,先加此provider级覆盖;图片兜底=auxiliary.vision(chudian deepseek-v4-flash-vision-exp)。
§
「推送github」=双通道全推(徐总默认两处都要):①统一库skill-library(C:\Users\Administrator\skill-library)②hermes-data(本地仓库=/mnt/c/Users/Admin/hermes-sync,注意用户名是Admin非Administrator)。hermes-data走~/.hermes/sync-push.sh(已修为v5:先fetch+reset再拷贝本地,旧版顺序会静默丢掉已跟踪文件如SKILL.md的改动),跑完必核 local==remote。桌面成品(Word/PDF/PNG)不入库。
§
交付打包铁律(徐总2026.10.12):一任务全部产物先入同名文件夹再压成一个zip,桌面C:\Users\Administrator\Desktop只留压缩包禁零散。实操(folder→zipfile→rmtree勿shell rm;Word占用报PermissionError勿重试)详skill内容纪律。
§
memory工具陷阱:replace的content=整条覆盖(old_text仅定位),补句须抄全原条否则静默丢内容;想加内容而用量变小=已丢,立即还原。
§
公众号素材坑:『视频来了!』类视频型文章(mp.weixin.qq.com)js_content无正文且无var msg_title/ct,元数据用og:title/og:description兜底,正文从视频本身转写或同批姊妹图文稿取。完整提取脚本待wechat-publish被curator adopt后落位scripts/。
§
模型路由铁律(2026.10.29徐总更新):Hermes默认模型=chudian deepseek-v4-flash(provider deepseek, base_url https://llm.chudian.site/v1, key=DEEPSEEK_API_KEY);只有用户专门命令或调用指定skill才切kimi-k3,日常默认不再用kimi。切换/完成任务要报所用模型。视觉仍按降级链:deepseek-v4-flash禁原生视觉,auxiliary.vision=chudian deepseek-v4-flash-vision-exp;短文案/生图旧规则由对应skill触发,不改默认路由。