---
name: wechat-qa-publish
description: 公众号文章发布后质量检查 + 替换已发布文章的标准流程。充当 wechat-publish skill 的 QA 互补技能。专门处理"发布后才发现问题"的补救场景。
version: 1.0.0
author: Hermes Agent (for 江敏/盈信税务)
created: 2026-07-27
---

## 触发场景

- 用户说"文章在手机上表格显示不全"
- 用户说"文章已发布但需要修改"
- 用户说"替换/重新发布这篇文章"
- 任何发布后要求修正的问题
- 你完成 publish 后，主动触发此技能进行质量检查

## 排版风格2选1验证（2026.8.10 新增 — 江姐纠正）

**发布前必须询问用户选择排版风格，不得默认 01 直接发布。** 江姐 2026.8.10 纠正：*"公众号文章为什么不让我选择哪种排版格式，有01和02两种"*。

- 两种风格（服务器 `/etc/wenyan/themes/`）：
  - **01 安信伯君**（`01-anxinbojun.css`）— 红底色，标题纯加粗，关键段红色强调，传统财税风格
  - **02 刘润**（`02-liurun-honglan.css`）— 15px正文·1.75行高·不首行缩进靠段距·**红#FF2941 / 蓝#0052FF 双色强调**，更现代有设计感
- 发布前检查清单：
  - [ ] 是否向用户出示了 01/02 两种风格选择？（不得跳过直接发）
  - [ ] 用户选定后，publish 命令的 `-c` 参数指向对应 css（`/etc/wenyan/themes/01-anxinbojun.css` 或 `02-liurun-honglan.css`）
- 数据冲击型文章（罚单金额、百分比对比）建议推荐 02 — 红蓝撞色能把重点数字更突出
- ⚠️ **02 风格的颜色配合**：02 是红#FF2941/蓝#0052FF 双色体系，内文若全部用默认红 #CC0000 会浪费撞色效果。用 02 时应：核心冲击数字（金额/罚单/百分比）用红 #FF2941，对比/背景数字（基数/比例）用蓝 #0052FF，让撞色真正发挥。若用户未指定，发布前可主动提议是否做双色优化
- `wechat-publish` 主技能为手动创建不可修改，故此硬要求由本 QA 技能承载并在每次发文时像其他清单项一样强制检查

## 交付路径铁律（2026.8.10 新增 — 江姐纠正）

**交付物（docx/文档/脚本）一律放桌面 `C:\Users\Admin\Desktop\`（WSL: /mnt/c/Users/Admin/Desktop/）。**

- ⚠️ **禁止用 `D:\360MoveData\Users\Admin\Desktop\` 作为交付路径** — 那是360迁移工具的旧桌面备份目录，不是江姐的真实桌面（江姐原话："没有 D:\360MoveData\，这个你要记住，不要再犯这个错误"）
- 用户给的素材（视频/图片）可能来自 `D:\360MoveData\...`，但**交付物**必须走 C 盘桌面
- 若误存到错误路径：`cp` 复制到 `/mnt/c/Users/Admin/Desktop/` 后 `rm` 删除误存文件

## 标题3选1验证（2026.8.5 新增 — 用户硬要求）

**出稿环节必须一次性给用户 3 个标题候选供其选择，不得只给 1 个。** 江姐 2026.8.5 明确要求：*"关于标题，以后你要创作出三个标题供我选择。"*

- 这是**所有文章/内容**的通用纪律（不只视频分支），在定稿发布前必须验证：
  - [ ] 出稿预览时是否并列给出了 **标题1 / 标题2 / 标题3**？
  - [ ] 三个标题是否覆盖不同角度（如 热点借势型 / 数据冲击型 / 焦虑驱动型）？
  - [ ] 是否含提问式/悬念式标题（江姐偏好，如「税局是怎么发现的？」）？
  - [ ] 用户**选定**后，才以该标题定稿发布（未选定不得直接发布）
- 若发布前的稿件只有 1 个标题 → 打回补 3 个候选
- `wechat-publish` 主技能为手动创建不可修改，故此硬要求由本 QA 技能承载并在每次发文时像其他清单项一样强制检查

## 封面/素材重复验证（2026.8.5 新增 — 用户踩过的坑）

用户曾明确不满：**"封面图你又重复使用旧的图，不应该啊。"** 根因是依赖 Unsplash 图库 + 无法识图判断是否和历史重复。

**硬规则：封面图、数字横幅等素材一律用 `wechat-publish/scripts/generate_assets.py` 代码原创生成（100% 不重复），禁止依赖 Unsplash。** 发布前 QA 必须验证：

- [ ] 封面是否为代码原创生成（非 Unsplash 下载图）？
- [ ] 数字横幅是否用 `generate_banner()` 按需生成（01-06 之外的 07/08/09/10 等任意数字都可自制作，不需用户上传）？
- [ ] 若手动上传了图片 → 登录服务器 `md5sum /var/www/html/images/cover_*.jpg` 对比历史封面 MD5，确认无重复？
- [ ] 生成横幅用的字体：中文必须用 CJK 字体（微软雅黑 `msyhbd.ttc` / 文泉驿 wqy-zenhei），用 PIL 默认 DejaVu 画中文会变「豆腐块方框」——若有则重绘

> 注：素材生成方法细则在 `wechat-publish` 主技能「素材自生成能力」一节；本 QA 技能负责验证这些铁律被遵守。

## 手机端预览验证清单（发布后拦截）

用户审核前，必须用手机微信打开预览，逐项检查：

| 检查项 | 通过标准 | 常见问题 |
|:-------|:---------|:---------|
| **3列以上表格** | 左右滑动流畅，各列文字完整 | 右列被截断 → 用 `div overflow-x: auto` 包裹整个表格（2026.8.12 实测通过，写法见下） |
| **2列表格** | 正常显示，无换行错位 | 无特别处理需求 |
| **GEO段落** | 楷体字号正确，分隔线显示 | 字号/字体异常 |
| **配图** | 所有图正常加载，无白块 | 路径错误 → 检查服务器文件 |
| **公司电话** | 数字正确，可点按拨号 | 错号/漏号 |
| **颜色标记** | 红色 #CC0000 正常渲染；02风格下红#FF2941/蓝#0052FF 双色正常 | 颜色代码错误 |
| **品牌落款** | 苏州盈信企业管理有限公司，服务顺序正确 | 公司名或顺序错 |

## 3列以上表格的滑动容器写法（2026.8.12 实测通过）

用户反馈"表格不能左右滑动、最右列显示不全"时，用 `<div>` 包裹整个 markdown 表格：

```markdown
**对比标题：**

