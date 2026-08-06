---
name: db-website-content-mgmt
category: devops
description: 修改数据库驱动型网站内容（ASP/Access、PHP/MySQL 等）—— 当内容存储在数据库中、且无直接数据库客户端可用时，通过临时服务端脚本注入实现内容更新。覆盖检测、脚本注入、执行、清理全流程。
triggers:
  - 用户需要"改一下网站上的内容"
  - 网站使用 ASP/PHP/ASP.NET 等动态生成页面
  - 发现网站内容存储在 .mdb / MySQL / SQL Server 等数据库中
  - 需要批量修改数据库中存储的文本内容（非手动编辑每个页面）
  - 用户要求更新网页上的"公司介绍"、"团队成员"、"资质证书"等动态内容
---
# 数据库驱动型网站内容修改技能

## 核心理念

> 用户说"改一下网站上的内容"，但网站是数据库驱动的（如 ASP + Access），
> 不是静态 HTML。你**不能直接编辑文件**修改内容，必须通过数据库操作。

关键挑战：在 Linux/WSL 环境下，你通常没有 Access/SQL Server 的客户端驱动。
解决思路：**利用网站自己的服务端脚本能力，通过临时脚本代理数据库操作。**

---

## 工作流

### Step 1: 诊断 — 网站是不是数据库驱动的？

在通过 FTP/文件系统查看网站文件时，识别线索：

| 线索 | 含义 |
|------|------|
| 扩展名为 `.asp`（非 .html/.htm） | 经典 ASP 网站，通常搭配 Access DB |
| 目录下存在 `.mdb` 文件 | Access 数据库文件，内容存储于此 |
| 扩展名为 `.aspx` | ASP.NET 网站，存储于 SQL Server/Express |
| 扩展名为 `.php` | PHP 网站，存储于 MySQL |
| 存在 `/inc/`、`/include/`、`/admin/` 等管理目录 | 有 CMS 系统 |
| 页面路径带 `?id=` 参数 | 动态页面，内容从数据库读取 |
| 页面 URL 以 `.html` 结尾但目录中有 `.asp` 模板文件 | 伪静态 / URL Rewrite |

### Step 2: 网站环境摸底——先建目录地图

连接 FTP 后不要急着上传脚本，先搞清楚目录结构：

```python
ftp.cwd('wwwroot')
dirs = []
ftp.retrlines('NLST', dirs.append)
print(dirs)
```

记录：
- 根目录下有哪些 .asp 文件（用来判断服务器端函数）
- 有没有 `inc/` 或 `admin/` 子目录
- 数据库文件 .mdb 在哪个目录
- 图片资源目录路径（资质证书、团队照片等）

**目的**：为后续上传临时脚本（放在哪）和清理（删哪些文件）建立清单。这一步做踏实了，不会漏删临时文件。

### Step 3: 确认数据库结构

找到 `.mdb` 文件后，先尝试本地解析：

```bash
# Linux: 如果有 mdbtools
mdbtools -tables database.mdb
cat table.mdb  # 实际使用 mdb-export <database.mdb> <table>
```

如果本地无法解析（常见于 WSL/Linux 无 Access 驱动）：
→ 跳过本地解析，直接进入 Step 3 的服务端查询。

### Step 3: 创建临时查询脚本

在本地创建一个只读查询脚本，上传到网站，通过 HTTP 访问执行：

#### 渐进式查询策略（对付 500）

当直接 `SELECT * FROM table` 或带函数 `SELECT LEFT(content,200)` 返回 HTTP 500 时：

1. **先查简单字段**：`SELECT id, s_name FROM table ORDER BY id`
2. **定位目标行**后，再单独查该行的全部字段：`SELECT * FROM table WHERE id=N`
3. 如果仍然 500，**逐列添加**：先查一列确认可行，再加一列

> 原因：Access 的 OLEDB 驱动在某些 IIS 环境下，对长文本/text 字段使用 SQL 函数（LEFT、SUBSTRING、LEN 等）会触发 500 内部错误。直接用原始字段名 `SELECT s_content` 反而安全。

**query.asp**（Access 数据库查询模板）：

