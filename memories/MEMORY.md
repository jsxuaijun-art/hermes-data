Tirith security scanner binary installed at ~/.hermes/bin/tirith, config updated to use absolute path. Downloaded v0.3.0 from sheeki03/tirith GitHub releases. Also patched prompt_toolkit application.py _handle_exception to check for running event loop before ensure_future() — fixes the "no current event loop" RuntimeError on shutdown.
§
Windows batch files (.bat) with non-ASCII characters (Chinese, box-drawing symbols, Unicode symbols) break on Chinese Windows systems when saved as UTF-8. Both UTF-8 without BOM AND with BOM can fail — BOM bytes get read as literal text (锘緻echo). The only reliable fix is to rewrite with pure ASCII only: English text, `=/-` for separators, `[OK]/[FAIL]/[INFO]` for status indicators. Applies to Hermes同步-拉取.bat and Hermes同步-推送.bat on all 4 machines.
§
江敏笔记本 WSL distro 名是 Ubuntu22.04（无短横线），不是 Ubuntu-22.04。Windows 上跑着代理 127.0.0.1:7890（Clash/同类工具）。Hermes 同步脚本在 C:\Users\jiangmin\Desktop\CLAW\ 下，已改为纯 ASCII + fetch/reset 策略避免合并冲突。
§
江敏笔记本（Windows 用户 jiangmin）的 Hermes 同步脚本已修复：
- 文件在 C:\Users\jiangmin\Desktop\CLAW\Hermes同步-拉取.bat 和 推送.bat
- 纯 ASCII 编码（无中文字符），Windows 侧跑 git，WSL 只负责 cp 文件
- WSL 发行版名称：Ubuntu22.04
- Windows 有代理 127.0.0.1:7890（Clash），git 在 Windows 侧跑所以代理生效
- Token 已保存在 hermes-sync/.git/credentials
- 仓库：jsxuaijun-art/hermes-data（脚本模板在 scripts/ 目录下）

还有 3 台电脑待配：家里电脑、办公室电脑、笔记本
- 每台需要修改：Windows 用户名、WSL 发行版名称、设备名
- 下次用户告知信息后生成对应脚本
§
Web search from WSL in China: cn.bing.com is the only major search engine that responds to automated requests. Google is unreachable (connection failed). Baidu returns captcha on curl/Python requests. DuckDuckGo lite returns no Chinese results. No proxy is configured in WSL environment variables (Windows proxy 127.0.0.1:7890 is Windows-only, unreachable from WSL). For Chinese video content, Bilibili HTML search works via curl (search.bilibili.com/all?keyword=...) — extract BV IDs from HTML, then look up titles via api.bilibili.com/x/web-interface/view?bvid=XXX. Bilibili API returns 412 Precondition Failed on direct Chinese keyword search.
§
用户（徐爱军/徐总）的公司团队介绍：
- 江姐：苏州本地人，高级会计师（苏州2万家同行不到5家有此资质）
- 徐总（徐爱军）：上海交通大学管理硕士
- 黎经理：注册税务师（CTA）
- 许经理：注册会计师（CPA）
用户让用这些事实写一段助理跟客户的对话，展示团队专业度，用于客户税务风险评估场景。