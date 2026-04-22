---
title: Phase 5 — API 端点与前端
version: 1.0
date: 2026-04-20
parent: 00-overview.md
---

# API 端点与前端

## 概述

Phase 5 新增自动驾驶控制、批量生成、统计查询三组 API，以及对应的前端控制台。所有 API 遵循 RESTful 风格，返回 JSON。

## 自动驾驶控制 API

### 启动自动驾驶

`POST /api/v1/novels/{id}/autopilot/start`

请求体包含 auto_approve_warnings（是否自动通过 warning）、pause_on_warning（warning 时是否暂停）、notification_frequency（通知频率）。

行为：检查小说是否存在且未在运行中，确定起始阶段（根据大纲和蓝图状态），保存配置，设置 autopilot_status = RUNNING，重置 error_count，发送 autopilot_started 事件。

响应返回 status、stage 和确认消息。

### 暂停自动驾驶

`POST /api/v1/novels/{id}/autopilot/pause`

行为：检查当前状态为 RUNNING，设置 autopilot_status = PAUSED，发送 autopilot_paused 事件。

响应返回 status、stage、current_beat_index 和确认消息。

### 恢复自动驾驶

`POST /api/v1/novels/{id}/autopilot/resume`

行为：检查当前状态为 PAUSED 或 ERROR，ERROR 状态恢复时重置 error_count，设置 autopilot_status = RUNNING，发送 autopilot_resumed 事件。

响应返回 status、stage、current_beat_index 和确认消息。

### 停止自动驾驶

`POST /api/v1/novels/{id}/autopilot/stop`

行为：检查当前状态为 RUNNING/PAUSED/ERROR，设置 autopilot_status = IDLE，autopilot_stage = STOPPED，重置 error_count，发送 stage_changed 事件。

响应返回 status、completed_chapters 和确认消息。

### 获取自动驾驶状态

`GET /api/v1/novels/{id}/autopilot/status`

响应包含：status、stage、current_beat_index、total_chapters、error_count、auto_approve_mode、config（完整配置对象）、circuit_breaker（novel_state 和 global_state 及 global_failure_count）。

## 批量生成 API

### 启动批量生成

`POST /api/v1/novels/{id}/chapters/batch-generate`

请求体包含 start_chapter、end_chapter、auto_approve_audit（是否自动通过审计）、pause_on_warning。

行为：检查自动驾驶未在运行中，验证章节范围有效，验证指定范围内所有蓝图存在（缺少则返回 400 并列出缺失章节），调用 BatchGenerator 启动批量生成。

响应返回 status、stage、batch_range 和确认消息。

## 统计 API

### 获取小说统计

`GET /api/v1/novels/{id}/stats`

响应包含：total_chapters、completed_chapters、total_tokens_used、total_cost_estimate、avg_tokens_per_chapter、avg_generation_time_seconds、audit_pass_rate、avg_revision_rounds、circuit_breaker_triggers、started_at、last_chapter_at、estimated_completion。

### 获取每章统计明细

`GET /api/v1/novels/{id}/stats/chapters?start=1&end=50`

响应包含 chapters 数组，每项含 chapter_num、tokens_used、generation_time_seconds、revision_rounds、audit_passed、word_count、cost_estimate。

## 通知配置 API

### 更新 Webhook 配置

`PUT /api/v1/novels/{id}/notifications`

请求体包含 webhook_url、webhook_secret、config（通知配置对象，含 frequency、notify_on_chapter、notify_on_error、notify_on_pause、notify_on_complete、milestone_interval）。

### 测试 Webhook

`POST /api/v1/novels/{id}/notifications/test`

发送一条测试通知到配置的 webhook_url，返回 success 状态和消息。

