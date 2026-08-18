# hermes-diag 实例配方（注销清税诊断 Web 应用）

2026-08 实测验证的实例级细节。类级方法见 SKILL.md。

## 实例拓扑速查

| 项 | 值 |
|---|---|
| 生产目录 | /opt/hermes-data-app（阿里云 47.103.27.171） |
| 本机开发目录 | ~/hermes-data-app（WSL） |
| 服务 | hermes-diag.service（venv 同目录，端口 8000，HOST 0.0.0.0） |
| 入口 | https://47.103.27.171/diag/（nginx hermes-gateway 站点 443 块 `location /diag/` → 127.0.0.1:8000/） |
| 登录 | Basic Auth diag / yingxin2026（/etc/nginx/ssl/ 旁 htpasswd，openssl apr1 生成） |
| 企微群 webhook key | 6519fbd7-05ce-4faf-a253-8975aa35361d（群机器人，markdown 推送） |
| 引擎双拷贝 | /opt/hermes-data-app/qingshui_risk_engine.py ↔ ~/.hermes/skills/tax-planning/company-deregistration/scripts/qingshui_risk_engine.py |

## 表单字段约定（2026-08 现行）

- 文件：`<input name="files" multiple>`（拖拽 dropzone id=dropzone，DataTransfer 合并；**每文件行带「✕ 删除」按钮**，JS 用 `new DataTransfer()` 重建 input.files 后 re-render）
- **无公司名输入框**（用户 2026-08 明确不要；主体信息从报表识别）
- 股东动态行：`sh_name` / `sh_ratio` / `sh_capital` / `sh_paid`（认缴出资/实缴额 万元；getlist 按 index 对齐；JS addSh() 加行、✕ 删行）
- 文件分流：仅 .xlsx/.xls 进解析；其他（情况说明.txt/pdf 等）作附件，docx 出「上传附件」段 + 结果页 📎 列表
- 报告「股东及出资信息」段：gen_docx(findings, total_assets, report_path, tax, shareholders=..., attachments=...)

## 本地测试脚本模式（部署前必跑）

```python
# 造多文件：科目余额表 + 资产负债表（openpyxl 现场生成）+ 一个情况说明.txt 附件
s = requests.Session()
r = s.post("http://127.0.0.1:5000/diagnose",
    files=[('files', ('测试科目余额表.xlsx', f1, MIME)),
           ('files', ('测试资产负债表.xlsx', f2, MIME)),
           ('files', ('情况说明.txt', f3, 'text/plain'))],
    data={'sh_name':['张三','李四'],'sh_ratio':['60','40'],
          'sh_capital':['600','400'],'sh_paid':['600','0']})
assert r.status_code == 200
assert '张三' in r.text and '实缴 600 万元' in r.text and '情况说明.txt' in r.text
dl = re.search(r'download/([^"\\']+)', r.text)
r2 = s.get("http://127.0.0.1:5000/download/" + dl.group(1))
assert r2.content[:2] == b'PK'
import docx
txt = '\n'.join(p.text for p in docx.Document(io.BytesIO(r2.content)).paragraphs)
assert '股东：张三' in txt and '实缴 600 万元' in txt and '上传附件' in txt and '情况说明.txt' in txt
```

## 公网验证（部署后）

```python
s = requests.Session(); s.verify = False; s.auth = ('diag','yingxin2026')
BASE = "https://47.103.27.171/diag"
# 首页字段齐全 + 上传 + 结果页 + 下载 docx 解析断言（同上模式）
```

## 企微群推送模式

```python
requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={KEY}",
    json={"msgtype":"markdown","markdown":{"content":"🆕 **升级说明**\n\n- 新功能...\n- 地址 https://47.103.27.171/diag/ · 账号 `diag` 密码 `yingxin2026`"}})
# 返回 {"errcode":0,"errmsg":"ok"} 即成功
```

## 上线命令

```bash
scp app.py qingshui_risk_engine.py root@47.103.27.171:/opt/hermes-data-app/
scp templates/* root@47.103.27.171:/opt/hermes-data-app/templates/
ssh root@47.103.27.171 'systemctl restart hermes-diag.service && sleep 4 && systemctl is-active hermes-diag.service'
cp qingshui_risk_engine.py ~/.hermes/skills/tax-planning/company-deregistration/scripts/   # 同步 skill 侧
```

## 已踩过的坑（实例级）

- 生产模板不生效：Flask 模板缓存 → 已设 TEMPLATES_AUTO_RELOAD=True，改模板免重启；改 app.py 必须 restart。
- nginx auth 不生效：sites-enabled 残留 `hermes-gateway.bak.diag` 备份与正式配置 conflict，旧块（无 auth）抢流量 → `ls /etc/nginx/sites-enabled/` 移出备份再 `nginx -t && systemctl reload nginx`。
- 中文文件名被 secure_filename 剥掉扩展名 → uuid+原扩展名保存（2026-08 初版 bug，已修）。
- 生成 docx 被 Word 打开锁死无法覆盖 → 换新文件名（-更新版/v2）或让用户关闭 Word。
