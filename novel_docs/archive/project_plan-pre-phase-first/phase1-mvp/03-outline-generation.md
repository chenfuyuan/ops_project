---
title: Phase 1 — 大纲生成（雪花写作法）
version: 1.0
date: 2026-04-20
---

# 大纲生成（雪花写作法）

## 概述

借鉴 AI_NovelGenerator 的雪花写作法，将大纲生成拆为 5 个顺序步骤，每步一次 LLM 调用。每步产物持久化，支持断点续跑和人工编辑。

## 五步流程

### Step 1: 核心种子 (Core Seed)

**输入：** 用户提供的小说前提（premise）、类型（genre）、语言（language）

**LLM 提示词要点：**
- 将前提浓缩为一句话的故事本质公式
- 格式："当[主角]遭遇[事件]，必须[行动]，否则[灾难]；同时[隐藏危机]酝酿"
- 要求包含：核心冲突、主角驱动力、风险/赌注、潜在的深层矛盾

**输出：** 一段文本（core_seed），存入 `novel_architecture.core_seed`

**示例输出：**
> 当落魄修士陈墨意外获得上古传承，必须在三大宗门的追杀中成长为足以自保的强者，否则不仅自身难保，还将连累收留他的小村庄；同时，传承中封印的远古邪灵正借他的修炼悄然苏醒。

### Step 2: 角色动力系统 (Character Dynamics)

**输入：** core_seed + premise + genre

**LLM 提示词要点：**
- 设计 3-6 个核心角色
- 每个角色包含驱动力三角：
  - 表层追求（Surface Pursuit）：角色自认为想要的
  - 深层欲望（Deep Desire）：真正驱动行为的
  - 灵魂需求（Soul Need）：成长所必需的
- 弧线设计：初始状态 → 触发事件 → 认知失调 → 转变 → 终态
- 角色间关系冲突网：至少 3 对核心冲突关系

**输出：** 结构化角色列表，存入 `characters` 表

**每个角色的数据结构包含：**

| 字段 | 说明 |
|------|------|
| name | 角色名 |
| surface_pursuit | 表层追求——角色自认为想要的 |
| deep_desire | 深层欲望——真正驱动行为的 |
| soul_need | 灵魂需求——成长所必需的 |
| arc_design | 弧线设计：initial → trigger → dissonance → transformation → final |
| relationship_web | 与其他角色的关系及冲突描述 |

### Step 3: 角色初始状态 (Initial Character State)

**输入：** core_seed + 角色列表

**LLM 提示词要点：**
- 为每个角色生成详细的初始状态表
- 包含：持有物品、能力列表、身体状态、心理状态、当前位置、关系网快照、即将面临的触发事件

**输出：** 存入 `character_states` 表（chapter_num=0）

**数据结构：** 每个角色的初始状态记录（chapter_num=0）包含：

| 字段 | 说明 |
|------|------|
| character_id | 角色 ID |
| chapter_num | 0（表示初始状态） |
| items | 持有物品列表 |
| abilities | 能力列表 |
| physical_state | 身体状态描述 |
| mental_state | 心理状态描述 |
| location | 当前位置 |
| relationships | 与其他角色的关系快照（类型、信任度、备注） |
| key_events | 即将面临的触发事件 |

### Step 4: 世界观构建 (World Building)

**输入：** core_seed + 角色列表 + genre

**LLM 提示词要点：**
- 构建三维世界：
  - 物理维度：地理、气候、资源分布、重要地标
  - 社会维度：势力格局、权力结构、文化习俗、经济体系
  - 隐喻维度：世界规则如何映射主题（如修炼体系映射个人成长）
- 动态元素：世界中哪些因素会随角色决策而变化
- 与角色的交互点：世界设定如何制造冲突和机遇

**输出：** 文本，存入 `novel_architecture.world_building`

### Step 5: 三幕结构 (Three-Act Structure)

**输入：** core_seed + 角色列表 + 世界观

**LLM 提示词要点：**
- 设计三幕结构：
  - 第一幕（触发/建置）：约占 25%，建立世界和角色，引入核心冲突
  - 第二幕（对抗/发展）：约占 50%，升级冲突，角色成长，多线交织
  - 第三幕（解决/高潮）：约占 25%，冲突总爆发，角色完成弧线
- 每幕包含：
  - 关键转折点
  - 嵌套反转（至少每幕 1 个意外反转）
  - 伏笔布局计划（哪些伏笔在哪一幕植入/收获）
  - 悬念因子（每幕结束时的悬念钩子）

**输出：** JSON 结构，存入 `novel_architecture.three_act_structure`

三幕结构数据包含 act1/act2/act3 三个部分，每幕包含：

| 字段 | 说明 |
|------|------|
| name | 幕名（触发/对抗/解决） |
| chapter_range | 章节范围，如 [1, 50] |
| summary | 本幕概要 |
| key_turning_points | 关键转折点列表 |
| reversals | 嵌套反转列表 |
| foreshadowing_plan | 伏笔布局计划（植入/收获） |
| suspense_hook | 本幕结束时的悬念钩子 |

## 检查点恢复

每步完成后更新 `novel_architecture.checkpoint` 字段。恢复逻辑：

1. 如果指定了 start_from，从该步骤开始
2. 否则读取 checkpoint 值，从 checkpoint+1 开始
3. 如果无 checkpoint，从第 1 步开始
4. 每步执行完毕后立即更新 checkpoint，确保中断后可恢复

## 人工编辑

每步生成后，用户可以：
1. 查看生成结果
2. 直接编辑文本/JSON
3. 保存修改
4. 选择重新生成当前步骤（会覆盖当前结果）
5. 继续下一步（使用编辑后的结果作为输入）

前端需要为每步提供编辑器：
- Step 1, 4: 纯文本编辑器
- Step 2, 3: 结构化表单 + JSON 编辑器
- Step 5: 结构化表单（三幕各自展开）
