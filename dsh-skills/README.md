# DeepSeek Harness 盈信技能库（由 Hermes Agent 迁移）

生成日期：2026-11-21
来源：Hermes Agent (~/.hermes/skills) → DeepSeek Harness 用户级 skill 根目录
数量：91 个 skill · 全部平铺为顶级目录，每个含 SKILL.md + references/scripts/资源

## 作用
提供盈信企业管理（苏州）的业务知识、话术、财税技能，供 DeepSeek Harness 按需调用。

## 内容分布
- 税种/政策（33）：tax-vat / tax-enterprise-income / tax-individual-income / tax-law / tax-policy-qa / tax-audit-response / tax-regulation-monitor / tax-incentive-policy 等
- 公司/商事（10）：company-registration / company-deregistration / suzhou-equity-transfer-guide / holding-company-firewall 等
- 盈信业务/法务/销售（19）：yingxin-business-suite / yingxin-legal-advisor / price-negotiation / sales-communication / company-law / civil-code / criminal-law 等
- 内容/公众号/短视频（21）：wechat-publish / wechat-qa-publish / short-video-* / xiaohongshu / geo-optimization / humanizer-zh 等
- 文书交付（10）：docx / word-documents / minimax-docx / xlsx / pptx-generator / officecli 等

## 合规校验
- 91/91 含 SKILL.md
- frontmatter name 均为 kebab-case 且与目录名一致（wechat-article-typeset 已修正）

## 完整清单
- auto-douyin-editor
- business-registration-advisor
- china-tax-compliance
- china-tax-policy-advisory
- chinese-business-doc-templates
- civil-code
- client-communication
- client-group-welcome
- cn-regulation-verification
- company-deregistration
- company-law
- company-registration
- compliant-accounting
- corporate-tax-planning
- criminal-law
- deliverable-handoff
- docx
- dual-model-content-pipeline
- enterprise-diagnostic
- enterprise-visit-biz-handoff
- enterprise-visit-biz-handoff-tax
- equity-architecture-guide
- financial-mini-program
- financial-statement-analysis
- ga-xin-accounting-ops-v2
- ga-xin-tax-knowledge
- generate-docx-without-python-docx
- geo-optimization
- gxrd-client-ops
- holding-company-firewall
- hong-kong-finance-tax
- humanizer
- humanizer-zh
- manager-xu-business-registration
- markdown-to-word-converter
- minimax-docx
- officecli
- overseas-client-acquisition
- peng-accounting-douyin-style
- platform-qualification-certification
- pptx-generator
- price-negotiation
- sales-communication
- short-video-ad
- short-video-city-breakout
- short-video-copywriting
- short-video-fun-breakout
- short-video-general
- short-video-industry-flow
- suzhou-equity-transfer-guide
- tax-admin
- tax-audit-response
- tax-consumption
- tax-content-creation
- tax-content-factbase
- tax-deed
- tax-enterprise-income
- tax-environment
- tax-farmland
- tax-incentive-policy
- tax-individual-income
- tax-land-appreciation
- tax-law
- tax-planning-fin-analysis-industry
- tax-policy-qa
- tax-regulation-monitor
- tax-resource
- tax-risk-self-check-report
- tax-service-skill-design
- tax-ship-tonnage
- tax-stamp
- tax-tariff
- tax-tobacco
- tax-urban-maintenance
- tax-vat
- tax-vehicle-purchase
- tax-vehicle-vessel
- video-to-article
- wechat-article-search
- wechat-article-typeset
- wechat-comic-cells
- wechat-moments-marketing
- wechat-publish
- wechat-qa-publish
- word-documents
- xiaohongshu-marketing
- xlsx
- yingxin-brand-taglines
- yingxin-business-suite
- yingxin-legal-advisor
- yingxin-online-presence

## 维护与同步
此目录随 hermes-data 仓库（git@github.com:jsxuaijun-art/hermes-data）四机同步。
改一处 → push → 各机 pull → 重启 DSH 生效。请勿在此放真实客户/凭证等敏感材料。
