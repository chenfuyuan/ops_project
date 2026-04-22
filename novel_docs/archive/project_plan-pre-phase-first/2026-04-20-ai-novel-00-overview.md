---
title: AI 长篇小说生成系统 — 设计总览
version: 1.0
date: 2026-04-20
status: draft
---

# AI 长篇小说生成系统 — 设计总览

## 文档角色

本文档是 `novel_docs/superpowers/specs/` 的统一入口，承担总纲层职责：

- 说明项目愿景、核心约束与全局判断
- 指向总纲专题与阶段路线
- 为后续 OpenSpec 或继续规划提供第一层上下文

阅读顺序默认遵循：**总纲入口 → 阶段路线 / 目标 phase overview → 按需专题文档**。

## 项目愿景

构建一个高质量的 AI 长篇小说生成系统，融合 AI_NovelGenerator、InkOS、PlotPilot 三个开源项目的精华。先自用探索 AI 小说的可能性和工作流，验证后演进为 SaaS 服务。

## 核心约束

- **技术栈：** Python 引擎（FastAPI）+ TypeScript 前端
- **小说类型：** 中英文长篇（200+ 章）
- **交互模式：** 先人工主导，后加自动模式
- **质量优先级：** 一致性 > 叙事性 > 文学性
- **LLM 策略：** 多模型路由，按任务分配不同模型
- **开发策略：** MVP 全流程先跑通，分 6 个阶段演进

## 三家精华提炼

### 从 AI_NovelGenerator 取

| 特性 | 说明 |
|------|------|
| 雪花写作法 | 五步大纲生成：核心种子 → 角色动力三角 → 角色初始状态 → 世界观 → 三幕结构 |
| 提示组装流水线 | 多轮 LLM 调用准备上下文（摘要生成、关键词提取、知识过滤），而非简单模板拼接 |
| 章节蓝图标注 | 悬念密度、伏笔操作（植入/强化/收获）、认知颠覆度（1-5 星） |
| 检查点恢复 | 长链 LLM 调用中途失败可从断点续跑 |

### 从 InkOS 取

| 特性 | 说明 |
|------|------|
| 编译治理模式 | 规划 → 上下文编译 → 生成 → 审计 → 状态提交，每步产出可检查的中间产物 |
| 伏笔生命周期 | open → progressing → deferred → resolved，带 last_advanced_chapter 追踪 |
| 多维连续性审计 | 审计发现问题 → 自动修订 → 再审计，直到关键问题清零 |
| JSON Delta 状态更新 | 增量更新 + schema 校验，拒绝非法变更 |
| 多 Agent 职责分离 | Planner / Composer / Writer / Auditor / Reflector 各司其职 |
| 去 AI 化规则 | 疲劳词表、禁用句式、风格指纹注入 |

### 从 PlotPilot 取

| 特性 | 说明 |
|------|------|
| 洋葱模型上下文预算 | T0（永不裁剪）→ T1（可压缩）→ T2（动态水位线）→ T3（优先牺牲） |
| 记忆引擎事实锁 | FACT_LOCK / COMPLETED_BEATS / REVEALED_CLUES 三类不可变约束 |
| 章后统一管线 | 无论人写还是 AI 写，同一套后处理提取和状态更新 |
| 主题代理系统 | 按类型注入写作规则、禁忌、节拍模板，可插拔技能 |
| 张力分析 | 每章 0-10 评分，历史曲线可视化，连续低张力预警 |
| 语音漂移检测 | 统计模式（零成本）+ LLM 模式（深度），漂移时定向重写 |
| 知识图谱三元组 | 主-谓-宾事实提取，支持信息边界查询 |
| 自动驾驶状态机 | 数据库驱动 + 熔断器 + 节拍级幂等恢复 |

## 文档索引

### 总纲专题

| 文档 | 角色 | 内容 |
|------|------|------|
| [01-architecture.md](2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 系统架构与核心流水线 |
| [02-data-model.md](2026-04-20-ai-novel-02-data-model.md) | 总纲专题 | 数据模型与存储设计 |
| [03-core-services.md](2026-04-20-ai-novel-03-core-services.md) | 总纲专题 | 核心服务详细设计 |
| [workflow-node-architecture.md](2026-04-20-business-workflow-node-centered-architecture-design.md) | 总纲专题 | 业务线 / workflow / node-centered 架构方向 |
| [common-components.md](common-components.md) | 横切专题 | 可跨多个 phase 复用的通用组件清单 |

### 阶段路线

| 文档 | 角色 | 内容 |
|------|------|------|
| [04-phases.md](2026-04-20-ai-novel-04-phases.md) | 阶段索引 | 6 个 phase 的演进顺序、依赖关系与 phase overview 入口 |
