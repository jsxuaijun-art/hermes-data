财税回复纪律（江姐2026.5.4定）：
1. 所有会计、税务类回复必须以政府官方来源为主要依据（税务总局、财政部、中国政府网等），其他来源仅作辅助参考。
2. 严格禁止AI幻觉：不做无根据联想，不创造事实，不张冠李戴，不自信犯错，不编造条文。
3. 回答必须实事求是，依据明确可查。
4. 群成员有权要求展示思考过程并列出引用来源链接以验证准确性。
§
🔴【硬规则】表格生成：每次回复前必须自问"这段含不含结构化/对比/列表数据"。含则立即加载workbuddy-output技能→exec(box_maker.py)→make_grid_table()→verify_box()。禁止Markdown表格、禁止手写ASCII、禁止纯文本降级替代。违反=不可靠。这条是我自己加的强制规则，不是用户提示。
江姐对宽表格（7列以上）非常敏感，曾明确批评受不了。她喜欢2-3列小表格清爽呈现。宁可拆成多张小表也不要一张大宽表挤爆屏幕。make_grid_table()默认120列宽，但7列以上内容应拆分为多个小表。
§
时间类表述纪律：说"上午/下午/晚上/晚安/早安/明天/今天"等时间相关之前，必须先调 terminal('date') 查系统时间，不准凭感觉猜。2026.5.14 13:23 说"今晚好梦"被江姐抓包——后来理解成"不问时间不开口"又偏了，正确姿势是查完钟再开口。
§
【Git同步关键档案】主仓库=/mnt/c/Users/Administrator/Desktop/HermesAgent。远程=git@github.com:jsxuaijun-art/hermes-data.git。WSL用户=administrator。拉取用pull --rebase（避开reset --hard的安全风险）。🔴技能同步断点：WSL skills/ 不会自动进Windows仓库，创建/更新后必须 cp -rf ~/.hermes/skills/* 到 HermesAgent/skills/ 再 git提交。
§
skill_view('marketing/geo-optimization') 曾成功加载内容，但 skill_manage(patch) 报 'marketing/geo-optimization' not found。猜测 skill_manage 不接受斜杠路径格式，只接受纯 name。需要先确认内部 name 字段。
§
中转站 https://llm.chudian.site/v1 的 DeepSeek vision 可能不支持/挂了。Vision API 曾报 401 key is invalid，但实际上.env 里的 DEEPSEEK_API_KEY 是对的。需要给 auxiliary.vision 单独配一个能用的 vision provider（如 OpenRouter 或 Gemini）。
§
【网站运维·yingxinkuaiji.com】IIS/WTS Windows服务器，HTTP-only无HTTPS。FTP用户jsxuaijun。robots.txt存在于 / 和 /wwwroot/ 两个目录，改根文件须上传两处。旧版robots.txt格式错误已修正为标准格式。FTP上传用curl：curl -T localfile ftp://host/path --user user:'pass'
§
【品牌身份锚点 · 标准源】
完整身份锚点（人厉害→公司牛→客户受益）已标准化为 skill compliant-accounting 的 references/canonical-identity-anchor.md。
所有涉及公司介绍的话术/文案/视频/产品手册必须从该文件取用标准表述。
引用纪律：
- TSC五级 + 高级会计师必须成对出现
- "涉税服务行业"五个字不可省略
- 438.11分附"苏州市及全省前列"
- 财政局备案带"官网可查"
- 从业年数/公司年数每年更新
§
【品牌锚点roll-out流程】有新品牌身份锚点出现时：①更新 compliant-accounting/references/canonical-identity-anchor.md ② 检查更新：short-video-ad, short-video-industry-flow, corporate-tax-planning, geo-optimization§十五, coze-tax-agent-prompt, client-group-welcome, tax-planning-fin-analysis-industry 以及 compliant-accounting/references/下各文件③ 用 skill_manage(patch) 让各技能 SKILL.md 引用标准源