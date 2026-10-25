# 财税交付约定——桌面路径与 docx 生成

## 交付路径

- Windows 桌面 = `/mnt/c/Users/jiangmin/Desktop/`（WSL 下映射）。确认过存在 `jiangmin` 账户；若系统提示用户不同，先 `ls /mnt/c/Users/*/Desktop` 确认真实桌面目录。
- 交付章/协议/清单/报告时：生成 .docx 放桌面并**报告绝对路径**；同时可给一份 .md 便于随手编辑。
- 批量交付（主协议 + 附件/清单）可打包 zip 或逐一放桌面，并列出全部文件名。

## docx 生成（docx skill 脚本）

- 用 `python3` 调脚本（环境无裸 `python`）：
  - `python3 <docx_skill>/scripts/docx_create.py spec.json out.docx` 创建；
  - `python3 .../docx_read.py out.docx --structure / --text` 校验结构/正文；
  - `python3 .../docx_validate.py out.docx` 健康检查；
  - 拷贝到桌面 `cp out.docx /mnt/c/Users/jiangmin/Desktop/` 并 `ls -la` 确认。
- spec.json 支持 blocks: heading / paragraph / bullet_list / numbered_list / table / page_break。
- **坑: 自定义样式名别与 python-docx 默认模板内置重名**（如 `Title`）→ 报 `document already contains style`。用不冲突的名字（如 `DocTitle`）；内置样式名（Heading 1、List Bullet/Number、Table Grid）直接可用。
- 中文正文用默认字体即可；需要时在 `styles` 里显式设 font + size_pt + color。
- 验证习惯：创建后 `--structure` 看标题大纲、`--text` 抽查关键条目，避免空文档/段落错位。

## 文档风格（此用户偏好）

- 财税服务协议/清单结尾常给“可转发客户”的一句话总结，并主动询问是否补附件（授权书、风险告知书、承诺函等）或打包。
- 涉及责任/风险条款时，明确划合规底线（法律强制不可免责的部分），不要为了讨好而承诺不可能的保护。
