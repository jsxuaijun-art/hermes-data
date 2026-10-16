---
name: word-batch-edit
display_name: Word 文档批量查找替换
display_name_en: Batch Find/Replace in Word Docs
description: 在 Windows 上对一批已有 .doc/.docx 合同或文档做精确的批量查找替换（改条款、改错字、插入句子），基于 Word COM 自动化，逐文件独立实例，改前快照备份、改后字符级校验。
description_zh: 用 Word COM 对一批 .doc/.docx 做批量查找替换，可靠、可回滚、可校验。
description_en: Batch find/replace across many .doc/.docx files via Word COM automation, with backup and verification.
category: office
version: 1.0.0
agent_created: true
author: WorkBuddy
---

# Word 文档批量查找替换

在一批已有的 `.doc` / `.docx`（合同、协议等）里做**精确的批量查找替换**：改条款措辞、删句子、插句子、改错别字。适用于 `tencent-local-office-edit` 的 editor_sdk **打不开已有文档**（本机反复复现：文件能注册进 pool 但 C++ 编辑器加载不出内容，`doc_find` 报 "document is not open"，与格式/OneDrive 无关）时的替代路线。

## 何时用

- 用户说"把 X 文件里的 A 改成 B / 删掉 C / 在 D 后面加上 E"，且目标是**已存在的 Word 文件**。
- 一次要改**多份**同款文档。
- 需要**可回滚**和**可校验**。

不要用它做：新建文档（用 office 技能）、复杂排版重构。

## 铁律（照做，别问）

1. **先备份**：改前把目标文件整批复制到 `_bak_YYYYMMDD/` 快照目录。
2. **先探查精确字面**：先用只读脚本 dump 目标段落原文。中文合同里标点**全角/半角混用**（如"10份以内**,**销货清单"是半角逗号），`Find` 必须一字不差才命中。
3. **改后必校验**：`old残留=False` 且 `new就位=True`，并读回实际段落确认落点。
4. **只改该改的**：若目标串在文档里多处出现，用**足够长的整串**精确匹配，避免误伤（例："基础服务项目："要带冒号，才不会碰到正文里的"基础服务项目③"）。
5. **删除等危险操作先给用户确认**；纯文本替换在同一轮迭代里可直接做（用户已授权的前提下）。

## 可靠模式（本机已验证）

- **Word COM**：`New-Object -ComObject Word.Application`。
- **每份文档独立 Word 实例**：开→改→存→`$doc.Close($false)`→`$word.Quit()`。避免一个文件出问题拖垮整批、避免会话 RPC 断连。
- **绝不用 `while` 循环跑 `Find.Execute` 计数**——Word COM 在 PowerShell 里会**死循环卡死**（曾卡 4 分钟无输出）。只做"单次 Find / 单次 ReplaceAll + 改前改后状态记录"。
- **脚本编码**：先写 UTF-8（无 BOM），再用受管 Python 转成 **UTF-8-SIG（带 BOM）**：
  ```bash
  VP="C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe"
  "$VP" -c "
  src='...\\xxx.ps1'; dst='...\\xxx_bom.ps1'
  with open(src,'r',encoding='utf-8') as f: data=f.read()
  with open(dst,'w',encoding='utf-8-sig') as f: f.write(data)
  print('BOM copy written')
  "
  ```
- **调用**：用 PowerShell 工具执行 `& "…\xxx_bom.ps1"`。**`Invoke-Expression`/`iex` 被安全策略拦截**，别用。
- **查残留**：`$doc.Content.Find.Execute($old, …)` 返回 `True/False` 即"是否还存在"。
- **精确上下文**：`$cr=$doc.Content.Duplicate; $cf=$cr.Find.Execute($anchor,…); $cr.Paragraphs.Item(1).Range.Text` 读该段落（一次 Find，不循环）。

## ⚠️ 头号地雷：PowerShell 把弯引号当字符串定界符

PowerShell 会把 **U+201C “ / U+201D ”**（弯引号）以及 **U+2018 ‘ / U+2019 ’** 当作**字符串定界符**。若把它们直接写进 `.ps1` 的双引号字符串里，脚本**解析报错**（`表达式或语句中包含意外的标记`），**整脚本不执行、连日志都不生成**。