```asp
<%@ Language=VBScript %>
<% Option Explicit %>
<%
Dim conn, rs, sql
Set conn = Server.CreateObject("ADODB.Connection")
' === 修改数据库路径为实际路径 ===
conn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & Server.MapPath("database.mdb")

' === 修改 SQL 查询为需要的语句 ===
sql = "SELECT * FROM a_info ORDER BY a_id"

Set rs = conn.Execute(sql)

' 输出为表格
Response.Write "<table border='1'><tr>"
' 输出列名
For i = 0 To rs.Fields.Count - 1
    Response.Write "<th>" & rs.Fields(i).Name & "</th>"
Next
Response.Write "</tr>"

' 输出数据
Do While Not rs.EOF
    Response.Write "<tr>"
    For i = 0 To rs.Fields.Count - 1
        Response.Write "<td>" & Server.HTMLEncode(rs.Fields(i).Value & "") & "</td>"
    Next
    Response.Write "</tr>"
    rs.MoveNext
Loop

Response.Write "</table>"

rs.Close
Set rs = Nothing
conn.Close
Set conn = Nothing
%>
```

#### 识别服务端辅助函数（省心大招）

先看网站现有 ASP 文件（index.asp、about.asp 等）有没有封装好的数据库读取函数。
常见命名模式：

| 函数 | 返回 |
|------|------|
| `db_content(table, id)` | 正文内容 |
| `db_name(table, id)` | 页面标题 |
| `db_name1(table, id)` | 关键词 keywords |
| `db_name2(table, id)` | 描述 description |

如果存在这些函数，优先用！比手写 SQL 更可靠（已处理编码、格式化、空值保护）：

```asp
s_content = db_content("a_info", 4)  ' 一行搞定
```

这些函数通常定义在 `inc/conn.asp` 或 `inc/function.asp` 里，看一眼就知道怎么用。

### Step 4: 分析数据并确定修改方案

访问临时脚本 URL → 获取数据库内容 → 确认要修改的字段和值。

常见字段映射：

| 网站页面 | 可能的数据表/字段 |
|---------|-----------------|
| 关于我们 | `a_info` 表, `s_name` (标题), `s_content` (内容), `s_photo_url` (图片) |
| 团队介绍 | `team` 表, `s_name` (姓名), `s_detail` (介绍), `s_photo_url` (头像) |
| 业务/服务 | `service` 表, `s_title` (服务名称), `s_content` (描述) |
| 新闻动态 | `news` 表, `s_title` (标题), `s_content` (正文), `d_update_time` (日期) |
| 资质证书 | `cert` 表, `s_name` (证书名称), `s_photo_url` (证书图片) |

### Step 5: 创建并执行修改脚本

确定要修改的内容后，创建 UPDATE 脚本，上传执行：

```asp
<%@ Language=VBScript %>
<% Option Explicit %>
<%
Dim conn, sql
Set conn = Server.CreateObject("ADODB.Connection")
conn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & Server.MapPath("database.mdb")

' === 修改 SQL 为实际更新语句 ===
sql = "UPDATE a_info SET s_name = '示范基地成员单位' WHERE a_id = 17"

conn.Execute(sql)

Response.Write "<p>✅ 更新成功</p>"

conn.Close
Set conn = Nothing
%>
```

**注意：**
- UPDATE 前先在查询脚本里确认 WHERE 条件精确
- 如果是纯文本替换（不是整个字段替换），确认 SQL 支持字符串替换函数
  - Access: `UPDATE table SET field = Replace(field, '旧字', '新字') WHERE condition`
  - MySQL: `UPDATE table SET field = REPLACE(field, '旧字', '新字') WHERE condition`

### Step 5 备选方案：RecordSet 读-改-写模式（推荐中文替换场景）

当「读出现有内容 → 中文文本替换 → 写回」时，**RecordSet 读-改-写** 比 SQL UPDATE 更灵活（编码可控、支持 If/Else 条件逻辑、可做错误回滚）：

