# Skill 合并速查（2026-09 实操：5话术skill → sales-communication）

## 触发词定位速查（合并后）

| 旧 skill | 去向 |
|---|---|
| price-negotiation / enterprise-diagnostic / client-group-welcome / client-communication | 全部并入 `communication/sales-communication`（触发词：话术/沟通/沟通建议） |
| yingxin-business-suite 的 S1-S5 销售 | 跳转 sales-communication；财税咨询/GEO/公众号/朋友圈 四大子系统保留在原 skill |
| 内容创作类（短视频/朋友圈/公众号） | 边界约定：独立保留，不并入话术母skill |

## 母skill 目录结构（参考样板）

```
communication/sales-communication/
├── SKILL.md                          # 9阶段框架（新客线1-4 + 存量线5-9）
└── references/
    ├── 00-核心弹药库/                # S1-S5弹药库、话术精炼库、实战经验-销售客户等
    ├── 02-首次接触/                  # 企业诊断、建群开场、初次洽谈SOP
    ├── 03-价值塑造与报价/            # 洽谈话术大库、低价反杀
    ├── 05-关系维护/                  # 客户沟通三段式、通知话术
    ├── 07-老客户压价/ 08-续费/       # 压价应对、续费话术
    └── canonical-identity-anchor.md  # 身份锚点（跨skill共享）
```

## 合并执行清单（浓缩版）

1. `search_files`(files) 列每个源 skill 完整文件树 —— 别只看 SKILL.md
2. 与用户确认边界（哪些并入、哪些保留独立）
3. 建母skill：类级名 + 触发词 + 分阶段框架
4. 逐文件复制 references + 源 SKILL.md 正文另存为 reference
5. **删源前逐文件比对清单**（`ls <src>/references/...` 对照）—— 本实操漏拷过 `us-eu-textile-export-certification.md`(7.5KB)，靠保底补回
6. 伞skill：已并入部分换跳转，操作性文件（凭据/清单）移到 references 根保留
7. grep 伞skill 无残留引用 → rm -rf 源 skill
8. 验证：母skill linked_files 生效 + 被删 skill 消失 + 伞skill 跳转正常

## 坑

- **rm 后验证必须串行**：破坏性操作后在同一批并行工具调用里查存在性会读到删除前旧状态 → 误判"被神秘恢复"。判据：mtime 是旧时间戳 = 从未真删。单独等几秒再查。
- **引用断链**：删源后其它 skill 指向旧名的引用会断（本库 memory-management 仍有指向已删 skill 的陈旧行，属用户自有 skill，需 `hermes curator adopt` 后才能由 curator 修正）。
