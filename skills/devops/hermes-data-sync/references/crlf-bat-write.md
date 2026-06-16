# CRLF Bat 文件写入方法（WSL → Windows）

## 核心规则

向 Windows 文件系统写 `.bat` 文件时：
- **不可用 `write_file`** → 生成 LF 换行（`\n`），cmd 无法解析
- **必须用 Python 二进制写** → 显式指定 CRLF（`\r\n`）

## 标准模板

```python
path = '/mnt/c/Users/Admin/Desktop/script.bat'

lines = [
    '@echo off',
    'chcp 65001 >nul',
    'echo.',
    'echo First step...',
    'wsl -d Ubuntu-22.04 -- bash -c "echo hi"',
    'echo.',
    'pause',
]

# 关键：\r\n 作为行连接符，末尾再加一次 \r\n
content = '\r\n'.join(lines) + '\r\n'

with open(path, 'wb') as f:
    f.write(content.encode('ascii'))
```

## 是什么

| 属性 | 值 |
|------|------|
| 写入工具 | `execute_code` 跑 Python |
| 文件模式 | `'wb'`（二进制写） |
| 换行符 | `'\r\n'.join(lines)` |
| 编码 | `.encode('ascii')` 最安全；UTF-8 用 `.encode('utf-8')` |
| 行末 | 最后再加一次 `'\r\n'` 确保文件以换行结束 |

## 验证方法

从 Windows 侧确认（用 `cmd.exe /c` 从 WSL 调用）：

```bash
cmd.exe /c "type C:\Users\Admin\Desktop\script.bat"
# 应显示每行正确内容，无乱码

# 或用 PowerShell 读换行符
powershell.exe -Command "Get-Content 'C:\Users\Admin\Desktop\script.bat' | Select-Object -First 3"
```

## 编码策略优先级

1. **纯 ASCII + CRLF** — 稳定可靠，cmd 零兼容问题
2. **UTF-8 with BOM + CRLF** — 需要 BOM 三字节 `\xef\xbb\xbf` 开头，部分系统仍可能失败
3. **GBK/ANSI** — 不推荐，不支持线框等 Unicode 字符

## 真实故障排查 Checklist

当 .bat 文件出乱码时，按此顺序排查：

```
□ 文件是 CRLF 换行？  →  xxd | grep '0d0a'
□ 文件是 ASCII/UTF-8？ →  file *.bat
□ WSL 路径正确？       →  /home/dmin/ 不是 /root/
□ .bat 在 Windows 桌面？→  C:\Users\Admin\Desktop\ 不是 D:\...
□ 命令中无中文/线框？  →  grep -P '[^\x00-\x7F]' *.bat
```
