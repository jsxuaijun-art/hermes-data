<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<%
Response.Charset = "utf-8"
Session.CodePage = "65001"
%>
<!--#include file="inc/conn.asp"-->
<%
' ====================================
' ASP + Access 数据库内容更新模板
' 使用说明：
' 1. 确认 inc/conn.asp 路径正确
' 2. 修改下方 SQL 和逻辑
' 3. 上传到网站根目录
' 4. 浏览器访问执行
' 5. 确认后立即 FTP 删除
' ====================================

Dim rs, sql, oldC, newC

' === 查询确认阶段（先注释掉，去掉下面注释运行） ===
' Set rs = Server.CreateObject("ADODB.RecordSet")
' rs.Open "SELECT id, s_name FROM a_info ORDER BY id", conn, 1, 1
' Do While Not rs.EOF
'     Response.Write "id=" & rs("id") & " | " & rs("s_name") & "<br>"
'     rs.MoveNext
' Loop
' rs.Close()
' Response.End()

' === 更新阶段（确认定位准确后执行） ===
Set rs = Server.CreateObject("ADODB.RecordSet")
rs.Open "SELECT s_content FROM a_info WHERE id=1", conn, 1, 3  ' 3=adLockOptimistic

If Not rs.EOF Then
    oldC = rs("s_content") & ""
    
    ' 在这里修改替换逻辑
    newC = Replace(oldC, "旧文字", "新文字")
    
    rs("s_content") = newC
    rs.Update()
    
    If Err.Number = 0 Then
        Response.Write "✅ 更新成功！<br>"
        Response.Write "旧长度: " & Len(oldC) & " → 新长度: " & Len(newC)
    Else
        Response.Write "❌ 更新失败: " & Err.Description
        Err.Clear()
    End If
Else
    Response.Write "❌ 未找到指定记录"
End If

rs.Close()
Set rs = Nothing
%>