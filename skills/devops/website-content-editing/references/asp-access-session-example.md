# ASP + Access 网站内容修改 — 实战参考（2026.5 案例）

## 网站环境

- **类型**：经典 ASP + Access 数据库
- **数据库文件**：`website.mdb`（位于网站根目录）
- **内容存储表**：`a_info`（页面内容表）
- **关键字段**：
  - `a_id` — 主键（整数）
  - `s_name` — 页面/区块标题（文本，最长 100 中文字符）
  - `s_content` — 正文内容（长文本，带 HTML 标签）
  - `s_name1` — 关键词/keywords
  - `s_name2` — 描述/description
  - `s_photo_url` — 关联图片路径
  - `s_author` — 作者（部分行有值，部分为空）
  - `a_file_path` — 文件路径（部分行有值）
  - `d_update_time` — 更新时间
  - `a_visit_count` — 访问计数

## 案例 1：修改标题 + 关键词

**目标**：将关于我们页面中某个区块的标题从"盈信"改为"示范基地成员单位"，
并修改正文中的关键词。

**定位过程**：
1. 上传 `query.asp` → 执行 SELECT * FROM a_info → 发现 a_id 是主键
2. 通过逐条查看 `s_name` 定位到目标行
3. 确认 `s_name` 字段长度限制

## 案例 3：关于盈信页面双重关键词替换（2026.5 新增）

**目标**：将关于盈信页面（a_info id=1）第三段中两个关键词加粗显示：
- `苏州工业园区会计服务外包示范基地` → `苏州工业园区会计服务外包示范基地（苏州工业园区会计学会）` 加粗
- `省市行业协会会员` → `苏州会计服务协会和江苏省代理记帐协会会员` 加粗

**操作要点**：
- 通过 `rs.Open "SELECT s_content FROM a_info WHERE id=1", conn, 1, 3` 读取完整内容
- s_content 约 13000+ 字符 HTML，包含段落、图片、列表
- 用 VBScript `Replace()` 分别替换两处关键词：
```vb
newC = Replace(oldC, "苏州工业园区会计服务外包示范基地", _
    "<strong>苏州工业园区会计服务外包示范基地（苏州工业园区会计学会）</strong>")
newC = Replace(newC, "省市行业协会会员", _
    "<strong>苏州会计服务协会和江苏省代理记帐协会会员</strong>")
```
- 上传方式：用 Python `storbinary()` 传输 UTF-8 编码的 .asp 文件
- **一次更新两处**，分别加 `<strong>` 标签

**关键发现**：
- 长文本（13000+ 字符）字段用 RecordSet 方式读写安全，不走 SQL
- 多个 `Replace()` 链式调用可以一次完成全部修改
- 验证方式：HTTP 打开 about.asp 页面肉眼确认

## 案例 2：首页底部简介追加文字（2026.5 新增）

**目标**：首页（a_info id=4）底部简介最后一句前插入
"公司系苏州工业园区会计服务外包示范基地成员单位，资质可查。"

**操作要点**：
- 首页内容在 a_info.id=4（通过 index.asp 中 `db_content("a_info",4)` 确认）
- 约 6000+ 字符 HTML 内容，包含多层内联 `<span>` 标签
- 用 `Replace(oldC, "以上资质，欢迎您亲临查验", "新句子。以上资质，欢迎您亲临查验")` 插入
- 成功验证：HTTP 抓取确认 "示范基地" 出现在正确位置

**注意**：首页和"关于盈信"是不同的记录（id=4 是首页，id=1 是关于盈信）

## 页面 URL 参数映射

查看现有 ASP 源码（about.asp）发现参数命名不直观：

```asp
id = isid(kill_sql(rq("info")), 1)
```

- 实际 URL 参数是 `?info=` **不是** `?id=`
- 伪静态映射示例：`about.html` → `about.asp?info=1`，`about_40.html` → `about.asp?info=40`
- 函数 `isid()` 和 `kill_sql()` 定义在 `inc/conn.asp` 中

## 关于盈信页面（a_info id=1）完整记录

**s_name**：关于盈信（示范基地成员单位）
**s_name1**（keywords）：内资公司注册，工商登记，营业执照办理，工商注册，企业注册，公司注册,税务申报，代理记帐
**s_name2**（description）：（空）

