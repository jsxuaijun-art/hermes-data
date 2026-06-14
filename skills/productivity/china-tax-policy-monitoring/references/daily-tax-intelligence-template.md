# 财税战略情报中心 — 每日报告模板

## 模板结构说明

这是一个 markdown 模板文件，配合 `daily_tax_loader.py` 使用。模板中的 `{{DATE_YYYY-MM-DD}}` 和 `{{DOW_CN}}` 由加载脚本在运行时替换。

实际文件路径：`~/.hermes/cron/daily_tax_intelligence.md`

## 信息源（15个，执行时至少覆盖5个）

1. 国家税务总局 www.chinatax.gov.cn
2. 财政部 www.mof.gov.cn
3. 证监会 www.csrc.gov.cn
4. 工信部 www.miit.gov.cn
5. 国家发改委 www.ndrc.gov.cn
6. 国家市场监督管理总局 www.samr.gov.cn
7. 国家数据局
8. 中国税务报 www.ctaxnews.com.cn
9. 上海市税务局 shanghai.chinatax.gov.cn
10. 江苏省税务局 jiangsu.chinatax.gov.cn
11. 浙江省税务局 zhejiang.chinatax.gov.cn
12. 广东省税务局 guangdong.chinatax.gov.cn
13. 北京市税务局 beijing.chinatax.gov.cn
14. 四大会计师事务所研究报告
15. 中国政府网 www.gov.cn

## 输出格式

# 财税战略情报中心 — 每日报告
日期：{YYYY-MM-DD}（星期{X}）

### 一、今日热点摘要（5-10条）
每条格式：标题、来源[链接]、要点、影响评估

### 二、重点案例拆解（3-5个）
每个案例：行业、风险行为、发现机制、处罚金额、定性逻辑、企业启示

### 三、风险提醒
- 企业自查建议
- 高端客户行动建议

### 四、内容营销素材
- 视频号选题 × 3条
- 抖音选题 × 3条
- 小红书选题 × 2条
- 客户咨询切入口 × 1条

### 五、数据来源
逐一列出所有引用来源URL

## 推送标记
- 周一/三/五：报告顶部加 ⚠️ 本报告需发送至企业微信群
- 其他日：报告顶部加 📁 报告已存档，无需推送
