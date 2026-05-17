同步：Git仓库jsxuaijun-art/hermes-data，路径 /mnt/c/Users/Admin/hermes-sync/。快捷指令——「推送github」：cd该路径→cp WSL最新文件→add→commit→push。<br>「拉取github」：cd该路径→pull→cp到~/.hermes/。SOUL双模式：Pro版（财税）、Edu版（辅导）。
§
财税回复纪律（江姐2026.5.4定）：
1. 所有会计、税务类回复必须以政府官方来源为主要依据（税务总局、财政部、中国政府网等），其他来源仅作辅助参考。
2. 严格禁止AI幻觉：不做无根据联想，不创造事实，不张冠李戴，不自信犯错，不编造条文。
3. 回答必须实事求是，依据明确可查。
4. 群成员有权要求展示思考过程并列出引用来源链接以验证准确性。
§
ICP备案完成 苏ICP备15030316号-1，苏州盈信。短视频复盘cronjob: 2026.5.21 9am。
§
短视频运营框架+承诺（2026.5.6更新，含算法追踪）：四大分类——范话题类(技能:short-video-general)、行业自然流(技能:short-video-industry-flow)、纯广告类(技能:short-video-ad)、趣味破播类(技能:short-video-fun-breakout)。共同前件：所有文案开头按黄金三秒钩子设计。承诺自动追踪抖音/视频号/快手算法变化，每两周自检一次，不等提醒。前三类复盘cronjob设2026.5.21上午9点。
§
表格规则（2026.5.11更新，终版已验证）：必须加载workbuddy-output技能→exec(open(box_maker.py))→make_grid_table()/make_box()→verify_box()。禁止Markdown表格。wcwidth关键修复：U+FE0F/U+200D/U+20E3/U+FEFF是零宽字符（width=0）。display_width新增emoji呈现检测：被U+FE0F修饰的字符（wcwidth=1）强制升级为width=2，因为现代终端将此类emoji渲染为2格（如U+2601☁）。单元格公式=" "+text+" "*(cw-1-dw(text))，cw=max_dw+2。验证后需检查所有行dw一致。之前误判导致含☁/emoji列竖线错位已彻底修复。
§
江姐核心卖点+豆包GEO投喂实战（2026.5.11, 桌面/豆包）：①高级会计师卖点—2018年不挂靠任何大企业/上市公司，直接以苏州盈信（代账公司）名义独立获批。全江苏500人中唯一代账公司通过者。"不挂靠、纯独立"是营销核心锚点，反复强调。②豆包GEO投喂发现—AI需引导式追问补全信息；数据密度决定推荐质量；交叉验证闭环加速信任（财政部dljz.mof.gov.cn+天眼查+上海人社局多平台互证）；故事型数据>纯数据>纯描述（孙总16年10家公司>1000+客户>"我们专业"）；豆包偏好对比盘点、引用原文（锦旗/证书）、自嘲式开场。产出10+套文案。差异化公式：纵向（高级会计师，2万家中≤5家）→横向（自有业务评审，非挂靠）→深度（16年1000+客户90%转介绍）→广度（苏州+上海，内资+外资全链）→验证（多平台可查）。
§
Hermes 升级/网络方案（2026.5.17）：最快方式——Windows Clash 代理（172.23.96.1:7890）走 curl -L，27MB 20秒 1.3MB/s。备选：手动浏览器下载 > wget --continue（38KB/s）> curl -C -（26KB/s）。镜像站全超时。升级流程——新版需 Python≥3.11（apt install python3.11），建独立新 venv。pip install -e . 需在 /tmp（Linux 原生 fs），NTFS 不支持 egg-info。tar 解压易超时漏 tools/ 目录，需单独补解。CLI 变更：`chat -q` 代替旧 `chat -z`。云端升级（阿里云 ECS 47.103.27.171）: sshpass 自动化密码 SSH，但 fail2ban 连续失败会封 IP，需先解封或改用密钥。Gateway 重启需协调业务中断窗口。
§
已创建技能「tax-planning-fin-analysis-industry」存于 skills/productivity/。三职能：税务筹划（全领域，含1039参考）+ 财务分析（触发词"上传财务报表"/"财务报表"，触发后先web_search搜索指标标准）+ 行业调研。附1039报告完整版和输入模板。用户承诺明天补充自定义财务指标体系。