**解法**：用 char 码拼，源文件里不出现字面弯引号：
```powershell
$q1 = [char]0x201C   # “
$q2 = [char]0x201D   # ”
$new = "……准确性，" + $q1 + "确认开具" + $q2 + "后再交由甲方……"
```
（半角直引号 `"` `'` 才是常规定界符；弯引号/全角引号同样是定界符，是隐藏坑。）

## 脚本模板

```powershell
# -*- coding: utf-8 -*-
$ErrorActionPreference = "SilentlyContinue"
Get-Process -Name "WINWORD" -ErrorAction SilentlyContinue | ForEach-Object { $_.Kill() }
Start-Sleep -Milliseconds 300

$base  = "D:\某目录"
$files = @("a.doc","b.docx")     # 显式列出，别用通配
$old   = "要替换的旧串"
$new   = "新串"                   # 含弯引号时用 [char]0x201C/0x201D 拼
$log   = "C:\...\_docedit\modify_log.txt"
"" | Out-File -FilePath $log -Encoding utf8

foreach ($f in $files) {
    $path = Join-Path $base $f
    $word = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false; $word.DisplayAlerts = 0
        $doc = $word.Documents.Open($path, $false, $false)   # 第3参 ReadOnly=$false 才能存
        $before = $doc.Content.Find.Execute($old, $false,$false,$false,$false,$false,$false,1,$false,$null,0,$null)
        if ($before) {
            $doc.Content.Find.Execute($old, $false,$false,$false,$false,$false,$false,1,$false,$new,2,$null)  # Replace=2 全部
            $after_old = $doc.Content.Find.Execute($old, $false,$false,$false,$false,$false,$false,1,$false,$null,0,$null)
            $after_new = $doc.Content.Find.Execute($new, $false,$false,$false,$false,$false,$false,1,$false,$null,0,$null)
            $doc.Save()
            Add-Content -Path $log -Value "$f | MATCH | $after_old | $after_new" -Encoding utf8
        } else {
            Add-Content -Path $log -Value "$f | NO_MATCH" -Encoding utf8
        }
        $doc.Close($false)
    } catch {
        Add-Content -Path $log -Value "$f | ERROR | $($_.Exception.Message)" -Encoding utf8
    } finally {
        if ($word -ne $null) { $word.Quit() }
    }
}
```

## 常用套路

- **删句子** → `$new = ""`（Replace=2）。
- **插句子** → `$old` 取原句，`$new` = 原句+新句；或把"锚点+后续"整体作为 old，`$new` 里插入。
- **改错别字** → `$old="忆方"`，`$new="乙方"`（罕见字可直接全文档替换，安全）。
- **"另起一行"要小心自动编号**：若该处是 Word 自动编号列表（"1./（一）"等**不在正文文本流里**、`Content.Text` 看不到），用**手动换行符 `^l`（Shift+Enter，字符 000B）**而不是真段落回车 `^p`（000D），否则新行会被自动编号成 2./3. 造成错乱。

## 实战案例（盈信财税代理合同系列）

`D:\OneDrive\Desktop\工作\1工作常用\2.协议\0财税代理协议`（9 份：7 个 `.doc` + 2 个 `.docx`）多轮迭代修改：
- 删"不适用于四.（一）.（1）.之税务零申报服务。"；"1. 基础服务项目"→"1. 基础服务项目（代理记帐）"（带冒号，避免误伤正文"基础服务项目③"）。
- 正文标题"财税服务协议"→"财税服务合同"；文件名"财税代理协议*"→"财税代理合同*"（重命名用 PowerShell `Rename-Item`）。
- 在"基础服务项目（代理记帐）："后插入免责句并让"在□内打√…"另起一行（用手动换行符）。
- 「六、违约条款」"提前终止协议的"→"提前终止协议（包括但不限于注销、清算等情形）的"（"（二）"是自动编号，不在文本流）。
- 错别字"支付忆方"→"支付乙方"。
- 「（三）发票开具服务」整句替换（新句含弯引号"确认开具"，用 [char] 拼）。
经验：2 个 `.docx`（个体户代开发票、税务检查协助）是**不同模板**，多数条款不含，属正常 NO_MATCH。
