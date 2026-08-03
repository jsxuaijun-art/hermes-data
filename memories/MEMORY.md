抖音算法权重公式已入 short-video-copywriting skill。查询weight formula → skill_view。
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
2026.7.4 词汇默写本词根版v3最终: "#"列0.2cm/页码"2/365"/255+Membean根/Part1(28组×6轮+鼓励语)+Part2(50组×4轮无学习)/音标填空两行/鼓励语每组必出。skill已更新至vocab-memory-book scripts/build_root.py。
§
2026.7.24 文件袋定稿：高级会计师创办→苏州盈信→16年→业务线→双电话→双二维码→底部'江苏省高级会计师·代理记账行业入选企业'。服务：税务合规·公司注册·代理记账/会计外包·高企申报·财务咨询。电话132-2229-7318/180-1262-7126。二维码cli.im生成。单面印刷。存桌面'文件袋设计_定稿.docx'。
§
2026.7.25 本轮会话全部内容已固化至skills：①wechat-publish→配图铁律5条+摘要120字人工编写+落款服务顺序（税务合规·会计外包·高企申报·公司注册·代理记账·财务咨询）；②short-video-copywriting→脚本输出格式（速览表→标题三件套→标签→文案→拍摄速查）+交付.docx放桌面。③携程反垄断4条脚本+离岸信托征税公平角度2条脚本已存桌面。
§
GEO落款定稿(2026.7.26)：【关于苏州盈信】17px楷体深灰+正文14px楷体灰+分隔线+【核型业务】17px深蓝加粗+业务列表14px灰。大小字号已定稿。
§
虚开发票文章(2026.7.27最终) Media ID: ZIKXbXZdS_X3B-GDVk11B-fGNT3OT9jg2D6RB1eK6uF4qoRNrNdFPqTlSOl7Mm0V。references/旧GEO落款需手动更新。
§
公众号文章规范（2026.7.26 定稿）：①GEO正文14px（与业务信息字号统一），②表格表头用"序号"不用"#"。已写入wechat-publish。
§
2026.7.27 创建 wechat-qa-publish skill（互补wechat-publish）：公众号发布后QA。含手机端预览验证清单（3列表格滑动检查）、替换已发布文章6步流程。wechat-publish手动创建无法被curator patch，故用新skill承载发布后QA职责。
§
Hermes 15级进化框架：自检已完成（基线L7），进入按周执行升级。第1周邮箱（163 POP3落地+每日cron监控）、L4单模型分层策略、第2周L6并行调研已跑通（3路：竞品定价/金税四期/抖音获客）。用户想把L6并发从3提到5，先跑3够用。