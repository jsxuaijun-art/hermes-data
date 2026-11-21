---
title: 命名与组织规范
type: conventions
last-updated: 2026-06-15
---

# 命名与组织规范

## 文件命名

- 日期笔记：YYYY-MM-DD.md 或 YYYY-MM-DD-一句话标题.md
- 项目笔记：20-Projects/客户简称-主题.md
- 知识笔记：30-Knowledge/主题分类/具体概念.md
- 模板：99-Templates/类型-用途.md

## 标签

- 顶层标签：#moc (Map of Content)、#daily、#project、#knowledge、#ai-memory
- 状态标签：#todo、#in-progress、#done、#archived
- 优先级：#p0、#p1、#p2

## Frontmatter 必备字段

```yaml
---
title: 笔记标题
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## 链接

- 内部链接：[[笔记名]] 或 [[笔记名|显示文字]]
- 跨目录引用：[[20-Projects/某客户/README]]

## 双向链接约定

- 项目笔记里用 [[30-Knowledge/某概念]] 反向引用知识
- 知识笔记里用 [[20-Projects/某客户]] 标注应用场景
- 每日笔记用 [[20-Projects/...]] 标注今天的事归属哪个项目
