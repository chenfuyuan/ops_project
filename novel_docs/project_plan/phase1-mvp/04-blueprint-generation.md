---
title: Phase 1 — 章节蓝图生成
version: 1.0
date: 2026-04-20
---

# 章节蓝图生成

## 概述

基于大纲的三幕结构，生成每一章的结构化蓝图。借鉴 AI_NovelGenerator 的蓝图设计，每章蓝图包含叙事定位、悬念密度、伏笔操作等标注，为后续章节生成提供精确指导。

## 输入

- 大纲三幕结构（`novel_architecture.three_act_structure`）
- 角色列表（`characters` 表）
- 世界观（`novel_architecture.world_building`）
- 小说配置（目标章节数、每章字数）

## 输出

每章一条 `chapter_blueprints` 记录，包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| chapter_num | int | 章节序号 |
| title | str | 章节标题 |
| positioning | str | 角色/事件/主题定位——本章聚焦什么 |
| core_function | enum | advance（推进）/ twist（转折）/ reveal（揭示）/ setup（铺垫）/ climax（高潮） |
| suspense_density | int(1-5) | 悬念密度：1=舒缓，5=极度紧张 |
| foreshadow_ops | json | 伏笔操作列表 |
| disruption_level | int(1-5) | 认知颠覆度：读者预期被打破的程度 |
| summary | str | 一句话概要 |

### 伏笔操作格式

每条伏笔操作包含：op（plant 植入 / reinforce 强化 / harvest 收获）、description（操作描述）、target_foreshadow（关联的伏笔名称）。例如：植入"暗示玉佩与上古宗门有关"，关联伏笔"玉佩的秘密"。

## 生成策略

### 批次生成

长篇小说（200+ 章）不能一次生成全部蓝图，按批次处理：

- 每批 20 章
- 每批的 LLM 输入包含：三幕结构中对应部分 + 已生成的前一批蓝图摘要
- 批次间保持连贯性：上一批最后 3 章的蓝图作为下一批的上下文
- 支持续写：自动检测已生成的最大章节号，从下一章开始；也可手动指定起始章节

### 悬念单元规划

章节按 3-5 章为一个"悬念单元"分组，遵循节奏曲线：

```
悬念单元（5 章示例）:
  Ch1: suspense=3 (铺垫)
  Ch2: suspense=4 (升级)
  Ch3: suspense=5 (高潮)
  Ch4: suspense=2 (缓冲/反思)
  Ch5: suspense=4 (新悬念引入)
```

LLM 提示词中明确要求按悬念单元规划节奏，避免连续多章同一张力水平。

### 伏笔分布规划

LLM 提示词中要求：
- 第一幕：以 plant（植入）为主，每 3-5 章至少植入一个伏笔
- 第二幕：plant + reinforce 混合，已有伏笔定期强化
- 第三幕：以 harvest（收获）为主，确保所有重要伏笔在结局前收获

生成蓝图时，LLM 需要参考大纲中的伏笔布局计划（`foreshadowing_plan`），确保蓝图与大纲一致。

## LLM 提示词结构

蓝图生成的提示词包含小说基本信息（类型、总章节数、每章字数）、大纲中对应当前批次的三幕结构部分、角色列表摘要、以及前一批最后 3 章的蓝图作为上下文。

要求 LLM 输出 JSON 数组，每章包含 title、positioning、core_function、suspense_density(1-5)、foreshadow_ops、disruption_level(1-5)、summary 字段。同时要求按 3-5 章为一个悬念单元规划节奏，伏笔操作需与大纲的伏笔计划一致。

## 人工编辑

蓝图生成后，用户可以：
1. 查看全部蓝图列表（表格视图）
2. 编辑单章蓝图的任何字段
3. 调整悬念密度（可视化滑块）
4. 添加/删除/修改伏笔操作
5. 重新生成指定批次（不影响其他批次）
6. 插入新章节或删除章节（自动重新编号）

## 蓝图与伏笔台账的联动

蓝图中的 `foreshadow_ops` 在保存时自动同步到 `foreshadowing` 表：
- `plant` 操作 → 创建新的 foreshadowing 记录（status=open）
- `harvest` 操作 → 标记对应 foreshadowing 的预期收获章节

这是蓝图层面的"计划"，实际的伏笔状态更新在章节生成后的 Reflector 阶段执行。
