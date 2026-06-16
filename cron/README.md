# 财税情报定时任务

## 任务结构

### 任务1：每日财税监控（每天07:00）
- 文件：daily_tax_intelligence.md (提示词)
- 产出：~/tax_intel/daily/YYYY-MM-DD.md
- 内容：任务1（每日核心监控）+ 任务7（内容营销素材）

### 任务2：每周深度分析（每周一08:00）
- 文件：weekly_tax_deep_dive.md (提示词)
- 产出：~/tax_intel/weekly/YYYY-WW.md
- 内容：任务3（每周深度分析）+ 任务8（趋势预测）

## 推送机制（待配企微Webhook）
- 周一：推送每日+每周两篇
- 周三：推送每日
- 周五：推送每日

## 目录结构
~/tax_intel/
├── daily/      # 每日报告
├── weekly/     # 每周报告
└── monthly/    # 每月报告（预留）
