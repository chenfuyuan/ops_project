---
title: Phase 1 — 章节生成流水线（简化版）
version: 1.0
date: 2026-04-20
---

# 章节生成流水线（简化版）

## 概述

Phase 1 实现简化版流水线：Plan → Compose → Draft → Commit。跳过 Audit 和 Revise（Phase 2 引入）。每步产出中间产物，持久化到 `pipeline_artifacts` 表。

## 流水线编排器

PipelineOrchestrator 管理单章生成的完整生命周期，按顺序执行四个阶段：Plan → Compose → Draft → Commit。

核心特性：
- 每阶段产出中间产物（artifact），持久化到 `pipeline_artifacts` 表
- 支持断点续跑：指定 resume_from 参数可从任意阶段恢复，之前的阶段从已有产物加载
- 如果恢复点之前缺少必要产物，报错

### PipelineContext

流水线上下文在各阶段间传递数据，包含：

| 字段 | 来源 | 说明 |
|------|------|------|
| novel_id | 输入 | 小说 ID |
| chapter_num | 输入 | 章节号 |
| chapter_intent | Plan 产出 | 写作意图 |
| context_payload | Compose 产出 | 分层上下文 |
| rule_stack | Compose 产出 | 规则列表 |
| draft_content | Draft 产出 | 章节全文 |
| chapter | Commit 产出 | 最终章节记录 |
| token_usage | 各阶段 | 每阶段的 token 消耗 |
| timing | 各阶段 | 每阶段耗时 |

## Stage 1: Plan（规划）

**执行者：** Planner Agent

**输入：**
- 大纲（novel_architecture）
- 当前章节蓝图（chapter_blueprint）
- 前一章摘要（chapter_summary of chapter_num-1）
- 活跃伏笔列表（status=open 的 foreshadowing）

**LLM 提示词结构：**

Planner 的提示词包含大纲概要（核心种子 + 当前幕结构）、本章蓝图（标题、定位、核心功能、悬念密度、伏笔操作）、前一章摘要和活跃伏笔列表，要求输出 must_keep / must_avoid / scene_guidance / foreshadow_instructions 四个部分。

**输出：** ChapterIntent，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| must_keep | list[str] | 必须包含的元素 |
| must_avoid | list[str] | 必须避免的内容 |
| scene_guidance | str | 场景节奏指导 |
| foreshadow_instructions | str | 伏笔操作指导 |
| estimated_scenes | int | 预估场景数 |

## Stage 2: Compose（上下文编译）

**执行者：** Composer（无 LLM 调用，纯本地逻辑）

**输入：**
- ChapterIntent（来自 Plan）
- DB 中的全部相关状态

**处理逻辑：**

调用 MemoryEngine.build_context() 执行简化版洋葱模型（Phase 1 跳过 T1），然后编译规则栈并生成输入追踪。具体步骤：

1. 构建上下文（洋葱模型）：调用 MemoryEngine，按 T0/T2/T3 分层组装上下文，总预算 30K tokens
2. 编译规则栈：包含目标字数、悬念密度目标等规则；第一章额外添加"建立世界观和引入主角"规则；Phase 3 会在此注入主题代理规则
3. 生成输入追踪（trace）：记录各层 token 用量和向量召回来源，用于调试和审计

**输出：**
- ContextPayload：分层组装的上下文
- Rule Stack：规则列表
- Trace：输入追踪（调试用）

## Stage 3: Draft（写作）

**执行者：** Writer Agent

**输入：**
- ContextPayload（来自 Compose）
- Rule Stack
- ChapterIntent（来自 Plan）

**LLM 提示词组装：**

Writer 将 ContextPayload、ChapterIntent 和 Rule Stack 组装为 system prompt + user prompt，通过 AIGatewayRouter 流式生成。生成过程中逐块通过 SSE 推送到前端。

**System Prompt 结构：** 包含写作规则列表和通用写作要求（场景驱动叙事、对话有潜台词、动作场景注重感官细节、保持前文一致性、章节结尾留悬念）。

**User Prompt 结构：** 按洋葱模型分层组织——T0（核心设定、角色锚点）、T2（近期剧情）、T3（向量召回的相关段落），加上本章写作意图（must_keep/must_avoid/scene_guidance/foreshadow_instructions）和蓝图信息。

**第一章特殊处理：**
- 没有"近期剧情"，替换为完整的世界观设定
- 增加"开篇指导"：建立世界观、引入主角、设置初始悬念
- 不包含向量召回（T3 为空）

**输出：** 章节全文（draft_content）

## Stage 4: Commit（提交）

**执行者：** 简化版 Reflector + 章后统一管线

Phase 1 的 Commit 阶段合并了 Reflector 和 PostChapterPipeline 的核心功能，执行步骤：

1. 保存章节文本到文件系统
2. 创建章节记录（status="final"，Phase 1 无审计）
3. LLM 提取状态变更（简化版 Reflector，见下文）
4. 持久化状态变更（摘要、角色状态、伏笔）
5. 向量索引（将章节分段存入 ChromaDB）

### 状态提取（简化版 Reflector）

一次 LLM 调用提取所有状态变更。提示词包含当前角色状态、活跃伏笔和本章内容，要求 LLM 以 JSON 输出以下结构化信息：

**ChapterDelta 输出结构：**

| 字段 | 类型 | 说明 |
|------|------|------|
| summary | str | 本章摘要（200字以内） |
| key_events | list[str] | 关键事件列表 |
| characters_present | list[str] | 出场角色 ID 列表 |
| character_state_changes | list | 角色状态变更列表（见下表） |
| foreshadowing_events | list | 伏笔事件列表（见下表） |

**角色状态变更字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| character_id | str | 角色 ID |
| items | list[str]? | 持有物品变更 |
| abilities | list[str]? | 能力变更 |
| physical_state | str? | 身体状态 |
| mental_state | str? | 心理状态 |
| location | str? | 当前位置 |
| relationships | dict? | 关系变更 |
| key_events | str? | 关键事件 |

**伏笔事件字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| event_type | str | new_plant / advance / resolve |
| description | str | 事件描述 |
| related_foreshadow_id | str? | 关联伏笔 ID（advance/resolve 时必填） |

### 状态持久化

`_apply_delta` 方法将 ChapterDelta 中的变更写入数据库，执行三步操作：

1. 写入章节摘要：将 summary、key_events、characters_present 存入 chapter_summaries 表
2. 更新角色状态：遍历 character_state_changes，为每个角色创建新的状态快照（与前一状态合并，不修改历史记录）
3. 更新伏笔：遍历 foreshadowing_events，按 event_type 分别处理：
   - `new_plant` → 创建新伏笔记录（status=open）
   - `advance` → 更新对应伏笔的 last_advanced_chapter
   - `resolve` → 将对应伏笔标记为 resolved

### 向量索引

将章节内容分段后存入 ChromaDB 向量库：

1. 将章节全文按段落分割，每段不超过 500 tokens
2. 为每段生成元数据（novel_id、chapter_num、segment_index）
3. 以 `{novel_id}_ch{chapter_num}_seg{index}` 为 ID 存入 `chapter_vectors` collection

## 人工编辑章节

用户可以在任何时候手动编辑章节内容。编辑保存后，触发章后统一管线重新执行（幂等）：

1. 用户编辑章节内容并保存
2. 后端检测到内容变更
3. 重新执行 Commit 阶段（清除旧的摘要/状态/向量，重新提取和索引）
4. 标记 `source="mixed"`（AI 生成 + 人工编辑）

这确保无论内容来源如何，状态始终与实际章节内容一致。
