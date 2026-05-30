# 南通卡曼案例：完整方案生成工作流

## 背景

南通卡曼体育用品有限公司（主营阿迪达斯/耐克零售）
- 结构：卡曼（南通，一般纳税人，~1000万/年）→ 2家分公司（苏州高铁新城，已开业1年，一盈一亏）
- 模式：耐克→瑞丽（代理商，开专票）→卡曼采购→分公司零售
- 关键参数：POS入其他账户，返利按年结算，员工社保未确认

## 执行步骤

### Step 1: 读取已确认信息清单 (.docx)

使用纯 stdlib 读取：

```python
import zipfile, xml.etree.ElementTree as ET
z = zipfile.ZipFile(path, 'r')
root = ET.fromstring(z.read('word/document.xml'))
# 提取所有段落文本
texts = []
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    para_text = ''.join(t.text or '' for t in p.iter(...))
    texts.append(para_text)
```

### Step 2: 读取已有案例文件

路径：`reference-material-integration/coze-tax-agent-prompt/references/case-nt-sports.txt`

发现原有案例已过时（个体户→分公司结构变更），需要重写。

### Step 3: 交叉比对 + 优先级分类

DOCX 中的"确认"列与原有未确认项逐项比对：

| 原状态 | 新确认 | 结论 |
|--------|--------|------|
| 待确认 | 已超500万 | P0 ✅ 核心确认 |
| 待确认 | 一般纳税人 | P0 ✅ 核心确认 |
| 待确认 | 其他账户 | P0 ⚠️ 需进一步确认 |
| 待确认 | 未填（社保） | P1 ❌ 仍待补充 |

### Step 4: 生成完整方案（多模块）

方案结构（按优先级和税种排列）：
1. 架构全景 — 更新了结构树
2. 11项确认状态表 — 标注P0/P1/P2 + ✅⚠️❌⬆️
3. 分税种分析 — 增值税/所得税/个税/社保/返利 逐项
4. 风险矩阵 — 5项，🔴🟡🟢 三级
5. 方案对比 — 方向A（推荐）vs 方向B（排除）
6. 实施路线图 — 6步，含时间线
7. 法规索引 — 5条关键法规+文号

### Step 5: 双格式交付

- 终端：使用 box_maker.py 的 make_grid_table() / make_box()
- 桌面文件：`D:\360MoveData\Users\Admin\Desktop\南通卡曼_税务筹划与合规方案.docx`

## 关键教训

1. **永远优先看已确认信息**，而不是从头开始分析
2. **P0 信息决定方案路径** — POS资金流向异常直接影响了风险等级排序
3. **已有案例文件要立即更新** — 旧版"3家个体户"结构会误导后续分析
4. **社保未确认是个坑** — 容易忽略但影响企业所得税分配和合规
5. **返利入账方式** — 体育用品行业常见但容易被忽略的税务点

## 输出文件清单

- 案例文件（已更新）：`references/case-nt-sports.txt`
- 终端报告（已生成）：本轮对话终端输出
- Word方案（已交付）：桌面 .docx
