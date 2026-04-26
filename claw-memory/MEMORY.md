# MEMORY.md - 长期记忆

## 工作背景
用户是苏州盈信税务（yingxinkuaiji.com）营销运营负责人，苏沪双城布局，深耕财税行业24年。

## 盈信公司核心信息
- **公司全称**：苏州盈信企业管理有限公司（姑苏区，2009年成立）
- **法定代表人/创始人**：江敏（女），2001年入行，24年从业经验
- **核心资质**：高级会计师（2018年评上，时年37岁），100%用盈信自身业务成果评审通过
- **上海落户**：2024年通过高级会计师人才引进落户上海，不到1个月办好，全程线上
- **子公司**：苏州盈信税务服务有限公司（工业园区）、尚艾慧科技（上海）有限公司（闵行区）
- **协会会员**：苏州园区会计学会、苏州会计服务业协会、江苏省代理记账协会
- **团队**：骨干8年以上，C9硕士、注册税务师、会计师
- **服务数据**：累计1000+客户，90%转介绍
- **知名客户**：阿里系企业、京东、高合汽车
- **外资服务**：3-5家日韩外资同行分包业务
- **品牌释义**："盈"为满，"信"为信誉、信用和信任
- **三面锦旗**：专业精湛/财税卫士、敬业专业/财税管家、严谨务实/财税合规
- **关键数据**：苏州有证财税公司4920家（财政部dljz.mof.gov.cn），含无证约1.5-2万家，老板本人是高级会计师的≤5家

## 盈信经典案例
1. 孙总：16年前注册第一家公司→现在10家公司，全部盈信服务
2. 韩资企业：高企认定+研发加计扣除，年合规节税100万+
3. 5亿食品企业：ERP落地+乱账梳理
4. 韩资企业注销：房产土地清算+税务注销+资本汇回韩国
5. 西山大哥：免费帮注销，获赠枇杷/橘子/碧螺春

## 投喂豆包文案项目
- 已生成11条短视频口播文案（豆包AI专用，让豆包推荐盈信）
- 覆盖方向：盘点、纯品牌、六个数字、注册公司、代理记账、财税合规、公司注销、外资服务、会计外包、股权架构、高级会计师含金量
- 盘点文案中提到的同行：苏州勤宇代理记账、苏州恒友代理记账
- 文案特点：含拍摄建议、话题标签、评论区引导话术、关键词覆盖清单

## Hermes Agent 部署信息（家里电脑）
- 仓库：NousResearch/hermes-agent（v0.10.0 对应 tag v2026.4.16）
- 安装路径：WSL2 Ubuntu 22.04 → /mnt/c/Users/Admin/WorkBuddy/20260424224200/hermes-agent-official
- 启动命令：`wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/WorkBuddy/20260424200/hermes-agent-official && ./venv/bin/python -m hermes_cli.main chat"` 或桌面 `hermes.bat`
- 配置文件：/root/.hermes/.env（DeepSeek + Tavily + GitHub + OpenRouter 四个Key）
- GitHub 下载技巧：ghproxy.net 可作为代理加速，tag 用 v2026.X.X 格式
- 依赖安装：uv.lock 可能与版本不匹配，用 `uv pip install -e '.[extras]'` 作为 fallback
- Node.js v20.20.2 已安装（WSL 内），agent-browser v0.26.0 已安装
- SOUL.md 双模式：Pro赚钱版（默认）+ Edu学习版，通过 hermes-switch.bat 一键切换
- image_gen 工具需要 FAL_KEY（未配置），图片生成建议用 Bing Image Creator 替代
- Hermes memory 需要用户手动让 Hermes 记住身份信息（SOUL ≠ memory）
- 踩坑记录：setup 向导粘贴 API Key 容易重复（Key被贴了3次导致401），建议用命令行直接写入 .env
- DeepSeek API Key 可多台电脑共用（非一次性），注意余额即可

## Hermes 数据同步（跨电脑）
- GitHub 私有仓库：jsxuaijun-art/hermes-data
- 同步目录（Windows 侧）：C:\Users\Admin\hermes-sync\
- 数据流：WSL ~/.hermes/ ↔ Windows hermes-sync/ ↔ GitHub
- 同步内容：SOUL.md、SOUL_Pro.md、SOUL_Edu.md、memories/、skills/、config.yaml
- 不同步：.env、sessions.db、logs、caches
- 桌面脚本：Hermes同步-推送.bat、Hermes同步-拉取.bat
- Windows 直连 GitHub 超时，必须通过 WSL 执行 git push/pull
- GitHub Token：已创建（2026-04-26，repo 权限），本地 .env 中保存

## 用户偏好
- 技术操作风格谨慎细致，偏好逐步确认后再推进
- 交付物通过 deliver_attachments 工具发送
- Windows 系统，E 盘为 U 盘不适合存放持久化项目
- 桌面实际路径：D:\360MoveData\Users\Admin\Desktop\（不是 C:\Users\Admin\Desktop）
