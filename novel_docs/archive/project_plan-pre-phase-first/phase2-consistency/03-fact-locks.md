---
title: Phase 2 — 事实锁与 JSON Delta
version: 1.0
date: 2026-04-20
---

# 事实锁与 JSON Delta 状态更新

## 事实锁机制

### 三类事实锁

**FACT_LOCK — 不可逆事实**

一旦发生就不可撤销的事件，注入 T0 层永不裁剪：
- 角色死亡：`"张三在第45章被赵无极杀死"`
- 重大身份揭示：`"李四的真实身份是前朝皇子"`
- 世界规则确立：`"金丹期以下修士无法飞行"`
- 重大物品毁灭：`"上古神器天命剑在第80章碎裂"`

**COMPLETED_BEATS — 已完成节拍**

已经发生过的剧情节拍，防止 AI 重复：
- `"主角已在第23章获得火焰之剑"`
- `"宗门大比已在第50-55章完成，主角获得第三名"`
- `"主角与林雪已在第67章和解"`

**REVEALED_CLUES — 已揭示线索**

读者已经知道的信息，防止矛盾：
- `"读者已知反派是主角的父亲（第90章揭示）"`
- `"读者已知玉佩是打开上古遗迹的钥匙（第30章暗示，第75章明确）"`

### 事实锁的创建

**自动创建（Reflector 提取）：**

Reflector 在 Commit 阶段提取候选事实锁。每个候选包含类型（FACT_LOCK / COMPLETED_BEATS / REVEALED_CLUES）、内容描述和置信度（0-1）。

置信度 ≥ 0.9 的候选自动创建为事实锁。
置信度 0.7-0.9 的候选标记为"待确认"，在前端显示供用户确认。
置信度 < 0.7 的候选丢弃。

**手动创建：**

用户可以在前端手动添加事实锁，用于补充 AI 未检测到的重要事实。

**自动规则判定：**

某些模式可以通过规则自动判定：
- 角色状态变为"死亡" → 自动创建 FACT_LOCK
- 蓝图中标记为 `core_function=reveal` 的章节完成 → 检查是否有 REVEALED_CLUES 候选

### 事实锁的注入

事实锁注入 T0 层，按类型分组呈现：不可逆事件、已完成剧情（防止重复）、读者已知信息（防止矛盾）。

## JSON Delta 状态更新

### 从全量替换升级为增量更新

Phase 1 的 Reflector 输出完整的状态快照。Phase 2 改为输出 Delta（增量变更），减少 LLM 输出量并提高准确性。

### Delta 格式

**StateDelta（顶层增量结构）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| summary | ChapterSummaryDelta | 章节摘要（全量，因为每章都是新的） |
| character_changes | CharacterDelta 列表 | 角色状态增量变更 |
| foreshadowing_events | ForeshadowingDelta 列表 | 伏笔事件增量 |
| fact_lock_candidates | FactLockCandidate 列表 | 事实锁候选增量 |

**CharacterDelta（角色状态增量）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| character_id | string | 角色 ID |
| changes | dict | 只包含变化的字段。例如 location 直接赋新值；items 使用 add/remove 子结构 |

**ForeshadowingDelta（伏笔事件增量）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| event_type | string | new_plant / advance / resolve / defer |
| foreshadow_id | string（可选） | advance / resolve / defer 时必填 |
| description | string | 事件描述 |
| related_characters | string 列表（可选） | 相关角色 |

### 校验规则

CharacterDelta 的 changes 字段只允许以下 key：items、abilities、physical_state、mental_state、location、relationships、key_events。其中 items 变更必须使用 add/remove 子结构。

ForeshadowingDelta 中，event_type 为 advance / resolve / defer 时，foreshadow_id 为必填。

### Delta 应用逻辑

增量变更按以下步骤应用到数据库：

1. **角色状态：** 读取角色最新状态 → 合并 delta 中的变更字段 → 写入新快照（按章节号）
2. **伏笔：** 按 event_type 分别处理
   - new_plant → 创建新伏笔记录
   - advance → 更新状态为 progressing，记录 last_advanced_chapter
   - resolve → 更新状态为 resolved，记录 resolved_chapter
   - defer → 更新状态为 deferred
3. **事实锁：** 按置信度处理
   - 置信度 ≥ 0.9 → 直接创建事实锁
   - 置信度 0.7-0.9 → 创建为"待确认"状态，前端显示供用户确认
   - 置信度 < 0.7 → 丢弃

## 前端变更

### 事实锁管理面板

新增页面 `/novels/:id/fact-locks`：
- 分组显示：FACT_LOCK / COMPLETED_BEATS / REVEALED_CLUES
- 每条显示：内容、来源章节、创建方式（自动/手动）
- 待确认的事实锁高亮显示，带确认/拒绝按钮
- 手动添加事实锁的表单

### 审计问题面板

写作工作台右栏新增"审计"Tab：
- 按严重度分组显示问题
- critical 问题红色高亮
- 每个问题显示：维度、描述、位置、建议、状态（已修复/待处理/已忽略）
- 操作：标记为已忽略、跳转到问题位置
