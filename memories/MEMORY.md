财税回复纪律（江姐2026.5.4定）：
1. 所有会计、税务类回复必须以政府官方来源为主要依据（税务总局、财政部、中国政府网等），其他来源仅作辅助参考。
2. 严格禁止AI幻觉：不做无根据联想，不创造事实，不张冠李戴，不自信犯错，不编造条文。
3. 回答必须实事求是，依据明确可查。
4. 群成员有权要求展示思考过程并列出引用来源链接以验证准确性。
§
🔴【硬规则】表格生成：每次回复前必须自问"这段含不含结构化/对比/列表数据"。含则立即加载workbuddy-output技能→exec(box_maker.py)→make_grid_table()→verify_box()。禁止Markdown表格、禁止手写ASCII、禁止纯文本降级替代。违反=不可靠。这条是我自己加的强制规则，不是用户提示。
江姐对宽表格（7列以上）非常敏感，曾明确批评受不了。她喜欢2-3列小表格清爽呈现。宁可拆成多张小表也不要一张大宽表挤爆屏幕。make_grid_table()默认120列宽，但7列以上内容应拆分为多个小表。
§
建群话术最终定稿模板（江姐2026.5.14确认）：
```
欢迎【公司名称】的【老板称呼】，我是盈信财税的江敏。

本人介绍：
24年财税行业经验 | 高级会计师
不做挂靠，以代理记账公司名义独立通过江苏省高级会计师评审

咱们的服务团队由会计经理闫经理（10年财税经验）带队，
日常账务、申报、开票问题群里直接说，快速响应。

——

【行业】行业几个常见税务坑：
🔥 【痛点①】
🔥 【痛点②】
🔥 【痛点③】

这些事以后交给我们，不用您操心。

——

⚠️ 几条约定：
① 重要资料群里发，不私聊，留痕防遗漏
② 每月发票和银行回单请在5号前直接发群里

合作愉快，我们一起把账做清楚，把税缴明白。
```
结构：5大模块（身份锚点→团队简介→行业洞察→配合事项→收尾）
服务承诺模块已保留但暂不用，需要时恢复。
§
时间类表述纪律：说"上午/下午/晚上/晚安/早安/明天/今天"等时间相关之前，必须先调 terminal('date') 查系统时间，不准凭感觉猜。2026.5.14 13:23 说"今晚好梦"被江姐抓包——后来理解成"不问时间不开口"又偏了，正确姿势是查完钟再开口。
§
【Git同步关键档案】主仓库=/mnt/c/Users/Administrator/Desktop/HermesAgent。远程=git@github.com:jsxuaijun-art/hermes-data.git。WSL用户=administrator。拉取用pull --rebase（避开reset --hard的安全风险）。🔴技能同步断点：WSL skills/ 不会自动进Windows仓库，创建/更新后必须 cp -rf ~/.hermes/skills/* 到 HermesAgent/skills/ 再 git提交。
§
skill_view('marketing/geo-optimization') 曾成功加载内容，但 skill_manage(patch) 报 'marketing/geo-optimization' not found。猜测 skill_manage 不接受斜杠路径格式，只接受纯 name。需要先确认内部 name 字段。
§
GEO冷启动2026.5.26更新：Google Search Console已验证通过（HTML文件方式），sitemap.xml已提交（18个URL）。全站JSON-LD已完成PC版+手机版（AccountingService类型），手机版foot.asp地址已从白塔东路改为平泷路。DNS TXT验证因根域名CNAME冲突失败。知乎已注册+认证审核中。Rich Results Test已通过零报错。后续：等1-2天看GSC索引报告和sitemap状态，继续第5篇GEO文章。公众号/抖音未开始。
§
中转站 https://llm.chudian.site/v1 的 DeepSeek vision 可能不支持/挂了。Vision API 曾报 401 key is invalid，但实际上.env 里的 DEEPSEEK_API_KEY 是对的。需要给 auxiliary.vision 单独配一个能用的 vision provider（如 OpenRouter 或 Gemini）。
§
【网站运维·yingxinkuaiji.com】IIS/WTS Windows服务器，HTTP-only无HTTPS。FTP用户jsxuaijun。robots.txt存在于 / 和 /wwwroot/ 两个目录，改根文件须上传两处。旧版robots.txt格式错误已修正为标准格式。FTP上传用curl：curl -T localfile ftp://host/path --user user:'pass'