```asp
<%@ Language=VBScript %>
<% Option Explicit %>
<%
On Error Resume Next

Dim conn, rs
Set conn = Server.CreateObject("ADODB.Connection")
conn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & Server.MapPath("database.mdb")

' === 打开记录集（读写模式：1=Keyset, 3=Optimistic Lock） ===
Set rs = Server.CreateObject("ADODB.RecordSet")
rs.Open "SELECT s_content FROM a_info WHERE id=1", conn, 1, 3

If Not rs.EOF Then
    Dim oldC, newC
    oldC = rs("s_content")
    
    ' === VBScript Replace() 做中文文本替换，编码全程可控 ===
    newC = Replace(oldC, "旧文字", "新文字")
    
    rs("s_content") = newC
    rs.Update()
    
    If Err.Number = 0 Then
        Response.Write "✅ 更新成功"
    Else
        Response.Write "❌ 更新失败: " & Err.Description
    End If
End If

rs.Close()
Set rs = Nothing
conn.Close()
Set conn = Nothing
%>
```

**适用场景对比：**

| 场景 | 传统 SQL UPDATE | RecordSet 读-改-写 |
|------|----------------|-------------------|
| 字段内局部中文替换 | `Replace()` 嵌套在 SQL，编码穿越层数多 | VBScript 内 `Replace()`，编码可控 ✅ |
| 多段逻辑（先查再决定改不改） | SQL 难处理条件分支 | 可写 If/Else 判断 ✅ |
| 出错回滚 | 无回滚能力 | `Err.Number` 检查后 `CancelUpdate()` ✅ |
| 中文编码安全性 | 依赖 OLEDB 驱动对 UTF-8 的兼容 | ASP 文件 UTF-8 + binary FTP → 中文可控 ✅ |

### Step 5 编码安全：上传含中文的 ASP 文件

ASP 文件中的中文字符在上传时经过 **两次编码转换**：FTP 控制通道编码 + 文件自身编码。

**规范做法：**

```python
from ftplib import FTP

ftp = FTP()
ftp.encoding = 'latin-1'      # 控制通道（对中文 Windows 兼容性最广）
ftp.connect(host, 21)
ftp.login(user, passwd)
ftp.set_pasv(True)

# 🔴 用 storbinary() 不是 storlines()
# binary 模式以字节流原样传输，保证 UTF-8 多字节序列不被破坏

asp_content = '''<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<%%
Response.Charset = "utf-8"
%%>
...'''

with open('/tmp/script.asp', 'wb') as f:
    f.write(asp_content.encode('utf-8'))

with open('/tmp/script.asp', 'rb') as f:
    ftp.storbinary('STOR script.asp', f)   # ✅ 中文不乱码

# ❌ 不要用 storlines() — text mode，中文多字节会被切断
```

**ASP 文件头部编码三件套（缺一不可）：**

```asp
<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<%% Response.Charset = "utf-8" %%>
<% Session.CodePage = "65001" %%>
```

**中文写在 VBScript 里还是用 ChrW()？**

| 方式 | 适用场景 |
|------|--------|
| 直接写中文 | ASP 文件 UTF-8 + `storbinary` 上传 ✅ 主流做法 |
| `ChrW(&x) & ChrW(&x)` | 极端情况保底方案（文件编码不可控时的救急） |

正常情况直接写 `Replace(oldC, "示范基地", "示范基地(会计学会)")` 即可。

### Step 5 进阶：关键词统一化 + 多页面同步

当需要在**多个页面**中统一某个关键词或资质名称时，不要逐个页面手动改。

**操作流**：
1. **全站扫描**：查全表确认关键词涉及哪些记录
2. **挨个改**：每个命中记录独立执行 Replace 更新
3. **一致性验证**：验证每个命中记录是否都被更新

**实战案例（2026.5.22 盈信官网多页面关键词统一）**：

背景：官网多处提到资质名称，散落在不同记录中且表述不一致：
- 📄 首页（id=4）：`苏州工业园区会计服务外包示范基地成员单位` + `苏州工业园区会计学会（服务外包示范基地）推荐成员`
- 📄 关于盈信（id=1）：`苏州工业园区会计服务外包示范基地` + `省市行业协会会员`

统一目标：
- `示范基地` → `<strong>苏州工业园区会计服务外包示范基地（苏州工业园区会计学会）</strong>`
- `省市行业协会会员` → `<strong>苏州会计服务协会和江苏省代理记帐协会会员</strong>`

