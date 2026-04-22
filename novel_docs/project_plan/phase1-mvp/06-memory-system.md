---
title: Phase 1 — 基础记忆系统
version: 1.0
date: 2026-04-20
---

# 基础记忆系统

## 概述

Phase 1 实现简化版记忆引擎，支持三层洋葱模型（跳过 T1）。核心目标：为 Writer 提供足够的上下文，使生成的章节与前文保持基本一致性。

## 洋葱模型（Phase 1 简化版）

| 层级 | 内容 | Token 预算 | 来源 |
|------|------|-----------|------|
| T0（永不裁剪） | 核心设定 + 角色锚点 + 活跃伏笔 | ~4K | novel_architecture + characters + character_states(latest) + foreshadowing(open) |
| T2（动态水位线） | 最近 N 章全文 | ~18K | chapters 表 + 文件系统 |
| T3（优先牺牲） | 向量召回结果 | 剩余预算 | ChromaDB |

T1（知识图谱 + 剧情线摘要）在 Phase 3 引入。

## MemoryEngine 接口

MemoryEngine 是记忆系统的核心，管理小说的全部记忆，为 Composer 提供分层上下文。依赖注入所有仓储（novel、architecture、character、character_state、chapter、summary、foreshadowing）以及 ChromaDB 客户端和文件存储。

核心方法 `build_context(novel_id, chapter_num, token_budget=30000)` 按以下顺序构建上下文：

1. 构建 T0 层（核心设定），计算其 token 用量
2. 将剩余预算的 70% 分配给 T2 层（近章全文）
3. 将最终剩余预算分配给 T3 层（向量召回）
4. 返回 ContextPayload（包含各层内容和 token 统计）

### T0 层：核心设定（永不裁剪）

T0 层组装三部分内容：

1. 核心种子和世界观：从 novel_architecture 表读取 core_seed 和 world_building
2. 角色锚点：遍历所有角色，获取每个角色的最新状态（位置、身体状态、心理状态），拼接为摘要文本
3. 活跃伏笔：查询所有 status=open 的伏笔，列出描述和植入章节

返回 T0Context 对象，包含 core_setting、character_anchors、active_foreshadowing 三个文本字段。

### T2 层：近章全文（动态水位线）

从最近的章节开始向前遍历，尽可能多地加载全文，直到 token 预算用完：

1. 从 chapter_num-1 开始倒序遍历
2. 读取章节全文，估算 token 数
3. 如果预算足够，加入上下文（格式：`【第N章】\n{全文}`）
4. 如果预算不够放全文，尝试用该章摘要替代（格式：`【第N章摘要】{摘要}`）
5. 如果连摘要也放不下，停止遍历

返回拼接后的文本和总 token 数。

### T3 层：向量召回（优先牺牲）

基于当前章节蓝图做向量检索，召回相关段落：

1. 如果剩余预算 ≤ 0，返回空
2. 用蓝图的 summary + positioning 拼接为查询文本
3. 从 ChromaDB 的 `chapter_vectors` collection 检索 top-10 结果（过滤 novel_id）
4. 过滤掉最近 3 章的内容（已在 T2 中包含，避免重复）
5. 按预算裁剪，逐条加入直到预算用完（格式：`【第N章片段】{内容}`）

返回拼接后的文本和总 token 数。

## ContextPayload 数据结构

**T0Context** 包含三个文本字段：

| 字段 | 说明 |
|------|------|
| core_setting | 核心种子 + 世界观 |
| character_anchors | 各角色最新状态摘要 |
| active_foreshadowing | 活跃伏笔列表 |

T0Context 提供 `to_text()` 方法，将三部分拼接为带标题的文本（"## 核心设定"、"## 角色状态"、"## 活跃伏笔"）。

**ContextPayload** 包含各层内容和 token 统计：

| 字段 | 类型 | 说明 |
|------|------|------|
| t0 | T0Context | 核心设定层 |
| t0_tokens | int | T0 层 token 数 |
| t2 | str | 近章全文/摘要 |
| t2_tokens | int | T2 层 token 数 |
| t3 | str | 向量召回结果 |
| t3_tokens | int | T3 层 token 数 |
| t3_sources | list[dict]? | 召回来源信息（调试用） |

提供 `total_tokens()` 方法返回三层 token 总和。

## 第一章特殊处理

第一章没有前文，记忆系统的行为：
- T0：完整的核心设定 + 角色初始状态（chapter_num=0）+ 无活跃伏笔
- T2：空（无前章）
- T3：空（向量库为空）

Writer 的提示词会针对第一章做特殊处理（见 05-chapter-pipeline.md）。

## 向量检索配置

ChromaDB 配置：
- Collection: `chapter_vectors`
- Embedding: 使用 ChromaDB 默认的 all-MiniLM-L6-v2（Phase 1 够用）
- 分段策略：按段落分割，每段不超过 500 tokens
- 检索数量：默认 top-10，过滤后通常 5-8 条

后续 Phase 可升级 embedding 模型（如 text-embedding-3-small）或切换到更强的向量数据库。
