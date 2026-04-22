---
title: Phase 5 — 自动化与规模化
version: 2.0
date: 2026-04-20
goal: 从人工主导过渡到自动模式，为 SaaS 做准备
prerequisite: Phase 2, 3, 4
---

# Phase 5 — 自动化与规模化

## 文档角色

本文档属于 **Phase 主线层 overview**，负责表达本阶段的目标、范围、完成标准与子主题入口，不替代相关 topic 的详细设计说明。

阅读方式：先阅读总纲入口与阶段路线，再阅读本 overview，最后按需进入本阶段专题文档。

## 阶段目标

在 Phase 2-4 构建的质量保障体系基础上，实现全自动写作模式。用户设定好参数后，系统可以自动完成从大纲到完整小说的全流程，仅在关键节点暂停等待人工审核。

## 完成标准

- 自动驾驶状态机可用，支持全流程自动执行
- 熔断器保护 API 调用，防止雪崩
- 崩溃后可从断点恢复（节拍级幂等）
- SSE 实时推送写作进度到前端
- 通知系统可用（Webhook + HMAC-SHA256 签名）
- 批量生成可用
- API 层完善，支持多项目并发

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-autopilot.md](01-autopilot.md) | 自动驾驶状态机守护进程、状态流转、数据库驱动、幂等恢复、自动审批、批量生成 |
| [02-circuit-breaker.md](02-circuit-breaker.md) | 熔断器系统：单小说熔断、全局熔断、状态机、LLM 适配层集成、恢复逻辑 |
| [03-realtime-notifications.md](03-realtime-notifications.md) | SSE 事件总线、实时推送、Webhook 通知、HMAC 签名、统计追踪 |
| [04-api-frontend.md](04-api-frontend.md) | 自动驾驶控制 API、批量生成 API、统计 API、前端控制台与面板 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与流水线背景 |
| [../2026-04-20-ai-novel-03-core-services.md](../2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 补充核心服务边界 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考跨 phase 复用的通用组件 |
