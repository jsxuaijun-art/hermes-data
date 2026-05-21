' 重新创建桌面快捷方式（带错误检查版）
Set WshShell = CreateObject("WScript.Shell")

' 获取桌面路径
strDesktop = WshShell.SpecialFolders("Desktop")

' 当前脚本所在目录（scripts/）
strScriptPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "")
strBatPath = strScriptPath & "run_docs.bat"

' 检查文件是否存在
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FileExists(strBatPath) Then
    MsgBox "错误：未找到文件" & vbCrLf & strBatPath, vbCritical, "文件不存在"
    WScript.Quit
End If

' 创建快捷方式
strLnk = strDesktop & "\盈信合规文书生成器.lnk"
Set oShortCut = WshShell.CreateShortcut(strLnk)
oShortCut.TargetPath = strBatPath
oShortCut.WorkingDirectory = strScriptPath
oShortCut.Description = "苏州盈信 - 代理记账合规文书生成器"
oShortCut.Save

MsgBox "桌面快捷方式创建成功！" & vbCrLf & vbCrLf & "双击「盈信合规文书生成器」即可运行。", vbInformation, "苏州盈信企业管理有限公司"
