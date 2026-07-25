2026.6.19 抖音算法深度更新已入skills：权重公式VPS35%+ENG25%+RET20%+TAG15%+ACCT5%。晋级门槛：完播≥38%/互动≥12%/留存≥18%/纯度≥65%/健康≥70%。指标排序：收藏>复访>铁粉互动>5秒完播>整体完播>评论>点赞>转发。六阶池(种子300-500→兴趣500-5000→价值→扩量→高热200万→超级千万)。直播15min赛马+内容/交易/合规(一票否决)。考核24h变7天。标签匹配→行为预测。付费eCPM=eCTR×eCVR×出价×1000。
§
表格规则（2026.5.24更新）：必须加载 box_maker.py，用 make_grid_table() 生成带 ├┤横线和│竖线的 ASCII 网格。右竖线严格对齐，禁止 Markdown 表格。生成后 verify_box() 验证。单元格公式 cell=" "+text+" "*(cw-1-dw(text))，cw=max_dw+2。Emoji/CJK按wcwidth+emoji presentation检测（U+FE0F/U+200D零宽跳过）。已替代旧的skill_view路径。具体路径见用户profile。
§
2026.6.27 商事登记(注册/变更/注销)正式确认为核心业务线，与税务合规/代理记账/高级会计师背书并列。企微内部机器人名yingxin_inner，热点视频链接发给它。
§
高级会计师名单锚点（2026.5.23）：2018江苏819人中江姐是唯一以代账公司名义通过高级会计师评审者（非挂靠）。2025年1216人中仅3家代账公司。差异公式：纵向819唯一→横向大厂垫背→深度16年→广度苏州上海→验证多平台。对外用"八九百人里唯一一家代账公司"最有冲击力。已在skills存档。
§
韩红走面儿方法论：锚点(认知税/面子通缩/情感庞氏)→三段(立论点→挖根因→定调收网)→上帝视角抽象真普适→融合财税找隐喻链。犀利=硬逻辑非情绪。江姐满意。
§
Chinese web search (2026.6.27): Google blocked. Priority: ① Bing(cn.bing.com) ② curl_cffi to Sogou ③ Playwright(chromium at ~/.cache/ms-playwright/) ④ Baidu triggers captcha. DrissionPage needs Chrome path. For hot topics → ALWAYS proactively ask user to send 1-2 Douyin videos (ffmpeg+faster-whisper analyze) or provide keywords to search news. Douyin.com has strong anti-scrape, can't access directly.
§
2026.6.27 商事登记文案方法论已验证：热点→专业→CTA三段式，商事登记6个切入角度(比价/注销/变更/体检/类型/注册资本)。脚本上限5条放桌面不存memory。工作流：江姐给热点→我问有视频没→她发企微yingxin_inner→我ffmpeg+whisper分析→出文案。CTRL:统一用"找江姐"。
§
x
§
英语词频：GitHub raw(hermitdave/FrequencyWords)已429封禁(2026.7.6确认，国际联网也拿不到)。改用本地缓存或百度文库VIP+新东方txt下载替代。
§
2026.7.4 词汇默写本词根版v3最终: "#"列0.2cm/页码"2/365"/255+Membean根/Part1(28组×6轮+鼓励语)+Part2(50组×4轮无学习)/音标填空两行/鼓励语每组必出。skill已更新至vocab-memory-book scripts/build_root.py。
§
2026.7.7 cron 多环境要点：「财税情报推送」在阿里云 /root/.hermes/ 跑（非WSL本机），每周一/三/五 ~08:30，爬政策→推企微。7/6-7/7连续502 llm.chudian.site挂。交互教训：用户贴实时日志=在tail -f。已补入cron-tasks skill。
§
2026.7.24 文件袋定稿：正面全部内容（高级会计师创办→苏州盈信→16年→业务线→双电话→双二维码→底部'江苏省高级会计师·代理记账行业入选企业'），背面空白。服务列表：税务合规·公司注册·代理记账 / 会计外包·高企申报·财务咨询。电话132-2229-7318和180-1262-7126。二维码用草料cli.im生成。单面印刷。定稿存桌面'文件袋设计_定稿.docx'。
§
2026.7.25 配图纪律+换图流程入wechat-publish；措辞封顶原则入offline-collateral-design。对味确认。