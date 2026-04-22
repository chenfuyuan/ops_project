---
title: Phase 2 — 伏笔完整生命周期
version: 1.0
date: 2026-04-20
---

# 伏笔完整生命周期

## 状态机升级

Phase 1 只有 open/resolved 两个状态。Phase 2 扩展为完整生命周期：

```
         plant
           │
           ▼
        ┌──────┐
        │ open │
        └──┬───┘
           │
     ┌─────┼─────────┐
     │     │         │
     ▼     ▼         ▼
 advance  defer    resolve
     │     │         │
     ▼     ▼         ▼
┌────────┐ ┌────────┐ ┌──────────┐
│progress│ │deferred│ │ resolved │
│  ing   │ │        │ │          │
└───┬────┘ └───┬────┘ └──────────┘
    │          │
    │    resume │
    │     ┌────┘
    ▼     ▼
  advance/resolve
```

### 状态定义

| 状态 | 含义 | 触发条件 |
|------|------|---------|
| open | 刚植入，尚未推进 | Reflector 检测到新伏笔植入 |
| progressing | 有后续章节推进或强化 | Reflector 检测到已有伏笔被推进 |
| deferred | 主动延后 | 用户手动标记，或 Planner 建议延后 |
| resolved | 已收获/解决 | Reflector 检测到伏笔被收获 |

### 数据库变更

`foreshadowing` 表新增字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| deferred_reason | TEXT | 延后原因 |
| deferred_until_chapter | INTEGER | 预计恢复章节号 |

## 停滞预警系统

### 预警规则

每章 Commit 后检查所有活跃伏笔（open + progressing 状态）：

| 未推进章节数 | 严重度 | 预警内容 |
|-------------|--------|---------|
| ≥ 20 章 | critical | 伏笔可能被遗忘，建议在近期章节中推进或收获 |
| ≥ 10 章 | warning | 伏笔较久未推进，考虑在后续章节中强化 |

未推进章节数 = 当前章节号 - max(last_advanced_chapter, planted_chapter)

### 预警注入

停滞预警注入 Planner 的输入，引导后续章节处理。预警按严重度排列，包含伏笔描述、停滞章节数、植入章节号，以及处理建议（critical 建议收获或重大推进，warning 建议强化暗示）。

## 伏笔台账前端升级

### 可视化增强

- 伏笔时间线：横轴为章节号，每个伏笔一条线，标注植入/推进/收获节点
- 颜色编码：open=蓝色，progressing=橙色，deferred=灰色，resolved=绿色
- 停滞预警：超过 10 章未推进的伏笔闪烁提示

### 操作增强

- 手动标记为 deferred（需填写原因和预计恢复章节）
- 手动标记为 resolved
- 从 deferred 恢复为 open
- 批量操作：选中多个伏笔批量标记

