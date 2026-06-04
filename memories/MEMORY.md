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
【股权架构三skill闭环】已读 Book 1《一本书讲透股权》(宋俊生·王亚龙, 2025.12, 280页)全文 /tmp/equity_book1_full.txt。分配：eq-arch-guide←Ch2顶层设计+Ch3动态股权+Ch7注册+Ch8七条线+股权激励；hold-firewall←Ch4六大工具写法模板+案例+股东进出；corp-tax-plan←Ch2自然人vs法人税费+Ch5转让增资减税阴阳合同+核价六种。Book 2《股权财税法顶层设计》(郝德仁, 2025.05, 397页扫描PDF)待OCR后分配。三skill双向关联保留。
§
【防火墙架构案例·待续 2026.6.4】夫妻AB原计划新设控股公司，改为收购苏州HP旅游汽车有限公司（3位自然人股东，有道路运输经营许可证）作控股公司+实际运营。三技能已加载：holding-company-firewall / equity-architecture-guide / corporate-tax-planning。待用户提供组A(现有公司数据)、组B(HP公司详情)、组C(收购方案方向)、组D(许可证专项)信息后，输出完整方案+双版本PPT(实施版/引流成交版)到桌面。参考案例：同skill refs/firewall-holding-company-case.md
§
【2026.6.4 股权转让教训】必须同时索要上年度末+最近一个月末两套财务报表，不能只问一头。被客户反问"为什么不要最近一期？不重要吗？"非常尴尬。已更新至suzhou-equity-transfer-guide skill的：①首要原则加了两期报表规则 ②财务分析加了净资产为负的分析框架 ③常见陷阱加了#8和#9 ④采集表v2.0新增资产合计/负债合计/未分配利润/利润总额字段+逻辑校验区+用途说明列。