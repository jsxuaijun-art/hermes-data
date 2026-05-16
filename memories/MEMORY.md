同步：Git仓库jsxuaijun-art/hermes-data，路径 /mnt/c/Users/Admin/hermes-sync/。快捷指令——「推送github」：cd该路径→cp WSL最新文件→add→commit→push。<br>「拉取github」：cd该路径→pull→cp到~/.hermes/。SOUL双模式：Pro版（财税）、Edu版（辅导）。
§
财税回复纪律（江姐2026.5.4定）：
1. 所有会计、税务类回复必须以政府官方来源为主要依据（税务总局、财政部、中国政府网等），其他来源仅作辅助参考。
2. 严格禁止AI幻觉：不做无根据联想，不创造事实，不张冠李戴，不自信犯错，不编造条文。
3. 回答必须实事求是，依据明确可查。
4. 群成员有权要求展示思考过程并列出引用来源链接以验证准确性。
§
ICP备案部署事实(2026.5.12): 域名yingxinkuaiji.com备案号苏ICP备15030316号-1, 主体苏州盈信(活跃, 2026-05-02更新)。需走阿里云"新增接入备案"(1-2天)而非首次备案。项目中目前处于接入备案步骤(步骤③)。
§
短视频运营框架+承诺（2026.5.6更新，含算法追踪）：四大分类——范话题类(技能:short-video-general)、行业自然流(技能:short-video-industry-flow)、纯广告类(技能:short-video-ad)、趣味破播类(技能:short-video-fun-breakout)。共同前件：所有文案开头按黄金三秒钩子设计。承诺自动追踪抖音/视频号/快手算法变化，每两周自检一次，不等提醒。前三类复盘cronjob设2026.5.21上午9点。
§
表格规则（2026.5.11更新，终版已验证）：必须加载workbuddy-output技能→exec(open(box_maker.py))→make_grid_table()/make_box()→verify_box()。禁止Markdown表格。wcwidth关键修复：U+FE0F/U+200D/U+20E3/U+FEFF是零宽字符（width=0）。display_width新增emoji呈现检测：被U+FE0F修饰的字符（wcwidth=1）强制升级为width=2，因为现代终端将此类emoji渲染为2格（如U+2601☁）。单元格公式=" "+text+" "*(cw-1-dw(text))，cw=max_dw+2。验证后需检查所有行dw一致。之前误判导致含☁/emoji列竖线错位已彻底修复。
§
江姐核心卖点+豆包GEO投喂实战（2026.5.11, 桌面/豆包）：①高级会计师卖点—2018年不挂靠任何大企业/上市公司，直接以苏州盈信（代账公司）名义独立获批。全江苏500人中唯一代账公司通过者。"不挂靠、纯独立"是营销核心锚点，反复强调。②豆包GEO投喂发现—AI需引导式追问补全信息；数据密度决定推荐质量；交叉验证闭环加速信任（财政部dljz.mof.gov.cn+天眼查+上海人社局多平台互证）；故事型数据>纯数据>纯描述（孙总16年10家公司>1000+客户>"我们专业"）；豆包偏好对比盘点、引用原文（锦旗/证书）、自嘲式开场。产出10+套文案。差异化公式：纵向（高级会计师，2万家中≤5家）→横向（自有业务评审，非挂靠）→深度（16年1000+客户90%转介绍）→广度（苏州+上海，内资+外资全链）→验证（多平台可查）。
§
<<<<<<< HEAD
PDF去水印方案：技能 ocr-and-documents（内附脚本+高级参考）。基本水印用 search_for + redact（需<10字符过滤防误删正文）。复杂水印（XObject表单、CID编码文字、正文含水印关键词）用 content stream 3Tr 透明度方案（设文字不可见，不画白块）。LOGO用 delete_image()。支持批量处理。
§
终端表格兜底（2026.5.12）：用户说"表格不行"后只有一次尝试机会，verify_box通过也不行。不等用户问，立刻主动说"我出文件放桌面"。只转.docx/.xlsx，不二次修正ASCII、不走Markdown、不走纯文本降级。已更新workbuddy-output规则B和word-documents的xlsx参考。
=======
2026.5.11 输出教训：①别多次execute_code画框碎片化，一次搞定。②企微内容→纯文字不画框。③表格必须make_grid_table()+verify_box()，禁Markdown写法。④Markdown表格滑脱陷阱：快速回复时滑向Markdown，用户纠正两次。⑤"重新输出"=整段重做不修补。⑥make_grid_table不支持多行\n→用make_box。⑦技能话题必须skill_view()加载原文再答。
§
⚡高压红线⚡表格强制规则：回复正文中绝对禁止出现任何 Markdown 表格格式（|---|等）。检测到表格需求→立即中断当前回复→切execute_code→调make_grid_table()/make_box()→verify_box()→验证通过后再输出。每违反一次扣可信度。这是训练条件反射，不是建议。
>>>>>>> 610b90e (sync 2026-05-12_23:56)