执行步：
1. 扫描全表定位到 id=1、id=4
2. 修改 id=1 s_content（两处Replace链式调用）
3. 修改 id=4 s_content（两处Replace链式调用）
4. 验证：HTTP 抓取首页和关于盈信页面确认关键词统一

为什么要用 RecordSet 读-改-写而非 SQL 批量 UPDATE：
| 场景 | RecordSet 读-改-写 | 纯 SQL UPDATE |
|------|-------------------|---------------|
| 字段内局部中文替换 | ✅ VBScript 内 Replace，编码可控 | ⚠️ Access SQL 中 Replace() 对长中文可能编码越界 |
| 两处不同替换逻辑 | ✅ 分两次 Replace() 调用 | ❌ 嵌套 REPLACE 可读性差 |
| 不同页面不同策略 | ✅ 每个 id 独立处理 | ❌ 难写一条 SQL 同时处理两处逻辑 |
| 执行后验证 | ✅ 可以 Response.Write 新内容 | ❌ 需另写查询 |

核心教训：
- **不要用中文 LIKE 查询** → 先查 id/s_name 定位，再逐个查 s_content
- **不要用 SQL Replace() 处理长中文** → 用 RecordSet + VBScript Replace
- **长文本字段（6000+ 字符 HTML）直接 SELECT 原始字段**，不走 SQL 函数
- **多页面同步前先扫全表**，确认所有涉及记录，避免漏改

### Step 5 应对 SQL LIKE 中文导致的 500 错误

**问题：** ASP 中 `WHERE s_content LIKE '%中文%'` 带中文条件 → HTTP 500

**原因：** 中文 SQL 条件在 ASP 代码中经过编码转换，传递给 Access OLEDB 驱动后变乱码，查询失败。

**解法：**

- 不要用中文 LIKE 查询。先 `SELECT id, s_name FROM a_info` 定位行，再按 id 查 s_content
- 或用 `INSTR()` 替代 LIKE（但同样编码敏感，不推荐）

```asp
' ❌ 会 500
rs.Open "SELECT * FROM a_info WHERE s_content LIKE '%示范基地%'", conn

' ✅ 安全
rs.Open "SELECT id, s_name FROM a_info ORDER BY id", conn
' 手动定位后
rs.Open "SELECT s_content FROM a_info WHERE id=1", conn
```

### Step 6: 验证修改

1. ✅ 方案一（推荐）：在更新脚本内直接验证 — Update() 后立即 Response.Write 新旧内容，确认无误再删脚本。避免"删了脚本才发现没改对"。
2. ✅ 方案二：HTTP 访问目标页面，确认内容正确显示
3. ✅ 方案三：重新执行查询脚本，确认数据库已更新

### Step 7: 清理 — 删除临时脚本

**这是最重要的一步。** 临时脚本暴露了数据库结构，必须立即删除：

- 通过 FTP 删除 query.asp、update.asp 等临时文件
- 确认文件已不在服务器上（列出目录检查）

---

## 图片/附件修改

如果网站上的图片（如资质证书、团队照片）存储在数据库中：

1. 先确认图片字段类型
   - 如果字段存的是**文件路径**（推荐）：直接将新图片上传到对应目录，更新数据库路径
   - 如果字段存的是**二进制数据**（Blob）：需要专门的脚本处理，较复杂

2. 判断字段类型的方法：
   - 查出来的字段值以 `/` 开头或包含 `.jpg`/`.png` → 文件路径
   - 查出来是一长串乱码 → 二进制存储

---

## 适用场景与变体

### ASP + Access（经典 ASP）
- 连接字符串：`Provider=Microsoft.Jet.OLEDB.4.0;Data Source={path}`
- 脚本扩展名：`.asp`
- 特点：无需编译，上传即生效

### ASP.NET + SQL Server
- 可能需要编译，不适合临时脚本方式
- 替代方案：找后台管理页面，或直接用 SSMS 通过 VPN 连接

### PHP + MySQL
- 写一个临时 `query.php`，用 `mysqli_connect()` + `mysqli_query()`
- 执行完立即删除
- 脚本示例：
```php
<?php
$conn = mysqli_connect('localhost', 'user', 'pass', 'dbname');
if (!$conn) { die('连接失败: ' . mysqli_connect_error()); }
$sql = "SELECT * FROM pages";
$result = mysqli_query($conn, $sql);
echo "<table>";
while ($row = mysqli_fetch_assoc($result)) {
    echo "<tr><td>" . htmlspecialchars($row['title']) . "</td></tr>";
}
echo "</table>";
mysqli_close($conn);
?>
```

