---
title: Phase 5 — 自动驾驶状态机
version: 1.0
date: 2026-04-20
parent: 00-overview.md
---

# 自动驾驶状态机（AutopilotDaemon）

## 概述

AutopilotDaemon 是后台异步守护进程，负责驱动小说从大纲到完稿的全自动流程。它以数据库为唯一状态源，轮询 novels 表中状态为 RUNNING 的小说，按状态机逻辑逐步推进。进程重启后可无缝恢复，无需内存状态。

## 状态流转图

```
IDLE → MACRO_PLANNING → ACT_PLANNING → WRITING → AUDITING → PAUSED_FOR_REVIEW → COMPLETED
  ↑                                                    │              │
  └────────────────── STOPPED ◄────────────────────────┘              │
                         ↑                                            │
                         └────────────────────────────────────────────┘
                                    (用户手动停止)
```

## 状态定义

| 状态 | 含义 | 自动转换条件 |
|------|------|-------------|
| IDLE | 未启动 | 用户点击"开始"→ MACRO_PLANNING |
| MACRO_PLANNING | 正在生成大纲 | 大纲五步完成 → ACT_PLANNING |
| ACT_PLANNING | 正在生成蓝图 | 当前批次蓝图完成 → WRITING |
| WRITING | 正在生成章节 | 当前章节流水线完成 → AUDITING |
| AUDITING | 正在审计 | 审计通过 → 下一章 WRITING；审计失败（3 轮修订后仍有 critical）→ PAUSED_FOR_REVIEW |
| PAUSED_FOR_REVIEW | 等待人工审核 | 用户处理完问题 → WRITING |
| COMPLETED | 全部章节完成 | 终态 |
| STOPPED | 用户手动停止 | 用户点击"继续"→ 恢复到停止前的状态 |

## 数据库 Schema

所有状态持久化在 novels 表中，不依赖进程内存。新增字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| autopilot_status | VARCHAR(20) | 状态：IDLE / RUNNING / PAUSED / ERROR / COMPLETED |
| autopilot_stage | VARCHAR(30) | 阶段：MACRO_PLANNING / ACT_PLANNING / WRITING / AUDITING / PAUSED_FOR_REVIEW / COMPLETED / STOPPED |
| current_beat_index | INTEGER | 已成功完成的最后一个章节号（默认 0） |
| error_count | INTEGER | 连续错误计数（默认 0） |
| auto_approve_mode | BOOLEAN | 是否自动审批（默认 FALSE） |
| autopilot_config | JSONB | 运行时配置 |

autopilot_config 包含以下配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| auto_approve_warnings | false | 是否自动通过 warning 级审计 |
| pause_on_warning | true | warning 时是否暂停 |
| notification_frequency | "every_chapter" | 通知频率 |
| max_concurrent_revisions | 3 | 最大修订轮次 |
| batch_start | null | 批量生成起始章节 |
| batch_end | null | 批量生成结束章节 |

## 守护进程设计

### 核心循环

AutopilotDaemon 以 5 秒间隔轮询数据库。设计原则：

- 数据库是唯一状态源，进程无状态
- 每个节拍（章节）完成后持久化进度
- 崩溃后从 current_beat_index + 1 恢复

每次 tick 执行：

1. 全局熔断检查（详见 02-circuit-breaker.md），熔断器开启则跳过本轮
2. 查询所有 autopilot_status = RUNNING 的小说
3. 逐个处理，根据 autopilot_stage 分发到对应处理逻辑
4. 异常时调用错误处理流程

### 各阶段处理

MACRO_PLANNING：
1. 发送 stage_changed 事件
2. 调用 MacroPlanner 执行大纲生成五步流程
3. 成功后转换到 ACT_PLANNING

ACT_PLANNING：
1. 计算下一批蓝图范围（从 current_beat_index + 1 开始）
2. 发送 stage_changed 事件（含批次详情）
3. 调用 ActPlanner 生成蓝图
4. 完成后转换到 WRITING

WRITING：
1. 计算下一章节号（current_beat_index + 1）
2. 如果超过总章节数，转换到 COMPLETED 并通知
3. 如果蓝图不存在，回退到 ACT_PLANNING
4. 发送 chapter_started 事件
5. 调用 ChapterPipeline 执行章节生成流水线（含 draft → audit → revise 循环）
6. 完成后转换到 AUDITING

AUDITING：
1. 获取最新审计结果
2. 发送 audit_result 事件
3. 有 critical 问题 → 必须暂停（PAUSED_FOR_REVIEW），通知用户
4. 有 warning 且未开启自动审批 → 根据 pause_on_warning 配置决定是否暂停
5. 审计通过 → 更新 current_beat_index，重置 error_count，转换到 WRITING，发送 chapter_completed 事件

### 状态转换与错误处理

状态转换为原子操作：更新数据库 autopilot_stage 并发送 stage_changed 事件。

错误处理：递增 error_count，发送 error 事件。连续错误达到 3 次时触发单小说熔断（设置 autopilot_status = ERROR），通知用户。

## 幂等恢复机制

- current_beat_index 是已成功完成的最后一个章节号
- 每次章节审计通过后原子更新 current_beat_index
- 崩溃恢复时从 current_beat_index + 1 继续
- 如果崩溃发生在 AUDITING 阶段中间，重置到 WRITING 重跑该章
- 流水线内部的检查点恢复（Phase 1）确保章节生成中途崩溃也能恢复

## 自动审批模式

| 审计结果 | 默认模式 | 自动审批模式 |
|---------|---------|------------|
| 无问题 | 自动继续 | 自动继续 |
| 仅 info | 自动继续 | 自动继续 |
| 有 warning | 暂停等人工（可配置） | 自动继续，记录日志 |
| 有 critical | 暂停等人工 | 暂停等人工（critical 永远不自动通过） |

AutoApprovePolicy 负责判断是否需要暂停：critical 永远暂停；warning 根据 auto_approve_warnings 和 pause_on_warning 配置决定。

## 批量生成

批量生成是自动驾驶的子集——仅执行 WRITING 阶段的指定章节范围。

```
自动驾驶 = MACRO_PLANNING + ACT_PLANNING + WRITING + AUDITING（全流程）
批量生成 = WRITING + AUDITING（指定范围，蓝图必须已存在）
```

BatchGenerator 启动流程：

1. 验证指定范围内所有章节的蓝图存在
2. 配置 autopilot_config 的 batch_start 和 batch_end
3. 设置 current_beat_index 为 start_chapter - 1
4. 设置 autopilot_stage = WRITING，autopilot_status = RUNNING

批量生成完成判断：当 chapter_num > batch_end 时，转换到 COMPLETED 并发送 batch_completed 通知。

## 生命周期管理

启动：应用启动时创建 AutopilotDaemon 实例并注册为后台任务，同时恢复所有中断的小说（遍历 RUNNING 状态的小说执行恢复逻辑）。

优雅关闭：停止守护进程主循环，当前正在处理的章节会在下次启动时恢复。