## API 端点汇总

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/novels/{id}/autopilot/start` | 启动自动驾驶 |
| `POST` | `/api/v1/novels/{id}/autopilot/pause` | 暂停自动驾驶 |
| `POST` | `/api/v1/novels/{id}/autopilot/resume` | 恢复自动驾驶 |
| `POST` | `/api/v1/novels/{id}/autopilot/stop` | 停止自动驾驶 |
| `GET` | `/api/v1/novels/{id}/autopilot/status` | 获取自动驾驶状态 |
| `POST` | `/api/v1/novels/{id}/chapters/batch-generate` | 启动批量生成 |
| `GET` | `/api/v1/novels/{id}/events` | SSE 事件流 |
| `GET` | `/api/v1/novels/{id}/stats` | 获取小说统计 |
| `GET` | `/api/v1/novels/{id}/stats/chapters` | 获取每章统计明细 |
| `PUT` | `/api/v1/novels/{id}/notifications` | 更新通知配置 |
| `POST` | `/api/v1/novels/{id}/notifications/test` | 测试 Webhook |

## 前端变更

### 1. 自动驾驶控制台

主控制面板，位于小说详情页顶部：

```
┌─────────────────────────────────────────────────────────┐
│  自动驾驶控制台                                          │
│                                                         │
│  状态: ● 运行中    阶段: 正在写作                         │
│  进度: ████████████░░░░░░░░ 42/200 (21%)                │
│                                                         │
│  [暂停]  [停止]                                          │
│                                                         │
│  ┌─ 实时日志 ──────────────────────────────────────────┐ │
│  │ 14:30:01  第42章开始生成                             │ │
│  │ 14:30:15  draft 阶段完成                            │ │
│  │ 14:30:20  审计开始                                  │ │
│  │ 14:30:25  审计通过 (0 critical, 1 warning, 2 info)  │ │
│  │ 14:30:26  第42章完成 (3,200字)                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─ 当前章节预览 ─────────────────────────────────────┐  │
│  │ (流式输出中...)                                      │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

组件结构：

- 状态指示灯（颜色映射：RUNNING=绿, PAUSED=黄, ERROR=红, COMPLETED=蓝）
- 阶段文字（绑定 autopilot_stage）
- 进度条（current_beat_index / total_chapters）
- 控制按钮组（根据状态显示不同按钮）
- 实时日志流（SSE stage_changed / chapter_completed / error 事件驱动）
- 章节预览区（SSE draft_chunk 事件驱动，流式追加文本）

### 2. 批量生成配置

弹窗或侧边栏组件：

- 章节范围选择器（下拉或滑块，范围 1 ~ total_chapters）
- 蓝图状态检查（选择范围后实时检查蓝图是否存在）
- 缺少蓝图时禁用"开始"按钮并提示
- 自动审核通过开关（映射 auto_approve_audit）
- Warning 暂停开关（映射 pause_on_warning）

### 3. 通知设置

设置页面中的通知配置区：

- Webhook URL 输入框
- Webhook Secret 输入框（密码模式）
- 通知频率选择（每章通知 / 每 N 章通知 / 仅里程碑通知）
- 通知事件开关（章节完成、审计暂停、错误发生、全部完成）
- 「测试通知」和「保存」按钮

### 4. 运行统计面板

统计仪表盘，位于小说详情页的"统计"标签：

```
┌─────────────────────────────────────────────────────────┐
│  运行统计                                                │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 已完成    │  │ Token    │  │ 预估成本  │  │ 审计通过 │ │
│  │ 85/200   │  │ 1.25M    │  │ ¥12.50   │  │ 82%     │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                         │
│  Token 用量趋势（按章节折线图）                            │
│  审计通过率趋势（折线图）                                  │
│                                                         │
│  生成速度: 平均 45s/章  |  修订轮次: 平均 1.3 轮          │
│  熔断触发: 2 次         |  预计完成: 2026-04-25           │
└─────────────────────────────────────────────────────────┘
```

数据来源：

- 概览卡片：GET /api/v1/novels/{id}/stats
- 趋势图表：GET /api/v1/novels/{id}/stats/chapters
- 实时更新：SSE stats_update 事件

图表库建议：使用 Chart.js 或 ECharts，支持实时数据追加。
