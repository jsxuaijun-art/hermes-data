# Unsplash Photo ID 图库（公众号配图）

## 使用说明

服务器从阿里云ECS访问Unsplash CDN可能超时，以下Photo ID已验证可用。

下载命令模板：
```bash
ssh root@47.103.27.171 "curl -sL -o /var/www/html/images/<filename>.jpg 'https://images.unsplash.com/photo-<PHOTO_ID>?w=400&q=60' -w '%{http_code}'"
```
参数 `w=400&q=60` 减低分辨率加速下载（含文字的文章够用）。

下载后必须验证完整性：`file /var/www/html/images/<filename>.jpg`，输出应为"JPEG image data"而非"data"。

## 政府/政策类

| 场景 | Photo ID | 文件名建议 |
|:-----|:---------|:-----------|
| 政府办公大楼 | 1517245386807-bb43f82c33c4 | cover_gov, section_gov |
| 办税大厅/税务 | 1504639725590-34d0984388bd | section_taxhall |

## 科技/研发类

| 场景 | Photo ID | 文件名建议 |
|:-----|:---------|:-----------|
| 科技企业研发车间 | 1532094349884-543bc11b234d | section_factory |
| 实验室科研场景 | 1581091226825-a6a2a5aee158 | section_techlab |
| 科技/工业设备 | 1581092335397-9583eb92d2c1 | section_tech |

## 商务/办公类

| 场景 | Photo ID | 文件名建议 |
|:-----|:---------|:-----------|
| 现代写字楼 | 1486406146926-c627a92ad1ab | cover_building |
| 明亮办公室 | 1497366216548-37526070297c | section_office |
| 办公+数据图表 | 1554224155-6726b3ff858f | section_chart |
| 签约/文件 | 1450101499163-c8848c66ca85 | section_sign |
| 城市CBD天际线 | 1480714378408-67cf0d13bc1b | cover_city |
| 商务会议/讨论 | 1519389950473-47ba0277781c | section_meeting |

## 数据/财务类

| 场景 | Photo ID | 文件名建议 |
|:-----|:---------|:-----------|
| 数据分析/大屏 | 1551288049-bebda4e38f71 | section_datascreen |
| 财务计算/算账 | 1554224155-6726b3ff858f | section_finance |
| 数据报表/增长图表 | 1460925895917-afdab827c52f | section_checklist, section_report |
| 财务账单/算账 | 1554224154-26032ffc0d07 | section_lowprice, section_calc |

> 以上 1460925895917、1554224154 两条为 2026.8.5 自查通知文章实配验证（WSL 直链可下载，JPEG 有效）。

## 会议/商办类（2026.8.5 补充验证）

| 场景 | Photo ID | 文件名建议 |
|:-----|:---------|:-----------|
| 会议室讨论 | 1542744173-8e7e53415bb0 | section_tips, section_meeting2 |
| 商务办公协作 | 1556761175-b413da4baf72 | section_office2 |
| 商务会议/文件 | 1517048676732-d65bc937f952 | section_policy, cover_doc |
| 天秤/法令司法 | 1543286386-713bdd548da4 | section_law |
