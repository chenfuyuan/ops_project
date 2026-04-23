---
title: Phase 1 — MVP 全流程跑通
version: 1.0
date: 2026-04-20
goal: 从大纲到完整章节的最小闭环，能实际用起来写小说
---

# Phase 1 — MVP 全流程跑通

## 文档角色

本文档属于 **Phase 主线层 overview**，只承担本阶段的目标、范围、完成标准、非目标与子主题入口，不承载跨阶段专题的完整细节。

阅读方式：先从总纲入口进入阶段路线，再进入本 overview，最后按需阅读本阶段专题文档。

## 阶段目标

构建一个可用的最小闭环系统：用户创建小说项目 → 生成大纲 → 生成章节蓝图 → 逐章生成内容 → 章后自动提取状态。全程人工主导，每步可审核和编辑。

## 完成标准

- 能创建一个小说项目，配置基本参数（标题、前提、类型、语言、模型）
- 能通过雪花写作法生成完整大纲（五步），每步可编辑，支持断点续跑
- 能生成章节蓝图（含悬念密度、伏笔操作标注），支持批次生成和续写
- 能逐章生成内容（流式输出），生成前可查看和编辑上下文
- 每章完成后自动提取摘要、角色状态变更、伏笔事件并持久化
- 有基础 Web UI 支持以上全部操作
- 支持至少 2 种 LLM 提供商，可按任务类型配置不同模型

## 不包含

- 审计和修订循环（Phase 2）
- 事实锁机制（Phase 2）
- 知识图谱三元组（Phase 3）
- 主题代理系统（Phase 3）
- 张力分析（Phase 3）
- 风格引擎和去 AI 化（Phase 4）
- 自动驾驶模式（Phase 5）
- 多用户和 SaaS 功能（Phase 6）

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-project-scaffold.md](01-project-scaffold.md) | 项目脚手架与基础设施 |
| [02-llm-adapter.md](02-llm-adapter.md) | AI 网关与多模型路由 |
| [03-outline-generation.md](03-outline-generation.md) | 大纲生成（雪花写作法） |
| [04-blueprint-generation.md](04-blueprint-generation.md) | 章节蓝图生成 |
| [05-chapter-pipeline.md](05-chapter-pipeline.md) | 章节生成流水线（简化版） |
| [06-memory-system.md](06-memory-system.md) | 基础记忆系统 |
| [07-api-endpoints.md](07-api-endpoints.md) | API 端点设计 |
| [08-frontend.md](08-frontend.md) | 前端界面设计 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与核心流水线背景 |
| [../2026-04-20-ai-novel-02-data-model.md](../2026-04-20-ai-novel-02-data-model.md) | 总纲专题 | 补充数据模型与存储基线 |
| [../2026-04-20-ai-novel-03-core-services.md](../2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 补充核心服务边界 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考可跨 phase 复用的通用组件 |
