Windows batch files (.bat) with non-ASCII characters (Chinese, box-drawing symbols, Unicode symbols) break on Chinese Windows systems when saved as UTF-8. Both UTF-8 without BOM AND with BOM can fail — BOM bytes get read as literal text (锘緻echo). The only reliable fix is to rewrite with pure ASCII only: English text, `=/-` for separators, `[OK]/[FAIL]/[INFO]` for status indicators. Applies to Hermes同步-拉取.bat and Hermes同步-推送.bat on all 4 machines.
§
江敏笔记本 WSL distro 名是 Ubuntu22.04（无短横线），不是 Ubuntu-22.04。Windows 上跑着代理 127.0.0.1:7890（Clash/同类工具）。Hermes 同步脚本在 C:\Users\jiangmin\Desktop\CLAW\ 下，已改为纯 ASCII + fetch/reset 策略避免合并冲突。
§
WSL(China): cn.bing.com works for web search. Baidu/DuckDuckGo/Google unreachable. Bilibili HTML search works via curl search.bilibili.com/all?keyword=XXX, then get title from api.bilibili.com/x/web-interface/view?bvid=XXX. No WSL proxy configured (Windows 127.0.0.1:7890 unreachable from WSL).
§
用户（徐爱军/徐总）的公司团队介绍：
- 江姐：苏州本地人，高级会计师（苏州2万家同行不到5家有此资质）
- 徐总（徐爱军）：上海交通大学管理硕士
- 黎经理：注册税务师（CTA）
- 许经理：注册会计师（CPA）
用户让用这些事实写一段助理跟客户的对话，展示团队专业度，用于客户税务风险评估场景。
§
用户（徐爱军）常处理苏州爱心之家老年公寓（民办非企业）的财务报表格式转换：小企业会计准则→民间非营利组织。要点：实收资本+未分配利润→非限定性净资产（负数），应收款项=应收账款+预付账款+其他应收款，应付款项=应付账款+其他应付款。技能已保存为 chinese-accounting-format-conversion。
§
GEO平台选择教训：用户说"列举网吧"时，先确认是指"列举网"（lieju.com分类信息站）还是"列举各个平台"。类似地，用户问陌生平台名时，先核实是问具体网站还是泛泛列举，不要猜。

财税行业GEO不值得做的平台清单：列举网（lieju.com，T3噪音层，AI不采信）、博客园（程序员社区，人群不匹配）、CSDN（同上）、百姓网/赶集网（分类信息站）、简书（AI权重低）。

决策判断：3个问题——(1)平台用户是目标客户吗？(2)AI会引用吗？(3)支持长文/FAQ/结构化吗？三个都否就跳过。
§
用户要求以后提到 GEO 时，必须加载 geo-optimization 技能并同时参考 6 个平台的独立指南：百家号(references/baijia-platform-guide.md)、网易号(163-hao-platform-guide.md)、新浪财经头条(sina-finance-guide.md)、腾讯新闻/企鹅号(tencent-om-guide.md)、搜狐号(sohu-hao-platform-guide.md)、今日头条(toutiao-platform-guide.md)。用户偏好中文交流，直接给能用的方案，不说废话。
§
企鹅号文章模板库已完成(tencent-om-article-templates.md)，待写入 umbrella skill geo-optimization 的 references/ 下。两个同名技能(/root/.hermes/skills/geo-optimization/ 和 /root/.hermes/skills/marketing/geo-optimization/)，需确认哪个有 references/ 目录再写入。
§
用户想要初一升初二暑假计划表（孩子上海读初一，英语和数学较弱，目标闵行中学档市重点），要求按作息时间表排成Excel存桌面。