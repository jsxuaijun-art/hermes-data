---
name: flask-report-webapp-dev
description: Use when 开发/维护报表上传→诊断→docx下载类 Flask 网页应用：多文件、中文名、动态表单、部署验证。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [flask, webapp, upload, docx, deploy, wecom]
    related_skills: [aliyun-hermes-server, company-deregistration]
---

# Flask 报表上传诊断网页应用 开发/维护

面向用户的「上传财务报表 → 自动诊断 → 生成/下载 Word 报告」类工具型 Flask 应用。典型实例：**hermes-diag 注销清税诊断工具**（阿里云 47.103.27.171 /diag/，供不会 Hermes 的同事使用）。这类应用用户会持续加功能，每次迭代都要走同一套方法。

## When to Use

- 用户对这类网页应用提需求：多文件上传、补充信息字段、报告内容增改、登录/部署改动
- 报表上传类应用出现中文文件名/多文件/表单字段不生效的问题
- 需要把引擎（诊断/报告脚本）在网页与 Hermes skill 两侧保持一致

## 架构心智（该类应用骨架）

```
web-app-dir/            # 如 /opt/hermes-data-app（生产）/ ~/hermes-data-app（本机开发）
├── app.py              # Flask 路由 + 上传/表单解析 + 调引擎生成报告
├── qingshui_risk_engine.py   # 报表解析+诊断+docx 引擎（从 Hermes skill 拷贝来的副本）
├── templates/          # index.html（上传+表单）/ result.html（诊断结果+下载）
└── venv/               # flask + openpyxl + xlrd + python-docx
```

**引擎双拷贝同步铁律**：引擎脚本在 web 应用目录和 Hermes skill 目录（如 company-deregistration/scripts/）各有一份拷贝。改任何一边必须 `cp` 同步另一边，否则网页与 Hermes 侧行为分叉。引擎改公共函数（如 gen_docx）时用**向后兼容参数**（`shareholders=None, company=None`），旧调用不受影响。注意：用户自有的 skill 只允许 cp 覆盖引擎文件，不得改其 SKILL.md。

## 多文件上传

- 前端：`<input type="file" multiple>` + 拖拽 dropzone（`dataTransfer.files` 合并进 `input.files` 用 `new DataTransfer()` 累积）；提示文字写明「可一次选/拖入多个（按住 Ctrl 多选）」。
- 单个删除：文件列表每行加「✕ 删除」按钮，JS 用 `new DataTransfer()` 重建 `input.files`（排除该 index）再 `render()`——上传错了随时可删，无需清空重选。
- 后端：`request.files.getlist('files')` 循环保存；**文件保存用 `uuid + 原扩展名`**（`os.path.splitext(f.filename)[1]`），绝不 `secure_filename()`——它会剥掉中文名导致文件无扩展名、openpyxl 认不出格式。
- 分类解析：按原文件名关键词分流（"科目余额表"→parse_subject_balance；"资产负债表"/"利润表"→parse_bs_and_pl）；无法分类的文件也尝试解析兜底。

## 动态行表单（补充信息）

- 前端：一行一个模板（`sh_name`/`sh_ratio`/`sh_capital`/`sh_paid`），JS `＋添加股东` 按钮 `document.createElement` 动态加行、行内 ✕ 按钮删除。placeholder 用「认缴出资 / 实缴额」区分两个金额。
- 后端：`request.form.getlist('sh_name')` 等按 index 对齐，跳过空姓名，组装 list[dict] 传给引擎和 result 模板。
- 报告：gen_docx 增加「股东及出资信息」段（每股东 姓名/持股%/认缴/实缴）。**用户明确不要表单收集公司名**（主体信息从报表识别即可），不要自作主张加公司名输入框。

## 附件文件（情况说明等非报表佐证）

