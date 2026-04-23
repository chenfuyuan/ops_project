---
title: Phase 5 — 熔断器系统
version: 1.0
date: 2026-04-20
parent: 00-overview.md
---

# 熔断器系统（Circuit Breaker）

## 概述

熔断器保护系统免受 LLM API 故障的级联影响。分为两层：单小说熔断（防止单个小说的持续错误消耗资源）和全局熔断（防止 API 提供商故障时所有小说同时重试导致雪崩）。

## 状态机

```
         成功
    ┌──────────┐
    ▼          │
 CLOSED ──────► OPEN ──────► HALF_OPEN
    ▲    失败达阈值   冷却超时      │
    │                              │
    └──────── 探测成功 ────────────┘
                  │
              探测失败 → 回到 OPEN
```

| 状态 | 含义 | 行为 |
|------|------|------|
| CLOSED | 正常 | 放行所有请求，记录失败计数 |
| OPEN | 熔断 | 拒绝所有请求，等待冷却时间 |
| HALF_OPEN | 探测 | 放行一个请求，成功则关闭，失败则重新打开 |

## 单小说熔断器

### 参数

| 参数 | 值 | 说明 |
|------|---|------|
| MAX_CONSECUTIVE_FAILURES | 3 | 连续失败次数阈值 |
| 触发动作 | 暂停该小说 | 设置 autopilot_status = ERROR |
| 恢复方式 | 人工重置 | 用户确认后重置 error_count 并恢复 |

### 职责

NovelCircuitBreaker 负责单小说级别的熔断保护，状态持久化在 novels.error_count 中，不依赖内存。

- on_failure(novel_id, error)：递增 error_count，达到阈值时设置 autopilot_status = ERROR，通过事件总线发送 circuit_open 事件，通过 Webhook 通知用户
- on_success(novel_id)：重置 error_count
- reset(novel_id)：人工重置熔断器，重置 error_count，设置 autopilot_status = PAUSED，发送 circuit_reset 事件

## 全局熔断器

### 参数

| 参数 | 值 | 说明 |
|------|---|------|
| FAILURE_THRESHOLD | 5 | 全局失败次数阈值 |
| COOLDOWN_SECONDS | 120 | 冷却时间（秒） |
| HALF_OPEN_MAX_REQUESTS | 1 | 半开状态最大探测请求数 |
| 触发动作 | 拒绝所有 LLM 请求 | 所有小说暂停调用 |
| 恢复方式 | 自动探测 | 冷却后半开探测，成功则关闭 |

### 职责

GlobalCircuitBreaker 防止 API 提供商故障时雪崩。所有 LLM 调用前必须经过 allow_request() 检查。状态存储在内存中（单进程），进程重启后自动重置为 CLOSED。每个订阅者队列最大积压 100 个事件。

- allow_request()：CLOSED 状态放行；OPEN 状态检查冷却时间，超时则进入 HALF_OPEN；HALF_OPEN 状态限制探测请求数
- on_failure(error)：HALF_OPEN 状态探测失败回到 OPEN；CLOSED 状态失败计数达阈值则打开
- on_success()：HALF_OPEN 状态探测成功则关闭熔断器并重置计数；CLOSED 状态成功则重置计数
- force_reset()：管理员强制重置为 CLOSED
- get_status()：返回当前状态、失败计数、阈值、冷却时间等监控信息

## 与 AI 网关集成

CircuitBreakerAIGatewayAdapter 包装原有的 AI 网关调用适配层，在每次调用前后执行熔断器逻辑：

1. 全局熔断检查：调用 global_breaker.allow_request()，不允许则抛出 CircuitOpenError
2. 执行 LLM 调用
3. 成功时：调用 global_breaker.on_success() 和 novel_breaker.on_success()
4. 失败时：调用 global_breaker.on_failure() 和 novel_breaker.on_failure()，然后重新抛出异常

## 可重试错误分类

并非所有错误都应触发熔断计数。ErrorClassifier 区分两类错误：

应触发熔断计数的错误（基础设施类）：
- rate_limit_exceeded（API 限流）
- server_error（5xx 错误）
- timeout（超时）
- connection_error（连接失败）

不应触发熔断计数的错误（业务逻辑类）：
- invalid_prompt（提示词格式错误）
- content_filter（内容过滤）
- context_length_exceeded（上下文超长）

默认行为：未分类的错误计入熔断器。

## 监控与告警

BreakerMonitor 定期收集熔断器指标，包括：
- 全局熔断器状态（state、failure_count、threshold、cooldown_seconds）
- 各小说熔断器状态（error_count、是否处于 ERROR 状态）
- 当前处于熔断状态的小说总数
