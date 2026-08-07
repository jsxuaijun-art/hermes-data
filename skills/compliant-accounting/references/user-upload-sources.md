# 用户已上传源文件（待处理）

以下为用户上传的原始材料路径，解压操作待用户确认后执行。

## 2026.5.18 会话中的上传

- **合规账工具包**：`/mnt/d/OneDrive/Desktop/合规账.zip`
  - 大小：~222 MB，78 个文件
  - 含：话术、协议、流程工具、产品手册、薪酬设计、百问百答等
  - 状态：❌ 用户尚未允许解压

- **盈信 LOGO**：`/mnt/f/BaiduNetdiskDownload/logo.jpg`
  - 大小：~32 KB
  - 状态：待嵌入文档

## 处理计划（待用户确认后执行）

1. 解压到 `/tmp/compliant-accounting/`
2. 逐文件读取分析
3. 替换所有第三方公司名为"盈信"
4. 清理水印/页眉页脚
5. 嵌入 LOGO
6. 按 `01_洽谈/02_签约/03_交付/04_质检/05_知识库` 框架整理
7. 输出到桌面 `D:\360MoveData\Users\Admin\Desktop\合规账-整理包\`
8. 推送 GitHub

## 参考关联

- 现有 `compliant-accounting` 技能已包含标准框架
- `corporate-tax-planning` — 税务筹划引用