- 同事常上传「情况说明」等佐证文件，应允许上传并附进报告。
- 后端 `_is_report()` 分流：仅 .xlsx/.xls 进解析；其余（pdf/docx/txt/图片）**不解析**，保存为附件并把文件名列表传入引擎。
- 引擎 gen_docx 加「上传附件」段列出文件名；result 页 summary 显示 📎 附件列表。

## 子路径部署 + 登录

- 挂在 nginx 子路径（如 /diag/）下时，模板里表单/下载/返回链接**必须相对路径**（`action="diagnose"`、`href="download/xxx"`、`href="./"`），绝对路径会绕开前缀 404。
- Flask 生产默认缓存模板：`app.config['TEMPLATES_AUTO_RELOAD']=True` 后改模板免重启；改 app.py 必须重启 systemd 服务。
- 登录用 nginx `auth_basic`（openssl apr1 生成密码文件，用户名 diag/密码如 yingxin2026）；验证时无密码必须 401、有密码 200。**改完确认生效的 server 块真被加载**——sites-enabled 里残留的 .bak 备份文件会 conflict 抢走请求（见 Pitfalls）。

## 本地测试 → 上线 → 验证 → 通知 循环

1. **本地改**：本机开发目录改 app.py/templates/引擎。
2. **本地测**：`PORT=5000 venv/bin/python app.py` 起服务；requests 发多文件+表单字段（`files=[('files',(中文名, fh, mime)), ...]`、`data={'sh_name':[...],'sh_paid':[...]}`），断言：状态 200、结果页含股东/附件、下载的 docx `PK` 开头且 python-docx 读段落含「股东及出资信息」「上传附件」等关键词。测完 kill。
3. **同步引擎**：`cp` 引擎到 Hermes skill 对应目录。
4. **上线**：scp app.py/引擎/templates 到服务器 → `systemctl restart hermes-diag.service` → `systemctl is-active` 确认 active。
5. **公网验证**：`requests` 带 `s.verify=False` + Basic Auth 走 https 全流程（首页含新字段 → 上传 → 结果页 → 下载报告解析断言）。服务器本机验证用 http://localhost:8000 即可。
6. **通知同事**：企微群 webhook 推 markdown 说明（`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=<KEY>`，`errcode:0` 即成功），写清新功能 + 地址 + 登录账号密码。

## Pitfalls

- **中文文件名**：上传文件保存必须 uuid+原扩展名，secure_filename 会剥中文。
- **模板缓存**：生产改模板不生效=缓存。已设 TEMPLATES_AUTO_RELOAD 则免重启；改 app.py 必须重启服务。
- **nginx 残留备份抢流量**：sites-enabled 里 `.bak`/备份文件会与正式配置 conflict，旧配置（无 auth/无反代）可能接管请求。验证行为不对时先 `ls /etc/nginx/sites-enabled/` 把备份移出再 reload。
- **安全闸拦截**：SSH 重启生产服务、`git push` 推送 GitHub 等写操作都可能触发安全闸等待用户确认，超时即整条命令 BLOCK。**把 commit+push 拆成独立步骤、先征得用户同意再执行**，别把多步操作链成一条长命令（一条超时全部作废，还看不到进度）。
- **Word 文件锁**：生成的 docx 被 Word 打开时无法覆盖/删除——换新文件名或请用户关闭 Word。
- **引擎分叉**：改引擎只改了一边拷贝，网页与 Hermes 诊断结果不一致。改完立刻 cp 同步。

## Verification

- 本地 + 公网两轮 requests 断言（多文件、表单字段、结果页、docx 段落关键词）。
- 服务 active、nginx auth 401/200 行为正确、企微群推送 errcode 0。
- 引擎两侧用 `search_files` 查关键参数确认一致（如 `shareholders=None` 两边都 ≥1 处）。

## 关联

- 服务器拓扑/nginx/systemd 服务细节 → `aliyun-hermes-server`（用户自有，只读）
- 本类应用的具体实例配方（hermes-diag 文件级细节、完整验证脚本模式）→ `references/hermes-diag-app-dev.md`