**s_content 段落结构**：
1. 公司简介：成立2009年，创始人25年经验，阿里巴巴供应商，985/211专业团队
2. 核心背书：不挂靠，直接以代理记账公司名义获高级会计师资格
3. 资质说明：苏州财政局批准+示范基地成员单位+省市行业协会会员
4. 服务理念："四心"经营理念（诚心、专心、用心、齐心）
5. 品牌宣言：盈信释义，十七年品牌积淀

**已包含的关键资质文案**：
- 公司系苏州工业园区会计服务外包示范基地成员单位，资质可查
- 以上资质，欢迎您亲临查验
- 不逐一列出，欢迎莅临查证

## 常用 SQL（Access）

### 查看所有记录
```sql
SELECT id, s_name, s_order, s_type FROM a_info ORDER BY id
```

### 查看单条完整内容
```sql
SELECT * FROM a_info WHERE id=1
```

### 更新内容（追加/替换）
```asp
oldC = rs("s_content")
newC = Replace(oldC, "旧文字", "新文字")
rs("s_content") = newC
rs.Update()
```

## 临时脚本文件清单（执行后必须删除）

| 文件名 | 用途 | 必须删除？|
|--------|------|----------|
| `_list_a_info.asp` | 查询 all IDs + s_name | ✅ |
| `_about_id1.asp` | 查询 id=1 完整内容 | ✅ |
| `_about_full.asp` | 查询 id=1 s_content HTML | ✅ |
| `_update_home_intro.asp` | 修改首页 s_content | ✅ |
| `_verify_home.asp` | 验证修改结果 | ✅ |

## 注意点

1. `Replace()` 函数在 Access SQL 中区分大小写？实际测试不区分
2. 数据库路径不要硬编码到每个脚本里 — 写在一个变量里方便改
3. ASP 文件上传后需要确认文件权限（Windows Server 默认可执行无特殊设置）
4. 上传目录：确认 `.asp` 文件在 IIS 的虚拟目录中，否则无法解析
5. 使用 `Response.Write "<p>ok</p>"` 作为最简单的执行确认
6. **查询时避免对长文本字段用 LEFT()/LEN() 等函数**，会引发 500
7. **渐进式查询**：先查 id/s_name，定位到行后再查 s_content

## 连接字符串参考

```asp
' Access 数据库
conn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & Server.MapPath("website.mdb")

' 如果 Jet 驱动不可用，尝试 ACE
conn.Open "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=" & Server.MapPath("website.mdb")

' UTF-8 编码设定（必须在 ASP 文件头部）
<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<% 
Response.CharSet = "utf-8"
Session.CodePage = "65001"
%>
```

## FTP 连中文 Windows 服务器的规范

```python
ftp = FTP()
ftp.encoding = 'latin-1'  ' 关键！中文 Windows 服务器不认 utf-8
ftp.connect(host, 21, timeout=15)
ftp.login(user, passwd)
ftp.set_pasv(True)  ' 被动模式，防火墙友好
```

## 常见错误与解决

| 错误 | 原因 | 解法 |
|------|------|------|
| HTTP 500 / 页面空白 | ASP 语法错误或 SQL 执行异常 | 简化 SQL，先写 `Response.Write "ok"` 测试连接 |
| FTP 550 file not found | 文件名有中文或 URL 重写导致 | 确认实际文件名，用 NLST 列出目录检查 |
| 更新后页面无变化 | 缓存 | 清除浏览器缓存或隐身模式查看 |
| 中文显示乱码 | 编码不匹配 | 确保 ASP 头部三件套：`Codepage=65001` + `Response.Charset=utf-8` + `Session.CodePage=65001` |
| SQL LIKE 中文 → 500 | Access OLEDB 驱动编码转换失败 | 不要用中文 LIKE 查询，改用 `WHERE id=N` 精确查询 |
| FTP 上传后 ASP 中文变乱码 | 用了 `storlines()` 而非 `storbinary()` | 用 `storbinary()` 二进制传输 UTF-8 编码的 .asp 文件 |
| Upload 后页面空白 | ASP 中 `%%>` 被代码块截断 | ASP 代码中不要出现 `%%>`（这是 Markdown 转义产物）。写 `%>` 即可 |