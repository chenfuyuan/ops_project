---
title: Phase 2 — 一致性审计器
version: 1.0
date: 2026-04-20
---

# 一致性审计器（Auditor Agent）

## 概述

Auditor 在 Draft 阶段之后执行，对照 DB 中的状态检查章节草稿的逻辑一致性。输出结构化的问题清单，每项标注维度和严重度。

## 15 个审计维度

### Critical 级别（必须修复，否则阻塞发布）

| # | 维度 | 检查内容 | 检查方式 |
|---|------|---------|---------|
| 1 | 角色记忆 | 角色不能"知道"未亲身经历或被告知的事件 | 对照 character_states 的 key_events 和 relationships，检查角色在章节中引用的信息是否有合法来源 |
| 2 | 角色存活 | 已死亡角色不能出场（除非有明确的超自然解释） | 检查 fact_locks 中 FACT_LOCK 类型的死亡记录，与章节出场角色交叉比对 |
| 3 | 物品连续性 | 物品不能凭空出现或消失 | 对照 character_states.items，检查章节中使用的物品是否在角色持有列表中 |
| 4 | 能力连续性 | 角色使用的能力必须是已获得的 | 对照 character_states.abilities，检查章节中展示的能力是否已习得 |
| 5 | 时间线一致 | 事件时序不能矛盾（如"三天前"的事件与实际章节间隔不符） | 对照 chapter_summaries 的时间线信息，检查时间引用的合理性 |
| 6 | 事实锁违反 | 章节内容不能与已锁定的不可逆事实矛盾 | 遍历所有 FACT_LOCK 记录，检查章节是否违反 |
| 7 | 已完成节拍重复 | 不能重复已经发生过的剧情节拍 | 遍历 COMPLETED_BEATS 记录，检查章节是否重复相同情节 |
| 8 | 已揭示线索矛盾 | 不能与读者已知的信息矛盾 | 遍历 REVEALED_CLUES 记录，检查章节是否给出矛盾信息 |

### Warning 级别（建议修复，不阻塞但标记人工审核）

| # | 维度 | 检查内容 | 检查方式 |
|---|------|---------|---------|
| 9 | 伏笔追踪 | 已植入伏笔是否在合理时间内推进 | 检查 open 状态伏笔的 last_advanced_chapter，超过 10 章未推进则预警 |
| 10 | 大纲偏离 | 章节内容是否偏离蓝图设定 | 对照 chapter_blueprint 的 positioning 和 core_function，检查章节是否覆盖了蓝图要求 |
| 11 | 关系连续性 | 角色关系变化需有铺垫 | 对照 character_states.relationships，检查关系突变是否有前文支撑 |
| 12 | 地理一致 | 角色位置移动需合理 | 对照 character_states.location，检查角色是否在合理时间内到达新位置 |
| 13 | 信息边界 | 角色间信息传递需有渠道 | 检查角色 A 向角色 B 透露的信息，角色 A 是否确实知道该信息 |

### Info 级别（仅记录）

| # | 维度 | 检查内容 |
|---|------|---------|
| 14 | 叙事节奏 | 连续 3+ 章无实质剧情进展 |
| 15 | 字数达标 | 章节字数是否在目标范围（±20%）内 |

## LLM 调用设计

审计通过一次 LLM 调用完成，将所有维度的检查材料打包发送。

**输入材料：**
1. 每个出场角色的最新 character_state
2. 所有事实锁（FACT_LOCK / COMPLETED_BEATS / REVEALED_CLUES）
3. open 状态的伏笔列表（含 planted_chapter 和 last_advanced_chapter）
4. 本章蓝图（chapter_blueprint）
5. 前 3 章的 chapter_summary
6. 待审计的章节草稿

**输出要求：** LLM 逐一检查 15 个维度，对每个发现的问题输出维度名称、严重度、问题描述、位置和修复建议。无问题的维度不输出。

## 输出结构

**审计问题（AuditIssue）：**

| 字段 | 说明 |
|------|------|
| dimension | 审计维度名称 |
| severity | 严重度：critical / warning / info |
| description | 问题描述 |
| location | 问题在章节中的位置 |
| suggestion | 修复建议 |

**审计结果（AuditResult）：**

| 字段 | 说明 |
|------|------|
| issues | 问题清单 |
| critical_count | critical 问题数 |
| warning_count | warning 问题数 |
| info_count | info 问题数 |
| passed | 是否通过（critical_count == 0）|

## 审计结果持久化

每个问题存入 `audit_issues` 表：
- `chapter_id`: 关联章节
- `novel_id`: 关联小说
- `dimension`: 审计维度
- `severity`: 严重度
- `description`: 问题描述 + 位置 + 建议
- `resolved`: 是否已解决
- `resolved_by`: auto（自动修订）/ human（人工处理）
