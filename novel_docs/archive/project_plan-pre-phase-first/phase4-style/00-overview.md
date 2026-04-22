---
title: Phase 4 — 风格与去 AI 化（总览）
version: 1.0
date: 2026-04-20
goal: 让产出不像 AI 写的，有一致的文学风格
prerequisite: Phase 2
---

# Phase 4 — 风格与去 AI 化

## 文档角色

本文档属于 **Phase 主线层 overview**，负责定义本阶段的目标、范围、完成标准与子主题入口，不承载跨阶段横切专题的完整细节。

阅读方式：先从总纲入口和阶段路线建立上下文，再阅读本 overview，最后按需进入本阶段专题文档。

## 阶段目标

解决 AI 生成文本的两大风格问题：(1) AI 味重——用词重复、句式单调、缺乏个性；(2) 风格漂移——长篇写作中风格逐渐偏离。

## 完成标准

- 风格指纹系统上线：能从参考文本提取风格特征并注入写作
- 语音漂移检测双模式可用（统计模式零成本 + LLM 模式深度分析）
- 去 AI 化规则引擎生效，中英文分别维护疲劳词表和禁用句式
- AI 检测评分可用，高分章节自动标记
- 漂移超阈值时触发定向重写建议

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-style-fingerprint.md](01-style-fingerprint.md) | 风格指纹系统 |
| [02-voice-drift.md](02-voice-drift.md) | 语音漂移检测 |
| [03-anti-ai-rules.md](03-anti-ai-rules.md) | 去 AI 化规则引擎与 AI 检测评分 |
| [04-api-frontend.md](04-api-frontend.md) | 新增 API 端点与前端变更 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与流水线背景 |
| [../2026-04-20-ai-novel-03-core-services.md](../2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 补充核心服务边界 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考跨 phase 复用的通用组件 |
