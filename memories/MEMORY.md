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
技能统一库:四工具(Hermes/Claude/Codex/WorkBuddy)同读SKILL.md零转换;canonical=C:\Users\Administrator\skill-library,管理器~/skill-library-ops/skilllib.py,cron skill-exchange周日23:00。
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
统一库(skilllib.py)实测铁律(2026.10):①四工具唯一共同硬性frontmatter=name,Claude风格(仅user-invocable/description/allowed-tools)会全库FAILURE,补法=在开头---后第二行插`name:<目录名>`;②install与import-from-hermes均非破坏(同名已存在即跳过)→改了技能内容不会自动扩散,verify只校验frontmatter不比对内容,故全绿≠已同步;证明分发须md5比对lib+四工具五处副本;③Hermes侧同名技能可能有多份嵌套副本(research-en/与deep-research/research-en/并存),定位用rglob勿写死分类路径。skill-library-sync系user-owned写不进,需`hermes curator adopt skill-library-sync`后移入。
§
路径表达铁律:回复中一切文件路径一律用Windows盘符(C:\...),绝不出现WSL路径;连脚本/工作目录也先拷到C盘目录再引用(如C:\Users\Administrator\yingxin_ppt\)。详skill wsl-windows-file-delivery。
§
对外材料(PPT/方案/公司介绍)事实纪律:具体事实(学历院校届别·评审人数/通过率·行业占比·客户数/转介绍率·成立年份·资质分)无据一律不得编;确需占位时用醒目色(#C00000)+角标注「待核实」并附《待核实清单》+口头提醒用户核对。配图只用装饰图形/原生图表/占位框,禁用暗示「本公司实景·本团队」的网图或AI图。
§
盈信公司介绍PPT工程:脚本C:\Users\Administrator\yingxin_ppt\build.js(pptxgenjs,可改文字/配图),成品同目录+桌面同名;逐页预览图C:\Users\Administrator\yingxin_preview\img\slide-01..10.png;校验脚本qa/overlap/pixcheck/final_check.py同目录。