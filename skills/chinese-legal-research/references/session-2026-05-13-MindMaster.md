# Session Reference: MindMaster 终身使用权纠纷 (2026.5.13)

## Case Details

| Field | Value |
|-------|-------|
| Software | 亿图脑图MindMaster (深圳市亿图软件有限公司) |
| Purchase | 终身使用权 + 终身维护服务 |
| Breach | 公司单方发布公告停止服务 |
| Court | 苏州工业园区人民法院 |
| Claim | 更换同等价值其他软件（不要求退费） |
| User | 苏州/上海财税行业老板 |

## Evidence Retrieved During Session

### 1. Opponent's EULA (live version from edrawsoft.cn)

URL: https://www.edrawsoft.cn/mindmaster/term.html

Key clauses found relevant to the dispute:

**第2条 许可授予**: "本协议授予的许可权是**可撤销的**" — the license itself is described as revocable, which is an important point for the格式条款 attack

**第8条 期限**: 区分了"永久许可"（可一直使用直至协议终止）和"指定有效期限的软件" — note that even "永久许可" is limited by "直至协议终止"

**第10条 软件更新**: "一旦更新版本发布，许可方可以**停止对先前版本的服务或支持**，而不向被许可方发出任何通知。许可方可以在更新软件或升级软件中添加新功能...或**删除原始功能**...被许可方对此不持异议。" — **This is the single most important clause**. It explicitly reserves the right to stop service and delete features without notice.

**第12条 支持**: "许可方在此没有义务为被许可方提供与软件相关的任何技术支持服务。" — disclaims any support obligation entirely.

### 2. Subscription Agreement (live version)

URL: https://www.edrawsoft.cn/mindmaster/subscription-agreement/

Only covers 连续包月 (auto-renewal subscription), not lifetime licenses. Not directly relevant to this dispute.

### 3. Complaint Platform Results

From 新浪黑猫投诉:
- Multiple complaints about MindMaster refunds (minor buying membership, etc.)
- Pattern: Many users confused about terms, auto-renewal charges

From Zhihu:
- Questions discussing MindMaster policy changes
- User complaints about service termination

### 4. Company Background

- Developer: 深圳市亿图软件有限公司 (Shenzhen Yimu Software Co., Ltd.)
- Parent: 万兴科技 (Wondershare Technology, A-share listed: 300624)
- This matters: a listed company being sued provides additional PR leverage

## Search Strategies That Worked

| Search Engine | Query | Result |
|---------------|-------|--------|
| Sogou (搜狗) | `MindMaster 终身 许可 投诉` | Found 黑猫投诉 pages |
| Sogou | `MindMaster 停止服务` | Found Zhihu articles |
| Bing | `MindMaster lifetime license terminated` | Found CSDN, Zhihu, official pages |
| Direct curl | `edrawsoft.cn/mindmaster/term.html` | ✅ Full EULA retrieved |

## Search Strategies That Failed

| Attempt | Reason |
|---------|--------|
| wenshu.court.gov.cn direct API | Anti-scraping (CAPTCHA + JS token) |
| wenshu.court.gov.cn via REST endpoints | 404/blocked |
| Google `site:wenshu.court.gov.cn` | Network/firewall limitations |
| 天眼查/企查查 API | Subscription required |
| 北大法宝 API | Subscription required |

## Legal Arguments Developed

See the代理词 at `D:\360MoveData\Users\Admin\Desktop\MindMaster代理词_苏州工业园区法院.docx`

Four-core argument structure proved effective:

1. **根本违约** — 民法典第509条 + 第577条
   - "终身使用权"是合同实质性条款
   - 合同目的完全落空

2. **格式条款无效** — 民法典第496条 + 第497条
   - 第10条的"可随时停止服务"排除了原告主要权利
   - 第12条的"无支持义务"同样无效
   - 被告未尽合理提示说明义务

3. **"更换"有据** — 民法典第582条
   - 更换是法定补救措施
   - 不要求退费 → 强化善意 → 减轻法官顾虑（三重优势论证法）

4. **诚信原则** — 民法典第7条
   - 承诺在先 → 收费 → 停服，三步走完全违背诚信

## Tips for Similar Cases

- **Always retrieve the opponent's current EULA** — it documents their legal position and gives you concrete clauses to attack
- **The "不要求退费、只要求更换" strategy is a strong rhetorical position** — it reframes the case from "customer demanding money back" to "customer just wants what was promised"
- **Listed company defendants are more sensitive to reputation damage** — this may make them more amenable to settlement before judgment
- **When writing for a 苏州工业园区法院 case, use 苏0591 format for the case number placeholder**
- **The document should include a 预判与回应 section** — this shows the court you've thought through the opponent's arguments already
