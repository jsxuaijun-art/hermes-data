防误删sync_guard+P11见skill hermes-data-sync,wsl-hermes-env§9。注销skill勿改qingshui_risk_engine.py(把「期初」当「期末」),用前人工核对期末(C&G列)差>10%废弃。memories源=~/.hermes/memories/。
§
AI内容纪律(徐总2026.9.21定稿,权威文档:Obsidian公司运营/AI内容纪律+桌面txt):A涉法文案→严守严禁幻觉先核实再引带文号带依据清单;"法"=全部法律层面不限于税法(宪法/民典/公司/劳动/广告/反不正当竞争/个信法+行政法规部门规章司法解释+地方性法规政府规章+监管政策文号法定义务权利),无论主题是否财税.C非文案(客户答复/财税咨询/测算/报表)→等同A严守,B创作文案(泛话题/趣味破播/爆款/脑洞)→豁免尽情发挥,只守平台合规红线;交叉规则:B整篇可飞但引具体法规/数据当卖点那句回A须有据,一句话涉法必严创作可飞非文案必严。
§
GEO必加载geo-optimization技能+8平台指南(百家号/知乎/网易号/新浪财经头条/企鹅号/搜狐号/今日头条/公众号)。中文、直接给能用方案。
§
公众号铁律：①涉政策/数据/法条绝对不写幻觉，引用标官方文号宁少勿错；②配图禁止复用历史图/建图库，每次生成或查高相关新图逐段对应；③模板：公司介绍(盈信2009-12-11/江敏创办/TSC5级438.11/17年)→核心业务→二维码→CTA三动作+话题5-8个勿漏→作者"苏州盈信企业管理"。交付统一C:\Users\Administrator\Desktop。
§
用户触发词约定：「朋友圈」→wechat-moments-marketing出文案+3张Unsplash图+拷桌面+企微API推XuAiJun勿问确认。「调用短视频skill」→自动同时调爬虫skill(python-web-scraping-setup)按主题搜信息，输出要超前超脱的上帝视角、提出不同观点并分析得头头是道。
§
文章改写要求:除换措辞还要打乱结构顺序/重组角度与逻辑链,结构层面不雷同;五大事项类可重排/拆分重组/调侧重点。
§
Obsidian=第二知识库:D盘/mnt/d/obsidian-vault主库+obsidian_sync.sh,勿搬~/.hermes运行时(密钥/SQLite/--delete)。详obsidian skill。
§
公众号文章尾部(2026-08-06定稿)：电话132-2229-7318/180-1262-7126；CTA三动作(收藏/转发/关注)，标题「请点屏幕右下角：」红粗加大；话题标签5-8个勿漏。详见wechat-publish尾部模板。
§
文案创作路由(9.22):短视频默认豆包db;明说用Kimi才覆盖;爆款长文默认Kimi并主动提示·本机代目=CordC2.8.5(F:\CordC\)AllowLAN在设置→网络
§
hermes cron:create <schedule> <prompt>,执行查`hermes cron runs`;苏州政策监控已部署(cron'苏州城市破播'周二五9点投企微内部群'徐江机器人'wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg,gateway在线才自动触发,手动run不投递;细节见short-video-copywriting类型五);政务检索用anysearch抓官文(文号+日期)。pip清华。
§
脱敏边界【全局规则,适用所有skill】(2026.9.15定稿):只有用户主动发送的信息/文件才脱敏;agent抓网页/搜索(web_search/web_extract/browser_*)公开数据不脱敏,插件desensitize-read默认目标集已剔除网络类(read_file/search_files/terminal/execute_code/vision_analyze保留)。脱敏铁律(处理任何上传材料自动执行):①公司名除
§
技能统一库:四工具(Hermes/Claude/Codex/WorkBuddy)同读SKILL.md零转换;canonical=C:\Users\Administrator\skill-library,管理器~/skill-library-ops/skilllib.py,cron skill-exchange周日23:00。
§
本机(/home/administrator)Hermes升级=混合目录隔离法勿git reset:gh-proxy.com下tar→独立目录→venv pip install -e→config migrate→hermes gateway restart;新版api_server需强API_SERVER_KEY(openssl rand -hex 32入.env)否则exit78;详hermes-auto-upgrade-wsl。
§
代理=CordC2.8.5(F:\CordC\),AllowLAN在设置→网络;条件脚本~/.hermes/proxy.sh。
§
模型分工铁律:①一般性工作+爬虫skill搜索→chudian平台deepseek V4 Flash(节约);②公众号写作→KIMI-K3(子代理成稿);③文案创作→doubao;④完成文案创作/公众号写作时必须向用户汇报用的是哪个模型;⑤deepseek V4 Flash干不了的工作→提示建议、由用户拍板用哪个模型(如生图直接用doubao-seedream-5.0-pro-0724)。
§
生图铁律:有生图任务一律走doubao-seedream-5.0-pro-0724(经电信中转aigw.telecomjs.com/v1,OpenAI兼容),严禁用deepseek-v4-flash或降级其他模型,整任务跑完再回默认模型。脚本内嵌于image-gen-cn skill的scripts/目录($HOME/.hermes/skills/creative/image-gen-cn/scripts/image_gen_seedream.py),随skill跨机同步;key在每台机的.env配SEEDREAM_API_KEY(.env不同步需手动配)。视觉验收:auxiliary.vision用chudian的deepseek-v4-flash-vision-exp(复用DEEPSEEK_API_KEY),vision_analyze看图查乱码。见image-gen-cn skill。
