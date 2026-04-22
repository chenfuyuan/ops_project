---
title: Phase 2 — 一致性保障体系
version: 1.0
date: 2026-04-20
goal: 解决长篇写作最核心的问题——状态矛盾、伏笔遗忘、逻辑漏洞
prerequisite: Phase 1
---

# Phase 2 — 一致性保障体系

## 文档角色

本文档属于 **Phase 主线层 overview**，只承担本阶段的目标、范围、完成标准与子主题入口，不承载横切 topic 或其他 phase 的完整设计细节。

阅读方式：先阅读总纲入口与阶段路线，再进入本 overview，最后按需阅读本阶段专题文档。

## 阶段目标

在 Phase 1 的基础上，构建完整的质量保障体系。核心是：写完一章后，系统能自动发现并修复逻辑矛盾，确保 200+ 章长篇的状态一致性。

## 完成标准

- 每章生成后自动执行 15 维一致性审计
- critical 问题自动修订（最多 3 轮），非 critical 标记人工审核
- 伏笔支持完整生命周期（open → progressing → deferred → resolved），停滞自动预警
- 事实锁机制生效，不可逆事实被保护
- 状态更新改为 JSON Delta + Pydantic 校验，非法变更被拒绝
- 流水线中间产物完整可追溯

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-auditor.md](01-auditor.md) | 一致性审计器（15 维） |
| [02-reviser.md](02-reviser.md) | 审计-修订循环 |
| [03-fact-locks.md](03-fact-locks.md) | 事实锁与 JSON Delta |
| [04-foreshadowing-lifecycle.md](04-foreshadowing-lifecycle.md) | 伏笔完整生命周期 |
| [05-pipeline-upgrade.md](05-pipeline-upgrade.md) | 流水线升级与前端变更 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与流水线背景 |
| [../2026-04-20-ai-novel-03-core-services.md](../2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 补充核心服务边界 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考跨 phase 复用的通用组件 |
