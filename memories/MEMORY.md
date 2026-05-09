设备：家里电脑 + 办公室电脑 + 笔记本 + 江敏笔记本（共4台），全部安装 Hermes Agent 和 WordBuddy，通过 GitHub 仓库 hermes-data 同步数据
§
Tirith security scanner binary installed at ~/.hermes/bin/tirith, config updated to use absolute path. Downloaded v0.3.0 from sheeki03/tirith GitHub releases. Also patched prompt_toolkit application.py _handle_exception to check for running event loop before ensure_future() — fixes the "no current event loop" RuntimeError on shutdown.
§
Windows batch files (.bat) with non-ASCII characters (Chinese, box-drawing symbols, Unicode symbols) break on Chinese Windows systems when saved as UTF-8. Both UTF-8 without BOM AND with BOM can fail — BOM bytes get read as literal text (锘緻echo). The only reliable fix is to rewrite with pure ASCII only: English text, `=/-` for separators, `[OK]/[FAIL]/[INFO]` for status indicators. Applies to Hermes同步-拉取.bat and Hermes同步-推送.bat on all 4 machines.
§
江敏笔记本 WSL distro 名是 Ubuntu22.04（无短横线），不是 Ubuntu-22.04。Windows 上跑着代理 127.0.0.1:7890（Clash/同类工具）。Hermes 同步脚本在 C:\Users\jiangmin\Desktop\CLAW\ 下，已改为纯 ASCII + fetch/reset 策略避免合并冲突。
§
IMA OpenAPI skill 已安装 ~/.hermes/skills/ima-skill/，凭证存于 ~/.config/ima/client_id 和 api_key。Node.js v20.18.0 在 ~/.local/node/bin/node。API Base: https://ima.qq.com。Client ID: 2ee6c4f520af5d9f8499a1b30b096388。用户有 6 个知识库（徐爱军的知识库、销售学等）和 3 篇笔记（供应商洽谈记录、客户来访记录含1039贸易方式内容、ima笔记使用指南）。搜索已在 KB 和 Notes 中验证可用。注意：IMA 内容分 knowledge-base（文件）和 notes（笔记）两套存储，搜索需兜底两个模块。
§
所有表格输出必须使用 table-formatter 技能，全细线网格格式（┌┬┐│├┼┤└┴┘），横平竖直、左右对齐、每行有分隔线。绝对不用 Markdown 虚线表（|---|）。
§
table-formatter 技能已定型为最终版（全细线网格格式 ┌┬┐│├┼┤└┴┘），用户确认完美对齐。四台电脑命名已明确：1)江敏笔记本（Windows用户jiangmin，WSL Ubuntu22.04），2)办公室电脑（Windows用户Administrator，WSL Ubuntu 24.04.4），3)家里电脑，4)笔记本（待定）。所有电脑均通过 GitHub 仓库 hermes-data 双向同步，同步脚本已生成。
§
用户在企业微信群中建立了机器人，我之前帮他连接成功了。
§
企业微信群机器人已连接成功。Webhook Key: 339a62c0-c13b-4733-a706-6ce136a49fe6，当前工作模式为简单模式（直接发消息无需token）。Secret 备用: qCB8YuT6JSREfPAhV112EFk7D9XlCrCJ1Q4NFgidFy9。
§
企业微信 AI 机器人（双向）已配置完成。Bot ID: aibCgyqs_UpoYBfLGf0QejX1YCmKfW176cM, Secret 存在 .env 中。使用 WebSocket 模式（wecom）连接 wss://openws.work.weixin.qq.com。网关已启动并成功连接。注意：AI 机器人需要手动添加到群聊才能响应 @mention，不同于 Webhook 群机器人（单向推送）。用户无法扫码或打开手机链接，配置需后台手动操作。