<div style="overflow-x: auto; -webkit-overflow-scrolling: touch;">

| 对比项 | 主动补 | 被查实 |
|---|---|---|
| 税款 | 补 | 补 |
| 后果 | 到此为止 | 信用降D级，严重的移送公安 |

</div>
```

要点：
- `<div>` 开闭标签与表格之间各留一个**空行**（wenyan 渲染需要），表格本身的 markdown 语法不动
- 表格内的 `<span style="color:...">` 彩色标记可原样保留，不受影响
- 2列表格无需此处理
- 修正后用 `grep -c 'overflow-x: auto'` 验证容器数量正确

## 替换已发布文章的标准流程

### 场景
文章已发布到草稿箱/已群发后需要修改内容（表格修复、配图更换、文案修正、颜色修改等）。

### 步骤

1. **修正源文件**
   - 定位问题处的 markdown 源码
   - 修正（如表格加滑动容器、换配图、改文案等）

2. **重新 publish（⚠️ 2026.8.12 实测：wenyan CLI 只在服务器上，本机没有）**
   - 本机跑 publish 会报 `Cannot find module '/usr/lib/node_modules/@wenyan-md/cli/dist/cli.js'` — CLI 只装在服务器（node v24），必须 **markdown 先 rsync 到服务器，再 ssh 上去执行**
   - 获得**新的 Media ID**（wenyan 不接受覆盖，每次产生新 ID）
   ```bash
   # 本机：清残留代理（172.23.96.1:7890 会拖死 scp/ssh 传输）+ rsync 传 md
   unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
   rsync -av --timeout=20 -e "ssh -o ConnectTimeout=10" /tmp/article.md root@47.103.27.171:/tmp/article.md
   # 服务器上执行 publish（-c 用 /etc/wenyan/themes/ 下的主题 css）
   ssh -o ConnectTimeout=15 root@47.103.27.171 'cd /tmp && NODE_OPTIONS="--experimental-require-module" node /usr/lib/node_modules/@wenyan-md/cli/dist/cli.js publish -f /tmp/article.md --server http://127.0.0.1:3000 -c /etc/wenyan/themes/02-liurun-honglan.css 2>&1 | tail -30'
   ```
   - 成功标志：`发布成功，Media ID: <40位base64>`；根路径 GET 127.0.0.1:3000 返回 404 是正常的，别误判服务挂了
   - 完整发布链路 + 02 红蓝撞色 recolor 配方见 `dual-model-content-pipeline/references/wenyan-publish-ops.md`

3. **同步更新配图（如有）**
   - 上传新配图到服务器 `/var/www/html/images/`
   - 确保旧版配图 md5 不同

4. **知会用户**
   - 明确告知：旧 ID（已废弃）+ 新 ID（替换用）
   - 让用户：公众号后台 → 草稿箱 → 删旧草稿 → 用新 ID 拉新草稿 → 重新审核发布

5. **更新 skill 记录**
   - 更新 `references/` 下参考文件中的 Media ID
   - 源参考文件如有修正，同步更新

6. **同步到 GitHub**
   - 推送更新后的 skill 文件和参考文件
   - commit 信息结尾标注日期（如 `sync: fix table scroll 2026-07-27`）

## 与 wechat-publish 的关系

- `wechat-publish` 负责**发文前**的全流程（写作→配图→publish）
- `wechat-qa-publish` 负责**发文后**的验收与补救（检查→替换→修复）
- 两者互补，写作流程主技能不可被 **curator** 修改时，次技能承接 QA 职责
- ⚠️ **2026.8.12 实测：agent 侧 `skill_manage patch` 可以直接修改 wechat-publish 主技能**（本次会话成功把 GEO 段落「上海知名大学」patch 为「上海交通大学」，diff 确认生效）。"不可修改"仅限 curator 自动 patch；agent 主动修正主技能固定文案（GEO 落款、学历表述等）是可行的，且应优先直接改主技能源头，避免下次发文又带出旧文案
