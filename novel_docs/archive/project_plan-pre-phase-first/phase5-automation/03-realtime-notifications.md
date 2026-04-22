---
title: Phase 5 — 实时通知系统
version: 1.0
date: 2026-04-20
parent: 00-overview.md
---

# 实时通知系统（SSE + Webhook）

## 概述

实时通知系统由两部分组成：SSE 事件总线（面向前端，推送实时状态）和 Webhook 通知（面向外部系统，推送关键事件）。两者共享同一个 EventBus 核心，但投递方式不同。

## 架构

```
                    ┌─────────────┐
                    │  EventBus   │
                    │  (内存队列)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ SSE 推送  │ │ Webhook  │ │ 统计收集  │
        │ (前端)    │ │ (外部)   │ │ (内部)    │
        └──────────┘ └──────────┘ └──────────┘
```

## EventBus 设计

### 核心设计

- 每个小说维护独立的订阅者队列列表
- 订阅者通过 asyncio.Queue 接收事件
- 支持多个并发订阅者（多个浏览器标签页）
- 订阅者断开时自动清理队列
- 每个订阅者队列最大积压 100 个事件
- 心跳间隔 30 秒

### 事件数据结构

每个事件包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| event_type | str | 事件类型标识 |
| data | dict | 事件数据 |
| novel_id | str | 所属小说 ID |
| timestamp | float | 事件时间戳 |
| event_id | str | 唯一事件 ID（UUID） |

### 接口

- subscribe(novel_id)：订阅某小说的事件流，返回 asyncio.Queue
- unsubscribe(novel_id, queue)：取消订阅
- emit(novel_id, event_type, data)：向该小说的所有订阅者广播事件。队列满时丢弃最旧事件
- emit_to_all(event_type, data)：向所有小说的所有订阅者广播全局事件

## SSE 端点

`GET /api/v1/novels/{id}/events`

SSE 事件流端点。连接后持续推送事件，格式遵循 SSE 协议（id + event + data 字段）。客户端断开时自动取消订阅。超过心跳间隔无事件时发送心跳注释保持连接。

响应头：Cache-Control: no-cache, Connection: keep-alive, X-Accel-Buffering: no（nginx 禁用缓冲）。

## 事件类型定义

### 完整事件清单

| 事件类型 | 数据字段 | 触发时机 |
|---------|---------|---------|
| autopilot_started | stage | 自动驾驶启动 |
| stage_changed | from, to, detail(可选) | 阶段切换 |
| chapter_started | chapter_num | 开始生成章节 |
| pipeline_stage | stage, status | 流水线阶段变化（draft/audit/revise） |
| draft_chunk | content, chapter_num | 写作流式输出（逐段） |
| chapter_completed | chapter_num, word_count, tokens_used | 章节完成 |
| audit_result | chapter_num, critical, warning, info, issues | 审计结果 |
| audit_paused | chapter_num, issues, reason | 审计暂停等人工 |
| revision_started | chapter_num, round, issues | 开始修订 |
| revision_completed | chapter_num, round, fixed, remaining | 修订完成 |
| error | message, chapter_num(可选), error_count | 错误发生 |
| circuit_open | reason, last_error(可选) | 熔断器开启 |
| circuit_reset | message | 熔断器重置 |
| autopilot_completed | total_chapters, total_tokens, duration_seconds | 全部完成 |
| autopilot_paused | reason | 用户暂停 |
| autopilot_resumed | stage | 用户恢复 |
| batch_completed | start, end, total_tokens | 批量生成完成 |
| stats_update | completed, total, tokens, cost | 统计更新（每章完成后） |
| heartbeat | (空) | 心跳（SSE 注释行） |

## Webhook 通知系统

### 数据库配置

novels 表新增字段：

| 字段 | 说明 |
|------|------|
| webhook_url | Webhook 接收地址（可为空） |
| webhook_secret | HMAC 签名密钥 |
| notification_config | 通知配置（JSONB） |

notification_config 包含以下配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| frequency | "every_chapter" | 通知频率：every_chapter / every_n / milestone_only |
| notify_on_chapter | true | 章节完成时通知 |
| notify_on_milestone | true | 里程碑时通知 |
| notify_on_error | true | 错误时通知 |
| notify_on_pause | true | 暂停时通知 |
| notify_on_complete | true | 全部完成时通知 |
| milestone_interval | 10 | 里程碑间隔（章） |
| quiet_hours | null | 静默时段（start_hour, end_hour） |

### WebhookNotifier 职责

WebhookNotifier 向外部系统推送关键事件，使用 HMAC-SHA256 签名确保消息完整性。

Webhook 请求格式：
- 请求体：JSON，包含 event、novel_id、novel_title、message、timestamp、data
- 签名头：X-Signature-256（sha256=HMAC 签名值）
- 其他头：X-Event-Type、X-Novel-ID

始终通知的事件类型（不受频率配置影响）：audit_paused、circuit_open、autopilot_completed、error。

其他事件根据 notification_config 决定是否发送：检查静默时段、检查频率配置（milestone_only 模式下仅在章节号为 milestone_interval 的倍数时通知）。

### Webhook 签名验证

接收方使用 HMAC-SHA256 验证签名：用 webhook_secret 对请求体计算 HMAC，与 X-Signature-256 头中的签名值做常量时间比较。

## 统计追踪

### 统计数据

小说级统计（NovelStats）：

| 字段 | 说明 |
|------|------|
| novel_id | 小说 ID |
| total_chapters | 总章节数 |
| completed_chapters | 已完成章节数 |
| total_tokens_used | 总 token 消耗 |
| total_cost_estimate | 总成本估算 |
| avg_tokens_per_chapter | 平均每章 token |
| avg_generation_time_seconds | 平均生成时间 |
| audit_pass_rate | 审计通过率 |
| avg_revision_rounds | 平均修订轮次 |
| circuit_breaker_triggers | 熔断触发次数 |
| started_at / last_chapter_at | 开始/最后章节时间 |
| estimated_completion | 预计完成时间 |

单章统计（ChapterStats）：chapter_num、tokens_used、generation_time_seconds、revision_rounds、audit_passed、word_count、cost_estimate。

### StatsCollector 职责

StatsCollector 在每个关键节点记录指标，数据存储在 chapter_stats 表中。

chapter_stats 表字段：

| 字段 | 说明 |
|------|------|
| id | 主键（自增） |
| novel_id | 小说 ID（外键） |
| chapter_num | 章节号 |
| tokens_used | token 消耗 |
| generation_time_seconds | 生成耗时 |
| revision_rounds | 修订轮次 |
| audit_passed | 是否审计通过 |
| word_count | 字数 |
| cost_estimate | 成本估算 |
| created_at | 记录时间 |

唯一约束：(novel_id, chapter_num)。

成本估算基于每 1K tokens 的价格：input $0.003，output $0.015。

record_chapter 方法记录单章统计后，通过事件总线广播 stats_update 事件。get_novel_stats 方法聚合查询生成小说级统计。

## 前端 SSE 客户端

前端通过 EventSource API 连接 SSE 端点，注册各事件类型的处理器。浏览器 EventSource 内置自动重连机制。