---

## 参考案例

本技能仓库包含以下文件：

| 文件 | 内容 |
|------|------|
| `references/asp-access-session-example.md` | 2026年5月实战案例 — ASP + Access 网站修改实录，含数据库结构、脚本、注意事项、多案例对比 |
| `references/2026-05-22-yingxin-content-unification.md` | 2026.5.22 盈信官网多页面关键词统一化实战记录 — 全站资质名称统一、两处页面不同替换策略 |
| `references/sme-website-audit-checklist.md` | **中小企业官网内容巡检清单** — 修改前先审计。系统性检查各页面的文案准确性、信息一致性、基本合规性（地址、电话、资质）。与 db-website-content-mgmt 配合使用：先审计 → 再修改。 |
| `templates/asp-update-template.asp` | 可复用的 ASP 更新脚本模板，含查询确认和更新两段，复制到网站修改后即用 |

查看参考：`skill_view(name="db-website-content-mgmt", file_path="references/asp-access-session-example.md")`

使用模板：`skill_view(name="db-website-content-mgmt", file_path="templates/asp-update-template.asp")` → 复制内容 → 修改 SQL/替换逻辑 → 上传到网站执行

---

## 坑（Pitfalls）

| 坑 | 现象 | 正确处理 |
|----|------|---------|
| 忘记删临时脚本 | 数据库结构暴露给互联网 | 每次执行完立即 FTP 删除，最后列出目录确认 |
| 修改条件不对 | 更新了不该改的行 | UPDATE 前先用 SELECT 确认 WHERE 条件返回的行数 |
| 数据库路径猜错 | 脚本访问报 500 错误 | 在现有 ASP 文件中搜索连接字符串，用 `Server.MapPath()` 确认路径 |
| 路径含中文 | Access 连接失败 | 确保 `Data Source` 路径中的中文被正确编码 |
| 上传 .asp 文件后页面空白 | 可能 ASP 解析错误 | 先在本地检查语法，或者先上传一个简单的 `Response.Write "ok"` 测试 |
| 网站禁用文件写入 | FTP 上传成功但无法访问 | 检查文件权限，确认上传到正确目录（如 `/wwwroot/` 下） |
| 修改后不生效 | 页面可能缓存 | 清空浏览器缓存或用隐身模式重新访问 |
| 中文 LIKE 导致 500 | Access OLEDB 驱动编码转换失败 | 不用中文 LIKE 查询，改用 `WHERE id=N` 精确查 |
| 上传后 ASP 中文乱码 | 用了 `storlines()` 文本模式传输 | 用 `storbinary()` 二进制传输 UTF-8 编码文件 |
| ASP 代码中出现 `%%>` 而非 `%>` | 从 Markdown 文件复制代码时被转义 | 写代码时直接写 `%>`，不要用 `%%>`。如果是从 `skill_view()` 输出复制代码，检查并替换 `%%>` 为 `%>` |
| 字段内容是 Blob/二进制 | 看到乱码 | 这种字段是存图片的，不要直接改。图片改路径即可 |
| SQL 函数导致 ASP 500 | `SELECT LEFT(s_content, 200)` 返回 500 | 查询长文本字段时避免用 LEFT()/LEN() 等 SQL 函数，直接 SELECT 原始字段。先用简单字段定位行，再单独查该行的 s_content |
| FTP 编码不对导致中文乱码 | FTP 列目录或文件名变乱码 | 连接中文 Windows 服务器时设置 `ftp.encoding = 'latin-1'`（部分服务器用 gb2312，latin-1 兼容性最广） |

---

## 验证清单

执行完成后，逐项确认：

- [ ] 临时脚本已全部删除（FTP `NLST` 列表逐一核对，不能只看文件名前缀）
- [ ] 目标页面内容显示正确
- [ ] 所有修改过的字段显示正确
- [ ] 页面格式没有破坏（如 HTML 标签被转义）
- [ ] 网站其他页面功能正常
- [ ] 如果涉及图片：图片正常加载
