---
name: wsl-windows-file-delivery
description: 交付文件放Windows桌面/mnt/c/Users/Admin/Desktop，不显示WSL路径。
tags: [WSL, Windows, 交付, 桌面, 文件路径, 用户偏好]
---

# WSL → Windows 交付文件落地规范

## 触发条件
任何任务产出交付物（docx / txt / xlsx / 图片 / 截图 / 报告）时，交付前必须执行本规范。
首次发现：2026-08-24 用户明确纠正「我一直从windows侧拿文件的，你要记住，以后不要显示wsl桌面了」。

## 铁律
1. **交付文件一律放 Windows 桌面**：`/mnt/c/Users/Admin/Desktop/`（Windows 用户名 = Admin）。
2. **不要**放 WSL 桌面 `~/Desktop`、也**不要**放任何 WSL-only 目录（用户看不见）。
3. **回复中不要展示 WSL 路径**（如 `/home/dmin/Desktop/xxx.docx`），只给 Windows 路径（`C:\Users\Admin\Desktop\xxx.docx`）。
4. 若文件生成在别处（如 /tmp、工作目录），用 `cp` 拷到 Windows 桌面再交付。

## 步骤
1. 生成内容到临时位置（WSL 内任意可写目录）。
2. `cp <临时路径> /mnt/c/Users/Admin/Desktop/<文件名>`（中文文件名直接可用）。
3. 校验：`ls -la /mnt/c/Users/Admin/Desktop/<文件名>` 确认落盘。
4. 回复中只写 Windows 路径：`C:\Users\Admin\Desktop\<文件名>`。

## 实测路径速查（2026-08-24）
- Windows 桌面：`/mnt/c/Users/Admin/Desktop` ✅ 存在
- **勿再使用** `/mnt/d/OneDrive/Desktop`（曾误记，实际不存在）
- 判断 Windows 用户名方法：`ls -d /mnt/c/Users/*/Desktop`

## 已知误区和坑
- 旧记忆/旧 skill 里若残留 `D:\360MoveData\Users\Admin\Desktop` 或 `/mnt/d/OneDrive/Desktop` 等路径，一律以 `/mnt/c/Users/Admin/Desktop` 为准。
- WSL 里 `~/Desktop`（即 `/home/dmin/Desktop`）也存在，但用户不从那里拿文件——生成到那里等于没交付。
- 同步夹 memories/ 源 = `~/.hermes/memories/`（Hermes），非 `~/memories/`（Codex），与交付规范无关但常见混淆。

## 关联
- 短视频脚本 docx 交付细节见用户自有技能 `short-video-copywriting`（产出规范节）——该技能 created_by=None 属用户自有，后台 curator 不能改，需 `hermes curator adopt` 后方可增补。
- 预付费卡跑路×预收账款行业自然流案例见本技能 `references/prepaid-card-accounting-case.md`。