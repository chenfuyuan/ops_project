## Why

MVP 创作闭环的起点缺失。基础设施和 AI 网关已就绪，但项目尚无任何业务功能将作者的创作想法转化为可执行的创作计划。大纲生成是创作流水线的第一个节点——没有它，后续的章节蓝图和章节生成流水线无法启动。

## What Changes

- 在 `app/business/novel_generate/nodes/outline/` 下建立大纲生成领域模型，包括结构化种子（Seed）、骨架（Skeleton/SkeletonVolume）、章节摘要（ChapterSummary）和聚合大纲（Outline）
- 实现两阶段生成流程：种子 → 骨架生成（用户审阅/编辑）→ 确认 → 逐卷展开为章节摘要
- 通过 `OutlineAiPort` 抽象集成 AI 网关 STRUCTURED 模式，business 层不直接依赖 capability
- 在 `app/business/novel_generate/infrastructure/` 下实现 PostgreSQL 持久化（SQLAlchemy）
- 新增 HTTP 端点暴露大纲生成的创建、生成、确认、展开、编辑操作
- 在 `app/bootstrap/` 下新增装配模块完成 service + repository + AI port 的运行时组装

## Capabilities

### New Capabilities

- `outline-generation`: 大纲生成核心能力——接受结构化种子输入，分两阶段（骨架 → 章节摘要）生成可编辑、可下游消费的结构化大纲

### Modified Capabilities

- `ai-gateway`: 无需求级变更。大纲生成作为 AI 网关的消费方，通过已有的 STRUCTURED 模式调用，不修改网关自身能力边界。

## Impact

- **新增代码**：`app/business/novel_generate/`（领域模型、service、ports、rules）、`app/business/novel_generate/infrastructure/`（repository 实现）、`app/interfaces/http/outline.py`、`app/bootstrap/novel_generate.py`
- **数据库**：新增 PostgreSQL 表（种子、骨架、卷、章节摘要、大纲），需要数据库迁移
- **依赖**：复用已有依赖（SQLAlchemy、Pydantic、AI 网关），无新增外部依赖
- **前置条件**：PostgreSQL 基础设施切换需先完成（独立前置 change）
- **下游影响**：大纲结果将作为"章节蓝图"需求的稳定输入接口
