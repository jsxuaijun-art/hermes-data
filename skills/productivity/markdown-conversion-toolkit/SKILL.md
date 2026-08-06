---
name: markdown-conversion-toolkit
description: 微软 MarkItDown + tesseract 本地OCR 文档/图片转 Markdown 工具箱。当用户说"转成md/markdown""PDF转文字""Word转md""图片OCR""识别扫描件""提取表格文字""转换文档格式"时加载。命令统一为 mdconv。跨机器自动检测安装，缺工具时走一键安装脚本。
---

# 文档/图片 → Markdown 工具箱（跨机器自适应）

markitdown（文档/PDF转md）+ tesseract（图片中英文OCR），统一命令 `mdconv`。
本 skill 可在任意机器复用：检测到工具缺失时，自动/引导走一键安装脚本。

## 第 0 步：检测工具是否可用（每次加载先做）

> 注意：新终端/新会话默认**未激活 venv**，tesseract/markitdown 可能不在 PATH。
> 判定"已装"要用 venv 绝对路径，别只 `which`，否则会误判"未装"而重复安装。

```bash
# 定位 venv（任意机器通用）
VENV_PY=""
for c in "$HOME/hermes-agent/venv" "$HOME/.hermes/venv"; do
  [ -x "$c/bin/python" ] && VENV_PY="$c/bin/python" && break
done
echo "venv python: ${VENV_PY:-未找到}"

# mdconv 是否己生成
[ -x "$HOME/bin/mdconv" ] && echo "mdconv: 已装" || echo "mdconv: 未装（用安装脚本生成）"

# markitdown 是否在 venv
[ -n "$VENV_PY" ] && "$VENV_PY" -m pip show markitdown >/dev/null 2>&1 && echo "markitdown: 已装" || echo "markitdown: 未装"

# tesseract 是否在 venv 且含中文
[ -n "$VENV_PY" ] && "$(dirname "$VENV_PY")/tesseract" --list-langs 2>/dev/null | grep -q chi_sim && echo "OCR中文: OK" || echo "OCR: 需装/缺中文包"
```

- **工具齐** → 跳到「用法」直接用
- **工具缺** → 走「安装」（本机一次性；脚本可复用/同步到其他机器）

## 安装（一键脚本，跨机器通用）

脚本在本 skill 的 `scripts/setup_mdconv.sh`：
- 自动找/建 Python venv（优先 ~/hermes-agent/venv，其次 ~/.hermes/venv）
- 安装 `markitdown[all]`（清华镜像）
- 安装 `tesseract-binary`（pip 包，自带 chi_sim+eng 语言包，无需 apt）
- 生成 `~/bin/mdconv` 命令并确保入 PATH

```bash
# 方式A（Hermes内）：request 本skill，Hermes 自动执行安装
# 方式B（命令行，任何机器）：
bash scripts/setup_mdconv.sh
# 或从 skill 目录直接：
bash ~/.hermes/skills/productivity/markdown-conversion-toolkit/scripts/setup_mdconv.sh
```

装完后验证：
```bash
mdconv --help && mdconv 某文件.docx -o 测试.md && head 测试.md
```
> 跨机器部署：把本 skill 目录同步到新机器（Hermes 数据同步会自动带 skills），
> 在新机器执行上面的 setup_mdconv.sh 即可，一次搞定，无需手动记命令。

## 用法

```
mdconv 文件.docx                # 文档转md输出到终端
mdconv 文件.pdf -o 输出.md      # 另存为文件
mdconv 图片.png                 # 图片走tesseract中文+英文OCR
mdconv 目录/                    # 批量目录（每个文件输出）
```

## 关键说明

- docx/pdf 转换走 markitdown，结构/加粗/表格/列表还原好，中文正常
- **图片**（png/jpg/bmp/webp/tif）走 tesseract `-l chi_sim+eng`，中英文混合识别
- 表格转成 markdown 表格语法
- 反向（md→docx）用 pandoc 或 python-docx（markitdown 不负责此方向）
- ffmpeg 警告可忽略（仅影响音频/视频转文字）；有 imageio 二进制可软链 ~/bin/ffmpeg

## 坑与注意

1. **伪PDF**：文件头 `%PDF` 但结构损坏会报 `No /Root object!`。先 `head -c 100 文件|xxd` 看文件头确认。
2. **HTTP路径**：markitdown 支持 URL（`markitdown https://...`）。
3. 中文OCR准确率依赖图片清晰度；模糊扫描件可先放大/增强。
4. tesseract 用 pip 的 tesseract-binary（在 venv/bin），**别装系统 apt 版**冲突。
   若系统已有 tesseract，确认 `tesseract --list-langs` 有 chi_sim，没有则 `apt install tesseract-ocr-chi-sim`。
5. 手动方式旧版：`pip install 'markitdown[all]' -i 清华镜像` + `pip install tesseract-binary -i 清华镜像`（仅供理解，正常用脚本）。

## 触发场景
- 客户发的 PDF/Word 报表、合同、扫描件转 md，便于阅读/进知识库/给AI处理
- 财税资料（清税证明、判决书、报表）文字提取
- 图片中的中文文字识别
