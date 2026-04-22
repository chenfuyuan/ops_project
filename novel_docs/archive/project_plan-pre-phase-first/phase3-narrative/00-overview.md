---
title: Phase 3 — 叙事质量提升（总览）
version: 1.0
date: 2026-04-20
goal: 从"不出错"提升到"好看"——张力控制、类型化写作、知识图谱、完整上下文管理
prerequisite: Phase 2
---

# Phase 3 — 叙事质量提升

## 文档角色

本文档属于 **Phase 主线层 overview**，负责表达本阶段的目标、范围、完成标准与子主题入口，不替代具体 topic 文档本身。

阅读方式：先从总纲入口进入阶段路线，再阅读本 overview，最后按需进入本阶段专题文档。

## 阶段目标

Phase 2 保证了一致性（不出错），Phase 3 提升叙事质量（好看）。核心是让 AI 写出有节奏感、有类型特色、信息管理精确的章节。

## 完成标准

- 每章有张力评分（0-10），前端可视化张力曲线，连续异常自动预警
- 主题代理系统上线，至少支持 5 种类型（玄幻/都市/科幻/悬疑/言情），可插拔技能
- 知识图谱自动提取三元组，支持信息边界查询
- 洋葱模型 T1 层上线，上下文管理完整（T0/T1/T2/T3 四层）
- 章节蓝图增强：悬念单元可视化、场景类型指导

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-tension-analyzer.md](01-tension-analyzer.md) | 张力分析器 |
| [02-theme-agents.md](02-theme-agents.md) | 主题代理系统与可插拔技能 |
| [03-knowledge-graph.md](03-knowledge-graph.md) | 知识图谱服务 |
| [04-onion-model-t1.md](04-onion-model-t1.md) | 洋葱模型 T1 层与蓝图增强 |
| [05-api-frontend.md](05-api-frontend.md) | 新增 API 端点与前端变更 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与流水线背景 |
| [../2026-04-20-ai-novel-03-core-services.md](../2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 补充核心服务边界 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考跨 phase 复用的通用组件 |
