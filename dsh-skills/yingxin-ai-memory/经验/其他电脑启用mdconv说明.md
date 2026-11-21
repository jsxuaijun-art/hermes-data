# 其他电脑启用 mdconv（MarkItDown 文档转 Markdown 工具箱）

适用：新电脑 / 他地的电脑。power 前提已具备。

## 一步：拉取 skill（已有）
你的 Hermes 同步（拉取.bat → git fetch+reset 同步夹 → rsync 进 ~/.hermes/）会把 skill 一起带到。
确认 skill 是否到位：
```bash
ls ~/.hermes/skills/productivity/markdown-conversion-toolkit/
# 应看到 SKILL.md 和 scripts/setup_mdconv.sh
```

## 两步：装软件本体（每台机器只需做一次）
skill 同步的是「安装方法」，markitdown + tesseract 软件本身要本机各装一次：
```bash
bash ~/.hermes/skills/productivity/markdown-conversion-toolkit/scripts/setup_mdconv.sh
```
脚本自动完成（清华源）：
- 找/建 Python venv（优先 ~/hermes-agent/venv，其次 ~/.hermes/venv）
- 装 markitdown[all]（PPT/PDF/Excel/Word/音视频 转 md）
- 装/复用 tesseract 中文 OCR（图片认字）
- 生成 ~/bin/mdconv 命令并提示入 PATH

装完把 ~/bin 加进 PATH（脚本若显示 WARN 则执行）：
```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

## 三步：验证
```bash
mdconv --help              # 应出用法
mdconv 某文件.pdf -o 输出.md   # 实际转一个看效果
```
- 新会话默认未激活 venv，判定"已装"用 venv 绝对路径，别只 `which` 会误判。

## 日常用法
```
mdconv 文件.pdf -o 输出.md    # 转成文件
mdconv 文件.docx              # 直接看
mdconv 图片.png               # 图片走中文 OCR
mdconv 目录/                  # 批量目录
```

## 一句话心智
skill = 方法（已云端同步）；软件 = 每机装一次（不能跨机共享）。装好即长期可用。