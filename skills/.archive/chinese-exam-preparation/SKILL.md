---
name: chinese-exam-preparation
title: Chinese Professional Exam Preparation
description: Create structured study plans for Chinese professional certification exams — 税务师, 注册会计师(CPA), 中级会计, 法律职业资格, 建造师, etc. Covers exam schedule research, subject analysis, phased timeline planning, teacher/platform recommendations, and study strategy.
trigger: user asks to plan for a Chinese professional exam, create a study schedule, recommend teachers or training platforms, or build a 备考计划/学习规划 for 税务师/CPA/中级会计/法考/建造师/教师资格等
category: productivity
---

# Chinese Professional Exam Preparation

Create comprehensive exam preparation plans for Chinese professional certifications. This skill encodes the workflow for researching exam schedules, analyzing subjects, building multi-phase timelines, and recommending teachers from platforms like 中华/东奥/斯尔/之了/BT教育.

## Workflow

### 1. Identify Exam & Confirm Schedule

Chinese professional exams have schedules published annually by the Ministry of Human Resources and Social Security (人社部) around January. Confirm the current year's dates:

- Registration period (报名时间 / 补报名时间)
- Exam dates (考试时间)
- Score release window
- Subject arrangement per exam day (各科目具体安排)

Official sources (in priority order):
  1. The exam's official association website (e.g. cctaa.cn for 税务师, cicpa.org.cn for CPA)
  2. 人社部 annual professional exam plan notice
  3. Major training platforms' exam guide pages

### 2. Analyze Each Subject

For each subject the user wants to take, record:

| Attribute | Notes |
|-----------|-------|
| Difficulty | ★–★★★★★, relative to other subjects in the same exam |
| Duration | Hours per exam session |
| Question types | Multiple choice, multiple-select, calculation, short answer, comprehensive |
| Prerequisites | Subjects that MUST be studied first |
| Core chapter weight | Identify the ~20% of chapters that carry ~80% of exam points |
| Pass rate | Typical pass rate (for reference only — not a constraint) |

### 3. Determine Subject Ordering

**Dependency rule**: Subjects with content prerequisites must be scheduled after their foundation subjects.

Common dependency chains:
- 税务师: 税法一 + 税法二 → 涉税服务实务
- CPA: 会计 → 审计 / 税法 / 财务成本管理
- 中级会计: 中级会计实务 → 经济法 / 财务管理

**Cross-scheduling strategy**: Independent subjects (e.g. 涉税相关法律 in 税务师) can run in parallel with foundation subjects.

### 4. Build Phased Timeline

Calculate available months from now to the exam date. Divide into four phases:

| Phase | % of total time | Goal |
|-------|----------------|------|
| Foundation (基础阶段) | ~50% | Complete basic course (基础班) + chapter exercises for all subjects |
| Strengthening (强化阶段) | ~30% | Cross-chapter exercises, past exam papers (真题), subject-specific skill drills |
| Mock exam (真题阶段) | ~15% | Full timed mock exams (套卷), detailed error analysis |
| Sprint (冲刺阶段) | ~5% | Error review, formula/memorization cramming, full-timing simulation |

**For part-time candidates** (working professionals), specify daily time blocks:
- Morning (30-60 min): memorization / light review
- Lunch/commute (20-40 min): mobile app MCQ practice
- Evening (2-3 h): deep learning — 1 subject per night
- Weekend (5-6 h): 2 subjects, split morning/afternoon

### 5. Teacher & Platform Recommendations

Organize recommendations by subject. For each teacher:

- Name
- Current platform affiliation (中华/东奥/斯尔/之了/BT教育/环球网校)
- Teaching style (条理清晰/举例生动/重点突出/体系完整/口诀记忆)
- Best suited for (零基础/有基础/强化/冲刺)
- Recommended course pairing (基础班 → 习题班 → 冲刺班)

**How to research teachers** when uncertain:
- Search "【考试名】 【科目】 老师推荐" on 知乎
- Search Bilibili for course previews / free lessons of specific teachers
- Check the current year's platform course catalog (teachers change platforms over time)

Common platform profiles:
- **中华会计网校（正保）**: Comprehensive, strong in 税法/实务/法律, veteran teachers
- **东奥会计在线**: Strong in 会计/财管/税法, high-quality习题
- **斯尔教育**: Modern teaching style, fast-paced, good for structured learners
- **之了课堂**: Budget-friendly, free basic courses available
- **BT教育**: Exam-oriented, framework-based, good for sprinters

### 6. Subject-Specific Strategy

For each subject, include:
- Core chapters with approximate exam weight (%)
- Common failure points / tricky topics
- Recommended practice volume
- Time allocation during the exam session
- Formula/memorization aids
- Whether the subject rewards brute-force memorization vs. conceptual understanding

### 7. Output Format

Deliver the plan as either:
- A structured **Word document** (use the word-documents skill) with tables, phase timelines, and teacher reference cards
- A **terminal summary** with inline tables for quick reference if the user just wants the highlights

## Pitfalls

1. **Stale schedules**: Exam dates change annually. Always confirm the current year's official schedule from the association website, not from last year's documents or memory.

2. **Teacher platform churn**: Popular teachers switch platforms frequently (中华→东奥→斯尔). A teacher's well-known affiliation may be outdated. Check the current year's course catalog before recommending.

3. **Prerequisite ordering**: Subjects with content dependencies (e.g. 涉税服务实务 depends on 税法一/二) must appear later in the timeline. Recommending them in parallel is a real trap.

4. **Grade inflation pressure**: When the user lists multiple subjects, suggest a realistic pass target (e.g. "保三争四") based on available months and work status, rather than assuming all must pass in one sitting. Chinese exam scores typically roll over multiple years (税务师/CPA: 5 years, 中级: 2 years).

5. **Official source over third-party**: For registration dates, fees, and requirements, prefer the official association website. Third-party aggregators (考试吧, 233网校) are useful for study materials but sometimes publish stale or copy-pasted dates.

6. **Study-what-you-like trap**: Users often want to start with the easiest subject for confidence. But subjects with dependencies must come first regardless of difficulty — skipping the prerequisite subject wastes time when the dependent subject requires it.

7. **Over-reliance on audio courses**: 涉税相关法律 and similar memory-heavy subjects benefit from audio review during commutes. But calculation-heavy subjects (税法二, 实务) need active problem-solving practice — passive listening is not enough.

## Saved Reference Contents

See `references/2026-tax-agent-exam.md` for the full 税务师 (Tax Agent) 4-subject study plan generated in this session, including the complete teacher recommendation matrix, weekly schedule by phase, and subject weight analysis.
